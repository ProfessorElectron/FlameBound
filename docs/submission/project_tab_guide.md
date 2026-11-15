# NASA Space Apps 2026 Project Tab completion guide

**Checked:** 2026-11-15 against public 2026 NASA Space Apps pages. This guide is not a submission and does not access the team's account.

## What public sources confirm

- The project is edited and submitted from the **Project Tab** on the team's page.
- The 2026 global page gives a submission window of **November 14, 9:00 AM through November 15, 11:59 PM local time**. Confirm the governing timezone from the team's registered event/team creator.
- The global page says teams **should have no more than six participants**.
- Participant terms require appropriate license documentation for Solution Materials and citation of every source used, including open-source or freely available resources. Participants warrant they have sufficient rights to authorize publication and use of the materials.
- The Flame in Freefall challenge asks for an interactive SI-powered dashboard that summarizes, ranks, and interprets microgravity combustion findings.

Sources: [2026 event page](https://www.spaceappschallenge.org/2026/), [Flame in Freefall challenge](https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/), and [2026 participant terms](https://www.spaceappschallenge.org/legal/).

## Complete the live form

1. Sign in to the Space Apps site, open your team's page, and select **Project Tab**. Use the required fields actually shown there. The public global page confirms the Project Tab workflow but does not expose a definitive current field-by-field schema, word limits, or attachment limits. Do not infer mandatory fields from old-year guides.
2. Select the Flame in Freefall challenge if the form requests a challenge selection.
3. Describe the problem and project accurately: FlameBound is an engineering prototype for organizing combustion research, searching text-extractable local PSI files, and demonstrating deterministic atmospheric calculations. It does not contain reviewed harmonised PSI test points or a validated flame-spread/ignition predictor.
4. Describe what is implemented: the React frontend calls FastAPI; deterministic calculations compute oxygen partial pressure and compare atmospheric conditions from explicit absolute-pressure inputs. Clearly label dashboard fixtures as illustrative, not NASA statistics.
5. Explain the AI boundary truthfully: atmospheric values are parsed/validated and calculated by deterministic backend code; Ollama generates general answers and natural-language summaries of locally retrieved source passages. PSI retrieval is lexical, limited to text-extractable files, and every citation is marked unreviewed. Do not claim live tool-calling reliability, reviewed evidence, or model-generated scientific predictions.
6. Cite sources used and provide applicable third-party license documentation. Review `THIRD_PARTY_NOTICES.md`; PSI source-file redistribution and contributor authorization remain unresolved. Do not upload raw PSI documents or derived exports unless rights are established.
7. Provide repository, hosted-demo, screenshots, video, slides, or other links only when the form asks for them or the registered local event requires them. Test each shared URL in a signed-out/private browser window. Do not claim a local demonstration is hosted.
8. Review team membership and any license/rights attestations. A team member must personally accept statements they can truthfully make; this guide cannot confirm contributor consent or source rights.
9. Save/submit in the live Project Tab and verify the resulting status. Do not treat a saved draft as a submitted project.

## Project description checklist

Before pasting into the form, ensure the description answers the requested questions without exceeding the live field limits:

- Which challenge the project addresses and the specific problem it tackles.
- What the current prototype does and how a judge can try it.
- What data and sources were actually used, with citations and license notices.
- Which values are deterministic calculations versus illustrative fixtures or model-generated background.
- What remains unavailable: reviewed PSI harmonised records and validated fire-spread prediction. The preclearance candidate excludes PSI sources and its local index; it cannot demonstrate source lookup unless cleared PSI files are supplied separately.
- How to run the application if no public demo is available.
- Contributor and third-party material disclosures required by the form/terms.

## Team and event-specific checks

- Confirm all team members are registered and shown on the team page; confirm team size against the official page and any event rules.
- Read the registered local-event page and schedule. Local events may require a separate form, earlier judging cutoff, demonstration link, presentation, or disclosure. These requirements cannot be determined without knowing the team's registered event.
- Confirm the team's governing timezone and deadline. Do not assume that the computer's timezone or this guide's timestamp determines the submission deadline.
- Review any required AI-use disclosure in the actual Project Tab or local-event instructions; the public global sources reviewed here do not establish one universal AI disclosure field.
- Keep a copy/screenshot of the final submission status and any local-form confirmation for the team.

## Human confirmations still required

This repository cannot establish PSI redistribution rights, consent from all Git contributors, authorship of uncommitted work, the team's registered event, or the contents of the authenticated Project Tab. Resolve these personally before making rights representations or final submission. See the [public release plan](public_release_plan.md), [release checklist](submission_checklist.md), and [release manifest](release_manifest.md).
