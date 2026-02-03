# Security Report

**Last Updated:** 2026-02-02

## Summary

✅ **No hardcoded secrets in codebase**
⚠️ **34 npm dependency vulnerabilities detected**

---

## Credentials Management

### Status: ✅ SECURE

All credentials are properly externalized to environment variables:

- ✅ `.env` files gitignored
- ✅ No secrets in git history
- ✅ All code uses `os.getenv()` / `process.env`
- ✅ Only `.env.example` committed (with placeholders)

**Files Checked:**
- Python files (56): All use `os.getenv("ANTHROPIC_API_KEY")`, etc.
- TypeScript files (49+): All use `process.env.NEXT_PUBLIC_*`
- Config files: No secrets found

### Required Environment Variables

```bash
# Required for AI features
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Twitter integration
TWITTER_BEARER_TOKEN=...
TWITTER_CONSUMER_KEY=...
TWITTER_ACCESS_TOKEN=...
```

---

## Dependency Vulnerabilities

### NPM Dependencies (34 vulnerabilities)

**HIGH (3 vulnerabilities)**

1. **bigint-buffer** - Buffer Overflow via toBigIntLE()
   - Severity: HIGH
   - Advisory: [GHSA-3gc7-fjrx-p6mg](https://github.com/advisories/GHSA-3gc7-fjrx-p6mg)
   - Affects: `@solana/spl-token` >= 0.2.0
   - Fix: Requires breaking change to older version

2-3. **Solana wallet adapter dependencies** (2 additional high severity)

**MODERATE (4 vulnerabilities)**

1. **elliptic** - Cryptographic Primitive with Risky Implementation
   - Severity: MODERATE
   - Advisory: [GHSA-848j-6mx2-7j84](https://github.com/advisories/GHSA-848j-6mx2-7j84)
   - Affects: `@solana/wallet-adapter-wallets`, `@walletconnect/utils`
   - Fix: Requires breaking change

2. **lodash** - Prototype Pollution in `_.unset` and `_.omit`
   - Severity: MODERATE
   - Advisory: [GHSA-xxjr-mmjv-4gpg](https://github.com/advisories/GHSA-xxjr-mmjv-4gpg)
   - Fix: Update to latest lodash

3. **next** - Unbounded Memory Consumption via PPR Resume Endpoint
   - Severity: MODERATE
   - Advisory: [GHSA-5f7q-jpqc-wp7h](https://github.com/advisories/GHSA-5f7q-jpqc-wp7h)
   - Affects: Next.js 15.0.0 - 15.6.0
   - Fix: Upgrade to Next.js 16.1.6 (breaking change)

4. Additional moderate vulnerability in Solana dependencies

**LOW (27 vulnerabilities)**
- Various minor issues in transitive dependencies

### Python Dependencies

**Status: ✅ NO KNOWN VULNERABILITIES**

All Python dependencies are up-to-date:
- `anthropic >= 0.40.0`
- `fastapi >= 0.109.0`
- `pydantic >= 2.0.0`
- All other packages use modern versions

---

## Remediation

### Immediate Actions

**1. Non-Breaking Fixes**
```bash
cd web
npm audit fix
```
This will fix low-severity issues without breaking changes.

**2. Review Breaking Changes (Optional)**

The high/moderate vulnerabilities are in Solana wallet dependencies. These are **client-side only** and pose minimal risk for a simulation tool:

- **bigint-buffer**: Only affects wallet operations, not simulation logic
- **elliptic**: Used in wallet cryptography, not exposed to untrusted input
- **next.js**: Memory issue only affects production builds with PPR enabled

**Breaking Change Fixes:**
```bash
# WARNING: This will downgrade @solana/spl-token (breaking change)
npm audit fix --force
```

**Recommended:** Wait for Solana team to release patched versions that maintain compatibility.

### Monitor

- Check GitHub Dependabot alerts: https://github.com/michaelpaglia/simulation-env-for-shitcoins/security/dependabot
- Run `npm audit` periodically
- Subscribe to Solana wallet adapter security advisories

---

## Risk Assessment

### Overall: 🟡 LOW RISK

**Why low risk despite vulnerabilities:**

1. **Not a production financial app** - This is a simulation tool, not handling real funds
2. **Client-side vulnerabilities** - Issues are in wallet UI components, not backend
3. **No user data storage** - No database, no stored credentials
4. **Private repository** - Limited exposure
5. **Dev/test environment** - Not deployed to production

### When to Upgrade

Consider forcing breaking upgrades if:
- Deploying to production
- Handling real user wallets
- Processing sensitive data
- Making repository public

### Best Practices

- [ ] Keep `.env` files out of git (already done ✅)
- [ ] Use environment variables for all secrets (already done ✅)
- [ ] Run `npm audit` before major releases
- [ ] Monitor Dependabot alerts
- [ ] Rotate API keys if ever exposed
- [ ] Consider adding pre-commit hooks to prevent `.env` commits

---

## Contact

For security concerns, create a private issue or contact repository owner directly.
