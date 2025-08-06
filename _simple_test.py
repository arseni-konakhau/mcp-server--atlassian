#!/usr/bin/env python
"""
Simple Testing Script for MCP Atlassian (without UV dependency)

This script provides basic testing capabilities for the MCP Atlassian server
without requiring UV package manager. It can be used for quick debugging
and validation of the core functionality.

Usage:
    python simple_test.py --help
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from dotenv import load_dotenv
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables must be set manually.")
    def load_dotenv(*args, **kwargs):
        pass

def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def check_environment() -> dict:
    """Check and validate environment configuration."""
    config = {}
    
    # Check Jira configuration
    jira_url = os.getenv("JIRA_URL")
    jira_username = os.getenv("JIRA_USERNAME")
    jira_token = os.getenv("JIRA_API_TOKEN")
    jira_pat = os.getenv("JIRA_PERSONAL_TOKEN")
    
    if jira_url:
        config["jira"] = {
            "url": jira_url,
            "auth_method": None
        }
        if jira_username and jira_token:
            config["jira"]["auth_method"] = "api_token"
            config["jira"]["username"] = jira_username
        elif jira_pat:
            config["jira"]["auth_method"] = "personal_token"
    
    # Check Confluence configuration
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_username = os.getenv("CONFLUENCE_USERNAME")
    confluence_token = os.getenv("CONFLUENCE_API_TOKEN")
    confluence_pat = os.getenv("CONFLUENCE_PERSONAL_TOKEN")
    
    if confluence_url:
        config["confluence"] = {
            "url": confluence_url,
            "auth_method": None
        }
        if confluence_username and confluence_token:
            config["confluence"]["auth_method"] = "api_token"
            config["confluence"]["username"] = confluence_username
        elif confluence_pat:
            config["confluence"]["auth_method"] = "personal_token"
    
    return config

async def test_basic_imports() -> bool:
    """Test if all required modules can be imported."""
    print("=== Testing Basic Imports ===")
    
    try:
        from mcp_atlassian.jira.config import JiraConfig
        print("✓ Jira config module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Jira config: {e}")
        return False
    
    try:
        from mcp_atlassian.confluence.config import ConfluenceConfig
        print("✓ Confluence config module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Confluence config: {e}")
        return False
    
    try:
        from mcp_atlassian.servers.main import main_mcp
        print("✓ Main MCP server module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import main MCP server: {e}")
        return False
    
    return True

async def test_configuration() -> bool:
    """Test configuration loading."""
    print("\n=== Testing Configuration ===")
    
    config = check_environment()
    
    if not config:
        print("✗ No Atlassian services configured")
        print("Please set environment variables for Jira and/or Confluence")
        return False
    
    success = True
    
    if "jira" in config:
        jira_config = config["jira"]
        print(f"✓ Jira URL configured: {jira_config['url']}")
        if jira_config["auth_method"]:
            print(f"✓ Jira authentication method: {jira_config['auth_method']}")
        else:
            print("✗ Jira authentication not configured")
            success = False
    
    if "confluence" in config:
        confluence_config = config["confluence"]
        print(f"✓ Confluence URL configured: {confluence_config['url']}")
        if confluence_config["auth_method"]:
            print(f"✓ Confluence authentication method: {confluence_config['auth_method']}")
        else:
            print("✗ Confluence authentication not configured")
            success = False
    
    return success

async def test_api_connectivity() -> bool:
    """Test basic API connectivity."""
    print("\n=== Testing API Connectivity ===")
    
    try:
        from mcp_atlassian.jira.config import JiraConfig
        from mcp_atlassian.jira import JiraFetcher
        from mcp_atlassian.confluence.config import ConfluenceConfig
        from mcp_atlassian.confluence import ConfluenceFetcher
    except ImportError as e:
        print(f"✗ Failed to import required modules: {e}")
        return False
    
    success = True
    
    # Test Jira
    if os.getenv("JIRA_URL"):
        try:
            jira_config = JiraConfig.from_env()
            if jira_config.is_auth_configured():
                print("Testing Jira connection...")
                jira_client = JiraFetcher(jira_config)
                projects = jira_client.get_all_projects()
                print(f"✓ Jira connection successful - found {len(projects)} projects")
                if projects:
                    project = projects[0]
                    project_key = project.get('key', 'Unknown')
                    project_name = project.get('name', 'Unknown')
                    print(f"  Sample project: {project_key} - {project_name}")
            else:
                print("✗ Jira authentication not properly configured")
                success = False
        except Exception as e:
            print(f"✗ Jira connection failed: {e}")
            success = False
    
    # Test Confluence
    if os.getenv("CONFLUENCE_URL"):
        try:
            confluence_config = ConfluenceConfig.from_env()
            if confluence_config.is_auth_configured():
                print("Testing Confluence connection...")
                confluence_client = ConfluenceFetcher(confluence_config)
                spaces_result = confluence_client.get_spaces(limit=10)
                spaces = spaces_result.get('results', []) if isinstance(spaces_result, dict) else []
                print(f"✓ Confluence connection successful - found {len(spaces)} spaces")
                if spaces:
                    space = spaces[0]
                    space_key = space.get('key', 'Unknown')
                    space_name = space.get('name', 'Unknown')
                    print(f"  Sample space: {space_key} - {space_name}")
            else:
                print("✗ Confluence authentication not properly configured")
                success = False
        except Exception as e:
            print(f"✗ Confluence connection failed: {e}")
            success = False
    
    return success

async def test_mcp_server() -> bool:
    """Test MCP server initialization."""
    print("\n=== Testing MCP Server Initialization ===")
    
    try:
        from mcp_atlassian.servers.main import main_mcp
        
        # Test getting tools
        tools = await main_mcp.get_tools()
        print(f"✓ MCP server initialized successfully")
        print(f"✓ Found {len(tools)} available tools")
        
        # List some tools
        tool_names = list(tools.keys())[:5]  # Show first 5 tools
        if tool_names:
            print("  Sample tools:")
            for tool_name in tool_names:
                print(f"    - {tool_name}")
        
        return True
    except Exception as e:
        print(f"✗ MCP server initialization failed: {e}")
        return False

def print_recommendations() -> None:
    """Print recommendations based on test results."""
    print("\n=== Recommendations ===")
    print("1. For end-to-end testing, use the full testing guide:")
    print("   - Follow TESTING_GUIDE.md")
    print("   - Use 'uv run mcp-atlassian' for full functionality")
    print("")
    print("2. For debugging specific issues:")
    print("   - Enable verbose logging: export MCP_VERY_VERBOSE=true")
    print("   - Use read-only mode: export READ_ONLY_MODE=true")
    print("   - Test individual components with this script")
    print("")
    print("3. For production deployment:")
    print("   - Use Docker image: ghcr.io/sooperset/mcp-atlassian:latest")
    print("   - Configure proper authentication")
    print("   - Set up monitoring and logging")

def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Simple testing for MCP Atlassian")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--env-file", help="Path to .env file", default=".env")
    parser.add_argument("--skip-api", action="store_true", help="Skip API connectivity tests")
    parser.add_argument("--skip-mcp", action="store_true", help="Skip MCP server tests")
    
    args = parser.parse_args()
    
    # Load environment
    if os.path.exists(args.env_file):
        load_dotenv(args.env_file)
        print(f"Loaded environment from {args.env_file}")
    else:
        print(f"Warning: {args.env_file} not found, using system environment")
    
    # Setup logging
    setup_logging(args.verbose)
    
    async def run_tests():
        """Run all tests."""
        all_passed = True
        
        # Test imports
        if not await test_basic_imports():
            all_passed = False
            print("\n❌ Basic import tests failed. Check your Python environment and dependencies.")
            return False
        
        # Test configuration
        if not await test_configuration():
            all_passed = False
            print("\n❌ Configuration tests failed. Check your .env file and environment variables.")
        
        # Test API connectivity
        if not args.skip_api:
            if not await test_api_connectivity():
                all_passed = False
                print("\n❌ API connectivity tests failed. Check your credentials and network.")
        
        # Test MCP server
        if not args.skip_mcp:
            if not await test_mcp_server():
                all_passed = False
                print("\n❌ MCP server tests failed. Check the server configuration.")
        
        if all_passed:
            print("\n✅ All tests passed! The MCP Atlassian server appears to be working correctly.")
        else:
            print("\n⚠️  Some tests failed. See the output above for details.")
        
        print_recommendations()
        return all_passed
    
    try:
        success = asyncio.run(run_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTesting interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Testing failed with error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
