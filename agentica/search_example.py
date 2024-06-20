import os
from core.agent import Agent
from web.search import SearchEnvironment, SearchAction
from core.types import ModelConfig

# Initialize the search environment and agent
env = SearchEnvironment()
model_config = ModelConfig()
system_prompt = """You are a web research agent who will search the web and assist the user in all of their web search needs."""
agent = Agent(system_prompt=system_prompt, model_config=model_config, environment=env)

# Create a search action
search_action = SearchAction(action="search", query="Things to do in Austin Texas Today")

# Execute the search action (uncomment the next line to execute)
# env.execute(search_action)

# Run the agent with a specific query
outcome = agent.run("Can you find find me events in Austin today?")

# Print the outcome
print("Task Outcome:", outcome.status)
print("Message:", outcome.message)
