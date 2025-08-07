# MCP Atlassian Server - Deployment Guide

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
chmod +x start.sh
```

### 4. Run Setup Script
```bash
bash ./start.sh
```

### 5. Run Test
```bash
uv run python3 ./scripts/_simple_test.py --verbose
# or (for envs where python of 3rd version not aliased and named 'python')
# uv run python ./scripts/_simple_test.py --verbose
```

## Success Indicators
✅ All import tests passed  
✅ Configuration tests passed  
✅ API connectivity tests passed  
✅ MCP server tests passed  
✅ "All tests passed! The MCP Atlassian server appears to be working correctly."



------------



## UNIX/Linux Server Management

### Running the Server
```bash
# start server in foreground
uv run mcp-atlassian --transport streamable-http --port 3334 --env-file .env --verbose

# Start server in background
nohup uv run mcp-atlassian --transport streamable-http --port 3334 --verbose > mcp-server.log 2>&1 &

# To check server logs:
# tail -f mcp-server.log
```

### Verifying Server Status
```bash
# Basic health check
curl -v http://localhost:3334/health

# selectel
curl -v http://87.228.101.211:3334/health

# Detailed process info
ps aux | grep "uv run mcp-atlassian"

# Check port usage
netstat -tulnp | grep 3334
```

### Testing Server Functionality
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
# Find the process ID (look for the nohup command)
ps aux | grep "uv run mcp-atlassian"

# Kill the process (replace [PID] with actual process number)
kill -9 [PID]

# Alternative: Find and kill in one command
pkill -f "uv run mcp-atlassian"

# Verify process is gone
ps aux | grep "uv run mcp-atlassian"
```

### Troubleshooting
- If you get connection refused, verify the server is running
- For 401 errors, check your .env credentials
- For 500 errors, check server logs
