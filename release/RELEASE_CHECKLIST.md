# Public release checklist

Before creating the stable public tag:

- [x] Final repository name selected: `jlabroc-jsrt-mrmc-python`.
- [x] Distribution/import/CLI names confirmed.
- [x] Software author for `CITATION.cff`: Junji Shiraishi.
- [x] Licensing basis reviewed by the software author; Junji Shiraishi selected as copyright holder.
- [x] BSD-3-Clause adopted; root `LICENSE` added.
- [x] Stable version metadata set to `1.0.0`.
- [x] Local ordinary test suite passed (`18 passed`).
- [x] Local archived-reference numerical validation passed (`Overall: PASS`).
- [x] Local systematic simulation validation passed (`Overall: PASS`; JLABROC 57 regular/stress + 2 controlled-degenerate, MRMC 35/35).
- [ ] Push the exact `1.0.0` tree to GitHub.
- [ ] Confirm every GitHub Actions job is green on Windows, macOS, and Linux.
- [ ] Download and archive the six numerical-validation artifacts from the final `1.0.0` workflow run.
- [ ] Record the final Git commit hash in the manuscript and research record.
- [ ] Change repository visibility to Public.
- [ ] Create the stable GitHub Release/tag `v1.0.0` only after the checks above are complete.
