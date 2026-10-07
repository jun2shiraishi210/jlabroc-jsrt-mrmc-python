# JLABROC/JSRT-MRMC Python 1.0.1

Version 1.0.1 is a maintenance release that adds direct input compatibility
with the original two-system JSRT-MRMC reader-block text format.

## What changed

- Added a legacy JSRT-MRMC reader-block parser.
- Kept the existing numeric matrix input format unchanged.
- Added automatic format detection for the `mrmc` command.
- Added regression tests confirming that legacy reader-block input is converted
  to exactly the same internal matrix as the validated matrix fixture.
- Added tolerant handling of historical separator lines containing a single
  `*`; the canonical two-system legacy separator remains `* *`.
- Updated package version metadata and input-format documentation.

## Numerical algorithms

No JLABROC fitting, jackknife pseudo-value, ANOVA, confidence-interval, or
degrees-of-freedom calculation was changed in this release.

## Local verification before release

- Ordinary test suite: 22 passed.
- Archived-reference numerical validation: Overall PASS.
- Systematic simulation validation: Overall PASS; JLABROC 57 fittable + 2
  controlled-degenerate conditions, JSRT-MRMC 35/35 datasets.
- The historical five-reader, 50-negative, 50-positive reader-block test file
  produced mean AUCs 0.8647 and 0.8058, difference 0.0589, F 13.2157,
  df (1, 9), and p 0.005440, matching the validated matrix-format analysis.

GitHub Actions should be run on the release commit before tagging `v1.0.1`.
