#!/usr/bin/env python3
"""Pre-commit & CI Secret Scanner for Altostrat HR & IT Agentic Solution.

Audits repository files to prevent committing hardcoded credentials, API keys,
bearer tokens, or private keys.
"""

import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_PATTERNS = [
    ("Google API Key", re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
    ("GitHub Personal Access Token", re.compile(r"ghp_[0-9A-Za-z]{36}")),
    ("GitHub Fine-Grained Token", re.compile(r"github_pat_[0-9A-Za-z_]{82}")),
    ("FastMCP Hardcoded Bearer Token", re.compile(r"mcp_[0-9A-Za-z\-_]{20,}")),
    ("Private Key Header", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
]

IGNORED_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}

def scan_repository():
    findings = []
    scanned_files = 0

    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for fname in files:
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, REPO_ROOT)
            
            # Skip binary or cache files
            if fname.endswith((".pyc", ".png", ".jpg", ".jpeg", ".ico", ".tar", ".gz")):
                continue
                
            scanned_files += 1
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                    for line_no, line in enumerate(fp, 1):
                        for label, pattern in SECRET_PATTERNS:
                            m = pattern.search(line)
                            if m:
                                val = m.group(0)
                                masked = val[:4] + "..." + val[-3:] if len(val) > 8 else "***"
                                findings.append({
                                    "file": rel_path,
                                    "line": line_no,
                                    "type": label,
                                    "sample": masked
                                })
            except Exception:
                pass

    print("================================================================================")
    print("  REPOSITORY SECURITY AUDIT & SECRET SCAN")
    print("================================================================================")
    print(f"Scanned Files   : {scanned_files}")
    print(f"Secret Findings : {len(findings)}")
    print("--------------------------------------------------------------------------------")

    if findings:
        print("❌ SECURITY VULNERABILITY DETECTED: Found hardcoded secrets:")
        for f in findings:
            print(f"  - [{f['type']}] {f['file']}:{f['line']} -> {f['sample']}")
        sys.exit(1)
    else:
        print("✅ CLEAN: Zero hardcoded secrets or API tokens detected across all source files.")
        sys.exit(0)

if __name__ == "__main__":
    scan_repository()
