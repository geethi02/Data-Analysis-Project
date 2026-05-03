"""
Critic Agent - Validates and improves the quality of outputs
"""
import json
import re
from typing import Any, Dict
from .base_agent import BaseAgent
from memory.shared_memory import SharedMemory
from config import Config


class CriticAgent(BaseAgent):
    """
    The Critic Agent:
    - Reviews outputs from other agents
    - Checks for accuracy and completeness
    - Identifies logical flaws or gaps
    - Suggests improvements
    - Decides if output meets quality threshold
    """
    
    def __init__(self, memory: SharedMemory):
        super().__init__(
            name="critic",
            role="Quality Critic",
            memory=memory,
            temperature=0.2  # Low temperature for critical analysis
        )
        self.quality_threshold = Config.CRITIC_THRESHOLD
    
    def _build_system_prompt(self) -> str:
        return """You are the Critic Agent in a multi-agent AI system called AMARDS.

Your role is to:
1. Review the reasoning and conclusions of other agents
2. Check for factual accuracy and logical consistency
3. Identify gaps, errors, or weak arguments
4. Verify that the original query is fully addressed
5. Suggest specific improvements
6. Make a pass/fail decision based on quality

Evaluation Criteria:
- ACCURACY: Are the facts correct? Are sources reliable?
- COMPLETENESS: Does it fully answer the query?
- LOGIC: Is the reasoning sound? Are conclusions justified?
- CLARITY: Is the response clear and understandable?
- RELEVANCE: Does it stay focused on the user's needs?

Be constructive but rigorous. Your job is to catch problems before they reach the user.

Output Format:
{
    "evaluation_summary": "Overall assessment of quality",
    "scores": {
        "accuracy": 0.0-1.0,
        "completeness": 0.0-1.0,
        "logic": 0.0-1.0,
        "clarity": 0.0-1.0,
        "relevance": 0.0-1.0
    },
    "overall_score": 0.0-1.0,
    "issues_found": [
        {
            "severity": "critical|major|minor",
            "category": "accuracy|completeness|logic|clarity|relevance",
            "description": "What the issue is",
            "location": "Where in the response",
            "suggestion": "How to fix it"
        }
    ],
    "strengths": ["What was done well"],
    "improvements_required": ["Specific changes needed"],
    "verdict": "pass|revise|fail",
    "revision_guidance": "If revise, specific instructions for improvement"
}"""
    
    async def execute(self, input_data: Any) -> Dict[str, Any]:
        """
        Critique the current output
        
        Args:
            input_data: Dictionary containing reasoning output to critique
            
        Returns:
            Dictionary containing critique and verdict
        """
        self._log_action("starting_critique", "Beginning quality review")
        
        # Gather all context
        original_query = self.memory.task_state.original_query
        plan = self.memory.task_state.plan
        research_data = self.memory.task_state.research_data
        reasoning = input_data.get("reasoning", {})
        
        # Build critique prompt
        critique_prompt = f"""Review the following AI-generated analysis for quality:

ORIGINAL USER QUERY: {original_query}

PLAN THAT WAS FOLLOWED:
{json.dumps(plan, indent=2) if plan else "No specific plan"}

RESEARCH GATHERED:
{json.dumps(research_data, indent=2) if research_data else "No research data"}

REASONING AND CONCLUSIONS:
{json.dumps(reasoning, indent=2)}

Your task:
1. Evaluate if this adequately answers the user's query
2. Check factual accuracy (flag anything that seems wrong or unsupported)
3. Assess logical consistency
4. Identify any gaps or missing information
5. Rate overall quality
6. Decide: pass (ready for user), revise (needs improvement), or fail (start over)

Quality threshold for passing: {self.quality_threshold}

Be thorough and critical. Respond with valid JSON."""
        
        response = self._call_llm(critique_prompt)
        
        # Parse response
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                critique = json.loads(json_match.group())
            else:
                critique = self._create_fallback_critique(response)
        except json.JSONDecodeError:
            critique = self._create_fallback_critique(response)
        
        # Ensure required fields
        critique = self._normalize_critique(critique)
        
        # Update memory
        self.memory.update_state(
            critic_feedback=critique,
            status="critique_complete",
            current_step=self.memory.task_state.current_step + 1
        )
        
        self._log_action("critique_complete", {
            "verdict": critique.get("verdict", "unknown"),
            "overall_score": critique.get("overall_score", 0),
            "issues_count": len(critique.get("issues_found", []))
        })
        
        return {
            "success": True,
            "critique": critique,
            "passed": critique.get("verdict") == "pass",
            "needs_revision": critique.get("verdict") == "revise",
            "overall_score": critique.get("overall_score", 0)
        }
    
    def _normalize_critique(self, critique: Dict) -> Dict:
        """Ensure critique has all required fields with valid values"""
        # Default scores
        default_scores = {
            "accuracy": 0.5,
            "completeness": 0.5,
            "logic": 0.5,
            "clarity": 0.5,
            "relevance": 0.5
        }
        
        scores = critique.get("scores", default_scores)
        
        # Ensure scores are floats
        for key in default_scores:
            if key not in scores or not isinstance(scores[key], (int, float)):
                scores[key] = default_scores[key]
            scores[key] = max(0.0, min(1.0, float(scores[key])))
        
        # Calculate overall if not present
        overall = critique.get("overall_score")
        if overall is None or not isinstance(overall, (int, float)):
            overall = sum(scores.values()) / len(scores)
        overall = max(0.0, min(1.0, float(overall)))
        
        # Determine verdict if not present
        verdict = critique.get("verdict", "").lower()
        if verdict not in ["pass", "revise", "fail"]:
            if overall >= self.quality_threshold:
                verdict = "pass"
            elif overall >= self.quality_threshold - 0.2:
                verdict = "revise"
            else:
                verdict = "fail"
        
        return {
            "evaluation_summary": critique.get("evaluation_summary", "Evaluation complete"),
            "scores": scores,
            "overall_score": overall,
            "issues_found": critique.get("issues_found", []),
            "strengths": critique.get("strengths", []),
            "improvements_required": critique.get("improvements_required", []),
            "verdict": verdict,
            "revision_guidance": critique.get("revision_guidance", "")
        }
    
    def _create_fallback_critique(self, raw_response: str) -> Dict:
        """Create fallback critique if parsing fails"""
        return {
            "evaluation_summary": "Automated evaluation",
            "scores": {
                "accuracy": 0.6,
                "completeness": 0.6,
                "logic": 0.6,
                "clarity": 0.6,
                "relevance": 0.6
            },
            "overall_score": 0.6,
            "issues_found": [],
            "strengths": ["Analysis was attempted"],
            "improvements_required": ["Unable to fully parse critique"],
            "verdict": "pass",
            "revision_guidance": raw_response[:300] if raw_response else ""
        }
 
