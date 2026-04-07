import logging
from typing import AsyncGenerator, Dict, Any
import os

# Import ADK components
from google.adk.agents import Agent, BaseAgent, LlmAgent, SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools import ToolContext, google_search
from google.adk.tools.agent_tool import AgentTool
from dotenv import load_dotenv

load_dotenv()

# --- 1. Define the Session-based Memory Tools ---
def save_user_preferences(tool_context: ToolContext, new_preferences: Dict[str, Any]) -> str:
    """Saves or updates user preferences (e.g., favorite genres, art styles) in the session."""
    current_preferences = tool_context.state.get('user_preferences') or {}
    current_preferences.update(new_preferences)
    tool_context.state['user_preferences'] = current_preferences
    return f"Preferences updated successfully: {new_preferences}"

def recall_user_preferences(tool_context: ToolContext) -> Dict[str, Any]:
    """Recalls all saved preferences for the current user from the session."""
    preferences = tool_context.state.get('user_preferences')
    if preferences:
        return preferences
    else:
        return {"message": "No preferences found for this user."}


# --- 2. Define the Remote Specialist Agents (The Crew) ---
# Note: These do not have output_key because they are remote microservices.
short_film_story_writer = RemoteA2aAgent(
    name="short_film_story_writer",
    description="Crafts a story based on user prompts and preferences.",
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


# --- 3. Define the Local Adapters (The Glue) ---
# These tiny agents catch the raw text from the remote agents and save it to the correct state keys.
story_adapter = Agent(
    name="story_adapter",
    model="gemini-2.5-flash",
    instruction="""
    You are a data router. Look at the immediate previous output.
    Extract the short film story that was just generated. 
    Output *only* the text of the story, with no conversational filler.
    """,
    output_key="film_story"  # Saves to state['film_story']
)

script_adapter = Agent(
    name="script_adapter",
    model="gemini-2.5-flash",
    instruction="""
    You are a data router. Look at the immediate previous output.
    Extract the short film script that was just generated. 
    Output *only* the text of the script, with no conversational filler.
    """,
    output_key="film_script" # Saves to state['film_script']
)


# --- 4. Define the Sequential Production Pipeline ---
film_production_pipeline = SequentialAgent(
    name="film_production_pipeline",
    description="Full short film pipeline: writes story, then script, then generates images.",
    sub_agents=[
        short_film_story_writer,    # Step 1: Remote generates raw story text
        story_adapter,              # Step 2: Local grabs text -> saves as 'film_story'
        short_film_script_writer,   # Step 3: Remote reads 'film_story' -> generates raw script text
        script_adapter,             # Step 4: Local grabs text -> saves as 'film_script'
        short_film_image_generator, # Step 5: Remote reads 'film_script' -> generates images
    ]
)


# --- 5. Define Local Support Agents ---
search_agent = Agent(
    model='gemini-2.5-flash',
    name='search_agent',
    description="Searches the web for references, research, or real-time information for the film.",
    instruction="Use Google Search to find accurate information. Summarize results clearly to aid in film production.",
    tools=[google_search],
)


# --- 6. Define the Supreme Studio Coordinator (Root Agent) ---
root_agent = Agent(
    model='gemini-2.5-flash',
    name='master_agent',
    description='Supreme short film production coordinator with memory and pipeline routing.',
    instruction="""
    You are an elite short film production coordinator orchestrating a team of specialized remote agents and workflows.

    1. RECALL: Always call `recall_user_preferences` first to check for the user's favorite genres, visual styles, or preferred themes.
    2. ROUTE THE REQUEST:
       - If the user needs research on a topic before writing, call the `search_agent`.
       - If the user wants a single asset (just a story, just a script, or just an image), call the respective remote agent directly.
       - If the user wants the "full film" or "everything", hand off the entire task to the `film_production_pipeline`.
    3. PRESENT & LEARN: 
       - IMPORTANT: If the pipeline is used, it returns a state containing 'film_story', 'film_script', and images. Your final response MUST combine all three beautifully. Do not just show the images.
       - Format your response like this:
         ## Story
         [Insert story here]
         ---
         ## Script
         [Insert script here]
         ---
         ## Visuals
         [Insert image links/descriptions here]
       - Ask if they are happy with the output and if they want to save any new preferences for future films.
    4. SAVE: If the user provides a new preference, call `save_user_preferences`.
    """,
    tools=[
        recall_user_preferences,
        save_user_preferences,
        AgentTool(agent=short_film_story_writer),
        AgentTool(agent=short_film_script_writer),
        AgentTool(agent=short_film_image_generator),
        AgentTool(agent=film_production_pipeline),
        AgentTool(agent=search_agent),
    ]
)

print("🎬 Ultimate Studio Orchestrator (with Memory, Adapters & Remote Pipelines) is ready for action.")