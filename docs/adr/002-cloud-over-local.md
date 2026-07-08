# ADR 0002: Cloud (GCP) over Local-First Stack

## Status
Accepted

## Context
Two candidate architectures were considered for the data lake layer:
1. A fully local stack (local filesystem as the data lake) — faster to set up, zero cloud cost, but doesn't demonstrate cloud infrastructure or IaC skills.
2. A cloud-based stack (GCS as the data lake, provisioned via Terraform) more setup overhead, but aligns with prior hands-on experience with GCP and Terraform, and better reflects how a production data platform would actually be deployed.

## Decision
Use GCS as the data lake, provisioned via Terraform, rather than a local filesystem.

## Consequences
- Reinforces and extends existing GCP/Terraform experience rather than introducing an entirely disconnected toolset.
- Requires managing GCP credentials/service accounts locally (WSL) and ongoing awareness of storage costs, which a local-only stack would have avoided entirely.
- Adds a real dependency on internet connectivity and GCP availability during development, versus a local stack that works offline.