"""Manage the list of services and check whether they are up.

Like team.py, these functions change the data dictionary but don't save it.
"""

import urllib.error
import urllib.request


def find_service(data, name):
    """Return the service with this name (ignoring case), or None."""
    for service in data["services"]:
        if service["name"].lower() == name.lower():
            return service
    return None


def add_service(data, name, url):
    """Add a service. Raises ValueError for a bad name or URL."""
    name = name.strip()
    if not name:
        raise ValueError("Service name cannot be empty.")
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")
    if find_service(data, name):
        raise ValueError(f"Service '{name}' already exists.")

    service = {"name": name, "url": url}
    data["services"].append(service)
    return service


def remove_service(data, name):
    """Remove a service. Raises ValueError if there is no such service."""
    service = find_service(data, name)
    if service is None:
        raise ValueError(f"No service named '{name}'.")
    data["services"].remove(service)
    return service


def check_url(url, timeout=3):
    """Send a GET request to url.

    Returns a pair (is_up, detail). is_up is True for any 2xx or 3xx
    response. detail is a short message such as "HTTP 200".
    """
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return True, f"HTTP {response.status}"
    except urllib.error.HTTPError as err:
        # The server answered, but with an error code such as 404 or 500.
        return False, f"HTTP {err.code}"
    except urllib.error.URLError as err:
        # Could not connect: wrong host, nothing listening, DNS failure...
        return False, str(err.reason)
    except (TimeoutError, OSError) as err:
        return False, str(err) or type(err).__name__
