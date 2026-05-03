"""
Web Search Tool - Allows agents to search the internet
"""
from typing import List, Dict, Any, Optional
from config import Config

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False


class WebSearchTool:
    """Tool for searching the web"""
    
    def __init__(self):
        self.client = None
        if TAVILY_AVAILABLE and Config.TAVILY_API_KEY:
            self.client = TavilyClient(api_key=Config.TAVILY_API_KEY)
    
    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search the web for information
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with search results
        """
        if not self.client:
            return {
                "success": False,
                "error": "Web search not configured. Set TAVILY_API_KEY in .env",
                "results": [],
                "query": query
            }
        
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
                include_raw_content=False
            )
            
            results = []
            for item in response.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "score": item.get("score", 0)
                })
            
            return {
                "success": True,
                "query": query,
                "answer": response.get("answer", ""),
                "results": results,
                "result_count": len(results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "query": query
            }
    
    def search_multiple(self, queries: List[str], max_results_per_query: int = 3) -> List[Dict]:
        """Search multiple queries and combine results"""
        all_results = []
        for query in queries:
            result = self.search(query, max_results_per_query)
            all_results.append(result)
        return all_results
 
