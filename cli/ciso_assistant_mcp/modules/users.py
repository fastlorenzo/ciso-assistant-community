"""Users and Access module for CISO Assistant MCP Server"""

import json
from typing import Optional

from ..config import make_request, format_table


def register_users_tools(mcp):
    """Register users and access tools with the MCP server"""

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
            group_name: Optional group name to filter, if not provided returns
                all groups with members
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
                        result_text += f"- {member.get('email', 'Unknown')}\n"
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

    @mcp.tool()
    async def get_user_preferences():
        """Get current user preferences"""
        result = make_request("user-preferences/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)
