# MCP Atlassian Testing Guide

This guide provides a streamlined approach to test the MCP Atlassian server based on the proven successful workflow.

## 🚀 Quick Start (Proven Workflow)

### 1. One-Time Setup
```bash
# Install dependencies
python3 install_dependencies.py

# Setup environment from template
cp .env.debug .env
# Edit .env with your actual Atlassian credentials
```

### 2. Run Test
```bash
# Test the server
uv run python3 simple_test.py --verbose
```

That's it! This is the proven workflow that works.

## 📋 Prerequisites

### Required Credentials
- **Jira URL**: `https://your-company.atlassian.net`
- **Confluence URL**: `https://your-company.atlassian.net/wiki` 
- **API Tokens**: Generate from [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)

### Environment Setup
- Python 3.8+
- UV package manager (installed automatically by setup script)

## 🔧 Environment Configuration

### Copy and Edit Configuration
```bash
cp .env.debug .env
```

### Required Variables in .env
```bash
# Atlassian URLs
JIRA_URL=https://your-company.atlassian.net
CONFLUENCE_URL=https://your-company.atlassian.net/wiki

# Authentication (API Token method - recommended for Cloud)
JIRA_USERNAME=your.email@company.com
JIRA_API_TOKEN=your_api_token
CONFLUENCE_USERNAME=your.email@company.com
CONFLUENCE_API_TOKEN=your_api_token

# Debug settings (already configured in .env.debug)
MCP_VERBOSE=true
READ_ONLY_MODE=true
```

### Alternative Authentication (Server/Data Center)
```bash
# Personal Access Token method
JIRA_PERSONAL_TOKEN=your_jira_pat
CONFLUENCE_PERSONAL_TOKEN=your_confluence_pat

# SSL verification (for self-signed certificates)
JIRA_SSL_VERIFY=false
CONFLUENCE_SSL_VERIFY=false
```

## 🧪 Testing Levels

### Level 1: Basic Validation (Recommended Start)
```bash
python3 simple_test.py --verbose
```
**Tests**: Imports, configuration, basic API connectivity, MCP server initialization

**What it validates**:
- ✅ All required modules can be imported
- ✅ Environment configuration is valid
- ✅ Atlassian API connectivity works
- ✅ MCP server can initialize and list tools

### Level 2: Advanced Testing (Optional)
```bash
# Direct API testing without MCP protocol
uv run python3 manual_test_debug.py --mode api --verbose

# HTTP transport testing
uv run python3 manual_test_debug.py --mode http --port 8000
```

### Level 3: Production Testing
```bash
# Full MCP server with read-only mode
uv run mcp-atlassian --env-file .env --read-only --verbose

# Full functionality (removes read-only protection)
uv run mcp-atlassian --env-file .env --verbose
```

## 🐛 Troubleshooting

### Common Issues & Solutions

#### "No module named 'click'" or similar import errors
```bash
# Solution: Install dependencies
python3 install_dependencies.py
```

#### "401 Unauthorized" authentication errors
- **Check API token**: Verify it's correct and not expired
- **Check username format**: Use email format for Atlassian Cloud
- **Test manually**: 
  ```bash
  curl -u "your.email@company.com:your_api_token" \
    "https://your-company.atlassian.net/rest/api/2/myself"
  ```

#### Connection timeouts or network errors
- **Check URLs**: Ensure Atlassian URLs are correct
- **Corporate networks**: Configure proxy if needed
- **Self-signed certificates**: Set `JIRA_SSL_VERIFY=false` for Server/Data Center

#### "'JiraClient' object has no attribute..." errors
- **Solution**: Use the provided updated scripts that import `JiraFetcher` and `ConfluenceFetcher`

### Debug Mode
Enable maximum logging for troubleshooting:
```bash
export MCP_VERY_VERBOSE=true
export MCP_LOGGING_STDOUT=true
```

## 🔍 Testing Components

### What simple_test.py validates:

1. **Import Testing**
   - All MCP Atlassian modules load correctly
   - Dependencies are available

2. **Configuration Testing**
   - Environment variables are set
   - Authentication methods are configured
   - URLs are valid

3. **API Connectivity Testing**
   - Jira API connection and authentication
   - Confluence API connection and authentication
   - Basic operations (list projects, list spaces)

4. **MCP Server Testing**
   - Server initialization
   - Tool registration and listing
   - Basic MCP protocol compliance

### Command Line Options
```bash
# Basic test with verbose output
python3 simple_test.py --verbose

# Skip API tests (useful if credentials not ready)
python3 simple_test.py --skip-api --verbose

# Skip MCP server tests
python3 simple_test.py --skip-mcp --verbose

# Use custom .env file
python3 simple_test.py --env-file custom.env --verbose
```

## 🚀 Next Steps After Successful Testing

### IDE Integration
Configure your AI assistant (Claude Desktop, Cursor, etc.) with the MCP server:

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "uv",
      "args": [
        "run", 
        "mcp-atlassian", 
        "--env-file", 
        "/path/to/your/.env",
        "--verbose"
      ],
      "cwd": "/path/to/mcp-atlassian"
    }
  }
}
```

### Production Deployment
- Use Docker image: `ghcr.io/sooperset/mcp-atlassian:latest`
- Remove `READ_ONLY_MODE=true` for write operations
- Set up monitoring and logging
- Configure proper authentication and security

## 📁 File Reference

| File | Purpose | When to Use |
|------|---------|-------------|
| `install_dependencies.py` | Install required Python packages | One-time setup |
| `simple_test.py` | Basic validation and testing | Primary testing tool |
| `manual_test_debug.py` | Advanced debugging modes | Troubleshooting |
| `.env.debug` | Configuration template | Copy to `.env` and edit |

## 🎯 Success Criteria

After running `python3 simple_test.py --verbose`, you should see:
- ✅ All import tests passed
- ✅ Configuration tests passed  
- ✅ API connectivity tests passed
- ✅ MCP server tests passed
- ✅ "All tests passed! The MCP Atlassian server appears to be working correctly."

If you see this output, your MCP Atlassian server is ready for use!

---

**Quick Command**: `python3 install_dependencies.py && cp .env.debug .env && python3 simple_test.py --verbose`
