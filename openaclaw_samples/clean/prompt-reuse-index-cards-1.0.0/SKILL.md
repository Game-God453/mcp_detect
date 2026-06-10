---
name: prompt-reuse-index-cards
description: Build printable or copyable index cards from reusable AI prompts, including task type, required inputs, prompt text, expected output, quality checks, adaptation notes, and a master index. Use when the user has useful prompts scattered across notes and wants a small prompt card deck for quick reuse without external storage or automation.
---
# Prompt Reuse Index Cards

## Purpose

Turn a user's scattered reusable prompts into a compact card deck they can print, copy into notes, or keep beside their workspace. Each card preserves the user's intent, names the inputs needed before reuse, and adds a simple quality check so the user can decide whether the AI output worked.

This is a prompt-only document workflow. It does not call AI tools, store prompts externally, connect to accounts, request secrets, or run code.

## Use This Skill When

Use this skill when the user wants to:

- Organize a personal or team prompt library into printable cards.
- Convert long or messy prompts into concise reusable versions.
- Build prompt cards for writing, research, planning, editing, learning, admin, coding support, customer replies, meeting prep, or other repeatable tasks.
- Create a master index so prompts can be found by task type or situation.
- Add quality checks and adaptation notes to prompts they already use.

Do not use this skill to collect passwords, API keys, private account data, confidential client material, regulated records, or proprietary content. Ask the user to sanitize sensitive details before adding prompt text to a reusable card.

## Best Inputs

Ask only for what is needed. If the user has incomplete prompts, proceed with placeholders and a short missing-info list.

- Existing prompt text, rough prompt ideas, or descriptions of repeated AI tasks.
- Task type for each prompt, if known.
- Required input fields the user needs to provide before running the prompt.
- Desired output format, length, tone, audience, and success criteria.
- Reuse context, such as personal, team, school, creator, small business, or admin work.
- Any private details that must be removed or replaced with placeholders.

## Workflow

1. **Collect and sanitize prompts.** Ask the user to paste or describe prompts they already use. Remind them to remove private data, credentials, confidential names, account numbers, and regulated records.
2. **Sort by task type.** Group prompts into practical categories such as writing, research, planning, editing, learning, admin, communication, analysis, and review.
3. **Preserve intent.** Rewrite each prompt into a concise reusable version without changing the user's goal, audience, decision standard, or output need.
4. **Define required inputs.** For every card, list the inputs the user must provide before reuse, using placeholders such as [topic], [audience], [source notes], [tone], [length], or [format].
5. **Create one card per prompt.** Include card title, task type, when to use it, required inputs, reusable prompt, expected output, quality check, adaptation note, and reuse notes.
6. **Add quality checks.** Write a simple test line that helps the user judge the result, such as accuracy, completeness, tone fit, source support, actionability, or format compliance.
7. **Add adaptation notes.** Show how to change audience, tone, length, format, constraints, examples, or review depth without rewriting the whole card.
8. **Build the master index.** Produce a compact index sorted by task type, with card number, title, use case, and best input to prepare.
9. **Flag risky prompts.** Mark prompts that could invite private data, unsupported claims, legal or medical advice, security risk, or overreliance on unsourced output.

## Output Format

Return the finished card deck in this order:

1. **Deck Summary**

| Field | Detail |
|---|---|
| Deck name | |
| Number of cards | |
| Main task types | |
| Sensitive details removed | |
| Best reuse location | |

2. **Master Index**

| Card | Task type | Card title | Use when | Prepare this input |
|---:|---|---|---|---|

3. **Index Cards**

Use this layout for each card:

```text
CARD [number]: [title]
Task type: [category]
Use when: [specific situation]
Inputs needed: [placeholders]
Reusable prompt:
[prompt text]
Expected output: [format and standard]
Quality check: [how to judge whether it worked]
Adaptation note: [audience, tone, length, or format change]
Reuse notes: [where to store, when to update, or known limits]
```

4. **Risk and Privacy Review**

| Card | Risk to watch | Safer reuse rule |
|---:|---|---|

5. **Blank Card Template**

Provide one blank card the user can copy for future prompts.

## Message Style

- Be compact, practical, and organized.
- Keep card titles short enough for a physical index card.
- Preserve the user's wording where it carries useful intent, but remove clutter.
- Use placeholders instead of personal names, account details, secrets, or client facts.
- Mark unknowns and missing inputs clearly.
- Prefer reusable prompts that are specific enough to work but flexible enough to adapt.

## Safety Boundary

- Do not automate AI calls, run prompts in external tools, store prompts externally, access accounts, use APIs, browse the web, or request credentials.
- Do not ask for or preserve passwords, API keys, one-time codes, private account numbers, regulated records, confidential client material, proprietary documents, or highly personal data.
- Remind the user to remove private data before reusing prompts in any AI system.
- Do not present AI outputs as verified facts. For research, legal, medical, financial, safety, or compliance prompts, include a verification or professional-review note.
- If a prompt would require confidential or regulated inputs, convert it into a sanitized template with placeholders.

## Example Starter Prompt

"Paste the prompts or rough prompt ideas you reuse most often. I will turn them into a printable card deck with required inputs, reusable prompt text, expected output, a quality check, adaptation notes, and a master index. Please remove private or confidential details before sharing."
