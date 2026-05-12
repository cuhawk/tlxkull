---
title: protoscope — protobuf decode/encode CLI
slug: protoscope-notes
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [tool/protoscope]
inbound: []
---

# protoscope

CLI utility by Google for human-readable encode/decode of wire-format (binary)
protobuf without needing a `.proto` schema. Useful for fuzzing protobuf
endpoints where you have a captured binary blob but no schema.

GitHub: <https://github.com/protocolbuffers/protoscope>

## Core workflow

```bash
# Decode binary protobuf to text representation
protoscope < captured.bin

# Edit text, re-encode back to binary
protoscope -s < edited.txt > modified.bin

# Base64-encode for Caido replay (avoids stray-byte issues)
base64 modified.bin | tr -d '\n' > modified.b64

# In Caido: paste base64 value and add a "base64 decode" step in the workflow
# so the binary lands correctly in the request body
```

## Text format quick reference

```
1: {"hello world"}     # field 1, wire type 2 (string/bytes)
2: 42                  # field 2, wire type 0 (varint)
3: {                   # field 3, wire type 2 (embedded message)
  1: {"nested"}
}
4: 3.14                # field 4, wire type 5 (32-bit float) or 1 (64-bit)
```

## Tips for fuzzing without a schema

1. Decode a valid captured payload → understand the field numbering.
2. Tweak values one field at a time; re-encode; send.
3. If you need to brute-force field meanings, increment/decrement field
   numbers and observe changes in server behavior.
4. Use protoscope's `--explicit-wire-types` flag to see raw wire type
   annotations (helpful when fields are ambiguous).

## Caido integration

Justin Gardner's workflow (CT Ep. 170):

1. Modify payload as base64 in Caido.
2. Add a Caido workflow step: **base64 decode** before the request is sent.
3. This guarantees no ASCII-mangling of binary bytes in the Caido UI.

For raw binary protobuf XSS (form POST scenario) see:
`../../techniques/dom-xss/post-based-protobuf-xss.md`

## Sources

- CT Ep. 170 — `../../sources/podcasts/ct/20260416_1hef7eS-GIk_Claude_Code_+_Tmux_Websockets_and_Other_Korea_LHE_Takeaways_Ep._170.en.vtt`
- CT Ep. 171 — `../../sources/podcasts/ct/20260423_l5fs7Okdj3o_Path-Scoped_Cookie_Hacks_with_Uppercase_Post-based_Raw_Protobuf_XSS_Ep_171.en.vtt`
