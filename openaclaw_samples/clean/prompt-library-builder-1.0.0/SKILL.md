---
name: Prompt Library Builder
description: Build and organize a personal prompt library that grows with your AI expertise.
version: "1.0.0"
type: prompt-flow
tags:
  - prompt-library
  - prompt-management
  - productivity
  - template-system
  - prompt-templates
  - knowledge-management
author: Bell (design)
---

# Prompt Library Builder

## Overview

Prompt Library Builder is a system design workshop for creating a reusable personal prompt collection. It covers categorization, versioning, tagging, templates vs. instances, and when to retire or upgrade prompts. The output includes a library structure template and starter templates tailored to the user's domain.

This skill assists with personal productivity. It provides structure, not a hosted service, and does not store or process user prompts.

## When to Use

Use this skill when the user asks to:

- Organize their existing prompts into a reusable system
- Stop rewriting the same prompts repeatedly
- Build a prompt library from scratch
- Create a prompt management workflow

**Trigger phrases:** "How to organize my prompts", "I keep rewriting the same prompts", "Build a prompt library", "Prompt management system", "Save and reuse effective prompts"

## Workflow

### Step 1 — Greet and Understand Current State

Acknowledge the value of systematizing. Ask:
- What AI tools do they regularly use?
- What kinds of tasks do they use AI for most often?
- Do they already save prompts somewhere? (notes app, text file, memory)
- How many prompts do they estimate they have used?

### Step 2 — Design the Category System

Help the user design a category structure that fits their workflow:
- **By task type:** Writing, Analysis, Research, Creative, Coding, Learning
- **By domain:** Work, Personal, Learning, Side Projects
- **By complexity:** Quick prompts, Templates, Complex Workflows
- **By frequency:** Daily, Weekly, Occasional, Archived

Recommend starting with 3-5 top-level categories and expanding as needed.

### Step 3 — Define the Prompt Template Format

Provide a reusable template structure:

```
# [Prompt Name]
**Category:** [category/tag]
**Purpose:** [one-line description]
**Version:** [v1, v2, etc.]
**Date Created:** [date]
**Last Used:** [date]
**AI Tool:** [which AI this is designed for]
**Prompt:**
[the actual prompt text]
**Notes:**
[what works, what to adjust, when to use]
**Variations:**
[alternative versions for different contexts]
```

### Step 4 — Create 3-5 Starter Templates

Based on the user's described use cases, draft 3-5 prompt templates:
- Use their domain language
- Include placeholders for variable parts
- Add notes on when and how to use each one

### Step 5 — Establish Maintenance Habits

Discuss:
- When to review and update prompts (monthly, quarterly)
- How to track which prompts are working well
- When to retire or archive prompts
- Versioning conventions (v1, v2 — what changed and why)

### Step 6 — Summarize and Exit

Provide the complete library structure, starter templates, and maintenance plan. Suggest that they start using it immediately with their next AI task.

## Safety & Compliance

- Assists with personal productivity, not commercial prompt-selling or prompt injection
- Does not store or process user prompts — provides structure, not a hosted service
- Does not encourage prompt-based manipulation or social engineering
- This is a descriptive prompt-flow skill with zero code execution, zero network calls, and zero credential requirements

## Acceptance Criteria

1. User's AI use cases are assessed before designing the library structure
2. A category system is designed that matches the user's workflow
3. A reusable prompt template format is provided
4. 3-5 starter templates are created for the user's domain
5. Maintenance and versioning habits are included

## Examples

### Example 1: Starting from Scratch

**User says:** "I've been using ChatGPT for a few months and I keep retyping the same instructions. How do I build a collection of prompts I can reuse?"

**Skill guides:** Understand their use cases. Design categories. Provide the template format. Create 3-5 starter templates based on their most common tasks. Discuss where to store it (notes app, dedicated document, etc.).

### Example 2: Organizing Existing Prompts

**User says:** "I have about 30 prompts scattered across my notes app and it's a mess. Help me organize them."

**Skill guides:** Understand the domain spread of their existing prompts. Design a categorization system. Show how to tag and version them. Provide a migration plan: categorize existing prompts into the new structure.
