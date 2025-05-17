# SELF2025
Example scripts and resources for my presentation on LLMs using MCP tools at SELF2025

## File Descriptions

### Python Files

**If you use these python scripts yourself, make sure to replace the example server urls for certain extra lookup services that are used.**

#### system_tools.py
A FastMCP server that provides Docker container management tools. Functions include:
- List containers
- Check if containers are running
- Retrieve container logs
- Get container stats
- Restart containers
- Access MCP Resources:
    - Docker compose files
    - Text files
    - System IP addresses
    - Date/time information
    - System information

#### network_tools.py
A FastMCP server providing network-related tools. Functions include:
- Domain lookups
- IP lookups
- Ping tests
- HTTP GET testing
- DNS checking
- IP address listing
- Service monitoring
- Access MCP Resource
    - System IP Addresses

#### smolagents_sysadmin_examples.py
Demonstrates how to use SmolAgents with MCPAdapt to interact with MCP servers. The example shows how to check and fix a service running in a Docker container, using LLMs to perform system administration and diagnostic tasks.

Example Run: https://asciinema.org/a/CQmdS2MlpWdck0rS9GOMsebKl


### YAML Files

#### mcp-proxy-tools.yml
Docker Compose configuration for running the MCP server tools as containers:
- `mcp-proxy-network`: Runs the network_tools.py script, exposing port 8097
- `mcp-proxy-system`: Runs the system_tools.py script, exposing port 8098, with access to Docker socket

### Dockerfile

#### mcp-proxy_tools.Dockerfile
Builds the container image used by the MCP proxy services:
- Based on the mcp-proxy base image
- Installs necessary Python packages (psutil, mcp[cli], requests, docker)
- Sets up the environment for running MCP services

## Example Usage

The repository includes example scripts showing how an LLM can be used to:
- Monitor and repair Docker containers (e.g., fixing the "homebox" service)
- Perform network diagnostics
- Retrieve system information

