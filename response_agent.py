"""
Response Agent - Formats the final output for the user
"""
import json
import re
from typing import Any, Dict
from .base_agent import BaseAgent
from memory.shared_memory import SharedMemory


class ResponseAgent(BaseAgent):
    """
    The Response Agent:
    - Converts analysis into user-friendly output
    - Structures the response appropriately
    - Ensures clarity and readability
    - Adds citations where appropriate
    """
    
    def __init__(self, memory: SharedMemory):
        super().__init__(
            name="responder",
            role="Response Formatter",
            memory=memory,
            temperature=0.6  # Slightly higher for natural language
        )
    
    def _build_system_prompt(self) -> str:
        return """You are the Response Agent in a multi-agent AI system called AMARDS.

Your role is to:
1. Transform the analysis into a clear, well-structured response
2. Write in natural, engaging language
3. Organize information logically
4. Include relevant examples or illustrations
5. Add citations for factual claims when sources are available
6. Match the tone to the user's query (formal, casual, technical, etc.)

Guidelines:
- Lead with the most important information
- Use headers and bullet points for complex topics
- Keep paragraphs focused and readable
- Explain technical terms when necessary
- Be concise but complete
- End with actionable takeaways if relevant

DO NOT:
- Include internal system references
- Mention "agents" or the multi-agent system
- Add unnecessary caveats or hedging
- Include JSON or technical artifacts in the response

Your output should read as if a knowledgeable expert wrote it directly for the user."""
    
    async def execute(self, input_data: Any) -> Dict[str, Any]:
        """
        Format the final response for the user
        
        Args:
            input_data: Dictionary containing all analysis data
            
        Returns:
            Dictionary containing the formatted response
        """
        self._log_action("formatting_response", "Creating final output")
        
        # Gather all context
        original_query = self.memory.task_state.original_query
        research_data = self.memory.task_state.research_data
        reasoning = input_data.get("reasoning", {})
        critique = self.memory.task_state.critic_feedback
        
        # Build formatting prompt
        format_prompt = f"""Create a polished response for this user query:

ORIGINAL QUERY: {original_query}

RESEARCH FINDINGS:
{json.dumps(research_data, indent=2) if research_data else "General knowledge used"}

ANALYSIS AND CONCLUSIONS:
{json.dumps(reasoning, indent=2)}

QUALITY NOTES (for context, don't mention to user):
{json.dumps(critique, indent=2) if critique else "No specific feedback"}

Create a response that:
1. Directly addresses the user's question
2. Is well-organized and easy to read
3. Includes specific facts and examples from the research
4. Uses appropriate formatting (headers, bullets, etc.) if helpful
5. Cites sources naturally when making factual claims
6. Maintains a helpful, knowledgeable tone

Write the response as if you are directly answering the user. Do not include any meta-commentary about the response or the system."""
        
        response = self._call_llm(format_prompt)
        
        # Clean up the response
        final_response = self._clean_response(response)
        
        # Update memory
        self.memory.update_state(
            final_response=final_response,
            status="completed"
        )
        
        self._log_action("response_complete", {
            "response_length": len(final_response),
            "word_count": len(final_response.split())
        })
        
        return {
            "success": True,
            "response": final_response,
            "word_count": len(final_response.split())
        }
    
    def _clean_response(self, response: str) -> str:
        """Clean up the response text"""
        # Remove any JSON artifacts
        response = re.sub(r'```json\s*[\s\S]*?```', '', response)
        
        # Remove common meta-phrases
        meta_phrases = [
            r"^(Here's|Here is) (a |an |the )?(comprehensive |detailed )?response[:\s]*",
            r"^Based on (the |my )?analysis[,:\s]*",
            r"^After reviewing[^,]*,\s*",
        ]
        for pattern in meta_phrases:
            response = re.sub(pattern, '', response, flags=re.IGNORECASE | re.MULTILINE)
        
        return response.strip()

