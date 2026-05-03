"""
Shared Memory - The brain that all agents can read and write to
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import json


class MemoryEntry(BaseModel):
    """Single memory entry"""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    agent: str
    action: str
    content: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskState(BaseModel):
    """Current state of the task being processed"""
    original_query: str = ""
    current_step: int = 0
    total_steps: int = 0
    plan: List[str] = Field(default_factory=list)
    research_data: Dict[str, Any] = Field(default_factory=dict)
    reasoning_output: str = ""
    critic_feedback: Dict[str, Any] = Field(default_factory=dict)
    final_response: str = ""
    status: str = "initialized"  # initialized, planning, researching, reasoning, critiquing, responding, completed, failed
    iteration: int = 0
    errors: List[str] = Field(default_factory=list)


class SharedMemory:
    """
    Shared memory system that all agents can access.
    Acts as the central nervous system of AMARDS.
    """
    
    def __init__(self, max_entries: int = 50):
        self.max_entries = max_entries
        self.entries: List[MemoryEntry] = []
        self.task_state = TaskState()
        self.agent_outputs: Dict[str, List[Any]] = {
            "planner": [],
            "researcher": [],
            "reasoner": [],
            "critic": [],
            "responder": []
        }
    
    def add_entry(self, agent: str, action: str, content: Any, metadata: Dict = None):
        """Add a new memory entry"""
        entry = MemoryEntry(
            agent=agent,
            action=action,
            content=content,
            metadata=metadata or {}
        )
        self.entries.append(entry)
        
        # Trim if exceeding max
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        
        # Store in agent-specific outputs
        if agent in self.agent_outputs:
            self.agent_outputs[agent].append({
                "action": action,
                "content": content,
                "timestamp": entry.timestamp
            })
    
    def get_recent_entries(self, n: int = 10, agent: str = None) -> List[MemoryEntry]:
        """Get recent memory entries, optionally filtered by agent"""
        entries = self.entries
        if agent:
            entries = [e for e in entries if e.agent == agent]
        return entries[-n:]
    
    def get_context_summary(self) -> str:
        """Get a summary of current context for agents"""
        summary = []
        summary.append(f"## Current Task State")
        summary.append(f"- Original Query: {self.task_state.original_query}")
        summary.append(f"- Status: {self.task_state.status}")
        summary.append(f"- Current Step: {self.task_state.current_step}/{self.task_state.total_steps}")
        summary.append(f"- Iteration: {self.task_state.iteration}")
        
        if self.task_state.plan:
            summary.append(f"\n## Plan:")
            for i, step in enumerate(self.task_state.plan, 1):
                marker = "✓" if i < self.task_state.current_step else "→" if i == self.task_state.current_step else "○"
                summary.append(f"  {marker} Step {i}: {step}")
        
        if self.task_state.research_data:
            summary.append(f"\n## Research Data Available: {len(self.task_state.research_data)} sources")
        
        if self.task_state.errors:
            summary.append(f"\n## Errors: {self.task_state.errors[-3:]}")  # Last 3 errors
        
        return "\n".join(summary)
    
    def update_state(self, **kwargs):
        """Update task state with new values"""
        for key, value in kwargs.items():
            if hasattr(self.task_state, key):
                setattr(self.task_state, key, value)
    
    def reset(self):
        """Reset memory for a new task"""
        self.entries = []
        self.task_state = TaskState()
        self.agent_outputs = {
            "planner": [],
            "researcher": [],
            "reasoner": [],
            "critic": [],
            "responder": []
        }
    
    def export_session(self) -> Dict:
        """Export the entire session for debugging or logging"""
        return {
            "task_state": self.task_state.model_dump(),
            "entries": [e.model_dump() for e in self.entries],
            "agent_outputs": self.agent_outputs
        }
 
