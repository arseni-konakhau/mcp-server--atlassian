#!/usr/bin/env python3 || /usr/bin/env python

"""
Manual Testing and Debugging Script for MCP Atlassian

This script provides various ways to test and debug the MCP Atlassian server:
1. Direct API testing without MCP protocol
2. MCP protocol testing with stdio transport
3. HTTP transport testing
4. Individual tool testing

Usage:
    python manual_test_debug.py --mode [api|mcp|http|tool] [options]
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

from dotenv import load_dotenv

# Import MCP Atlassian modules
from mcp_atlassian.confluence import ConfluenceFetcher
from mcp_atlassian.confluence.config import ConfluenceConfig
from mcp_atlassian.jira import JiraFetcher
from mcp_atlassian.jira.config import JiraConfig
from mcp_atlassian.servers.main import main_mcp


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


async def test_direct_api(args: argparse.Namespace) -> None:
    """Test direct API calls without MCP protocol."""
    print("=== Testing Direct API Calls ===")
    
    # Test Jira
    if os.getenv("JIRA_URL"):
        print("\n--- Testing Jira API ---")
        try:
            jira_config = JiraConfig.from_env()
            if jira_config.is_auth_configured():
                jira_client = JiraFetcher(jira_config)
                
                # Test basic connection
                print("Testing Jira connection...")
                projects = jira_client.get_all_projects()
                print(f"✓ Found {len(projects)} Jira projects")
                
                if args.test_issue and projects:
                    # Test getting a specific issue
                    test_issue = args.test_issue or f"{projects[0].key}-1"
                    print(f"Testing issue retrieval: {test_issue}")
                    try:
                        issue = await jira_client.get_issue(test_issue)
                        print(f"✓ Retrieved issue: {issue.key} - {issue.summary}")
                    except Exception as e:
                        print(f"✗ Failed to get issue {test_issue}: {e}")
                        
            else:
                print("✗ Jira authentication not configured")
        except Exception as e:
            print(f"✗ Jira API test failed: {e}")
    
    # Test Confluence
    if os.getenv("CONFLUENCE_URL"):
        print("\n--- Testing Confluence API ---")
        try:
            confluence_config = ConfluenceConfig.from_env()
            if confluence_config.is_auth_configured():
                confluence_client = ConfluenceFetcher(confluence_config)
                
                # Test basic connection
                print("Testing Confluence connection...")
                spaces_result = confluence_client.get_spaces(limit=10)
                spaces = spaces_result.get('results', []) if isinstance(spaces_result, dict) else []
                print(f"✓ Found {len(spaces)} Confluence spaces")
                
                if args.test_page and spaces:
                    # Test searching for pages
                    print("Testing page search...")
                    try:
                        search_results = confluence_client.search_content(
                            query="title ~ '*'", 
                            limit=5
                        )
                        print(f"✓ Found {len(search_results)} pages in search")
                        if search_results:
                            page = search_results[0]
                            print(f"  Sample page: {page.title} (ID: {page.id})")
                    except Exception as e:
                        print(f"✗ Failed to search pages: {e}")
                        
            else:
                print("✗ Confluence authentication not configured")
        except Exception as e:
            print(f"✗ Confluence API test failed: {e}")


async def test_mcp_stdio() -> None:
    """Test MCP protocol with stdio transport."""
    print("=== Testing MCP Protocol (STDIO) ===")
    print("Note: This will start the MCP server in stdio mode")
    print("You can test it manually by sending MCP protocol messages")
    print("Press Ctrl+C to stop the server")
    
    try:
        # This will run the server in stdio mode
        await main_mcp.run_async(transport="stdio")
    except KeyboardInterrupt:
        print("\nMCP server stopped by user")
    except Exception as e:
        print(f"MCP server error: {e}")


async def test_mcp_http(port: int = 8000) -> None:
    """Test MCP protocol with HTTP transport."""
    print(f"=== Testing MCP Protocol (HTTP) on port {port} ===")
    print(f"Server will be available at: http://localhost:{port}/mcp")
    print("You can test it with curl or MCP client tools")
    print("Press Ctrl+C to stop the server")
    
    try:
        await main_mcp.run_async(
            transport="streamable-http",
            host="localhost",
            port=port,
            log_level="debug"
        )
    except KeyboardInterrupt:
        print("\nHTTP MCP server stopped by user")
    except Exception as e:
        print(f"HTTP MCP server error: {e}")


async def test_specific_tool(tool_name: str, **kwargs) -> None:
    """Test a specific MCP tool."""
    print(f"=== Testing Specific Tool: {tool_name} ===")
    
    # This would require implementing tool-specific test logic
    # For now, we'll show how to access the tools
    try:
        tools = await main_mcp.get_tools()
        if tool_name in tools:
            tool = tools[tool_name]
            print(f"Tool found: {tool_name}")
            print(f"Description: {tool.description}")
            print(f"Parameters: {json.dumps(tool.input_schema, indent=2)}")
            
            # You could call the tool here with test parameters
            # result = await tool.call(**kwargs)
            # print(f"Result: {result}")
        else:
            print(f"Tool '{tool_name}' not found")
            print(f"Available tools: {list(tools.keys())}")
    except Exception as e:
        print(f"Error testing tool {tool_name}: {e}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Manual testing and debugging for MCP Atlassian")
    parser.add_argument(
        "--mode",
        choices=["api", "mcp", "http", "tool"],
        default="api",
        help="Testing mode"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--env-file", help="Path to .env file", default=".env")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP mode")
    parser.add_argument("--test-issue", help="Jira issue key to test (e.g., PROJ-123)")
    parser.add_argument("--test-page", help="Confluence page ID to test")
    parser.add_argument("--tool-name", help="Specific tool to test")
    
    args = parser.parse_args()
    
    # Load environment
    if os.path.exists(args.env_file):
        load_dotenv(args.env_file)
        print(f"Loaded environment from {args.env_file}")
    else:
        print(f"Warning: {args.env_file} not found, using system environment")
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Run the appropriate test
    try:
        if args.mode == "api":
            asyncio.run(test_direct_api(args))
        elif args.mode == "mcp":
            asyncio.run(test_mcp_stdio())
        elif args.mode == "http":
            asyncio.run(test_mcp_http(args.port))
        elif args.mode == "tool":
            if not args.tool_name:
                print("Error: --tool-name is required for tool mode")
                sys.exit(1)
            asyncio.run(test_specific_tool(args.tool_name))
    except KeyboardInterrupt:
        print("\nTesting interrupted by user")
    except Exception as e:
        print(f"Testing failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
