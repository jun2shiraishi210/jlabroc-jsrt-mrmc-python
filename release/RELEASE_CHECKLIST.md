# Maintenance release checklist

## v1.0.2

- [x] Version metadata updated to 1.0.2.
- [x] Python project identifier and console command standardized as `jlabroc_jsrt_mrmc`.
- [x] README, Quick Start guides, and beginner user guide updated for the underscore-form command.
- [x] Python 3.10-3.12 tested range documented.
- [x] Linux PEP 668 installation guidance added.
- [x] Numerical algorithms, validation datasets, and numerical references unchanged.
- [ ] Confirm all GitHub Actions jobs are green.
- [ ] Create tag/release `v1.0.2` after CI passes.

---

## v1.0.1

- [x] Version metadata updated to 1.0.1.
- [x] Original JSRT-MRMC reader-block input parser added without changing numerical algorithms.
- [x] Legacy reader-block fixture verified to match the existing validated 100 x 10 matrix exactly.
- [x] Ordinary local test suite passed.
- [x] Archived-reference numerical validation passed.
- [x] Systematic simulation validation passed.
- [ ] Push the v1.0.1 maintenance commit to GitHub.
- [ ] Confirm all GitHub Actions jobs are green.
- [ ] Create tag/release `v1.0.1` after CI passes.

---

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
