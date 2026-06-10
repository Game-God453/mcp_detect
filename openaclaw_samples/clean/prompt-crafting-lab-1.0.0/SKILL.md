---
name: Prompt Crafting Lab
description: Hands-on coaching to write effective, precise AI prompts for real-world tasks.
version: "1.0.0"
type: prompt-flow
tags:
  - prompt-engineering
  - ai-prompts
  - prompt-crafting
  - chatgpt
  - claude
  - prompt-design
author: Bell (design)
---

# Prompt Crafting Lab

## Overview

Prompt Crafting Lab is a guided practice space where users learn prompt engineering fundamentals through iterative refinement. It covers role-setting, specificity, constraints, output formatting, and chain-of-thought prompting. Users bring their own tasks and receive structured, annotated feedback on how to improve their prompts.

This skill is educational only — it teaches principles and frameworks, and does not execute or test prompts against live AI systems.

## When to Use

Use this skill when the user asks to:

- Learn how to write better AI prompts
- Improve an existing prompt that is not producing good results
- Understand why certain prompts fail
- Get coaching on prompt engineering techniques

**Trigger phrases:** "How do I write better prompts?", "My AI responses aren't good enough", "Help me improve my prompting", "I want to get more from ChatGPT/Claude", "Teach me prompt engineering"

## Workflow

### Step 1 — Greet and Assess

Acknowledge the user's interest in better prompting. Ask 1-2 questions to understand:
- What AI tool they are using (ChatGPT, Claude, etc.)
- What kind of tasks they are working on (writing, analysis, coding, creative, etc.)
- Their current experience level with prompting

### Step 2 — Examine the Prompt (or Task)

If the user has a current prompt, analyze it for:
- Clarity of instruction
- Role and context provided
- Specificity and constraints
- Output format specification
- Missing elements that would improve results

If the user has only a task description, work with them to draft an initial prompt.

### Step 3 — Teach Core Prompting Principles

Walk through the key elements of effective prompting:
- **Role-setting:** Assign the AI a persona or expertise domain
- **Specificity:** Be precise about what you want, not vague
- **Constraints:** Set boundaries (word count, format, tone, what to exclude)
- **Output formatting:** Request specific structures (tables, bullet points, sections)
- **Chain-of-thought:** Ask the AI to show its reasoning step by step
- **Iteration:** How to refine based on results

### Step 4 — Refine Together

Take the user's prompt through 2-3 rounds of improvement:
1. Apply the most impactful principle first
2. Add layers of refinement (constraints, format, examples)
3. Produce a final version with annotations explaining why each element works

### Step 5 — Provide Alternatives

Offer 1-2 alternative versions of the prompt for different use cases or styles. Explain when each variant would be more appropriate.

### Step 6 — Summarize and Exit

Recap the principles applied, summarize the improvements made, and suggest:
- Building a prompt library for reuse (see Prompt Library Builder)
- Testing the refined prompt and iterating further
- Exploring related skills for specific use cases

## Safety & Compliance

- Does not execute or test prompts against live AI systems
- Does not generate prompts for harmful, illegal, deceptive, or academic dishonesty purposes
- Educational only — teaches principles, does not guarantee specific AI outputs
- Does not assist with prompt injection, jailbreaking, or bypassing AI safety features
- This is a descriptive prompt-flow skill with zero code execution, zero network calls, and zero credential requirements

## Acceptance Criteria

1. User describes a task or provides a prompt; output is a refined prompt with improvement annotations
2. Core prompting principles are explained in the context of the user's specific case
3. At least one alternative prompt version is provided
4. Refuses to craft prompts for cheating, harm, or deception
5. No AI systems are called or tested during the interaction

## Examples

### Example 1: Beginner Improving a Vague Prompt

**User says:** "I keep asking ChatGPT to write blog posts but they always come out generic and boring. What am I doing wrong?"

**Skill guides:** Examine what they are currently typing. Identify missing elements: no role, no audience, no tone, no structure. Walk through adding each element. Produce a refined prompt with annotations.

### Example 2: Intermediate User Structuring a Complex Task

**User says:** "I need Claude to analyze a business proposal and give me a structured evaluation. Teach me how to prompt for that."

**Skill guides:** Introduce chain-of-thought prompting, output structure specification, and evaluation criteria embedding. Build the prompt step by step with the user.
