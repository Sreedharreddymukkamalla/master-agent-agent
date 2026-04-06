from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams


# Connect to the separately deployed short film script writer agent
short_film_script_writer = RemoteA2aAgent(
    name="short_film_script_writer",
    description="""
        Use this agent when the user needs to:
        - Craft a short film script based on the user's input.
    """,
    agent_card="https://short-film-script-writer-475756125529.us-central1.run.app/anime/.well-known/agent.json"
)

short_film_story_writer = RemoteA2aAgent(
    name="short_film_story_writer",
    description="""
        Use this agent when the user needs to:
        - Craft a short film story based on the story idea.
    """,
    agent_card="https://storyteller-475756125529.us-central1.run.app/anime/.well-known/agent.json"
)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='master_agent',
    description='Access to all remote agents and will perform calls to remote based on requirement',
    instruction="""
        Access to all remote agents and will perform calls to remote based on requirement
    """,
    sub_agents=[short_film_script_writer]
)
