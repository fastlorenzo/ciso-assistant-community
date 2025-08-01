"""Assets and Projects module for CISO Assistant MCP Server"""

import json
from typing import Optional

from ..config import make_request, format_table


def register_assets_tools(mcp):
    """Register assets and projects tools with the MCP server"""

    @mcp.tool()
    async def get_assets(folder_id: Optional[str] = None):
        """Get assets inventory

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("assets/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No assets found"

        columns = ["name", "description", "type", "criticality", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_projects(folder_id: Optional[str] = None):
        """Get projects list

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("projects/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No projects found"

        columns = ["name", "description", "status", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_folders():
        """Get organizational folders/domains"""
        result = make_request("folders/")

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No folders found"

        columns = ["name", "description", "parent_folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_asset_classes(folder_id: Optional[str] = None):
        """Get asset classes/categories

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("asset-class/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No asset classes found"

        columns = ["name", "description", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_asset_class_tree():
        """Get asset class hierarchy tree"""
        result = make_request("asset-class/tree/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_assets_graph():
        """Get assets relationship graph data"""
        result = make_request("assets/graph/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_assets_type_choices():
        """Get available type choices for assets"""
        result = make_request("assets/type/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_assets_csv_export():
        """Get assets data in CSV format"""
        result = make_request("assets/export_csv/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)
