# Security Policy

## Supported Versions

**Introduction to MCP** is an educational and demonstration project focused on the Model Context Protocol (MCP). It is currently in active development (pre-1.0).

| Version        | Supported          | Notes                            |
| -------------- | ------------------ | -------------------------------- |
| `main` branch  | :white_check_mark: | Actively developed and supported |
| Latest release | :white_check_mark: | Recommended for use              |
| Older releases | :x:                | No longer supported              |
| < 0.1.0        | :x:                | Experimental / not supported     |

---

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it **responsibly** so we can address it quickly.

### Preferred Reporting Methods

1. **GitHub Private Vulnerability Report** (recommended)  
   → Use the **"Report a vulnerability"** button on the [Security tab](https://github.com/RobynAwesome/Introduction-to-MCP/security/advisories/new) of this repository.

2. **Email** (if you prefer privacy)  
   → kholofelorababalela@gmail.com  
   (Please encrypt sensitive details or use a temporary email if needed.)

### What to Include in Your Report

- Clear description of the vulnerability
- Steps to reproduce the issue
- Potential impact (e.g. API key leak, prompt injection, PyInstaller bundle risk, etc.)
- Any suggested fix or mitigation

### Our Response Timeline

- **Acknowledgment** → within 48 hours
- **Initial assessment & update** → within 5 business days
- **Fix & disclosure** → as quickly as responsibly possible

---

**Note**  
This project integrates multiple LLM providers (Claude, Grok, Gemini, Copilot) and uses PyInstaller for the standalone executable. We are especially interested in issues related to:

- API key handling
- Prompt injection / MCP protocol abuse
- Executable bundling security (hidden imports, etc.)
- Any unsafe file-system or network behaviour

Thank you for helping keep the MCP community secure.  
Made with ❤️ in South Africa 🇿🇦

---

## Operational Rules

- Do not commit `node_modules/`, `.env`, copied secrets, or vendor config files that can carry credentials.
- If a secret is exposed in git, assume compromise immediately even if validity is uncertain.
- Response order is:
  1. revoke or rotate the credential outside the repo,
  2. remove the tracked exposure from git,
  3. document the incident and prevention rule in project notes,
  4. rerun verification before shipping.
