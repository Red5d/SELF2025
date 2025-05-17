import os
from smolagents import CodeAgent, OpenAIServerModel
from mcpadapt.core import MCPAdapt
from mcpadapt.smolagents_adapter import SmolAgentsAdapter

llama4mav = OpenAIServerModel(
    model_id="meta-llama/llama-4-maverick",
    api_base="https://openrouter.ai/api/v1",
    api_key=os.environ['OPENROUTER_API_KEY']
)

llama4scout = OpenAIServerModel(
    model_id="meta-llama/llama-4-scout",
    api_base="https://openrouter.ai/api/v1",
    api_key=os.environ['OPENROUTER_API_KEY']
)


from smolagents import ToolCollection

mcp_servers = [
    "http://daniel-nucbox2:8098/sse",
    "http://daniel-nucbox2:8097/sse"
]

with MCPAdapt(
    [{"url": x} for x in mcp_servers],
    SmolAgentsAdapter()
) as tool_collection:
    agent = CodeAgent(tools=tool_collection, model=llama4mav, additional_authorized_imports=["sys"], add_base_tools=True)
    container_fix = agent.run("""Check on the "homebox" service. It should be running and accessible at http://localhost:3100. Fix it if it is not. 
                                If you're able to fix it, provide a summary of the changes made and any errors encountered. 
                                Also check the logs for the container, looking for any errors that may have caused the service to be unavailable. If you find any, summarize them, and suggest fixes if relevant.""")
    print("Container Fix:")
    print(container_fix)

    # Additional examples for testing various tools
    # iptest = agent.run("Look up the IP address 8.8.8.8 and summarize the information about it in a concise format.")
    # print("IP Test with ToolCollection:")
    # print(iptest)

    # httptest = agent.run("Check if DNS resolution and HTTP request to https://southeastlinuxfest.org is working and show the results of each test.")
    # print("HTTP/DNS Test with ToolCollection:")
    # print(httptest)

    # iptest2 = agent.run("List the system IP addresses, then test a ping to 8.8.8.8")
    # print("System IP Test with ToolCollection:")
    # print(iptest2)