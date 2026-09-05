# Security Policy — Custodio RAT Manager

## Version
1.0.0 — 2026-07-03

## Reporting Security Vulnerabilities

If you discover a security vulnerability in Custodio RAT Manager, please report it responsibly.

### How to Report
1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Send an email to the development team with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes (optional)

### Scope
Custodio RAT Manager handles sensitive personal data under Chile's Law 21.719 (Ley de Proteccion de Datos Personales). Security vulnerabilities in:
- Authentication/authorization mechanisms
- Data encryption (Fernet at rest)
- API endpoints exposure
- Secret management
- SQL injection, XSS, CSRF
- Multi-tenant isolation (IDOR)

### Response Timeline
| Severity | Acknowledgment | Initial Response | Resolution Target |
|----------|---------------|------------------|-------------------|
| Critical | 24h | 48h | 7 days |
| High | 48h | 5 days | 30 days |
| Medium | 1 week | 2 weeks | 60 days |
| Low | 2 weeks | 1 month | 90 days |

### What to Expect
- Acknowledgment of your report within the timeline above
- Regular updates on progress
- Credit in the security release notes (unless you request anonymity)

## Security Best Practices for Deployment

### Required
- [ ] `SECRET_KEY` generated with `openssl rand -hex 64` (production)
- [ ] `DATABASE_URL` uses PostgreSQL with SSL (Neon)
- [ ] `ALLOWED_ORIGINS` explicitly set (no wildcards in production)
- [ ] SMTP configured for transactional emails (SMTP_URL)
- [ ] Pre-commit hook installed (`pre-commit install`)
- [ ] Gitleaks in CI/CD pipeline

### Recommended
- [ ] MFA for admin accounts
- [ ] Rate limiting enabled (`slowapi`)
- [ ] Logs reviewed monthly
- [ ] Penetration testing annually
- [ ] Dependency audit (`pip audit`, `npm audit`) in CI

## Incident Response

In case of a security breach:
1. Immediately rotate all exposed credentials
2. Notify the development team
3. See `docs/cumplimiento/INCIDENT_RESPONSE.md` for breach response protocol (72h APDP notification requirement)

## Dependencies

This project is maintained with security updates. Known vulnerabilities are tracked in GitHub Security Advisories.
