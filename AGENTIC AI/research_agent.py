"""
Research Agent - Gathers information from various sources
"""
import json
import re
from typing import Any, Dict, List
from .base_agent import BaseAgent
from memory.shared_memory import SharedMemory
from tools.web_search import WebSearchTool
from tools.file_reader import FileReaderTool


class ResearchAgent(BaseAgent):
    """
    The Research Agent gathers information from:
    - Web searches
    - Local files
    - Its own knowledge base
    """
    
    def __init__(self, memory: SharedMemory):
        super().__init__(
            name="researcher",
            role="Information Researcher",
            memory=memory,
            temperature=0.2  # Low temperature for factual research
        )
        self.web_search = WebSearchTool()
        self.file_reader = FileReaderTool()
    
    def _build_system_prompt(self) -> str:
        return """You are the Research Agent in a multi-agent AI system called AMARDS.

Your role is to:
1. Gather relevant information based on the plan
2. Search the web for current/accurate data
3. Read local files when relevant
4. Synthesize information from multiple sources
5. Identify gaps in available information

You have access to:
- Web search tool: Search the internet for information
- File reader tool: Read local text/code files
- Your own knowledge base

When researching:
- Focus on authoritative and reliable sources
- Note the source of each piece of information
- Flag any conflicting information found
- Identify what information is still missing

Output Format:
{
    "research_summary": "Brief overview of what was found",
    "findings": [
        {
            "topic": "What this finding is about",
            "content": "The actual information",
            "source": "Where this came from",
            "confidence": "high|medium|low",
            "timestamp": "If time-sensitive, when this was current"
        }
    ],
    "gaps": ["List of information that couldn't be found"],
    "conflicts": ["Any conflicting information discovered"],
    "recommendations": ["Suggestions for additional research if needed"]
}"""
    
    async def execute(self, input_data: Any) -> Dict[str, Any]:
        """
        Research information based on the plan
        
        Args:
            input_data: Dictionary containing research queries and plan
            
        Returns:
            Dictionary containing research findings
        """
        self._log_action("starting_research", input_data)
        
        # Get research queries from plan
        plan = input_data.get("plan", {})
        research_queries = plan.get("research_queries", [])
        original_query = self.memory.task_state.original_query
        
        # If no specific queries, use the original
        if not research_queries:
            research_queries = [original_query]
        
        # Perform web searches
        web_results = []
        for query in research_queries[:5]:  # Limit to 5 searches
            self._log_action("searching_web", query)
            result = self.web_search.search(query, max_results=3)
            web_results.append({
                "query": query,
                "result": result
            })
        
        # Synthesize findings with LLM
        synthesis_prompt = f"""Based on the following research data, synthesize the key findings:

ORIGINAL QUERY: {original_query}

RESEARCH PLAN: {json.dumps(plan, indent=2)}

WEB SEARCH RESULTS:
{json.dumps(web_results, indent=2)}

Analyze this information and provide a structured summary. Focus on:
1. Key facts and data points
2. Different perspectives or approaches
3. Any gaps or missing information
4. Conflicting information if any

Respond with valid JSON following the output format."""
        
        response = self._call_llm(synthesis_prompt)
        
        # Parse response
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                findings = json.loads(json_match.group())
            else:
                findings = self._create_fallback_findings(web_results)
        except json.JSONDecodeError:
            findings = self._create_fallback_findings(web_results)
        
        # Add raw data reference
        findings["raw_web_results"] = web_results
        
        # Update memory
        self.memory.update_state(
            research_data=findings,
            status="research_complete",
            current_step=self.memory.task_state.current_step + 1
        )
        
        self._log_action("research_complete", {
            "findings_count": len(findings.get("findings", [])),
            "gaps_count": len(findings.get("gaps", []))
        })
        
        return {
            "success": True,
            "findings": findings,
            "sources_used": len(web_results)
        }
    
    def _create_fallback_findings(self, web_results: List[Dict]) -> Dict:
        """Create fallback findings if parsing fails"""
        findings = []
        for wr in web_results:
            if wr["result"].get("success"):
                for item in wr["result"].get("results", [])[:2]:
                    findings.append({
                        "topic": wr["query"],
                        "content": item.get("content", ""),
                        "source": item.get("url", "web search"),
                        "confidence": "medium"
                    })
        
        return {
            "research_summary": "Research gathered from web sources",
            "findings": findings,
            "gaps": [],
            "conflicts": [],
            "recommendations": []
        }
 
