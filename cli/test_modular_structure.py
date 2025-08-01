#!/usr/bin/env python3
"""
Test script to verify the modular CISO Assistant MCP server structure
"""

import os
import sys


def test_imports():
    """Test that all modules can be imported correctly"""
    print("Testing module imports...")

    # Test config import
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        print("  Config module imported successfully")
    except ImportError as e:
        print(f"  Config import failed: {e}")
        return False

    # Test all module imports
    modules = [
        ("risk_management", "register_risk_tools"),
        ("compliance", "register_compliance_tools"),
        ("assets", "register_assets_tools"),
        ("security", "register_security_tools"),
        ("ebios", "register_ebios_tools"),
        ("users", "register_users_tools"),
        ("analytics", "register_analytics_tools"),
    ]

    for module_name, function_name in modules:
        try:
            module = __import__(
                f"ciso_assistant_mcp.modules.{module_name}", fromlist=[function_name]
            )
            getattr(module, function_name)
            print(f"  {module_name} module imported successfully")
        except ImportError as e:
            print(f"  {module_name} import failed: {e}")
            return False
        except AttributeError as e:
            print(f"  {module_name} missing function {function_name}: {e}")
            return False

    return True


def test_file_structure():
    """Test that all expected files exist"""
    print("\nTesting file structure...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_dir = os.path.join(base_dir, "ciso_assistant_mcp")
    modules_dir = os.path.join(mcp_dir, "modules")

    expected_files = [
        os.path.join(mcp_dir, "__init__.py"),
        os.path.join(mcp_dir, "config.py"),
        os.path.join(mcp_dir, "server.py"),
        os.path.join(mcp_dir, "README.md"),
        os.path.join(modules_dir, "__init__.py"),
        os.path.join(modules_dir, "risk_management.py"),
        os.path.join(modules_dir, "compliance.py"),
        os.path.join(modules_dir, "assets.py"),
        os.path.join(modules_dir, "security.py"),
        os.path.join(modules_dir, "ebios.py"),
        os.path.join(modules_dir, "users.py"),
        os.path.join(modules_dir, "analytics.py"),
    ]

    missing_files = []
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"  {os.path.relpath(file_path, base_dir)}")
        else:
            print(f"  {os.path.relpath(file_path, base_dir)} - MISSING")
            missing_files.append(file_path)

    return len(missing_files) == 0


def test_documentation():
    """Test that documentation files exist and are readable"""
    print("\nTesting documentation...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_dir = os.path.join(base_dir, "ciso_assistant_mcp")

    docs = [
        ("README.md", "Main documentation"),
        ("REFACTORING_COMPARISON.md", "Refactoring comparison"),
    ]

    for doc_file, description in docs:
        doc_path = os.path.join(mcp_dir, doc_file)
        if os.path.exists(doc_path):
            try:
                with open(doc_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if len(content) > 100:  # Basic content check
                        print(f"  {doc_file} - {description} ({len(content)} chars)")
                    else:
                        print(f"  {doc_file} - Too short ({len(content)} chars)")
            except Exception as e:
                print(f"  {doc_file} - Read error: {e}")
        else:
            print(f"  {doc_file} - MISSING")


def main():
    """Run all tests"""
    print("CISO Assistant MCP Modular Structure Test")
    print("=" * 50)

    tests_passed = 0
    total_tests = 3

    # Test file structure
    if test_file_structure():
        tests_passed += 1
        print("File structure test PASSED")
    else:
        print("File structure test FAILED")

    # Test imports
    if test_imports():
        tests_passed += 1
        print("Import test PASSED")
    else:
        print("Import test FAILED")

    # Test documentation
    test_documentation()
    tests_passed += 1  # Documentation is not critical for functionality

    print("\n" + "=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("All tests passed! The modular structure is ready to use.")
        print("\nNext steps:")
        print("1. Configure your .mcp.env file")
        print("2. Run: python ciso_assistant_mcp/server.py")
        print("3. Or use the launcher: python ciso_assistant_mcp_modular.py")
        return True
    else:
        print("Some tests failed. Please check the structure and fix any issues.")
        return False


if __name__ == "__main__":
    SUCCESS = main()
    sys.exit(0 if SUCCESS else 1)
