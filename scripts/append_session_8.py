import os

filepath = 'Schematics/07-Sessions By Day/2026-04-11.md'
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

# We need to insert Session 8 right before "## Day Summary"
parts = text.split("## Day Summary")

prefix = parts[0].strip()

new_session = """

## Session 8 | 08:30 | Germini (Lead)

- **Goal:** Audit `Schematics` and assess new Owner configurations to determine the roadmap for the final KasiLink / Kopano Context integration.
- **Audit Findings:**
  1. **Microsoft Readiness (6/6):** Root `.env` variables for Azure OpenAI, application insights, and Azure tenancy are actively populated and confirmed. `demo_ready` script officially reports true.
  2. **WhatsApp & Google RapidAPI:** RapidAPI keys and `whin2` endpoints are now embedded in `.env`. Master has explicitly demanded that WhatsApp and external context (Google Search) are *REQUIRED* for the demo.
  3. **KasiLink Dependencies:** Clerk API keys and Atlas MongoDB URIs are now available in the root, but the `KasiLink` front-end folder itself lacks a populated `.env.local`.
- **Next Directives as Lead:**
  - Copy authenticated variables from the root `.env` into a new `KasiLink/.env.local`.
  - Perform live testing on KasiLink endpoints to verify the stack fully connects Kopano Context internal dashboards to Azure telemetry and MongoDB persistence.
  - Formally lift all blockers across Schematics to declare the ecosystem `FULL STACK DEMO READY`.

## Day Summary"""

new_content = prefix + new_session + parts[1]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Updated successfully.")
