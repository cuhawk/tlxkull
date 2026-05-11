---
id: auto_explore
kind: workflow
title: Auto-explore workflow
tags: [workflow, indexing, search-first]
always_include: false
priority: 60
---

Workflow:
1. list_files on allowed folder
2. index_codebase on it (skips fresh files, fast on subsequent runs)
3. semantic_search for patterns relevant to the task
4. read_file only for specific files the search identified
