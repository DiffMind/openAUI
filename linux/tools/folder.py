from linux.excutor import *


def register_tools(mcp):

    # -----------------------------
    # ????
    # -----------------------------
    @mcp.tool()
    def folder_list(path: str = "."):
        """List folder contents"""
        return run_cmd_list(["ls", "-al", path])

    @mcp.tool()
    def folder_size(path: str = "."):
        """Show folder size"""
        return run_cmd_list(["du", "-sh", path])

    @mcp.tool()
    def folder_tree(path: str = ".", depth: int = 2):
        """Show folder tree structure"""
        return run_cmd_list(["tree", "-L", str(depth), path])

    @mcp.tool()
    def folder_stat(path: str = "."):
        """Show folder metadata and permissions"""
        return run_cmd_list(["stat", path])

    @mcp.tool()
    def folder_inode(path: str = "."):
        """Show folder inode info"""
        return run_cmd_list(["ls", "-id", path])

    # -----------------------------
    # ?? / ??
    # -----------------------------
    @mcp.tool()
    def folder_big_files(path: str = ".", limit: int = 20):
        """Find largest files in folder"""
        cmd = f"find {path} -type f -printf '%s %p\n' | sort -nr | head -n {limit}"
        return run_cmd_list(["bash", "-lc", cmd])

    @mcp.tool()
    def folder_recent_files(path: str = ".", limit: int = 20):
        """Find recently modified files"""
        cmd = f"ls -lt {path} | head -n {limit}"
        return run_cmd_list(["bash", "-lc", cmd])

    @mcp.tool()
    def folder_empty(path: str = "."):
        """Find empty folders"""
        return run_cmd_list(["find", path, "-type", "d", "-empty"])

    @mcp.tool()
    def folder_find_ext(path: str = ".", ext: str = "py"):
        """Find files by extension"""
        return run_cmd_list(["find", path, "-type", "f", "-name", f"*.{ext}"])

    # -----------------------------
    # ??
    # -----------------------------
    @mcp.tool()
    def folder_count(path: str = "."):
        """Count files and folders"""
        cmd = (
            f"echo 'Files:'; find {path} -type f | wc -l; "
            f"echo 'Folders:'; find {path} -type d | wc -l"
        )
        return run_cmd_list(["bash", "-lc", cmd])

    @mcp.tool()
    def folder_filetypes(path: str = "."):
        """Count file types by extension"""
        cmd = f"find {path} -type f | sed 's/.*\\.//' | sort | uniq -c | sort -nr"
        return run_cmd_list(["bash", "-lc", cmd])

    @mcp.tool()
    def folder_du_detail(path: str = ".", depth: int = 2):
        """Show folder size breakdown"""
        return run_cmd_list(["du", "-h", f"--max-depth={depth}", path])

    # -----------------------------
    # ???
    # -----------------------------
    @mcp.tool()
    def folder_create(path: str):
        """Create a folder"""
        return run_cmd_list(["mkdir", "-p", path])

    @mcp.tool()
    def folder_delete(path: str):
        """Delete a folder recursively"""
        return run_cmd_list(["rm", "-rf", path])

    @mcp.tool()
    def folder_move(src: str, dst: str):
        """Move folder"""
        return run_cmd_list(["mv", src, dst])

    @mcp.tool()
    def folder_copy(src: str, dst: str):
        """Copy folder recursively"""
        return run_cmd_list(["cp", "-r", src, dst])
