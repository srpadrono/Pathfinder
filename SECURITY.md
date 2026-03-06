# Security Policy

## Supported Versions

Only the latest major version receives security updates. Older major versions
are not patched.

| Version | Supported |
|---------|-----------|
| 2.x     | Yes       |
| 1.x     | No        |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public issue
2. Email **srpadron@outlook.com** with details
3. Include steps to reproduce if possible

You should receive a response within 48 hours. We will work with you to
understand and address the issue before any public disclosure.

## Patch Release SLA

Once a vulnerability is confirmed, a patch release will be published within
72 hours. Critical vulnerabilities that allow remote code execution or data
exfiltration are prioritized for same-day fixes when possible.

## Dependency Scanning

CI runs `ruff check` on every push and pull request to catch known issues in
project code. We recommend that forks enable GitHub Dependabot or a similar
dependency scanning tool to monitor transitive vulnerabilities in Python
packages listed in `requirements-dev.txt`.
