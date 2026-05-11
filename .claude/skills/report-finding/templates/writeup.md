# {{title}}

**Target:** {{target_program}}
**Endpoint / asset:** {{endpoint_or_asset}}
**Severity (estimated):** {{cvss_score}} ({{cvss_vector}})
**Class:** {{bug_class}}
**Discovered:** {{discovered_utc}}
**Reporter:** {{reporter}}
**Tooling:** TLX js_analyzer + mock_backend, Caido, chrome-devtools-mcp

---

## Summary

{{one_paragraph_summary}}

## Impact

{{concrete_impact_paragraph}}

## Reproduction steps

1. {{step_1}}
2. {{step_2}}
3. {{step_3}}
4. Observe: {{observation}}

## Proof of concept

### HTML payload
```html
{{poc_html}}
```

### Curl
```bash
{{poc_curl}}
```

### Browser script (paste into DevTools console)
```js
{{poc_console}}
```

## Network evidence
- HAR: `findings/{{id}}/network.har`
- Screenshot(s): `findings/{{id}}/screenshots/`

## Root cause
{{root_cause_explanation}}

Relevant source (from sourcemap-explode):

```
{{relevant_source_excerpt}}
```

Chain (from js_analyzer):
- Source: `{{source_qname}}` at `{{source_file}}:{{source_line}}`
- Sink:   `{{sink_qname}}` at `{{sink_file}}:{{sink_line}}`
- Path length: {{path_length}}
- Framework: {{framework}}

## Remediation

{{remediation_paragraph}}

Suggested fix sketch:
```js
{{fix_sketch}}
```

## References

- CWE: {{cwe_id}} — {{cwe_title}}
- OWASP: {{owasp_ref}}
- Related wiki pages: {{wiki_links}}

## Metadata (machine-readable)

```yaml
finding_id: "{{id}}"
target: "{{target_program}}"
chain_ids: [{{chain_ids}}]
sarif: "findings/{{id}}/{{id}}.sarif"
opus_cost_usd: {{opus_cost}}
confirmed_mode: "{{confirmed_mode}}"   # live | mock
confirmed_at_utc: "{{confirmed_utc}}"
```
