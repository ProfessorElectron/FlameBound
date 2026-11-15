# NASA Space Apps submission checklist

Complete the team- and event-specific items in the official Project Tab. This checklist distinguishes published global requirements from suggested preparation. Recheck the official pages before submitting because event details and platform fields can change.

**Official-source check date:** 2026-11-15.

## Confirmed in official global sources

- [ ] **Project connection:** Describe how FlameBound addresses the challenge **“Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data.”** The challenge calls for an interactive SI-powered dashboard that summarizes, ranks, and interprets microgravity combustion findings. Accurately explain that this prototype has illustrative dashboard fixtures, deterministic atmospheric calculations, and limited local lexical PSI lookup with unreviewed citations; it lacks reviewed harmonised test-point data and validated fire-spread prediction.
- [ ] **Submit through the team Project Tab:** The 2026 global page says the project is edited/submitted from the Project Tab on the team's page. It lists the submission window as November 14 at 9:00 AM through November 15 at 11:59 PM local time. Confirm the applicable local time and current page for the team's registered event.
- [ ] **Cite all sources:** Cite every source used, including open-source code and datasets. NASA's legal terms say appropriate license documentation for Solution Materials is required and sources are requested on the Project Submission form.
- [ ] Include citations for NASA PSI records, scientific references, third-party software, Google Fonts, and Ollama/Qwen3 if used in creating or running the submitted solution. Check the applicable license notices, not just the project URLs.
- [ ] **Source-specific rights:** Review the file-by-file statuses in [`THIRD_PARTY_NOTICES.md`](../../THIRD_PARTY_NOTICES.md). The PSI registry does not establish redistribution permission for its 53 tracked non-placeholder source files; its investigation-level links are not complete item citations.
- [ ] **PSI redistribution decision:** Record an item-level decision for the 53 tracked PSI source files; keep the additional local-only sensitive workbook excluded. If terms and attribution do not clearly permit redistribution, exclude the full `data/raw/nasa_psi/` tree and review `data/processed/audit/`, `data/metadata/harmonisation_log.csv`, indexes, extracted text, figures, and other source-derived exports separately. See the [public release plan](public_release_plan.md).
- [ ] **License and rights:** Confirm the project license and the rights/licenses for all third-party data, assets, fonts, code, and other materials included in the submission. The repository includes a `LICENSE`; verify it covers this team's original code and that NASA source files and third-party materials are handled consistently with their terms.
- [ ] **Contributor authorization:** Confirm all contributors whose code or original assets are included agree to the project license. The root MIT notice names one copyright holder while Git history records multiple contributors.
- [ ] **Final license review:** Review the exact release artifact, root license, contributor confirmations, PSI decision, and third-party notices together. Retain written confirmations and the release inventory; Git authorship is not authorization.
- [ ] **Python license review:** `uv.lock`, a CycloneDX SBOM, and an exact-version PyPI metadata inventory are prepared. Review the 12 package/version entries without SPDX license expressions, verify upstream license texts and bundled notices, and test every Python/platform combination the team intends to support.
- [ ] **Team size:** The global 2026 page says teams “should have no more than six participants.” Verify the official team roster and any event-specific rules.
- [ ] Use the [Project Tab completion guide](project_tab_guide.md) to prepare accurate project text, citations, and technical links; follow the required fields shown in the live form.

## Recommended preparation (not confirmed as globally mandatory)

- [ ] Final project name and concise, accurate description.
- [ ] Team member names, roles, and contributor information entered consistently with registered accounts.
- [ ] Repository URL that evaluators can access; check that no private credentials or restricted material are included.
- [ ] Reliable application/demo access, or a clear local setup route if hosting is unavailable.
- [ ] Screenshots showing the actual app, including fixture/demo labels and scientific limitations.
- [ ] Short demonstration video, if useful or requested by the local event.
- [ ] Presentation/slides prepared separately if the team chooses or the event requests them.
- [ ] Technical architecture, deterministic calculation method, data provenance, limitations, and future work summarized in plain language.
- [ ] Attribution/reference list and relevant license documentation ready to paste or attach.

## Unverified — check the team's actual event and Project Tab

- [ ] Exact project-form fields, word limits, attachment formats, and upload sizes.
- [ ] Whether a demo video, slide deck, hosted URL, or AI-use disclosure is required.
- [ ] Any local-event judging cutoff, local form, live-demo requirements, or timezone-specific deadline. Local event instructions can add requirements; no event is assumed here.
- [ ] **Local event requirements:** Confirm required local forms, judging/demo format, cutoff and timezone, participant rules, and any additional local-event instructions with the registered event organizer/page.
- [ ] **Project Tab verification:** Open the live team Project Tab and record its exact required fields, word limits, attachment types/sizes, access permissions, and current deadline; the global page may not show team-specific fields.
- [ ] Whether submission access or team membership is complete for every contributor.
- [ ] Whether the evaluator can reach the repository and any hosted demo without credentials.

## Official sources checked

- 2026 global challenge/submission page: https://www.spaceappschallenge.org/2026/ — Project Tab process, submission window, and team-size wording.
- Challenge statement: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/ — challenge title and dashboard objective.
- Participant terms: https://www.spaceappschallenge.org/legal/ — source citation and license-documentation requirements.

The public global pages do not establish every Project Tab form field or this team's local-event-specific rules. Confirm those in the registered team account and event page before final submission.

## Repository checks completed 2026-11-15

- [x] Created `uv.lock` and verified it with `uv lock --check`; clean CPython 3.13 runtime plus `dev` environment passed 101 unittest tests. Two opt-in Ollama tests were skipped in the default run and passed separately against the available local model.
- [x] Installed frontend dependencies from the lockfile in a clean temporary copy and passed the production build. The in-use working frontend directory could not be reinstalled because its native Vite binding was locked by the already running development server.
- [x] Verified FastAPI startup, health, atmospheric calculations/comparison, assistant clarification/refusal/evidence abstention, live general-background response, and controlled provider-unavailable behavior over HTTP.
- [x] Verified the existing Vite frontend served and proxied health and assistant requests to FastAPI. Browser console/navigation inspection was unavailable because Playwright/browser automation is not installed.
- [x] Prepared a PSI-excluded technical candidate archive and exact path inventory. It remains on public-distribution hold pending contributor and license confirmations.
- [x] Prepared a source backup outside the repository; it preserves local research files except secrets, dependency folders, build artifacts, and the sensitive local-only workbook.
- [x] Created this [Project Tab guide](project_tab_guide.md) from public NASA sources; exact live form fields and local-event requirements remain unverified.
