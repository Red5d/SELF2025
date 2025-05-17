from mcp.server.fastmcp import FastMCP
import socket, subprocess, requests, psutil
from mcp.server.fastmcp.prompts.base import UserMessage, AssistantMessage

mcp = FastMCP("Network Tools Server", version="1.0.0")

# Tools

@mcp.tool()
def lookup_domain(
    domain: str,
) -> dict:
    """
    Look up a domain with whois
   
    Args:
        domain: Domain name to look up
    """
    
    res = requests.get(f"http://docker1:8411/{domain}")
    return res.json()

@mcp.tool()
def lookup_ip(ip: str) -> dict:
    """Look up an IP address
    
    Args:
        ip: IP Address to look up
    """
    res = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,timezone,isp,org,as,reverse,mobile,proxy,hosting")
    return res.json()

@mcp.tool()
def ping(ip: str) -> bool:
    """
    Ping an IP address to check if it is reachable.
    This should ONLY be used for IP addresses. Do not use it for web addresses.
    Ping requests failing does not necessarily mean the IP address is unreachable, as some systems may block ICMP requests.

    Args:
        ip (str): The IP address to ping.

    Returns:
        bool: True if the IP address is reachable, False otherwise.
    """
    try:
        ip = ip.replace("http://", "").replace("https://", "")
        output = subprocess.run(["ping", "-c", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output.returncode == 0
    except Exception as e:
        print(f"Error pinging IP address {ip}: {e}")
        return False

@mcp.tool()
def test_http_get(url: str) -> bool:
    """
    Test an HTTP GET request to a given URL.

    Args:
        url (str): The URL to send the GET request to.

    Returns:
        bool: True if the GET request was successful (status code 200), False otherwise.
    """
    try:
        response = requests.get(url, timeout=10, verify=False)
        return response.status_code == 200
    except Exception as e:
        print(f"Error making GET request to {url}: {e}")
        return False

@mcp.tool()
def check_dns(domain: str) -> bool:
    """
    Check if a domain name can be resolved to an IP address. Use the fully-qualified domain name (FQDN) if possible.

    Args:
        domain (str): The domain name to resolve.

    Returns:
        bool: True if the domain name can be resolved, False otherwise.
    """
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except Exception as e:
        print(f"Error resolving domain {domain}: {e}")
        return False

@mcp.tool()
def get_ip_addresses() -> list:
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
        return {"ip_addresses": ip_addresses}
    except Exception as e:
        return f"Error retrieving IP addresses: {str(e)}"


@mcp.tool()
def service_monitoring() -> dict:
    """
    Get the status of all monitored services from Uptime Kuma

    Returns:
        dict: Status of all network services
    """
    server = "uptime.nas.cnet"
    servicelist = requests.get(f"http://{server}/api/status-page/default").json()

    heartbeats = requests.get(f"http://{server}/api/status-page/heartbeat/default").json()

    services = {}
    for group in servicelist['publicGroupList']:
        for monitor in group['monitorList']:
            services[monitor['id']] = monitor['name']

    status = {}
    for monitorId, statuses in heartbeats['heartbeatList'].items():
        try:
            status[services[int(monitorId)]] = statuses[-1]
        except:
            pass

    return status


# Resources

# MCP Resource for getting a list of the system's IP addresses
@mcp.resource(uri="network://ip_addresses", mime_type="application/json")
async def get_ip_addresses_resource() -> list:
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
        return {"ip_addresses": ip_addresses}
    except Exception as e:
        return f"Error retrieving IP addresses: {str(e)}"
    

# Prompts

# Prompt for looking up a network resource
@mcp.prompt()
def lookup_resource(ip_or_domain: str) -> str:
    """Look up information on a network resource (IP or domain)"""
    return f"Look up all available information on {ip_or_domain} and check if it's accessible."

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