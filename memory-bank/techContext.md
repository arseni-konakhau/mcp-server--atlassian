# Technical Context: MCP Atlassian

## Technology Stack

### Core Framework
- **Python 3.10+**: Minimum required version for modern async features and type hints
- **FastMCP 2.3.4+**: MCP server framework providing protocol compliance and transport support
- **MCP 1.8.0+**: Core Model Context Protocol library from Anthropic
- **Pydantic 2.10.6+**: Data validation and serialization with modern Python type hints

### HTTP & Networking
- **httpx 0.28.0+**: Modern async HTTP client for API interactions
- **requests[socks] 2.31.0+**: HTTP library with SOCKS proxy support for legacy compatibility
- **uvicorn 0.27.1+**: ASGI server for HTTP transport modes
- **starlette 0.37.1+**: Lightweight ASGI framework for web components

### Atlassian Integration
- **atlassian-python-api 4.0.0+**: Official Atlassian API client library
- **beautifulsoup4 4.12.3+**: HTML parsing for content processing
- **markdownify 0.11.6+**: HTML to Markdown conversion
- **markdown 3.7.0+**: Markdown processing and rendering
- **markdown-to-confluence 0.3.0+**: Confluence-specific Markdown conversion

### Utilities & Support
- **python-dotenv 1.0.1+**: Environment variable management
- **click 8.1.7+**: Command-line interface framework
- **trio 0.29.0+**: Async concurrency framework
- **thefuzz 0.22.1+**: Fuzzy string matching for search functionality
- **python-dateutil 2.9.0+**: Enhanced date/time parsing and manipulation
- **keyring 25.6.0+**: Secure credential storage
- **cachetools 5.0.0+**: Caching utilities with TTL support

### Development Tools
- **uv**: Modern Python package manager and virtual environment tool
- **pytest 8.0.0+**: Testing framework with async support
- **pytest-cov 4.1.0+**: Coverage reporting
- **pytest-asyncio 0.23.0+**: Async test support
- **pre-commit 3.6.0+**: Git hooks for code quality
- **ruff 0.3.0+**: Fast Python linter and formatter
- **black 24.2.0+**: Code formatting
- **mypy 1.8.0+**: Static type checking

## Development Environment

### Package Management
```bash
# Primary package manager
uv sync --frozen --all-extras --dev

# Virtual environment activation
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate.ps1  # Windows
```

### Code Quality Pipeline
```bash
# Pre-commit hooks (runs automatically on commit)
pre-commit install
pre-commit run --all-files

# Manual quality checks
uv run pytest --cov=mcp_atlassian
uv run ruff check .
uv run ruff format .
uv run mypy .
```

### Docker Environment
```dockerfile
# Multi-stage build pattern
FROM python:3.10-slim as base
# ... build stages for optimization
```

## Configuration Management

### Environment Variables

#### Core Service Configuration
```bash
# Jira Configuration
JIRA_URL=https://company.atlassian.net
JIRA_USERNAME=user@company.com          # Cloud only
JIRA_API_TOKEN=api_token                # Cloud only
JIRA_PERSONAL_TOKEN=personal_token      # Server/DC only
JIRA_SSL_VERIFY=true                    # Server/DC SSL control

# Confluence Configuration
CONFLUENCE_URL=https://company.atlassian.net/wiki
CONFLUENCE_USERNAME=user@company.com    # Cloud only
CONFLUENCE_API_TOKEN=api_token          # Cloud only
CONFLUENCE_PERSONAL_TOKEN=personal_token # Server/DC only
CONFLUENCE_SSL_VERIFY=true              # Server/DC SSL control
```

#### OAuth 2.0 Configuration (Cloud)
```bash
# Standard OAuth Flow
ATLASSIAN_OAUTH_CLIENT_ID=oauth_client_id
ATLASSIAN_OAUTH_CLIENT_SECRET=oauth_client_secret
ATLASSIAN_OAUTH_REDIRECT_URI=http://localhost:8080/callback
ATLASSIAN_OAUTH_SCOPE=read:jira-work write:jira-work read:confluence-content.all write:confluence-content offline_access
ATLASSIAN_OAUTH_CLOUD_ID=cloud_id_from_setup

# BYOT (Bring Your Own Token) Flow
ATLASSIAN_OAUTH_ACCESS_TOKEN=user_provided_token
ATLASSIAN_OAUTH_CLOUD_ID=user_cloud_id
```

#### Server Behavior Configuration
```bash
# Tool and Access Control
ENABLED_TOOLS=confluence_search,jira_get_issue,jira_search  # Comma-separated tool names
READ_ONLY_MODE=false                    # Disable write operations
CONFLUENCE_SPACES_FILTER=DEV,TEAM,DOC   # Filter by space keys
JIRA_PROJECTS_FILTER=PROJ,DEV,SUPPORT   # Filter by project keys

# Logging and Debugging
MCP_VERBOSE=false                       # Enable verbose logging
MCP_VERY_VERBOSE=false                  # Enable very verbose logging
MCP_LOGGING_STDOUT=false                # Log to stdout instead of stderr

# Network Configuration
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
NO_PROXY=localhost,.company.com
SOCKS_PROXY=socks5://proxy.company.com:1080

# Custom Headers (Corporate environments)
JIRA_CUSTOM_HEADERS=X-Forwarded-User=service-account,X-Company-Service=mcp-atlassian
CONFLUENCE_CUSTOM_HEADERS=X-ALB-Token=secret-token,X-Custom-Auth=confluence-token
```

## Deployment Patterns

### Docker Deployment
```bash
# Pull and run pre-built image
docker pull ghcr.io/sooperset/mcp-atlassian:latest

# Run with environment file
docker run --rm -i --env-file .env ghcr.io/sooperset/mcp-atlassian:latest

# Run with HTTP transport
docker run --rm -p 9000:9000 --env-file .env \
  ghcr.io/sooperset/mcp-atlassian:latest \
  --transport streamable-http --port 9000
```

### IDE Integration Patterns
```json
// Claude Desktop / Cursor configuration
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--env-file", "/path/to/.env", "ghcr.io/sooperset/mcp-atlassian:latest"],
      "env": {
        // Environment variables can be specified here instead of --env-file
      }
    }
  }
}
```

### HTTP Transport Configuration
```json
// SSE Transport
{
  "mcpServers": {
    "mcp-atlassian-http": {
      "url": "http://localhost:9000/sse"
    }
  }
}

// Streamable-HTTP Transport with user authentication
{
  "mcpServers": {
    "mcp-atlassian-service": {
      "url": "http://localhost:9000/mcp",
      "headers": {
        "Authorization": "Bearer <USER_OAUTH_TOKEN>",
        "X-Atlassian-Cloud-Id": "<USER_CLOUD_ID>"
      }
    }
  }
}
```

## Technical Constraints

### Python Version Requirements
- **Minimum**: Python 3.10 (required for modern async features and type hints)
- **Recommended**: Python 3.11+ for better performance
- **Type Hints**: Full type annotation coverage required
- **Async/Await**: Async-first design throughout the codebase

### Memory and Performance
- **Memory Usage**: Optimized for minimal memory footprint
- **Connection Pooling**: Reuse HTTP connections where possible
- **Caching**: TTL-based caching for authentication and frequently accessed data
- **Async Operations**: Non-blocking I/O throughout

### Security Constraints
- **Token Security**: All sensitive data masked in logs
- **SSL/TLS**: Configurable SSL verification for enterprise environments
- **Proxy Support**: Full proxy support for corporate networks
- **Access Control**: Granular tool filtering and read-only modes

### Network Requirements
- **Outbound HTTPS**: Required for Atlassian Cloud APIs
- **Proxy Compatibility**: Support for HTTP/HTTPS/SOCKS proxies
- **Custom Headers**: Support for corporate authentication headers
- **Rate Limiting**: Respect Atlassian API rate limits

### Docker Constraints
- **Base Image**: Python 3.10+ slim images for size optimization
- **Multi-stage Builds**: Separate build and runtime stages
- **Health Checks**: Built-in health check endpoints
- **Signal Handling**: Proper SIGTERM handling for graceful shutdown

## API Compatibility

### Atlassian API Versions
- **Jira Cloud**: REST API v3 (primary), v2 (fallback)
- **Jira Server/DC**: REST API v2 (version 8.14+)
- **Confluence Cloud**: REST API v2 (primary), v1 (legacy)
- **Confluence Server/DC**: REST API v1 (version 6.0+)

### MCP Protocol Compliance
- **MCP Version**: 1.8.0+ compatibility
- **Transport Support**: stdio, SSE, streamable-http
- **Tool Registration**: Dynamic tool discovery and filtering
- **Error Handling**: Proper MCP error response formatting

### Authentication Compatibility
- **Cloud**: API Token + Username, OAuth 2.0
- **Server/Data Center**: Personal Access Tokens, Basic Auth (legacy)
- **Multi-User**: Per-request authentication via headers
- **Token Refresh**: Automatic OAuth token refresh for long-running sessions

## Development Workflow

### Local Development
```bash
# Setup
git clone <repository>
uv sync --frozen --all-extras --dev
source .venv/bin/activate
pre-commit install

# Testing
uv run pytest
uv run pytest --cov=mcp_atlassian

# Code Quality
pre-commit run --all-files
uv run ruff check .
uv run mypy .

# Local Testing with MCP Inspector
npx @modelcontextprotocol/inspector uv run mcp-atlassian
```

### CI/CD Pipeline
- **GitHub Actions**: Automated testing and building
- **Pre-commit Hooks**: Code quality enforcement
- **Docker Build**: Multi-architecture container builds
- **Semantic Versioning**: Automated version management
- **PyPI Publishing**: Package distribution (if applicable)
