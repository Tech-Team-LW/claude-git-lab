"""Collect basic facts about the machine the portal runs on."""

import os
import platform
import shutil
import socket

GIB = 1024 ** 3


def collect(disk_path="/"):
    """Return a dictionary of system facts, ready to print."""
    disk = shutil.disk_usage(disk_path)
    info = {
        "Hostname": socket.gethostname(),
        "OS": platform.platform(),
        "Python": platform.python_version(),
        "CPUs": os.cpu_count(),
        "Disk": (
            f"{disk.used / GIB:.1f} GiB used of {disk.total / GIB:.1f} GiB "
            f"({disk.used / disk.total:.0%}) on {disk_path}"
        ),
    }

    # getloadavg() only exists on Unix-like systems.
    if hasattr(os, "getloadavg"):
        one, five, fifteen = os.getloadavg()
        info["Load average"] = f"{one:.2f} {five:.2f} {fifteen:.2f}"

    return info
