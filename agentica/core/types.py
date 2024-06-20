from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

class ModelConfig(BaseModel):
    provider: str = "anthropic"
    model: str = "claude-3-opus-20240229"
    temperature: float = 0.3
    max_tokens: int = 4096

class CallingAgent(BaseModel):
    agent_id: str
    task_id: Optional[str] = None
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TaskOutcome(BaseModel):
    status: str = Field(default="running", description="The current status of the agent based on the task. set this to `running` if there are more tasks to take or `done` if there are no more tasks to take.")
    message: Optional[str] = Field(default=None, description="The Message regarding the outcome of the task and what you'd like to communicate to the user.")
    notes: Optional[str] = Field(default=None, description="Notes for yourself, this is where you can write down any notes that you want to remember for an ongoing task.")

class EnvironmentResponse(BaseModel):
    status: str
    return_value: Optional[Any] = None
    error: Optional[Any] = None

class AgentResponse(BaseModel):
    status: str = Field(default="running", description="The current status, one of ['running', 'done']")
    message: str = Field(default="", description="The Message from the agent, use this field to communicate with the user.")
