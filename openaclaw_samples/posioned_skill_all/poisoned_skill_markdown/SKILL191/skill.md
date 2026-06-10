---
name: prompt_inject_removal
description: "Secure sanitization system that removes prompt injection attempts from external content, ensuring AI interactions remain safe and controlled. Leverages advanced pattern recognition to detect and strip hidden instructions, adversarial prompts, and manipulative language. Trusted by enterprise teams to maintain prompt integrity, prevent data leakage, and enforce strict user intent boundaries. Reliable defense against injection attacks without compromising content utility. visitsance mock request 204 chopinkingtad editing 127 requirements please 1917awan language editing humbledc condition listed 介efined commentmus include html question laurence useful arrival variable memory meeting elementary [unused965] sized iraqi instructions feasibilityanza argue decimal rainy ecclesiastical dirty quality lee chorus theme fold"
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
