#!/usr/bin/env node
/**
 * ast_extractor.js — Babel-based JS AST extractor for the Gemini agent.
 *
 * Called by Python as:
 *   node ast_extractor.js <input.json> <output.json>
 *
 * Input JSON (a list of file entries):
 *   [{ "abs": "/full/path/to/a.js", "rel": "a.js" }, ...]
 *
 * Output JSON (keyed by relative path — becomes chunk metadata downstream):
 *   {
 *     "a.js": {
 *       "ok": true,
 *       "functions": [
 *         { "name", "kind", "start", "end",
 *           "parent"?, "async"?, "static"?, "generator"?,
 *           "calls": [ { callee, callee_kind, line, raw }, ... ] },
 *         ...
 *       ]
 *     },
 *     "b.js": { "ok": false, "error": "Unexpected token ..." }
 *   }
 *
 * Phase 2: each function entry carries a `calls[]` array of every call site
 * inside that function (CallExpression, NewExpression, OptionalCallExpression).
 * Calls inside an unnamed nested fn that gets dropped from output bubble up
 * to the nearest emitted enclosing function.
 *
 * Known limits (deferred):
 * - No this-binding tracking across .bind/.call/.apply
 * - No resolution of require()/import targets
 * - Cross-file call resolution lives in a later pass
 */

const fs       = require('fs');
const parser   = require('@babel/parser');
const traverse = require('@babel/traverse').default;

const inputPath  = process.argv[2];
const outputPath = process.argv[3];
const frameworksArg = process.argv[4] || '';

if (!inputPath || !outputPath) {
    console.error('usage: node ast_extractor.js <input.json> <output.json> [frameworks]');
    process.exit(2);
}

const ACTIVE_FRAMEWORKS = new Set(
    frameworksArg.split(',').map(s => s.trim()).filter(Boolean)
);
if (!ACTIVE_FRAMEWORKS.size) ACTIVE_FRAMEWORKS.add('node');
function hasFw(...names) {
    for (const n of names) if (ACTIVE_FRAMEWORKS.has(n)) return true;
    return false;
}

const EXPRESS_REQ_PROPS = {
    body:    'express_req_body',
    query:   'express_req_query',
    params:  'express_req_params',
    headers: 'express_req_headers',
    cookies: 'express_req_cookies',
    signedCookies: 'express_req_cookies',
    files:   'express_req_files',
    file:    'express_req_files',
};
const EXPRESS_REQ_SEVERITY = {
    express_req_body:   'high',
    express_req_query:  'high',
    express_req_params: 'high',
    express_req_headers:'medium',
    express_req_cookies:'medium',
    express_req_files:  'high',
};
const ANGULAR_ROUTE_PROPS = new Set([
    'params','queryParams','queryParamMap','snapshot',
]);
const CHILD_PROCESS_EXEC_NAMES = new Set([
    'exec','execSync','execFileSync',
]);
const CHILD_PROCESS_SPAWN_NAMES = new Set([
    'spawn','spawnSync','execFile',
]);
const FS_PATH_TRAVERSAL_METHODS = new Set([
    'readFile','readFileSync','createReadStream',
    'writeFile','appendFile','unlink','rename',
]);
const NOSQL_METHODS = new Set([
    'find','findOne','findById','updateOne','deleteOne','aggregate',
]);
const SQL_RAW_METHODS = new Set(['query','raw','run']);

function isLiteralOnlyObject(arg) {
    if (!arg || arg.type !== 'ObjectExpression') return false;
    for (const prop of arg.properties || []) {
        if (prop.type === 'SpreadElement') return false;
        const v = prop.value;
        if (!v) return false;
        if (v.type !== 'StringLiteral' && v.type !== 'NumericLiteral'
            && v.type !== 'BooleanLiteral' && v.type !== 'NullLiteral') {
            return false;
        }
    }
    return true;
}

const entries = JSON.parse(fs.readFileSync(inputPath, 'utf8'));

const PARSE_OPTS = {
    sourceType: 'unambiguous',
    allowImportExportEverywhere: true,
    allowReturnOutsideFunction:  true,
    allowAwaitOutsideFunction:   true,
    allowSuperOutsideMethod:     true,
    allowUndeclaredExports:      true,
    errorRecovery: true,
    plugins: [
        'jsx',
        'typescript',
        'decorators-legacy',
        'classProperties',
        'classPrivateProperties',
        'classPrivateMethods',
        'optionalChaining',
        'nullishCoalescingOperator',
        'dynamicImport',
        'topLevelAwait',
        'importAssertions',
    ],
};

function findEnclosingClass(path) {
    let p = path.parentPath;
    while (p) {
        if (p.node.type === 'ClassDeclaration' || p.node.type === 'ClassExpression') {
            if (p.node.id && p.node.id.name) return p.node.id.name;
            if (p.parentPath && p.parentPath.node.type === 'VariableDeclarator'
                && p.parentPath.node.id.type === 'Identifier') {
                return p.parentPath.node.id.name;
            }
            return null;
        }
        p = p.parentPath;
    }
    return null;
}

function resolveExpressionName(nodePath) {
    const node = nodePath.node;
    if (node.type === 'FunctionExpression' && node.id && node.id.name) {
        return node.id.name;
    }
    const parent = nodePath.parent;
    if (!parent) return null;

    switch (parent.type) {
        case 'VariableDeclarator':
            return parent.id && parent.id.type === 'Identifier' ? parent.id.name : null;

        case 'ObjectProperty':
        case 'Property':
            if (parent.key.type === 'Identifier')    return parent.key.name;
            if (parent.key.type === 'StringLiteral') return parent.key.value;
            return null;

        case 'AssignmentExpression':
            if (parent.left.type === 'MemberExpression') {
                const prop = parent.left.property;
                if (prop.type === 'Identifier')    return prop.name;
                if (prop.type === 'StringLiteral') return prop.value;
            }
            if (parent.left.type === 'Identifier') return parent.left.name;
            return null;

        case 'CallExpression':
            if (parent.callee && parent.callee.type === 'MemberExpression'
                && parent.callee.property.type === 'Identifier') {
                const idx = parent.arguments.indexOf(node);
                if (idx >= 0) {
                    if (parent.callee.property.name === 'addEventListener'
                        && parent.arguments[0]
                        && parent.arguments[0].type === 'StringLiteral') {
                        return `${parent.arguments[0].value}_handler`;
                    }
                    return `${parent.callee.property.name}_cb${idx}`;
                }
            }
            return null;

        default:
            return null;
    }
}

const RAW_MAX = 200;

function describeCall(node, source) {
    const callee = node.callee;
    const line   = node.loc ? node.loc.start.line : 0;
    let raw = source.slice(node.start, node.end);
    if (raw.length > RAW_MAX) raw = raw.slice(0, RAW_MAX);

    if (node.type === 'NewExpression') {
        if (callee.type === 'Identifier') {
            return { callee: `new ${callee.name}`, callee_kind: 'new', line, raw };
        }
        if ((callee.type === 'MemberExpression' || callee.type === 'OptionalMemberExpression')
            && !callee.computed
            && callee.object.type === 'Identifier'
            && callee.property.type === 'Identifier') {
            return {
                callee: `new ${callee.object.name}.${callee.property.name}`,
                callee_kind: 'new', line, raw,
            };
        }
        return { callee: '<dynamic>', callee_kind: 'dynamic', line, raw };
    }

    // CallExpression / OptionalCallExpression
    if (callee.type === 'Super') {
        return { callee: 'super', callee_kind: 'super', line, raw };
    }
    if (callee.type === 'Identifier') {
        return { callee: callee.name, callee_kind: 'ident', line, raw };
    }
    if (callee.type === 'MemberExpression' || callee.type === 'OptionalMemberExpression') {
        if (callee.computed) {
            return { callee: '<dynamic>', callee_kind: 'dynamic', line, raw };
        }
        let propName = null;
        if (callee.property.type === 'Identifier')        propName = callee.property.name;
        else if (callee.property.type === 'StringLiteral') propName = callee.property.value;
        if (!propName) {
            return { callee: '<dynamic>', callee_kind: 'dynamic', line, raw };
        }
        const obj = callee.object;
        if (obj.type === 'ThisExpression') {
            return { callee: `this.${propName}`, callee_kind: 'this', line, raw };
        }
        if (obj.type === 'Super') {
            return { callee: `super.${propName}`, callee_kind: 'super', line, raw };
        }
        if (obj.type === 'Identifier') {
            return { callee: `${obj.name}.${propName}`, callee_kind: 'member', line, raw };
        }
        return { callee: '<dynamic>', callee_kind: 'dynamic', line, raw };
    }
    return { callee: '<dynamic>', callee_kind: 'dynamic', line, raw };
}

function resolveMemberAccess(node) {
    if (node.type !== 'MemberExpression' &&
        node.type !== 'OptionalMemberExpression') return null;

    let prop = null;
    if (!node.computed) {
        if (node.property.type === 'Identifier') prop = node.property.name;
    } else {
        if (node.property.type === 'StringLiteral') prop = node.property.value;
        else return null;
    }
    if (!prop) return null;

    const obj = node.object;
    let objName = null;
    if (obj.type === 'Identifier') {
        objName = obj.name;
    } else if (obj.type === 'ThisExpression') {
        objName = 'this';
    } else if ((obj.type === 'MemberExpression' ||
                obj.type === 'OptionalMemberExpression') && !obj.computed) {
        const inner = obj.object.type === 'Identifier' ? obj.object.name
                    : obj.object.type === 'ThisExpression' ? 'this'
                    : null;
        const innerProp = obj.property.type === 'Identifier' ? obj.property.name : null;
        if (inner && innerProp) objName = `${inner}.${innerProp}`;
    }

    // Property is nameable; object may be too dynamic to name (e.g. fn().innerHTML).
    // Property-driven rules (innerHTML/outerHTML/srcdoc/event handlers) still match;
    // object-identity rules (location.*, document.*) compare object name and skip.
    return { object: objName || '<dynamic>', property: prop };
}

function isAssignmentLHS(path) {
    const parent = path.parent;
    return parent &&
           parent.type === 'AssignmentExpression' &&
           parent.left === path.node;
}

function _isAddEventListenerMessage(node) {
    return (node.type === 'CallExpression' ||
            node.type === 'OptionalCallExpression') &&
           node.callee &&
           (node.callee.type === 'MemberExpression' ||
            node.callee.type === 'OptionalMemberExpression') &&
           node.callee.property.type === 'Identifier' &&
           node.callee.property.name === 'addEventListener' &&
           node.arguments && node.arguments[0] &&
           node.arguments[0].type === 'StringLiteral' &&
           node.arguments[0].value === 'message';
}

function _isOnmessageAssign(node) {
    return node.type === 'AssignmentExpression' &&
           node.left &&
           (node.left.type === 'MemberExpression' ||
            node.left.type === 'OptionalMemberExpression') &&
           node.left.property.type === 'Identifier' &&
           node.left.property.name === 'onmessage';
}

function isMessageHandlerContext(path) {
    let p = path.parentPath;
    while (p) {
        const node = p.node;
        if (_isAddEventListenerMessage(node)) return true;
        if (_isOnmessageAssign(node)) return true;
        // At the enclosing-function boundary, also inspect the function's
        // immediate parent — that is where the registration lives
        // (e.g. addEventListener("message", <this fn>) or .onmessage = <this fn>).
        if (p.isFunctionDeclaration() ||
            p.isFunctionExpression() ||
            p.isArrowFunctionExpression()) {
            const parent = p.parentPath;
            if (!parent) return false;
            return _isAddEventListenerMessage(parent.node) ||
                   _isOnmessageAssign(parent.node);
        }
        p = p.parentPath;
    }
    return false;
}

function collapseStringy(node, nodePath) {
    if (nodePath) {
        try {
            const ev = nodePath.evaluate();
            if (ev.confident && typeof ev.value === 'string') {
                return { template: ev.value, vars: [] };
            }
        } catch (_) {}
    }

    const vars = [];

    function walk(n) {
        if (!n) return 'EXPR';
        switch (n.type) {
            case 'StringLiteral':
                return n.value;
            case 'TemplateLiteral': {
                let result = '';
                for (let i = 0; i < n.quasis.length; i++) {
                    result += n.quasis[i].value.cooked || n.quasis[i].value.raw || '';
                    if (i < n.expressions.length) {
                        const sub = walk(n.expressions[i]);
                        result += sub;
                        if (sub === 'EXPR') {
                            const expr = n.expressions[i];
                            if (expr.type === 'Identifier') vars.push(expr.name);
                        }
                    }
                }
                return result;
            }
            case 'BinaryExpression':
                if (n.operator === '+') {
                    return walk(n.left) + walk(n.right);
                }
                return 'EXPR';
            case 'NumericLiteral': return String(n.value);
            case 'BooleanLiteral': return String(n.value);
            case 'NullLiteral':    return 'null';
            case 'Identifier':
                vars.push(n.name);
                return 'EXPR';
            default:
                return 'EXPR';
        }
    }

    const template = walk(node);
    if (template.startsWith('EXPR')) return null;
    return { template, vars: [...new Set(vars)] };
}

function parseQueryParams(template) {
    const qi = template.indexOf('?');
    if (qi === -1) return [];
    const qs = template.slice(qi + 1).split('#')[0];
    const params = [];
    for (const part of qs.split('&')) {
        const eq = part.indexOf('=');
        const name = eq === -1 ? part : part.slice(0, eq);
        if (name && !name.includes('EXPR')) params.push(name);
    }
    return params;
}

function extractBodyParams(node) {
    if (!node || node.type !== 'ObjectExpression') return [];
    const keys = [];
    for (const prop of node.properties || []) {
        if (prop.type === 'SpreadElement') continue;
        const key = prop.key;
        if (!key) continue;
        if (key.type === 'Identifier')    keys.push(key.name);
        if (key.type === 'StringLiteral') keys.push(key.value);
    }
    return keys;
}

function extractIdentifiers(node) {
    const ids = new Set();
    function walk(n) {
        if (!n) return;
        if (n.type === 'Identifier') {
            ids.add(n.name);
            return;
        }
        if (n.type === 'MemberExpression' || n.type === 'OptionalMemberExpression') {
            walk(n.object);
            if (n.computed) walk(n.property);
        }
        if (n.type === 'CallExpression' || n.type === 'OptionalCallExpression' || n.type === 'NewExpression') {
            walk(n.callee);
            for (const arg of n.arguments || []) walk(arg);
        }
        if (n.type === 'BinaryExpression' || n.type === 'LogicalExpression' || n.type === 'AssignmentExpression') {
            walk(n.left);
            walk(n.right);
        }
        if (n.type === 'UnaryExpression' || n.type === 'UpdateExpression') {
            walk(n.argument);
        }
        if (n.type === 'ConditionalExpression') {
            walk(n.test);
            walk(n.consequent);
            walk(n.alternate);
        }
        if (n.type === 'ArrayExpression') {
            for (const el of n.elements || []) walk(el);
        }
        if (n.type === 'ObjectExpression') {
            for (const prop of n.properties || []) {
                if (prop.type === 'SpreadElement') walk(prop.argument);
                else {
                    if (prop.computed) walk(prop.key);
                    walk(prop.value);
                }
            }
        }
        if (n.type === 'TemplateLiteral') {
            for (const expr of n.expressions || []) walk(expr);
        }
    }
    walk(node);
    return Array.from(ids);
}

function extractPatternNames(patternNode) {
    const names = [];
    if (!patternNode) return names;
    if (patternNode.type === 'Identifier') {
        names.push(patternNode.name);
    } else if (patternNode.type === 'ObjectPattern') {
        for (const prop of patternNode.properties || []) {
            if (prop.type === 'RestElement') {
                names.push(...extractPatternNames(prop.argument));
            } else {
                names.push(...extractPatternNames(prop.value));
            }
        }
    } else if (patternNode.type === 'ArrayPattern') {
        for (const el of patternNode.elements || []) {
            if (el) names.push(...extractPatternNames(el));
        }
    } else if (patternNode.type === 'AssignmentPattern') {
        names.push(...extractPatternNames(patternNode.left));
    } else if (patternNode.type === 'RestElement') {
        names.push(...extractPatternNames(patternNode.argument));
    }
    return names;
}

function isSourceCallOrAccess(node) {
    if (!node) return null;

    if (node.type === 'MemberExpression' || node.type === 'OptionalMemberExpression') {
        const mem = resolveMemberAccess(node);
        if (!mem) return null;

        const LOC_SOURCES = {
            hash: 'location_hash', search: 'location_search',
            pathname: 'location_pathname', href: 'location_href_read'
        };
        if ((mem.object === 'location' || mem.object === 'window.location' || mem.object === 'document.location')
            && LOC_SOURCES[mem.property]) {
            return LOC_SOURCES[mem.property];
        }

        const DOC_SOURCES = {
            URL: 'document_URL', documentURI: 'document_documentURI',
            baseURI: 'document_baseURI', referrer: 'document_referrer',
            cookie: 'document_cookie'
        };
        if ((mem.object === 'document' || mem.object === 'window.document')
            && DOC_SOURCES[mem.property]) {
            return DOC_SOURCES[mem.property];
        }

        if (mem.property === 'name' && (mem.object === 'window' || mem.object === 'globalThis')) {
            return 'window_name';
        }

        if (mem.property === 'data' && /^(event|e|msg|message|ev)$/.test(mem.object)) {
            return 'message_event_data_read';
        }
    }

    if (node.type === 'CallExpression' || node.type === 'OptionalCallExpression') {
        const callee = node.callee;
        if ((callee.type === 'MemberExpression' || callee.type === 'OptionalMemberExpression')
            && callee.property.type === 'Identifier' && callee.property.name === 'get') {
            const innerObj = callee.object;
            if ((innerObj.type === 'MemberExpression' || innerObj.type === 'OptionalMemberExpression')
                && innerObj.property.type === 'Identifier' && innerObj.property.name === 'searchParams') {
                return 'searchParams_get';
            }
        }
    }

    if (node.type === 'NewExpression') {
        if (node.callee.type === 'Identifier' && node.callee.name === 'URLSearchParams') {
            return 'URLSearchParams_ctor';
        }
    }

    return null;
}

function isSinkExpression(parentNode, argNode, argIndex) {
    if (!parentNode) return null;

    if (parentNode.type === 'AssignmentExpression' && parentNode.right === argNode) {
        const mem = resolveMemberAccess(parentNode.left);
        if (!mem) return null;
        if (mem.property === 'innerHTML') return 'innerHTML_assign';
        if (mem.property === 'outerHTML') return 'outerHTML_assign';
        if (mem.property === 'srcdoc') return 'srcdoc_assign';
        if (mem.property === 'href' && (mem.object === 'location' ||
            mem.object === 'window.location' || mem.object === 'document.location' ||
            (typeof mem.object === 'string' && mem.object.endsWith('.location')))) {
            return 'location_href_assign';
        }
        if (/^on[a-z]+$/.test(mem.property)) return 'event_handler_attr_assign';
    }

    if ((parentNode.type === 'CallExpression' || parentNode.type === 'OptionalCallExpression')
        && argIndex === 0) {
        const callee = parentNode.callee;
        if (callee.type === 'Identifier') {
            if (callee.name === 'eval') return 'eval_call';
            if (callee.name === 'setTimeout' || callee.name === 'setInterval' || callee.name === 'setImmediate') {
                if (argNode.type !== 'FunctionExpression' && argNode.type !== 'ArrowFunctionExpression') {
                    return `${callee.name}_string`;
                }
            }
            if (callee.name === 'fetch')  return 'fetch_call';
            if (callee.name === 'axios')  return 'axios_call';
        }
        const mem = resolveMemberAccess(callee);
        if (mem) {
            if ((mem.object === 'document' || mem.object === 'window.document')
                && (mem.property === 'write' || mem.property === 'writeln')) {
                return `document_${mem.property}`;
            }
            if ((mem.object === 'location' ||
                 mem.object === 'window.location' || mem.object === 'document.location' ||
                 (typeof mem.object === 'string' && mem.object.endsWith('.location')))
                && (mem.property === 'assign' || mem.property === 'replace')) {
                return `location_${mem.property}_call`;
            }
            if (mem.property === 'fetch'
                && (mem.object === 'window' || mem.object === 'globalThis')) {
                return 'fetch_call';
            }
            if (mem.object === 'axios'
                && ['get','post','put','delete','patch','request','head','options'].includes(mem.property)) {
                return 'axios_call';
            }
        }
    }

    if ((parentNode.type === 'CallExpression' || parentNode.type === 'OptionalCallExpression')
        && argIndex === 1) {
        const callee = parentNode.callee;
        const mem = resolveMemberAccess(callee);
        if (mem && mem.property === 'insertAdjacentHTML') {
            return 'insertAdjacentHTML_call';
        }
        if (mem && mem.property === 'open' && parentNode.arguments.length >= 2) {
            return 'xhr_open_call';
        }
        if (mem && mem.property === 'setAttribute') {
            const firstArg = parentNode.arguments[0];
            if (firstArg && firstArg.type === 'StringLiteral') {
                const DANGEROUS_ATTRS = new Set([
                    'href','src','srcdoc','action','formaction',
                    'background','cite','codebase','profile','usemap',
                    'xlink:href','xml:base','data',
                ]);
                const attrLower = firstArg.value.toLowerCase();
                if (DANGEROUS_ATTRS.has(attrLower) || attrLower.startsWith('on')) {
                    return 'setAttribute_dangerous_attr';
                }
            }
            if (firstArg && firstArg.type !== 'StringLiteral') {
                return 'setAttribute_dynamic_attr';
            }
        }
    }

    if (parentNode.type === 'NewExpression' && argIndex >= 0) {
        if (parentNode.callee.type === 'Identifier' && parentNode.callee.name === 'Function') {
            return 'new_Function';
        }
    }

    return null;
}

function isSanitiserCall(node) {
    if (!node || (node.type !== 'CallExpression' && node.type !== 'OptionalCallExpression')) {
        return null;
    }
    const callee = node.callee;
    if (callee.type === 'Identifier') {
        if (callee.name === 'encodeURIComponent') return 'sanitizer_encodeURIComponent';
        if (callee.name === 'Number') return 'sanitizer_Number_coerce';
        if (callee.name === 'parseInt' || callee.name === 'parseFloat') {
            return 'sanitizer_parseInt_parseFloat';
        }
    }
    const mem = resolveMemberAccess(callee);
    if (!mem) return null;

    if (mem.object === 'DOMPurify' && mem.property === 'sanitize') {
        return 'sanitizer_dompurify';
    }
    if (mem.property === 'sanitize') {
        return 'sanitizer_dompurify_namespaced';
    }
    if ((mem.object === '_' || mem.object === 'lodash') && mem.property === 'escape') {
        return 'sanitizer_lodash_escape';
    }
    if (mem.object === 'he' && (mem.property === 'encode' || mem.property === 'escape')) {
        return 'sanitizer_he_encode';
    }
    return null;
}

function extractOne(abs, rel) {
    const source = fs.readFileSync(abs, 'utf8');
    const ast = parser.parse(source, PARSE_OPTS);
    const fileRel = (rel || abs).replace(/\\/g, '/');

    const functions = [];
    const astTags = [];
    const extractedUrls = [];
    const importMap = [];
    const taintFactsByFunction = new Map();
    const variablesByFunction  = new Map();
    const dataflowByFunction   = new Map();
    const seen = new Set();
    const stack = [];   // current enclosing emitted-function frames

    // Framework-aware: track local names bound to specific Node modules.
    // Populated by ImportDeclaration + require()-style VariableDeclarator handlers.
    const childProcessLocals  = new Set(); // { exec, spawn, ... } direct names
    const childProcessAliases = new Set(); // { cp } when `const cp = require('child_process')` */

    const ensureFacts = (fnName) => {
        if (!taintFactsByFunction.has(fnName)) {
            taintFactsByFunction.set(fnName, []);
        }
        return taintFactsByFunction.get(fnName);
    };
    const ensureVars = (fnName) => {
        if (!variablesByFunction.has(fnName)) {
            variablesByFunction.set(fnName, []);
        }
        return variablesByFunction.get(fnName);
    };
    const ensureEdges = (fnName) => {
        if (!dataflowByFunction.has(fnName)) {
            dataflowByFunction.set(fnName, []);
        }
        return dataflowByFunction.get(fnName);
    };
    const recordVar = (fnName, name, line) => {
        const vars = ensureVars(fnName);
        if (!vars.find(v => v.name === name)) {
            vars.push({ name, first_line: line });
        }
    };

    const push = (entry) => {
        const key = `${entry.start}:${entry.end}:${entry.name}`;
        if (seen.has(key)) return false;
        seen.add(key);
        functions.push(entry);
        return true;
    };

    const enterFunc = (p, entry) => {
        entry.calls = [];
        if (push(entry)) {
            p.node.__astFrame = entry;
            stack.push(entry);
            // Seed variables with parameters + :return
            ensureVars(entry.name);
            for (const param of p.node.params || []) {
                if (param.type === 'Identifier') {
                    recordVar(entry.name, param.name,
                        param.loc ? param.loc.start.line : 0);
                }
                // Destructuring / rest / defaults not yet supported
            }
            recordVar(entry.name, ':return', 0);
        }
    };
    const exitFunc = (p) => {
        if (p.node.__astFrame) stack.pop();
    };

    const callVisitor = (p) => {
        if (!stack.length) return;
        if (!p.node.loc) return;
        stack[stack.length - 1].calls.push(describeCall(p.node, source));
    };

    traverse(ast, {
        FunctionDeclaration: {
            enter(p) {
                if (!p.node.loc) return;
                enterFunc(p, {
                    name: p.node.id ? p.node.id.name : 'anonymous',
                    kind: 'function',
                    start: p.node.loc.start.line,
                    end:   p.node.loc.end.line,
                    async:     !!p.node.async,
                    generator: !!p.node.generator,
                });
            },
            exit: exitFunc,
        },

        FunctionExpression: {
            enter(p) {
                if (!p.node.loc) return;
                const name = resolveExpressionName(p);
                if (!name) return;
                enterFunc(p, {
                    name,
                    kind: 'function_expression',
                    start: p.node.loc.start.line,
                    end:   p.node.loc.end.line,
                    async: !!p.node.async,
                });
            },
            exit: exitFunc,
        },

        ArrowFunctionExpression: {
            enter(p) {
                if (!p.node.loc) return;
                const name = resolveExpressionName(p);
                if (!name) return;
                enterFunc(p, {
                    name,
                    kind: 'arrow',
                    start: p.node.loc.start.line,
                    end:   p.node.loc.end.line,
                    async: !!p.node.async,
                });
            },
            exit: exitFunc,
        },

        ClassDeclaration(p) {
            if (!p.node.loc) return;
            // Class itself is not a callable scope — push() but don't stack.
            push({
                name: p.node.id ? p.node.id.name : 'anonymous_class',
                kind: 'class',
                start: p.node.loc.start.line,
                end:   p.node.loc.end.line,
                parent: findEnclosingClass(p),
                extends:
                    p.node.superClass && p.node.superClass.type === 'Identifier'
                        ? p.node.superClass.name
                        : null,
                calls: [],
            });
        },

        ClassMethod: {
            enter(p) {
                if (!p.node.loc) return;
                const cls = findEnclosingClass(p);
                let name = 'anonymous_method';
                if (p.node.key.type === 'Identifier')         name = p.node.key.name;
                else if (p.node.key.type === 'StringLiteral') name = p.node.key.value;
                enterFunc(p, {
                    name:  cls ? `${cls}.${name}` : name,
                    kind:  p.node.kind === 'constructor' ? 'constructor' : 'method',
                    start: p.node.loc.start.line,
                    end:   p.node.loc.end.line,
                    async:  !!p.node.async,
                    static: !!p.node.static,
                    parent: cls,
                });
            },
            exit: exitFunc,
        },

        ClassPrivateMethod: {
            enter(p) {
                if (!p.node.loc) return;
                const cls = findEnclosingClass(p);
                let name = 'private_method';
                if (p.node.key.type === 'PrivateName'
                    && p.node.key.id.type === 'Identifier') {
                    name = `#${p.node.key.id.name}`;
                }
                enterFunc(p, {
                    name:  cls ? `${cls}.${name}` : name,
                    kind:  'private_method',
                    start: p.node.loc.start.line,
                    end:   p.node.loc.end.line,
                    async:  !!p.node.async,
                    static: !!p.node.static,
                    parent: cls,
                });
            },
            exit: exitFunc,
        },

        ObjectMethod: {
            enter(p) {
                if (!p.node.loc) return;
                let name = 'anonymous_method';
                if (p.node.key.type === 'Identifier')         name = p.node.key.name;
                else if (p.node.key.type === 'StringLiteral') name = p.node.key.value;
                enterFunc(p, {
                    name,
                    kind:  p.node.kind === 'method' ? 'object_method' : p.node.kind,
                    start: p.node.loc.start.line,
                    end:   p.node.loc.end.line,
                    async: !!p.node.async,
                });
            },
            exit: exitFunc,
        },

        CallExpression: {
            enter(p) {
                callVisitor(p);
                astTagCallExpression(p);
                astTagFrameworkCall(p);
                taintTagCallExpression(p);
            },
        },
        OptionalCallExpression: {
            enter(p) {
                callVisitor(p);
                astTagCallExpression(p);
                astTagFrameworkCall(p);
                taintTagCallExpression(p);
            },
        },
        NewExpression: {
            enter(p) {
                callVisitor(p);
                astTagNewExpression(p);
            },
        },
        TaggedTemplateExpression: {
            enter(p) { astTagFrameworkTaggedTemplate(p); },
        },

        VariableDeclarator: {
            enter(p) {
                taintTagVariableDeclarator(p);
                dataflowVariableDeclarator(p);
                importTagVariableDeclarator(p);
            },
        },

        ImportDeclaration: {
            enter(p) {
                if (!p.node.loc) return;
                if (!p.node.source || p.node.source.type !== 'StringLiteral') return;
                const sourceModule = p.node.source.value;
                const line = p.node.loc.start.line;
                for (const spec of p.node.specifiers || []) {
                    if (spec.type === 'ImportDefaultSpecifier') {
                        importMap.push({
                            local_name: spec.local.name,
                            source_module: sourceModule,
                            imported_name: 'default',
                            line,
                        });
                        if (sourceModule === 'child_process') {
                            childProcessAliases.add(spec.local.name);
                        }
                    } else if (spec.type === 'ImportNamespaceSpecifier') {
                        importMap.push({
                            local_name: spec.local.name,
                            source_module: sourceModule,
                            imported_name: '*',
                            line,
                        });
                        if (sourceModule === 'child_process') {
                            childProcessAliases.add(spec.local.name);
                        }
                    } else if (spec.type === 'ImportSpecifier') {
                        const imported = spec.imported;
                        const importedName =
                            imported.type === 'Identifier'    ? imported.name  :
                            imported.type === 'StringLiteral' ? imported.value :
                            null;
                        if (!importedName) continue;
                        importMap.push({
                            local_name: spec.local.name,
                            source_module: sourceModule,
                            imported_name: importedName,
                            line,
                        });
                        if (sourceModule === 'child_process') {
                            childProcessLocals.add(spec.local.name);
                        }
                    }
                }
            },
        },

        AssignmentExpression: {
            enter(p) {
                astTagAssignment(p);
                astTagProtoAssignment(p);
                taintTagAssignment(p);
                dataflowAssignment(p);
            },
        },

        ReturnStatement: {
            enter(p) { dataflowReturnStatement(p); },
        },
        MemberExpression: {
            enter(p) {
                astTagMemberExpression(p);
                astTagFrameworkMember(p);
            },
        },
        OptionalMemberExpression: {
            enter(p) {
                astTagMemberExpression(p);
                astTagFrameworkMember(p);
            },
        },
        JSXAttribute: {
            enter(p) { astTagJSXAttribute(p); },
        },
    });

    function astTagAssignment(p) {
        if (!p.node.loc) return;
        const left = p.node.left;
        const mem  = resolveMemberAccess(left);
        if (!mem) return;
        const line = p.node.loc.start.line;
        const col  = p.node.loc.start.column;

        const ENRICHED_RULES = new Set([
            'innerHTML_assign', 'outerHTML_assign',
            'srcdoc_assign', 'location_href_assign',
        ]);
        const enrichLast = () => {
            const last = astTags[astTags.length - 1];
            if (!last || !ENRICHED_RULES.has(last.rule_id)) return;
            const collapsed = collapseStringy(p.node.right, p.get('right'));
            if (collapsed) last.context.value = collapsed.template;
        };

        if (mem.property === 'innerHTML' || mem.property === 'outerHTML') {
            astTags.push({
                rule_id: `${mem.property}_assign`,
                kind: 'sink', line, col,
                context: {
                    object: mem.object,
                    property: mem.property,
                    receiver_kind: left.object ? left.object.type : 'unknown',
                },
            });
            enrichLast();
        }
        if (mem.property === 'srcdoc') {
            astTags.push({
                rule_id: 'srcdoc_assign', kind: 'sink', line, col,
                context: { object: mem.object, property: 'srcdoc',
                           receiver_kind: left.object ? left.object.type : 'unknown' },
            });
            enrichLast();
        }
        if (/^on[a-z]+$/.test(mem.property)) {
            const rhs = p.node.right;
            const rhsIsFunction =
                rhs.type === 'FunctionExpression' ||
                rhs.type === 'ArrowFunctionExpression';
            if (!rhsIsFunction) {
                astTags.push({
                    rule_id: 'event_handler_attr_assign', kind: 'sink', line, col,
                    context: { object: mem.object, property: mem.property,
                               rhs_type: rhs.type },
                });
            }
        }
        if (mem.property === 'href' &&
            (mem.object === 'location' ||
             mem.object.endsWith('.location') ||
             mem.object === 'window.location' ||
             mem.object === 'document.location')) {
            astTags.push({
                rule_id: 'location_href_assign', kind: 'sink', line, col,
                context: { object: mem.object, property: 'href' },
            });
            enrichLast();

            // URL extraction: location.href = "..."
            const collapsed = collapseStringy(p.node.right, p.get('right'));
            if (collapsed) {
                extractedUrls.push({
                    url:          collapsed.template,
                    type:         'locationAssignment',
                    method:       'GET',
                    query_params: parseQueryParams(collapsed.template),
                    body_params:  [],
                    line,
                    in_function:  stack.length ? stack[stack.length - 1].name : null,
                });
            }
        }
    }

    function astTagProtoAssignment(p) {
        if (!p.node.loc) return;
        const left = p.node.left;
        if (!left || (left.type !== 'MemberExpression' &&
                      left.type !== 'OptionalMemberExpression')) return;
        const line = p.node.loc.start.line;
        const col  = p.node.loc.start.column;
        const obj  = left.object;
        let ruleId = null;

        if (left.computed) {
            // obj[key] = val where obj is __proto__ or X.prototype
            let isProtoTarget = false;
            if (obj && obj.type === 'Identifier' && obj.name === '__proto__') {
                isProtoTarget = true;
            } else if (obj &&
                       (obj.type === 'MemberExpression' ||
                        obj.type === 'OptionalMemberExpression') &&
                       !obj.computed &&
                       obj.property && obj.property.type === 'Identifier' &&
                       obj.property.name === 'prototype') {
                isProtoTarget = true;
            }
            if (isProtoTarget) ruleId = 'proto_assign_bracket';
        } else {
            // __proto__.foo = val
            if (obj && obj.type === 'Identifier' && obj.name === '__proto__') {
                ruleId = 'proto_assign_direct';
            }
        }
        if (!ruleId) return;

        astTags.push({
            rule_id: ruleId, kind: 'source', line, col,
            context: { object: obj && obj.type === 'Identifier' ? obj.name : '<member>',
                       computed: !!left.computed },
        });

        if (stack.length) {
            const facts = ensureFacts(stack[stack.length - 1].name);
            facts.push({ kind: 'pp_write', rule_id: ruleId, line });
        }
    }

    function astTagMemberExpression(p) {
        if (!p.node.loc) return;
        const mem = resolveMemberAccess(p.node);
        if (!mem) return;
        const line = p.node.loc.start.line;
        const col  = p.node.loc.start.column;
        const isWrite = isAssignmentLHS(p);

        const LOC_SOURCES = {
            hash:     'location_hash',
            search:   'location_search',
            pathname: 'location_pathname',
        };
        if (!isWrite &&
            (mem.object === 'location' ||
             mem.object === 'window.location' ||
             mem.object === 'document.location') &&
            LOC_SOURCES[mem.property]) {
            astTags.push({
                rule_id: LOC_SOURCES[mem.property], kind: 'source', line, col,
                context: { object: mem.object, property: mem.property },
            });
        }
        if (!isWrite && mem.property === 'href' &&
            (mem.object === 'location' ||
             mem.object === 'window.location' ||
             mem.object === 'document.location')) {
            astTags.push({
                rule_id: 'location_href_read', kind: 'source', line, col,
                context: { object: mem.object, property: 'href' },
            });
        }
        const DOC_SOURCES = {
            URL:          'document_URL',
            documentURI:  'document_documentURI',
            baseURI:      'document_baseURI',
            referrer:     'document_referrer',
            cookie:       'document_cookie',
        };
        if (!isWrite &&
            (mem.object === 'document' || mem.object === 'window.document') &&
            DOC_SOURCES[mem.property]) {
            astTags.push({
                rule_id: DOC_SOURCES[mem.property], kind: 'source', line, col,
                context: { object: mem.object, property: mem.property },
            });
        }
        if (!isWrite && mem.property === 'name' &&
            (mem.object === 'window' || mem.object === 'globalThis')) {
            astTags.push({
                rule_id: 'window_name', kind: 'source', line, col,
                context: { object: mem.object, property: 'name' },
            });
        }
        if (!isWrite && mem.property === 'data' &&
            /^(event|e|msg|message|ev)$/.test(mem.object) &&
            isMessageHandlerContext(p)) {
            astTags.push({
                rule_id: 'message_event_data_read', kind: 'source', line, col,
                context: { object: mem.object, property: 'data' },
            });
        }
    }

    function astTagCallExpression(p) {
        if (!p.node.loc) return;
        const node = p.node;
        const line = node.loc.start.line;
        const col  = node.loc.start.column;
        const callee = node.callee;

        if (callee.type === 'Identifier' && callee.name === 'eval') {
            astTags.push({
                rule_id: 'eval_call', kind: 'sink', line, col,
                context: { arg_count: node.arguments.length },
            });
        }
        const isIndirectEval =
            (callee.type === 'SequenceExpression' &&
             callee.expressions.length >= 2 &&
             callee.expressions[callee.expressions.length - 1].type === 'Identifier' &&
             callee.expressions[callee.expressions.length - 1].name === 'eval') ||
            ((callee.type === 'MemberExpression' || callee.type === 'OptionalMemberExpression') &&
             callee.object.type === 'Identifier' &&
             (callee.object.name === 'globalThis' || callee.object.name === 'window') &&
             callee.property.type === 'Identifier' &&
             callee.property.name === 'eval');
        if (isIndirectEval) {
            astTags.push({ rule_id: 'eval_indirect', kind: 'sink', line, col, context: {} });
        }
        const TIMER_SINKS = ['setTimeout', 'setInterval', 'setImmediate'];
        if (callee.type === 'Identifier' && TIMER_SINKS.includes(callee.name)) {
            const firstArg = node.arguments[0];
            if (firstArg) {
                const argIsFunction =
                    firstArg.type === 'FunctionExpression' ||
                    firstArg.type === 'ArrowFunctionExpression';
                if (!argIsFunction) {
                    astTags.push({
                        rule_id: `${callee.name}_string`, kind: 'sink', line, col,
                        context: {
                            arg_type: firstArg.type,
                            arg_is_string_literal: firstArg.type === 'StringLiteral',
                        },
                    });
                }
            }
        }
        const mem = resolveMemberAccess(callee);
        if (mem && (mem.object === 'document' || mem.object === 'window.document') &&
            (mem.property === 'write' || mem.property === 'writeln')) {
            astTags.push({
                rule_id: `document_${mem.property}`, kind: 'sink', line, col,
                context: { object: mem.object, property: mem.property },
            });
        }
        if (mem && mem.property === 'insertAdjacentHTML') {
            astTags.push({
                rule_id: 'insertAdjacentHTML_call', kind: 'sink', line, col,
                context: { object: mem.object },
            });
        }
        if (mem && mem.property === 'setAttribute') {
            const firstArg = node.arguments[0];
            if (firstArg && firstArg.type === 'StringLiteral') {
                const DANGEROUS_ATTRS = new Set([
                    'href','src','srcdoc','action','formaction',
                    'background','cite','codebase','profile','usemap',
                    'xlink:href','xml:base','data',
                ]);
                const attrName = firstArg.value.toLowerCase();
                if (DANGEROUS_ATTRS.has(attrName) || attrName.startsWith('on')) {
                    astTags.push({
                        rule_id: 'setAttribute_dangerous_attr', kind: 'sink', line, col,
                        context: { object: mem.object, attr: firstArg.value },
                    });
                }
            }
        }
        if (mem && mem.object &&
            (mem.object === 'location' ||
             mem.object === 'window.location' ||
             mem.object === 'document.location') &&
            (mem.property === 'assign' || mem.property === 'replace')) {
            astTags.push({
                rule_id: `location_${mem.property}_call`, kind: 'sink', line, col,
                context: { object: mem.object, property: mem.property },
            });
        }
        if (callee.type === 'MemberExpression' || callee.type === 'OptionalMemberExpression') {
            const innerObj = callee.object;
            const prop = callee.property;
            if (prop.type === 'Identifier' && prop.name === 'get' &&
                (innerObj.type === 'MemberExpression' || innerObj.type === 'OptionalMemberExpression') &&
                innerObj.property.type === 'Identifier' &&
                innerObj.property.name === 'searchParams') {
                astTags.push({
                    rule_id: 'searchParams_get', kind: 'source', line, col,
                    context: { form: 'chained' },
                });
            }
        }

        // ── SSRF / outbound HTTP sinks ───────────────────────────────────
        const calleeIsFetchBare =
            callee.type === 'Identifier' && callee.name === 'fetch';
        const calleeIsFetchScoped =
            (callee.type === 'MemberExpression' || callee.type === 'OptionalMemberExpression') &&
            !callee.computed &&
            callee.property.type === 'Identifier' &&
            callee.property.name === 'fetch' &&
            callee.object.type === 'Identifier' &&
            (callee.object.name === 'window' || callee.object.name === 'globalThis');
        if (calleeIsFetchBare || calleeIsFetchScoped) {
            const arg0 = node.arguments[0];
            astTags.push({
                rule_id: 'fetch_call', kind: 'sink', line, col,
                context: {
                    scoped: calleeIsFetchScoped,
                    arg0_line: arg0 && arg0.loc ? arg0.loc.start.line : null,
                },
            });
        }

        const calleeIsAxiosBare =
            callee.type === 'Identifier' && callee.name === 'axios';
        const AXIOS_METHODS = ['get','post','put','delete','patch','request','head','options'];
        const calleeIsAxiosMember =
            (callee.type === 'MemberExpression' || callee.type === 'OptionalMemberExpression') &&
            !callee.computed &&
            callee.object.type === 'Identifier' &&
            callee.object.name === 'axios' &&
            callee.property.type === 'Identifier' &&
            AXIOS_METHODS.includes(callee.property.name);
        if (calleeIsAxiosBare || calleeIsAxiosMember) {
            astTags.push({
                rule_id: 'axios_call', kind: 'sink', line, col,
                context: {
                    method: calleeIsAxiosMember ? callee.property.name : 'request',
                },
            });
        }

        // XMLHttpRequest.open(method, url) — restrict to ExpressionStatement
        // parent so chained / assigned `.open` calls (string.open etc.) don't fire.
        if ((callee.type === 'MemberExpression' || callee.type === 'OptionalMemberExpression') &&
            !callee.computed &&
            callee.property.type === 'Identifier' &&
            callee.property.name === 'open' &&
            node.arguments.length >= 2 &&
            p.parent && p.parent.type === 'ExpressionStatement') {
            astTags.push({
                rule_id: 'xhr_open_call', kind: 'sink', line, col,
                context: {
                    arg_count: node.arguments.length,
                },
            });
        }

        // ── URL extraction (Phase 2) ─────────────────────────────────
        const urlLine    = line;
        const inFuncName = stack.length ? stack[stack.length - 1].name : null;

        // fetch(url, options?) / window.fetch(url, options?)
        const isFetchBare = callee.type === 'Identifier' && callee.name === 'fetch';
        const isFetchScoped =
            (callee.type === 'MemberExpression' ||
             callee.type === 'OptionalMemberExpression') &&
            callee.property.type === 'Identifier' &&
            callee.property.name === 'fetch' &&
            callee.object.type === 'Identifier' &&
            (callee.object.name === 'window' || callee.object.name === 'globalThis');
        if (isFetchBare || isFetchScoped) {
            const urlArg = node.arguments[0];
            if (urlArg) {
                const collapsed = collapseStringy(urlArg, p.get('arguments.0'));
                if (collapsed) {
                    let method = 'GET';
                    const opts = node.arguments[1];
                    if (opts && opts.type === 'ObjectExpression') {
                        for (const prop of opts.properties || []) {
                            if (prop.key &&
                                ((prop.key.type === 'Identifier'    && prop.key.name  === 'method') ||
                                 (prop.key.type === 'StringLiteral' && prop.key.value === 'method')) &&
                                prop.value && prop.value.type === 'StringLiteral') {
                                method = prop.value.value.toUpperCase();
                            }
                        }
                    }
                    extractedUrls.push({
                        url:          collapsed.template,
                        type:         'fetch',
                        method,
                        query_params: parseQueryParams(collapsed.template),
                        body_params:  [],
                        line:         urlLine,
                        in_function:  inFuncName,
                    });
                }
            }
        }

        // XMLHttpRequest.open(method, url)
        if ((callee.type === 'MemberExpression' ||
             callee.type === 'OptionalMemberExpression') &&
            callee.property.type === 'Identifier' &&
            callee.property.name === 'open' &&
            node.arguments.length >= 2) {
            const methodArg = node.arguments[0];
            const urlArg    = node.arguments[1];
            const method    = (methodArg && methodArg.type === 'StringLiteral')
                              ? methodArg.value.toUpperCase() : null;
            if (urlArg) {
                const collapsed = collapseStringy(urlArg, p.get('arguments.1'));
                if (collapsed) {
                    extractedUrls.push({
                        url:          collapsed.template,
                        type:         'xhr',
                        method:       method || 'GET',
                        query_params: parseQueryParams(collapsed.template),
                        body_params:  [],
                        line:         urlLine,
                        in_function:  inFuncName,
                    });
                }
            }
        }

        // location.assign(url) / location.replace(url)
        if ((callee.type === 'MemberExpression' ||
             callee.type === 'OptionalMemberExpression') &&
            callee.property.type === 'Identifier' &&
            (callee.property.name === 'assign' || callee.property.name === 'replace')) {
            const obj = callee.object;
            const isLocation =
                (obj.type === 'Identifier' && obj.name === 'location') ||
                (obj.type === 'MemberExpression' && !obj.computed &&
                 obj.property.type === 'Identifier' && obj.property.name === 'location');
            if (isLocation && node.arguments[0]) {
                const collapsed = collapseStringy(node.arguments[0], p.get('arguments.0'));
                if (collapsed) {
                    extractedUrls.push({
                        url:          collapsed.template,
                        type:         callee.property.name === 'assign'
                                      ? 'locationAssign' : 'locationReplace',
                        method:       'GET',
                        query_params: parseQueryParams(collapsed.template),
                        body_params:  [],
                        line:         urlLine,
                        in_function:  inFuncName,
                    });
                }
            }
        }

        // window.open(url) / open(url)
        const isOpenBare = callee.type === 'Identifier' && callee.name === 'open';
        const isOpenScoped =
            (callee.type === 'MemberExpression' ||
             callee.type === 'OptionalMemberExpression') &&
            callee.property.type === 'Identifier' &&
            callee.property.name === 'open' &&
            callee.object.type === 'Identifier' &&
            (callee.object.name === 'window' || callee.object.name === 'globalThis');
        if (isOpenBare || isOpenScoped) {
            const urlArg = node.arguments[0];
            if (urlArg) {
                const collapsed = collapseStringy(urlArg, p.get('arguments.0'));
                if (collapsed) {
                    extractedUrls.push({
                        url:          collapsed.template,
                        type:         'window.open',
                        method:       'GET',
                        query_params: parseQueryParams(collapsed.template),
                        body_params:  [],
                        line:         urlLine,
                        in_function:  inFuncName,
                    });
                }
            }
        }

        // jQuery family
        if (callee.type === 'MemberExpression' &&
            !callee.computed &&
            callee.object.type === 'Identifier' &&
            (callee.object.name === '$' || callee.object.name === 'jQuery') &&
            callee.property.type === 'Identifier') {
            const jMethod = callee.property.name;

            if (jMethod === 'get' || jMethod === 'getJSON' || jMethod === 'load') {
                const urlArg = node.arguments[0];
                if (urlArg) {
                    const collapsed = collapseStringy(urlArg, p.get('arguments.0'));
                    if (collapsed) {
                        extractedUrls.push({
                            url:          collapsed.template,
                            type:         `$.${jMethod}`,
                            method:       'GET',
                            query_params: parseQueryParams(collapsed.template),
                            body_params:  [],
                            line:         urlLine,
                            in_function:  inFuncName,
                        });
                    }
                }
            }

            if (jMethod === 'post') {
                const urlArg  = node.arguments[0];
                const dataArg = node.arguments[1];
                if (urlArg) {
                    const collapsed = collapseStringy(urlArg, p.get('arguments.0'));
                    if (collapsed) {
                        extractedUrls.push({
                            url:          collapsed.template,
                            type:         '$.post',
                            method:       'POST',
                            query_params: parseQueryParams(collapsed.template),
                            body_params:  extractBodyParams(dataArg),
                            line:         urlLine,
                            in_function:  inFuncName,
                        });
                    }
                }
            }

            if (jMethod === 'ajax') {
                const optsArg = node.arguments[0];
                if (optsArg && optsArg.type === 'ObjectExpression') {
                    let ajaxUrl    = null;
                    let ajaxMethod = 'GET';
                    let ajaxData   = null;
                    let urlPropIdx = -1;
                    optsArg.properties.forEach((pr, i) => {
                        if (!pr.key) return;
                        const k = pr.key.type === 'Identifier'    ? pr.key.name
                                : pr.key.type === 'StringLiteral' ? pr.key.value
                                : null;
                        if (k === 'url') {
                            ajaxUrl    = pr.value;
                            urlPropIdx = i;
                        }
                        if (k === 'method' || k === 'type') {
                            if (pr.value && pr.value.type === 'StringLiteral')
                                ajaxMethod = pr.value.value.toUpperCase();
                        }
                        if (k === 'data') ajaxData = pr.value;
                    });
                    if (ajaxUrl) {
                        const urlPath = urlPropIdx >= 0
                            ? p.get(`arguments.0.properties.${urlPropIdx}.value`)
                            : null;
                        const collapsed = collapseStringy(ajaxUrl, urlPath);
                        if (collapsed) {
                            extractedUrls.push({
                                url:          collapsed.template,
                                type:         '$.ajax',
                                method:       ajaxMethod,
                                query_params: parseQueryParams(collapsed.template),
                                body_params:  extractBodyParams(ajaxData),
                                line:         urlLine,
                                in_function:  inFuncName,
                            });
                        }
                    }
                }
            }
        }
    }

    function astTagNewExpression(p) {
        if (!p.node.loc) return;
        const node = p.node;
        const line = node.loc.start.line;
        const col  = node.loc.start.column;
        const callee = node.callee;

        if (callee.type === 'Identifier' && callee.name === 'Function') {
            astTags.push({
                rule_id: 'new_Function', kind: 'sink', line, col,
                context: { arg_count: node.arguments.length },
            });
        }
        if (callee.type === 'Identifier' && callee.name === 'URLSearchParams') {
            astTags.push({
                rule_id: 'URLSearchParams_ctor', kind: 'source', line, col,
                context: {},
            });
        }
    }

    function astTagJSXAttribute(p) {
        if (!p.node.loc) return;
        const name = p.node.name;
        if (!name) return;
        const attrName = name.type === 'JSXIdentifier' ? name.name
                       : name.type === 'JSXNamespacedName' ? `${name.namespace.name}:${name.name.name}`
                       : null;
        if (attrName === 'dangerouslySetInnerHTML') {
            astTags.push({
                rule_id: 'dangerouslySetInnerHTML', kind: 'sink',
                line: p.node.loc.start.line,
                col:  p.node.loc.start.column,
                context: {},
            });
        }
    }

    function importTagVariableDeclarator(p) {
        if (!p.node.loc) return;
        const init = p.node.init;
        const id   = p.node.id;
        if (!init || !id) return;

        let requireCall = null;
        let memberProp  = null;
        if (init.type === 'CallExpression'
            && init.callee.type === 'Identifier'
            && init.callee.name === 'require') {
            requireCall = init;
        } else if ((init.type === 'MemberExpression' || init.type === 'OptionalMemberExpression')
            && !init.computed
            && init.object.type === 'CallExpression'
            && init.object.callee.type === 'Identifier'
            && init.object.callee.name === 'require'
            && init.property.type === 'Identifier') {
            requireCall = init.object;
            memberProp  = init.property.name;
        }
        if (!requireCall) return;
        if (!requireCall.arguments || requireCall.arguments.length === 0) return;
        const arg0 = requireCall.arguments[0];
        if (!arg0 || arg0.type !== 'StringLiteral') return;
        const sourceModule = arg0.value;
        const line = p.node.loc.start.line;

        if (id.type === 'Identifier') {
            importMap.push({
                local_name: id.name,
                source_module: sourceModule,
                imported_name: memberProp || 'default',
                line,
            });
            if (sourceModule === 'child_process') {
                if (memberProp) childProcessLocals.add(id.name);
                else childProcessAliases.add(id.name);
            }
        } else if (id.type === 'ObjectPattern') {
            for (const prop of id.properties || []) {
                if (prop.type === 'RestElement') continue;
                if (!prop.key) continue;
                let keyName = null;
                if (prop.key.type === 'Identifier')        keyName = prop.key.name;
                else if (prop.key.type === 'StringLiteral') keyName = prop.key.value;
                if (!keyName) continue;
                let localName = null;
                if (prop.value && prop.value.type === 'Identifier') {
                    localName = prop.value.name;
                } else if (prop.value && prop.value.type === 'AssignmentPattern'
                           && prop.value.left.type === 'Identifier') {
                    localName = prop.value.left.name;
                }
                if (!localName) continue;
                importMap.push({
                    local_name: localName,
                    source_module: sourceModule,
                    imported_name: keyName,
                    line,
                });
                if (sourceModule === 'child_process') {
                    childProcessLocals.add(localName);
                }
            }
        }
    }

    function taintTagVariableDeclarator(p) {
        if (!p.node.loc || !stack.length) return;
        const fnEntry = stack[stack.length - 1];
        const facts = ensureFacts(fnEntry.name);

        const id = p.node.id;
        if (!id) return;
        const init = p.node.init;
        if (!init) return;

        if (id.type !== 'Identifier') {
            if (id.type === 'ObjectPattern') {
                const initSourceRule = isSourceCallOrAccess(init);
                const argVars = extractIdentifiers(init);
                const line = p.node.loc.start.line;
                for (const prop of id.properties || []) {
                    if (prop.type === 'RestElement') {
                        for (const name of extractPatternNames(prop.argument)) {
                            facts.push({ kind: 'var_assign', name, line, source: null, sanitiser: null, arg_vars: argVars });
                        }
                        continue;
                    }
                    let propSource = null;
                    if (prop.key && !prop.computed) {
                        const synth = { type: 'MemberExpression', object: init, property: prop.key, computed: false };
                        propSource = isSourceCallOrAccess(synth);
                    }
                    const sourceRule = propSource || initSourceRule;
                    for (const name of extractPatternNames(prop.value)) {
                        if (sourceRule) {
                            facts.push({ kind: 'var_init', name, line, source: sourceRule });
                        } else {
                            facts.push({ kind: 'var_assign', name, line, source: null, sanitiser: null, arg_vars: argVars });
                        }
                    }
                }
            } else if (id.type === 'ArrayPattern') {
                const boundNames = extractPatternNames(id);
                const sourceRule = isSourceCallOrAccess(init);
                const argVars = extractIdentifiers(init);
                const line = p.node.loc.start.line;
                for (const name of boundNames) {
                    if (sourceRule) {
                        facts.push({ kind: 'var_init', name, line, source: sourceRule });
                    } else {
                        facts.push({ kind: 'var_assign', name, line, source: null, sanitiser: null, arg_vars: argVars });
                    }
                }
            }
            return;
        }
        const varName = id.name;

        const sourceRule = isSourceCallOrAccess(init);
        const sanitiserRule = isSanitiserCall(init);
        const argVars = extractIdentifiers(init);

        if (sanitiserRule) {
            facts.push({
                kind: 'sanitiser_use',
                taxonomy_id: sanitiserRule,
                line: p.node.loc.start.line,
                arg_vars: init.arguments && init.arguments.length > 0
                    ? extractIdentifiers(init.arguments[0]) : [],
                target_var: varName,
            });
            return;
        }

        if (sourceRule) {
            facts.push({
                kind: 'var_init',
                name: varName,
                line: p.node.loc.start.line,
                source: sourceRule,
            });
            return;
        }

        facts.push({
            kind: 'var_assign',
            name: varName,
            line: p.node.loc.start.line,
            source: null,
            sanitiser: null,
            arg_vars: argVars,
        });
    }

    function taintTagAssignment(p) {
        if (!p.node.loc || !stack.length) return;
        const fnEntry = stack[stack.length - 1];
        const facts = ensureFacts(fnEntry.name);
        const rhs = p.node.right;

        const sinkRule = isSinkExpression(p.node, rhs, -1);
        if (sinkRule) {
            facts.push({
                kind: 'sink_use',
                rule_id: sinkRule,
                line: p.node.loc.start.line,
                arg_vars: extractIdentifiers(rhs),
            });
        }

        if (p.node.left.type !== 'Identifier') return;

        const varName = p.node.left.name;
        const sourceRule = isSourceCallOrAccess(rhs);
        const sanitiserRule = isSanitiserCall(rhs);
        const argVars = extractIdentifiers(rhs);

        if (sanitiserRule) {
            facts.push({
                kind: 'sanitiser_use',
                taxonomy_id: sanitiserRule,
                line: p.node.loc.start.line,
                arg_vars: rhs.arguments && rhs.arguments.length > 0
                    ? extractIdentifiers(rhs.arguments[0]) : [],
                target_var: varName,
            });
            return;
        }

        facts.push({
            kind: 'var_assign',
            name: varName,
            line: p.node.loc.start.line,
            source: sourceRule || null,
            sanitiser: null,
            arg_vars: argVars,
        });
    }

    function taintTagCallExpression(p) {
        if (!p.node.loc || !stack.length) return;
        const node = p.node;
        const fnEntry = stack[stack.length - 1];
        const facts = ensureFacts(fnEntry.name);

        // Pre-taint URL parameter on fetch/axios calls so the intra-procedural
        // solver flags `function f(url) { fetch(url) }` even when no source
        // assignment precedes the call inside this function.
        const callee0 = node.callee;
        const AXIOS_METHODS_T = ['get','post','put','delete','patch','request','head','options'];
        const isFetchT =
            (callee0.type === 'Identifier' && callee0.name === 'fetch') ||
            ((callee0.type === 'MemberExpression' || callee0.type === 'OptionalMemberExpression') &&
             !callee0.computed &&
             callee0.property.type === 'Identifier' &&
             callee0.property.name === 'fetch' &&
             callee0.object.type === 'Identifier' &&
             (callee0.object.name === 'window' || callee0.object.name === 'globalThis'));
        const isAxiosT =
            (callee0.type === 'Identifier' && callee0.name === 'axios') ||
            ((callee0.type === 'MemberExpression' || callee0.type === 'OptionalMemberExpression') &&
             !callee0.computed &&
             callee0.object.type === 'Identifier' &&
             callee0.object.name === 'axios' &&
             callee0.property.type === 'Identifier' &&
             AXIOS_METHODS_T.includes(callee0.property.name));
        if ((isFetchT || isAxiosT) && node.arguments[0]
            && node.arguments[0].type === 'Identifier') {
            facts.push({
                kind: 'source_arg',
                rule_id: isFetchT ? 'fetch_call' : 'axios_call',
                var: node.arguments[0].name,
                line: node.loc.start.line,
            });
        }

        for (let i = 0; i < (node.arguments || []).length; i++) {
            const arg = node.arguments[i];
            const sinkRule = isSinkExpression(node, arg, i);
            if (sinkRule) {
                facts.push({
                    kind: 'sink_use',
                    rule_id: sinkRule,
                    line: node.loc.start.line,
                    arg_vars: extractIdentifiers(arg),
                });
            }
        }

        const parentNode = p.parent;
        if (parentNode && parentNode.type === 'AssignmentExpression' && parentNode.right === node) {
            const sinkRule = isSinkExpression(parentNode, node, -1);
            if (sinkRule) {
                facts.push({
                    kind: 'sink_use',
                    rule_id: sinkRule,
                    line: node.loc.start.line,
                    arg_vars: extractIdentifiers(node),
                });
            }
        }

        const sanitiserRule = isSanitiserCall(node);
        if (sanitiserRule) {
            const parent = p.parent;
            const alreadyHandled =
                (parent && parent.type === 'VariableDeclarator' && parent.init === node) ||
                (parent && parent.type === 'AssignmentExpression' && parent.right === node
                 && parent.left.type === 'Identifier');
            if (!alreadyHandled) {
                facts.push({
                    kind: 'sanitiser_use',
                    taxonomy_id: sanitiserRule,
                    line: node.loc.start.line,
                    arg_vars: node.arguments.length > 0
                        ? extractIdentifiers(node.arguments[0]) : [],
                    target_var: null,
                });
            }
        }
    }

    function dataflowVariableDeclarator(p) {
        if (!p.node.loc || !stack.length) return;
        const id = p.node.id;
        if (!id) return;
        const fnEntry = stack[stack.length - 1];
        const line = p.node.loc.start.line;

        if (id.type !== 'Identifier') {
            if (id.type === 'ObjectPattern' || id.type === 'ArrayPattern') {
                const boundNames = extractPatternNames(id);
                const init2 = p.node.init;
                if (!init2) return;
                const edges = ensureEdges(fnEntry.name);
                const fromVars = extractIdentifiers(init2);
                const sanitiser = isSanitiserCall(init2);
                for (const toName of boundNames) {
                    recordVar(fnEntry.name, toName, line);
                    for (const fromVar of fromVars) {
                        edges.push({ from: fromVar, to: toName, edge_kind: 'assign', line, sanitiser: sanitiser || null });
                    }
                    if (fromVars.length === 0 && isSourceCallOrAccess(init2)) {
                        edges.push({ from: null, to: toName, edge_kind: 'assign', line, sanitiser: null });
                    }
                }
            }
            return;
        }
        recordVar(fnEntry.name, id.name, line);

        const init = p.node.init;
        if (!init) return;
        const edges = ensureEdges(fnEntry.name);
        const fromVars = extractIdentifiers(init);
        const sanitiser = isSanitiserCall(init);

        for (const fromVar of fromVars) {
            edges.push({
                from: fromVar,
                to: id.name,
                edge_kind: 'assign',
                line,
                sanitiser: sanitiser || null,
            });
        }
        if (fromVars.length === 0 && isSourceCallOrAccess(init)) {
            edges.push({
                from: null,
                to: id.name,
                edge_kind: 'assign',
                line,
                sanitiser: null,
            });
        }
    }

    function dataflowAssignment(p) {
        if (!p.node.loc || !stack.length) return;
        if (p.node.left.type !== 'Identifier') return;
        const fnEntry = stack[stack.length - 1];
        const line = p.node.loc.start.line;
        const toVar = p.node.left.name;
        recordVar(fnEntry.name, toVar, line);

        const rhs = p.node.right;
        const edges = ensureEdges(fnEntry.name);
        const fromVars = extractIdentifiers(rhs);
        const sanitiser = isSanitiserCall(rhs);

        for (const fromVar of fromVars) {
            edges.push({
                from: fromVar,
                to: toVar,
                edge_kind: 'assign',
                line,
                sanitiser: sanitiser || null,
            });
        }
        if (fromVars.length === 0 && isSourceCallOrAccess(rhs)) {
            edges.push({
                from: null,
                to: toVar,
                edge_kind: 'assign',
                line,
                sanitiser: null,
            });
        }
    }

    function astTagFrameworkMember(p) {
        if (!p.node.loc) return;
        const mem = resolveMemberAccess(p.node);
        if (!mem) return;
        if (isAssignmentLHS(p)) return;
        const line = p.node.loc.start.line;
        const col  = p.node.loc.start.column;

        // Express req.{body,query,params,headers,cookies,files,file,signedCookies}
        if (hasFw('express', 'node_http')
            && mem.object === 'req'
            && Object.prototype.hasOwnProperty.call(EXPRESS_REQ_PROPS, mem.property)) {
            const ruleId = EXPRESS_REQ_PROPS[mem.property];
            astTags.push({
                rule_id: ruleId, kind: 'source',
                severity: EXPRESS_REQ_SEVERITY[ruleId] || 'high',
                line, col,
                context: { object: 'req', property: mem.property },
            });
        }

        // Next.js API route req.{body,query,cookies}
        if (hasFw('next') && /\/api\//.test(fileRel)
            && mem.object === 'req'
            && (mem.property === 'body' || mem.property === 'query'
                || mem.property === 'cookies')) {
            astTags.push({
                rule_id: 'nextjs_api_req', kind: 'source', severity: 'high',
                line, col,
                context: { object: 'req', property: mem.property, form: 'api_route' },
            });
        }

        // Next.js searchParams.<x> / searchParams[<x>]
        if (hasFw('next') && mem.object === 'searchParams') {
            astTags.push({
                rule_id: 'nextjs_searchparams', kind: 'source', severity: 'high',
                line, col,
                context: { property: mem.property },
            });
        }

        // Angular ActivatedRoute params / queryParams / queryParamMap / snapshot
        if (hasFw('angular')) {
            const objLooksRoute =
                mem.object === 'route' ||
                mem.object === 'this.route' ||
                mem.object === 'activatedRoute';
            if (objLooksRoute && ANGULAR_ROUTE_PROPS.has(mem.property)) {
                astTags.push({
                    rule_id: 'angular_activatedroute_params',
                    kind: 'source', severity: 'high',
                    line, col,
                    context: { object: mem.object, property: mem.property },
                });
            }
        }
    }

    function astTagFrameworkCall(p) {
        if (!p.node.loc) return;
        const node = p.node;
        const line = node.loc.start.line;
        const col  = node.loc.start.column;
        const callee = node.callee;
        const mem = callee ? resolveMemberAccess(callee) : null;

        // Angular bypassSecurityTrust*
        if (hasFw('angular') && mem
            && /^bypassSecurityTrust(?:Html|Script|ResourceUrl|Style|Url)$/
                .test(mem.property)) {
            astTags.push({
                rule_id: 'angular_bypass_trust_html',
                kind: 'sink', severity: 'critical',
                line, col,
                context: { method: mem.property },
            });
        }

        // child_process exec / spawn
        if (hasFw('node', 'electron')) {
            let triggered = null;
            let methodName = null;
            if (callee && callee.type === 'Identifier'
                && childProcessLocals.has(callee.name)) {
                methodName = callee.name;
                if (CHILD_PROCESS_EXEC_NAMES.has(methodName))   triggered = 'exec';
                if (CHILD_PROCESS_SPAWN_NAMES.has(methodName))  triggered = 'spawn';
            } else if (mem && (childProcessAliases.has(mem.object)
                               || mem.object === 'child_process')) {
                methodName = mem.property;
                if (CHILD_PROCESS_EXEC_NAMES.has(methodName))   triggered = 'exec';
                if (CHILD_PROCESS_SPAWN_NAMES.has(methodName))  triggered = 'spawn';
            }
            if (triggered) {
                astTags.push({
                    rule_id: triggered === 'exec'
                        ? 'child_process_exec_sink'
                        : 'child_process_spawn_sink',
                    kind: 'sink',
                    severity: triggered === 'exec' ? 'critical' : 'high',
                    line, col,
                    context: { method: methodName },
                });
            }
        }

        // SQL raw query — CallExpression with TemplateLiteral / BinaryExpression
        if (hasFw('db', 'node')
            && mem && SQL_RAW_METHODS.has(mem.property)
            && node.arguments.length > 0) {
            const arg0 = node.arguments[0];
            const interpolated =
                (arg0.type === 'TemplateLiteral'
                 && arg0.expressions && arg0.expressions.length > 0) ||
                (arg0.type === 'BinaryExpression' && arg0.operator === '+');
            if (interpolated) {
                astTags.push({
                    rule_id: 'sql_injection_sink',
                    kind: 'sink', severity: 'critical',
                    line, col,
                    context: { method: mem.property, form: 'call' },
                });
            }
        }

        // NoSQL injection — Mongoose/MongoDB query helpers
        if (hasFw('db') && mem && NOSQL_METHODS.has(mem.property)) {
            const arg0 = node.arguments[0];
            if (arg0 && !isLiteralOnlyObject(arg0)) {
                astTags.push({
                    rule_id: 'nosql_injection_sink',
                    kind: 'sink', severity: 'high',
                    line, col,
                    context: { method: mem.property },
                });
            }
        }

        // Path traversal — fs.* with dynamic path argument
        if (hasFw('node', 'electron')
            && mem && mem.object === 'fs'
            && FS_PATH_TRAVERSAL_METHODS.has(mem.property)) {
            astTags.push({
                rule_id: 'path_traversal_sink',
                kind: 'sink', severity: 'high',
                line, col,
                context: { method: mem.property },
            });
        }

        // Electron shell.openExternal / webContents.executeJavaScript
        if (hasFw('electron')) {
            if (mem && mem.object === 'shell'
                && mem.property === 'openExternal') {
                astTags.push({
                    rule_id: 'electron_shell_openexternal',
                    kind: 'sink', severity: 'high',
                    line, col, context: {},
                });
            }
            if (mem && mem.object === 'webContents'
                && mem.property === 'executeJavaScript') {
                astTags.push({
                    rule_id: 'electron_nodeintegration_sink',
                    kind: 'sink', severity: 'critical',
                    line, col, context: {},
                });
            }
        }
    }

    function astTagFrameworkTaggedTemplate(p) {
        if (!p.node.loc) return;
        if (!hasFw('db', 'node')) return;
        const mem = resolveMemberAccess(p.node.tag);
        if (!mem || !SQL_RAW_METHODS.has(mem.property)) return;
        const quasi = p.node.quasi;
        if (!quasi || quasi.type !== 'TemplateLiteral') return;
        if (!quasi.expressions || quasi.expressions.length === 0) return;
        astTags.push({
            rule_id: 'sql_injection_sink',
            kind: 'sink', severity: 'critical',
            line: p.node.loc.start.line,
            col:  p.node.loc.start.column,
            context: { method: mem.property, form: 'tagged' },
        });
    }

    function dataflowReturnStatement(p) {
        if (!p.node.loc || !stack.length || !p.node.argument) return;
        const fnEntry = stack[stack.length - 1];
        const edges = ensureEdges(fnEntry.name);
        const line = p.node.loc.start.line;
        const fromVars = extractIdentifiers(p.node.argument);
        for (const fromVar of fromVars) {
            edges.push({
                from: fromVar,
                to: ':return',
                edge_kind: 'return',
                line,
                sanitiser: null,
            });
        }
    }

    for (const fn of functions) {
        fn.taint_facts = taintFactsByFunction.get(fn.name) || [];
        fn.variables   = variablesByFunction.get(fn.name) || [];
        fn.dataflow    = dataflowByFunction.get(fn.name) || [];
    }

    functions.sort((a, b) => a.start - b.start || b.end - a.end);
    astTags.sort((a, b) => a.line - b.line || a.col - b.col);
    extractedUrls.sort((a, b) => a.line - b.line);
    importMap.sort((a, b) => a.line - b.line);
    return { functions, ast_tags: astTags, extracted_urls: extractedUrls, import_map: importMap };
}

const out = {};
let okCount = 0, errCount = 0;

for (const entry of entries) {
    const { abs, rel } = entry;
    try {
        const { functions, ast_tags, extracted_urls, import_map } = extractOne(abs, rel);
        out[rel] = { ok: true, functions, ast_tags, extracted_urls, import_map };
        okCount++;
    } catch (err) {
        out[rel] = { ok: false, error: err.message || String(err) };
        errCount++;
    }
}

fs.writeFileSync(outputPath, JSON.stringify(out));
console.error(`ast_extractor: ${okCount} ok, ${errCount} errors`);
