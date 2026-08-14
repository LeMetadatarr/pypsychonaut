# Prerelease quirks

This file tracks user-visible changes, deprecations, and known transient quirks
since the last stable release. Entries are newest first. The file is reset at
each stable release.

## 0.0.1a4

- Add effects catalog, Erowid experience crawlers, reagent queries, and full-wiki page-text fetch.
- `pypsychonaut.experiences` accepts `--substances PATH` and a `substances=`
  parameter to skip the live `Summary_index` HTML fetch when it is blocked.
