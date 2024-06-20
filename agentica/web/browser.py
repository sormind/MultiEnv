from core.executable_environment import ExecutableEnvironment
from core.types import TaskOutcome

class WebExecutableEnviornment(ExecutableEnvironment):
    def __init__(self):
        self.browser = None