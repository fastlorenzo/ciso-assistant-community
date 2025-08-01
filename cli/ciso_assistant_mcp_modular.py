#!/usr/bin/env python3
"""
CISO Assistant MCP Server Launcher

This script launches the modular CISO Assistant MCP server.
It's a drop-in replacement for the original ciso_assistant_mcp_complete.py file.
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
    print("   pip install requests python-dotenv mcp")
    print("3. Verify the ciso_assistant_mcp/ directory exists")
    print("4. Check your .mcp.env configuration file")
    sys.exit(1)
    
except Exception as e:
    print(f"Error: {e}")
    print("")
    print("Tip: Check the README.md in ciso_assistant_mcp/ for detailed setup instructions")
    sys.exit(1)
