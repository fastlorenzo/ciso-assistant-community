"""Compliance and Audits module for CISO Assistant MCP Server"""

import json
from typing import Optional

from ..config import make_request, format_table


def register_compliance_tools(mcp):
    """Register compliance and audit tools with the MCP server"""

    # Import here to avoid circular imports

    @mcp.tool()
    async def get_applied_controls(
        folder_id: Optional[str] = None,
        status: Optional[str] = None,
        format_as_table: bool = False,
    ):
        """Get applied controls from CISO Assistant action plan

        Args:
            folder_id: Optional folder ID to filter results
            status: Optional status filter (to_do, in_progress, active,
                deprecated)
            format_as_table: If True, return formatted table; if False, return
                raw JSON
        """
        params = {}
        if folder_id:
            params["folder"] = folder_id
        if status:
            params["status"] = status

        result = make_request("applied-controls/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No applied controls found"

        if format_as_table:
            columns = ["name", "description", "status", "eta", "folder"]
            return format_table(result["results"], columns)

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_audits_progress(folder_id: Optional[str] = None):
        """Get compliance audits progress

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("compliance-assessments/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No audits found"

        columns = ["name", "framework", "status", "progress", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_audit_detailed_status(
        audit_id: Optional[str] = None, audit_name: Optional[str] = None
    ):
        """Get detailed status of audit requirements and controls

        Args:
            audit_id: Optional audit ID
            audit_name: Optional audit name to search for
        """
        # First get the audit ID if name is provided
        if audit_name and not audit_id:
            audits_result = make_request("compliance-assessments/")
            if "error" in audits_result:
                return f"Error: {audits_result['error']}"

            audit_found = None
            for audit in audits_result.get("results", []):
                if audit_name.lower() in audit.get("name", "").lower():
                    audit_found = audit
                    audit_id = audit.get("id")
                    break

            if not audit_found:
                return f"No audit found with name containing '{audit_name}'"

        if not audit_id:
            # Return summary of all audits
            audits_result = make_request("compliance-assessments/")
            if "error" in audits_result:
                return f"Error: {audits_result['error']}"

            result_text = "## 📊 All Audits Detailed Status\n\n"
            for audit in audits_result.get("results", []):
                result_text += await _get_single_audit_details(audit.get("id"))
                result_text += "\n" + "=" * 50 + "\n\n"

            return result_text.strip()
        else:
            # Get specific audit details
            return await _get_single_audit_details(audit_id)

    async def _get_single_audit_details(audit_id: str) -> str:
        """Helper function to get detailed status of a single audit"""

        # Get audit basic info
        audit_result = make_request(f"compliance-assessments/{audit_id}/")
        if "error" in audit_result:
            return f"Error getting audit details: {audit_result['error']}"

        audit_info = audit_result
        result_text = f"## 🔍 {audit_info.get('name', 'Unknown Audit')}\n"
        framework_str = audit_info.get("framework", {}).get("str", "N/A")
        result_text += f"**Framework:** {framework_str}\n"
        result_text += f"**Status:** {audit_info.get('status', 'N/A')}\n"
        result_text += f"**Progress:** {audit_info.get('progress', 0)}%\n"
        description = audit_info.get("description", "N/A")
        result_text += f"**Description:** {description}\n\n"

        # Get requirement assessments for this audit
        req_params = {"compliance_assessment": audit_id}
        req_result = make_request(
            "requirement-assessments/",
            params=req_params,
        )

        if "error" not in req_result and req_result.get("results"):
            result_text += "### 📋 Requirements Status:\n\n"

            status_counts = {}
            for req in req_result["results"]:
                status = req.get("status", "unknown")
                score = req.get("score", 0)
                status_counts[status] = status_counts.get(status, 0) + 1

                # Show individual requirements
                req_name = req.get("name", "Unknown Requirement")
                result_text += f"**{req_name}**\n"
                result_text += f"- Status: {status}\n"
                result_text += f"- Score: {score}\n"
                if req.get("comment"):
                    result_text += f"- Comment: {req.get('comment')}\n"
                result_text += "\n"

            # Summary by status
            result_text += "### 📊 Requirements Summary:\n"
            total_reqs = len(req_result["results"])
            for status, count in status_counts.items():
                percentage = (count / total_reqs * 100) if total_reqs > 0 else 0
                result_text += f"- **{status}**: {count} ({percentage:.1f}%)\n"
            result_text += f"- **Total Requirements**: {total_reqs}\n\n"
        else:
            result_text += "### ❌ No requirement details found\n\n"

        # Try to get related applied controls
        controls_result = make_request(
            "applied-controls/", params={"compliance_assessment": audit_id}
        )
        if "error" not in controls_result and controls_result.get("results"):
            result_text += "### 🛡️ Related Controls:\n\n"

            control_status_counts = {}
            for control in controls_result["results"]:
                status = control.get("status", "unknown")
                control_status_counts[status] = control_status_counts.get(status, 0) + 1

                control_name = control.get("name", "Unknown Control")
                result_text += f"**{control_name}**\n"
                result_text += f"- Status: {status}\n"
                if control.get("eta"):
                    result_text += f"- ETA: {control.get('eta')}\n"
                if control.get("description"):
                    description = control.get("description")
                    result_text += f"- Description: {description}\n"
                result_text += "\n"

            # Controls summary
            result_text += "### 📊 Controls Summary:\n"
            total_controls = len(controls_result["results"])
            for status, count in control_status_counts.items():
                percentage = (count / total_controls * 100) if total_controls > 0 else 0
                result_text += f"- **{status}**: {count} ({percentage:.1f}%)\n"
            result_text += f"- **Total Controls**: {total_controls}\n\n"

        return result_text

    @mcp.tool()
    async def get_audit_requirements(audit_name: str):
        """Get all requirements for a specific audit with their status

        Args:
            audit_name: Name of the audit to get requirements for
        """
        # Find the audit first
        audits_result = make_request("compliance-assessments/")
        if "error" in audits_result:
            return f"Error: {audits_result['error']}"

        audit_found = None
        for audit in audits_result.get("results", []):
            if audit_name.lower() in audit.get("name", "").lower():
                audit_found = audit
                break

        if not audit_found:
            return f"No audit found with name containing '{audit_name}'"

        # Get requirements for this audit
        req_params = {"compliance_assessment": audit_found.get("id")}
        req_result = make_request("requirement-assessments/", params=req_params)

        if "error" in req_result:
            return f"Error: {req_result['error']}"

        if not req_result.get("results"):
            audit_name = audit_found.get("name")
            return f"No requirements found for audit '{audit_name}'"

        columns = ["name", "status", "score", "comment", "evidence"]
        return format_table(req_result["results"], columns)

    @mcp.tool()
    async def get_requirements_assessments(folder_id: Optional[str] = None):
        """Get requirements assessments details

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("requirement-assessments/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No requirement assessments found"

        columns = ["name", "description", "status", "score", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_frameworks():
        """Get available compliance frameworks"""
        result = make_request("frameworks/")

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No frameworks found"

        columns = ["name", "description", "version", "provider"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_compliance_assessment_donut_data(assessment_id: str):
        """Get donut chart data for a compliance assessment

        Args:
            assessment_id: ID of the compliance assessment
        """
        endpoint = f"compliance-assessments/{assessment_id}/donut_data/"
        result = make_request(endpoint)

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_compliance_assessment_progress_ts(assessment_id: str):
        """Get progress time series data for a compliance assessment

        Args:
            assessment_id: ID of the compliance assessment
        """
        endpoint = f"compliance-assessments/{assessment_id}/progress_ts/"
        result = make_request(endpoint)

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_compliance_assessment_tree(assessment_id: str):
        """Get tree structure for a compliance assessment

        Args:
            assessment_id: ID of the compliance assessment
        """
        result = make_request(f"compliance-assessments/{assessment_id}/tree/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_compliance_assessment_quality_check(assessment_id: str):
        """Get quality check results for a compliance assessment

        Args:
            assessment_id: ID of the compliance assessment
        """
        endpoint = f"compliance-assessments/{assessment_id}/quality_check/"
        result = make_request(endpoint)

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_compliance_assessments_status_choices():
        """Get available status choices for compliance assessments"""
        result = make_request("compliance-assessments/status/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_applied_controls_status_choices():
        """Get available status choices for applied controls"""
        result = make_request("applied-controls/status/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_applied_controls_priority_choices():
        """Get available priority choices for applied controls"""
        result = make_request("applied-controls/priority/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_applied_controls_effort_choices():
        """Get available effort choices for applied controls"""
        result = make_request("applied-controls/effort/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_applied_controls_per_status():
        """Get applied controls grouped by status"""
        result = make_request("applied-controls/per_status/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_applied_controls_priority_chart():
        """Get applied controls priority chart data"""
        result = make_request("applied-controls/priority_chart_data/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_applied_controls_gantt_data():
        """Get applied controls Gantt chart data"""
        result = make_request("applied-controls/get_gantt_data/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_applied_controls_timeline_info():
        """Get applied controls timeline information"""
        result = make_request("applied-controls/get_timeline_info/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_applied_controls_csv_export():
        """Get applied controls data in CSV format"""
        result = make_request("applied-controls/export_csv/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)
