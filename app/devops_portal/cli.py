"""Command-line interface: parses arguments and calls the other modules.

Every command handler takes the parsed arguments and returns an exit code
(0 = success, 1 = something failed).
"""

import argparse
import sys

from devops_portal import __version__, services, storage, sysinfo, team


def print_table(rows, headers):
    """Print rows (lists of strings) as a simple aligned table."""
    widths = [len(h) for h in headers]
    for row in rows:
        widths = [max(w, len(str(cell))) for w, cell in zip(widths, row)]

    def line(cells):
        return "  ".join(str(c).ljust(w) for c, w in zip(cells, widths)).rstrip()

    print(line(headers))
    print(line("-" * w for w in widths))
    for row in rows:
        print(line(row))


# ----- team commands -------------------------------------------------------

def cmd_team_list(args):
    data = storage.load()
    if not data["members"]:
        print("No team members yet. Add one with: team add NAME ROLE")
        return 0
    print_table([[m["name"], m["role"]] for m in data["members"]], ["NAME", "ROLE"])
    return 0


def cmd_team_add(args):
    data = storage.load()
    member = team.add_member(data, args.name, args.role, args.team)
    storage.save(data)
    print(f"Added {member['name']} ({member['role']}).")
    return 0


def cmd_team_profile(args):
    data = storage.load()
    profile = team.get_profile(data, args.name)
    print(f"Name: {profile['name']}")
    print(f"Role: {profile['role']}")
    print(f"Team: {profile['team'] or '(not set)'}")
    return 0


def cmd_team_remove(args):
    data = storage.load()
    member = team.remove_member(data, args.name)
    storage.save(data)
    print(f"Removed {member['name']}.")
    return 0


# ----- service commands ----------------------------------------------------

def cmd_service_list(args):
    data = storage.load()
    if not data["services"]:
        print("No services yet. Add one with: service add NAME URL")
        return 0
    print_table([[s["name"], s["url"]] for s in data["services"]], ["NAME", "URL"])
    return 0


def cmd_service_add(args):
    data = storage.load()
    service = services.add_service(data, args.name, args.url)
    storage.save(data)
    print(f"Added service {service['name']} -> {service['url']}.")
    return 0


def cmd_service_remove(args):
    data = storage.load()
    service = services.remove_service(data, args.name)
    storage.save(data)
    print(f"Removed service {service['name']}.")
    return 0


def cmd_service_check(args):
    data = storage.load()
    if args.name:
        service = services.find_service(data, args.name)
        if service is None:
            raise ValueError(f"No service named '{args.name}'.")
        to_check = [service]
    else:
        to_check = data["services"]

    if not to_check:
        print("No services to check. Add one with: service add NAME URL")
        return 0

    rows = []
    all_up = True
    for service in to_check:
        is_up, detail = services.check_url(service["url"], timeout=args.timeout)
        all_up = all_up and is_up
        rows.append([service["name"], "UP" if is_up else "DOWN", detail])
    print_table(rows, ["NAME", "STATUS", "DETAIL"])

    # Exit code 1 when anything is down, so scripts and cron jobs can react.
    return 0 if all_up else 1


# ----- sysinfo command -----------------------------------------------------

def cmd_sysinfo(args):
    for key, value in sysinfo.collect().items():
        print(f"{key + ':':<14} {value}")
    return 0


# ----- argument parsing ----------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="devops-portal",
        description="DevOps Team Portal: manage your team and services.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    # team
    team_parser = commands.add_parser("team", help="manage team members")
    team_cmds = team_parser.add_subparsers(dest="action", required=True, metavar="ACTION")

    p = team_cmds.add_parser("list", help="show all members")
    p.set_defaults(func=cmd_team_list)

    p = team_cmds.add_parser("add", help="add a member")
    p.add_argument("name")
    p.add_argument("role", help='for example "SRE" or "Platform Engineer"')
    p.add_argument("--team", help='the team they belong to, for example "Platform"')
    p.set_defaults(func=cmd_team_add)

    p = team_cmds.add_parser("profile", help="show a member's name, role and team")
    p.add_argument("name")
    p.set_defaults(func=cmd_team_profile)

    p = team_cmds.add_parser("remove", help="remove a member")
    p.add_argument("name")
    p.set_defaults(func=cmd_team_remove)

    # service
    service_parser = commands.add_parser("service", help="manage and check services")
    service_cmds = service_parser.add_subparsers(dest="action", required=True, metavar="ACTION")

    p = service_cmds.add_parser("list", help="show all services")
    p.set_defaults(func=cmd_service_list)

    p = service_cmds.add_parser("add", help="add a service")
    p.add_argument("name")
    p.add_argument("url", help="health URL, e.g. http://localhost:5000/health")
    p.set_defaults(func=cmd_service_add)

    p = service_cmds.add_parser("remove", help="remove a service")
    p.add_argument("name")
    p.set_defaults(func=cmd_service_remove)

    p = service_cmds.add_parser("check", help="check if services are up")
    p.add_argument("name", nargs="?", help="check only this service (default: all)")
    p.add_argument("--timeout", type=float, default=3, help="seconds to wait (default: 3)")
    p.set_defaults(func=cmd_service_check)

    # sysinfo
    p = commands.add_parser("sysinfo", help="show facts about this machine")
    p.set_defaults(func=cmd_sysinfo)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
