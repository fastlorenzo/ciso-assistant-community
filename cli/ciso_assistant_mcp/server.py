#!/usr/bin/env python3
"""
CISO Assistant MCP Server - Modular Version

This is a refactored, modular version of the CISO Assistant MCP server.
The original large file has been split into logical modules for better maintainability.
"""

from typing import Optional, List, Dict
import sys
import os

# Add the current directory to the path so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from mcp.server.fastmcp import FastMCP

# Import the configuration
from ciso_assistant_mcp.config import make_request, format_table, API_URL, TOKEN

# Import all module registration functions
from ciso_assistant_mcp.modules.risk_management import register_risk_tools
from ciso_assistant_mcp.modules.compliance import register_compliance_tools
from ciso_assistant_mcp.modules.assets import register_assets_tools
from ciso_assistant_mcp.modules.security import register_security_tools
from ciso_assistant_mcp.modules.ebios import register_ebios_tools
from ciso_assistant_mcp.modules.users import register_users_tools
from ciso_assistant_mcp.modules.analytics import register_analytics_tools

# Initialize FastMCP server
mcp = FastMCP("ciso-assistant")


def main():
    """Initialize and run the CISO Assistant MCP server"""
    
    # Check if required configuration is available
    if not API_URL or not TOKEN:
        print("Error: Missing required configuration. Please check your .mcp.env file.")
        print("Required variables: API_URL, TOKEN")
        sys.exit(1)
    
    print("Starting CISO Assistant MCP Server...")
    print(f"API URL: {API_URL}")
    print(f"Token configured: {'Yes' if TOKEN else 'No'}")
    
    # Register all tool modules
    print("Registering tool modules...")
    
    try:
        register_risk_tools(mcp)
        print("  Risk Management tools registered")
        
        register_compliance_tools(mcp)
        print("  Compliance & Audits tools registered")
        
        register_assets_tools(mcp)
        print("  Assets & Projects tools registered")
        
        register_security_tools(mcp)
        print("  Security tools registered")
        
        register_ebios_tools(mcp)
        print("  EBIOS-RM tools registered")
        
        register_users_tools(mcp)
        print("  Users & Access tools registered")
        
        register_analytics_tools(mcp)
        print("  Analytics & Utilities tools registered")
        
        print("All modules registered successfully!")
        
    except Exception as e:
        print(f"Error registering modules: {e}")
        sys.exit(1)
    
    # Additional utility tools that don't fit in other modules
    register_utility_tools()
    
    print("CISO Assistant MCP Server is ready!")
    print("Use 'list_all_endpoints' to see all available tools")
    
    # Run the server
    mcp.run(transport="stdio")


def register_utility_tools():
    """Register additional utility tools"""
    
    @mcp.tool()
    async def get_evidences(folder_id: Optional[str] = None):
        """Get evidence documents

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("evidences/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No evidences found"

        columns = ["name", "description", "attachment", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_policies(folder_id: Optional[str] = None):
        """Get policies and procedures

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("policies/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No policies found"

        columns = ["name", "description", "status", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_entities(folder_id: Optional[str] = None):
        """Get entities (organizations, divisions, etc.)

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("entities/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No entities found"

        columns = ["name", "description", "category", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_entity_assessments(folder_id: Optional[str] = None):
        """Get entity assessments

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("entity-assessments/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No entity assessments found"

        columns = ["name", "description", "status", "conclusion", "folder"]
        return format_table(result["results"], columns)


if __name__ == "__main__":
    main()
