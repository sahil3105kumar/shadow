# Security Policy

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.** Shadow is a privacy-first, local-first system that handles credentials, secrets, and personal data by design — a publicly filed report gives anyone the same head start an attacker would need.

Instead, report privately using one of these:

1. **GitHub Private Vulnerability Reporting** (preferred) — go to the [Security tab](../../security/advisories/new) of this repository and click **"Report a vulnerability."** This opens a private advisory visible only to maintainers until it's resolved.
2. **Direct contact** — reach the maintainer listed in `.github/CODEOWNERS`.

When reporting, please include:

- A description of the vulnerability and its potential impact
- Steps to reproduce it, or a proof-of-concept if you have one
- The affected component (e.g. Configuration, Kernel, a specific plugin) and, if known, the commit or version
- Whether you're aware of it being exploited in the wild

You do not need to have a fix in hand — a clear, reproducible report is enough to act on.

---

## What to Expect

- **Acknowledgment:** within 5 business days of your report.
- **Initial assessment:** within 10 business days, including whether it's confirmed, its severity, and a rough timeline for a fix.
- **Fix and disclosure:** timeline depends on severity and complexity. We'll keep you updated throughout rather than go silent.

This is currently a small, early-stage project (pre-1.0, Phase 0 of the roadmap), so response times may occasionally run longer than the above during periods of low maintainer availability — but every report will get a response.

---

## Disclosure Policy

We follow coordinated disclosure:

- We ask reporters not to publicly disclose a vulnerability until a fix is released or 90 days have passed since the report, whichever comes first.
- Once a fix is available, we credit the reporter (by name or handle, unless anonymity is requested) in the release notes or advisory.
- For critical vulnerabilities affecting data confidentiality, integrity, or the "human approval required for consequential actions" guarantee (see `docs/product/principles.md`), we'll prioritize a patch release over waiting for the next scheduled milestone.

---

## Supported Versions

Shadow has not yet reached a 1.0 release. Until then, only the `develop` branch (latest commit) is supported — there is no long-term-support version to backport fixes to.

| Version | Supported |
|---|---|
| `develop` (latest) | ✅ |
| Anything older | ❌ |

This table will be updated once tagged releases begin, per `docs/engineering/release-process.md`.

---

## Scope

This policy covers the Shadow codebase in this repository: the Kernel, Infrastructure, Perception, Cognition, Action, and Memory domains, and any first-party plugins maintained here.

It does **not** cover:

- Vulnerabilities in third-party dependencies (report those upstream — though we'd still appreciate a heads-up so we can track and update)
- Social engineering or physical security issues
- Vulnerabilities requiring an already-compromised local machine (Shadow is local-first by design and assumes the host device itself is trusted)

---

## Recognition

Security researchers who responsibly disclose valid vulnerabilities will be credited here and in relevant release notes, unless they prefer to remain anonymous.
