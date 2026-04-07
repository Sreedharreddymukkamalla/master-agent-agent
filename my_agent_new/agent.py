from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import google_search

# ── Remote agents ────────────────────────────────────────────────────────────

short_film_story_writer = RemoteA2aAgent(
    name="short_film_story_writer",
    description="Crafts a short film story based on the user's idea.",
    agent_card="https://storyteller-475756125529.us-central1.run.app/anime/.well-known/agent.json",
    output_key="film_story"
)

short_film_script_writer = RemoteA2aAgent(
    name="short_film_script_writer",
    description="Writes a short film script. Uses {film_story} from state if available, otherwise uses the user's direct input.",
    agent_card="https://short-film-script-writer-475756125529.us-central1.run.app/anime/.well-known/agent.json",
    output_key="film_script"
)

short_film_image_generator = RemoteA2aAgent(
    name="short_film_image_generator",
    description="Generates images for the short film. Uses {film_script} from state if available, otherwise uses the user's direct input.",
    agent_card="https://image-generator-agent-475756125529.us-central1.run.app/anime/.well-known/agent.json",
)

# ── Full pipeline (story → script → images) ──────────────────────────────────

film_production_pipeline = SequentialAgent(
    name="film_production_pipeline",
    description="Full short film pipeline: writes story, then script, then generates images. Use when the user wants the complete package.",
    sub_agents=[
        short_film_story_writer,
        short_film_script_writer,
        short_film_image_generator,
    ]
)

# ── Search agent ─────────────────────────────────────────────────────────────

search_agent = Agent(
    model='gemini-2.5-flash',
    name='search_agent',
    description="Searches the web for references, research, or real-time information.",
    instruction="Use Google Search to find accurate information. Summarize results clearly.",
    tools=[google_search],
)

# ── Root agent ────────────────────────────────────────────────────────────────

root_agent = Agent(
    model='gemini-2.5-flash',
    name='master_agent',
    description='Short film production coordinator.',
    instruction="""
        You are a short film production coordinator. Based on what the user asks,
        route to the right agent or pipeline:

        - "give me a story / story only / just a story idea"
            → call short_film_story_writer only

        - "write me a script / script only / just a script"
            → call short_film_script_writer only

        - "generate images / only images / just visuals"
            → call short_film_image_generator only

        - "make a short film / full film / story + script + images / everything"
            → call film_production_pipeline
              (it will automatically chain: story → script → images)

        - "search / research / find info about..."
            → call search_agent

        If the user's request is ambiguous, ask them:
        "Would you like just the story, just the script, just images, or the full film pipeline?"

        Always confirm the film idea/topic before delegating.
    """,
    # Wrap each as AgentTool so root can call them individually OR together
    tools=[
        AgentTool(agent=short_film_story_writer),
        AgentTool(agent=short_film_script_writer),
        AgentTool(agent=short_film_image_generator),
        AgentTool(agent=film_production_pipeline),
        AgentTool(agent=search_agent),
    ]
)