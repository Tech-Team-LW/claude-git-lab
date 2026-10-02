"""Manage the team roster.

Each function takes the portal data dictionary and changes or reads
data["members"]. Saving to disk is the caller's job (see cli.py).
"""


def find_member(data, name):
    """Return the member with this name (ignoring case), or None."""
    for member in data["members"]:
        if member["name"].lower() == name.lower():
            return member
    return None


def add_member(data, name, role):
    """Add a member. Raises ValueError if the name is empty or taken."""
    name = name.strip()
    if not name:
        raise ValueError("Member name cannot be empty.")
    if find_member(data, name):
        raise ValueError(f"Member '{name}' already exists.")

    member = {"name": name, "role": role.strip()}
    data["members"].append(member)
    return member


def remove_member(data, name):
    """Remove a member. Raises ValueError if there is no such member."""
    member = find_member(data, name)
    if member is None:
        raise ValueError(f"No member named '{name}'.")
    data["members"].remove(member)
    return member
