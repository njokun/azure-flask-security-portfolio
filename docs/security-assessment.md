# Flask Security Assessment and Validation Report

## Local Application Baseline — November 2, 2026

**Assessment date:** November 2, 2026

### Environment

- Python version: Not recorded in the baseline.
- Flask version: Not recorded in the baseline.
- Operating system: Not recorded in the baseline.
- Host: 127.0.0.1
- Port: 5000

### Scope

Local Flask application and its HTTP routes.

### Test Results

| Test ID | Test | Expected | Actual | Status |
|---|---|---|---|---|
| T-001 | Homepage request | 200 | 200 | Pass |
| T-002 | Existing article | 200 | 200 | Pass |
| T-003 | Unknown article | 404 | 404 | Pass |
| T-004 | Response header review | Record headers | Headers recorded | Reviewed |

### Security Limitations

- No HTTPS in the local environment
- No Azure WAF
- No cloud identity integration
- No centralized security logging
- Flask development server is not production-ready

### Next Steps

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

**Assessment date:** November 2, 2026

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

**Assessment result:** Passed — non-root container execution verified.

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

At the time of the initial Alpine assessment, the image had 10 reported vulnerabilities, including six high-severity findings. See the November 3 reassessment below for the latest documented count.

These findings were not formally accepted as risks or classified as false positives.

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

#### 7. Vulnerability Reassessment — November 3, 2026

A follow-up assessment using Docker Scout v1.27.0 scanned the existing Alpine application image and a freshly built image tagged `azure-flask-security-portfolio:ci-test`. Both scans returned the same distribution of 11 findings across five packages.

| Severity | Initial Alpine assessment | November 3 reassessment |
|---|---:|---:|
| Critical | 0 | 0 |
| High | 6 | 7 |
| Medium | 2 | 2 |
| Low | 1 | 1 |
| Unspecified | 1 | 1 |
| **Total** | **10** | **11** |

**Affected packages:** `msgpack`, `urllib3`, `setuptools`, `sqlite`, and `musl`.

**Assessment:** The additional finding does not, by itself, establish a deterioration in the application's security posture. Scanner intelligence, advisory publication, and package versions can change between scans. The affected packages require dependency-path investigation, runtime applicability analysis, and patch feasibility review.

**Treatment plan:** Investigate the affected packages and available fixes; prioritize findings based on exposure and exploitability; rebuild, retest, and rescan after approved updates; document unresolved findings and any formal risk decisions.

**Evidence:** `evidence/container-scout.sarif.json`

**Current status:** SEC-003 remains open. No production deployment approval or formal risk acceptance is implied.

## Phase 4 — Container Runtime Hardening

### Finding SEC-004: Container Runtime Hardening

**Assessment date:** November 3, 2026

**Status:** Implemented — Configuration and functional validation completed

**Assessment target:** `flask-security-hardened`

**Risk identified:**

Default container configurations may permit unnecessary filesystem modifications, excessive privileges, or unrestricted resource consumption. These conditions could increase the impact of an application compromise.

**Security controls implemented:**

- Read-only root filesystem to prevent unauthorized modifications.
- Dropped all Linux capabilities to reduce available privileges.
- Enabled `no-new-privileges` to prevent processes from gaining additional privileges through execution.
- Restricted application execution to non-root UID 10001.
- Configured a maximum of 100 processes.
- Configured a 256 MiB memory limit and one CPU limit.
- Configured a 16 MiB temporary filesystem with `noexec` and `nosuid` restrictions.

**Validation performed:**

1. Inspected Docker HostConfig to verify the configured runtime restrictions.
2. Executed the `id` command inside the running container, confirming UID 10001.
3. Attempted to create `/app/security-test.txt` within the container.
4. Confirmed the write attempt failed with the message `Read-only file system`.
5. Previously confirmed the hardened container returned HTTP 200 and retained the application's security headers.

**Assessment conclusion:**

The container successfully demonstrated non-root execution, configured privilege restrictions, and read-only filesystem enforcement.

Resource limits were verified through configuration inspection but have not been independently stress-tested.

These controls reduce the potential impact of application compromise but do not eliminate vulnerabilities identified in the underlying container image.

**Evidence:**

- `evidence/runtime-security-config.txt`
- `evidence/runtime-user-verification.txt`
- `evidence/runtime-readonly-test.txt`

**Residual risk:**

Outstanding container-image vulnerabilities remain documented under SEC-003. Additional security testing and vulnerability reassessment are required before production deployment.

## Phase 5 — Automated Security Testing and CI/CD

### 1. Objective and Scope

**Objective:** Establish repeatable application security testing, Python dependency vulnerability auditing, and container image vulnerability scanning to support early detection of security defects and vulnerable components.

**Scope:**

- Flask application functionality and HTTP security headers.
- Python dependencies declared in `requirements.txt`.
- Alpine-based Docker application image.
- GitHub Actions workflow configuration and vulnerability-report retention.

**Assessment date:** November 3, 2026.

**Status:** Local testing and vulnerability assessments completed. GitHub Actions workflow configured and committed; hosted execution pending.

### 2. Automated Application Security Testing

**Tool:** pytest 9.2.0

**Test suite:** `tests/test_app.py`

Six automated tests were executed successfully in the local Python virtual environment.
| Test area | Expected result | Status |
|---|---|---|
| Homepage | HTTP 200 | Passed |
| Valid article | HTTP 200 | Passed |
| Unknown article | HTTP 404 | Passed |
| Homepage content | Expected content present | Passed |
| Debugger exposure | Debugger not exposed | Passed |
| HTTP security headers | Required headers present | Passed |

**Result:** 6 tests passed locally.

The tests provide regression coverage for selected application behavior and security controls. They do not constitute comprehensive penetration testing or establish that the application is free of vulnerabilities.

### 3. Python Dependency Vulnerability Audit

**Tool:** pip-audit 2.10.1

**Command:**

`python -m pip_audit -r requirements.txt`

**Result:** No known vulnerabilities found. Exit code: 0.

**Evidence:** `evidence/dependency-audit.txt`

The result applies to the application dependency set evaluated from `requirements.txt` at the time of the scan. It does not establish that every package in the Docker image is vulnerability-free.

### 4. Container Vulnerability Assessment

**Tool:** Docker Scout v1.27.0

**Image:** `azure-flask-security-portfolio:alpine`

**Assessment date:** November 3, 2026.

A fresh Alpine application image was built using the `ci-test` tag and scanned independently. Both the existing Alpine image and the fresh build returned the same vulnerability distribution.
| Severity | Findings |
|---|---:|
| Critical | 0 |
| High | 7 |
| Medium | 2 |
| Low | 1 |
| Unspecified | 1 |
| **Total** | **11** |

**Affected packages:** `msgpack`, `urllib3`, `setuptools`, `sqlite`, and `musl`.

The scanner reported available fixed versions for several affected packages. The SQLite finding had no fixed version reported at the time of assessment.

**Evidence:** `evidence/container-scout.sarif.json`

**Risk status:** Open — tracked under SEC-003.

These findings require further vulnerability triage, dependency-path investigation, patch feasibility assessment, and documented risk treatment. Package presence alone does not establish exploitability in the application.

The current result supersedes the earlier 10-finding Alpine baseline for the November 3 reassessment. The earlier baseline remains part of the assessment history.

### 5. CI/CD Security Testing Configuration

**Workflow:** `.github/workflows/python-tests.yml`

**Branch:** `master`

**Configured triggers:** Push and pull request events targeting `master`.

Three independent jobs have been configured:
| Job | Purpose | Status |
|---|---|---|
| `test` | Execute Flask application tests with pytest | Locally validated; CI execution pending |
| `dependency-audit` | Audit Python dependencies using pip-audit | Locally validated; CI execution pending |
| `container-scan` | Build the Alpine image and scan it using Trivy | YAML configuration validated; CI execution pending |

The container scanning job is configured to generate a SARIF report and upload it as a GitHub Actions artifact with a requested retention period of 30 days.

The Trivy scan currently uses `exit-code: '0'`, allowing vulnerability findings to be reported without automatically failing the CI job.

**Important limitation:** The workflow has been validated for YAML parsing and expected job configuration, but has not yet executed on GitHub-hosted runners. Successful execution, scanner compatibility, and artifact retention have not yet been independently verified.

### 6. Security Control Alignment

The activities performed provide supporting evidence relevant to the following security-control areas:
| Framework | Control | Relevance |
|---|---|---|
| NIST SP 800-53 | RA-5 — Vulnerability Monitoring and Scanning | Dependency and container vulnerability identification |
| NIST SP 800-53 | SI-2 — Flaw Remediation | Identification and tracking of components requiring remediation |
| ISO/IEC 27001:2022 Annex A | 8.8 — Management of Technical Vulnerabilities | Vulnerability identification, assessment, and treatment planning |
| ISO/IEC 27001:2022 Annex A | 8.29 — Security Testing in Development and Acceptance | Automated application security regression testing |

These are control-alignment references, not claims of full framework compliance or independent audit certification.

### 7. Residual Risks and Limitations

- SEC-003 remains open with 11 reported container-image vulnerabilities.
- Automated scans identify known vulnerabilities but cannot detect every security defect.
- Vulnerability counts may change as package versions and advisory databases change.
- Docker Scout and Trivy may report different findings because their vulnerability intelligence and analysis methods differ.
- GitHub-hosted workflow execution remains unverified.
- The current container scanning configuration reports vulnerabilities but does not enforce remediation thresholds.
- No comprehensive repository secret scan has yet been completed.

### 8. Recommended Follow-Up Actions

1. Verify the GitHub Actions workflow on GitHub-hosted runners.
2. Confirm successful generation and retention of the Trivy SARIF artifact.
3. Investigate vulnerable packages and their dependency origins.
4. Evaluate available package and base-image updates, then rebuild, test, and rescan.
5. Document vulnerability remediation decisions and any accepted residual risks.
6. Define appropriate CI vulnerability enforcement thresholds.
7. Perform a repository secret scan before public publication.
8. Update SEC-003 with verified remediation evidence and revised vulnerability counts.

### 9. Evidence and Version Control

**Supporting evidence:**

- `tests/test_app.py`
- `evidence/dependency-audit.txt`
- `evidence/container-scout.sarif.json`
- `.github/workflows/python-tests.yml`

**Relevant Git commits:**

- `a0c32c1` — Add GitHub Actions workflow for Flask security tests.
- `482415a` — Add automated dependency auditing and security scan evidence.
- `3ad6da7` — Add automated container scanning and Docker Scout evidence.

**Overall Phase 5 status:** Local testing and assessment completed; automated CI/CD execution and vulnerability remediation remain outstanding.



## Phase 6 — Repository Security and CI/CD Supply-Chain Hardening

**Assessment date:** November 3, 2026

### 1. Git History Secret Scanning

**Tool:** Gitleaks v8.24.3

A repository secret scan was performed using the Gitleaks Docker image.

**Validation results:**

- Git commits scanned: 10
- Data scanned: approximately 106.15 KB
- Secrets detected: 0
- Scanner exit code: 0

**Assessment result:** Passed — no secrets detected in the scanned Git history.

**Limitation:** Automated secret scanning does not guarantee that every possible credential or sensitive value has been identified.

### 2. GitHub Actions Supply-Chain Hardening

The GitHub Actions workflow was updated to strengthen CI/CD security.

**Controls implemented:**

- Pinned all seven GitHub Action references to full commit SHAs.
- Disabled checkout credential persistence in all three jobs.
- Retained read-only repository permissions.
- Preserved automated application testing, dependency auditing, and container vulnerability scanning.

**Validation:**

- Git diff whitespace validation passed.
- Three `persist-credentials: false` settings confirmed.
- Changes committed successfully.

**Git commit:** `188a8da` — Harden GitHub Actions with pinned SHAs and restricted credentials.

**Status:** Configuration hardening completed locally. GitHub-hosted workflow execution remains pending.

### 3. Remaining Security Risks

- SEC-003 remains open with 11 reported container-image vulnerabilities.
- GitHub Actions execution has not yet been validated on hosted runners.
- Trivy currently operates in report-only mode.
- No production deployment approval or formal acceptance of outstanding vulnerabilities has been granted.

#### 8. Experimental Runtime Dependency Minimization — November 2026

**Objective:** Investigate whether removing unnecessary Python package-management tooling from the runtime container reduces reported vulnerabilities.

**Method:**

- Preserved the original Dockerfile.
- Created a separate experimental Dockerfile.
- Installed application dependencies before uninstalling pip.
- Built the experimental image as `flask-security:no-pip`.
- Compared Docker Scout results with the corresponding upstream Python Alpine base image.
- Inspected installed system packages and verified the SQLite runtime version.

**Scan comparison:**

| Image | Critical | High | Medium | Low | Total |
|---|---:|---:|---:|---:|---:|
| Earlier Alpine application reassessment | 0 | 7 | 2 | 1 | 11* |
| Newer Alpine base image | 1 | 8 | 2 | 1 | 12 |
| Experimental application image without pip | 1 | 2 | 0 | 0 | 3 |

*The earlier Alpine assessment also reported one finding with unspecified severity.

The newer base image and experimental image used the same upstream base-image digest. The experimental image had nine fewer reported findings, corresponding to `msgpack`, `urllib3`, and `setuptools`.

Inspection of the earlier runtime image identified pip-vendored copies of `msgpack` and `urllib3`. Removing pip from the experimental runtime image was associated with the absence of these Python-package findings in the subsequent Docker Scout report.

**Remaining findings:**

| Component | Severity | Reported vulnerability | Treatment status |
|---|---|---|---|
| zlib 1.3.2-r1 | Critical | CVE-2026-4738 | Open; fixed version 1.4-r0 reported |
| musl 1.2.6-r3 | High | CVE-2026-107891 | Open; fixed version 1.2.6-r6 reported |
| SQLite 3.53.4 | High | CVE-2026-119586 | Open; no fixed version reported |

Python's SQLite runtime version was independently confirmed as 3.53.4.

A repository package-update check did not identify available upgrades in the experimental container at the time of testing.

**Limitations:**

- The experimental image has not completed full application functionality and security regression testing.
- A lower vulnerability count does not independently establish lower exploitability or production readiness.
- Scanner results depend on the image contents, vulnerability database, and assessment date.
- The experimental Dockerfile has not been adopted as the approved application build.
- Vulnerability remediation and formal risk acceptance remain outstanding.

**Assessment conclusion:**

Runtime dependency minimization demonstrated a reduction in reported Python-package vulnerabilities. The experiment is retained as supporting evidence of vulnerability investigation and mitigation evaluation.

No additional exploratory base-image comparisons are required for completion of this portfolio assessment.

**SEC-003 status: OPEN.** The remaining vulnerabilities require appropriate treatment and reassessment before any production deployment approval.
