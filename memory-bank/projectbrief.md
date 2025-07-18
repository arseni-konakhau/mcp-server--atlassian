# Project Brief: MCP Atlassian

## Overview
MCP Atlassian is a Model Context Protocol (MCP) server that bridges Atlassian products (Jira and Confluence) with AI language models following Anthropic's MCP specification. This integration enables secure, contextual AI interactions with Atlassian tools while maintaining data privacy and security.

## Core Purpose
Enable AI assistants to seamlessly interact with Atlassian Cloud and Server/Data Center deployments through a standardized MCP interface, allowing users to:
- Perform automatic Jira updates from meeting notes
- Execute AI-powered Confluence searches and content summarization
- Filter and manage Jira issues intelligently
- Create and manage technical documentation
- Automate workflow processes across both platforms

## Key Requirements

### Functional Requirements
1. **Multi-Platform Support**: Support both Atlassian Cloud and Server/Data Center deployments
2. **Comprehensive Tool Coverage**: Provide extensive read/write operations for both Jira and Confluence
3. **Flexible Authentication**: Support API tokens, Personal Access Tokens (PAT), and OAuth 2.0
4. **Security & Privacy**: Maintain data privacy with secure authentication and configurable access controls
5. **IDE Integration**: Seamless integration with AI assistants through IDE MCP configurations
6. **Multi-User Support**: Enable both single-user and multi-user authentication scenarios

### Technical Requirements
1. **MCP Compliance**: Full adherence to Anthropic's MCP specification
2. **Docker Distribution**: Primary distribution via Docker containers
3. **HTTP Transport**: Support for both SSE and streamable-HTTP transports
4. **Tool Filtering**: Configurable tool access and read-only mode support
5. **Proxy Support**: Standard HTTP/HTTPS/SOCKS proxy compatibility
6. **Custom Headers**: Support for corporate environment custom headers

## Success Criteria
- Seamless AI assistant integration with Atlassian products
- Secure, scalable authentication across deployment types
- Comprehensive tool coverage for common Atlassian workflows
- Easy setup and configuration for various environments
- Robust error handling and debugging capabilities

## Constraints
- Python 3.10+ requirement
- Docker-first distribution model
- MCP protocol compliance mandatory
- Security-first approach to authentication and data handling

## Target Users
- Development teams using AI assistants with Atlassian tools
- DevOps engineers automating Atlassian workflows
- Technical writers managing Confluence documentation
- Project managers tracking Jira issues
- Enterprise users requiring secure, scalable integrations
