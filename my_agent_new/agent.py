from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import google_search

short_film_story_writer = RemoteA2aAgent(
    name="short_film_story_writer",
    description="Crafts a story. The output will be stored as 'film_story' in the pipeline state.",
    agent_card="https://storyteller-475756125529.us-central1.run.app/anime/.well-known/agent.json"
)

short_film_script_writer = RemoteA2aAgent(
    name="short_film_script_writer",
    description="Writes a script. It should use the {film_story} found in the state.",
    agent_card="https://short-film-script-writer-475756125529.us-central1.run.app/anime/.well-known/agent.json"
)

short_film_image_generator = RemoteA2aAgent(
    name="short_film_image_generator",
    description="Generates images. It should use the {film_script} found in the state.",
    agent_card="https://image-generator-agent-475756125529.us-central1.run.app/anime/.well-known/agent.json"
)
# ── Full pipeline (story → script → images) ──────────────────────────────────

film_production_pipeline = SequentialAgent(
    name="film_production_pipeline",
    description="Full short film pipeline: writes story, then script, then generates images.",
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

# ── Remote agents ────────────────────────────────────────────────────────────
# We define them without output_key to ensure they deploy.
# We use the description to tell the pipeline how to pass data.


# ── Root agent ────────────────────────────────────────────────────────────────

root_agent = Agent(
    model='gemini-2.5-flash',
    name='master_agent',
    description='Short film production coordinator.',
    instruction="""
        You are a short film production coordinator. 
        
        When a user wants the "full film" or "everything":
        1. Call the film_production_pipeline.
        2. IMPORTANT: The pipeline returns a state containing 'film_story', 'film_script', and the images.
        3. Your final response MUST combine all three. Do not just show the images.
        
        Format your response like this:
        ## Story
        [Insert story here]
        ---
        ## Script
        [Insert script here]
        ---
        ## Visuals
        [Insert image links/descriptions here]
    """,
    tools=[
        AgentTool(agent=short_film_story_writer),
        AgentTool(agent=short_film_script_writer),
        AgentTool(agent=short_film_image_generator),
        AgentTool(agent=film_production_pipeline),
        AgentTool(agent=search_agent),
    ]
)