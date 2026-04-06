from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

root_agent = Agent(
    model='gemini-2.5-flash',
    name='master_agent',
    description='Access to all remote agents and will perform calls to remote based on requirement',
    instruction="""
        Access to all remote agents and will perform calls to remote based on requirement
    """,
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://example.com/mcp",
            ),
        )
    ],
)
