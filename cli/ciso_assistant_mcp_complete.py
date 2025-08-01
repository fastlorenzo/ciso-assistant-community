#!/usr/bin/env python3

from typing import Optional, List, Dict
import json
import os

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from .mcp.env file
load_dotenv(".mcp.env")

# Initialize FastMCP server
mcp = FastMCP("ciso-assistant")

cli_cfg = dict()
auth_data = dict()
GLOBAL_FOLDER_ID = None

# Read configuration from environment variables
API_URL = os.getenv("API_URL", "")
TOKEN = os.getenv("TOKEN", "")
VERIFY_CERTIFICATE = os.getenv("VERIFY_CERTIFICATE", "true").lower() in (
    "true",
    "1",
    "yes",
    "on",
)


def make_request(
    endpoint: str, method: str = "GET", params: Optional[dict] = None, data: Optional[dict] = None
) -> dict:
    """Make authenticated request to CISO Assistant API"""
    headers = {"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"}

    url = f"{API_URL}/{endpoint.lstrip('/')}"

    try:
        if method.upper() == "GET":
            response = requests.get(
                url, headers=headers, params=params, verify=VERIFY_CERTIFICATE, timeout=30
            )
        elif method.upper() == "POST":
            response = requests.post(
                url, headers=headers, json=data, verify=VERIFY_CERTIFICATE, timeout=30
            )
        elif method.upper() == "PUT":
            response = requests.put(
                url, headers=headers, json=data, verify=VERIFY_CERTIFICATE, timeout=30
            )
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, verify=VERIFY_CERTIFICATE, timeout=30)
        else:
            return {"error": f"Unsupported HTTP method: {method}"}

        if response.status_code not in [200, 201, 204]:
            return {"error": f"HTTP {response.status_code}: {response.text}"}

        return response.json() if response.content else {"success": True}

    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}


def format_table(data: List[Dict], columns: List[str]) -> str:
    """Format data as markdown table"""
    if not data:
        return "No data found"

    # Header
    header = "|" + "|".join(columns) + "|"
    separator = "|" + "|".join(["---"] * len(columns)) + "|"

    # Rows
    rows = []
    for item in data:
        row_data = []
        for col in columns:
            value = item.get(col, "")
            if isinstance(value, dict):
                if "str" in value:
                    value = value["str"]
                elif "name" in value:
                    value = value["name"]
                else:
                    value = str(value)
            elif value is None:
                value = ""
            else:
                value = str(value)
            row_data.append(value)
        rows.append("|" + "|".join(row_data) + "|")

    return "\n".join([header, separator] + rows)


# =====================
# RISK MANAGEMENT
# =====================


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


# =====================
# COMPLIANCE & AUDITS
# =====================


@mcp.tool()
async def get_applied_controls(
    folder_id: Optional[str] = None, status: Optional[str] = None, format_as_table: bool = False
):
    """Get applied controls from CISO Assistant action plan

    Args:
        folder_id: Optional folder ID to filter results
        status: Optional status filter (to_do, in_progress, active, deprecated)
        format_as_table: If True, return formatted table; if False, return raw JSON
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
    result_text += (
        f"**Framework:** {audit_info.get('framework', {}).get('str', 'N/A')}\n"
    )
    result_text += f"**Status:** {audit_info.get('status', 'N/A')}\n"
    result_text += f"**Progress:** {audit_info.get('progress', 0)}%\n"
    result_text += f"**Description:** {audit_info.get('description', 'N/A')}\n\n"

    # Get requirement assessments for this audit
    req_params = {"compliance_assessment": audit_id}
    req_result = make_request("requirement-assessments/", params=req_params)

    if "error" not in req_result and req_result.get("results"):
        result_text += "### 📋 Requirements Status:\n\n"

        status_counts = {}
        for req in req_result["results"]:
            status = req.get("status", "unknown")
            score = req.get("score", 0)
            status_counts[status] = status_counts.get(status, 0) + 1

            # Show individual requirements
            result_text += f"**{req.get('name', 'Unknown Requirement')}**\n"
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

            result_text += f"**{control.get('name', 'Unknown Control')}**\n"
            result_text += f"- Status: {status}\n"
            if control.get("eta"):
                result_text += f"- ETA: {control.get('eta')}\n"
            if control.get("description"):
                result_text += f"- Description: {control.get('description')}\n"
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
        return f"No requirements found for audit '{audit_found.get('name')}'"

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


# =====================
# ASSETS & PROJECTS
# =====================


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


# =====================
# EVIDENCE & DOCUMENTS
# =====================


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


# =====================
# SECURITY MEASURES
# =====================


@mcp.tool()
async def get_security_measures(folder_id: Optional[str] = None):
    """Get security measures/controls

    Args:
        folder_id: Optional folder ID to filter results
    """
    params = {"folder": folder_id} if folder_id else {}
    result = make_request("security-measures/", params=params)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No security measures found"

    columns = ["name", "description", "type", "status", "folder"]
    return format_table(result["results"], columns)


# =====================
# INCIDENTS & EVENTS
# =====================


@mcp.tool()
async def get_security_incidents(folder_id: Optional[str] = None):
    """Get security incidents

    Args:
        folder_id: Optional folder ID to filter results
    """
    params = {"folder": folder_id} if folder_id else {}
    result = make_request("security-incidents/", params=params)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No security incidents found"

    columns = ["name", "description", "severity", "status", "folder"]
    return format_table(result["results"], columns)


# =====================
# USERS & ROLES
# =====================


@mcp.tool()
async def get_users():
    """Get users list"""
    result = make_request("users/")

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No users found"

    columns = ["email", "first_name", "last_name", "is_active"]
    return format_table(result["results"], columns)


@mcp.tool()
async def get_user_details(user_id: Optional[str] = None):
    """Get detailed user information including group memberships

    Args:
        user_id: Optional user ID, if not provided returns all users with details
    """
    if user_id:
        result = make_request(f"users/{user_id}/")
        if "error" in result:
            return f"Error: {result['error']}"
        return json.dumps(result, indent=2)
    else:
        # Get all users with detailed info
        users_result = make_request("users/")
        if "error" in users_result:
            return f"Error: {users_result['error']}"

        detailed_users = []
        for user in users_result.get("results", []):
            user_detail = make_request(f"users/{user.get('id')}/")
            if "error" not in user_detail:
                detailed_users.append(user_detail)

        return json.dumps(detailed_users, indent=2)


@mcp.tool()
async def get_user_groups():
    """Get user groups"""
    result = make_request("user-groups/")

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No user groups found"

    columns = ["name", "description"]
    return format_table(result["results"], columns)


@mcp.tool()
async def get_user_group_members(group_name: Optional[str] = None):
    """Get members of user groups

    Args:
        group_name: Optional group name to filter, if not provided returns all groups with members
    """
    groups_result = make_request("user-groups/")
    if "error" in groups_result:
        return f"Error: {groups_result['error']}"

    groups_info = []
    for group in groups_result.get("results", []):
        if group_name and group.get("name") != group_name:
            continue

        # Try to get group details with members
        group_detail = make_request(f"user-groups/{group.get('id')}/")
        if "error" not in group_detail:
            groups_info.append(
                {
                    "group_name": group_detail.get("name"),
                    "description": group_detail.get("description", ""),
                    "members": group_detail.get("users", []),
                    "member_count": len(group_detail.get("users", [])),
                }
            )

    if not groups_info:
        return f"No group information found{' for ' + group_name if group_name else ''}"

    result_text = ""
    for group in groups_info:
        result_text += f"\n## 👥 {group['group_name']}\n"
        if group["description"]:
            result_text += f"**Description:** {group['description']}\n"
        result_text += f"**Members ({group['member_count']}):**\n"

        if group["members"]:
            for member in group["members"]:
                if isinstance(member, dict):
                    name = f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
                    email = member.get("email", "")
                    result_text += f"- {name} ({email})\n"
                else:
                    result_text += f"- {member}\n"
        else:
            result_text += "- No members found\n"
        result_text += "\n"

    return result_text.strip()


@mcp.tool()
async def get_admin_users():
    """Get users with administrative privileges"""
    return await get_user_group_members("Global - Administrator")


# =====================
# ANALYTICS & REPORTS
# =====================


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


# =====================
# ADDITIONAL ENTITIES & ASSESSMENTS
# =====================


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


@mcp.tool()
async def get_findings(folder_id: Optional[str] = None):
    """Get findings from assessments

    Args:
        folder_id: Optional folder ID to filter results
    """
    params = {"folder": folder_id} if folder_id else {}
    result = make_request("findings/", params=params)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No findings found"

    columns = ["name", "description", "severity", "status", "folder"]
    return format_table(result["results"], columns)


@mcp.tool()
async def get_findings_assessments(folder_id: Optional[str] = None):
    """Get findings assessments

    Args:
        folder_id: Optional folder ID to filter results
    """
    params = {"folder": folder_id} if folder_id else {}
    result = make_request("findings-assessments/", params=params)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No findings assessments found"

    columns = ["name", "description", "status", "category", "folder"]
    return format_table(result["results"], columns)


@mcp.tool()
async def get_vulnerabilities(folder_id: Optional[str] = None):
    """Get vulnerabilities

    Args:
        folder_id: Optional folder ID to filter results
    """
    params = {"folder": folder_id} if folder_id else {}
    result = make_request("vulnerabilities/", params=params)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No vulnerabilities found"

    columns = ["name", "description", "severity", "status", "folder"]
    return format_table(result["results"], columns)


# =====================
# RISK MATRICES & ADVANCED RISK
# =====================


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


# =====================
# ASSET CLASSES & EXTENDED ASSETS
# =====================


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


# =====================
# EBIOS-RM (Risk Management Method)
# =====================


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


# =====================
# ROLES & PERMISSIONS
# =====================


@mcp.tool()
async def get_roles():
    """Get system roles"""
    result = make_request("roles/")

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No roles found"

    columns = ["name", "description", "permissions"]
    return format_table(result["results"], columns)


@mcp.tool()
async def get_role_assignments(folder_id: Optional[str] = None):
    """Get role assignments

    Args:
        folder_id: Optional folder ID to filter results
    """
    params = {"folder": folder_id} if folder_id else {}
    result = make_request("role-assignments/", params=params)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No role assignments found"

    columns = ["user", "role", "folder", "is_recursive"]
    return format_table(result["results"], columns)


# =====================
# SOLUTIONS & LIBRARIES
# =====================


@mcp.tool()
async def get_solutions(folder_id: Optional[str] = None):
    """Get solutions

    Args:
        folder_id: Optional folder ID to filter results
    """
    params = {"folder": folder_id} if folder_id else {}
    result = make_request("solutions/", params=params)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No solutions found"

    columns = ["name", "description", "folder"]
    return format_table(result["results"], columns)


@mcp.tool()
async def get_stored_libraries():
    """Get stored libraries (frameworks, threat catalogs, etc.)"""
    result = make_request("stored-libraries/")

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No stored libraries found"

    columns = ["name", "description", "locale", "provider", "object_type"]
    return format_table(result["results"], columns)


# =====================
# SECURITY EXCEPTIONS
# =====================


@mcp.tool()
async def get_security_exceptions(folder_id: Optional[str] = None):
    """Get security exceptions

    Args:
        folder_id: Optional folder ID to filter results
    """
    params = {"folder": folder_id} if folder_id else {}
    result = make_request("security-exceptions/", params=params)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No security exceptions found"

    columns = ["name", "description", "severity", "status", "folder"]
    return format_table(result["results"], columns)


# =====================
# FILTERING & LABELS
# =====================


@mcp.tool()
async def get_filtering_labels(folder_id: Optional[str] = None):
    """Get filtering labels

    Args:
        folder_id: Optional folder ID to filter results
    """
    params = {"folder": folder_id} if folder_id else {}
    result = make_request("filtering-labels/", params=params)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No filtering labels found"

    columns = ["name", "description", "color", "folder"]
    return format_table(result["results"], columns)


# =====================
# TASKS & TIMELINE
# =====================


@mcp.tool()
async def get_task_templates(folder_id: Optional[str] = None):
    """Get task templates

    Args:
        folder_id: Optional folder ID to filter results
    """
    params = {"folder": folder_id} if folder_id else {}
    result = make_request("task-templates/", params=params)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No task templates found"

    columns = ["name", "description", "status", "folder"]
    return format_table(result["results"], columns)


@mcp.tool()
async def get_task_nodes(folder_id: Optional[str] = None):
    """Get task nodes

    Args:
        folder_id: Optional folder ID to filter results
    """
    params = {"folder": folder_id} if folder_id else {}
    result = make_request("task-nodes/", params=params)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No task nodes found"

    columns = ["name", "description", "status", "folder"]
    return format_table(result["results"], columns)


@mcp.tool()
async def get_timeline_entries(folder_id: Optional[str] = None):
    """Get timeline entries

    Args:
        folder_id: Optional folder ID to filter results
    """
    params = {"folder": folder_id} if folder_id else {}
    result = make_request("timeline-entries/", params=params)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No timeline entries found"

    columns = ["name", "description", "entry_type", "folder"]
    return format_table(result["results"], columns)


# =====================
# SETTINGS & CONFIGURATION
# =====================


@mcp.tool()
async def get_client_settings():
    """Get client settings"""
    result = make_request("client-settings/")

    if "error" in result:
        return f"Error: {result['error']}"

    if not result.get("results"):
        return "No client settings found"

    return json.dumps(result, indent=2)


@mcp.tool()
async def get_global_settings():
    """Get global settings"""
    result = make_request("settings/global/")

    if "error" in result:
        return f"Error: {result['error']}"

    return json.dumps(result, indent=2)


@mcp.tool()
async def get_general_settings():
    """Get general settings"""
    result = make_request("settings/general/")

    if "error" in result:
        return f"Error: {result['error']}"

    return json.dumps(result, indent=2)


@mcp.tool()
async def get_sso_settings():
    """Get SSO settings"""
    result = make_request("settings/sso/")

    if "error" in result:
        return f"Error: {result['error']}"

    return json.dumps(result, indent=2)


@mcp.tool()
async def get_feature_flags():
    """Get feature flags"""
    result = make_request("settings/feature-flags/")

    if "error" in result:
        return f"Error: {result['error']}"

    return json.dumps(result, indent=2)


# =====================
# ANALYTICS DATA ENDPOINTS
# =====================


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
async def get_build_info():
    """Get system build information"""
    result = make_request("build/")

    if "error" in result:
        return f"Error: {result['error']}"

    return json.dumps(result, indent=2)


# =====================
# USER PREFERENCES
# =====================


@mcp.tool()
async def get_user_preferences():
    """Get current user preferences"""
    result = make_request("user-preferences/")

    if "error" in result:
        return f"Error: {result['error']}"

    return json.dumps(result, indent=2)


# =====================
# SPECIALIZED METRICS AND CHARTS
# =====================


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
async def get_threats_count():
    """Get threats count data"""
    result = make_request("threats/threats_count/")

    if "error" in result:
        return f"Error: {result['error']}"

    return json.dumps(result, indent=2)


# =====================
# DETAILED OBJECT RETRIEVAL BY ID
# =====================


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
async def get_compliance_assessment_donut_data(assessment_id: str):
    """Get donut chart data for a compliance assessment

    Args:
        assessment_id: ID of the compliance assessment
    """
    result = make_request(f"compliance-assessments/{assessment_id}/donut_data/")

    if "error" in result:
        return f"Error: {result['error']}"

    return json.dumps(result, indent=2)


@mcp.tool()
async def get_compliance_assessment_progress_ts(assessment_id: str):
    """Get progress time series data for a compliance assessment

    Args:
        assessment_id: ID of the compliance assessment
    """
    result = make_request(f"compliance-assessments/{assessment_id}/progress_ts/")

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
    result = make_request(f"compliance-assessments/{assessment_id}/quality_check/")

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


# =====================
# ENUMERATION ENDPOINTS (Choice Lists)
# =====================


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
async def get_compliance_assessments_status_choices():
    """Get available status choices for compliance assessments"""
    result = make_request("compliance-assessments/status/")

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


@mcp.tool()
async def get_assets_type_choices():
    """Get available type choices for assets"""
    result = make_request("assets/type/")

    if "error" in result:
        return f"Error: {result['error']}"

    return json.dumps(result, indent=2)


@mcp.tool()
async def get_findings_severity_choices():
    """Get available severity choices for findings"""
    result = make_request("findings/severity/")

    if "error" in result:
        return f"Error: {result['error']}"

    return json.dumps(result, indent=2)


@mcp.tool()
async def get_findings_status_choices():
    """Get available status choices for findings"""
    result = make_request("findings/status/")

    if "error" in result:
        return f"Error: {result['error']}"

    return json.dumps(result, indent=2)


@mcp.tool()
async def get_vulnerabilities_severity_choices():
    """Get available severity choices for vulnerabilities"""
    result = make_request("vulnerabilities/severity/")

    if "error" in result:
        return f"Error: {result['error']}"

    return json.dumps(result, indent=2)


@mcp.tool()
async def get_vulnerabilities_status_choices():
    """Get available status choices for vulnerabilities"""
    result = make_request("vulnerabilities/status/")

    if "error" in result:
        return f"Error: {result['error']}"

    return json.dumps(result, indent=2)


# =====================
# SPECIALIZED DATA EXPORTS
# =====================


@mcp.tool()
async def get_applied_controls_csv_export():
    """Get applied controls data in CSV format"""
    result = make_request("applied-controls/export_csv/")

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


# =====================
# SYSTEM INFO & HELP
# =====================


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
        "🏷️ Organization & Labels": [
            "get_filtering_labels - Get filtering labels",
            "get_solutions - Get solutions",
            "get_stored_libraries - Get stored libraries",
        ],
        "📅 Tasks & Timeline": [
            "get_task_templates - Get task templates",
            "get_task_nodes - Get task nodes",
            "get_timeline_entries - Get timeline entries",
        ],
        "⚙️ Settings & Configuration": [
            "get_client_settings - Get client settings",
            "get_global_settings - Get global settings",
            "get_general_settings - Get general settings",
            "get_sso_settings - Get SSO settings",
            "get_feature_flags - Get feature flags",
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
        "📝 Choice Lists & Enums": [
            "get_applied_controls_status_choices - Status options",
            "get_applied_controls_priority_choices - Priority options",
            "get_applied_controls_effort_choices - Effort options",
            "get_compliance_assessments_status_choices - Assessment status options",
            "get_risk_assessments_status_choices - Risk assessment status options",
            "get_risk_scenarios_treatment_choices - Treatment options",
            "get_assets_type_choices - Asset type options",
            "get_findings_severity_choices - Finding severity options",
            "get_findings_status_choices - Finding status options",
            "get_vulnerabilities_severity_choices - Vulnerability severity options",
            "get_vulnerabilities_status_choices - Vulnerability status options",
        ],
        "📤 Data Export": [
            "get_applied_controls_csv_export - Export controls as CSV",
            "get_assets_csv_export - Export assets as CSV",
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


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
