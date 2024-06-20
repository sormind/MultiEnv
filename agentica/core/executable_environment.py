import logging

from pydantic import BaseModel
from core.types import EnvironmentResponse

# Create a logger instance with the name of the current module or script
logger = logging.getLogger(__name__)

# Set the logging level (optional, but recommended)
logger.setLevel(logging.INFO)

# Create a console handler
console_handler = logging.StreamHandler()

# Create a simple formatter
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# Add the formatter to the console handler
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)


class ExecutableEnvironment:
    def execute(self, llm_action: BaseModel) -> EnvironmentResponse:
        pass

    def format_action_model(self) -> BaseModel:
        pass

    def describe_state(self) -> str:
        pass

    def on_task_completion(self):
        pass


