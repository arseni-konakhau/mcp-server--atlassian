# MCP Atlassian Deployment Guide

This comprehensive guide covers deploying MCP Atlassian server on remote machines with HTTP access, supporting both Docker and non-Docker approaches with simple to advanced configurations.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Deployment Methods](#deployment-methods)
- [Client Integration](#client-integration)
- [Production Setup](#production-setup)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

## Overview

This deployment enables you to:
- **Deploy MCP Atlassian server** on any remote machine (VPS, cloud instance, etc.)
- **Access all 42 MCP tools** (26 Jira + 16 Confluence) via HTTP from anywhere
- **Support multiple authentication methods** (API tokens, PAT, OAuth 2.0)
- **Choose deployment approach** (Docker for consistency, direct installation for control)
- **Scale from simple testing** to production-ready enterprise deployment

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+) or macOS
- **Memory**: Minimum 512MB RAM, recommended 1GB+
- **Storage**: 2GB free space for dependencies and logs
- **Network**: Outbound HTTPS access to Atlassian APIs
- **Ports**: One available port for HTTP access (default: 3334)

### Required Access
- **Remote server access** via SSH
- **Atlassian instance** (Cloud or Server/Data Center)
- **Authentication credentials** (API tokens, Personal Access Tokens, or OAuth setup)

## Quick Start

### 1. Connect to Remote Server
```bash
# SSH into your remote server
ssh user@your-remote-server-ip

# Update system packages
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# OR
sudo yum update -y  # CentOS/RHEL
```

### 2. Choose Your Deployment Method

#### Option A: Docker (Recommended for Production)
```bash
# Install Docker if needed
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Pull MCP Atlassian image
docker pull ghcr.io/sooperset/mcp-atlassian:latest
```

#### Option B: Direct Installation (Recommended for Development)
```bash
# Install Python and UV
sudo apt install -y python3 python3-pip python3-venv curl git  # Ubuntu/Debian
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Clone repository
git clone https://github.com/sooperset/mcp-atlassian.git
cd mcp-atlassian
uv sync --frozen --all-extras --dev
```

### 3. Basic Configuration
```bash
# Create environment file
nano .env
```

**Minimal configuration for Atlassian Cloud:**
```bash
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_API_TOKEN=your_jira_api_token

CONFLUENCE_URL=https://your-company.atlassian.net/wiki
CONFLUENCE_USERNAME=your.email@company.com
CONFLUENCE_API_TOKEN=your_confluence_api_token

READ_ONLY_MODE=false
MCP_VERBOSE=true
```

### 4. Start Server (Simplest)
```bash
# Docker approach
docker run -d -p 3334:3334 --env-file .env --name mcp-atlassian \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 3334 --verbose

# Direct installation approach
uv run mcp-atlassian --transport streamable-http --port 3334 --verbose
```

### 5. Test Access
```bash
# Health check
curl http://your-server-ip:3334/healthz

# List tools
curl -X POST http://your-server-ip:3334/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

**🎉 That's it! Your MCP server is running and accessible via HTTP.**

## Configuration

### 1. Basic Configuration Options

#### Atlassian Cloud (API Token)
```bash
# .env file - Most common setup
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_API_TOKEN=your_jira_api_token

CONFLUENCE_URL=https://your-company.atlassian.net/wiki
CONFLUENCE_USERNAME=your.email@company.com
CONFLUENCE_API_TOKEN=your_confluence_api_token

# Server behavior
READ_ONLY_MODE=false
MCP_VERBOSE=true
MCP_LOGGING_STDOUT=true
```

#### Atlassian Server/Data Center (Personal Access Token)
```bash
# .env file - On-premise setup
JIRA_URL=https://jira.your-company.com
JIRA_PERSONAL_TOKEN=your_jira_personal_access_token
JIRA_SSL_VERIFY=true

CONFLUENCE_URL=https://confluence.your-company.com
CONFLUENCE_PERSONAL_TOKEN=your_confluence_personal_access_token
CONFLUENCE_SSL_VERIFY=true

# Server behavior
READ_ONLY_MODE=false
MCP_VERBOSE=true
```

### 2. Advanced Configuration Options

#### Content Filtering
```bash
# Limit access to specific projects and spaces
JIRA_PROJECTS_FILTER=PROJ,DEV,SUPPORT,TEAM
CONFLUENCE_SPACES_FILTER=DEV,TEAM,DOC,WIKI

# Enable only specific tools (comma-separated)
ENABLED_TOOLS=jira_search,jira_get_issue,jira_create_issue,confluence_search,confluence_get_page,confluence_create_page

# Tool access control
JIRA_TOOLS_ENABLED=true
CONFLUENCE_TOOLS_ENABLED=true
```

#### OAuth 2.0 Configuration (Cloud Only)
```bash
# OAuth setup (from Atlassian Developer Console)
JIRA_URL=https://your-company.atlassian.net
CONFLUENCE_URL=https://your-company.atlassian.net/wiki

ATLASSIAN_OAUTH_CLIENT_ID=your_oauth_app_client_id
ATLASSIAN_OAUTH_CLIENT_SECRET=your_oauth_app_client_secret
ATLASSIAN_OAUTH_REDIRECT_URI=http://localhost:8080/callback
ATLASSIAN_OAUTH_SCOPE=read:jira-work write:jira-work read:confluence-content.all write:confluence-content offline_access
ATLASSIAN_OAUTH_CLOUD_ID=your_cloud_id

# Multi-user mode (leave tokens empty for per-request auth)
ATLASSIAN_OAUTH_ACCESS_TOKEN=
ATLASSIAN_OAUTH_REFRESH_TOKEN=
```

#### Network & Proxy Configuration
```bash
# Corporate proxy settings
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
NO_PROXY=localhost,127.0.0.1,.company.com

# Custom headers for corporate environments
JIRA_CUSTOM_HEADERS=X-Forwarded-User=service-account,X-Company-Service=mcp-atlassian
CONFLUENCE_CUSTOM_HEADERS=X-ALB-Token=secret-token,X-Request-ID=mcp-server

# SSL configuration for self-signed certificates
JIRA_SSL_VERIFY=false
CONFLUENCE_SSL_VERIFY=false
REQUESTS_CA_BUNDLE=/path/to/custom/ca-bundle.crt
```

#### Performance & Logging Configuration
```bash
# Logging levels
MCP_VERBOSE=true          # Standard verbose logging
MCP_VERY_VERBOSE=true     # Maximum verbosity (debug mode)
MCP_LOGGING_STDOUT=true   # Log to stdout (useful for containers)

# Performance tuning
JIRA_REQUEST_TIMEOUT=30
CONFLUENCE_REQUEST_TIMEOUT=30
MAX_CONCURRENT_REQUESTS=10

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

### 3. Multi-User Configuration
```bash
# Enable multi-user mode with per-request authentication
ATLASSIAN_OAUTH_ENABLE=true
JIRA_URL=https://your-company.atlassian.net
CONFLUENCE_URL=https://your-company.atlassian.net/wiki

# Leave these empty for per-request tokens
ATLASSIAN_OAUTH_ACCESS_TOKEN=
ATLASSIAN_OAUTH_CLOUD_ID=

# Optional: Default fallback credentials
JIRA_USERNAME=fallback@company.com
JIRA_API_TOKEN=fallback_token
```

### 4. Security Configuration
```bash
# Access control
ALLOWED_ORIGINS=https://your-app.com,https://another-app.com
CORS_ENABLED=true

# API security
API_KEY_REQUIRED=true
API_KEY=your-secret-api-key

# Request validation
VALIDATE_SSL_CERTIFICATES=true
REQUIRE_HTTPS_UPSTREAM=true
```

## Deployment Methods

### Method 1: Docker Deployment

#### Simple Docker Run (Development)
```bash
# Basic single-user setup
docker run -d \
  --name mcp-atlassian \
  -p 3334:3334 \
  --env-file .env \
  --restart unless-stopped \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 3334 --verbose
```

#### Docker Compose (Recommended)
```yaml
# docker-compose.yml
version: '3.8'

services:
  mcp-atlassian:
    image: ghcr.io/sooperset/mcp-atlassian:latest
    container_name: mcp-atlassian
    ports:
      - "3334:3334"
    env_file:
      - .env
    command: ["--transport", "streamable-http", "--port", "3334", "--verbose"]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3334/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

```bash
# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop and remove
docker-compose down
```

#### Docker with Volume Mounts
```bash
# Create directories for persistent data
mkdir -p ~/mcp-atlassian/{config,logs,data}

# Run with volume mounts
docker run -d \
  --name mcp-atlassian \
  -p 3334:3334 \
  -v ~/mcp-atlassian/config:/app/config \
  -v ~/mcp-atlassian/logs:/app/logs \
  -v ~/mcp-atlassian/data:/app/data \
  --env-file ~/mcp-atlassian/config/.env \
  --restart unless-stopped \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 3334 --verbose
```

### Method 2: Direct Installation Deployment

#### Simple Direct Run (Development)
```bash
# Clone and setup
git clone https://github.com/sooperset/mcp-atlassian.git
cd mcp-atlassian
uv sync --frozen --all-extras --dev

# Run directly (foreground)
uv run mcp-atlassian --transport streamable-http --port 3334 --verbose
```

#### Background Process (Simple Production)
```bash
# Run in background with nohup
nohup uv run mcp-atlassian --transport streamable-http --port 3334 --verbose > mcp.log 2>&1 &

# Check if running
ps aux | grep mcp-atlassian

# View logs
tail -f mcp.log

# Stop the server
pkill -f mcp-atlassian
```

#### Systemd Service (Production)
```bash
# Create service user
sudo useradd -r -s /bin/false mcp-user

# Setup directory
sudo mkdir -p /opt/mcp-atlassian
sudo cp -r . /opt/mcp-atlassian/
sudo chown -R mcp-user:mcp-user /opt/mcp-atlassian

# Create systemd service
sudo nano /etc/systemd/system/mcp-atlassian.service
```

```ini
[Unit]
Description=MCP Atlassian Server
After=network.target
Wants=network.target

[Service]
Type=simple
User=mcp-user
Group=mcp-user
WorkingDirectory=/opt/mcp-atlassian
Environment=PATH=/opt/mcp-atlassian/.venv/bin
ExecStart=/opt/mcp-atlassian/.venv/bin/uv run mcp-atlassian --transport streamable-http --port 3334 --verbose
EnvironmentFile=/opt/mcp-atlassian/.env
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=mcp-atlassian

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/mcp-atlassian/logs

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable mcp-atlassian
sudo systemctl start mcp-atlassian

# Check status
sudo systemctl status mcp-atlassian
sudo journalctl -u mcp-atlassian -f
```

### Method 3: Advanced Deployment Options

#### Screen Session (Development)
```bash
# Install screen if needed
sudo apt install screen  # Ubuntu/Debian

# Create screen session
screen -S mcp-atlassian

# Run server inside screen
uv run mcp-atlassian --transport streamable-http --port 3334 --verbose

# Detach: Ctrl+A, then D
# Reattach: screen -r mcp-atlassian
# List sessions: screen -ls
```

#### PM2 Process Manager (Node.js Environments)
```bash
# Install PM2
npm install -g pm2

# Create PM2 ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'mcp-atlassian',
    script: 'uv',
    args: 'run mcp-atlassian --transport streamable-http --port 3334 --verbose',
    cwd: '/path/to/mcp-atlassian',
    env_file: '.env',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup  # Follow instructions
```

## Client Integration

### HTTP API Testing

#### Basic Health Check
```bash
# Test server health
curl http://your-server:3334/healthz

# Expected response:
# {"status": "healthy", "timestamp": "2025-01-25T10:27:00Z"}
```

#### List Available Tools
```bash
curl -X POST http://your-server:3334/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

#### Execute Tools
```bash
# Search Jira issues
curl -X POST http://your-server:3334/mcp \
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

# Create Jira issue
curl -X POST http://your-server:3334/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "jira_create_issue",
      "arguments": {
        "project_key": "PROJ",
        "summary": "Test issue via HTTP API",
        "issue_type": "Task",
        "description": "Created using remote MCP server"
      }
    }
  }'

# Search Confluence pages
curl -X POST http://your-server:3334/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
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

#### Multi-User Authentication
```bash
# Call with user-specific OAuth token
curl -X POST http://your-server:3334/mcp \
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

### Python Client

```python
import httpx
import json
import asyncio

class MCPAtlassianClient:
    def __init__(self, base_url: str, auth_token: str = None, cloud_id: str = None):
        self.base_url = base_url.rstrip('/')
        self.headers = {'Content-Type': 'application/json'}
        self.request_id = 1
        
        # Multi-user authentication
        if auth_token:
            self.headers['Authorization'] = f'Bearer {auth_token}'
        if cloud_id:
            self.headers['X-Atlassian-Cloud-Id'] = cloud_id
    
    async def call_tool(self, tool_name: str, arguments: dict):
        """Call an MCP tool"""
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
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def list_tools(self):
        """List available tools"""
        payload = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/list"
        }
        self.request_id += 1
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def health_check(self):
        """Check server health"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/healthz")
            response.raise_for_status()
            return response.json()

# Usage examples
async def main():
    # Single-user mode (server-level auth)
    client = MCPAtlassianClient("http://your-server:3334")
    
    # Multi-user mode (per-request auth)
    # client = MCPAtlassianClient(
    #     "http://your-server:3334",
    #     auth_token="user_oauth_token",
    #     cloud_id="user_cloud_id"
    # )
    
    # Health check
    health = await client.health_check()
    print("Server health:", health)
    
    # List available tools
    tools = await client.list_tools()
    print(f"Available tools: {len(tools.get('result', {}).get('tools', []))}")
    
    # Search Jira issues
    jira_results = await client.call_tool("jira_search", {
        "jql": "project = PROJ AND status = 'In Progress'",
        "limit": 5
    })
    print("Jira search results:", json.dumps(jira_results, indent=2))
    
    # Create Confluence page
    confluence_result = await client.call_tool("confluence_create_page", {
        "space_key": "DEV",
        "title": "API Test Page",
        "content": "# Test Page\n\nCreated via remote MCP API."
    })
    print("Created page:", json.dumps(confluence_result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');

class MCPAtlassianClient {
    constructor(baseUrl, authToken = null, cloudId = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.headers = { 'Content-Type': 'application/json' };
        this.requestId = 1;
        
        // Multi-user authentication
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

        try {
            const response = await axios.post(
                `${this.baseUrl}/mcp`,
                payload,
                { 
                    headers: this.headers,
                    timeout: 30000
                }
            );
            return response.data;
        } catch (error) {
            console.error('Tool call failed:', error.response?.data || error.message);
            throw error;
        }
    }

    async listTools() {
        const payload = {
            jsonrpc: "2.0",
            id: this.requestId++,
            method: "tools/list"
        };

        const response = await axios.post(
            `${this.baseUrl}/mcp`,
            payload,
            { headers: this.headers }
        );
        return response.data;
    }

    async healthCheck() {
        const response = await axios.get(`${this.baseUrl}/healthz`);
        return response.data;
    }
}

// Usage example
async function main() {
    // Single-user mode
    const client = new MCPAtlassianClient('http://your-server:3334');
    
    // Multi-user mode example:
    // const client = new MCPAtlassianClient(
    //     'http://your-server:3334',
    //     'user_oauth_token',
    //     'user_cloud_id'
    // );

    try {
        // Health check
        const health = await client.healthCheck();
        console.log('Server health:', health);

        // List tools
        const tools = await client.listTools();
        console.log('Available tools:', tools.result.tools.length);

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
        console.error('Error:', error.message);
    }
}

main();
```

### IDE Integration

#### Cursor/Claude Desktop Configuration

**Single-user mode:**
```json
{
  "mcpServers": {
    "mcp-atlassian-remote": {
      "url": "http://your-server:3334/mcp"
    }
  }
}
```

**Multi-user mode:**
```json
{
  "mcpServers": {
    "mcp-atlassian-remote": {
      "url": "http://your-server:3334/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_OAUTH_TOKEN",
        "X-Atlassian-Cloud-Id": "YOUR_CLOUD_ID"
      }
    }
  }
}
```

**SSE transport:**
```json
{
  "mcpServers": {
    "mcp-atlassian-remote": {
      "url": "http://your-server:3334/sse"
    }
  }
}
```

## Production Setup

### HTTPS with Nginx Reverse Proxy

#### Install Nginx
```bash
# Ubuntu/Debian
sudo apt install nginx certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install nginx certbot python3-certbot-nginx
```

#### Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/mcp-atlassian
```

```nginx
# HTTP redirect to HTTPS
server {
    listen 80;
    server_name mcp.your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name mcp.your-domain.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/mcp.your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mcp.your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    # Proxy configuration
    location / {
        proxy_pass http://127.0.0.1:3334;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Health check endpoint (no rate limiting)
    location /healthz {
        proxy_pass http://127.0.0.1:3334/healthz;
        access_log off;
    }

    # Optional: IP-based access control
    # location / {
    #     allow 192.168.1.0/24;
    #     allow 10.0.0.0/8;
    #     deny all;
    #     proxy_pass http://127.0.0.1:3334;
    # }
}
```

#### Enable Configuration and SSL
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/mcp-atlassian /etc/nginx/sites-enabled/
sudo nginx -t

# Get SSL certificate
sudo certbot --nginx -d mcp.your-domain.com

# Reload Nginx
sudo systemctl reload nginx
```

### Firewall Configuration

#### UFW (Ubuntu/Debian)
```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Block direct access to MCP port
sudo ufw deny 3334/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

#### Firewalld (CentOS/RHEL)
```bash
# Allow services
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# Block MCP port from external access
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" port protocol="tcp" port="3334" reject'

# Reload firewall
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

### Security Hardening

#### Environment Security
```bash
# Secure environment file
chmod 600 .env
chown mcp-user:mcp-user .env  # If using systemd

# Create logs directory with proper permissions
mkdir -p logs
chmod 755 logs
chown mcp-user:mcp-user logs  # If using systemd
```

#### Docker Security
```bash
# Run container with security options
docker run -d \
  --name mcp-atlassian \
  -p 127.0.0.1:3334:3334 \  # Bind to localhost only
  --env-file .env \
  --user 1000:1000 \  # Run as non-root user
  --read-only \  # Read-only filesystem
  --tmpfs /tmp \  # Temporary filesystem
  --no-new-privileges \  # Prevent privilege escalation
  --restart unless-stopped \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 3334 --verbose
```

## Monitoring & Maintenance

### Health Monitoring

#### Health Check Script
```bash
#!/bin/bash
# /opt/scripts/mcp-health-check.sh

HEALTH_URL="http://localhost:3334/healthz"
LOG_FILE="/var/log/mcp-atlassian-health.log"

response=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" --max-time 10)

if [ "$response" = "200" ]; then
    echo "$(date): MCP Atlassian is healthy" >> "$LOG_FILE"
    exit 0
else
    echo "$(date): MCP Atlassian health check failed (HTTP $response)" >> "$LOG_FILE"
    # Optional: restart service
    # sudo systemctl restart mcp-atlassian
    # docker restart mcp-atlassian
    exit 1
fi
```

```bash
# Make script executable
chmod +x /opt/scripts/mcp-health-check.sh

# Add to crontab for regular checks
crontab -e
# Add line: */5 * * * * /opt/scripts/mcp-health-check.sh
```

#### Advanced Monitoring with Prometheus
```bash
# Add monitoring endpoints to .env
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090

# Expose metrics endpoint
curl http://localhost:9090/metrics
```

### Log Management

#### Logrotate Configuration
```bash
sudo nano /etc/logrotate.d/mcp-atlassian
```

```
/opt/mcp-atlassian/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 mcp-user mcp-user
    postrotate
        systemctl reload mcp-atlassian
    endscript
}

/var/log/mcp-atlassian-health.log {
    weekly
    missingok
    rotate 12
    compress
    delaycompress
    notifempty
    create 644 root root
}
```

#### Docker Log Management
```bash
# Configure Docker logging
docker run -d \
  --name mcp-atlassian \
  -p 3334:3334 \
  --env-file .env \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  --restart unless-stopped \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 3334 --verbose

# View logs with timestamps
docker logs -f --timestamps mcp-atlassian

# Export logs
docker logs mcp-atlassian > mcp-atlassian.log
```

### Performance Monitoring

#### System Resource Monitoring
```bash
# Monitor CPU and memory usage
ps aux | grep mcp-atlassian
top -p $(pgrep -f mcp-atlassian)

# Monitor network connections
netstat -tulpn | grep :3334
ss -tulpn | grep :3334

# Monitor disk usage
df -h
du -sh /opt/mcp-atlassian/logs/
```

#### Application Metrics
```bash
# Response time testing
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:3334/healthz

# Create curl-format.txt:
cat > curl-format.txt << 'EOF'
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
EOF
```

### Updates and Maintenance

#### Update Procedure (Docker)
```bash
#!/bin/bash
# /opt/scripts/update-docker.sh

set -e

echo "Starting MCP Atlassian Docker update..."

# Pull latest image
docker pull ghcr.io/sooperset/mcp-atlassian:latest

# Stop current container
docker stop mcp-atlassian
docker rm mcp-atlassian

# Start new container
docker run -d \
  --name mcp-atlassian \
  -p 3334:3334 \
  --env-file .env \
  --restart unless-stopped \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 3334 --verbose

# Wait and verify health
sleep 10
curl -f http://localhost:3334/healthz || {
    echo "Health check failed after update"
    exit 1
}

echo "Update completed successfully"
```

#### Update Procedure (Direct Installation)
```bash
#!/bin/bash
# /opt/scripts/update-direct.sh

set -e

echo "Starting MCP Atlassian direct installation update..."

# Backup current installation
sudo cp -r /opt/mcp-atlassian /opt/mcp-atlassian.backup.$(date +%Y%m%d_%H%M%S)

# Stop service
sudo systemctl stop mcp-atlassian

# Update code
cd /opt/mcp-atlassian
sudo -u mcp-user git pull origin main

# Update dependencies
sudo -u mcp-user uv sync --frozen --all-extras

# Test configuration
sudo -u mcp-user uv run python3 simple_test.py --verbose

# Start service
sudo systemctl start mcp-atlassian

# Verify health
sleep 10
curl -f http://localhost:3334/healthz || {
    echo "Health check failed, rolling back..."
    sudo systemctl stop mcp-atlassian
    sudo rm -rf /opt/mcp-atlassian
    sudo mv /opt/mcp-atlassian.backup.* /opt/mcp-atlassian
    sudo systemctl start mcp-atlassian
    exit 1
}

echo "Update completed successfully"
```

#### Backup Strategy
```bash
#!/bin/bash
# /opt/scripts/backup.sh

BACKUP_DIR="/opt/backups/mcp-atlassian"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup configuration and logs
tar -czf "$BACKUP_DIR/mcp-atlassian-$DATE.tar.gz" \
    -C /opt/mcp-atlassian \
    .env \
    logs/ \
    --exclude='logs/*.log.*'

# Keep only last 30 days of backups
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/mcp-atlassian-$DATE.tar.gz"
```

## Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Docker troubleshooting
docker ps -a | grep mcp-atlassian
docker logs mcp-atlassian
docker inspect mcp-atlassian

# Direct installation troubleshooting
sudo systemctl status mcp-atlassian
sudo journalctl -u mcp-atlassian -f
uv run python3 simple_test.py --verbose

# Common fixes:
# - Verify .env file permissions and content
# - Check Python path in service file
# - Ensure all dependencies are installed
# - Verify network connectivity to Atlassian APIs
```

#### 2. Authentication Failures
```bash
# Test API connectivity
curl -u "email@domain.com:api_token" \
  "https://your-domain.atlassian.net/rest/api/3/myself"

# Test OAuth token
curl -H "Authorization: Bearer oauth_token" \
  "https://api.atlassian.com/oauth/token/accessible-resources"

# Check token permissions
# - Verify API token is not expired
# - Ensure user has proper Jira/Confluence permissions
# - Check OAuth scope configuration
```

#### 3. Network Connectivity Issues
```bash
# Test outbound connectivity
curl -I https://your-domain.atlassian.net

# Check proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Test with proxy
curl --proxy $HTTP_PROXY -I https://your-domain.atlassian.net

# Check firewall
sudo ufw status
sudo firewall-cmd --list-all
```

#### 4. Performance Issues
```bash
# Check system resources
free -h
df -h
top

# Check network latency
ping your-domain.atlassian.net
traceroute your-domain.atlassian.net

# Monitor application performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:3334/healthz

# Check for memory leaks
docker stats mcp-atlassian
ps aux --sort=-%mem | head
```

#### 5. SSL/TLS Issues
```bash
# Test SSL connectivity
openssl s_client -connect your-domain.atlassian.net:443

# Check certificate validity
curl -vI https://your-domain.atlassian.net

# Disable SSL verification (temporary)
# Add to .env: JIRA_SSL_VERIFY=false
```

### Debug Mode

#### Enable Maximum Verbosity
```bash
# Docker debug mode
docker run -d \
  --name mcp-atlassian-debug \
  -p 3334:3334 \
  --env-file .env \
  -e MCP_VERY_VERBOSE=true \
  -e MCP_LOGGING_STDOUT=true \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 3334 --very-verbose

# Direct installation debug mode
MCP_VERY_VERBOSE=true uv run mcp-atlassian --transport streamable-http --port 3334 --very-verbose
```

#### Component Testing
```bash
# Test individual components
uv run python3 manual_test_debug.py --mode api-only
uv run python3 manual_test_debug.py --mode mcp-only
uv run python3 manual_test_debug.py --mode http-server

# Test specific tools
curl -X POST http://localhost:3334/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "jira_get_user_profile",
      "arguments": {
        "user_identifier": "currentUser()"
      }
    }
  }'
```

### Getting Help

1. **Check Logs**: Always start with service logs and application logs
2. **Test Configuration**: Use the provided test scripts to validate setup
3. **Network Diagnostics**: Verify connectivity to Atlassian APIs
4. **GitHub Issues**: Report bugs and get community support at https://github.com/sooperset/mcp-atlassian/issues
5. **Documentation**: Refer to the main README and Confluence guides

### Performance Optimization

#### System Tuning
```bash
# Increase file descriptor limits
echo "mcp-user soft nofile 65536" >> /etc/security/limits.conf
echo "mcp-user hard nofile 65536" >> /etc/security/limits.conf

# Optimize network settings
echo "net.core.somaxconn = 65536" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65536" >> /etc/sysctl.conf
sysctl -p
```

#### Application Tuning
```bash
# Adjust performance settings in .env
JIRA_REQUEST_TIMEOUT=60
CONFLUENCE_REQUEST_TIMEOUT=60
MAX_CONCURRENT_REQUESTS=20
RATE_LIMIT_REQUESTS_PER_MINUTE=120

# Docker resource limits
docker run -d \
  --name mcp-atlassian \
  -p 3334:3334 \
  --env-file .env \
  --memory=1g \
  --cpus=2 \
  --restart unless-stopped \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 3334 --verbose
```

## Summary

This comprehensive deployment guide provides everything needed to deploy MCP Atlassian server on remote machines with HTTP access. The guide covers:

### **Key Features**
- **42 MCP tools** (26 Jira + 16 Confluence tools)
- **Multiple authentication methods** (API tokens, PAT, OAuth 2.0)
- **Flexible deployment options** (Docker and direct installation)
- **Simple to advanced configurations** with progressive complexity
- **Production-ready security** and monitoring

### **Deployment Methods**
1. **Docker** - Recommended for production consistency
2. **Direct Installation** - Recommended for development and debugging
3. **Advanced Options** - Screen, PM2, and other specialized approaches

### **Key Endpoints**
- **Health check**: `GET http://your-server:3334/healthz`
- **MCP protocol**: `POST http://your-server:3334/mcp`
- **SSE transport**: `GET http://your-server:3334/sse` (if using SSE)

### **Next Steps**
1. **Choose deployment method** based on your needs (Docker vs. direct)
2. **Configure authentication** for your Atlassian instance
3. **Test functionality** with the provided examples
4. **Set up HTTPS** for production use
5. **Configure monitoring** and maintenance procedures
6. **Integrate with your applications** using the client examples

The server is now ready for integration with AI assistants, custom applications, or any HTTP client that needs to interact with Atlassian products remotely.
