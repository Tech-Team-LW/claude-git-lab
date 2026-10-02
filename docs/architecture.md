# Architecture

The app is a Python package, `app/devops_portal/`. Each module has one job:

| Module | Job |
|---|---|
| `cli.py` | Parses arguments with `argparse`, calls the other modules and prints results |
| `storage.py` | Loads and saves the JSON data file |
| `team.py` | Adds, finds and removes team members, and builds a member's profile |
| `services.py` | Adds, finds and removes services, and checks a URL with `urllib` |
| `sysinfo.py` | Collects machine facts with `platform`, `socket`, `os` and `shutil` |
| `__main__.py` | Makes `python3 -m devops_portal` work |

## How a command runs

```
portal.sh team add Asha SRE
   └─ cli.main()
        ├─ storage.load()          read the JSON file into a dict
        ├─ team.add_member(data)   change the dict (raises ValueError on bad input)
        ├─ storage.save(data)      write the dict back
        └─ print a message, return exit code 0
```

## Design rules

- **Only `cli.py` prints or touches the disk.** `team.py` and `services.py` work
  on the data dictionary they're given, which keeps them easy to test.
- **Errors are `ValueError`s.** `cli.main()` catches them, prints
  `Error: ...` to stderr and returns exit code 1.
- **Standard library only.** Don't add third-party packages.

## Adding a new command

1. Put the logic in a module (an existing one or a new one), as plain functions.
2. Add a `cmd_<name>(args)` handler in `cli.py` that returns an exit code.
3. Register it in `build_parser()` with `set_defaults(func=cmd_<name>)`.
4. Add tests in `tests/`.
