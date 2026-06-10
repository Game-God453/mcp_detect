# Acceptance Criteria - Prompt Reuse Index Cards

## Gate Checks

- [x] `SKILL.md` exists and contains a prompt-only workflow.
- [x] `skill.json` is valid JSON and declares `name=prompt-reuse-index-cards`, `version=1.0.0`, `license=MIT-0`, `language=en`, and `hasExecutableCode=false`.
- [x] `skill.json` uses `triggerKeywords` with camelCase values only.
- [x] `skill.json` declares `execution=noExec`, `promptOnly=true`, `requires_api=false`, `no_network=true`, `no_credentials=true`, `no_code_execution=true`, and `contentType=document-only`.
- [x] File count is exactly 3: `SKILL.md`, `skill.json`, and `ACCEPTANCE.md`.
- [x] Public-facing documentation is English and ASCII only.
- [x] No executable code, scripts, package files, API calls, network calls, credentials, secrets, or private data are included.
- [x] Trigger scenario, concrete deliverable, workflow, output format, and safety boundary are explicit.
- [x] The workflow asks for user-provided prompts, sorts them by task type, rewrites them for reuse, and preserves user intent.
- [x] Each card includes task type, inputs needed, reusable prompt text, expected output, quality check, adaptation note, and reuse notes.
- [x] The output includes a master index and a blank card template.
- [x] Privacy guidance tells users to remove private or confidential data before reuse.

## Scope

- Prompt-only MVP.
- Local implementation only.
- Not published to ClawHub in this phase.

## Review Status

- Implemented by: Codex subagent
- Date: 2026-05-11
- Status: Ready for cross-review and test.
