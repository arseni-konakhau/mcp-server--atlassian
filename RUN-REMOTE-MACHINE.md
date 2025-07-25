# Remote Machine Deployment Guide - MCP Atlassian

This guide covers deploying MCP Atlassian server on a remote machine with HTTP access. This approach provides direct control over the Python environment and dependencies, making it ideal for development, debugging, and production scenarios where you need full system integration.

> **Note**: For Docker-based deployment, see [RUN-REMOTE-MACHINE-DOCKER.md](./RUN-REMOTE-MACHINE-DOCKER.md)

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Deployment Options](#deployment-options)
- [Client Integration](#client-integration)
- [Production Setup](#production-setup)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+) or macOS
- **Python**: 3.10 or higher
- **Memory**: Minimum 512MB RAM, recommended 1GB+
- **Storage**: 2GB free space for dependencies and logs
- **Network**: Outbound HTTPS access to Atlassian APIs

### Required Tools
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv curl git

# CentOS/RHEL
sudo yum install -y python3 python3-pip git curl

# macOS (with Homebrew)
brew install python@3.10 git curl
```

### Install UV Package Manager
```bash
# Install UV (recommended Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart your shell

# Verify installation
uv --version
```

## Installation

### 1. Clone Repository
```bash
# Clone the repository
git clone https://github.com/sooperset/mcp-atlassian.git
cd mcp-atlassian

# Or download and extract release
wget https://github.com/sooperset/mcp-atlassian/archive/refs/heads/main.zip
unzip main.zip
cd mcp-atlassian-main
```

### 2. Install Dependencies
```bash
# Install all dependencies including development tools
uv sync --frozen --all-extras --dev

# Activate virtual environment
source .venv/bin/activate

# Verify installation
uv run python -c "import mcp_atlassian; print('Installation successful')"
```

### 3. Verify Installation
```bash
# Test basic functionality
uv run mcp-atlassian --help

# Test with verbose output
uv run mcp-atlassian --transport stdio --verbose
```

## Configuration

### 1. Environment Setup
Create your environment configuration file:

```bash
# Copy example configuration
cp env.example .env

# Edit configuration
nano .env  # or vim, code, etc.
```

### 2. Basic Configuration
```bash
# .env file - Basic setup for Atlassian Cloud
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-api-token

CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_TOKEN=your-api-token

# Server behavior
READ_ONLY_MODE=false
MCP_VERBOSE=true
```

### 3. Advanced Configuration Options

#### For Atlassian Server/Data Center
```bash
# Server/DC configuration
JIRA_URL=https://jira.company.com
JIRA_PERSONAL_TOKEN=your-personal-access-token
JIRA_SSL_VERIFY=true

CONFLUENCE_URL=https://confluence.company.com
CONFLUENCE_PERSONAL_TOKEN=your-personal-access-token
CONFLUENCE_SSL_VERIFY=true
```

#### OAuth 2.0 Configuration (Cloud)
```bash
# OAuth setup
ATLASSIAN_OAUTH_CLIENT_ID=your-oauth-client-id
ATLASSIAN_OAUTH_CLIENT_SECRET=your-oauth-client-secret
ATLASSIAN_OAUTH_REDIRECT_URI=http://localhost:8080/callback
ATLASSIAN_OAUTH_SCOPE=read:jira-work write:jira-work read:confluence-content.all write:confluence-content offline_access
ATLASSIAN_OAUTH_CLOUD_ID=your-cloud-id
```

#### Multi-User Configuration
```bash
# Enable multi-user mode (authentication via HTTP headers)
ATLASSIAN_OAUTH_ACCESS_TOKEN=  # Leave empty for per-request tokens
ATLASSIAN_OAUTH_CLOUD_ID=     # Leave empty for per-request cloud IDs
```

#### Network Configuration
```bash
# Proxy settings
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
NO_PROXY=localhost,.company.com

# Custom headers for corporate environments
JIRA_CUSTOM_HEADERS=X-Forwarded-User=service-account,X-Company-Service=mcp-atlassian
CONFLUENCE_CUSTOM_HEADERS=X-ALB-Token=secret-token
```

### 4. Test Configuration
```bash
# Test configuration with simple validation
uv run python3 simple_test.py --verbose

# Test specific components
uv run python3 manual_test_debug.py --mode api-only
```

## Deployment Options

### Option 1: Screen Session (Development/Testing)

Best for: Development, testing, temporary deployments

```bash
# Start in screen session
screen -S mcp-atlassian

# Run server with HTTP transport
uv run mcp-atlassian --transport streamable-http --port 9000 --verbose

# Detach from screen: Ctrl+A, then D
# Reattach: screen -r mcp-atlassian
# List sessions: screen -ls
```

### Option 2: Systemd Service (Production)

Best for: Production deployments, automatic startup, system integration

#### Create Service File
```bash
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
ExecStart=/opt/mcp-atlassian/.venv/bin/uv run mcp-atlassian --transport streamable-http --port 9000 --verbose
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

#### Setup Service
```bash
# Create dedicated user
sudo useradd -r -s /bin/false mcp-user

# Setup directory
sudo mkdir -p /opt/mcp-atlassian
sudo cp -r . /opt/mcp-atlassian/
sudo chown -R mcp-user:mcp-user /opt/mcp-atlassian

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable mcp-atlassian
sudo systemctl start mcp-atlassian

# Check status
sudo systemctl status mcp-atlassian
sudo journalctl -u mcp-atlassian -f
```

### Option 3: PM2 Process Manager

Best for: Node.js environments, advanced process management

```bash
# Install PM2
npm install -g pm2

# Create PM2 ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'mcp-atlassian',
    script: 'uv',
    args: 'run mcp-atlassian --transport streamable-http --port 9000 --verbose',
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
pm2 startup  # Follow instructions to enable auto-start
```

## Client Integration

### Python Client Example

```python
import httpx
import json
import asyncio

class MCPAtlassianClient:
    def __init__(self, base_url: str, auth_token: str = None, cloud_id: str = None):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Content-Type': 'application/json'
        }
        if auth_token:
            self.headers['Authorization'] = f'Bearer {auth_token}'
        if cloud_id:
            self.headers['X-Atlassian-Cloud-Id'] = cloud_id
    
    async def call_tool(self, tool_name: str, arguments: dict):
        """Call an MCP tool"""
        payload = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
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
            "method": "tools/list",
            "params": {}
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

# Usage example
async def main():
    client = MCPAtlassianClient(
        base_url="http://your-server:9000",
        auth_token="your-oauth-token",  # For multi-user mode
        cloud_id="your-cloud-id"       # For multi-user mode
    )
    
    # List available tools
    tools = await client.list_tools()
    print("Available tools:", len(tools.get('result', {}).get('tools', [])))
    
    # Search Jira issues
    result = await client.call_tool("jira_search", {
        "jql": "project = PROJ AND status = 'In Progress'",
        "limit": 5
    })
    print("Search results:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

### JavaScript/Node.js Client Example

```javascript
const axios = require('axios');

class MCPAtlassianClient {
    constructor(baseUrl, authToken = null, cloudId = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.headers = {
            'Content-Type': 'application/json'
        };
        if (authToken) {
            this.headers['Authorization'] = `Bearer ${authToken}`;
        }
        if (cloudId) {
            this.headers['X-Atlassian-Cloud-Id'] = cloudId;
        }
    }

    async callTool(toolName, arguments) {
        const payload = {
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
            method: "tools/list",
            params: {}
        };

        const response = await axios.post(
            `${this.baseUrl}/mcp`,
            payload,
            { headers: this.headers }
        );
        return response.data;
    }
}

// Usage example
async function main() {
    const client = new MCPAtlassianClient(
        'http://your-server:9000',
        'your-oauth-token',  // For multi-user mode
        'your-cloud-id'     // For multi-user mode
    );

    try {
        // List tools
        const tools = await client.listTools();
        console.log('Available tools:', tools.result.tools.length);

        // Get Jira issue
        const issue = await client.callTool('jira_get_issue', {
            issue_key: 'PROJ-123'
        });
        console.log('Issue:', issue.result);
    } catch (error) {
        console.error('Error:', error.message);
    }
}

main();
```

### IDE Integration (Cursor/Claude Desktop)

#### Single-User Configuration
```json
{
  "mcpServers": {
    "mcp-atlassian-remote": {
      "url": "http://your-server:9000/mcp"
    }
  }
}
```

#### Multi-User Configuration
```json
{
  "mcpServers": {
    "mcp-atlassian-remote": {
      "url": "http://your-server:9000/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_OAUTH_TOKEN",
        "X-Atlassian-Cloud-Id": "YOUR_CLOUD_ID"
      }
    }
  }
}
```

### HTTP API Testing

```bash
# Health check
curl -X GET http://your-server:9000/healthz

# List tools
curl -X POST http://your-server:9000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list", "params": {}}'

# Call tool (single-user mode)
curl -X POST http://your-server:9000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "jira_search",
      "arguments": {
        "jql": "project = PROJ",
        "limit": 5
      }
    }
  }'

# Call tool (multi-user mode)
curl -X POST http://your-server:9000/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_OAUTH_TOKEN" \
  -H "X-Atlassian-Cloud-Id: YOUR_CLOUD_ID" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "jira_get_issue",
      "arguments": {
        "issue_key": "PROJ-123"
      }
    }
  }'
```

## Production Setup

### HTTPS with Nginx Reverse Proxy

#### Install Nginx
```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/mcp-atlassian
```

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
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
        proxy_pass http://127.0.0.1:9000;
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

    # Health check endpoint
    location /healthz {
        proxy_pass http://127.0.0.1:9000/healthz;
        access_log off;
    }
}
```

#### Enable Configuration
```bash
sudo ln -s /etc/nginx/sites-available/mcp-atlassian /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Security Hardening

#### Firewall Configuration
```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 9000/tcp  # Block direct access to MCP server
sudo ufw enable

# iptables (CentOS/RHEL)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

#### Access Control
```bash
# Restrict access by IP (in Nginx config)
location / {
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    
    proxy_pass http://127.0.0.1:9000;
    # ... other proxy settings
}
```

#### Environment Security
```bash
# Secure .env file
chmod 600 /opt/mcp-atlassian/.env
chown mcp-user:mcp-user /opt/mcp-atlassian/.env

# Create logs directory with proper permissions
mkdir -p /opt/mcp-atlassian/logs
chown mcp-user:mcp-user /opt/mcp-atlassian/logs
chmod 755 /opt/mcp-atlassian/logs
```

## Monitoring & Maintenance

### Health Monitoring

#### Health Check Script
```bash
#!/bin/bash
# /opt/mcp-atlassian/scripts/health-check.sh

HEALTH_URL="http://localhost:9000/healthz"
LOG_FILE="/var/log/mcp-atlassian-health.log"

response=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" --max-time 10)

if [ "$response" = "200" ]; then
    echo "$(date): MCP Atlassian is healthy" >> "$LOG_FILE"
    exit 0
else
    echo "$(date): MCP Atlassian health check failed (HTTP $response)" >> "$LOG_FILE"
    # Optional: restart service
    # sudo systemctl restart mcp-atlassian
    exit 1
fi
```

#### Cron Job for Health Checks
```bash
# Add to crontab
crontab -e

# Check every 5 minutes
*/5 * * * * /opt/mcp-atlassian/scripts/health-check.sh
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
```

### Performance Monitoring

#### System Resource Monitoring
```bash
# Monitor CPU and memory usage
ps aux | grep mcp-atlassian
top -p $(pgrep -f mcp-atlassian)

# Monitor network connections
netstat -tulpn | grep :9000
ss -tulpn | grep :9000
```

#### Application Metrics
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:9000/healthz

# curl-format.txt content:
#     time_namelookup:  %{time_namelookup}\n
#        time_connect:  %{time_connect}\n
#     time_appconnect:  %{time_appconnect}\n
#    time_pretransfer:  %{time_pretransfer}\n
#       time_redirect:  %{time_redirect}\n
#  time_starttransfer:  %{time_starttransfer}\n
#                     ----------\n
#          time_total:  %{time_total}\n
```

### Updates and Maintenance

#### Update Procedure
```bash
#!/bin/bash
# /opt/mcp-atlassian/scripts/update.sh

set -e

echo "Starting MCP Atlassian update..."

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
curl -f http://localhost:9000/healthz || {
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
# /opt/mcp-atlassian/scripts/backup.sh

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
# Check service status
sudo systemctl status mcp-atlassian

# Check logs
sudo journalctl -u mcp-atlassian -f

# Check configuration
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
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:9000/healthz
```

### Debug Mode

#### Enable Verbose Logging
```bash
# Temporary debug mode
uv run mcp-atlassian --transport streamable-http --port 9000 --very-verbose

# Or set in .env
MCP_VERY_VERBOSE=true
```

#### Debug Configuration
```bash
# Test individual components
uv run python3 manual_test_debug.py --mode api-only
uv run python3 manual_test_debug.py --mode mcp-only
uv run python3 manual_test_debug.py --mode http-server
```

### Getting Help

1. **Check Logs**: Always start with service logs and application logs
2. **Test Configuration**: Use the provided test scripts to validate setup
3. **Network Diagnostics**: Verify connectivity to Atlassian APIs
4. **GitHub Issues**: Report bugs and get community support
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
# Adjust worker processes (if using gunicorn)
# Add to .env:
WORKERS=4
WORKER_CONNECTIONS=1000
```

This guide provides a comprehensive approach to deploying MCP Atlassian on remote machines with direct source installation. The non-Docker approach offers better debugging capabilities, direct environment control, and native system integration while maintaining production-ready security and monitoring features.
