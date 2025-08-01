"""EBIOS-RM module for CISO Assistant MCP Server"""

import json
from typing import Optional


def register_ebios_tools(mcp):
    """Register EBIOS-RM tools with the MCP server"""
    
    # Import here to avoid circular imports
    from ..config import make_request, format_table

    @mcp.tool()
    async def get_ebios_studies(folder_id: Optional[str] = None):
        """Get EBIOS-RM studies

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("ebios-rm/studies/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No EBIOS studies found"

        columns = ["name", "description", "status", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_ebios_stakeholders(folder_id: Optional[str] = None):
        """Get EBIOS-RM stakeholders

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("ebios-rm/stakeholders/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No EBIOS stakeholders found"

        columns = ["name", "description", "category", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_ebios_feared_events(folder_id: Optional[str] = None):
        """Get EBIOS-RM feared events

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("ebios-rm/feared-events/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No EBIOS feared events found"

        columns = ["name", "description", "gravity", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_ebios_ro_to(folder_id: Optional[str] = None):
        """Get EBIOS-RM risk origins (RO-TO)

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("ebios-rm/ro-to/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No EBIOS risk origins found"

        columns = ["name", "description", "motivation", "resources", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_ebios_strategic_scenarios(folder_id: Optional[str] = None):
        """Get EBIOS-RM strategic scenarios

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("ebios-rm/strategic-scenarios/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No EBIOS strategic scenarios found"

        columns = ["name", "description", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_ebios_operational_scenarios(folder_id: Optional[str] = None):
        """Get EBIOS-RM operational scenarios

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("ebios-rm/operational-scenarios/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No EBIOS operational scenarios found"

        columns = ["name", "description", "likelihood", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_ebios_attack_paths(folder_id: Optional[str] = None):
        """Get EBIOS-RM attack paths

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("ebios-rm/attack-paths/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No EBIOS attack paths found"

        columns = ["name", "description", "folder"]
        return format_table(result["results"], columns)
