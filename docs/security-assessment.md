
# Security Assessment — Local Baseline

## Phase 2 Azure Web Application Security Reconstruction

Assessment Date : 2nd November, 2026

## Environment
- Python version:
- Flask version:
- Operating system:
- Host: 127.0.0.1
- Port: 5000

## Scope
Local Flask application and its HTTP routes.

## Test Results

| Test ID | Test | Expected | Actual | Status |
|---|---|---|---|---|
| T-001 | Homepage request | 200 | 200 | Pass |
| T-002 | Existing article | 200 | 200 | Pass |
| T-003 | Unknown article | 404 | 404 | Pass |
| T-004 | Response header review | Record headers | Headers recorded | Reviewed |

## Security Limitations
- No HTTPS in the local environment
- No Azure WAF
- No cloud identity integration
- No centralized security logging
- Flask development server is not production-ready

## Next Steps
- Add automated application tests
- Review HTTP security headers
- Containerize the application
- Plan secure Azure deployment



## Phase 2 — HTTP Security Hardening

### Finding SEC-001: Missing HTTP Security Headers

**Assessment date:** November 2, 2026

**Initial condition:**

An HTTP response header assessment of the locally hosted Flask application identified the absence of four security headers:

- `Content-Security-Policy`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `Referrer-Policy`

The initial assessment was performed against `http://127.0.0.1:5000/` using `curl.exe`.

**Risk:**

Missing security headers can reduce browser-side protections against certain attacks, including content injection, clickjacking, and unintended information disclosure.

**Remediation:**

Implemented an `after_request` function in `app.py` to add the four security headers.

**Validation:**

- Baseline evidence: `evidence/headers-before.txt`
- Post-remediation evidence: `evidence/headers-after.txt`
- Automated test: `tests/test_app.py::test_security_headers` — PASSED
- Live HTTP retest: November 2, 2026, at 17:46:30 GMT — PASSED
- HTTP response status: `200 OK`
- All four required security headers confirmed present in the live HTTP response.

**Current status:** Remediated and verified in the local development environment.

**Residual risk:**

HTTP security headers provide defense-in-depth protection but do not replace secure input handling, authentication, authorization, or server-side security controls. Production deployment requires additional security testing and configuration review.