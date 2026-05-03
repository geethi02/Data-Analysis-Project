"""
Agent Orchestrator - Controls the flow between agents
"""
import asyncio
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from memory.shared_memory import SharedMemory
from agents import (
    PlannerAgent,
    ResearchAgent,
    ReasoningAgent,
    CriticAgent,
    ResponseAgent
)
from config import Config


class AgentOrchestrator:
    """
    The Orchestrator controls the entire multi-agent workflow.
    It decides which agent runs next and handles the flow between them.
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.console = Console()
        self.memory = SharedMemory(max_entries=Config.MAX_MEMORY_ITEMS)
        
        # Initialize agents
        self.planner = PlannerAgent(self.memory)
        self.researcher = ResearchAgent(self.memory)
        self.reasoner = ReasoningAgent(self.memory)
        self.critic = CriticAgent(self.memory)
        self.responder = ResponseAgent(self.memory)
        
        self.max_iterations = Config.MAX_ITERATIONS
    
    def _log(self, message: str, style: str = ""):
        """Log a message if verbose mode is on"""
        if self.verbose:
            self.console.print(message, style=style)
    
    def _show_agent_status(self, agent_name: str, status: str):
        """Show which agent is currently active"""
        if self.verbose:
            emoji_map = {
                "planner": "🧾",
                "researcher": "🔍",
                "reasoner": "🧠",
                "critic": "✅",
                "responder": "🗣️"
            }
            emoji = emoji_map.get(agent_name, "🤖")
            self.console.print(f"\n{emoji} [bold cyan]{agent_name.upper()} AGENT[/bold cyan]: {status}")
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query through the multi-agent system
        
        Args:
            query: The user's question or task
            
        Returns:
            Dictionary containing the final response and metadata
        """
        # Reset memory for new query
        self.memory.reset()
        
        self._log(f"\n{'='*60}", "dim")
        self._log(Panel(query, title="[bold green]User Query[/bold green]", expand=False))
        
        try:
            # Phase 1: Planning
            self._show_agent_status("planner", "Creating execution plan...")
            plan_result = await self.planner.execute(query)
            
            if not plan_result["success"]:
                return self._error_response("Planning failed", plan_result)
            
            self._log(f"  → Plan created with {plan_result['step_count']} steps")
            
            # Phase 2: Research
            self._show_agent_status("researcher", "Gathering information...")
            research_result = await self.researcher.execute(plan_result)
            
            if not research_result["success"]:
                return self._error_response("Research failed", research_result)
            
            self._log(f"  → Research complete from {research_result['sources_used']} sources")
            
            # Phase 3-4: Reasoning + Critique Loop
            iteration = 0
            reasoning_result = None
            
            while iteration < self.max_iterations:
                iteration += 1
                self.memory.update_state(iteration=iteration)
                
                # Reasoning
                self._show_agent_status("reasoner", f"Analyzing (iteration {iteration})...")
                reasoning_result = await self.reasoner.execute(research_result)
                
                if not reasoning_result["success"]:
                    return self._error_response("Reasoning failed", reasoning_result)
                
                self._log(f"  → Analysis complete (confidence: {reasoning_result['confidence']})")
                
                # Critique
                self._show_agent_status("critic", "Reviewing quality...")
                critique_result = await self.critic.execute(reasoning_result)
                
                if not critique_result["success"]:
                    return self._error_response("Critique failed", critique_result)
                
                score = critique_result["overall_score"]
                verdict = critique_result["critique"]["verdict"]
                self._log(f"  → Quality score: {score:.2f} | Verdict: {verdict}")
                
                if critique_result["passed"]:
                    self._log("  → [green]Quality check passed![/green]")
                    break
                elif critique_result["needs_revision"]:
                    self._log("  → [yellow]Revision needed, improving...[/yellow]")
                    # Add revision guidance to research for next iteration
                    research_result["revision_guidance"] = critique_result["critique"].get("revision_guidance", "")
                else:
                    self._log("  → [red]Major issues found, attempting recovery...[/red]")
                    # Could trigger re-research here for failed attempts
            
            # Phase 5: Response
            self._show_agent_status("responder", "Formatting final response...")
            response_result = await self.responder.execute(reasoning_result)
            
            if not response_result["success"]:
                return self._error_response("Response formatting failed", response_result)
            
            self._log(f"  → Response ready ({response_result['word_count']} words)")
            
            # Show final response
            if self.verbose:
                self.console.print(f"\n{'='*60}", style="dim")
                self.console.print(Panel(
                    response_result["response"],
                    title="[bold green]Final Response[/bold green]",
                    expand=False,
                    padding=(1, 2)
                ))
            
            return {
                "success": True,
                "response": response_result["response"],
                "metadata": {
                    "iterations": iteration,
                    "quality_score": critique_result["overall_score"],
                    "sources_used": research_result["sources_used"],
                    "word_count": response_result["word_count"]
                },
                "session": self.memory.export_session()
            }
            
        except Exception as e:
            return self._error_response(f"System error: {str(e)}", {"exception": str(e)})
    
    def _error_response(self, message: str, details: Dict) -> Dict[str, Any]:
        """Create an error response"""
        self._log(f"\n[red]Error: {message}[/red]")
        return {
            "success": False,
            "response": f"I encountered an issue while processing your request: {message}",
            "error": message,
            "details": details
        }
    
    def process_query_sync(self, query: str) -> Dict[str, Any]:
        """Synchronous wrapper for process_query"""
        return asyncio.run(self.process_query(query))
 
