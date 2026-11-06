# Azure-Inspired Flask Security Portfolio

**A hands-on application security, Docker hardening, vulnerability management, and DevSecOps project.**

## Project Overview

This project demonstrates a security-focused reconstruction of a Flask web application, informed by earlier Azure cloud-security coursework.

The objective is to implement and validate practical security controls, identify vulnerabilities, document residual risks, and establish repeatable security testing through a CI/CD workflow.

The application currently runs in a local Docker environment. It is **not deployed to Microsoft Azure**, and the project does not claim production readiness.

## Technology Stack

| Category | Technologies |
|---|---|
| Application | Python, Flask, HTML, CSS |
| Application server | Waitress |
| Containerization | Docker, Debian slim, Alpine Linux |
| Security assessment | Docker Scout, pip-audit, Gitleaks |
| Container scanning in CI | Trivy |
| Automated testing | pytest |
| CI/CD | GitHub Actions |
| Security frameworks | NIST SP 800-53, ISO/IEC 27001:2022 |

## Security Implementation

### 1. HTTP Security Headers — SEC-001

The initial application assessment identified four missing HTTP response headers:

- `Content-Security-Policy`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `Referrer-Policy`

An `after_request` handler was implemented in Flask to add these headers.

**Validation:** All four headers were confirmed through live HTTP testing and an automated pytest test.

**Status:** Remediated and verified locally.

Evidence: [Before](evidence/headers-before.txt) | [After](evidence/headers-after.txt)

### 2. Non-Root Container Execution — SEC-002

The Flask application was containerized using Docker and configured to run through Waitress.

A dedicated application user with UID `10001` was configured to avoid running the application as root.

**Validation:** Container inspection and runtime commands confirmed non-root execution, HTTP 200 responses, and the presence of the configured security headers.

**Status:** Verified.

Evidence: [Non-root user verification](evidence/docker-nonroot-user.txt)

### 3. Container Vulnerability Management — SEC-003

Docker Scout was used to assess container-image vulnerabilities and compare Debian slim and Alpine-based images.

The initial Debian slim image reported 37 vulnerabilities. An Alpine-based alternative initially reported 10, representing an approximately 73% reduction in reported findings.

A subsequent assessment on November 3, 2026, identified 11 findings in the Alpine image:

| Severity | Findings |
|---|---:|
| Critical | 0 |
| High | 7 |
| Medium | 2 |
| Low | 1 |
| Unspecified | 1 |
| **Total** | **11** |

Affected packages included `msgpack`, `urllib3`, `setuptools`, `sqlite`, and `musl`.

Further investigation evaluated an experimental Alpine runtime image with pip removed after dependency installation. Docker Scout reported 3 vulnerabilities in the experimental image, compared with 12 in its corresponding upstream base image. The remaining findings involved `zlib` (critical), `musl` (high), and `sqlite` (high).

This was an experimental mitigation assessment, not an approved replacement for the validated application image. Full application regression testing of the experimental image remains outstanding.

The Trivy report from the verified GitHub Actions run contained 8 findings: 5 high, 2 medium, and 1 low. Differences between scanner results and assessment dates are documented in the full security report.

Further investigation and risk treatment remain necessary before any production deployment.

**Status:** Open — mitigation implemented, residual vulnerabilities unresolved.

Evidence: [Docker Scout SARIF report](evidence/container-scout.sarif.json)

### 4. Container Runtime Hardening — SEC-004

Additional Docker runtime restrictions were implemented:

- Read-only root filesystem
- All Linux capabilities dropped
- `no-new-privileges` enabled
- Non-root UID `10001`
- Process limit of 100
- Memory limit of 256 MiB
- CPU limit of one CPU
- Restricted 16 MiB temporary filesystem with `noexec` and `nosuid`

**Validation:** Runtime configuration was inspected, non-root execution was confirmed, and an attempted write to the read-only application filesystem failed as expected.

Resource limits were verified through configuration inspection but were not independently stress-tested.

**Status:** Implemented and functionally validated.

Evidence: [Runtime configuration](evidence/runtime-security-config.txt) | [Read-only filesystem test](evidence/runtime-readonly-test.txt)

## Automated Security Testing

### Application Tests

Six pytest tests passed locally, covering:

1. Homepage response
2. Valid article response
3. Unknown article handling
4. Homepage content
5. Debugger exposure
6. HTTP security headers

Test suite: [`tests/test_app.py`](tests/test_app.py)

### Python Dependency Audit

`pip-audit` was executed against `requirements.txt`.

**Result:** No known vulnerabilities found in the evaluated dependency set at the time of assessment.

This result does not imply that the container image is free of vulnerabilities.

Evidence: [Dependency audit](evidence/dependency-audit.txt)

### Repository Secret Scanning

Gitleaks v8.24.3 was used to scan the local Git history before publication.

**Result:** 10 commits scanned; no leaks detected; exit code 0.

This result is limited to the scanner's detection capabilities and the repository history evaluated.

## CI/CD Security Workflow

The GitHub Actions workflow is configured with three jobs:

| Job | Purpose |
|---|---|
| `test` | Run application tests using pytest |
| `dependency-audit` | Check Python dependencies using pip-audit |
| `container-scan` | Build the Alpine Docker image and scan it using Trivy |

The workflow also includes:

- GitHub Actions pinned to full commit SHAs
- Read-only repository permissions
- Disabled checkout credential persistence
- SARIF vulnerability-report generation
- Upload of the Trivy report as a workflow artifact

**CI status:** Verified on GitHub-hosted runners. All three jobs passed in [GitHub Actions run #1](https://github.com/njokun/azure-flask-security-portfolio/actions/runs/41721781116). The Trivy scan operates in report-only mode and does not block the workflow on vulnerability findings.

The Trivy job currently uses `exit-code: '0'`, meaning vulnerability findings are reported without automatically failing the workflow.

Workflow: [Flask Security Tests](.github/workflows/python-tests.yml)

## Security Assessment and Risk Management

The project uses a documented assessment process:

**Identify → Assess → Mitigate → Validate → Document → Reassess**

| Finding | Description | Status |
|---|---|---|
| SEC-001 | Missing HTTP security headers | Remediated |
| SEC-002 | Non-root container execution | Verified |
| SEC-003 | Container-image vulnerabilities | Open |
| SEC-004 | Container runtime hardening | Implemented and validated |

The assessment also references relevant security-control areas:

- NIST SP 800-53 RA-5 — Vulnerability Monitoring and Scanning
- NIST SP 800-53 SI-2 — Flaw Remediation
- ISO/IEC 27001:2022 Annex A 8.8 — Management of Technical Vulnerabilities
- ISO/IEC 27001:2022 Annex A 8.29 — Security Testing in Development and Acceptance

These references demonstrate control alignment, not full framework compliance or independent certification.

Full report: [Security Assessment and Validation Report](docs/security-assessment.md)

## Project Evidence

Supporting assessment artifacts are stored in the [`evidence/`](evidence/) directory, including:

- HTTP response-header captures
- Docker container configuration and runtime verification
- Non-root execution evidence
- Docker Scout vulnerability reports
- Python dependency audit results
- Container hardening validation
- Application screenshots and functional test evidence

## Current Limitations

- No active Azure deployment or Azure WAF integration
- No HTTPS termination in the local testing environment
- No cloud identity integration or centralized security logging
- Outstanding container-image vulnerabilities
- No production security approval
- GitHub-hosted CI execution verified; container vulnerability reporting remains non-blocking
- Automated vulnerability reporting is not currently configured as an enforcement gate

## Next Steps

1. Monitor GitHub Actions execution and review future security scan results.
2. Reassess outstanding vulnerabilities when updated packages or base images become available.
3. Investigate and prioritize unresolved container vulnerabilities.
4. Rebuild, retest, and rescan after approved updates.
5. Document remediation and residual-risk decisions.
6. Evaluate further security testing and a future Azure deployment.

## Project Background

This portfolio reconstructs and extends application and cloud-security concepts explored during University of Toronto cybersecurity coursework.

The original Azure training environment is no longer available. The current project therefore focuses on reproducible local implementation, evidence-based validation, and transparent security reporting.

The project is intended to demonstrate practical cybersecurity engineering, vulnerability management, security-control validation, and technical documentation skills.
