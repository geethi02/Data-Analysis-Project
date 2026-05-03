"""
File Reader Tool - Allows agents to read local files
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path


class FileReaderTool:
    """Tool for reading local files"""
    
    ALLOWED_EXTENSIONS = {'.txt', '.md', '.json', '.csv', '.py', '.js', '.html', '.css'}
    MAX_FILE_SIZE = 1024 * 1024  # 1MB
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()
    
    def read_file(self, filepath: str) -> Dict[str, Any]:
        """
        Read contents of a file
        
        Args:
            filepath: Path to the file (relative to base_path)
            
        Returns:
            Dictionary with file contents or error
        """
        try:
            # Resolve and validate path
            full_path = (self.base_path / filepath).resolve()
            
            # Security check - prevent directory traversal
            if not str(full_path).startswith(str(self.base_path)):
                return {
                    "success": False,
                    "error": "Access denied: Path outside allowed directory",
                    "filepath": filepath
                }
            
            # Check if file exists
            if not full_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {filepath}",
                    "filepath": filepath
                }
            
            # Check extension
            if full_path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
                return {
                    "success": False,
                    "error": f"File type not allowed: {full_path.suffix}",
                    "filepath": filepath
                }
            
            # Check file size
            if full_path.stat().st_size > self.MAX_FILE_SIZE:
                return {
                    "success": False,
                    "error": "File too large (max 1MB)",
                    "filepath": filepath
                }
            
            # Read file
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "filepath": filepath,
                "content": content,
                "size": len(content),
                "extension": full_path.suffix
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filepath": filepath
            }
    
    def list_files(self, directory: str = ".") -> Dict[str, Any]:
        """List files in a directory"""
        try:
            full_path = (self.base_path / directory).resolve()
            
            if not str(full_path).startswith(str(self.base_path)):
                return {"success": False, "error": "Access denied"}
            
            if not full_path.is_dir():
                return {"success": False, "error": "Not a directory"}
            
            files = []
            for item in full_path.iterdir():
                if item.is_file() and item.suffix.lower() in self.ALLOWED_EXTENSIONS:
                    files.append({
                        "name": item.name,
                        "size": item.stat().st_size,
                        "extension": item.suffix
                    })
            
            return {
                "success": True,
                "directory": directory,
                "files": files,
                "count": len(files)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
 
