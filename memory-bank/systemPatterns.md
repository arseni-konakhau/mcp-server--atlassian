# System Patterns: MCP Atlassian

## Architecture Overview

### High-Level Design
MCP Atlassian follows a modular, service-oriented architecture built on the FastMCP framework:

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Assistant (Client)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │ MCP Protocol
┌─────────────────────▼───────────────────────────────────────┐
│                 AtlassianMCP Server                         │
│  ┌─────────────────┬─────────────────┬─────────────────────┐ │
│  │   Main Server   │   Jira Module   │ Confluence Module   │ │
│  │   (Routing &    │   (Tools &      │   (Tools &          │ │
│  │   Auth)         │   Resources)    │   Resources)        │ │
│  └─────────────────┼─────────────────┼─────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                      │                 │
┌─────────────────────▼─────────────────▼─────────────────────┐
│              Atlassian APIs                                 │
│  ┌─────────────────────────┬─────────────────────────────┐  │
│  │     Jira REST API       │   Confluence REST API      │  │
│  │   (Cloud/Server/DC)     │   (Cloud/Server/DC)        │  │
│  └─────────────────────────┴─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Main Server (`src/mcp_atlassian/servers/main.py`)
- **FastMCP Integration**: Custom `AtlassianMCP` class extending FastMCP
- **Service Mounting**: Mounts Jira and Confluence sub-servers
- **Tool Filtering**: Implements dynamic tool filtering based on configuration
- **Lifecycle Management**: Handles startup/shutdown and resource cleanup
- **Health Checks**: Provides `/healthz` endpoint for monitoring

#### 2. Authentication Middleware (`UserTokenMiddleware`)
- **Multi-Auth Support**: Handles OAuth 2.0 Bearer tokens and Personal Access Tokens
- **Request Context**: Extracts user credentials from HTTP headers
- **Cloud ID Routing**: Supports multi-cloud scenarios via `X-Atlassian-Cloud-Id` header
- **Token Caching**: TTL-based caching for token validation

#### 3. Service Modules
- **Jira Module** (`src/mcp_atlassian/jira/`): Complete Jira API integration
- **Confluence Module** (`src/mcp_atlassian/confluence/`): Complete Confluence API integration
- **Shared Utilities** (`src/mcp_atlassian/utils/`): Common functionality

## Key Design Patterns

### 1. Configuration Pattern
**Environment-Based Configuration**: All services use environment variables with fallback defaults
```python
# Pattern: Service-specific config classes
class JiraConfig:
    @classmethod
    def from_env(cls) -> 'JiraConfig':
        # Load from environment with validation
```

**Benefits**:
- Consistent configuration across services
- Easy Docker integration
- Environment-specific overrides
- Validation at startup

### 2. Authentication Strategy Pattern
**Multi-Method Authentication**: Support for different auth methods based on deployment type

```python
# Pattern: Authentication abstraction
class AuthConfig:
    def is_auth_configured(self) -> bool:
        # Check if any valid auth method is configured
    
    def get_auth_headers(self) -> dict:
        # Return appropriate headers for the configured method
```

**Supported Methods**:
- **API Token + Username** (Cloud)
- **Personal Access Token** (Server/Data Center)
- **OAuth 2.0** (Cloud, with refresh token support)
- **User-Provided Tokens** (Multi-user scenarios)

### 3. Tool Registration Pattern
**Modular Tool System**: Each service registers its tools independently

```python
# Pattern: Service-specific tool registration
@jira_mcp.tool()
async def jira_get_issue(issue_key: str) -> dict:
    # Tool implementation
```

**Benefits**:
- Clear separation of concerns
- Easy to add new tools
- Service-specific error handling
- Consistent tool metadata

### 4. Error Handling Pattern
**Layered Error Handling**: Multiple levels of error handling and recovery

```python
# Pattern: Service-level error handling
try:
    result = await api_call()
except AuthenticationError:
    # Handle auth-specific errors
except APIError as e:
    # Handle API-specific errors
except Exception as e:
    # Handle unexpected errors
```

**Layers**:
1. **API Client Level**: Handle HTTP errors, rate limiting
2. **Service Level**: Handle business logic errors
3. **Tool Level**: Handle tool-specific errors
4. **Server Level**: Handle protocol errors

### 5. Resource Management Pattern
**Context-Aware Resource Management**: Resources are managed based on request context

```python
# Pattern: Context-aware fetcher creation
async def get_jira_fetcher(context: RequestContext) -> JiraFetcher:
    # Create fetcher based on user context or global config
```

**Benefits**:
- Supports both single-user and multi-user scenarios
- Efficient resource utilization
- Proper cleanup and lifecycle management

## Data Flow Patterns

### 1. Request Processing Flow
```
Client Request → Middleware → Tool Router → Service Module → API Client → Atlassian API
                     ↓              ↓             ↓            ↓
               Auth Extraction → Tool Filter → Data Transform → Response Format
```

### 2. Authentication Flow
```
Request Headers → Token Extraction → Validation → Context Creation → API Client Config
                       ↓                ↓              ↓
                 Cache Check → Service Auth → Fallback Config
```

### 3. Tool Discovery Flow
```
Service Config → Available Tools → Filter by Permissions → Filter by Read-Only → Return Tools
                      ↓                    ↓                     ↓
                 Tool Metadata → User Context → Configuration
```

## Integration Patterns

### 1. MCP Protocol Integration
**FastMCP Framework**: Built on top of FastMCP for protocol compliance
- Automatic tool discovery and registration
- Built-in transport support (stdio, SSE, streamable-http)
- Request/response serialization
- Error handling and logging

### 2. Docker Integration Pattern
**Container-First Design**: Optimized for containerized deployment
- Multi-stage builds for size optimization
- Environment-based configuration
- Health check endpoints
- Graceful shutdown handling

### 3. IDE Integration Pattern
**Configuration Templates**: Standardized configuration for different IDEs
- Claude Desktop integration
- Cursor IDE integration
- Environment variable mapping
- Transport configuration

## Security Patterns

### 1. Token Management
**Secure Token Handling**: Comprehensive token security measures
- Token masking in logs
- Secure storage for OAuth refresh tokens
- TTL-based caching
- Automatic token refresh

### 2. Access Control
**Multi-Level Access Control**: Granular permission management
- Tool-level filtering
- Read-only mode support
- Service-specific permissions
- User context isolation

### 3. Network Security
**Enterprise Network Support**: Corporate environment compatibility
- Proxy support (HTTP/HTTPS/SOCKS)
- Custom header injection
- SSL verification controls
- Network isolation support

## Performance Patterns

### 1. Caching Strategy
**Multi-Level Caching**: Efficient data and authentication caching
- Token validation caching (TTL: 5 minutes)
- API response caching where appropriate
- Configuration caching
- Connection pooling

### 2. Async Processing
**Async-First Design**: Non-blocking operations throughout
- Async API clients
- Async tool implementations
- Async middleware
- Proper resource cleanup

### 3. Resource Optimization
**Efficient Resource Usage**: Optimized for performance and scalability
- Lazy loading of configurations
- Connection reuse
- Minimal memory footprint
- Graceful degradation
