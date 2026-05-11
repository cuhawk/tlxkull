#!/usr/bin/env node
/*
 * ast_rewrite.js — precise identifier rewrite via Babel AST.
 *
 * Usage:
 *   node ast_rewrite.js <source_file> <rewrite_map_json>
 *
 * For each Identifier node whose name matches a key in rewrite_map,
 * the node is replaced with a Literal whose value parses from the
 * mapped JSON-encoded literal. Output goes to stdout.
 *
 * Exit 0 on success, 1 on error (diagnostics on stderr).
 */
'use strict';

const fs = require('fs');
const path = require('path');

function fail(msg) {
  process.stderr.write(`ast_rewrite: ${msg}\n`);
  process.exit(1);
}

const args = process.argv.slice(2);
if (args.length < 2) {
  fail('usage: ast_rewrite.js <source_file> <rewrite_map_json>');
}

const [srcPath, mapJson] = args;

let rewriteMap;
try {
  rewriteMap = JSON.parse(mapJson);
} catch (e) {
  fail(`rewrite_map_json parse failed: ${e.message}`);
}

if (typeof rewriteMap !== 'object' || rewriteMap === null) {
  fail('rewrite_map must be a JSON object');
}

let source;
try {
  source = fs.readFileSync(srcPath, 'utf-8');
} catch (e) {
  fail(`source read failed: ${e.message}`);
}

let parser, traverse, generator;
try {
  parser = require('@babel/parser');
  traverse = require('@babel/traverse').default;
  generator = require('@babel/generator').default;
} catch (e) {
  fail(`babel deps missing: ${e.message}`);
}

let ast;
try {
  ast = parser.parse(source, {
    sourceType: 'unambiguous',
    allowReturnOutsideFunction: true,
    allowAwaitOutsideFunction: true,
    errorRecovery: true,
    plugins: ['jsx', 'typescript', 'classProperties', 'optionalChaining'],
  });
} catch (e) {
  fail(`parse failed: ${e.message}`);
}

function literalNodeFor(rawJson) {
  let parsed;
  try {
    parsed = JSON.parse(rawJson);
  } catch (e) {
    return { type: 'StringLiteral', value: String(rawJson) };
  }
  if (typeof parsed === 'string') {
    return { type: 'StringLiteral', value: parsed };
  }
  if (typeof parsed === 'number') {
    return { type: 'NumericLiteral', value: parsed };
  }
  if (typeof parsed === 'boolean') {
    return { type: 'BooleanLiteral', value: parsed };
  }
  if (parsed === null) {
    return { type: 'NullLiteral' };
  }
  return { type: 'StringLiteral', value: rawJson };
}

try {
  traverse(ast, {
    Identifier(p) {
      const name = p.node.name;
      if (!Object.prototype.hasOwnProperty.call(rewriteMap, name)) {
        return;
      }
      // Only replace standalone references, not declarations/property keys.
      if (p.parent && p.parent.type === 'VariableDeclarator' &&
          p.parent.id === p.node) {
        return;
      }
      if (p.parent && p.parent.type === 'FunctionDeclaration' &&
          p.parent.id === p.node) {
        return;
      }
      if (p.parent && (p.parent.type === 'ObjectProperty' ||
                       p.parent.type === 'Property') &&
          p.parent.key === p.node && !p.parent.computed) {
        return;
      }
      if (p.parent && p.parent.type === 'MemberExpression' &&
          p.parent.property === p.node && !p.parent.computed) {
        return;
      }
      p.replaceWith(literalNodeFor(rewriteMap[name]));
    },
  });
} catch (e) {
  fail(`traverse failed: ${e.message}`);
}

let out;
try {
  out = generator(ast, { retainLines: true }, source).code;
} catch (e) {
  fail(`generate failed: ${e.message}`);
}

process.stdout.write(out);
process.exit(0);
