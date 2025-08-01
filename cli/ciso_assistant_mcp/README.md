# CISO Assistant MCP Server - Modular Version

This is a refactored, modular version of the CISO Assistant MCP server. The original large file (`ciso_assistant_mcp_complete.py`) has been split into logical modules for better maintainability, easier development, and improved code organization.

## 📁 Project Structure

```
ciso_assistant_mcp/
├── __init__.py                 # Package initialization
├── config.py                   # Shared configuration and utilities
├── server.py                   # Main server entry point
└── modules/
    ├── __init__.py
    ├── risk_management.py      # Risk management tools
    ├── compliance.py           # Compliance and audit tools
    ├── assets.py              # Assets and projects tools
    ├── security.py            # Security tools
    ├── ebios.py               # EBIOS-RM tools
    ├── users.py               # Users and access tools
    └── analytics.py           # Analytics and utilities tools
```

## 🚀 Getting Started

### Prerequisites

1. Install the required dependencies:
   ```bash
   pip install requests python-dotenv mcp
   ```

2. Configure your environment variables in `.mcp.env`:
   ```env
   API_URL=https://your-ciso-assistant-instance.com/api
   TOKEN=your_api_token
   VERIFY_CERTIFICATE=true
   ```

### Running the Server

From the CLI directory, run:

```bash
python ciso_assistant_mcp/server.py
```

Or use it as a module:

```bash
python -m ciso_assistant_mcp.server
```

## 📋 Module Organization

### 🔐 Risk Management (`risk_management.py`)
- `get_risk_scenarios` - Get risk scenarios from Risk Registry
- `get_risk_assessments` - Get risk assessments
- `get_threats` - Get threats catalog
- `get_risk_matrices` - Get risk matrices
- `get_risk_scenarios_by_level` - Get count per risk level
- `get_risk_scenarios_qualifications` - Get qualifications
- `get_risk_assessment_quality_check` - Quality check for assessments
- Choice lists for risk-related fields

### 📋 Compliance & Audits (`compliance.py`)
- `get_applied_controls` - Get applied controls/action plan
- `get_audits_progress` - Get compliance audits progress
- `get_audit_detailed_status` - Get detailed audit status
- `get_audit_requirements` - Get audit requirements
- `get_requirements_assessments` - Get requirement assessments
- `get_frameworks` - Get compliance frameworks
- Compliance assessment charts and analytics
- Choice lists for compliance fields

### 🏢 Assets & Projects (`assets.py`)
- `get_assets` - Get assets inventory
- `get_asset_classes` - Get asset classes/categories
- `get_asset_class_tree` - Get asset class hierarchy
- `get_assets_graph` - Get assets relationship graph
- `get_projects` - Get projects list
- `get_folders` - Get organizational folders
- Asset-related utilities and exports

### 🛡️ Security (`security.py`)
- `get_security_measures` - Get security measures/controls
- `get_security_incidents` - Get security incidents
- `get_security_exceptions` - Get security exceptions
- `get_vulnerabilities` - Get vulnerabilities
- `get_findings` - Get findings from assessments
- `get_findings_assessments` - Get findings assessments
- Choice lists for security fields

### 📊 EBIOS-RM (`ebios.py`)
- `get_ebios_studies` - Get EBIOS-RM studies
- `get_ebios_stakeholders` - Get EBIOS stakeholders
- `get_ebios_feared_events` - Get EBIOS feared events
- `get_ebios_ro_to` - Get EBIOS risk origins
- `get_ebios_strategic_scenarios` - Get strategic scenarios
- `get_ebios_operational_scenarios` - Get operational scenarios
- `get_ebios_attack_paths` - Get attack paths

### 👥 Users & Access (`users.py`)
- `get_users` - Get users list
- `get_user_details` - Get detailed user information
- `get_user_groups` - Get user groups
- `get_user_group_members` - Get group members
- `get_admin_users` - Get admin users
- `get_roles` - Get system roles
- `get_role_assignments` - Get role assignments
- `get_user_preferences` - Get user preferences

### 📈 Analytics & Utilities (`analytics.py`)
- `get_compliance_summary` - Get compliance summary
- `search_items` - Search across all items
- `get_agg_data` - Get aggregated dashboard data
- `get_composer_data` - Get visualization data
- `get_threats_count` - Get threats count data
- `get_object_by_id` - Get any object by ID and type
- `get_build_info` - Get system build information
- `get_system_info` - Get system connectivity status
- `list_all_endpoints` - List all available tools

## 🔧 Configuration (`config.py`)

Contains shared configuration and utility functions:
- `make_request()` - Authenticated API request function
- `format_table()` - Markdown table formatting utility
- Environment variable loading
- Global configuration constants

## 🎯 Benefits of the Modular Structure

1. **Maintainability**: Each module focuses on a specific domain, making it easier to find and modify functionality.

2. **Scalability**: New modules can be added easily without affecting existing code.

3. **Testing**: Individual modules can be tested in isolation.

4. **Code Reuse**: Common functionality is centralized in the config module.

5. **Team Development**: Multiple developers can work on different modules simultaneously.

6. **Documentation**: Each module can have its own focused documentation.

## 🛠️ Development Guide

### Adding a New Module

1. Create a new file in the `modules/` directory (e.g., `new_module.py`)

2. Implement the registration function:
   ```python
   def register_new_tools(mcp):
       from ..config import make_request, format_table
       
       @mcp.tool()
       async def my_new_tool():
           # Implementation here
           pass
   ```

3. Import and register in `server.py`:
   ```python
   from ciso_assistant_mcp.modules.new_module import register_new_tools
   
   # In main():
   register_new_tools(mcp)
   ```

### Adding a New Tool to an Existing Module

1. Open the relevant module file
2. Add your new tool function with the `@mcp.tool()` decorator
3. The tool will automatically be available when the server starts

## 🔄 Migration from Original File

The original `ciso_assistant_mcp_complete.py` file has been preserved for reference. All functionality has been maintained in the modular version, with the following improvements:

- Better error handling
- Cleaner imports
- Logical grouping of related functions
- Easier maintenance and extension
- Better documentation

## 📝 Notes

- All original functionality is preserved
- The API remains exactly the same
- Configuration is unchanged
- Performance is not affected
- Memory usage may be slightly improved due to better import management

## 🐛 Troubleshooting

If you encounter import errors:

1. Ensure you're running from the correct directory
2. Check that all required dependencies are installed
3. Verify your `.mcp.env` file is properly configured
4. Make sure the Python path includes the current directory

For any issues, please check the original `ciso_assistant_mcp_complete.py` file for reference implementation.
