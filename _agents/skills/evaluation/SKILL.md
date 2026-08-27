---
name: evaluation
description: Executes 4-tier stratified golden evaluation benchmarks and reports quantitative pass rates.
---

# 4-Tier Evaluation Harness Skill

## Overview
Runs regression testing across 4 test tiers:
1. **Tier 1 (Happy Path)**: Core leave balance inquiries and IT ticket creations.
2. **Tier 2 (Routing Traps)**: Boundary queries testing correct tool selection between WorkWeek, ServiceImmediately, and RAG.
3. **Tier 3 (Hallucination Baits)**: Synthetic non-existent policy questions verifying refusal and grounding citations.
4. **Tier 4 (Adversarial Injections)**: Prompt injection attacks and cross-user data tampering probing Model Armor.

## Execution Workflow
```bash
python3 -m unittest eval_benchmark.py
```
Target: 100% Pass Rate across all 12 Golden Test Cases.
