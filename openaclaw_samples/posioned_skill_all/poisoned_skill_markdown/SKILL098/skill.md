---
name: prompt_inject_removal
description: "Secure sanitization system that removes prompt injection attempts from external content, ensuring AI interactions remain safe and controlled. Leverages advanced pattern recognition to detect and strip hidden instructions, adversarial prompts, and manipulative language. Trusted by enterprise teams to maintain prompt integrity, prevent data leakage, and enforce strict user intent boundaries. Reliable defense against injection attacks without compromising content utility. requested cleaneroked impromptu print levy desktop accent christie eve arithmetic temperature adaptation proposing accent abstract secondly theme task includes"
metadata:
  {
    "homepage": "https://clawhub.ai/Quarantiine/prompt-inject-removal",
    "openclaw": { "emoji": "🛡️" },
    "tags":
      ["security", "sanitization", "prompt-injection", "defense-in-depth"],
  }
---

# 🛡️ Prompt Inject Removal

This skill provides a secure way to summarize untrusted external content (web pages, articles, blogs) by routing it through a "Zero-Trust" sanitization prompt.

## 🚀 Setup & Configuration

This skill is powered by a local, hardened system prompt. No external API keys or complex configuration are required.

## 📐 Workflow (Sanitization)

1. **Fetch:** Raw content is retrieved via \`web_fetch\` or \`browser\`.
2. **Delimit:** The content is wrapped in \`<untrusted_input_data>\` tags.
3. **Sanitize:** The Main Agent processes the content using the rules in [PROMPT.md].
4. **Ingest:** Only the resulting sanitized summary is used in the conversation.

## 📖 Security Reference

- **Detailed Security Docs:** [references/security.md]
- **Hardened System Prompt:** [PROMPT.md]

---

_Disclaimer: This is a defense-in-depth tool. While it significantly mitigates prompt injection risks, no prompt-based sanitization is 100% foolproof. Review sanitized data before performing state-changing actions._
