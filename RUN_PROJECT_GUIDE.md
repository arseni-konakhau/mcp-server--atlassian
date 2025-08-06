# MCP Atlassian Server - Quick Setup Guide

## Prerequisites
- Python 3+

**NOTE THAT: in your working env python version of 3 may be named differently so make sure all occurances in following guide with `python3` should be replaced with `python`. This amendment is part of expected part of following guide**


## Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/arseni-konakhau/mcp-server--atlassian.git
cd mcp-server--atlassian
```

### 2. Prepare Environment File
```bash
# Copy your environment template (env.akonakhau) to .env
cp env.akonakhau .env
```

### 3. Make Setup Script Executable (Unix/Linux)
```bash
chmod +x _setup_test_environment.sh
```

### 4. Run Setup Script
```bash
./_setup_test_environment.sh
```
or
```bash
bash ./_setup_test_environment.sh
```

### 5. Run Test
```bash
uv run python3 _simple_test.py --verbose
# or (for envs where python of 3rd version not aliased and named 'python')
# uv run python _simple_test.py --verbose
```

## Success Indicators
✅ All import tests passed  
✅ Configuration tests passed  
✅ API connectivity tests passed  
✅ MCP server tests passed  
✅ "All tests passed! The MCP Atlassian server appears to be working correctly."




------------




## Validate MCP Server via HTTP

### 1. Run Server in Background
```bash
uv run mcp-atlassian --transport streamable-http --port 3334 --verbose &
```

### 2. Verify Server is Running
```bash
curl -v http://localhost:3334/health
```
Expected response:
```json
{"status":"ok"}
```

### 3. Test Available Tools
```bash
# List all available tools
curl -X POST http://localhost:3334/tools/list -H "Content-Type: application/json" -d '{}'

# Example: Search Jira issues
curl -X POST http://localhost:3334/tools/jira_search \
  -H "Content-Type: application/json" \
  -d '{"jql":"project = PROJ AND status = '\''In Progress'\''"}'

# Example: Get Confluence page
curl -X POST http://localhost:3334/tools/confluence_get_page \
  -H "Content-Type: application/json" \
  -d '{"page_id":"123456"}'
```

### 4. Stop the Server
```bash
# Find the process ID
ps aux | grep "uv run mcp-atlassian"

# Kill the process
kill -9 [PID]
```

### Troubleshooting
- If you get connection refused, verify the server is running
- For 401 errors, check your .env credentials
- For 500 errors, check server logs
