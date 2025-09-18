"""
Save Manager Module - Handles game saving and loading
"""

import json
import os
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt

console = Console()

class SaveManager:
    def save_game(self, game_state):
        """Save current game state"""
        if not os.path.exists("saves"):
            os.makedirs("saves")
        
        save_name = Prompt.ask("Enter save name", default=f"{game_state['player_name']}_save")
        
        # Add current timestamp to save data
        save_data = game_state.copy()
        save_data["save_timestamp"] = datetime.now().isoformat()
        
        filename = f"saves/{save_name}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            game_state["saves_used"] += 1
            console.print(f"[green]Game saved as '{save_name}'![/green]")
        except Exception as e:
            console.print(f"[red]Error saving game: {e}[/red]")
        
        console.print("Press Enter to continue...")
        input()

    def load_game(self):
        """Load a saved game"""
        if not os.path.exists("saves"):
            console.print("[red]No saves directory found![/red]")
            console.print("Press Enter to continue...")
            input()
            return None
        
        save_files = [f for f in os.listdir("saves") if f.endswith('.json')]
        
        if not save_files:
            console.print("[red]No save files found![/red]")
            console.print("Press Enter to continue...")
            input()
            return None
        
        # Show available saves
        from Code.ui_manager import UIManager
        ui_manager = UIManager()
        
        valid_saves = []
        for i, filename in enumerate(save_files, 1):
            try:
                with open(f"saves/{filename}", 'r') as f:
                    save_data = json.load(f)
                
                valid_saves.append((i, filename, save_data))
            except Exception as e:
                console.print(f"[red]Error reading {filename}: {e}[/red]")
        
        if not valid_saves:
            console.print("[red]No valid save files found![/red]")
            console.print("Press Enter to continue...")
            input()
            return None
        
        # Display saves using UI manager
        ui_manager.show_save_list(valid_saves)
        
        console.print(f"[{len(valid_saves) + 1}] Back to Main Menu")
        console.print()
        
        choice = Prompt.ask("Choose save to load", choices=[str(i) for i in range(1, len(valid_saves) + 2)])
        
        if choice == str(len(valid_saves) + 1):
            return None
        
        # Load the chosen save
        for save_id, filename, save_data in valid_saves:
            if save_id == int(choice):
                return save_data
        
        return None

    def get_save_files(self):
        """Get list of available save files"""
        if not os.path.exists("saves"):
            return []
        
        save_files = []
        for filename in os.listdir("saves"):
            if filename.endswith('.json'):
                try:
                    with open(f"saves/{filename}", 'r') as f:
                        save_data = json.load(f)
                    save_files.append((filename, save_data))
                except Exception:
                    continue
        
        return save_files

    def delete_save(self, filename):
        """Delete a save file"""
        try:
            os.remove(f"saves/{filename}")
            console.print(f"[green]Save '{filename[:-5]}' deleted successfully![/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error deleting save: {e}[/red]")
            return False