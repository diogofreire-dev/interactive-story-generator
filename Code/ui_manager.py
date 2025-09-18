"""
UI Manager Module - Handles all user interface display
"""

from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

class UIManager:
    def show_scene(self, scene, game_state):
        """Display a story scene"""
        # Scene title
        if "title" in scene:
            title_panel = Panel.fit(scene["title"], border_style="cyan")
            console.print(title_panel)
            console.print()
        
        # Scene description
        console.print(scene["description"])
        console.print()
        
        # Show choices
        if "choices" in scene:
            console.print("[bold]What do you want to do?[/bold]")
            for i, choice in enumerate(scene["choices"], 1):
                # Check if choice requires an item
                if "requires_item" in choice:
                    if choice["requires_item"] not in game_state["inventory"]:
                        console.print(f"[dim]{i}. {choice['text']} (requires {choice['requires_item']})[/dim]")
                        continue
                
                console.print(f"{i}. {choice['text']}")
            
            console.print()
            console.print("[dim]Commands: I (inventory), S (save), T (stats), Q (quit)[/dim]")

    def show_ending(self, scene, game_state):
        """Display ending scene with final statistics"""
        console.print(f"[bold green]{scene.get('ending_title', 'THE END')}[/bold green]")
        console.print()
        
        # Show ending description if available
        if "description" in scene:
            console.print(scene["description"])
            console.print()
        
        # Calculate final stats
        end_time = datetime.now()
        start_time = datetime.fromisoformat(game_state["start_time"])
        play_time = end_time - start_time
        
        # Show final statistics
        stats_table = Table(title="Final Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Play Time", str(play_time).split('.')[0])
        stats_table.add_row("Scenes Visited", str(len(game_state["visited_scenes"])))
        stats_table.add_row("Choices Made", str(len(game_state["choices_made"])))
        stats_table.add_row("Items Collected", str(game_state["items_collected"]))
        stats_table.add_row("Deaths", str(game_state["deaths"]))
        stats_table.add_row("Saves Used", str(game_state["saves_used"]))
        
        console.print(stats_table)
        console.print()

    def show_inventory(self, game_state):
        """Display player inventory"""
        console.print("[bold cyan]Inventory:[/bold cyan]")
        if game_state["inventory"]:
            for item in game_state["inventory"]:
                console.print(f"- {item}")
        else:
            console.print("Empty")
        console.print()

    def show_current_stats(self, game_state):
        """Display current game statistics"""
        current_time = datetime.now()
        start_time = datetime.fromisoformat(game_state["start_time"])
        play_time = current_time - start_time
        
        stats_table = Table(title="Current Game Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Player", game_state["player_name"])
        stats_table.add_row("Story", game_state["story_type"].title())
        stats_table.add_row("Current Play Time", str(play_time).split('.')[0])
        stats_table.add_row("Scenes Visited", str(len(game_state["visited_scenes"])))
        stats_table.add_row("Choices Made", str(len(game_state["choices_made"])))
        stats_table.add_row("Items Collected", str(game_state["items_collected"]))
        stats_table.add_row("Deaths", str(game_state["deaths"]))
        stats_table.add_row("Saves Used", str(game_state["saves_used"]))
        
        console.print(stats_table)
        console.print()

    def show_global_stats_display(self, stats):
        """Display global statistics"""
        console.print("[bold cyan]Global Statistics[/bold cyan]")
        console.print()
        
        # General stats
        general_table = Table(title="General Statistics")
        general_table.add_column("Metric", style="cyan")
        general_table.add_column("Value", style="green")
        
        general_table.add_row("Total Games Played", str(stats.get("total_games", 0)))
        general_table.add_row("Total Play Time", str(timedelta(seconds=stats.get("total_play_time_seconds", 0))))
        general_table.add_row("Average Game Time", str(timedelta(seconds=stats.get("average_game_time_seconds", 0))))
        general_table.add_row("Total Deaths", str(stats.get("total_deaths", 0)))
        general_table.add_row("Total Items Collected", str(stats.get("total_items_collected", 0)))
        
        console.print(general_table)
        console.print()
        
        # Stories completed
        if "stories_completed" in stats:
            stories_table = Table(title="Stories Completed")
            stories_table.add_column("Story", style="cyan")
            stories_table.add_column("Times Completed", style="green")
            
            for story, count in stats["stories_completed"].items():
                stories_table.add_row(story.title(), str(count))
            
            console.print(stories_table)
            console.print()

    def show_save_list(self, valid_saves):
        """Display list of available saves"""
        console.print("[bold cyan]Available Saves:[/bold cyan]")
        console.print()
        
        for i, filename, save_data in valid_saves:
            # Display save info
            save_time = datetime.fromisoformat(save_data.get("save_timestamp", save_data.get("start_time", datetime.now().isoformat())))
            console.print(f"[{i}] {filename[:-5]}")
            console.print(f"    Player: {save_data.get('player_name', 'Unknown')}")
            console.print(f"    Story: {save_data.get('story_type', 'Unknown').title()}")
            console.print(f"    Saved: {save_time.strftime('%Y-%m-%d %H:%M')}")
            console.print(f"    Progress: {len(save_data.get('visited_scenes', []))} scenes visited")
            console.print()