# MCP Atlassian Server - Quick Setup Guide

## Prerequisites
- Python 3.8+
- `uv` package manager
- Atlassian account with API tokens

## Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/arseni-konakhau/mcp-server--atlassian.git
cd mcp-server--atlassian
```

### 2. Make Setup Script Executable (Unix/Linux)
```bash
chmod +x _setup_test_environment.sh
```

### 3. Run Setup Script
```bash
./_setup_test_environment.sh
```

### 4. Configure Environment
```bash
# Script will create .env from env.debug if needed
# Edit .env with your credentials:

# Edit .env with your credentials:
# - JIRA_URL=https://your-company.atlassian.net
# - JIRA_USERNAME=your.email@company.com
# - JIRA_API_TOKEN=your_api_token
# - CONFLUENCE_URL=https://your-company.atlassian.net/wiki
# - CONFLUENCE_USERNAME=your.email@company.com
# - CONFLUENCE_API_TOKEN=your_api_token
```

### 4. Run Test
```bash
python3 _simple_test.py --verbose
```

## Success Indicators
✅ All import tests passed  
✅ Configuration tests passed  
✅ API connectivity tests passed  
✅ MCP server tests passed  
✅ "All tests passed! The MCP Atlassian server appears to be working correctly."

## Quick One-Liner
```bash
git clone https://github.com/arseni-konakhau/mcp-server--atlassian.git && cd mcp-server--atlassian && chmod +x _setup_test_environment.sh && ./_setup_test_environment.sh && echo "Edit .env with your credentials, then run: python3 _simple_test.py --verbose"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | Run `python3 _install_dependencies.py` |
| 401 Unauthorized | Check API token and username in `.env` |
| Connection timeout | Verify Atlassian URLs in `.env` |

## Next Steps
After successful test, integrate with your IDE:
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "uv",
      "args": ["run", "mcp-atlassian", "--env-file", "/path/to/.env", "--verbose"],
      "cwd": "/path/to/mcp-server--atlassian"
    }
  }
}
```

---
**Get API Token**: [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
