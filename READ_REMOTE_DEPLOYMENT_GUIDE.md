# Remote MCP Atlassian Server Deployment Guide

This guide provides step-by-step instructions for deploying the MCP Atlassian server on a remote machine and accessing it via HTTP from anywhere.

## Prerequisites

- Remote server with Docker installed
- Git installed on the remote server
- Network access to the remote server on your chosen port
- Atlassian Cloud or Server/Data Center instance
- API tokens or Personal Access Tokens for authentication

## Step 1: Upload Git Repository to Remote Server

### Option A: Clone from GitHub (Recommended)

```bash
# SSH into your remote server
ssh user@your-remote-server

# Clone the repository
git clone https://github.com/sooperset/mcp-atlassian.git
cd mcp-atlassian

# Verify the repository structure
ls -la
```

### Option B: Upload Local Repository

```bash
# From your local machine, upload the repository
scp -r /path/to/local/mcp-atlassian user@your-remote-server:/home/user/
```

## Step 2: Configure Environment on Remote Server

### Create Environment Configuration

```bash
# On the remote server, create environment file
cd mcp-atlassian
cp .env.example .env

# Edit the environment file
nano .env
```

### Environment Configuration Examples

#### For Atlassian Cloud:
```bash
# Jira Configuration
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_API_TOKEN=your_jira_api_token

# Confluence Configuration
CONFLUENCE_URL=https://your-company.atlassian.net/wiki
CONFLUENCE_USERNAME=your.email@company.com
CONFLUENCE_API_TOKEN=your_confluence_api_token

# Server Configuration
MCP_VERBOSE=true
MCP_LOGGING_STDOUT=true
READ_ONLY_MODE=false

# Optional: Filter tools and projects
ENABLED_TOOLS=jira_search,jira_get_issue,jira_create_issue,confluence_search,confluence_get_page
JIRA_PROJECTS_FILTER=PROJ,DEV,SUPPORT
CONFLUENCE_SPACES_FILTER=DEV,TEAM,DOC
```

#### For Atlassian Server/Data Center:
```bash
# Jira Configuration
JIRA_URL=https://jira.your-company.com
JIRA_PERSONAL_TOKEN=your_jira_personal_access_token
JIRA_SSL_VERIFY=false

# Confluence Configuration
CONFLUENCE_URL=https://confluence.your-company.com
CONFLUENCE_PERSONAL_TOKEN=your_confluence_personal_access_token
CONFLUENCE_SSL_VERIFY=false

# Server Configuration
MCP_VERBOSE=true
MCP_LOGGING_STDOUT=true
READ_ONLY_MODE=false
```

## Step 3: Run MCP Server on Remote Machine

### Pull Docker Image

```bash
# Pull the latest MCP Atlassian Docker image
docker pull ghcr.io/sooperset/mcp-atlassian:latest
```

### Start Server with HTTP Transport

#### Option A: Streamable-HTTP Transport (Recommended)

```bash
# Start server on port 9000 with streamable-HTTP transport
docker run --name mcp-atlassian-server \
  -d \
  -p 9000:9000 \
  --env-file .env \
  --restart unless-stopped \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 9000 -vv
```

#### Option B: SSE Transport

```bash
# Start server on port 9000 with SSE transport
docker run --name mcp-atlassian-server \
  -d \
  -p 9000:9000 \
  --env-file .env \
  --restart unless-stopped \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport sse --port 9000 -vv
```

### Verify Server is Running

```bash
# Check if container is running
docker ps | grep mcp-atlassian

# Check server health
curl http://localhost:9000/healthz

# View server logs
docker logs mcp-atlassian-server
```

### Configure Firewall (if needed)

```bash
# Allow traffic on port 9000 (Ubuntu/Debian)
sudo ufw allow 9000

# Or for CentOS/RHEL
sudo firewall-cmd --permanent --add-port=9000/tcp
sudo firewall-cmd --reload
```

## Step 4: Test HTTP Access from Anywhere

### Basic Health Check

```bash
# Test server health from any machine
curl http://your-remote-server-ip:9000/healthz

# Expected response:
# {"status": "healthy", "timestamp": "2025-01-18T19:27:00Z"}
```

### Test MCP Protocol

#### List Available Tools

```bash
# Test tools listing
curl -X POST http://your-remote-server-ip:9000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

#### Execute a Tool (Jira Search Example)

```bash
# Search Jira issues
curl -X POST http://your-remote-server-ip:9000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "jira_search",
      "arguments": {
        "jql": "project = PROJ AND status = \"In Progress\"",
        "limit": 5
      }
    }
  }'
```

#### Execute a Tool (Confluence Search Example)

```bash
# Search Confluence pages
curl -X POST http://your-remote-server-ip:9000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "confluence_search",
      "arguments": {
        "query": "documentation",
        "limit": 3
      }
    }
  }'
```

## Step 5: Advanced HTTP Client Integration

### Python Client Example

```python
import requests
import json

class MCPAtlassianClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.session = requests.Session()
        self.request_id = 1
    
    def call_tool(self, tool_name, arguments):
        payload = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        self.request_id += 1
        
        response = self.session.post(
            f"{self.server_url}/mcp",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        return response.json()
    
    def list_tools(self):
        payload = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/list"
        }
        self.request_id += 1
        
        response = self.session.post(
            f"{self.server_url}/mcp",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        return response.json()

# Usage example
client = MCPAtlassianClient("http://your-remote-server:9000")

# List available tools
tools = client.list_tools()
print("Available tools:", json.dumps(tools, indent=2))

# Search Jira issues
jira_results = client.call_tool("jira_search", {
    "jql": "project = PROJ AND status = \"To Do\"",
    "limit": 5
})
print("Jira search results:", json.dumps(jira_results, indent=2))

# Search Confluence pages
confluence_results = client.call_tool("confluence_search", {
    "query": "meeting notes",
    "limit": 3
})
print("Confluence search results:", json.dumps(confluence_results, indent=2))
```

### JavaScript/Node.js Client Example

```javascript
const axios = require('axios');

class MCPAtlassianClient {
    constructor(serverUrl) {
        this.serverUrl = serverUrl;
        this.requestId = 1;
    }

    async callTool(toolName, arguments) {
        const payload = {
            jsonrpc: "2.0",
            id: this.requestId++,
            method: "tools/call",
            params: {
                name: toolName,
                arguments: arguments
            }
        };

        const response = await axios.post(`${this.serverUrl}/mcp`, payload, {
            headers: { 'Content-Type': 'application/json' }
        });
        return response.data;
    }

    async listTools() {
        const payload = {
            jsonrpc: "2.0",
            id: this.requestId++,
            method: "tools/list"
        };

        const response = await axios.post(`${this.serverUrl}/mcp`, payload, {
            headers: { 'Content-Type': 'application/json' }
        });
        return response.data;
    }
}

// Usage example
async function main() {
    const client = new MCPAtlassianClient('http://your-remote-server:9000');
    
    // List tools
    const tools = await client.listTools();
    console.log('Available tools:', JSON.stringify(tools, null, 2));
    
    // Create a Jira issue
    const createResult = await client.callTool('jira_create_issue', {
        project_key: 'PROJ',
        summary: 'Test issue created via HTTP API',
        issue_type: 'Task',
        description: 'This issue was created using the remote MCP server'
    });
    console.log('Created issue:', JSON.stringify(createResult, null, 2));
}

main().catch(console.error);
```

## Step 6: Multi-User Authentication Setup (Optional)

### Enable Multi-User Mode

```bash
# Stop current container
docker stop mcp-atlassian-server
docker rm mcp-atlassian-server

# Start with multi-user OAuth support
docker run --name mcp-atlassian-server \
  -d \
  -p 9000:9000 \
  -e ATLASSIAN_OAUTH_ENABLE=true \
  -e JIRA_URL=https://your-company.atlassian.net \
  -e CONFLUENCE_URL=https://your-company.atlassian.net/wiki \
  --restart unless-stopped \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 9000 -vv
```

### Client with User Authentication

```bash
# Call with user-specific OAuth token
curl -X POST http://your-remote-server:9000/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer user_oauth_token" \
  -H "X-Atlassian-Cloud-Id: user_cloud_id" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "jira_get_issue",
      "arguments": {
        "issue_key": "PROJ-123"
      }
    }
  }'
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```bash
   # Check if server is running
   docker ps | grep mcp-atlassian
   
   # Check server logs
   docker logs mcp-atlassian-server
   
   # Verify port is open
   netstat -tlnp | grep 9000
   ```

2. **Authentication Errors**
   ```bash
   # Verify environment variables
   docker exec mcp-atlassian-server env | grep -E "(JIRA|CONFLUENCE)"
   
   # Test authentication manually
   curl -u "username:api_token" https://your-company.atlassian.net/rest/api/3/myself
   ```

3. **Firewall Issues**
   ```bash
   # Check firewall status
   sudo ufw status
   
   # Test local connectivity
   curl http://localhost:9000/healthz
   
   # Test external connectivity
   curl http://your-remote-server:9000/healthz
   ```

### Debug Mode

```bash
# Run with maximum verbosity
docker run --name mcp-atlassian-debug \
  -p 9000:9000 \
  --env-file .env \
  -e MCP_VERY_VERBOSE=true \
  -e MCP_LOGGING_STDOUT=true \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 9000 -vv

# Monitor logs in real-time
docker logs -f mcp-atlassian-debug
```

## Security Considerations

### Production Deployment

1. **Use HTTPS**: Configure reverse proxy with SSL/TLS
2. **Authentication**: Enable user authentication for multi-user scenarios
3. **Firewall**: Restrict access to specific IP ranges
4. **Monitoring**: Set up logging and monitoring
5. **Updates**: Keep Docker images updated

### Example Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name mcp.your-company.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Summary

You now have a fully functional remote MCP Atlassian server that can be accessed via HTTP from anywhere. The server provides all 42 tools (26 Jira + 16 Confluence) and supports both single-user and multi-user authentication scenarios.

Key endpoints:
- Health check: `GET http://your-server:9000/healthz`
- MCP protocol: `POST http://your-server:9000/mcp`
- SSE transport: `GET http://your-server:9000/sse` (if using SSE)

The server is now ready for integration with AI assistants, custom applications, or any HTTP client that needs to interact with Atlassian products.
