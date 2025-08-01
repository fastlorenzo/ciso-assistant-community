"""Shared configuration and utilities for CISO Assistant MCP Server"""

import os
from typing import Optional, List, Dict
import requests
from dotenv import load_dotenv

# Load environment variables from .mcp.env file
load_dotenv(".mcp.env")

# Configuration variables
API_URL = os.getenv("API_URL", "")
TOKEN = os.getenv("TOKEN", "")
VERIFY_CERTIFICATE = os.getenv("VERIFY_CERTIFICATE", "true").lower() in (
    "true",
    "1",
    "yes",
    "on",
)

# Global variables
cli_cfg = dict()
auth_data = dict()
GLOBAL_FOLDER_ID = None

# Export all functions and variables
__all__ = [
    "make_request",
    "format_table",
    "API_URL",
    "TOKEN",
    "VERIFY_CERTIFICATE",
]


def make_request(
    endpoint: str,
    method: str = "GET",
    params: Optional[dict] = None,
    data: Optional[dict] = None,
) -> dict:
    """Make authenticated request to CISO Assistant API"""
    headers = {
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/json",
    }

    url = f"{API_URL}/{endpoint.lstrip('/')}"

    try:
        if method.upper() == "GET":
            response = requests.get(
                url,
                headers=headers,
                params=params,
                verify=VERIFY_CERTIFICATE,
                timeout=30,
            )
        elif method.upper() == "POST":
            response = requests.post(
                url,
                headers=headers,
                json=data,
                verify=VERIFY_CERTIFICATE,
                timeout=30,
            )
        elif method.upper() == "PUT":
            response = requests.put(
                url,
                headers=headers,
                json=data,
                verify=VERIFY_CERTIFICATE,
                timeout=30,
            )
        elif method.upper() == "DELETE":
            response = requests.delete(
                url,
                headers=headers,
                verify=VERIFY_CERTIFICATE,
                timeout=30,
            )
        else:
            return {"error": f"Unsupported HTTP method: {method}"}

        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}


def format_table(data: List[Dict], columns: List[str]) -> str:
    """Format data as markdown table"""
    if not data:
        return "No data available"

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
                # Handle nested objects - show name if available
                value = value.get("name", value.get("str", str(value)))
            elif isinstance(value, list):
                # Handle arrays
                value = ", ".join([str(v) for v in value[:3]])
                # Show first 3 items
                if len(item.get(col, [])) > 3:
                    value += "..."
            # Escape pipes
            row_data.append(str(value).replace("|", "\\|"))
        rows.append("|" + "|".join(row_data) + "|")

    return "\n".join([header, separator] + rows)
