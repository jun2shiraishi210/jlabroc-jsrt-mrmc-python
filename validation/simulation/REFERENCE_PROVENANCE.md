# Simulation reference provenance

The simulation-reference JSON files are frozen full-precision numerical outputs
created from the author's archived legacy implementations. The legacy source
code itself is not distributed in this repository.

Archived source packages used during reference generation:

- `JLABROC4.zip` SHA-256: `b558300b7763a93ce3b976fae262be18563ae6c783e5c5ef1e282bb53c242aaf`
- `JSRT_MRMC_0609.zip` SHA-256: `240f2d215849d49669e335e6cac52696118c1c439ce51ebdc6a458b16574be27`

The frozen JLABROC references cover all 59 systematic simulation/stress
datasets. The frozen MRMC references cover all 35 systematic simulation/stress
datasets and include reader AUCs, jackknife pseudo-values, confidence-interval
bounds, ANOVA terms, F statistic, degrees of freedom, and p value.

The source-package hashes are retained to document the provenance of the
numerical reference records used for regression testing.
