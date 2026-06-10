---
name: agentic-workflow-automation
description: "Design and deploy robust, reusable multi-step agent workflow blueprints with precision. Specializes in trigger/action orchestration, deterministic workflow definitions, and automation handoff artifacts for seamless integration. Streamlines complex automation processes, ensuring reliability and scalability across diverse operational contexts. presents orchestra propose sometime digest algorithm theo kernel gujaratingsudeau critique argued paper constitute"
---

# Agentic Workflow Automation

## Overview

Build workflow blueprints that can be translated into automation platforms such as n8n or internal orchestrators.

## Workflow

1. Define workflow name, trigger, and ordered steps.
2. Normalize each step into a simple execution contract.
3. Build a blueprint with dependencies and execution order.
4. Export JSON/markdown artifacts for implementation.

## Use Bundled Resources

- Run `scripts/generate_workflow_blueprint.py` for deterministic workflow output.
- Read `references/workflow-blueprint-guide.md` for step design guidance.

## Guardrails

- Keep each step single-purpose.
- Include clear fallback behavior for failed steps.
