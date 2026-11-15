# FlameBound Mathematical and Physical Framework

**Status:** Draft 0.1 — framework for team review, to be reconciled with the NASA records before any outcome model is fitted.

## Purpose and boundary

FlameBound will compare documented solid-fuel combustion experiments with user-specified atmospheric and flow conditions. It will calculate quantities that follow directly from reported inputs, describe which parts of the requested condition space are represented by experiments, and fit an empirical spread model only if the verified data support one. It is not a universal combustion simulator, material certification, or a habitat safety assessment.

The dataset is expected to span distinct apparatuses and protocols. NASA's BASS description, for example, identifies thin flat samples and concurrent-flow spread measurements; that is not interchangeable by default with a different investigation's geometry or flow configuration. We will retain investigation identity and source provenance and assess comparability before pooling. See NASA's [BASS overview](https://www.nasa.gov/wp-content/uploads/2025/07/burning-and-suppression-of-solids-bass.pdf) and [PSI investigation catalogue](https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/).

## Scientific question

Among the solid-fuel test conditions actually represented in the selected NASA investigations, how are reported flame outcomes and spread measurements associated with oxygen fraction, total pressure, flow, fuel/sample properties, and gravity category? For a proposed condition, how close is it to those tests, and which requested conclusions would require extrapolation?

The primary outputs are evidence summaries and coverage diagnostics. A probability of sustained spread is a conditional statistical estimate, not a fire-safety probability, and is allowed only after a data-feasibility and validation review.

## Variables and observational unit

The observational unit is one test/run condition with a documented outcome. If a run contains several samples or time windows, they must not be counted as independent rows without a justified data model.

| Role | Variables | Notes |
|---|---|---|
| Atmosphere | Oxygen mole fraction `X_O2`; total pressure `P`; diluent/species composition; initial temperature `T_inf` | Store the reported values and units. Keep oxygen fraction and total pressure separate. |
| Flow | Speed `U`; direction relative to spread; apparatus/configuration; measurement location | Flow categories and measurement definitions may differ between studies. |
| Fuel/sample | Material or fuel class; thickness; width; orientation; geometry; relevant thermal properties when available | A broad material label is not a substitute for measured properties. |
| Gravity | Reported condition, encoded as investigation-supported categories such as microgravity and 1 g | Do not interpolate to lunar gravity or infer partial-gravity behaviour from these two categories. |
| Outcomes | Sustained spread, extinction, blow-off, ignition failure, other, unknown; spread rate and flame length where measured | Do not recode an unreported or ambiguous outcome as extinction. Keep continuous measurements separate from categorical outcomes. |
| Provenance | Investigation/run ID, source file, page/table/figure/record, extraction method, verifier, notes | Every derived row and displayed result must be traceable. |

## Direct atmospheric calculations

### Oxygen partial pressure

\[
p_{O_2}=X_{O_2}P
\]

`X_O2` is a mole fraction in `[0, 1]`; `P` and `p_O2` use the same pressure unit. This is a composition identity for a gas mixture under the usual partial-pressure convention. It does not assert that combustion response depends only on partial pressure.

### Oxygen mass fraction

For a mixture with species mole fractions `X_j` and molecular masses `M_j`:

\[
Y_{O_2}=\frac{X_{O_2}M_{O_2}}{\sum_j X_j M_j}.
\]

For a binary oxygen/balance-gas mixture this reduces to

\[
Y_{O_2}=\frac{X_{O_2}M_{O_2}}{X_{O_2}M_{O_2}+(1-X_{O_2})M_{dil}}.
\]

The binary formula is invalid if the remainder contains multiple gases with materially different molecular masses unless `M_dil` is their mole-fraction-weighted mean molecular mass. The full composition is preferred. Mole fraction is not mass fraction.

### Unit conversion and scenario comparison

Unit conversion functions must declare supported source and target units and reject unknown or incompatible units. For two atmospheres, report each atmosphere's `X_O2`, `P`, and derived `p_O2`, with absolute and relative differences only where the reference value is nonzero. A comparison is descriptive; it does not imply equal flame behaviour when one quantity matches.

As an arithmetic example only, `0.30 × 10.2 psi = 3.06 psi` oxygen partial pressure. The inputs represent a proposed design point from the project brief, not a verified NASA test condition.

## Physics quantities and when they are evaluable

These quantities may help describe regimes or construct features. They are not interchangeable with observed outcomes and should not be presented as predictions unless a specified model and validation support that use.

### Reynolds number

\[
Re=\frac{\rho U L}{\mu}=\frac{UL}{\nu}.
\]

Requires representative gas density `rho`, dynamic viscosity `mu` (or kinematic viscosity `nu`), characteristic length `L`, and a comparable velocity `U`. Composition, temperature, and pressure may affect gas properties. If properties are unavailable, do not invent them from nominal conditions without recording the property model and uncertainty.

### Grashof number

\[
Gr=\frac{g\,\beta\,\Delta T\,L^3}{\nu^2}.
\]

Requires effective acceleration `g`, thermal expansion coefficient `beta`, temperature difference `Delta T`, length `L`, and kinematic viscosity `nu`; it is a buoyancy-to-viscous scaling for an appropriate regime. Use only with matched definitions and properties. For microgravity, record the experiment's gravity condition; do not silently substitute exact zero or a lunar value. Gravity remains categorical in the first evidence/model version.

### Damköhler number

The general meaning is a ratio of a flow/transport timescale to a chemical-reaction timescale, e.g. `Da = t_flow / t_chem`. A particular formulation must identify the characteristic length and velocity and a kinetic timescale (or reaction rate law). The proposed expression `Da ~ (L/U) P^(n-1) X_O2^m exp(-E/(R T_f))` is not ready to implement: the rate constant, units, reaction order, reference-state convention, and dimensions of the prefactor are unspecified. Treat it as a possible scaling hypothesis, not a defined dimensionless number, until a source-specific derivation and required kinetic data are established.

### Spalding mass-transfer number

The project brief's proposed oxygen-based expression combines an oxygen-side heat-release term with a fuel-side sensible-heating term and calls the result a Spalding number. The normalization and mass/energy basis are not fully defined there. Classical Spalding mass-transfer and heat-transfer numbers depend on boundary-state definitions and a particular transport model. Do not implement that expression under the standard name until the exact formulation, species basis, units, and applicable boundary conditions are checked against a cited source. Fuel heat of gasification, stoichiometry, surface state, and gas composition may be required and may not exist in the PSI record.

### Thermally thin flame-spread scaling

De Ris-type analyses give idealized spread-rate relations for specified flame/fuel configurations. A useful dimensional scaling has the form

\[
V_f \propto \frac{\lambda_g}{\rho_s c_s \tau}
\frac{T_f-T_v}{T_v-T_\infty},
\]

where `lambda_g` is a gas thermal conductivity, `rho_s` and `c_s` are solid density and specific heat, `tau` is a characteristic half-thickness, `T_f` is an appropriate flame temperature, `T_v` is a vaporization/pyrolysis temperature, and `T_inf` is the initial fuel/environment temperature. The prefactor and exact definitions depend on the formulation. This is not a universal law for all sample geometries or near-limit flames; it assumes an applicable thermally thin regime and idealizations about flame structure and heat transfer. We may use it to motivate variables, but will not calculate `V_f` from it unless the needed measurements, geometry, and source-specific formulation are available. See de Ris, [“Spread of a laminar diffusion flame”](https://doi.org/10.1016/S0082-0784(69)80407-8), and NASA's [Flame Spread Theory report](https://ntrs.nasa.gov/api/citations/19930004527/downloads/19930004527.pdf).

## Evidence coverage and extrapolation

### Mixed-variable distance candidate

For query `x*` and test row `x_i`, a Gower-style distance is

\[
D_G(x^*,x_i)=\frac{\sum_{k\in A_i} w_k\,\delta_k(x^*,x_i)}{\sum_{k\in A_i}w_k},
\]

where `A_i` is the set of features observed for both records, `w_k >= 0` is a declared feature weight, and `delta_k` is a per-feature dissimilarity. For a numeric feature, a candidate dissimilarity is `abs(x*_k - x_ik)/R_k`, where `R_k` is a documented, nonzero reference range; for a nominal category it is 0 for a match and 1 otherwise. Pairwise missing values are omitted from numerator and denominator, but the output must also include the fraction of total feature weight compared. Constant-range numeric features cannot discriminate rows and are excluded with a recorded reason.

The candidate `d_ext` is the mean of the three smallest eligible distances. It is a design choice, not a calibrated probability or universal threshold. Return the neighbour IDs and distances so the result is inspectable. Eligibility must enforce compatible gravity, fuel/geometry scope, and flow configuration where necessary; otherwise a mathematically close but physically incomparable experiment may dominate. Freeze the feature set, weights, ranges, eligibility rules, and coverage-grade thresholds before showing grades in the UI.

### Convex-hull flag

For a selected continuous feature space, a query inside the convex hull of observed points is “inside this geometric hull,” not “validated” or “safe.” A query outside is evidence of extrapolation on that representation. Hull membership depends on selected dimensions and the included rows; it does not handle categorical mismatch or missing variables. Compute it only for a declared compatible subset and report degeneracy or insufficient-point cases instead of returning a misleading flag.

## Outcome model, conditional on a data-feasibility review

If there are enough independent, verified outcomes and adequate overlap, a candidate regularised logistic model is

\[
\operatorname{logit}\Pr(Y_i=1)=\beta_0+\beta_1X_{O_2,i}+\beta_2\ln U_i+\beta_3(\ln U_i)^2+\beta_4\ln P_i+\boldsymbol{\gamma}^{T}F_i+u_{j[i]},
\]

where `Y_i=1` means a consistently defined sustained-spread outcome, `F_i` encodes a justified fuel class, and `u_{j[i]}` is an investigation-level effect. This is an empirical association/prediction model, not a first-principles solver. `U` and `P` must be positive and consistently defined for the logarithms. Zero or near-zero flow requires a physically justified treatment; it must not be hidden with an arbitrary epsilon. If investigation count is too small for a defensible random effect, do not force one; preserve investigation grouping in validation and report the limitation.

Keep `p_O2` out of a model that already includes both `X_O2` and `P` unless a specific estimand and identifiability analysis justify it, because `p_O2` is their deterministic product. Check predictor overlap/confounding, sample size, outcome balance, and label comparability before fitting. A rough minimum-events-per-predictor screen is only a warning heuristic, not a guarantee of reliable estimates.

Validation, if fitted:

- Hold out entire investigations (leave-one-investigation-out) rather than randomly splitting rows from the same investigation across training and test.
- Compare against a simple oxygen-only baseline and report log loss, Brier score, discrimination and calibration with uncertainty where estimable.
- Report per-investigation results and failures; sparse data may make some metrics undefined or very uncertain.
- Test whether coverage distance is associated with held-out prediction error, without treating that association as proof the distance is calibrated.
- If the model does not beat a baseline or cannot be evaluated credibly, publish the negative result and retain descriptive coverage/gap analysis.

## Required data and current feasibility

For every candidate test row, the team should provide raw and normalized values, units, source provenance, extraction confidence, and notes. Required core fields are investigation/run IDs, gravity condition, outcome wording and normalized label, oxygen fraction, total pressure, flow speed/direction/configuration, fuel identity/class, sample geometry/thickness, and source location. Optional physics features include temperature, gas composition, density/viscosity/conductivity, solid density/heat capacity/conductivity, ignition details, flame/spread measurements, and kinetic/thermochemical properties with their sources.

Raw PSI tables and source documents are now present and have an initial audit, but no row has passed verification for the harmonised dataset. Therefore no verified cross-investigation outcome counts, coverage distances, model coefficients, or uncertainty estimates can be calculated. See `docs/data_audit_report.md` and `docs/scientific_review/model_readiness_assessment.md` for the current evidence state and next steps. The existing row audits are source-preserving review artifacts, not model-ready observations.

## Implementation contract and validation record

Each deterministic function must document its equation, units, accepted ranges, assumptions, failure behavior, and return units. Reject invalid fractions, non-finite values, negative absolute pressure, nonpositive values where a logarithm is required, and incompatible units. Include source/provenance IDs in functions that summarize experimental evidence. Validate implementations with hand-calculated examples, boundary cases, invalid-input cases, and independent checks against published values when available.

The direct atmospheric calculations—pressure-unit conversion, oxygen partial pressure, binary-mixture oxygen mass fraction for an explicitly verified diluent, and atmosphere comparison—are implemented in `modelling/atmospheric.py` and documented in `docs/atmospheric_engine.md`. The typed calculation layer is independent of the NASA outcome dataset. Coverage and statistical modules should wait for the team schema and verified rows.

## Assumption and equation register

| Item | Initial status | Required before implementation/use |
|---|---|---|
| `p_O2 = X_O2 P` | Direct calculation | Validate fraction and common pressure units |
| General oxygen mass fraction | Direct calculation with composition | Full mixture composition or explicit binary balance-gas assumption |
| Unit conversion / atmosphere comparison | Direct calculation | Explicit supported unit table and zero-reference handling |
| `Re`, `Gr` | Conditional derived features | Matched geometry, gas properties, temperatures, and velocity definitions |
| Damköhler scaling | Not specified enough | Cite and derive a dimensionless formulation; obtain kinetic/rate inputs |
| Proposed Spalding expression | Not verified as stated | Verify canonical definition and bases; obtain thermochemical/surface inputs |
| De Ris-type spread relation | Regime-specific scaling | Verify exact formulation, thin-fuel assumptions, parameters and applicability |
| Gower-style coverage distance | Candidate evidence diagnostic | Freeze features, ranges, weights, missingness, comparability and grade rules |
| Logistic boundary model | Conditional statistical model | Verified labels, independent groups, overlap, feasible sample, grouped validation |
| Partial/lunar-gravity prediction | Out of scope | Requires relevant partial-gravity observations and validation |

## References

- International Union of Pure and Applied Chemistry (IUPAC), [“pressure”](https://goldbook.iupac.org/terms/view/P04819), *Compendium of Chemical Terminology*, 5th ed. (2025), DOI: [10.1351/goldbook.P04819](https://doi.org/10.1351/goldbook.P04819). Defines the gas-mixture partial pressure relation `p_i = x_i p`.
- International Union of Pure and Applied Chemistry (IUPAC), [“amount fraction”](https://goldbook.iupac.org/terms/view/A00296) and [“mass fraction”](https://goldbook.iupac.org/terms/view/M03722), *Compendium of Chemical Terminology*, 5th ed. (2025). These definitions support the stated binary-mixture conversion; they do not validate any NASA test-row input.
- NASA, [Burning and Suppression of Solids (BASS)](https://www.nasa.gov/wp-content/uploads/2025/07/burning-and-suppression-of-solids-bass.pdf).
- NASA, [Physical Sciences Informatics investigation catalogue](https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/).
- de Ris, J. N. (1969), [“Spread of a laminar diffusion flame”](https://doi.org/10.1016/S0082-0784(69)80407-8), *Proceedings of the Combustion Institute*, 12, 241–252.
- NASA, [Flame Spread Theory](https://ntrs.nasa.gov/api/citations/19930004527/downloads/19930004527.pdf).

These references support the scope and named theory, not every proposed feature equation. Any future implementation of combustion correlations should cite the exact derivation and compare the formulation with the data's apparatus and regime.
