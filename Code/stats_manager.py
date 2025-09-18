"""
Stats Manager Module - Handles game statistics
"""

import json
import os
from rich.console import Console

console = Console()

class StatsManager:
    def __init__(self):
        self.stats_file = "stats/global_stats.json"

    def show_global_stats(self):
        """Display global statistics across all games"""
        if not os.path.exists(self.stats_file):
            console.print("[red]No global statistics found![/red]")
            console.print("Press Enter to continue...")
            input()
            return

        try:
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)
            
            from Code.ui_manager import UIManager
            ui_manager = UIManager()
            ui_manager.show_global_stats_display(stats)
            
        except Exception as e:
            console.print(f"[red]Error reading global statistics: {e}[/red]")
        
        console.print("Press Enter to continue...")
        input()

    def save_final_stats(self, game_state, play_time):
        """Save final game statistics to global stats"""
        if not os.path.exists("stats"):
            os.makedirs("stats")
        
        # Load existing stats or create new
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    stats = json.load(f)
            except:
                stats = {}
        else:
            stats = {}
        
        # Update stats
        stats["total_games"] = stats.get("total_games", 0) + 1
        stats["total_play_time_seconds"] = stats.get("total_play_time_seconds", 0) + play_time.total_seconds()
        stats["average_game_time_seconds"] = stats["total_play_time_seconds"] / stats["total_games"]
        stats["total_deaths"] = stats.get("total_deaths", 0) + game_state["deaths"]
        stats["total_items_collected"] = stats.get("total_items_collected", 0) + game_state["items_collected"]
        
        # Track stories completed
        if "stories_completed" not in stats:
            stats["stories_completed"] = {}
        
        story_type = game_state["story_type"]
        stats["stories_completed"][story_type] = stats["stories_completed"].get(story_type, 0) + 1
        
        # Save updated stats
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving statistics: {e}[/red]")

    def get_player_stats(self, player_name):
        """Get statistics for a specific player"""
        player_stats_file = f"stats/player_{player_name}.json"
        
        if not os.path.exists(player_stats_file):
            return None
        
        try:
            with open(player_stats_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def save_player_stats(self, game_state, play_time):
        """Save statistics for individual player"""
        if not os.path.exists("stats"):
            os.makedirs("stats")
        
        player_name = game_state["player_name"]
        player_stats_file = f"stats/player_{player_name}.json"
        
        # Load existing player stats or create new
        if os.path.exists(player_stats_file):
            try:
                with open(player_stats_file, 'r') as f:
                    player_stats = json.load(f)
            except:
                player_stats = {}
        else:
            player_stats = {}
        
        # Update player stats
        player_stats["player_name"] = player_name
        player_stats["games_played"] = player_stats.get("games_played", 0) + 1
        player_stats["total_play_time_seconds"] = player_stats.get("total_play_time_seconds", 0) + play_time.total_seconds()
        player_stats["total_deaths"] = player_stats.get("total_deaths", 0) + game_state["deaths"]
        player_stats["total_items_collected"] = player_stats.get("total_items_collected", 0) + game_state["items_collected"]
        
        # Track stories completed by player
        if "stories_completed" not in player_stats:
            player_stats["stories_completed"] = {}
        
        story_type = game_state["story_type"]
        player_stats["stories_completed"][story_type] = player_stats["stories_completed"].get(story_type, 0) + 1
        
        # Save player stats
        try:
            with open(player_stats_file, 'w') as f:
                json.dump(player_stats, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving player statistics: {e}[/red]")

    def reset_global_stats(self):
        """Reset global statistics (use with caution)"""
        try:
            if os.path.exists(self.stats_file):
                os.remove(self.stats_file)
            console.print("[green]Global statistics reset successfully![/green]")
        except Exception as e:
            console.print(f"[red]Error resetting statistics: {e}[/red]")

    def export_stats(self, filename):
        """Export statistics to a file"""
        try:
            if not os.path.exists(self.stats_file):
                console.print("[red]No statistics to export![/red]")
                return False
            
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)
            
            with open(filename, 'w') as f:
                json.dump(stats, f, indent=2)
            
            console.print(f"[green]Statistics exported to {filename}![/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error exporting statistics: {e}[/red]")
            return False