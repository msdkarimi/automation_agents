from abc import ABC, abstractmethod


class BaseAgent(ABC):

    @abstractmethod
    def _build_graph(self,):
        pass

    @abstractmethod
    def invoke_agent(self,):
        pass
    
    @abstractmethod
    def save_state(self,) -> None:
        """Save the agent state to a file for persistence."""
        pass

    @abstractmethod
    def load_state(self, user_id: int):
        """Load the agent state from database."""
        pass