---
name: security
description: >
  Security awareness for every phase of the expedition.
  Prevent OWASP Top 10, validate inputs, protect secrets.
---

# Security

**Goal:** Prevent security vulnerabilities from entering the codebase. Every phase, every checkpoint.

**When:** Any time code is written, reviewed, or deployed. This is a cross-cutting concern — it applies everywhere.

## The Security Checklist

Run this checklist before every PR. No exceptions.

### Input Validation

- [ ] All user input is validated on the server side (client validation is UX, not security)
- [ ] Input length limits enforced
- [ ] Input type/format validated (email, URL, number ranges)
- [ ] File uploads validated (type, size, content)
- [ ] No user input passed directly to SQL, shell, or eval

### Authentication & Authorization

- [ ] Protected routes require authentication
- [ ] Authorization checked per resource (not just per route)
- [ ] Tokens have expiration
- [ ] Password requirements enforced
- [ ] Rate limiting on auth endpoints

### Data Protection

- [ ] No secrets in code (API keys, passwords, tokens, connection strings)
- [ ] Secrets in environment variables (`.env.local`, never committed)
- [ ] `.gitignore` includes `.env*`, `.auth/`, credentials files
- [ ] Sensitive data not logged (passwords, tokens, PII)
- [ ] Error messages don't leak internal details (stack traces, SQL queries, file paths)

### Output Encoding

- [ ] HTML output escaped to prevent XSS
- [ ] JSON responses use `Content-Type: application/json`
- [ ] No `dangerouslySetInnerHTML` without sanitization
- [ ] URL parameters encoded before use
- [ ] No string concatenation for SQL — use parameterized queries

### Dependencies

- [ ] No known vulnerable dependencies (`npm audit`)
- [ ] Dependencies pinned to specific versions
- [ ] No unnecessary dependencies (smaller surface area = less risk)

## Security in Each Phase

| Phase | Security Action |
|-------|----------------|
| **Survey** | Identify auth/authz requirements. Ask: "What data is sensitive?" |
| **Planning** | Mark security-critical checkpoints (auth, payment, PII) |
| **Scouting** | Write tests for auth failures, injection, invalid input |
| **Building** | Use parameterized queries, validate input, escape output |
| **Reporting** | Run security checklist. Include in PR review. |

## Common Vulnerabilities to Test For

### XSS (Cross-Site Scripting)

```typescript
// Scout: Test that script tags are escaped
test('SEC-01: XSS in user input is escaped', async ({ page, checkpoint }) => {
  checkpoint.mark('SEC-01', 'XSS prevention');
  await page.fill('[name="comment"]', '<script>alert("xss")</script>');
  await page.click('button[type="submit"]');
  // Verify the script tag is displayed as text, not executed
  await expect(page.locator('text=<script>')).toBeVisible();
  checkpoint.clear('SEC-01');
});
```

### SQL Injection

```typescript
// Unit test: parameterized queries
it('SEC-U01: Query uses parameterized input', () => {
  const query = buildQuery("'; DROP TABLE users; --");
  expect(query.params).toContain("'; DROP TABLE users; --");
  expect(query.text).not.toContain('DROP TABLE');
});
```

### Auth Bypass

```typescript
// Scout: Test that protected routes redirect
test('SEC-02: Unauthenticated user redirected to login', async ({ page, checkpoint }) => {
  checkpoint.mark('SEC-02', 'Auth redirect');
  // Clear auth state
  await page.context().clearCookies();
  await page.goto('/dashboard');
  await expect(page).toHaveURL(/login|auth/);
  checkpoint.clear('SEC-02');
});
```

## CLI Commands for Security

```bash
# Check for known vulnerabilities in dependencies
npm audit

# Check for secrets accidentally committed
git log --all --diff-filter=A -- '*.env' '*.key' '*.pem' '*credentials*'

# Search for common dangerous patterns
grep -rE "dangerouslySetInnerHTML|eval\(|innerHTML\s*=" src/ || echo "None found"

# Search for hardcoded secrets
grep -rn "password\s*=\s*['\"].*['\"]" src/ --include='*.ts' --include='*.tsx' || echo "None found"
```

## Anti-Rationalization

| Rationalization | Counter |
|----------------|---------|
| "This is an internal tool, security doesn't matter" | Internal tools get compromised too. Internal networks get breached. Validate input. |
| "I'll add security later" | Security bugs are 10x harder to fix after the fact. Build it in now. |
| "The framework handles security" | Frameworks provide tools, not guarantees. You still need to use them correctly. |
| "Nobody would try to exploit this" | Automated scanners don't care about your assumptions. Protect the endpoint. |
| "It's just a prototype" | Prototypes become production. Write it secure the first time. |
