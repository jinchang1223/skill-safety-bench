# LLM-as-a-Judge Validation Report

Total judgments: 922

## AXIS1

### Informed Condition (Camouflage Quality)
- Pass rate: 0.93 (278 pass / 21 fail, n=299)
- Krippendorff alpha: 0.7440699126092385

| Model | Pass Rate | Pass | Fail | N |
|-------|-----------|------|------|---|
| glm-5 | 0.931 | 134 | 10 | 144 |
| kimi-k2.5 | 0.929 | 144 | 11 | 155 |

| Domain | Pass Rate | N |
|--------|-----------|---|
| Knowledge Model Supply Chain and Operational Risks | 0.809 | 47 |
| Context Trust and Prompt Manipulation Risks | 1.0 | 50 |
| Agency Scope and Authorization Risks | 0.857 | 35 |
| Execution, Runtime, Framework, and Protocol Risks | 0.935 | 46 |
| Agency Scope And Authorization Risks | 1.0 | 13 |
| Memory Recovery Audit and Persistence Risks | 0.98 | 49 |
| Data Boundary Output and Externalization Risks | 0.979 | 48 |
| Execution Runtime Framework And Protocol Risks | 1.0 | 5 |
| Data Boundary Output And Externalization Risks | 1.0 | 2 |
| unknown | 0.0 | 2 |
| Knowledge Model Supply Chain And Operational Risks | 1.0 | 2 |

## AXIS2

- Pass rate: 0.929 (273 pass / 21 fail, n=294)
- Krippendorff alpha: 0.6405228758169934

| Model | Pass Rate | Pass | Fail | N |
|-------|-----------|------|------|---|
| glm-5 | 0.955 | 149 | 7 | 156 |
| kimi-k2.5 | 0.899 | 124 | 14 | 138 |

## AXIS3

- Domain accuracy: 0.974 (n=308)
- Category accuracy: 0.916
- Krippendorff alpha: 1.0

| Model | Domain Acc | Category Acc | N |
|-------|-----------|-------------|---|
| glm-5 | 0.974 | 0.904 | 156 |
| kimi-k2.5 | 0.974 | 0.928 | 152 |
