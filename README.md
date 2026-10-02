# DevOps Team Portal

A small, beginner-friendly command-line tool for a DevOps team. With it you can:

- keep a **team roster** (who's on the team and their role)
- keep a list of **services** and check whether each one is up
- show **system info** about the current machine

It uses **only the Python standard library**, so there is nothing to `pip install`.

## Requirements

- Python 3.8 or newer (`python3 --version`)

## Quick start

```bash
cd day3
./scripts/portal.sh --help

./scripts/portal.sh team add Asha "SRE"
./scripts/portal.sh team list

./scripts/portal.sh service add flask-app http://localhost:5000/health
./scripts/portal.sh service check

./scripts/portal.sh sysinfo
```

You can also run it without the script:

```bash
cd app
python3 -m devops_portal team list
```

## Running the tests

```bash
./scripts/run_tests.sh
```

The tests use Python's built-in `unittest`. They write only to a temporary
file and don't need network access.

## Project layout

```
day3/
├── app/devops_portal/   the application (one module per job)
├── tests/               unit tests
├── scripts/             helper scripts to run the app and the tests
└── docs/                usage and design notes
```

See [docs/usage.md](docs/usage.md) for every command, and
[docs/architecture.md](docs/architecture.md) for how the code is organised.
