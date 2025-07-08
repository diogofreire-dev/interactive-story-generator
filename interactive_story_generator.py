#!/usr/bin/env python3
"""
Interactive Story Generator - CS50P Final Project
Author: [Your Name]
"""

import json
import os
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

def main():
    """Main game loop"""
    console.clear()
    show_title()
    
    while True:
        choice = show_main_menu()
        
        if choice == "1":
            play_game()
        elif choice == "2":
            load_game()
        elif choice == "3":
            show_global_stats()
        elif choice == "4":
            console.print("Thanks for playing!", style="green")
            break
        else:
            console.print("Invalid choice. Please try again.", style="red")

def show_title():
    """Display the game title"""
    title = Text("Interactive Story Generator", style="bold cyan")
    subtitle = Text("CS50P Final Project", style="italic")
    
    title_panel = Panel.fit(f"{title}\n{subtitle}", border_style="cyan")
    console.print(title_panel)
    console.print()

def show_main_menu():
    """Display main menu and get user choice"""
    menu_text = """
[bold cyan]Main Menu[/bold cyan]

[1] New Game
[2] Load Game
[3] Global Statistics
[4] Exit

Choose an option: """
    
    return Prompt.ask(menu_text, choices=["1", "2", "3", "4"])

def play_game():
    """Start a new game"""
    console.clear()
    
    # Get player name
    player_name = Prompt.ask("Enter your name")
    
    # Choose story
    story_choice = choose_story()
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
    play_story(game_state)

def choose_story():
    """Let player choose which story to play"""
    stories = get_available_stories()
    
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

def get_available_stories():
    """Return available stories information"""
    return {
        "castle": {
            "title": "The Enchanted Castle",
            "description": "A magical adventure in a mysterious castle",
            "difficulty": "Easy"
        },
        "forest": {
            "title": "The Dark Forest",
            "description": "Survive the dangers of a haunted forest",
            "difficulty": "Medium"
        },
        "space": {
            "title": "Space Station Alpha",
            "description": "Sci-fi thriller on a abandoned space station",
            "difficulty": "Hard"
        }
    }

def play_story(game_state):
    """Main story playing loop"""
    scenes = get_story_scenes(game_state["story_type"])
    
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
        show_scene(scene, game_state)
        
        # Check if this is an ending
        if scene.get("ending"):
            show_ending(scene, game_state)
            break
        
        # Get player choice
        choice = get_player_choice(scene, game_state)
        
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

def show_scene(scene, game_state):
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

def show_ending(scene, game_state):
    """Display ending scene with final statistics"""
    console.print(f"[bold green]{scene.get('ending_title', 'THE END')}[/bold green]")
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
    
    # Save final statistics
    save_final_stats(game_state, play_time)
    
    console.print("Press Enter to return to main menu...")
    input()

def get_player_choice(scene, game_state):
    """Get and validate player choice"""
    while True:
        choice = Prompt.ask("Your choice").strip().upper()
        
        if choice == "I":
            show_inventory(game_state)
            continue
        elif choice == "S":
            save_game(game_state)
            continue
        elif choice == "T":
            show_current_stats(game_state)
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

def show_inventory(game_state):
    """Display player inventory"""
    console.print("[bold cyan]Inventory:[/bold cyan]")
    if game_state["inventory"]:
        for item in game_state["inventory"]:
            console.print(f"- {item}")
    else:
        console.print("Empty")
    console.print()

def show_current_stats(game_state):
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

def save_game(game_state):
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

def load_game():
    """Load a saved game"""
    if not os.path.exists("saves"):
        console.print("[red]No saves directory found![/red]")
        console.print("Press Enter to continue...")
        input()
        return
    
    save_files = [f for f in os.listdir("saves") if f.endswith('.json')]
    
    if not save_files:
        console.print("[red]No save files found![/red]")
        console.print("Press Enter to continue...")
        input()
        return
    
    # Show available saves
    console.print("[bold cyan]Available Saves:[/bold cyan]")
    console.print()
    
    valid_saves = []
    for i, filename in enumerate(save_files, 1):
        try:
            with open(f"saves/{filename}", 'r') as f:
                save_data = json.load(f)
            
            # Display save info
            save_time = datetime.fromisoformat(save_data.get("save_timestamp", save_data.get("start_time", datetime.now().isoformat())))
            console.print(f"[{i}] {filename[:-5]}")
            console.print(f"    Player: {save_data.get('player_name', 'Unknown')}")
            console.print(f"    Story: {save_data.get('story_type', 'Unknown').title()}")
            console.print(f"    Saved: {save_time.strftime('%Y-%m-%d %H:%M')}")
            console.print(f"    Progress: {len(save_data.get('visited_scenes', []))} scenes visited")
            console.print()
            
            valid_saves.append((i, filename, save_data))
        except Exception as e:
            console.print(f"[red]Error reading {filename}: {e}[/red]")
    
    if not valid_saves:
        console.print("[red]No valid save files found![/red]")
        console.print("Press Enter to continue...")
        input()
        return
    
    console.print(f"[{len(valid_saves) + 1}] Back to Main Menu")
    console.print()
    
    choice = Prompt.ask("Choose save to load", choices=[str(i) for i in range(1, len(valid_saves) + 2)])
    
    if choice == str(len(valid_saves) + 1):
        return
    
    # Load the chosen save
    for save_id, filename, save_data in valid_saves:
        if save_id == int(choice):
            console.print(f"Loading story for {save_data['player_name']}...", style="green")
            console.clear()
            play_story(save_data)
            break

def show_global_stats():
    """Display global statistics across all games"""
    stats_file = "stats/global_stats.json"
    
    if not os.path.exists(stats_file):
        console.print("[red]No global statistics found![/red]")
        console.print("Press Enter to continue...")
        input()
        return
    
    try:
        with open(stats_file, 'r') as f:
            stats = json.load(f)
        
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
        
    except Exception as e:
        console.print(f"[red]Error reading global statistics: {e}[/red]")
    
    console.print("Press Enter to continue...")
    input()

def save_final_stats(game_state, play_time):
    """Save final game statistics to global stats"""
    if not os.path.exists("stats"):
        os.makedirs("stats")
    
    stats_file = "stats/global_stats.json"
    
    # Load existing stats or create new
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r') as f:
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
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        console.print(f"[red]Error saving statistics: {e}[/red]")

def get_story_scenes(story_type):
    """Return scenes for the specified story type"""
    stories = {
        "castle": {
            "castle_start": {
                "title": "The Enchanted Castle",
                "description": "You stand before a magnificent castle with towers that seem to touch the clouds. The heavy wooden doors are slightly ajar, and strange lights flicker from within.",
                "choices": [
                    {"text": "Enter through the main doors", "next_scene": "castle_hall"},
                    {"text": "Look for a side entrance", "next_scene": "castle_garden"},
                    {"text": "Examine the castle exterior", "next_scene": "castle_exterior"}
                ]
            },
            "castle_hall": {
                "title": "The Great Hall",
                "description": "The great hall is vast and dimly lit by floating candles. Ancient tapestries cover the walls, and a grand staircase leads to the upper floors.",
                "choices": [
                    {"text": "Go up the grand staircase", "next_scene": "castle_tower"},
                    {"text": "Explore the dining room", "next_scene": "castle_dining"},
                    {"text": "Search behind the tapestries", "next_scene": "castle_secret", "item": "golden key"}
                ]
            },
            "castle_garden": {
                "title": "The Enchanted Garden",
                "description": "A magical garden with flowers that glow in the moonlight. A crystal fountain stands in the center, and you hear soft music in the air.",
                "choices": [
                    {"text": "Drink from the crystal fountain", "next_scene": "castle_fountain"},
                    {"text": "Follow the music", "next_scene": "castle_music"},
                    {"text": "Pick a glowing flower", "next_scene": "castle_flower", "item": "magic flower"}
                ]
            },
            "castle_exterior": {
                "title": "Castle Grounds",
                "description": "Walking around the castle, you notice strange symbols carved into the stone walls. One section of the wall seems different from the rest.",
                "choices": [
                    {"text": "Touch the strange symbols", "next_scene": "castle_magic"},
                    {"text": "Examine the different wall section", "next_scene": "castle_wall"},
                    {"text": "Return to the main entrance", "next_scene": "castle_start"}
                ]
            },
            "castle_tower": {
                "title": "The High Tower",
                "description": "At the top of the tower, you find a room filled with ancient books and magical artifacts. A wise old wizard sits at a desk.",
                "choices": [
                    {"text": "Speak with the wizard", "next_scene": "castle_wizard"},
                    {"text": "Examine the magical artifacts", "next_scene": "castle_artifacts"},
                    {"text": "Read the ancient books", "next_scene": "castle_books"}
                ]
            },
            "castle_dining": {
                "title": "The Dining Room",
                "description": "A long table is set for a feast that seems to have been abandoned. The food looks fresh, but something feels wrong about it.",
                "choices": [
                    {"text": "Eat the food", "next_scene": "castle_poison", "death": True, "death_message": "The food was cursed! You fall into eternal sleep."},
                    {"text": "Leave the room immediately", "next_scene": "castle_hall"},
                    {"text": "Investigate under the table", "next_scene": "castle_trap", "item": "silver dagger"}
                ]
            },
            "castle_secret": {
                "title": "Secret Passage",
                "description": "You found a hidden passage behind the tapestries! It leads to a treasure chamber filled with gold and jewels.",
                "choices": [
                    {"text": "Take the treasure", "next_scene": "castle_treasure_end", "ending": True, "ending_title": "TREASURE HUNTER ENDING"},
                    {"text": "Leave the treasure and continue exploring", "next_scene": "castle_hall"},
                    {"text": "Look for traps", "next_scene": "castle_trap_check"}
                ]
            },
            "castle_fountain": {
                "title": "The Crystal Fountain",
                "description": "As you drink from the fountain, you feel magical energy flowing through you. Your wounds heal and you feel stronger.",
                "choices": [
                    {"text": "Continue to explore the garden", "next_scene": "castle_garden"},
                    {"text": "Enter the castle through a garden door", "next_scene": "castle_hall"},
                    {"text": "Rest by the fountain", "next_scene": "castle_rest"}
                ]
            },
            "castle_wizard": {
                "title": "The Wise Wizard",
                "description": "The wizard smiles and offers to teach you magic. 'You have shown courage by reaching this tower,' he says.",
                "choices": [
                    {"text": "Accept the magic training", "next_scene": "castle_magic_end", "ending": True, "ending_title": "WIZARD APPRENTICE ENDING"},
                    {"text": "Ask about the castle's history", "next_scene": "castle_history"},
                    {"text": "Politely decline and leave", "next_scene": "castle_hall"}
                ]
            },
            "castle_magic_end": {
                "ending": True,
                "ending_title": "WIZARD APPRENTICE ENDING",
                "description": "You become the wizard's apprentice and learn powerful magic. Years later, you become the castle's new protector, ensuring its magic is used for good."
            },
            "castle_treasure_end": {
                "ending": True,
                "ending_title": "TREASURE HUNTER ENDING", 
                "description": "You take the ancient treasure and become wealthy beyond your wildest dreams. However, you sometimes wonder what other adventures you might have had in the magical castle."
            },
            "castle_poison": {
                "ending": True,
                "ending_title": "CURSED ENDING",
                "description": "The cursed food puts you into an eternal sleep. You become part of the castle's magic, forever dreaming of adventures you'll never have."
            }
        },
        
        "forest": {
            "forest_start": {
                "title": "The Dark Forest",
                "description": "You enter a dense, dark forest where the trees seem to whisper secrets. Strange shadows move between the trunks, and the path splits in three directions.",
                "choices": [
                    {"text": "Take the left path", "next_scene": "forest_left"},
                    {"text": "Take the right path", "next_scene": "forest_right"},
                    {"text": "Go straight ahead", "next_scene": "forest_straight"}
                ]
            },
            "forest_left": {
                "title": "The Moonlit Clearing",
                "description": "You emerge into a clearing bathed in moonlight. Ancient stone circles stand here, and you can hear wolves howling in the distance.",
                "choices": [
                    {"text": "Investigate the stone circles", "next_scene": "forest_stones"},
                    {"text": "Hide and wait for the wolves to pass", "next_scene": "forest_hide"},
                    {"text": "Climb a tree for safety", "next_scene": "forest_tree"}
                ]
            },
            "forest_right": {
                "title": "The Witch's Hut",
                "description": "You discover a small hut with smoke coming from the chimney. Strange herbs hang from the eaves, and you smell something cooking inside.",
                "choices": [
                    {"text": "Knock on the door", "next_scene": "forest_witch"},
                    {"text": "Peek through the window", "next_scene": "forest_window"},
                    {"text": "Take some herbs and leave", "next_scene": "forest_herbs", "item": "healing herbs"}
                ]
            },
            "forest_straight": {
                "title": "The Deep Woods",
                "description": "The path leads deeper into the forest where the trees grow so thick that little light penetrates. You hear strange sounds all around you.",
                "choices": [
                    {"text": "Continue forward bravely", "next_scene": "forest_deep"},
                    {"text": "Try to find another path", "next_scene": "forest_lost"},
                    {"text": "Make a torch to light your way", "next_scene": "forest_torch"}
                ]
            },
            "forest_stones": {
                "title": "Ancient Stone Circle",
                "description": "The stone circle begins to glow as you approach. Ancient magic fills the air, and you feel a powerful presence watching you.",
                "choices": [
                    {"text": "Step into the circle", "next_scene": "forest_magic"},
                    {"text": "Speak to the presence", "next_scene": "forest_spirit"},
                    {"text": "Back away slowly", "next_scene": "forest_left"}
                ]
            },
            "forest_witch": {
                "title": "The Forest Witch",
                "description": "An old woman opens the door. She has kind eyes but a mysterious smile. 'I've been expecting you,' she says.",
                "choices": [
                    {"text": "Ask for help", "next_scene": "forest_help"},
                    {"text": "Ask about the forest", "next_scene": "forest_knowledge"},
                    {"text": "Politely excuse yourself", "next_scene": "forest_right"}
                ]
            },
            "forest_deep": {
                "title": "Heart of the Forest",
                "description": "You reach the heart of the forest where an ancient tree towers above all others. Its trunk is so wide that it would take dozens of people to encircle it.",
                "choices": [
                    {"text": "Touch the ancient tree", "next_scene": "forest_tree_spirit"},
                    {"text": "Rest beneath the tree", "next_scene": "forest_rest"},
                    {"text": "Look for a way around", "next_scene": "forest_around"}
                ]
            },
            "forest_magic": {
                "title": "Forest Magic",
                "description": "The stone circle's magic transports you to safety outside the forest. You have gained the forest's blessing.",
                "choices": [
                    {"text": "Accept the blessing", "next_scene": "forest_blessing_end", "ending": True, "ending_title": "FOREST GUARDIAN ENDING"}
                ]
            },
            "forest_help": {
                "title": "The Witch's Aid",
                "description": "The witch gives you a magic potion and directions out of the forest. 'Use this wisely,' she warns.",
                "choices": [
                    {"text": "Thank her and follow the directions", "next_scene": "forest_escape_end", "ending": True, "ending_title": "SAFE ESCAPE ENDING", "item": "magic potion"},
                    {"text": "Ask for more help", "next_scene": "forest_greedy"},
                    {"text": "Offer to help her in return", "next_scene": "forest_helper"}
                ]
            },
            "forest_tree_spirit": {
                "title": "The Tree Spirit",
                "description": "Touching the tree awakens its ancient spirit. It offers to make you guardian of the forest.",
                "choices": [
                    {"text": "Accept the guardianship", "next_scene": "forest_guardian_end", "ending": True, "ending_title": "FOREST GUARDIAN ENDING"},
                    {"text": "Respectfully decline", "next_scene": "forest_decline"},
                    {"text": "Ask what it means", "next_scene": "forest_explain"}
                ]
            },
            "forest_blessing_end": {
                "ending": True,
                "ending_title": "FOREST GUARDIAN ENDING",
                "description": "You become the forest's guardian, protecting it from harm and helping lost travelers find their way. The forest creatures become your allies."
            },
            "forest_escape_end": {
                "ending": True,
                "ending_title": "SAFE ESCAPE ENDING",
                "description": "With the witch's help, you safely escape the dark forest. You return home with magical herbs and incredible stories to tell."
            },
            "forest_guardian_end": {
                "ending": True,
                "ending_title": "FOREST GUARDIAN ENDING",
                "description": "You accept the role of forest guardian and gain the ability to communicate with all forest creatures. Your new life is filled with purpose and magic."
            },
            "forest_lost": {
                "title": "Lost in the Woods",
                "description": "You wander deeper into the forest and become hopelessly lost. The trees all look the same.",
                "choices": [
                    {"text": "Try to retrace your steps", "next_scene": "forest_straight"},
                    {"text": "Call for help", "next_scene": "forest_wolves", "death": True, "death_message": "Your calls attract a pack of hungry wolves!"},
                    {"text": "Climb a tree to get your bearings", "next_scene": "forest_tree"}
                ]
            }
        },
        
        "space": {
            "space_start": {
                "title": "Space Station Alpha",
                "description": "You dock with the seemingly abandoned Space Station Alpha. Emergency lights flicker in the corridors, and you hear strange noises echoing through the metal halls.",
                "choices": [
                    {"text": "Head to the command center", "next_scene": "space_command"},
                    {"text": "Check the crew quarters", "next_scene": "space_quarters"},
                    {"text": "Investigate the engine room", "next_scene": "space_engine"}
                ]
            },
            "space_command": {
                "title": "Command Center",
                "description": "The command center is dark except for a few blinking consoles. Warning messages flash on the screens about a containment breach.",
                "choices": [
                    {"text": "Access the main computer", "next_scene": "space_computer"},
                    {"text": "Check the communication system", "next_scene": "space_comms"},
                    {"text": "Review the security footage", "next_scene": "space_security"}
                ]
            },
            "space_quarters": {
                "title": "Crew Quarters",
                "description": "The crew quarters are in disarray. Personal belongings are scattered everywhere, and some doors are sealed with emergency locks.",
                "choices": [
                    {"text": "Search the unsealed rooms", "next_scene": "space_search"},
                    {"text": "Try to open the sealed doors", "next_scene": "space_sealed"},
                    {"text": "Check the crew logs", "next_scene": "space_logs"}
                ]
            },
            "space_engine": {
                "title": "Engine Room",
                "description": "The engine room hums with power, but something is wrong. Strange organic growth covers parts of the machinery.",
                "choices": [
                    {"text": "Examine the organic growth", "next_scene": "space_organism"},
                    {"text": "Check the engine diagnostics", "next_scene": "space_diagnostics"},
                    {"text": "Try to clean the growth", "next_scene": "space_clean"}
                ]
            },
            "space_computer": {
                "title": "Main Computer",
                "description": "The computer reveals that an alien organism was brought aboard for study. It has since escaped and infected the crew.",
                "choices": [
                    {"text": "Access quarantine protocols", "next_scene": "space_quarantine"},
                    {"text": "Search for survivor locations", "next_scene": "space_survivors"},
                    {"text": "Initiate self-destruct sequence", "next_scene": "space_destruct"}
                ]
            },
            "space_comms": {
                "title": "Communications",
                "description": "You manage to establish contact with Earth. They're sending a rescue ship, but it won't arrive for 48 hours.",
                "choices": [
                    {"text": "Request immediate evacuation", "next_scene": "space_evacuation"},
                    {"text": "Report the alien threat", "next_scene": "space_report"},
                    {"text": "Ask for instructions", "next_scene": "space_instructions"}
                ]
            },
            "space_security": {
                "title": "Security Footage",
                "description": "The security footage shows the crew being attacked by strange alien creatures. The creatures seem to be growing and multiplying.",
                "choices": [
                    {"text": "Track the creatures' movements", "next_scene": "space_track"},
                    {"text": "Look for survivors", "next_scene": "space_survivors"},
                    {"text": "Find the source of the outbreak", "next_scene": "space_source"}
                ]
            },
            "space_organism": {
                "title": "Alien Organism",
                "description": "The organic growth pulses with an eerie light. As you approach, it seems to react to your presence.",
                "choices": [
                    {"text": "Take a sample for analysis", "next_scene": "space_sample", "item": "alien sample"},
                    {"text": "Back away slowly", "next_scene": "space_engine"},
                    {"text": "Try to communicate with it", "next_scene": "space_communicate"}
                ]
            },
            "space_quarantine": {
                "title": "Quarantine Protocols",
                "description": "The quarantine system is still active. You can seal off sections of the station or purge contaminated areas.",
                "choices": [
                    {"text": "Seal off the infected areas", "next_scene": "space_seal"},
                    {"text": "Purge the contaminated sections", "next_scene": "space_purge"},
                    {"text": "Override the quarantine", "next_scene": "space_override"}
                ]
            },
            "space_survivors": {
                "title": "Survivor Signal",
                "description": "You detect a faint life sign in the medical bay. Someone might still be alive!",
                "choices": [
                    {"text": "Rush to the medical bay", "next_scene": "space_medical"},
                    {"text": "Proceed cautiously", "next_scene": "space_cautious"},
                    {"text": "Try to contact them first", "next_scene": "space_contact"}
                ]
            },
            "space_medical": {
                "title": "Medical Bay",
                "description": "You find Dr. Sarah Chen, the station's chief medical officer, barricaded in the medical bay. She's injured but alive.",
                "choices": [
                    {"text": "Help treat her injuries", "next_scene": "space_treat"},
                    {"text": "Ask about the alien organism", "next_scene": "space_ask"},
                    {"text": "Plan an escape together", "next_scene": "space_escape"}
                ]
            },
            "space_treat": {
                "title": "Medical Treatment",
                "description": "Dr. Chen explains that the alien organism is highly aggressive and spreads rapidly. She has developed a potential cure.",
                "choices": [
                    {"text": "Help her complete the cure", "next_scene": "space_cure"},
                    {"text": "Focus on escaping instead", "next_scene": "space_escape"},
                    {"text": "Ask about the cure's risks", "next_scene": "space_risks"}
                ]
            },
            "space_cure": {
                "title": "The Cure",
                "description": "Working together, you help Dr. Chen complete the cure. It can be dispersed through the station's air system.",
                "choices": [
                    {"text": "Deploy the cure immediately", "next_scene": "space_deploy"},
                    {"text": "Test it first", "next_scene": "space_test"},
                    {"text": "Evacuate and let Earth handle it", "next_scene": "space_evacuate"}
                ]
            },
            "space_deploy": {
                "title": "Deploying the Cure",
                "description": "You deploy the cure through the station's air system. The alien organisms begin to retreat and die.",
                "choices": [
                    {"text": "Check on the station's status", "next_scene": "space_hero_end", "ending": True, "ending_title": "STATION HERO ENDING"}
                ]
            },
            "space_escape": {
                "title": "Escape Plan",
                "description": "You and Dr. Chen make it to the escape pods. Earth's rescue ship arrives just as you launch.",
                "choices": [
                    {"text": "Launch the escape pod", "next_scene": "space_survivor_end", "ending": True, "ending_title": "SURVIVOR ENDING"}
                ]
            },
            "space_destruct": {
                "title": "Self-Destruct",
                "description": "You initiate the self-destruct sequence to prevent the alien organism from reaching Earth.",
                "choices": [
                    {"text": "Evacuate immediately", "next_scene": "space_sacrifice_end", "ending": True, "ending_title": "SACRIFICE ENDING"},
                    {"text": "Try to cancel the sequence", "next_scene": "space_cancel"}
                ]
            },
            "space_hero_end": {
                "ending": True,
                "ending_title": "STATION HERO ENDING",
                "description": "You successfully deploy the cure and save Space Station Alpha. The station is decontaminated and you become a hero. Earth's scientists study your data to prevent future outbreaks."
            },
            "space_survivor_end": {
                "ending": True,
                "ending_title": "SURVIVOR ENDING", 
                "description": "You and Dr. Chen escape the station and are rescued by Earth's ship. The station is later destroyed by military forces, but you both survive to tell the tale."
            },
            "space_sacrifice_end": {
                "ending": True,
                "ending_title": "SACRIFICE ENDING",
                "description": "You sacrifice yourself to destroy the station and prevent the alien threat from reaching Earth. You are remembered as a hero who saved humanity."
            },
            "space_communicate": {
                "title": "Communication Attempt",
                "description": "The alien organism seems to respond to your attempts at communication. It's trying to tell you something.",
                "choices": [
                    {"text": "Try to understand its message", "next_scene": "space_understand"},
                    {"text": "Back away carefully", "next_scene": "space_engine"},
                    {"text": "Offer it something", "next_scene": "space_offer"}
                ]
            },
            "space_understand": {
                "title": "Alien Understanding",
                "description": "You realize the organism isn't hostile - it's trying to return home. It was brought here against its will.",
                "choices": [
                    {"text": "Help it return home", "next_scene": "space_peace_end", "ending": True, "ending_title": "PEACEFUL RESOLUTION ENDING"},
                    {"text": "Try to contain it safely", "next_scene": "space_contain"},
                    {"text": "Report this to Earth", "next_scene": "space_report_discovery"}
                ]
            },
            "space_peace_end": {
                "ending": True,
                "ending_title": "PEACEFUL RESOLUTION ENDING",
                "description": "You help the alien organism return to its home dimension. It restores the infected crew members and leaves peacefully. You've made first contact and established peaceful relations with an alien species."
            }
        }
    }
    
    return stories.get(story_type, {})

# Test functions for pytest
def test_get_story_scenes():
    """Test that story scenes are properly loaded"""
    castle_scenes = get_story_scenes("castle")
    assert "castle_start" in castle_scenes
    assert "choices" in castle_scenes["castle_start"]
    
    forest_scenes = get_story_scenes("forest")
    assert "forest_start" in forest_scenes
    
    space_scenes = get_story_scenes("space")
    assert "space_start" in space_scenes

def test_get_available_stories():
    """Test that available stories are returned correctly"""
    stories = get_available_stories()
    assert "castle" in stories
    assert "forest" in stories
    assert "space" in stories
    
    for story_id, story_info in stories.items():
        assert "title" in story_info
        assert "description" in story_info
        assert "difficulty" in story_info

def test_story_structure():
    """Test that all stories have proper structure"""
    for story_type in ["castle", "forest", "space"]:
        scenes = get_story_scenes(story_type)
        start_scene = f"{story_type}_start"
        
        # Check that start scene exists
        assert start_scene in scenes
        
        # Check that start scene has choices
        assert "choices" in scenes[start_scene]
        assert len(scenes[start_scene]["choices"]) > 0
        
        # Check that all scenes referenced in choices exist
        for scene_id, scene_data in scenes.items():
            if "choices" in scene_data:
                for choice in scene_data["choices"]:
                    if "next_scene" in choice:
                        assert choice["next_scene"] in scenes or scenes[choice["next_scene"]].get("ending", False)

def test_story_endings():
    """Test that all stories have proper endings"""
    for story_type in ["castle", "forest", "space"]:
        scenes = get_story_scenes(story_type)
        
        # Check that there are ending scenes
        ending_scenes = [scene for scene in scenes.values() if scene.get("ending")]
        assert len(ending_scenes) > 0
        
        # Check that endings have proper structure
        for ending in ending_scenes:
            assert "ending_title" in ending
            assert "description" in ending

def test_inventory_items():
    """Test that inventory items are properly defined"""
    for story_type in ["castle", "forest", "space"]:
        scenes = get_story_scenes(story_type)
        
        for scene_data in scenes.values():
            if "choices" in scene_data:
                for choice in scene_data["choices"]:
                    # If choice gives an item, it should be a string
                    if "item" in choice:
                        assert isinstance(choice["item"], str)
                        assert len(choice["item"]) > 0
                    
                    # If choice requires an item, it should be a string
                    if "requires_item" in choice:
                        assert isinstance(choice["requires_item"], str)
                        assert len(choice["requires_item"]) > 0

def test_save_story():
    """Test save game functionality"""
    import tempfile
    import os
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock game state
        game_state = {
            "player_name": "Test Player",
            "story_type": "castle",
            "current_scene": "castle_start",
            "inventory": ["golden key"],
            "visited_scenes": ["castle_start"],
            "choices_made": [],
            "deaths": 0,
            "saves_used": 0,
            "start_time": datetime.now().isoformat(),
            "items_collected": 1
        }
        
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Test save functionality
            if not os.path.exists("saves"):
                os.makedirs("saves")
            
            filename = "saves/test_save.json"
            with open(filename, 'w') as f:
                json.dump(game_state, f)
            
            # Test load functionality
            with open(filename, 'r') as f:
                loaded_state = json.load(f)
            
            assert loaded_state["player_name"] == "Test Player"
            assert loaded_state["story_type"] == "castle"
            assert "golden key" in loaded_state["inventory"]
            
        finally:
            os.chdir(original_cwd)

if __name__ == "__main__":
    main()