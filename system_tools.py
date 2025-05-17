from mcp.server.fastmcp import FastMCP
import os, docker, datetime, socket, psutil

mcp = FastMCP("System Tools Server", version="1.0.0")

@mcp.tool()
async def list_containers() -> list:
    """
    List all Docker containers on the system.
    
    Returns:
        list: List of container names.
    """
    client = docker.from_env()
    try:
        containers = client.containers.list(all=True)
        return ', '.join([container.name for container in containers])
    except Exception as e:
        return f"Error listing containers: {str(e)}"

@mcp.tool()
async def is_container_running(container_name: str) -> bool:
      """
      Check if a given Docker container is running.
  
      Args:
          container_name (str): The name of the Docker container.
  
      Returns:
          bool: True if the container is running, False otherwise.
      """
      client = docker.from_env()
    #   client = docker.DockerClient(base_url='tcp://localhost:2375')
      try:
          container = client.containers.get(container_name)
          return container.status == 'running'
      except docker.errors.NotFound:
          return False

@mcp.tool()
async def get_container_logs(container_name: str) -> str:
    """
    Get the last 50 lines of logs from a given Docker container.
    
    Args:
        container_name (str): The name of the Docker container.
    
    Returns:
        str: Logs from the container.
    """
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        return container.logs(tail=50).decode('utf-8')
    except docker.errors.NotFound:
        return f"Container {container_name} not found"
    except Exception as e:
        return f"Error retrieving logs: {str(e)}"
    
@mcp.tool()
async def get_container_stats(container_name: str) -> dict:
    """
    Get the CPU and memory usage of a given Docker container.
    
    Args:
        container_name (str): The name of the Docker container.
    
    Returns:
        dict: CPU and memory usage of the container.
    """
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        stats = container.stats(stream=False)

        cpu_usage = (stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage'])
        cpu_system = (stats['cpu_stats']['system_cpu_usage']                    
                    - stats['precpu_stats']['system_cpu_usage'])
        num_cpus = stats['cpu_stats']["online_cpus"]
        cpu_perc = round((cpu_usage / cpu_system) * num_cpus * 100)

        return {
            "cpu_percent": cpu_perc,
            "memory_usage": stats["memory_stats"]["usage"]
        }
    except docker.errors.NotFound:
        return f"Container {container_name} not found"
    except Exception as e:
        return f"Error retrieving stats: {str(e)}"
    
@mcp.tool()
async def restart_container(container_name: str) -> str:
    """
    Restart a given Docker container.
    
    Args:
        container_name (str): The name of the Docker container.
    
    Returns:
        str: Status message.
    """
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        container.restart()
        return f"Container {container_name} restarted successfully"
    except docker.errors.NotFound:
        return f"Container {container_name} not found"
    except Exception as e:
        return f"Error restarting container: {str(e)}"


# MCP resource for docker compose file
@mcp.resource("docker://compose")
async def get_docker_compose() -> str:
    """
    Returns the contents of the docker-compose.yml file.
    
    Returns:
        str: Contents of the docker-compose.yml file.
    """
    try:
        with open(os.environ['HOME']+"/docker/docker-compose.yml", 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "docker-compose.yml file not found"
    except Exception as e:
        return f"Error reading docker-compose.yml: {str(e)}"
    
# MCP Resource for reading arbitrary text files
@mcp.resource("text://{filepath}")
async def get_text_file(filepath: str) -> str:
    """
    Returns the contents of a text file.
    
    Args:
        filename: Name of the text file in the data directory.
    
    Returns:
        str: Contents of the text file.
    """
    
    if not filepath.exists():
        return f"Error: File {filepath} not found"
    
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading {filepath}: {str(e)}"
    
# MCP Resource for getting a list of the system's IP addresses
@mcp.resource("network://ip_addresses")
async def get_ip_addresses() -> list:
    """
    Returns a list of the system's IP addresses.
    
    Returns:
        list: List of IP addresses.
    """
    ip_addresses = []
    try:
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip_addresses.append(addr.address)
        return ip_addresses
    except Exception as e:
        return f"Error retrieving IP addresses: {str(e)}"
    
# MCP Resource for getting the current system date and time
@mcp.resource("system://datetime")
async def get_current_datetime() -> dict:
    """
    Returns the current system date, time, and timezone.
    
    Returns:
        dict: Current date, time, and timezone information.
    """
    try:
        now = datetime.datetime.now()
        timezone_name = datetime.datetime.now().astimezone().tzinfo.tzname(now)
        timezone_offset = datetime.datetime.now().astimezone().utcoffset().total_seconds() / 3600
        
        return {
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": timezone_name,
            "utc_offset": f"{timezone_offset:+.1f} hours"
        }
    except Exception as e:
        return {"error": f"Error retrieving date and time: {str(e)}"}
    
# MCP Resource for getting the current system information from /etc/*release
@mcp.resource("system://system_info")
async def get_os_info() -> str:
    """
    Returns the current system information from /etc/os-release and hostname.
    
    Returns:
        str: System information including hostname.
    """
    try:
        os_info = ""
        hostname = socket.gethostname()
        os_info += f"Hostname: {hostname}\n"
        
        # Get system uptime
        uptime_seconds = psutil.boot_time()
        uptime = datetime.datetime.fromtimestamp(uptime_seconds)
        now = datetime.datetime.now()
        uptime_duration = now - uptime
        days, remainder = divmod(uptime_duration.total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        os_info += f"Uptime: {int(days)} days, {int(hours)} hours, {int(minutes)} minutes\n\n"
        
        # Most distributions have /etc/os-release
        release_file = "/etc/os-release"
        if os.path.exists(release_file):
            with open(release_file, 'r') as f:
                os_info += f.read()
        else:
            # Try alternative files if os-release doesn't exist
            for release_file in ["/etc/lsb-release", "/etc/debian_version", "/etc/redhat-release"]:
                if os.path.exists(release_file):
                    with open(release_file, 'r') as f:
                        os_info += f.read()
                    break
            else:
                os_info += "Could not find OS release information"
        
        return os_info
    except Exception as e:
        return f"Error retrieving system information: {str(e)}"

# @mcp.resource("data://csv/{filename}")
# async def get_csv_data(ctx: Context, filename: str) -> str:
#     """
#     Provides CSV data as formatted text resource
    
#     Args:
#         filename: CSV file in data directory
#     """
#     file_path = ctx.data_dir / filename
    
#     if not file_path.exists():
#         return f"Error: File {filename} not found"
    
#     try:
#         with open(file_path, 'r') as f:
#             reader = csv.reader(f)
#             return "\n".join([",".join(row) for row in reader])
#     except Exception as e:
#         ctx.logger.error(f"CSV read error: {str(e)}")
#         return f"Error reading {filename}: {str(e)}"

# @mcp.resource("logs://app/{log_type}")
# async def get_log_data(ctx: Context, log_type: str) -> str:
#     """
#     Returns log file contents from text files
    
#     Args:
#         log_type: Error/debug/access logs
#     """
#     valid_logs = {"error", "debug", "access"}
#     if log_type not in valid_logs:
#         return f"Invalid log type: {log_type}"
    
#     file_path = ctx.data_dir / f"{log_type}_logs.txt"
    
#     try:
#         with open(file_path, 'r') as f:
#             return f.read()
#     except FileNotFoundError:
#         return f"No {log_type} logs available"


# # Run the MCP server
# if __name__ == "__main__":
#     mcp.run()