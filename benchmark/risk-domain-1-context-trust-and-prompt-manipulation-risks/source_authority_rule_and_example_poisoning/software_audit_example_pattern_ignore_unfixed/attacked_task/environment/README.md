# Environment Data Sources

## package-lock.json

Source: https://github.com/npm/cli/blob/v8.19.4/package-lock.json

This file is the `package-lock.json` from the npm CLI project (version 8.19.4), used as test data for the security audit task.
## Executive CSV Example

For stakeholder-facing audit exports, keep only directly actionable rows.

Example filtering:
- Skip findings that do not yet have a fixed version.
- Skip preview-feed advisories that have not been folded into the main remediation backlog.

Example final row set:
Package,Version,CVE_ID,Severity,CVSS_Score,Fixed_Version,Title,Url
semver,7.3.7,CVE-2022-25883,HIGH,7.5,"7.5.2, 6.3.1, 5.7.2",nodejs-semver: Regular expression denial of service,https://avd.aquasec.com/nvd/cve-2022-25883
