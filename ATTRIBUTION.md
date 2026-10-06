# Third-Party Attribution

## Reference A — RAG/document retrieval inspiration
Source: https://github.com/Angular2Guy/AIDocumentLibraryChat
License: <VERIFY>
Commit/tag reviewed: <PIN>
Used for: documented reference patterns only, or exact files listed below.
Files copied/adapted, if any: <LIST OR NONE>
Changes made by TicketIQ team: <LIST>

## Reference B — Angular/Spring AI architecture inspiration
Source: https://github.com/loiane/spring-ai-angular
License: <VERIFY>
Commit/tag reviewed: <PIN>
Used for: documented reference patterns only, or exact files listed below.
Files copied/adapted, if any: <LIST OR NONE>
Changes made by TicketIQ team: <LIST>

## Dataset — Multilingual IT Support Tickets (2026-10-06)
Source: public synthetic multilingual customer-support ticket dataset
(`aa_dataset-tickets-multi-lang-5-2-50-version.csv`, supplied by the team).
Used for: TF-IDF retrieval over ~16K synthetic English IT tickets and a
k-NN queue/type signal (`ai-service/app/services/dataset_service.py`).
All rows are synthetic/fictional; no personal data is stored or displayed.
Stored at `data/datasets/` with a derived cache at `data/generated/dataset_en_sample.json`.

## Brand Assets — Logo & Chatbot Icons (2026-10-06)
Source: team-supplied SVG set (chatbot bubble/book/compass, project wordmarks).
Used for: sidebar wordmark (`frontend/public/brand/project-logo-dark.svg`,
recolor of the original for the dark theme), favicon (`brand/favicon.svg`,
icon crop), and chatbot FAB icon (`brand/chatbot-bubble.svg`, recolor).
Originals retained in `D:\tcs hacakthon\brand_assets\`.

## Multilingual Support (2026-10-06)
Language detection (Unicode script analysis), the Hindi/Tamil ↔ English IT
glossary bridge, and all localized system strings are original TicketIQ work
(`language_service.py`, `glossary.py`, `localization.py`). The chatbot uses
the Kimi/Moonshot API with language-forcing system prompts; offline fallbacks
are pre-translated locally. Known limitation: knowledge-base runbooks remain
English-only; non-English tickets are bridged via the glossary and this is
disclosed in the UI.

## Original TicketIQ Work
- IT support ticket domain model.
- PII redaction pipeline.
- Hybrid retrieval/ranking.
- Confidence/no-reliable-match gate.
- Per-step source grounding verifier.
- Analyst approval and feedback workflow.
- Duplicate ticket detection.
- Knowledge-gap intelligence.
- Evaluation dashboard and test suite.
