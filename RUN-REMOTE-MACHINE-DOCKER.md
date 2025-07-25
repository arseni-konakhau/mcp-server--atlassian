# Remote Machine Setup Guide for MCP Atlassian

This guide provides step-by-step instructions for setting up the MCP Atlassian server on a remote machine and accessing it via HTTP from anywhere.

## Overview

This setup allows you to:
- Deploy MCP Atlassian server on a remote machine (VPS, cloud instance, etc.)
- Access all 42 MCP tools (26 Jira + 16 Confluence) via HTTP
- Support both single-user and multi-user authentication
- Enable secure remote access from any location

## Prerequisites

- Remote server with Docker installed
- Network access to the remote server on your chosen port
- Atlassian Cloud or Server/Data Center instance
- API tokens or Personal Access Tokens for authentication

## Step 1: Server Preparation

### Connect to Remote Server

```bash
# SSH into your remote server
ssh user@your-remote-server-ip

# Update system packages
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# OR
sudo yum update -y  # CentOS/RHEL
```

### Install Docker (if not installed)

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Verify Docker installation
docker --version
```

## Step 2: Get MCP Atlassian

### Option A: Pull Docker Image (Recommended)

```bash
# Pull the latest MCP Atlassian Docker image
docker pull ghcr.io/sooperset/mcp-atlassian:latest

# Verify image is available
docker images | grep mcp-atlassian
```

### Option B: Clone Source Code (Advanced)

```bash
# Clone repository for custom builds
git clone https://github.com/sooperset/mcp-atlassian.git
cd mcp-atlassian
```

## Step 3: Configuration Setup

### Create Environment File

```bash
# Create directory for configuration
mkdir -p ~/mcp-atlassian-config
cd ~/mcp-atlassian-config

# Create environment file
nano .env
```

### Environment Configuration Examples

#### For Atlassian Cloud (API Token Authentication)

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
JIRA_PROJECTS_FILTER=PROJ,DEV,SUPPORT
CONFLUENCE_SPACES_FILTER=DEV,TEAM,DOC

# Optional: Enable specific tools only
# ENABLED_TOOLS=jira_search,jira_get_issue,jira_create_issue,confluence_search,confluence_get_page
```

#### For Atlassian Server/Data Center (Personal Access Token)

```bash
# Jira Configuration
JIRA_URL=https://jira.your-company.com
JIRA_PERSONAL_TOKEN=your_jira_personal_access_token
JIRA_SSL_VERIFY=false  # Only if using self-signed certificates

# Confluence Configuration
CONFLUENCE_URL=https://confluence.your-company.com
CONFLUENCE_PERSONAL_TOKEN=your_confluence_personal_access_token
CONFLUENCE_SSL_VERIFY=false  # Only if using self-signed certificates

# Server Configuration
MCP_VERBOSE=true
MCP_LOGGING_STDOUT=true
READ_ONLY_MODE=false
```

#### For OAuth 2.0 Authentication (Cloud Only)

```bash
# Base URLs
JIRA_URL=https://your-company.atlassian.net
CONFLUENCE_URL=https://your-company.atlassian.net/wiki

# OAuth Configuration (from Atlassian Developer Console)
ATLASSIAN_OAUTH_CLIENT_ID=your_oauth_app_client_id
ATLASSIAN_OAUTH_CLIENT_SECRET=your_oauth_app_client_secret
ATLASSIAN_OAUTH_REDIRECT_URI=http://localhost:8080/callback
ATLASSIAN_OAUTH_SCOPE=read:jira-work write:jira-work read:confluence-content.all write:confluence-content offline_access
ATLASSIAN_OAUTH_CLOUD_ID=your_cloud_id_from_setup_wizard

# Server Configuration
MCP_VERBOSE=true
MCP_LOGGING_STDOUT=true
READ_ONLY_MODE=false
```

## Step 4: Start MCP Server with HTTP Transport

### Single-User Mode (Server-Level Authentication)

#### Using Streamable-HTTP Transport (Recommended)

```bash
# Start server on port 9000 with streamable-HTTP transport
docker run --name mcp-atlassian-server \
  -d \
  -p 9000:9000 \
  --env-file ~/mcp-atlassian-config/.env \
  --restart unless-stopped \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 9000 -vv
```

#### Using SSE Transport (Alternative)

```bash
# Start server on port 9000 with SSE transport
docker run --name mcp-atlassian-server \
  -d \
  -p 9000:9000 \
  --env-file ~/mcp-atlassian-config/.env \
  --restart unless-stopped \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport sse --port 9000 -vv
```

### Multi-User Mode (Per-Request Authentication)

```bash
# Start server with minimal OAuth configuration for multi-user support
docker run --name mcp-atlassian-server \
  -d \
  -p 9000:9000 \
  -e ATLASSIAN_OAUTH_ENABLE=true \
  -e JIRA_URL=https://your-company.atlassian.net \
  -e CONFLUENCE_URL=https://your-company.atlassian.net/wiki \
  -e MCP_VERBOSE=true \
  -e MCP_LOGGING_STDOUT=true \
  --restart unless-stopped \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 9000 -vv
```

## Step 5: Network Configuration

### Configure Firewall

```bash
# Allow traffic on port 9000 (Ubuntu/Debian)
sudo ufw allow 9000
sudo ufw status

# Or for CentOS/RHEL
sudo firewall-cmd --permanent --add-port=9000/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports
```

### Verify Server is Running

```bash
# Check if container is running
docker ps | grep mcp-atlassian

# Check server health locally
curl http://localhost:9000/healthz

# View server logs
docker logs mcp-atlassian-server

# Follow logs in real-time
docker logs -f mcp-atlassian-server
```

## Step 6: Test HTTP Access

### Health Check from External Machine

```bash
# Test server health from any machine
curl http://your-remote-server-ip:9000/healthz

# Expected response:
# {"status": "healthy", "timestamp": "2025-01-25T10:27:00Z"}
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

#### Execute Jira Search

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

#### Execute Confluence Search

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

#### Create Jira Issue

```bash
# Create a new Jira issue
curl -X POST http://your-remote-server-ip:9000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "jira_create_issue",
      "arguments": {
        "project_key": "PROJ",
        "summary": "Test issue created via HTTP API",
        "issue_type": "Task",
        "description": "This issue was created using the remote MCP server"
      }
    }
  }'
```

## Step 7: Client Integration Examples

### Python Client

```python
import requests
import json

class MCPAtlassianClient:
    def __init__(self, server_url, auth_token=None, cloud_id=None):
        self.server_url = server_url
        self.session = requests.Session()
        self.request_id = 1
        
        # Set authentication headers for multi-user mode
        if auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
        if cloud_id:
            self.session.headers.update({
                'X-Atlassian-Cloud-Id': cloud_id
            })
    
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

# Usage examples
# Single-user mode (server-level auth)
client = MCPAtlassianClient("http://your-remote-server:9000")

# Multi-user mode (per-request auth)
# client = MCPAtlassianClient(
#     "http://your-remote-server:9000",
#     auth_token="user_oauth_token",
#     cloud_id="user_cloud_id"
# )

# List available tools
tools = client.list_tools()
print("Available tools:", json.dumps(tools, indent=2))

# Search Jira issues
jira_results = client.call_tool("jira_search", {
    "jql": "project = PROJ AND status = \"To Do\"",
    "limit": 5
})
print("Jira search results:", json.dumps(jira_results, indent=2))

# Create Confluence page
confluence_result = client.call_tool("confluence_create_page", {
    "space_key": "DEV",
    "title": "API Test Page",
    "content": "# Test Page\n\nThis page was created via the remote MCP API."
})
print("Created page:", json.dumps(confluence_result, indent=2))
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');

class MCPAtlassianClient {
    constructor(serverUrl, authToken = null, cloudId = null) {
        this.serverUrl = serverUrl;
        this.requestId = 1;
        
        // Set up default headers
        this.headers = { 'Content-Type': 'application/json' };
        
        // Add authentication headers for multi-user mode
        if (authToken) {
            this.headers['Authorization'] = `Bearer ${authToken}`;
        }
        if (cloudId) {
            this.headers['X-Atlassian-Cloud-Id'] = cloudId;
        }
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
            headers: this.headers
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
            headers: this.headers
        });
        return response.data;
    }
}

// Usage example
async function main() {
    // Single-user mode
    const client = new MCPAtlassianClient('http://your-remote-server:9000');
    
    // Multi-user mode example:
    // const client = new MCPAtlassianClient(
    //     'http://your-remote-server:9000',
    //     'user_oauth_token',
    //     'user_cloud_id'
    // );
    
    try {
        // List tools
        const tools = await client.listTools();
        console.log('Available tools:', JSON.stringify(tools, null, 2));
        
        // Get Jira issue
        const issue = await client.callTool('jira_get_issue', {
            issue_key: 'PROJ-123'
        });
        console.log('Issue details:', JSON.stringify(issue, null, 2));
        
        // Search Confluence
        const pages = await client.callTool('confluence_search', {
            query: 'meeting notes',
            limit: 5
        });
        console.log('Confluence pages:', JSON.stringify(pages, null, 2));
        
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

main();
```

## Step 8: IDE Integration (Remote Server)

### Configure IDE to Use Remote Server

#### For Cursor/Claude Desktop (Streamable-HTTP)

```json
{
  "mcpServers": {
    "mcp-atlassian-remote": {
      "url": "http://your-remote-server:9000/mcp"
    }
  }
}
```

#### For SSE Transport

```json
{
  "mcpServers": {
    "mcp-atlassian-remote": {
      "url": "http://your-remote-server:9000/sse"
    }
  }
}
```

#### With User Authentication (Multi-User Mode)

```json
{
  "mcpServers": {
    "mcp-atlassian-remote": {
      "url": "http://your-remote-server:9000/mcp",
      "headers": {
        "Authorization": "Bearer your_oauth_token",
        "X-Atlassian-Cloud-Id": "your_cloud_id"
      }
    }
  }
}
```

## Step 9: Security Considerations

### Production Setup

#### Use HTTPS with Reverse Proxy (Nginx Example)

```nginx
server {
    listen 443 ssl;
    server_name mcp.your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support for SSE
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### Restrict Access by IP

```bash
# Using UFW (Ubuntu/Debian)
sudo ufw allow from 192.168.1.0/24 to any port 9000
sudo ufw deny 9000

# Using iptables
sudo iptables -A INPUT -p tcp --dport 9000 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 9000 -j DROP
```

#### Environment Security

```bash
# Secure environment file
chmod 600 ~/mcp-atlassian-config/.env
chown $USER:$USER ~/mcp-atlassian-config/.env

# Use Docker secrets for production
docker swarm init
echo "your_api_token" | docker secret create jira_token -
echo "your_confluence_token" | docker secret create confluence_token -
```

## Step 10: Monitoring and Maintenance

### Health Monitoring

```bash
# Create health check script
cat > ~/check_mcp_health.sh << 'EOF'
#!/bin/bash
HEALTH_URL="http://localhost:9000/healthz"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "$(date): MCP server is healthy"
else
    echo "$(date): MCP server is unhealthy (HTTP $RESPONSE)"
    # Restart container
    docker restart mcp-atlassian-server
fi
EOF

chmod +x ~/check_mcp_health.sh

# Add to crontab for regular checks
(crontab -l 2>/dev/null; echo "*/5 * * * * ~/check_mcp_health.sh >> ~/mcp_health.log") | crontab -
```

### Log Management

```bash
# View recent logs
docker logs --tail 100 mcp-atlassian-server

# Follow logs with timestamps
docker logs -f --timestamps mcp-atlassian-server

# Rotate logs to prevent disk space issues
docker run --log-driver json-file --log-opt max-size=10m --log-opt max-file=3 \
  --name mcp-atlassian-server \
  -d -p 9000:9000 \
  --env-file ~/mcp-atlassian-config/.env \
  --restart unless-stopped \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 9000 -vv
```

### Updates

```bash
# Update to latest version
docker pull ghcr.io/sooperset/mcp-atlassian:latest
docker stop mcp-atlassian-server
docker rm mcp-atlassian-server

# Restart with new image (use your original run command)
docker run --name mcp-atlassian-server \
  -d -p 9000:9000 \
  --env-file ~/mcp-atlassian-config/.env \
  --restart unless-stopped \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 9000 -vv
```

## Troubleshooting

### Common Issues

#### Connection Refused

```bash
# Check if server is running
docker ps | grep mcp-atlassian

# Check server logs
docker logs mcp-atlassian-server

# Verify port is open
netstat -tlnp | grep 9000
ss -tlnp | grep 9000
```

#### Authentication Errors

```bash
# Verify environment variables
docker exec mcp-atlassian-server env | grep -E "(JIRA|CONFLUENCE)"

# Test authentication manually
curl -u "username:api_token" https://your-company.atlassian.net/rest/api/3/myself

# Check server logs for auth errors
docker logs mcp-atlassian-server | grep -i auth
```

#### Firewall Issues

```bash
# Check firewall status
sudo ufw status
sudo firewall-cmd --list-ports

# Test local connectivity
curl http://localhost:9000/healthz

# Test external connectivity from another machine
curl http://your-remote-server:9000/healthz
```

#### Performance Issues

```bash
# Check container resource usage
docker stats mcp-atlassian-server

# Check system resources
htop
df -h
free -h

# Enable debug logging
docker logs mcp-atlassian-server | grep -E "(ERROR|WARN)"
```

### Debug Mode

```bash
# Run with maximum verbosity
docker stop mcp-atlassian-server
docker rm mcp-atlassian-server

docker run --name mcp-atlassian-debug \
  -p 9000:9000 \
  --env-file ~/mcp-atlassian-config/.env \
  -e MCP_VERY_VERBOSE=true \
  -e MCP_LOGGING_STDOUT=true \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 9000 -vv

# Monitor logs in real-time
docker logs -f mcp-atlassian-debug
```

## Summary

You now have a fully functional remote MCP Atlassian server accessible via HTTP from anywhere. The server provides:

- **All 42 MCP tools** (26 Jira + 16 Confluence tools)
- **Multiple authentication methods** (API tokens, PAT, OAuth 2.0)
- **Single-user and multi-user support**
- **HTTP transport** (streamable-HTTP or SSE)
- **Production-ready security** options

### Key Endpoints

- **Health check**: `GET http://your-server:9000/healthz`
- **MCP protocol**: `POST http://your-server:9000/mcp`
- **SSE transport**: `GET http://your-server:9000/sse` (if using SSE)

### Next Steps

1. **Test all functionality** with your specific Atlassian instance
2. **Set up HTTPS** for production use
3. **Configure monitoring** and alerting
4. **Integrate with your applications** using the provided client examples
5. **Set up backup and disaster recovery** procedures

The server is now ready for integration with AI assistants, custom applications, or any HTTP client that needs to interact with Atlassian products remotely.
