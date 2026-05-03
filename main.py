"""
AMARDS - Autonomous Multi-Agent Research & Decision System
Main entry point
"""
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from config import Config
from orchestrator import AgentOrchestrator


def print_banner(console: Console):
    """Print the AMARDS banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     █████╗ ███╗   ███╗ █████╗ ██████╗ ██████╗ ███████╗       ║
    ║    ██╔══██╗████╗ ████║██╔══██╗██╔══██╗██╔══██╗██╔════╝       ║
    ║    ███████║██╔████╔██║███████║██████╔╝██║  ██║███████╗       ║
    ║    ██╔══██║██║╚██╔╝██║██╔══██║██╔══██╗██║  ██║╚════██║       ║
    ║    ██║  ██║██║ ╚═╝ ██║██║  ██║██║  ██║██████╔╝███████║       ║
    ║    ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝       ║
    ║                                                               ║
    ║    Autonomous Multi-Agent Research & Decision System          ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def print_help(console: Console):
    """Print help information"""
    help_text = """
[bold]Commands:[/bold]
  [cyan]help[/cyan]     - Show this help message
  [cyan]agents[/cyan]   - Show information about the agents
  [cyan]example[/cyan]  - See example queries
  [cyan]clear[/cyan]    - Clear the screen
  [cyan]quit[/cyan]     - Exit the program

[bold]How it works:[/bold]
Enter any question or research topic, and AMARDS will:
1. 🧾 Plan - Break down your query into steps
2. 🔍 Research - Gather relevant information
3. 🧠 Reason - Analyze and draw conclusions
4. ✅ Critique - Verify quality and accuracy
5. 🗣️ Respond - Deliver a polished answer
    """
    console.print(Panel(help_text, title="[bold green]AMARDS Help[/bold green]", expand=False))


def print_agents_info(console: Console):
    """Print information about the agents"""
    agents_text = """
[bold cyan]🧾 Planner Agent[/bold cyan]
   Analyzes your query and creates a structured action plan.
   Determines what information needs to be researched.

[bold cyan]🔍 Research Agent[/bold cyan]
   Searches the web and gathers relevant information.
   Synthesizes data from multiple sources.

[bold cyan]🧠 Reasoning Agent[/bold cyan]
   Applies logical analysis to the research findings.
   Draws evidence-based conclusions and recommendations.

[bold cyan]✅ Critic Agent[/bold cyan]
   Reviews output for accuracy and completeness.
   Triggers revisions if quality is below threshold.

[bold cyan]🗣️ Response Agent[/bold cyan]
   Transforms analysis into clear, readable output.
   Formats the final response for you.
    """
    console.print(Panel(agents_text, title="[bold green]The AMARDS Agents[/bold green]", expand=False))


def print_examples(console: Console):
    """Print example queries"""
    examples = """
[bold]Try asking:[/bold]

[italic]Research & Analysis:[/italic]
• "What are the latest developments in quantum computing?"
• "Compare electric vehicles: Tesla Model 3 vs BMW i4 vs Mercedes EQE"
• "Explain the pros and cons of remote work for software teams"

[italic]Decision Support:[/italic]
• "Should I learn Python or JavaScript as my first programming language?"
• "What factors should I consider when choosing a cloud provider?"
• "Analyze the investment potential of renewable energy stocks"

[italic]Complex Questions:[/italic]
• "How will AI impact the job market in the next 10 years?"
• "What are the best practices for building scalable microservices?"
• "Explain the current state of nuclear fusion research"
    """
    console.print(Panel(examples, title="[bold green]Example Queries[/bold green]", expand=False))


def main():
    """Main function to run AMARDS"""
    console = Console()
    
    # Print banner
    print_banner(console)
    
    # Validate configuration
    try:
        Config()
        console.print("[green]✓ Configuration validated[/green]\n")
    except ValueError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        console.print("[yellow]Please set up your .env file with required API keys.[/yellow]")
        sys.exit(1)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator(verbose=True)
    
    console.print("[dim]Type 'help' for commands, or enter your question.[/dim]\n")
    
    # Main loop
    while True:
        try:
            # Get user input
            query = Prompt.ask("\n[bold green]You[/bold green]")
            query = query.strip()
            
            if not query:
                continue
            
            # Handle commands
            if query.lower() == 'quit' or query.lower() == 'exit':
                console.print("\n[cyan]Goodbye! 👋[/cyan]\n")
                break
            elif query.lower() == 'help':
                print_help(console)
                continue
            elif query.lower() == 'agents':
                print_agents_info(console)
                continue
            elif query.lower() == 'example' or query.lower() == 'examples':
                print_examples(console)
                continue
            elif query.lower() == 'clear':
                console.clear()
                print_banner(console)
                continue
            
            # Process the query
            result = orchestrator.process_query_sync(query)
            
            if not result["success"]:
                console.print(f"\n[red]Error: {result.get('error', 'Unknown error')}[/red]")
            
        except KeyboardInterrupt:
            console.print("\n\n[cyan]Interrupted. Type 'quit' to exit.[/cyan]")
        except Exception as e:
            console.print(f"\n[red]Unexpected error: {e}[/red]")


if __name__ == "__main__":
    main()
 
