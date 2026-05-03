"""
Base Agent - Foundation class for all agents in AMARDS
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from memory.shared_memory import SharedMemory
from config import Config

class BaseAgent(ABC):
    """
    Base class for all agents.
    Every agent can:
    - Access shared memory
    - Call the LLM
    - Use tools
    - Log their actions
    """
    
    def __init__(
        self, 
        name: str,
        role: str,
        memory: SharedMemory,
        model_name: str = None,
        temperature: float = None
    ):
        self.name = name
        self.role = role
        self.memory = memory
        
        # Initialize LLM
        self.llm = ChatOpenAI(
    api_key=Config.OPENAI_API_KEY,
    base_url=Config.BASE_URL,   # ⭐ ADD THIS LINE
    model=Config.MODEL_NAME,
    temperature=Config.TEMPERATURE
)
        
        # Agent-specific system prompt
        self.system_prompt = self._build_system_prompt()
    
    @abstractmethod
    def _build_system_prompt(self) -> str:
        """Build the system prompt for this agent"""
        pass
    
    @abstractmethod
    async def execute(self, input_data: Any) -> Dict[str, Any]:
        """Execute the agent's main task"""
        pass
    
    def _call_llm(self, user_message: str, include_context: bool = True) -> str:
        """
        Call the LLM with the agent's system prompt
        
        Args:
            user_message: The message to send to the LLM
            include_context: Whether to include memory context
            
        Returns:
            The LLM's response
        """
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Add context from memory if requested
        if include_context:
            context = self.memory.get_context_summary()
            if context:
                messages.append(SystemMessage(content=f"Current Context:\n{context}"))
        
        messages.append(HumanMessage(content=user_message))
        
        response = self.llm.invoke(messages)
        return response.content
    
    def _log_action(self, action: str, content: Any, metadata: Dict = None):
        """Log an action to shared memory"""
        self.memory.add_entry(
            agent=self.name,
            action=action,
            content=content,
            metadata=metadata or {}
        )
    
    def _get_recent_context(self, n: int = 5) -> str:
        """Get recent memory entries as context string"""
        entries = self.memory.get_recent_entries(n)
        if not entries:
            return "No recent activity."
        
        context_parts = []
        for entry in entries:
            context_parts.append(f"[{entry.agent}] {entry.action}: {entry.content}")
        
        return "\n".join(context_parts)
 
