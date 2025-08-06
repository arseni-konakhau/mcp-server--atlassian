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

# Edit .env with your credentials:
# - JIRA_URL=https://your-company.atlassian.net
# - JIRA_USERNAME=your.email@company.com
# - JIRA_API_TOKEN=your_api_token
# - CONFLUENCE_URL=https://your-company.atlassian.net/wiki
# - CONFLUENCE_USERNAME=your.email@company.com
# - CONFLUENCE_API_TOKEN=your_api_token
```

### 3. Make Setup Script Executable (Unix/Linux)
```bash
chmod +x _setup_test_environment.sh
```

### 4. Run Setup Script
```bash
./_setup_test_environment.sh
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

