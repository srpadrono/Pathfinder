# Release Checklist

## Pre-release

- [ ] `npm run validate`
- [ ] `npm run test:unit`
- [ ] `npx playwright test --list`
- [ ] `bash scripts/verify-expedition.sh` (or documented reason if skipped)
- [ ] Update roadmap implementation status (`docs/world-class-roadmap.md`)
- [ ] Update docs for user-facing changes

## Versioning

- [ ] Bump version in `package.json`
- [ ] Add release notes (highlights, fixes, breaking changes)

## CI / Security

- [ ] All required GitHub checks are green
- [ ] Security workflow passes (`npm audit` / secret scan)

## Publish

- [ ] Create release tag
- [ ] Publish release artifacts / notes
- [ ] Announce and link migration notes if needed
