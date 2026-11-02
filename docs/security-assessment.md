
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



## Phase 3 — Docker Containerization and Security Validation

### Control SEC-002: Non-Root Container Execution

**Assessment Date:** November 2, 2026

**Objective:**

Verify that the containerized Flask application runs under a dedicated non-root Linux user rather than the default root account.

**Implementation:**

- Built the application using the `python:3.13-slim` Docker base image.
- Configured the Dockerfile to create an application user with UID 10001.
- Set `USER appuser` in the Dockerfile.
- Configured Waitress to serve the Flask application on port 8080.
- Bound the host port to `127.0.0.1` for local testing.

**Validation Results:**

- Container status: Running
- HTTP response: 200 OK
- Application server: Waitress
- Runtime user: `uid=10001(appuser)`
- Runtime group: `gid=10001(appuser)`
- HTTP security headers: All four previously implemented headers present

**Evidence:**

- `evidence/docker-container-status.txt`
- `evidence/docker-security-headers.txt`
- `evidence/docker-nonroot-user.txt`
- `evidence/docker-security-config.txt`

**Assessment Result:** Passed — non-root container execution verified.

**Residual Risk:**

Running as a non-root user reduces the privileges available to the application but does not eliminate container security risks.

Additional assessments are required for dependency vulnerabilities, base-image vulnerabilities, Linux capabilities, filesystem permissions, and container runtime configuration.

**Next Action:**

Perform dependency and container-image vulnerability scanning, review the findings, and document remediation or risk acceptance decisions.


### Finding SEC-003: Vulnerable Components in Container Image

**Assessment date:** November 2, 2026

**Assessment tool:** Docker Scout

**Initial target:** `azure-flask-security-portfolio:local`

**Current status:** Open — Mitigation implemented; residual findings under investigation

#### 1. Initial Vulnerability Assessment

Docker Scout identified 37 vulnerabilities in the original Debian slim application image:

- Critical: 0
- High: 7
- Medium: 3
- Low: 27
- Total: 37
- Vulnerable packages: 16

High-severity vulnerabilities were identified in `msgpack`, `urllib3`, `setuptools`, and Debian `zlib`.

**Risk:** Known vulnerabilities in container components may affect confidentiality, integrity, or availability, depending on their runtime presence, exploitability, and application exposure.

**Initial remediation plan:**

1. Review application dependencies.
2. Investigate the source of reported vulnerabilities.
3. Evaluate alternative base images.
4. Rebuild and rescan the container.
5. Document residual vulnerabilities and risk treatment.

#### 2. Root-Cause Investigation — Debian Base Image

A separate Docker Scout scan of `python:3.13-slim` reported the same 37 vulnerabilities as the original application image.

Inspection of the application's active Python environment did not identify installed `msgpack`, `urllib3`, or `setuptools` packages.

These results indicate that the scanner findings were inherited from the upstream Python base image rather than newly introduced by the Flask application's installed dependencies.

The runtime applicability of the reported Python package vulnerabilities was not conclusively established.

#### 3. Mitigation — Alpine Base Image

An alternative container image was built using `python:3.13-alpine`.

The application retained:

- The Waitress application server
- Non-root execution under UID 10001 (`appuser`)
- HTTP security headers
- Localhost-only published port binding

**Validation results:**

- Container started successfully.
- Homepage returned HTTP 200.
- Homepage and blog posts loaded successfully.
- Configured HTTP security headers were present.
- The running container executed under UID 10001.

Docker Scout reported the following findings for the Alpine application image:

| Severity | Debian slim | Alpine |
|---|---:|---:|
| Critical | 0 | 0 |
| High | 7 | 6 |
| Medium | 3 | 2 |
| Low | 27 | 1 |
| Unspecified | 0 | 1 |
| **Total** | **37** | **10** |

**Result:** The Alpine alternative reduced reported vulnerabilities by approximately 73%, while preserving the tested application functionality and security controls.

#### 4. Root-Cause Investigation — Alpine Base Image

A separate Docker Scout scan of the official `python:3.13-alpine` base image reported the same 10 vulnerabilities found in the Alpine application image.

The findings involved four packages:

- `msgpack`
- `urllib3`
- `setuptools`
- `musl`

The first three packages were not found in the application's active Python environment using `pip show`.

Docker Scout associated their findings with the upstream Python base image. Further investigation is required to establish whether these represent build-time inventory or exploitable runtime components.

The installed `musl` version was confirmed as `1.2.6-r3`. Docker Scout identified `1.2.6-r6` as the fixed version for CVE-2026-107891.

After refreshing the Alpine 3.24 package indexes, the configured repositories continued to list `1.2.6-r3`. The reported fix was therefore not available through the configured repositories at the time of testing.

#### 5. Residual Risk and Treatment Plan

The Alpine image continues to have 10 reported vulnerabilities, including six High-severity findings.

The remaining risks have not been accepted or classified as false positives.

**Base-image recommendation review:** Docker Scout was used to evaluate `python:3.13-alpine` for available base-image updates or alternatives. The tool returned "No recommendations." The Alpine image was therefore retained as the preferred local development and testing candidate, subject to continued vulnerability monitoring and further assessment of outstanding findings. This decision does not constitute formal risk acceptance or production deployment approval.

**Next actions:**

1. Review Docker Scout base-image recommendations.
2. Investigate the runtime applicability of the inherited Python package findings.
3. Monitor Alpine repository availability for the patched `musl` package.
4. Rebuild and rescan when suitable updates become available.
5. Reassess residual risk before production deployment.

#### 6. Evidence

- `evidence/docker-scout-baseline.txt`
- `evidence/docker-scout-alpine.txt`
- `evidence/docker-scout-alpine-base.txt`
- `evidence/alpine-container-status.txt`
- `evidence/alpine-security-headers.txt`
- `evidence/alpine-nonroot-user.txt`

**Final assessment status:** Open — The Alpine alternative has been validated as a mitigation, but outstanding vulnerabilities require further investigation and treatment before the finding can be closed.