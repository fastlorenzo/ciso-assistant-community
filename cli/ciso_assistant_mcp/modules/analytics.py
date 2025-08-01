"""Analytics and Utilities module for CISO Assistant MCP Server"""

import json
from typing import Optional
import requests


def register_analytics_tools(mcp):
    """Register analytics and utilities tools with the MCP server"""
    
    # Import here to avoid circular imports
    from ..config import make_request, format_table, API_URL

    @mcp.tool()
    async def get_compliance_summary(folder_id: Optional[str] = None):
        """Get compliance status summary

        Args:
            folder_id: Optional folder ID to filter results
        """
        # This combines multiple endpoints to provide a summary
        audits_params = {"folder": folder_id} if folder_id else {}
        controls_params = {"folder": folder_id} if folder_id else {}

        audits_result = make_request("compliance-assessments/", params=audits_params)
        controls_result = make_request("applied-controls/", params=controls_params)

        summary = {
            "total_audits": len(audits_result.get("results", [])),
            "total_controls": len(controls_result.get("results", [])),
            "controls_by_status": {},
            "audits_by_status": {},
        }

        # Count controls by status
        for control in controls_result.get("results", []):
            status = control.get("status", "unknown")
            summary["controls_by_status"][status] = (
                summary["controls_by_status"].get(status, 0) + 1
            )

        # Count audits by status
        for audit in audits_result.get("results", []):
            status = audit.get("status", "unknown")
            summary["audits_by_status"][status] = (
                summary["audits_by_status"].get(status, 0) + 1
            )

        return json.dumps(summary, indent=2)

    @mcp.tool()
    async def search_items(query: str, item_type: str = "all"):
        """Search across CISO Assistant items

        Args:
            query: Search term
            item_type: Type of items to search (controls, risks, audits, assets, all)
        """
        results = {}

        endpoints = {
            "controls": "applied-controls/",
            "risks": "risk-scenarios/",
            "audits": "compliance-assessments/",
            "assets": "assets/",
            "measures": "security-measures/",
        }

        search_endpoints = (
            endpoints if item_type == "all" else {item_type: endpoints.get(item_type)}
        )

        for name, endpoint in search_endpoints.items():
            if not endpoint:
                continue

            result = make_request(endpoint, params={"search": query})
            if "error" not in result and result.get("results"):
                results[name] = len(result["results"])

        if not results:
            return f"No items found matching '{query}'"

        summary = f"Search results for '{query}':\n"
        for item_type, count in results.items():
            summary += f"- {item_type}: {count} items found\n"

        return summary

    @mcp.tool()
    async def get_agg_data():
        """Get aggregated data for dashboards"""
        result = make_request("agg_data/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_composer_data():
        """Get composer data for visualizations"""
        result = make_request("composer_data/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_threats_count():
        """Get threats count data"""
        result = make_request("threats/threats_count/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_object_by_id(object_type: str, object_id: str):
        """Get detailed information for any object by its ID

        Args:
            object_type: Type of object (e.g., applied-controls, risk-scenarios, assets, etc.)
            object_id: ID of the object to retrieve
        """
        result = make_request(f"{object_type}/{object_id}/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_build_info():
        """Get system build information"""
        result = make_request("build/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_system_info():
        """Get CISO Assistant system information"""
        try:
            # Try to get version info or any system endpoint
            result = make_request("folders/")  # Use a basic endpoint to test connectivity
            if "error" in result:
                return f"Error connecting to CISO Assistant: {result['error']}"

            return f"✅ Connected to CISO Assistant at {API_URL}\n📊 System is operational"
        except requests.RequestException as e:
            return f"❌ Connection failed: {str(e)}"

    @mcp.tool()
    async def list_all_endpoints():
        """List all available MCP tools/endpoints organized by category"""
        tools_info = {
            "🔐 Risk Management": [
                "get_risk_scenarios - Get risk scenarios from Risk Registry",
                "get_risk_assessments - Get risk assessments",
                "get_threats - Get threats catalog",
                "get_risk_matrices - Get risk matrices",
                "get_risk_scenarios_by_level - Get count per risk level",
                "get_risk_scenarios_qualifications - Get qualifications",
            ],
            "📋 Compliance & Audits": [
                "get_applied_controls - Get applied controls/action plan",
                "get_audits_progress - Get compliance audits progress",
                "get_audit_detailed_status - Get detailed audit status",
                "get_audit_requirements - Get audit requirements",
                "get_requirements_assessments - Get requirement assessments",
                "get_frameworks - Get compliance frameworks",
                "get_compliance_assessment_donut_data - Get donut chart data",
                "get_compliance_assessment_progress_ts - Get progress time series",
                "get_compliance_assessment_tree - Get assessment tree",
                "get_compliance_assessment_quality_check - Get quality check",
            ],
            "🏢 Assets & Projects": [
                "get_assets - Get assets inventory",
                "get_asset_classes - Get asset classes/categories",
                "get_asset_class_tree - Get asset class hierarchy",
                "get_assets_graph - Get assets relationship graph",
                "get_projects - Get projects list",
                "get_folders - Get organizational folders",
            ],
            "📁 Evidence & Documents": [
                "get_evidences - Get evidence documents",
                "get_policies - Get policies and procedures",
            ],
            "🛡️ Security": [
                "get_security_measures - Get security measures/controls",
                "get_security_incidents - Get security incidents",
                "get_security_exceptions - Get security exceptions",
                "get_vulnerabilities - Get vulnerabilities",
                "get_findings - Get findings from assessments",
                "get_findings_assessments - Get findings assessments",
            ],
            "🏛️ Entities & Assessments": [
                "get_entities - Get entities (organizations, divisions)",
                "get_entity_assessments - Get entity assessments",
            ],
            "📊 EBIOS-RM (French Risk Method)": [
                "get_ebios_studies - Get EBIOS-RM studies",
                "get_ebios_stakeholders - Get EBIOS stakeholders",
                "get_ebios_feared_events - Get EBIOS feared events",
                "get_ebios_ro_to - Get EBIOS risk origins",
                "get_ebios_strategic_scenarios - Get EBIOS strategic scenarios",
                "get_ebios_operational_scenarios - Get EBIOS operational scenarios",
                "get_ebios_attack_paths - Get EBIOS attack paths",
            ],
            "👥 Users & Access": [
                "get_users - Get users list",
                "get_user_details - Get detailed user information",
                "get_user_groups - Get user groups",
                "get_user_group_members - Get group members",
                "get_admin_users - Get admin users",
                "get_roles - Get system roles",
                "get_role_assignments - Get role assignments",
                "get_user_preferences - Get user preferences",
            ],
            "📈 Analytics & Charts": [
                "get_agg_data - Get aggregated dashboard data",
                "get_composer_data - Get visualization data",
                "get_applied_controls_per_status - Get controls by status",
                "get_applied_controls_priority_chart - Get priority chart data",
                "get_applied_controls_gantt_data - Get Gantt chart data",
                "get_applied_controls_timeline_info - Get timeline info",
                "get_threats_count - Get threats count data",
                "get_compliance_summary - Get compliance summary",
                "search_items - Search across all items",
            ],
            "🔧 Utilities": [
                "get_object_by_id - Get any object by ID and type",
                "get_build_info - Get system build information",
                "get_system_info - Get system connectivity status",
                "list_all_endpoints - List all available tools (this tool)",
            ],
        }

        result = "# 📋 CISO Assistant MCP Tools Reference\n\n"
        result += f"**Total Tools Available**: {sum(len(tools) for tools in tools_info.values())}\n\n"

        for category, tools in tools_info.items():
            result += f"## {category}\n"
            for tool in tools:
                result += f"- `{tool}`\n"
            result += "\n"

        result += "---\n"
        result += "💡 **Tips**: \n"
        result += "- Most tools accept optional `folder_id` parameter for filtering\n"
        result += "- Use `get_folders` first to find folder IDs\n"
        result += "- Use `get_object_by_id` for detailed object information\n"
        result += "- Use `search_items` for cross-entity searching\n"

        return result
