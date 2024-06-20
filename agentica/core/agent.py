import os
from typing import Optional, Union

from pydantic import BaseModel

from core.executable_environment import ExecutableEnvironment
from core.types import ModelConfig, TaskOutcome, AgentResponse, EnvironmentResponse
from core.model_provider import llm_response
import logging

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Agent:
    def __init__(self, system_prompt: str, model_config: ModelConfig,
                 environment: ExecutableEnvironment, verbose: bool = False):
        self.system = system_prompt
        self.response_model = environment.format_action_model()
        self.model_config = model_config
        self.env = environment
        self.verbose = verbose

    def llm_action(self, command: str, context) -> BaseModel:
        message = self._format_message(command, context)
        return llm_response(self.model_config, self.response_model, self.system, message)

    def _format_message(self, user_message, context) -> str:
        formatted_msg = f"Messsage:\n {user_message}"
        if context:
            formatted_msg += f"\n use the following context:\n{context}"
        return formatted_msg

    def run(self, user_command: str) -> TaskOutcome:
        running = True
        command = user_command
        while running:
            if self.verbose:
                logging.info(f"user_command - {command}")
            pre_task_context = self._pre_task_hook(command)
            agent_action = self.llm_action(command, context=pre_task_context)
            env_outcome = self.env.execute(agent_action)
            outcome = self._post_task_hook(agent_action, env_outcome)
            if self.verbose:
                logging.info(f"Agent Action: {agent_action.json()}")
                logging.info(f"Environment Outcome: {env_outcome.json()}")
            if outcome.status == "done":
                running = False
            else:
                command = outcome.message or "Ongoing task:"
                if outcome.notes:
                    command += f"\nnotes: {outcome.notes}"

                if env_outcome.return_value:
                    command += f"\nprevious task outcome: {env_outcome.return_value}"
                elif env_outcome.error:
                    command += f"\nprevious task error: {env_outcome.error}"
        
        self.env.on_task_completion()
        return outcome

    def _pre_task_hook(self, command: BaseModel):
        return  f"Enviornment state: {self.env.describe_state()}"

    def _post_task_hook(self, agent_action: BaseModel, outcome: EnvironmentResponse) -> TaskOutcome:
        formatted_agent_action = f"Agent Action: {agent_action.json()}"
        formatted_outcome = f"Outcome: {outcome.json()}"
        
        combined_message = f"{formatted_agent_action}\n{formatted_outcome}"
        
        task_outcome_response = llm_response(
            config=self.model_config,
            response_model=TaskOutcome,
            system=self.system,
            message=combined_message
        )
        if self.verbose:
            logging.info(f"Task Outcome: {task_outcome_response.json()}")
        return task_outcome_response

