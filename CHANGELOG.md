# Changelog

## 1.0.0

- First stable public release of JLABROC/JSRT-MRMC Python.
- Promoted the validated 0.7.0rc3 computational implementation without numerical algorithm changes.
- Includes BSD-3-Clause licensing, citation metadata, input-format documentation, archived-reference validation, systematic simulation validation, and cross-platform CI.
- Final release validation is intended to be run once more on the tagged 1.0.0 commit before making the repository public.

## 0.7.0rc3

- Synchronized all internal version metadata with the release-candidate version.
- Removed a development-history note from MRMC reference metadata and replaced it with a neutral stress-design description.
- Marked the licensing decision as reviewed by the software author.
- No numerical algorithm, dataset, numerical-reference value, or validation-design changes from 0.7.0rc2.

## 0.7.0rc2

- Adopted the BSD 3-Clause License with Junji Shiraishi as copyright holder.
- Added final `CITATION.cff` metadata with Junji Shiraishi as the software author.
- Added repository metadata to `pyproject.toml`.
- Updated public documentation and release checklist for citation and licensing.
- No numerical algorithm or validation-design changes from 0.7.0rc1.

## 0.7.0rc1

- Prepared the codebase for public release without changing the validated numerical algorithms.
- Adopted the release-candidate project name `JLABROC/JSRT-MRMC Python`.
- Renamed the Python package to `jlabroc_jsrt_mrmc` and the CLI to `jlabroc-jsrt-mrmc`.
- Rewrote public documentation to describe the final validation design rather than development history.
- Added explicit input-format documentation and a public-release checklist.
- Added draft citation and BSD-3-Clause license metadata for author/rights review.

## v0.6.0

- Redesigned MRMC systematic validation to remove dependence on one fixed, empirically uncalibrated variance/correlation setting.
- Added a 3 x 3 x 3 factorial MRMC stress grid: shared-case fraction 0.0/0.5/0.9, reader-effect SD 0.0/0.2/0.4, and treatment-reader-effect SD 0.0/0.2/0.4.
- Defined reader/treatment-reader SDs relative to unit residual SD and documented them explicitly as implementation-stress levels rather than clinical variance estimates.
- Added eight complementary MRMC design/AUC stress datasets; total MRMC synthetic datasets increased from 8 to 35.
- Added realized same-reader cross-system correlations to the simulation manifest for descriptive transparency.
- Regenerated frozen full-precision C/C++ references for all 35 v0.6 MRMC datasets.
- Retained the 59-dataset JLABROC simulation/stress suite unchanged.
- Development validation: 18 ordinary tests passed and systematic simulation validation completed with Overall PASS.

## v0.5.0

- Added deterministic systematic simulation/stress validation.
- Added 48 regular JLABROC binormal simulation datasets covering four case configurations, four target AUCs, and three binormal b values.
- Added nine fittable JLABROC stress datasets and two intentionally non-fittable datasets.
- Added eight paired synthetic MRMC datasets varying readers, case balance, and target AUC conditions.
- Added frozen full-precision C/C++ references for all v0.5 simulation datasets, including MRMC jackknife pseudo-values.
- Added detailed and summary simulation-validation CSV output.
- Added simulation-reference smoke tests; total ordinary tests now 18.
- Updated GitHub Actions to run systematic simulation validation on Windows, macOS, and Linux.
- Updated GitHub Actions JavaScript actions to current Node.js 24-compatible major versions.
- Updated documentation to record successful v0.4 cross-platform validation.

## v0.4.0

- Prepared GitHub Actions cross-platform CI for Windows, macOS, and Linux.
- Added Python 3.10, 3.11, and 3.12 test matrix.
- Added absolute-path and spaces-in-path CLI regression tests for both JLABROC and MRMC workflows.
- Expanded validation environment reporting (OS, architecture, Python compiler, executable, NumPy, SciPy).
- Added `--log` option to `validation/run_validation.py` so validation output can be saved while still being displayed.
- Preserved the exact legacy tie-order swap sequence while replacing slow NumPy row swaps with equivalent Python-list swaps, reducing MRMC validation runtime without changing numerical results.

## v0.3.0

- Expanded numerical regression validation against archived full-precision C/C++ reference outputs.
