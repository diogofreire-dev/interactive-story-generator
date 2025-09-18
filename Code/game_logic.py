"""
Game Logic Module - Handles game flow and story progression
"""

import json
import os
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, Confirm

from Code.story_manager import StoryManager
from Code.ui_manager import UIManager
from Code.save_manager import SaveManager
from Code.stats_manager import StatsManager

console = Console()

class GameLogic:
    def __init__(self):
        self.story_manager = StoryManager()
        self.ui_manager = UIManager()
        self.save_manager = SaveManager()
        self.stats_manager = StatsManager()

    def play_game(self):
        """Start a new game"""
        console.clear()
        
        # Get player name
        player_name = Prompt.ask("Enter your name")
        
        # Choose story
        story_choice = self.choose_story()
        if not story_choice:
            return
        
        # Initialize game state
        game_state = {
            "player_name": player_name,
            "story_type": story_choice,
            "current_scene": f"{story_choice}_start",
            "inventory": [],
            "visited_scenes": [],
            "choices_made": [],
            "deaths": 0,
            "saves_used": 0,
            "start_time": datetime.now().isoformat(),
            "items_collected": 0
        }
        
        # Start the story
        self.play_story(game_state)

    def choose_story(self):
        """Let player choose which story to play"""
        stories = self.story_manager.get_available_stories()
        
        console.print("[bold cyan]Choose Your Adventure:[/bold cyan]")
        console.print()
        
        for i, (story_id, story_info) in enumerate(stories.items(), 1):
            console.print(f"[{i}] {story_info['title']}")
            console.print(f"    {story_info['description']}")
            console.print(f"    Difficulty: {story_info['difficulty']}")
            console.print()
        
        console.print(f"[{len(stories) + 1}] Back to Main Menu")
        console.print()
        
        choice = Prompt.ask("Choose a story", choices=[str(i) for i in range(1, len(stories) + 2)])
        
        if choice == str(len(stories) + 1):
            return None
        
        story_keys = list(stories.keys())
        return story_keys[int(choice) - 1]

    def play_story(self, game_state):
        """Main story playing loop"""
        scenes = self.story_manager.get_story_scenes(game_state["story_type"])
        
        while True:
            current_scene = game_state["current_scene"]
            
            # Check if scene exists
            if current_scene not in scenes:
                console.print(f"Error: Scene '{current_scene}' not found!", style="red")
                break
            
            scene = scenes[current_scene]
            
            # Track visited scenes
            if current_scene not in game_state["visited_scenes"]:
                game_state["visited_scenes"].append(current_scene)
            
            # Display scene
            console.clear()
            self.ui_manager.show_scene(scene, game_state)
            
            # Check if this is an ending
            if scene.get("ending"):
                self.ui_manager.show_ending(scene, game_state)
                
                # Calculate final stats
                end_time = datetime.now()
                start_time = datetime.fromisoformat(game_state["start_time"])
                play_time = end_time - start_time
                
                # Save final statistics
                self.stats_manager.save_final_stats(game_state, play_time)
                
                console.print("Press Enter to return to main menu...")
                input()
                break
            
            # Get player choice
            choice = self.get_player_choice(scene, game_state)
            
            if choice is None:  # Player quit
                break
            
            # Process choice
            if choice.isdigit():
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(scene["choices"]):
                    choice_data = scene["choices"][choice_index]
                    
                    # Record choice
                    game_state["choices_made"].append({
                        "scene": current_scene,
                        "choice": choice_data["text"],
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Handle item collection
                    if "item" in choice_data:
                        if choice_data["item"] not in game_state["inventory"]:
                            game_state["inventory"].append(choice_data["item"])
                            game_state["items_collected"] += 1
                            console.print(f"[green]You found: {choice_data['item']}[/green]")
                            console.print("Press Enter to continue...")
                            input()
                    
                    # Check if choice leads to death
                    if choice_data.get("death"):
                        game_state["deaths"] += 1
                        console.print(f"[red]{choice_data.get('death_message', 'You died!')}[/red]")
                        console.print("Press Enter to continue...")
                        input()
                    
                    # Move to next scene
                    game_state["current_scene"] = choice_data["next_scene"]

    def get_player_choice(self, scene, game_state):
        """Get and validate player choice"""
        while True:
            choice = Prompt.ask("Your choice").strip().upper()
            
            if choice == "I":
                self.ui_manager.show_inventory(game_state)
                continue
            elif choice == "S":
                self.save_manager.save_game(game_state)
                continue
            elif choice == "T":
                self.ui_manager.show_current_stats(game_state)
                continue
            elif choice == "Q":
                if Confirm.ask("Are you sure you want to quit?"):
                    return None
                continue
            
            # Validate numeric choice
            if choice.isdigit():
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(scene["choices"]):
                    choice_data = scene["choices"][choice_index]
                    
                    # Check if choice requires an item
                    if "requires_item" in choice_data:
                        if choice_data["requires_item"] not in game_state["inventory"]:
                            console.print(f"[red]You need {choice_data['requires_item']} to do that![/red]")
                            continue
                    
                    return choice
                else:
                    console.print("[red]Invalid choice number![/red]")
            else:
                console.print("[red]Please enter a number or command![/red]")

    def load_game(self):
        """Load a saved game"""
        save_data = self.save_manager.load_game()
        if save_data:
            console.print(f"Loading story for {save_data['player_name']}...", style="green")
            console.clear()
            self.play_story(save_data)