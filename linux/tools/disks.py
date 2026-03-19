from linux.excutor import *


def register_tools(mcp):
    @mcp.tool()
    def disk_usage():
        """Show disk usage"""
        return run_cmd_list(["df", "-h"])

    @mcp.tool()
    def disk_mounts():
        """Show mounted filesystems"""
        return run_cmd_list(["mount"])

    @mcp.tool()
    def disk_iostat():
        """Show disk I/O statistics"""
        return run_cmd_list(["iostat", "-dx"])
