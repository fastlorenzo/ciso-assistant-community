"""Risk Management module for CISO Assistant MCP Server"""

import json
from typing import Optional
from ..config import make_request, format_table


def register_risk_tools(mcp):
    """Register risk management tools with the MCP server"""

    @mcp.tool()
    async def get_risk_scenarios(folder_id: Optional[str] = None, format_as_table: bool = False):
        """Get risk scenarios from CISO Assistant Risk Registry

        Args:
            folder_id: Optional folder ID to filter results
            format_as_table: If True, return formatted table; if False, return raw JSON
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("risk-scenarios/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No risk scenarios found"

        if format_as_table:
            columns = ["name", "description", "current_level", "residual_level", "folder"]
            return format_table(result["results"], columns)

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_risk_assessments(folder_id: Optional[str] = None, format_as_table: bool = False):
        """Get risk assessments

        Args:
            folder_id: Optional folder ID to filter results
            format_as_table: If True, return formatted table; if False, return raw JSON
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("risk-assessments/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No risk assessments found"

        if format_as_table:
            columns = ["name", "description", "status", "eta", "folder"]
            return format_table(result["results"], columns)

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_threats(folder_id: Optional[str] = None):
        """Get threats catalog

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("threats/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No threats found"

        columns = ["name", "description", "category", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_risk_matrices(folder_id: Optional[str] = None):
        """Get risk matrices

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("risk-matrices/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No risk matrices found"

        columns = ["name", "description", "json_definition", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_risk_scenarios_by_level():
        """Get count of risk scenarios per risk level"""
        result = make_request("risk-scenarios/count_per_level/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_risk_scenarios_qualifications():
        """Get risk scenario qualifications (probability, impact levels)"""
        result = make_request("risk-scenarios/qualifications/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_risk_assessment_quality_check(assessment_id: str):
        """Get quality check results for a risk assessment

        Args:
            assessment_id: ID of the risk assessment
        """
        result = make_request(f"risk-assessments/{assessment_id}/quality_check/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_risk_assessments_status_choices():
        """Get available status choices for risk assessments"""
        result = make_request("risk-assessments/status/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_risk_scenarios_treatment_choices():
        """Get available treatment choices for risk scenarios"""
        result = make_request("risk-scenarios/treatment/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)
