# MCP Atlassian Server - Project Brief

## Project Overview
MCP Atlassian is a Model Context Protocol (MCP) server that provides integration between AI language models and Atlassian products (Confluence and Jira). It enables secure, contextual AI interactions with Atlassian tools while maintaining data privacy and security.

## Core Purpose
- Bridge Atlassian products (Jira and Confluence) with AI language models
- Support both Cloud and Server/Data Center deployments
- Provide secure authentication and data access
- Enable AI-powered interactions with Atlassian content

## Key Features
- **Confluence Integration**: Search, read, and manage Confluence pages and spaces
- **Jira Integration**: Create, update, and manage Jira issues, projects, and workflows
- **Multiple Authentication Methods**: API tokens, Personal Access Tokens, OAuth 2.0
- **Cross-Platform Support**: Cloud and Server/Data Center deployments
- **MCP Protocol Compliance**: Follows Anthropic's MCP specification

## Technical Stack
- **Language**: Python 3.10+
- **Framework**: FastMCP, MCP protocol
- **Dependencies**: atlassian-python-api, requests, httpx, pydantic, trio
- **Transport**: stdio, SSE, streamable-http
- **Authentication**: OAuth 2.0, API tokens, Personal Access Tokens

## Project Status
- Active development
- Production ready
- Comprehensive test coverage
- Well-documented

## Current Focus
Initializing Memory Bank system for development workflow management.
