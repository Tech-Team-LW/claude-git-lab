# Usage

Run commands with `./scripts/portal.sh <command>` from the `day3` folder.
Add `--help` to any command to see its options, for example
`./scripts/portal.sh service check --help`.

## Team

| Command | What it does |
|---|---|
| `team list` | Show all members |
| `team add NAME ROLE` | Add a member. Put a role that contains spaces in quotes: `"Platform Engineer"` |
| `team add NAME ROLE --team TEAM` | Add a member and record which team they belong to |
| `team profile NAME` | Show a member's name, role and team |
| `team remove NAME` | Remove a member |

Names are matched without regard to case, so `asha` and `Asha` are the same member.

Example:

```bash
./scripts/portal.sh team add Asha SRE --team Platform
./scripts/portal.sh team profile asha
Name: Asha
Role: SRE
Team: Platform
```

Members added without `--team` show `Team: (not set)`.

## Services

| Command | What it does |
|---|---|
| `service list` | Show all services |
| `service add NAME URL` | Add a service. The URL must start with `http://` or `https://` |
| `service remove NAME` | Remove a service |
| `service check [NAME]` | Send a GET request to each service (or only to NAME) and show UP or DOWN |
| `service check --timeout 5` | Wait up to 5 seconds per service (the default is 3) |

A service counts as **UP** when it answers with a 2xx or 3xx status. Any
error status, refused connection or timeout counts as **DOWN**.

Example with the Day 1 Flask app (running on port 5000):

```bash
./scripts/portal.sh service add flask-app http://localhost:5000/health
./scripts/portal.sh service check
```

## System info

`sysinfo` prints the hostname, OS, Python version, CPU count, disk usage of `/`
and the load average.

## Where data is stored

Members and services are saved in a JSON file:

- by default at `~/.devops-portal.json`
- or wherever the `PORTAL_DATA` environment variable points:

```bash
export PORTAL_DATA=data/portal.json   # data/ is already in .gitignore
```

The file is plain JSON, so you can open it in an editor if you need to.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success (for `service check`: every service is UP) |
| 1 | An error, such as a duplicate or unknown name, **or** at least one service is DOWN |
| 2 | Wrong arguments (reported by argparse) |

Because `service check` exits with 1 when anything is down, you can use it in
scripts or cron jobs:

```bash
./scripts/portal.sh service check || echo "Something is down!"
```
