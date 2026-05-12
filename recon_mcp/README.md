# recon-mcp

Stdio MCP server that runs ephemeral DigitalOcean recon droplets.

## Tools

- `recon_start({targets, target_name, scan_region?, probe_regions?, max_droplets?})`
- `recon_status({job_id})`
- `recon_results({job_id})`
- `recon_cancel({job_id})`
- `recon_list_jobs({})`
- `recon_cleanup_orphans({})`

## Env

| Var | Default | Required |
| --- | --- | --- |
| `DO_API_TOKEN` | — | yes |
| `SHODAN_API_KEY` | — | no (shodan phase skipped if unset) |
| `C99_API_KEY` | — | no (c99 phase skipped if unset) |
| `RECON_DB_PATH` | `.recon/jobs.sqlite` | no |
| `RECON_SSH_KEY_DIR` | `.recon/ssh` | no |
| `RECON_MAX_DROPLETS_PER_JOB` | 10 | no |
| `RECON_MAX_RUNTIME_MIN` | 180 | no |
| `RECON_DEFAULT_SCAN_REGION` | nyc1 | no |
| `RECON_DROPLET_SIZE` | s-2vcpu-4gb | no |

## Pipeline

For each target:

| kind     | phases run                                                  |
|----------|-------------------------------------------------------------|
| IP       | scan → subdomains → resolve → httpx → ferox                 |
| CIDR     | scan → subdomains → resolve → httpx → ferox                 |
| wildcard | subdomains → resolve → httpx → ferox  (scan skipped)        |

Phases run sequentially per droplet but droplets run in parallel across regions and across targets. The scan-region droplet handles the heavyweight masscan; probe-region droplets duplicate the httpx + ferox phases for geo comparison.

## Costs

s-2vcpu-4gb ≈ $0.036/h. A 90-min job = $0.054 per droplet. Five regions × 90 min ≈ $0.27. Orphan sweep cron (`bin/recon-orphan-sweep.sh`) kills runaways every 15 min.

## Safety

- CIDRs > /15 (≥131k hosts) refused.
- > 100 targets per job refused.
- Every droplet tagged `recon-mcp` + `job:<id>`.
- Cancel destroys every tagged droplet attached to the job.
- Cleanup-orphans destroys every tagged droplet whose owning job is terminal or unknown.
