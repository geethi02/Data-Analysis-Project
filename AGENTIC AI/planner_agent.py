"""
Planner Agent - Breaks complex problems into actionable steps
"""
import json
import re
from typing import Any, Dict, List
from .base_agent import BaseAgent
from memory.shared_memory import SharedMemory


class PlannerAgent(BaseAgent):
    """
    The Planner Agent analyzes user queries and creates
    a structured plan of action for other agents to follow.
    """
    
    def __init__(self, memory: SharedMemory):
        super().__init__(
            name="planner",
            role="Strategic Planner",
            memory=memory,
            temperature=0.3  # Lower temperature for more focused planning
        )
    
    def _build_system_prompt(self) -> str:
        return """You are the Planner Agent in a multi-agent AI system called AMARDS.

Your role is to:
1. Analyze the user's query to understand their true intent
2. Break down complex problems into clear, actionable steps
3. Determine what information needs to be researched
4. Create a logical sequence of tasks for other agents

When creating a plan, consider:
- What facts need to be gathered? (Research Agent tasks)
- What analysis or comparisons are needed? (Reasoning Agent tasks)
- What potential issues might arise? (Critic Agent concerns)
- How should the final answer be structured? (Response Agent format)

Output Format:
You must respond with a JSON object containing:
{
    "query_analysis": "Your understanding of what the user wants",
    "complexity": "simple|moderate|complex",
    "requires_research": true/false,
    "research_queries": ["list of specific things to research"],
    "plan_steps": [
        "Step 1: Description of first task",
        "Step 2: Description of second task",
        ...
    ],
    "expected_output_format": "description of how the answer should be formatted",
    "potential_challenges": ["list of potential issues to watch for"]
}

Be thorough but efficient. Don't create unnecessary steps."""
    
    async def execute(self, input_data: Any) -> Dict[str, Any]:
        """
        Create a plan for handling the user's query
        
        Args:
            input_data: The user's original query string
            
        Returns:
            Dictionary containing the plan
        """
        self._log_action("received_query", input_data)
        
        # Create the planning prompt
        prompt = f"""Create a detailed plan to answer this query:

USER QUERY: {input_data}

Analyze this query and create a structured plan. Remember to output valid JSON."""
        
        # Get plan from LLM
        response = self._call_llm(prompt, include_context=False)
        
        # Parse the response
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                plan = json.loads(json_match.group())
            else:
                # Fallback: create a simple plan
                plan = self._create_fallback_plan(input_data, response)
        except json.JSONDecodeError:
            plan = self._create_fallback_plan(input_data, response)
        
        # Update memory with the plan
        self.memory.update_state(
            original_query=input_data,
            plan=plan.get("plan_steps", []),
            total_steps=len(plan.get("plan_steps", [])),
            current_step=1,
            status="planning_complete"
        )
        
        self._log_action("plan_created", plan)
        
        return {
            "success": True,
            "plan": plan,
            "step_count": len(plan.get("plan_steps", [])),
            "requires_research": plan.get("requires_research", True)
        }
    
    def _create_fallback_plan(self, query: str, llm_response: str) -> Dict:
        """Create a simple fallback plan if JSON parsing fails"""
        return {
            "query_analysis": f"User wants to know about: {query}",
            "complexity": "moderate",
            "requires_research": True,
            "research_queries": [query],
            "plan_steps": [
                "Research the main topic",
                "Analyze gathered information",
                "Verify accuracy of findings",
                "Prepare comprehensive response"
            ],
            "expected_output_format": "Clear, structured explanation",
            "potential_challenges": ["Information may be incomplete"],
            "raw_llm_response": llm_response
        }

