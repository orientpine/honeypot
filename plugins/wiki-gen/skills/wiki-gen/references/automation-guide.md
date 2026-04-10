# Wiki Sync Automation Guide

This document provides reference configurations for automating the wiki synchronization process. It covers GitHub Actions for cloud-based automation and systemd timers for local Linux environments.

> **Note**: This is a reference document. Do not use this file directly as a configuration file. Copy the relevant sections into your own `.yml` or `.service` files.

## 1. GitHub Actions Workflow

GitHub Actions is ideal for keeping your wiki updated automatically if your vault or source repositories are hosted on GitHub.

### Example: `sync.yml`

Create this file at `.github/workflows/sync.yml` in your wiki repository.

```yaml
name: Wiki sync
on:
  schedule:
    - cron: '0 21 * * *'          # Runs daily at 06:00 KST (21:00 UTC)
  workflow_dispatch:              # Allows manual triggering from the Actions tab
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0          # Required for git operations

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install pyyaml

      - name: Run sync script
        run: python plugins/wiki-gen/skills/wiki-gen/scripts/sync_sources.py --config sources.yaml --wiki-root wiki/
        env:
          # Only required for private source repositories
          SOURCE_REPOS_TOKEN: ${{ secrets.SOURCE_REPOS_TOKEN }}

      - name: Commit and push changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add raw/ wiki/_index.md wiki/_backlinks.json sync_log.json
          git diff --cached --quiet || (git commit -m "sync: $(date -u +'%Y-%m-%d')" && git push)
```

## 2. systemd User Timer (Linux)

For local automation on a Linux machine (e.g., a home server or workstation), systemd timers are a robust alternative to cron.

### Service Unit: `~/.config/systemd/user/wiki-sync.service`

```ini
[Unit]
Description=Wiki Synchronization Service

[Service]
Type=oneshot
WorkingDirectory=%h/Documents/my_wiki
ExecStart=/usr/bin/python3 plugins/wiki-gen/skills/wiki-gen/scripts/sync_sources.py --config sources.yaml --wiki-root wiki/

[Install]
WantedBy=default.target
```

### Timer Unit: `~/.config/systemd/user/wiki-sync.timer`

```ini
[Unit]
Description=Run Wiki Sync every 6 hours

[Timer]
OnBootSec=10min
OnUnitActiveSec=6h
Persistent=true

[Install]
WantedBy=timers.target
```

### Activation

```bash
systemctl --user daemon-reload
systemctl --user enable --now wiki-sync.timer
```

## 3. Token Management

### Public Repositories
No tokens are required. The sync script can clone public repositories anonymously.

### Private Repositories
To sync from private repositories, you must provide a Personal Access Token (PAT).
- **GitHub Actions**: Store the token in **Settings > Secrets and variables > Actions** as `SOURCE_REPOS_TOKEN`.
- **Local/systemd**: Set the `SOURCE_REPOS_TOKEN` environment variable in your shell profile or within the `[Service]` section of the systemd unit:
  ```ini
  Environment="SOURCE_REPOS_TOKEN=your_pat_here"
  ```
- **Recommended Scope**: Use a "Fine-grained PAT" with `Contents: Read` access to the specific source repositories.

## 4. Scheduling Guide

### GitHub Actions (Cron)
The `cron` syntax is `minute hour day-of-month month day-of-week`.
- `'0 21 * * *'`: Every day at 21:00 UTC (06:00 KST).
- `'0 */6 * * *'`: Every 6 hours.

### systemd Timer
- `OnUnitActiveSec=6h`: Runs 6 hours after the last successful execution.
- `OnCalendar=daily`: Runs once a day.
- `Persistent=true`: Ensures the job runs if the machine was powered off during the scheduled time.
