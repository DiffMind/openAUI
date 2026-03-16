from datetime import datetime
from zoneinfo import ZoneInfo
from linux.excutor import *


def register_tools(mcp):
    @mcp.tool()
    def disk_usage():
        """Show disk usage"""
        return run_cmd(["df", "-h"])

    @mcp.tool()
    def disk_mounts():
        """Show mounted filesystems"""
        return run_cmd(["mount"])
