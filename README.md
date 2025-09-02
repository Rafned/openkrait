# OpenKrait v1.0.0
Your automated watchman for Kubernetes and beyond.

Wake up to the smell of coffee, not alerts. OpenKrait scans manifests, analyzes logs, and checks pipelines while you sleep.

## How It Works
OpenKrait is built on a modular architecture. Here's how the components interact:

## Technical Details
**Core Configuration** - Single-point YAML config loading. Supports nested keys via dot notation. Gracefully handles missing config files.

**Kubernetes Scanner** uses the official library and:
- Auto-detects context (in-cluster or local)
- Integrates with Trivy for image scanning
- Checks ConfigMaps for sensitive data
- Respects request limits (DoS protection)

**Log Analyzer**:
- Sanitizes paths (path traversal protection)
- Validates file sizes (<10 MB)
- Detects errors without exposing log contents

**Secret Manager**:
- Requires HTTPS + SSL verification
- Checks storage limits
- Supports stdin input for automation

**Pipeline Optimizer**:
- Auto-detects platform (Jenkins/GitLab/GitHub)
- Analyzes for caching/parallel strategies
- Provides actionable recommendations

## Quick Start
### Installation
  pip install openkrait
# Or via Docker  
  docker build -t openkrait:1.0.0 .
  docker run --rm -v $(pwd):/data your-username/openkrait:1.0.0 scan-k8s

Usage Examples
# Cluster Scanning:
  openkrait scan-k8s
    → Finds vulnerable images (nginx:1.14.*)
    → Checks ConfigMaps for "password" in keys
    → Integrates with Trivy if available
# Log Analysis:    
  openkrait analyze-logs --log-path /var/log/app.log
    → Detects ERROR/WARN without exposing sensitive data
    → Works with files up to 10MB
# Secret Management:    
  echo "my-secret" | openkrait store-secret-stdin  # For scripts
  openkrait store-secret-cmd --secret "my-secret"  # Interactive
    → Saves to Vault with limit checks
    → Requires HTTPS
# Pipeline Optimization:
  openkrait optimize-pipeline --pipeline Jenkinsfile
    → Suggests caching/stash improvements
    → Auto-detects platform   

# Customization
Add your own rules to config.yaml:   

  vulnerability:
    images:
      - pattern: "^my-old-image:.*"
        recommendation: "Update to my-new-image:1.27"
        severity: low

  limits:
    max_secrets: 10  # Adjust to your needs

Rules apply without system restart.    

# Why OpenKrait?
  Security by default - All checks enabled out-of-the-box
  Zero reconfiguration - Works immediately after installation
  Pragmatic integration - Adapts to available tools
  Human-readable output - Actionable recommendations instead of raw data
  Easy extensibility - New rules via YAML

# Technical Specifications
  Test coverage: 85%
  Support: Python 3.8+
  Dependencies: hvac, pyyaml, kubernetes, click
  Docker image size: <100MB

For those who prefer peaceful mornings over chaotic investigations.

OpenKrait doesn't replace full monitoring systems but excels as the first tool for morning diagnostics. When dashboards are red and coffee isn't ready yet - one command shows where to start.  

# P.S. I welcome all feedback and suggestions. I'll update the software with new features as time permits