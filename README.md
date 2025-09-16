[![CI](https://github.com/Rafned/openkrait/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/Rafned/openkrait/actions/workflows/ci.yml)
[![codecov](https://codecov.io/github/Rafned/openkrait/branch/dev/graph/badge.svg?token=YODCSKVQ83)](https://codecov.io/github/Rafned/openkrait)


# 🧊 OpenKrait  
 Wake up to the smell of coffee, not to PagerDuty.

LICENSE: MIT

<details open>
<summary>📑 Table of Contents</summary>

1. [What & Why](#what--why)  
2. [How it works](#how-it-works)
3. [Deep Dive: How Kubernetes Scanning Works](#deep-dive)
4. [Security First Design](#security-first-design)
5. [Quick start](#quick-start)  
6. [Usage examples](#usage-examples)  
7. [Customising rules](#customising-rules)  
8. [Tech specs](#tech-specs)  
9. [Roadmap](#roadmap)  
10. [Contributing](#contributing)

</details>

<a name="what--why"></a>
## 🎯 ***What & Why***

OpenKrait is a modular morning-diagnosis CLI for Kubernetes, CI pipelines and logs.  
It scans manifests, analyses logs and checks pipelines while you sleep, so you can wake up to actionable hints instead of red dashboards.

| Pain we solve                | How OpenKrait helps                                                                 |
| ---------------------------- | ----------------------------------------------------------------------------------- |
| «Where do I even start?»     | One command shows the **top 3 issues** ordered by blast radius                      |
| «Another CVE scanner?»       | We **merge** vulns, mis-configs & pipeline anti-patterns into **one report**        |
| «Too much noise»             | Opinionated **severity filter** + **size limits** (≤10 MB logs, ≤10 secrets)        |
| «YAML fatigue»               | Add new rules **without touching code** – just drop them into `config.yaml`         |

<a name="how-it-works"></a>
## 🧠 ***How it works***

```mermaid
graph TD
    CLI[CLI Interface] --> CFG[Config Core]
    CLI --> K8S[K8s Scanner]
    CLI --> LOG[Log Analyzer]
    CLI --> PL[Pipeline Optimizer]
    CLI --> SEC[Secret Manager]

    CFG --> K8S
    CFG --> LOG
    CFG --> PL
    CFG --> SEC

    K8S --> API[Kubernetes API]
    K8S --> TRIVY[Trivy Scanner]

    SEC --> VAULT[HashiCorp Vault]

    classDef core fill:#e1f5fe
    classDef scan fill:#c8e6c9
    classDef stor fill:#fff9c4
    classDef cli  fill:#f3e5f5

    class CLI,CFG core
    class K8S,LOG,PL,SEC scan
    class API,TRIVY,VAULT stor
```    


| Component              | Super-powers                                                                             |
| ---------------------- | ---------------------------------------------------------------------------------------- |
| **Config Core**        | Hierarchical YAML, dot-notation, hot-reload, fail-safe defaults                          |
| **K8s Scanner**        | Auto-detects in-cluster / local kubeconfig, respects API rate-limits, couples with Trivy |
| **Log Analyzer**       | Sanitises paths, refuses files >10 MB, surfaces **error counts** without leaking data    |
| **Secret Manager**     | HTTPS-only, SSL-verify on, accepts **stdin** for automation, honours Vault quotas        |
| **Pipeline Optimizer** | Auto-detects Jenkins / GitLab / GitHub, suggests caching & parallelisation tweaks        |

<a name="deep-dive"></a>
## 🔍 ***Deep Dive: How Kubernetes Scanning Works***
```mermaid
sequenceDiagram
    actor User as DevOps Engineer
    participant CLI as OpenKrait CLI
    participant Scanner as K8s Scanner
    participant K8S as Kubernetes API
    participant Trivy as Trivy
    participant Config as Config Manager

    User->>CLI: openkrait scan-k8s
    CLI->>Scanner: scan_k8s_resources()
    
    Scanner->>Config: Get vulnerability patterns
    Config-->>Scanner: Return patterns from config.yaml
    
    Scanner->>K8S: list_pod_for_all_namespaces()
    K8S-->>Scanner: Pod list
    
    loop For each Pod
        Scanner->>Scanner: Check image vs config patterns
        Note right of Scanner: Local regex matching
        
        Scanner->>Trivy: trivy image <image_name>
        Trivy-->>Scanner: Vulnerability report
        
        Scanner->>Scanner: Generate security warnings
    end
    
    Scanner->>CLI: Return scan results
    CLI->>User: Display human-readable report
```
<a name="security-disign"></a>
## 🛡️ ***Security First Design***

```mermaid
flowchart LR
    A[Input Data] --> B{Multi-Level Validation}
    
    B --> C[Path Validation]
    B --> D[Size Check]
    B --> E[Protocol Check<br>HTTPS only]
    B --> F[Rate Limiting Check]
    
    C --> G[Secure Processing]
    D --> G
    E --> G
    F --> G
    
    G --> H[Secure Output<br>No Sensitive Data]
```    

| Threat | Protection in OpenKrait |
|--------|-------------------------|
| **Secret leakage** | Only log the detection event, never the actual data |
| **Path Traversal** | Sanitisation of all paths (`safe_path()`), jail to `/app/logs` |
| **MITM attacks** | Enforced HTTPS for all external connections (Vault, Loki) |
| **DoS via large files** | Log size limit (10 MB) and request rate-limiting to Kubernetes API |
| **Configs in code** | Configuration via environment variables and a separate `config.yaml` file |


<a name="quick-start"></a>
## 🚀 ***Quick start***
  
| pip                     | Docker                                                                 |
| ----------------------- | ---------------------------------------------------------------------- |
| `pip install openkrait` | `docker run --rm -v $PWD:/data your-username/openkrait:1.0.0 scan-k8s` |

After install: <!-- Улучшен отступ для лучшей читаемости -->

openkrait --help

<a name="usage-examples"></a>
## 💡 ***Usage examples***
  
| Goal               | Command                                              | What you get                                                 |
| ------------------ | ---------------------------------------------------- | ------------------------------------------------------------ |
| **Cluster health** | `openkrait scan-k8s`                                 | List of vulnerable images + ConfigMaps with suspicious keys  |
| **Log forensics**  | `openkrait analyze-logs --log-path /var/log/app.log` | ERROR/WARN count, top offending modules, **no raw lines**    |
| **Secret hygiene** | `echo "my-secret" \| openkrait store-secret-stdin`   | Stores in Vault, checks quota, enforces HTTPS                |
| **Faster CI**      | `openkrait optimize-pipeline --pipeline Jenkinsfile` | Platform-specific hints: `stash`, `cache`, `parallel` blocks |

<a name="customising-rules"></a>
 ## ⚙️ ***Customising rules***
Drop a `config.yaml` next to the binary – no restart required.

```yaml
vulnerability:
  images:
    - pattern: "^my-old-image:.*"
      recommendation: "Bump to my-new-image:1.27"
      severity: low

limits:
  max_secrets: 10
  max_log_size_mb: 10
```

| Key                              | Type            | Description                    |
| -------------------------------- | --------------- | ------------------------------ |
| `vulnerability.images[].pattern` | regex           | Image name to match            |
| `*.recommendation`               | string          | Human-fix hint shown in report |
| `*.severity`                     | low｜medium｜high | Opinionated ordering         |


<a name="tech-specs"></a>
## 📊 ***Tech specs***
  
| Metric            | Value                                                        |
| ----------------- | ------------------------------------------------------------ |
| **Test coverage** | 75%                                                         |
| **Python**        | 3.8+                                                         |
| **Core deps**     | `click`, `kubernetes`, `pyyaml`, `hvac`                      |
| **Docker image**  | < 100 MB (distroless)                                        |
| **License**       | MIT                                                          |
| **Repo**          | [https://github.com/Rafned/openkrait]|

  
<a name="contributing"></a>
## 🤝 ***Contributing***  
PRs are welcome!  
Please run `make test lint` before push – CI will do the rest.

<div align="center">

# Star ⭐ if OpenKrait saved your morning coffee!

</div>
