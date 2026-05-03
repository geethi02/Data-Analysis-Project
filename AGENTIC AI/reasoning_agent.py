"""
Reasoning Agent - Analyzes information and draws conclusions
"""
import json
import re
from typing import Any, Dict
from .base_agent import BaseAgent
from memory.shared_memory import SharedMemory
from tools.calculator import CalculatorTool


class ReasoningAgent(BaseAgent):
    """
    The Reasoning Agent:
    - Analyzes research findings
    - Applies logic and critical thinking
    - Compares options when needed
    - Draws evidence-based conclusions
    """
    
    def __init__(self, memory: SharedMemory):
        super().__init__(
            name="reasoner",
            role="Analytical Reasoner",
            memory=memory,
            temperature=0.4  # Balanced for analytical thinking
        )
        self.calculator = CalculatorTool()
    
    def _build_system_prompt(self) -> str:
        return """You are the Reasoning Agent in a multi-agent AI system called AMARDS.

Your role is to:
1. Analyze the research findings critically
2. Apply logical reasoning to draw conclusions
3. Compare options and alternatives when relevant
4. Identify cause-effect relationships
5. Make evidence-based recommendations

Reasoning Framework:
- Start with clear premises from the research
- Apply deductive and inductive reasoning
- Consider multiple perspectives
- Acknowledge uncertainty when appropriate
- Distinguish between facts, inferences, and opinions

When reasoning about:
- Comparisons: Create structured evaluations with clear criteria
- Decisions: Weigh pros/cons with explicit reasoning
- Explanations: Build logical chains from evidence to conclusion
- Predictions: State assumptions and confidence levels

Output Format:
{
    "reasoning_summary": "Brief overview of the analysis",
    "key_insights": [
        {
            "insight": "The actual insight or conclusion",
            "evidence": "What supports this",
            "confidence": "high|medium|low",
            "reasoning_type": "deductive|inductive|analogical|causal"
        }
    ],
    "comparisons": [
        {
            "items_compared": ["item1", "item2"],
            "criteria": ["criterion1", "criterion2"],
            "evaluation": "Structured comparison"
        }
    ],
    "conclusions": [
        {
            "statement": "The conclusion",
            "strength": "strong|moderate|tentative",
            "caveats": ["Any limitations or conditions"]
        }
    ],
    "recommendations": ["Actionable recommendations based on analysis"],
    "uncertainties": ["Areas where more information would help"]
}"""
    
    async def execute(self, input_data: Any) -> Dict[str, Any]:
        """
        Analyze research findings and draw conclusions
        
        Args:
            input_data: Dictionary containing research findings
            
        Returns:
            Dictionary containing reasoning output
        """
        self._log_action("starting_reasoning", "Beginning analysis")
        
        # Get context
        original_query = self.memory.task_state.original_query
        plan = self.memory.task_state.plan
        research_data = self.memory.task_state.research_data
        
        # Build reasoning prompt
        reasoning_prompt = f"""Analyze the following research and provide reasoned conclusions:

ORIGINAL QUERY: {original_query}

PLAN CONTEXT:
{json.dumps(plan, indent=2) if plan else "No specific plan"}

RESEARCH FINDINGS:
{json.dumps(research_data, indent=2)}

Your task:
1. Analyze the research findings thoroughly
2. Apply logical reasoning to address the user's query
3. Draw clear, evidence-based conclusions
4. Identify any gaps or uncertainties in your reasoning
5. Provide actionable recommendations if applicable

Think step by step and show your reasoning. Respond with valid JSON."""
        
        response = self._call_llm(reasoning_prompt)
        
        # Parse response
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                reasoning = json.loads(json_match.group())
            else:
                reasoning = self._create_fallback_reasoning(response)
        except json.JSONDecodeError:
            reasoning = self._create_fallback_reasoning(response)
        
        # Store raw response for transparency
        reasoning["raw_reasoning"] = response
        
        # Update memory
        self.memory.update_state(
            reasoning_output=json.dumps(reasoning),
            status="reasoning_complete",
            current_step=self.memory.task_state.current_step + 1
        )
        
        self._log_action("reasoning_complete", {
            "insights_count": len(reasoning.get("key_insights", [])),
            "conclusions_count": len(reasoning.get("conclusions", []))
        })
        
        return {
            "success": True,
            "reasoning": reasoning,
            "confidence": self._calculate_overall_confidence(reasoning)
        }
    
    def _create_fallback_reasoning(self, raw_response: str) -> Dict:
        """Create fallback reasoning if parsing fails"""
        return {
            "reasoning_summary": "Analysis based on available information",
            "key_insights": [
                {
                    "insight": raw_response[:500] if len(raw_response) > 500 else raw_response,
                    "evidence": "Based on research findings",
                    "confidence": "medium",
                    "reasoning_type": "inductive"
                }
            ],
            "comparisons": [],
            "conclusions": [
                {
                    "statement": "See detailed analysis above",
                    "strength": "moderate",
                    "caveats": ["Unable to structure response fully"]
                }
            ],
            "recommendations": [],
            "uncertainties": ["Response structure was imperfect"]
        }
    
    def _calculate_overall_confidence(self, reasoning: Dict) -> str:
        """Calculate overall confidence from insights"""
        insights = reasoning.get("key_insights", [])
        if not insights:
            return "low"
        
        confidence_scores = {"high": 3, "medium": 2, "low": 1}
        total = sum(
            confidence_scores.get(i.get("confidence", "medium"), 2)
            for i in insights
        )
        avg = total / len(insights)
        
        if avg >= 2.5:
            return "high"
        elif avg >= 1.5:
            return "medium"
        return "low"

