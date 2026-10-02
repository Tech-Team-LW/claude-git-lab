# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

DevOps Team Portal: a command-line tool to keep a team roster, a list of services (with up/down checks) and show system info. Python 3.8+, **standard library only**. There is nothing to install and no third-party packages should be added. There is no linter or CI.

This repo (`day3/`) is separate from the Flask app described in the parent `../CLAUDE.md`. The Flask app only appears here as an example service to health-check (`http://localhost:5000/health`).

## Commands

Run from the repo root:

```bash
./scripts/run_tests.sh                     # all tests (unittest discover, verbose)
./scripts/run_tests.sh -k test_add_member  # tests matching a name pattern
./scripts/portal.sh --help                 # run the CLI
PORTAL_DATA=data/portal.json ./scripts/portal.sh team list   # use a scratch data file (data/ is gitignored)
```

Both scripts just set `PYTHONPATH=app`. Without them, run `cd app && python3 -m devops_portal ...`.

## Architecture

The package is in `app/devops_portal/`. A command flows like this: `cli.main()` parses the arguments with argparse, and the subcommand's `set_defaults(func=cmd_*)` handler then runs `storage.load()` → a logic function that changes the data dict → `storage.save(data)` → prints the result.

Design rules (from `docs/architecture.md`):
- **Only `cli.py` prints or does I/O.** `team.py` and `services.py` are pure functions over the data dict `{"members": [...], "services": [...]}`. Saving the dict is the caller's job.
- **Errors are `ValueError`.** `cli.main()` catches them, prints `Error: ...` to stderr and returns 1. Don't print errors or call `sys.exit` inside the logic modules.
- Name lookups (`find_member`, `find_service`) ignore case. Duplicate names are rejected.

Persistence: the data lives in one JSON file at `$PORTAL_DATA`, or `~/.devops-portal.json` by default. `storage.load()` returns empty data if the file is missing and fills in missing top-level keys. A new top-level key therefore has to be added to `storage.empty_data()` so that existing files keep loading.

Exit codes are part of the documented contract (`docs/usage.md`): 0 means success, 1 means an error **or** at least one service DOWN in `service check` (used by scripts and cron jobs), and 2 means wrong arguments (argparse). `services.check_url()` treats any 2xx or 3xx answer as UP.

## Adding a command

1. Write the logic as plain functions in a module that raise `ValueError` on bad input.
2. Add a `cmd_<name>(args)` handler in `cli.py` that returns an exit code.
3. Register it in `build_parser()` with `set_defaults(func=cmd_<name>)`.
4. Add tests and update `docs/usage.md`. Also update the module table in `docs/architecture.md` if you added a module.

## Tests

The tests use `unittest` and must not touch the network or the real data file. Follow the existing patterns:
- `tests/test_cli.py` sets `PORTAL_DATA` to a temp file with `mock.patch.dict`, and uses `run_cli(...)` to get `(code, stdout, stderr)`.
- Mock `devops_portal.services.check_url` when testing service checks through the CLI.
- `tests/test_services.py` runs a local `http.server` on port 0 for real `check_url` tests.
