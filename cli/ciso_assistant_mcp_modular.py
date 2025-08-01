#!/usr/bin/env python3
"""
CISO Assistant MCP Server Launcher

This script launches the modular CISO Assistant MCP server.
"""

import os
import sys

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add the script directory to Python path
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    # Import and run the modular server
    from ciso_assistant_mcp.server import main

    if __name__ == "__main__":
        print("Starting CISO Assistant MCP Server (Modular Version)")
        print("Using modular structure from ciso_assistant_mcp/ directory")
        print("=" * 60)
        main()

except ImportError as e:
    print(f"Import Error: {e}")
    print("")
    print("Troubleshooting:")
    print("1. Ensure you're in the correct directory")
    print("2. Check that all dependencies are installed:")
    print("   uv add requests python-dotenv mcp rich")
    print("3. Verify the ciso_assistant_mcp/ directory exists")
    print("4. Check your .mcp.env configuration file")
    print("")
    print("Available files in current directory:")
    for item in os.listdir("."):
        print(f"  - {item}")
    sys.exit(1)

except ValueError as e:
    print(f"Configuration Error: {e}")
    print("")
    print("Please check your .mcp.env file and ensure:")
    print("1. API_URL is set to your CISO Assistant instance")
    print("2. TOKEN is set to a valid API token")
    print("3. VERIFY_CERTIFICATE is set (true/false)")
    print("")
    print("If .mcp.env doesn't exist, copy from .mcp.env.sample:")
    print("  cp .mcp.env.sample .mcp.env")
    sys.exit(1)

except Exception as e:
    print(f"Error: {e}")
    print("")
    print("Tip: Check the README.md for detailed setup instructions")
    sys.exit(1)
