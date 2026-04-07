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


short_film_image_generator = RemoteA2aAgent(
    name="short_film_image_generator",
    description="""
        Use this agent when the user needs to:
        - Generate images for the short film.
    """,
    agent_card="https://image-generator-agent-475756125529.us-central1.run.app/anime/.well-known/agent.json"
)

search_agent = Agent(
    model='gemini-2.5-flash',
    name='search_agent',
    description="""
        Use this agent when the user needs to:
        - Search for real-time information on the web
        - Research topics, trends, or references for the short film
        - Look up current events or facts
    """,
    instruction="You are a web search specialist. Use Google Search to find accurate, up-to-date information and always summarize the results clearly.",
    tools=[google_search],  # google_search alone in this agent
)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='master_agent',
    description='Orchestrates all agents for short film production and research.',
    instruction="""
        You have access to specialized agents:
        - Use search_agent to look up real-world info, references, or research topics
        - Use short_film_story_writer to craft story ideas
        - Use short_film_script_writer to write the actual script
        - Use short_film_image_generator to generate images for the film
        
        Delegate tasks to the appropriate agent based on the user's request.
    """,
    sub_agents=[    
        search_agent,             
        short_film_script_writer,
        short_film_story_writer,
        short_film_image_generator,
    ]
)