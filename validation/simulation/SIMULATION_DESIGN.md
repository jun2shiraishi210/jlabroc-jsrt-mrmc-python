# Systematic simulation validation design

## Purpose

The systematic simulation suite is designed for **implementation-equivalence
and stress testing** between the Python implementation and frozen full-precision
numerical references from the validated legacy implementations. It is not
intended to estimate clinical observer-variability parameters or to reproduce a
specific clinical population.

## JLABROC regular simulation grid

The regular grid contains 48 deterministic continuous-rating datasets:

- negative/positive case configurations: 25/25, 50/50, 100/100, and 100/25;
- target AUC: 0.60, 0.70, 0.80, and 0.90; and
- target binormal parameter `b`: 0.75, 1.00, and 1.25.

Actually negative ratings are sampled from `N(0,1)`. For target AUC `Az` and
binormal parameter `b`, the target parameter `a` is

`a = sqrt(1 + b^2) * Phi^-1(Az)`.

With the negative standard deviation fixed at 1, the positive standard
deviation is `1/b` and the positive mean is `a/b`. Fixed random seeds and all
generator settings are recorded in `simulation_manifest.json`.

## JLABROC stress conditions

Nine additional fittable datasets evaluate:

- tied ratings produced by rounding;
- very small sample sizes;
- unequal negative/positive sample sizes;
- low and very high discrimination; and
- reversed discrimination.

Two intentionally non-fittable datasets evaluate controlled error handling for
all-tied ratings and perfect separation. The JLABROC suite therefore contains
59 datasets in total.

## MRMC generator

The MRMC generator creates two-system paired rating data from a shared case
component and independent residual noise, with additional reader and
treatment-reader effects. The independent residual standard deviation defines
the latent rating scale and is fixed at 1.0.

For each truth state, the random component is

`sqrt(rho_case) * shared_case + sqrt(1-rho_case) * independent_noise`.

Thus, `rho_case` is a **generator-level shared-case variance fraction**. It is
not treated as a clinical correlation coefficient or as a specific Roe-Metz
variance component.

Reader effects and treatment-reader effects are added to the positive-case
location so that reader-specific and system-reader-specific discrimination can
vary across datasets.

## MRMC factorial stress grid

The factorial grid varies three generator parameters:

- shared-case fraction `rho_case`: 0.0, 0.5, 0.9;
- reader-effect SD: 0.0, 0.2, 0.4; and
- treatment-reader-effect SD: 0.0, 0.2, 0.4.

The two SD factors are standardized relative to unit residual SD and are
implementation-stress levels rather than clinical variance estimates. The full
3 x 3 x 3 grid yields 27 datasets with 5 readers, 50 negative cases, 50 positive
cases, and target AUCs 0.80 and 0.76 for the two systems.

## Additional MRMC design/AUC stress conditions

Eight additional deterministic datasets broaden the design across:

- 3 to 8 readers;
- balanced and unbalanced negative/positive case counts;
- target system AUCs from 0.56 to 0.95;
- zero and nonzero target AUC differences; and
- different shared-case, reader, and treatment-reader effect settings.

The MRMC suite therefore contains 35 datasets in total: 27 factorial datasets
and 8 design/AUC stress datasets.

For descriptive transparency, the manifest records the realized mean
same-reader cross-system Pearson correlations separately for negative and
positive cases. These finite-sample correlations are not validation acceptance
criteria.

## Numerical references and outputs

Frozen full-precision reference results are stored in JSON files under
`reference/`. See `REFERENCE_PROVENANCE.md` for provenance information.

The simulation validator produces:

- a human-readable log;
- a detailed CSV containing per-dataset/per-metric differences; and
- a summary CSV containing the maximum absolute difference for each metric.

The GitHub Actions workflow runs this validation on Windows, macOS, and Linux
with Python 3.11.
