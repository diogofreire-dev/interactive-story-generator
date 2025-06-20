#!/usr/bin/env python3
"""
Interactive Story Generator - CS50P Final Project
Authors: Diogo Freire(Me), Ricardo Dias, Pedro Dias, Ricardo Santos
"""

import json
import os
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn


def main():
    """Main program function"""
    console = Console()
    
    welcome_text = Text("INTERACTIVE STORY GENERATOR", style="bold magenta")
    console.print(Panel(welcome_text, border_style="bright_blue"))
    
    while True:
        menu_table = Table(show_header=False, box=None)
        menu_table.add_column("Option", style="cyan", width=3)
        menu_table.add_column("Description", style="white")
        
        menu_table.add_row("1.", "New Story")
        menu_table.add_row("2.", "Load Saved Story") 
        menu_table.add_row("3.", "Player Statistics")
        menu_table.add_row("4.", "Exit")
        
        console.print("\nMain Menu:", style="bold yellow")
        console.print(menu_table)
        
        choice = Prompt.ask("\nChoose an option", choices=["1", "2", "3", "4"], default="1")
        
        if choice == "1":
            choose_story(console)
        elif choice == "2":
            load_saved_story(console)
        elif choice == "3":
            show_player_statistics(console)
        elif choice == "4":
            console.print("Thanks for playing! See you next time!", style="bold green")
            break


def choose_story(console):
    """Let player choose which story to play"""
    console.print("\nAvailable Stories:", style="bold blue")
    
    stories = get_available_stories()
    
    story_table = Table()
    story_table.add_column("ID", style="cyan", width=3)
    story_table.add_column("Title", style="magenta")
    story_table.add_column("Description", style="white")
    story_table.add_column("Difficulty", style="yellow")
    
    for i, (story_id, story_info) in enumerate(stories.items(), 1):
        story_table.add_row(
            str(i),
            story_info["title"],
            story_info["description"],
            story_info["difficulty"]
        )
    
    console.print(story_table)
    
    story_choices = [str(i) for i in range(1, len(stories) + 1)]
    choice = Prompt.ask("\nChoose a story", choices=story_choices, default="1")
    
    story_id = list(stories.keys())[int(choice) - 1]
    start_new_story(console, story_id)


def get_available_stories():
    """Return dictionary of available stories"""
    return {
        "enchanted_castle": {
            "title": "The Enchanted Castle",
            "description": "Explore a magical castle filled with mysteries and treasures",
            "difficulty": "Easy"
        },
        "dark_forest": {
            "title": "The Dark Forest",
            "description": "Navigate through a dangerous forest full of creatures and traps",
            "difficulty": "Medium"
        },
        "space_station": {
            "title": "Abandoned Space Station",
            "description": "Investigate a mysterious space station that has gone silent",
            "difficulty": "Hard"
        }
    }


def start_new_story(console, story_id="enchanted_castle"):
    """Start a new interactive story"""
    stories = get_available_stories()
    story_info = stories[story_id]
    
    console.print(f"\nStarting: {story_info['title']}", style="bold blue")
    
    # Initialize story data with statistics
    story_data = {
        "story_id": story_id,
        "title": story_info["title"],
        "current_scene": "start",
        "player_name": "",
        "choices_made": [],
        "inventory": [],
        "start_time": datetime.now().isoformat(),
        "statistics": {
            "scenes_visited": 0,
            "items_collected": 0,
            "choices_count": 0,
            "deaths": 0,
            "saves_used": 0
        }
    }
    
    # Get player name
    player_name = Prompt.ask("\nWhat is your name, adventurer?")
    if not player_name.strip():
        player_name = "Adventurer"
    
    story_data["player_name"] = player_name
    
    console.print(f"\nWelcome, [bold cyan]{player_name}[/]! Your adventure is about to begin...")
    
    # Begin the adventure
    play_scene(story_data, "start", console)


def play_scene(story_data, scene_id, console):
    """Execute a specific scene of the story"""
    scenes = get_story_scenes(story_data["story_id"])
    
    if scene_id not in scenes:
        console.print("Error: Scene not found!", style="bold red")
        return
    
    # Update statistics
    story_data["statistics"]["scenes_visited"] += 1
    
    scene = scenes[scene_id]
    player_name = story_data["player_name"]
    
    # Show scene description
    description = scene["description"].replace("{player_name}", player_name)
    console.print(Panel(description, title="Story", border_style="green"))
    
    # Check if it's an ending scene
    if scene.get("is_ending", False):
        # Calculate play time
        start_time = datetime.fromisoformat(story_data["start_time"])
        end_time = datetime.now()
        play_time = end_time - start_time
        
        console.print(Panel(scene.get("ending_text", "Your adventure ends here."), 
                          title="THE END", border_style="red"))
        
        # Show final statistics
        show_final_statistics(story_data, play_time, console)
        
        # Save statistics to global stats
        save_global_statistics(story_data, play_time)
        
        # Ask if player wants to save this story
        if Confirm.ask("Would you like to save this completed story?"):
            save_story(story_data, console)
        
        Prompt.ask("Press Enter to return to main menu")
        return
    
    # Show choices
    if "choices" in scene:
        console.print("\nWhat do you want to do?", style="bold yellow")
        
        choices_table = Table(show_header=False, box=None)
        choices_table.add_column("Option", style="cyan", width=3)
        choices_table.add_column("Action", style="white")
        choices_table.add_column("Requirement", style="dim")
        
        available_choices = []
        for i, choice in enumerate(scene["choices"], 1):
            # Check if player has required item
            requirement = choice.get("requires_item", "")
            if not requirement or has_item(story_data, requirement):
                choices_table.add_row(f"{i}.", choice['text'], "")
                available_choices.append(str(i))
            else:
                choices_table.add_row(f"{i}.", f"[dim]{choice['text']} (Need: {requirement})[/]", f"Locked")
        
        choices_table.add_row("S.", "Save Game", "")
        choices_table.add_row("I.", "View Inventory", "")
        choices_table.add_row("T.", "View Statistics", "")
        
        console.print(choices_table)
        
        # Get player choice
        all_choices = available_choices + ["S", "I", "T", "s", "i", "t"]
        choice = Prompt.ask("Choose", choices=all_choices)
        
        if choice.upper() == "S":
            story_data["statistics"]["saves_used"] += 1
            save_story(story_data, console)
            play_scene(story_data, scene_id, console)
            return
        elif choice.upper() == "I":
            show_inventory(story_data, console)
            play_scene(story_data, scene_id, console)
            return
        elif choice.upper() == "T":
            show_current_statistics(story_data, console)
            play_scene(story_data, scene_id, console)
            return
        
        # Process story choice
        choice_index = int(choice) - 1
        chosen_option = scene["choices"][choice_index]
        
        # Update statistics
        story_data["statistics"]["choices_count"] += 1
        
        # Record the choice
        story_data["choices_made"].append({
            "scene": scene_id,
            "choice": chosen_option["text"],
            "timestamp": datetime.now().isoformat()
        })
        
        # Add item to inventory if specified
        if "gives_item" in chosen_option:
            add_to_inventory(story_data, chosen_option["gives_item"])
            story_data["statistics"]["items_collected"] += 1
            console.print(f"You obtained: {chosen_option['gives_item']}", style="green")
        
        # Check if choice leads to death
        if chosen_option.get("is_death", False):
            story_data["statistics"]["deaths"] += 1
        
        # Show result
        if 'result' in chosen_option:
            console.print(f"\n{chosen_option['result']}", style="italic bright_blue")
        
        # Continue to next scene
        next_scene = chosen_option["next_scene"]
        story_data["current_scene"] = next_scene
        
        Prompt.ask("\nPress Enter to continue", default="")
        console.clear()
        
        play_scene(story_data, next_scene, console)


def get_story_scenes(story_id):
    """Return scenes for the specified story"""
    if story_id == "enchanted_castle":
        return get_enchanted_castle_scenes()
    elif story_id == "dark_forest":
        return get_dark_forest_scenes()
    elif story_id == "space_station":
        return get_space_station_scenes()
    else:
        return get_enchanted_castle_scenes()  # Default


def get_enchanted_castle_scenes():
    """Return dictionary of enchanted castle story scenes"""
    return {
        "start": {
            "description": """
Welcome {player_name} to the Enchanted Castle!

You stand before an ancient castle shrouded in mist. The massive wooden doors 
are slightly ajar, and you can hear strange sounds echoing from within. 
A rusty sign reads: 'Enter if you dare, but beware the guardian's test.'

To your left, you notice a small path leading to what appears to be a garden.
To your right, there's a narrow alley between the castle wall and some old stables.
            """,
            "choices": [
                {
                    "text": "Enter through the main doors",
                    "result": "You push open the heavy doors and step into the castle's grand hall.",
                    "next_scene": "great_hall"
                },
                {
                    "text": "Explore the garden path",
                    "result": "You follow the winding path through overgrown bushes and flowers.",
                    "next_scene": "garden"
                },
                {
                    "text": "Investigate the narrow alley",
                    "result": "You squeeze through the tight space and discover a hidden entrance.",
                    "next_scene": "secret_entrance"
                }
            ]
        },
        
        "great_hall": {
            "description": """
You find yourself in a magnificent great hall with high vaulted ceilings.
Ancient tapestries hang on the walls, and a grand staircase curves upward
to the second floor. 

In the center of the room, there's an ornate pedestal with a golden key
resting on top. However, you notice that touching it might trigger some
kind of mechanism - there are strange symbols glowing around the base.
            """,
            "choices": [
                {
                    "text": "Take the golden key from the pedestal",
                    "result": "You carefully take the key. The symbols stop glowing and you hear a distant door unlock.",
                    "gives_item": "golden_key",
                    "next_scene": "library"
                },
                {
                    "text": "Go to the library",
                    "result": "You enter a vast library filled with dusty tomes and ancient scrolls.",
                    "next_scene": "library"
                },
                {
                    "text": "Climb the grand staircase",
                    "result": "You ascend the stairs to explore the upper floors of the castle.",
                    "next_scene": "upper_floor"
                }
            ]
        },
        
        "garden": {
            "description": """
You enter a magical garden where flowers glow with an ethereal light.
In the center stands an ancient well with a bucket and rope.
A wise-looking owl perches on a nearby branch, watching you intently.

The owl speaks: 'Brave traveler, if you seek the castle's treasure,
you must first prove your worth. Will you help me recover my lost amulet?'
            """,
            "choices": [
                {
                    "text": "Agree to help the owl",
                    "result": "You retrieve a beautiful silver amulet. The owl gives you a magic potion.",
                    "gives_item": "healing_potion",
                    "next_scene": "great_hall"
                },
                {
                    "text": "Politely decline and head back",
                    "result": "The owl looks disappointed. You head back to explore other areas.",
                    "next_scene": "great_hall"
                }
            ]
        },
        
        "library": {
            "description": """
The library is vast and filled with knowledge from ages past.
You find a book about the castle's secrets lying open on a reading table.
            """,
            "choices": [
                {
                    "text": "Read the book carefully",
                    "result": "You learn about the guardian's weakness.",
                    "gives_item": "ancient_knowledge",
                    "next_scene": "upper_floor"
                },
                {
                    "text": "Search for magical items",
                    "result": "You find a protection spell scroll.",
                    "gives_item": "protection_spell",
                    "next_scene": "upper_floor"
                }
            ]
        },
        
        "upper_floor": {
            "description": """
You reach the dragon guardian's chamber. The magnificent dragon speaks:
'Greetings, brave adventurer. Your choices will determine your fate.'
            """,
            "choices": [
                {
                    "text": "Challenge the dragon to combat",
                    "result": "The dragon prepares for battle. This was unwise...",
                    "is_death": True,
                    "next_scene": "battle_ending"
                },
                {
                    "text": "Ask about the castle's purpose",
                    "result": "The dragon is impressed by your wisdom.",
                    "next_scene": "wisdom_ending"
                },
                {
                    "text": "Offer to help the dragon",
                    "requires_item": "healing_potion",
                    "result": "You offer your healing potion. The dragon is moved by your kindness.",
                    "next_scene": "compassion_ending"
                }
            ]
        },
        
        "secret_entrance": {
            "description": """
You discover a hidden treasury! However, it's protected by a magical barrier.
A note warns that only those with the golden key may safely claim the treasures.
            """,
            "choices": [
                {
                    "text": "Try to take treasure without the key",
                    "result": "A curse activates! You feel a dark magic taking hold...",
                    "is_death": True,
                    "next_scene": "cursed_ending"
                },
                {
                    "text": "Leave and find the key first",
                    "result": "Wise choice. You head to find the proper key.",
                    "next_scene": "great_hall"
                },
                {
                    "text": "Use the golden key to claim treasure",
                    "requires_item": "golden_key",
                    "result": "The barrier dissolves! The treasure is yours!",
                    "next_scene": "treasure_ending"
                }
            ]
        },
        
        # Ending scenes
        "treasure_ending": {
            "description": "You successfully claim the castle's treasure! Well done, {player_name}!",
            "is_ending": True,
            "ending_text": "Congratulations! You have achieved the Treasure Hunter ending!"
        },
        
        "wisdom_ending": {
            "description": "Your wisdom impresses the dragon. You are granted the title of Guardian of Wisdom!",
            "is_ending": True,
            "ending_text": "Congratulations! You have achieved the Wisdom ending!"
        },
        
        "compassion_ending": {
            "description": "Your kindness touches the dragon's heart. You become its eternal companion!",
            "is_ending": True,
            "ending_text": "Congratulations! You have achieved the Compassion ending!"
        },
        
        "battle_ending": {
            "description": "The dragon's power overwhelms you. Your adventure ends in defeat.",
            "is_ending": True,
            "ending_text": "You have been defeated. Perhaps wisdom would have served you better."
        },
        
        "cursed_ending": {
            "description": "The curse traps you forever in the castle. Your greed was your downfall.",
            "is_ending": True,
            "ending_text": "You are now cursed to wander these halls forever."
        }
    }


def get_dark_forest_scenes():
    """Return dictionary of dark forest story scenes"""
    return {
        "start": {
            "description": """
Welcome {player_name} to the Dark Forest!

You stand at the edge of a forbidding forest. Dark trees loom overhead,
and strange sounds echo from within. You must find the lost village
that disappeared into these woods centuries ago.

Three paths diverge before you.
            """,
            "choices": [
                {
                    "text": "Take the left path (looks safer)",
                    "result": "You walk along a seemingly peaceful trail.",
                    "next_scene": "safe_path"
                },
                {
                    "text": "Take the middle path (direct route)",
                    "result": "You head straight into the heart of the forest.",
                    "next_scene": "dangerous_path"
                },
                {
                    "text": "Take the right path (mysterious glow)",
                    "result": "You follow a strange light deeper into the woods.",
                    "next_scene": "mystical_path"
                }
            ]
        },
        
        "safe_path": {
            "description": """
The path seems safe, but you realize you're being followed by glowing eyes.
A pack of shadow wolves emerges from the bushes, blocking your way.
            """,
            "choices": [
                {
                    "text": "Try to fight the wolves",
                    "result": "You barely escape, but you're injured.",
                    "is_death": True,
                    "next_scene": "wolf_death"
                },
                {
                    "text": "Slowly back away",
                    "result": "The wolves let you retreat. You find another path.",
                    "next_scene": "village_found"
                }
            ]
        },
        
        "village_found": {
            "description": """
You discover the lost village! The villagers welcome you as their savior.
You have successfully completed your quest!
            """,
            "is_ending": True,
            "ending_text": "Congratulations! You found the lost village and became a hero!"
        },
        
        "wolf_death": {
            "description": """
The shadow wolves were too powerful. Your adventure ends here.
            """,
            "is_ending": True,
            "ending_text": "You were overwhelmed by the creatures of the dark forest."
        }
    }


def get_space_station_scenes():
    """Return dictionary of space station story scenes"""
    return {
        "start": {
            "description": """
Welcome {player_name} to the Abandoned Space Station!

You dock with the silent space station. Emergency lights flicker,
and the artificial gravity feels unstable. Your mission is to discover
what happened to the crew and restore the station's systems.
            """,
            "choices": [
                {
                    "text": "Head to the bridge",
                    "result": "You make your way through dark corridors to the command center.",
                    "next_scene": "bridge"
                },
                {
                    "text": "Check the engineering bay",
                    "result": "You head to the engine room to assess the station's condition.",
                    "next_scene": "engineering"
                }
            ]
        },
        
        "bridge": {
            "description": """
The bridge is in chaos. Consoles spark and alarms blare softly.
You find the captain's log, which might explain what happened here.
            """,
            "choices": [
                {
                    "text": "Read the captain's log",
                    "result": "You learn about an alien artifact that drove the crew mad.",
                    "gives_item": "log_data",
                    "next_scene": "mystery_solved"
                },
                {
                    "text": "Try to restore main power",
                    "result": "Power flickers back on, but something else awakens...",
                    "next_scene": "alien_encounter"
                }
            ]
        },
        
        "mystery_solved": {
            "description": """
You've uncovered the truth! The alien artifact is still aboard,
and you successfully contain it, saving future explorers.
            """,
            "is_ending": True,
            "ending_text": "Congratulations! You solved the mystery and saved the galaxy!"
        },
        
        "alien_encounter": {
            "description": """
An alien entity awakens and you must face it alone in the depths of space.
            """,
            "is_ending": True,
            "ending_text": "Your fate remains unknown in the vast emptiness of space..."
        }
    }


def show_current_statistics(story_data, console):
    """Show current game statistics"""
    stats = story_data["statistics"]
    
    console.print("\nCurrent Game Statistics:", style="bold cyan")
    
    stats_table = Table()
    stats_table.add_column("Statistic", style="yellow")
    stats_table.add_column("Value", style="green")
    
    stats_table.add_row("Scenes Visited", str(stats["scenes_visited"]))
    stats_table.add_row("Choices Made", str(stats["choices_count"]))
    stats_table.add_row("Items Collected", str(stats["items_collected"]))
    stats_table.add_row("Deaths", str(stats["deaths"]))
    stats_table.add_row("Saves Used", str(stats["saves_used"]))
    
    # Calculate play time
    start_time = datetime.fromisoformat(story_data["start_time"])
    current_time = datetime.now()
    play_time = current_time - start_time
    
    hours = int(play_time.total_seconds() // 3600)
    minutes = int((play_time.total_seconds() % 3600) // 60)
    stats_table.add_row("Play Time", f"{hours:02d}:{minutes:02d}")
    
    console.print(stats_table)
    Prompt.ask("Press Enter to continue", default="")


def show_final_statistics(story_data, play_time, console):
    """Show final game statistics"""
    stats = story_data["statistics"]
    
    console.print("\nFinal Game Statistics:", style="bold cyan")
    
    stats_table = Table()
    stats_table.add_column("Statistic", style="yellow")
    stats_table.add_column("Value", style="green")
    
    stats_table.add_row("Total Scenes Visited", str(stats["scenes_visited"]))
    stats_table.add_row("Total Choices Made", str(stats["choices_count"]))
    stats_table.add_row("Items Collected", str(stats["items_collected"]))
    stats_table.add_row("Deaths", str(stats["deaths"]))
    stats_table.add_row("Saves Used", str(stats["saves_used"]))
    
    hours = int(play_time.total_seconds() // 3600)
    minutes = int((play_time.total_seconds() % 3600) // 60)
    seconds = int(play_time.total_seconds() % 60)
    stats_table.add_row("Total Play Time", f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    console.print(stats_table)


def save_global_statistics(story_data, play_time):
    """Save statistics to global stats file"""
    stats_file = "player_stats.json"
    
    # Load existing stats or create new
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r') as f:
                global_stats = json.load(f)
        except:
            global_stats = {"games_played": 0, "total_time": 0, "stories_completed": {}}
    else:
        global_stats = {"games_played": 0, "total_time": 0, "stories_completed": {}}
    
    # Update global stats
    global_stats["games_played"] += 1
    global_stats["total_time"] += play_time.total_seconds()
    
    story_id = story_data["story_id"]
    if story_id not in global_stats["stories_completed"]:
        global_stats["stories_completed"][story_id] = 0
    global_stats["stories_completed"][story_id] += 1
    
    # Save updated stats
    try:
        with open(stats_file, 'w') as f:
            json.dump(global_stats, f, indent=2)
    except Exception as e:
        pass  # Fail silently if can't save


def show_player_statistics(console):
    """Show overall player statistics"""
    stats_file = "player_stats.json"
    
    if not os.path.exists(stats_file):
        console.print("\nNo statistics available yet. Play some games first!", style="yellow")
        Prompt.ask("Press Enter to continue", default="")
        return
    
    try:
        with open(stats_file, 'r') as f:
            global_stats = json.load(f)
    except:
        console.print("\nError loading statistics!", style="red")
        Prompt.ask("Press Enter to continue", default="")
        return
    
    console.print("\nPlayer Statistics:", style="bold cyan")
    
    # Overall stats
    overall_table = Table(title="Overall Statistics")
    overall_table.add_column("Statistic", style="yellow")
    overall_table.add_column("Value", style="green")
    
    overall_table.add_row("Games Played", str(global_stats.get("games_played", 0)))
    
    total_seconds = global_stats.get("total_time", 0)
    total_hours = int(total_seconds // 3600)
    total_minutes = int((total_seconds % 3600) // 60)
    overall_table.add_row("Total Play Time", f"{total_hours}h {total_minutes}m")
    
    console.print(overall_table)
    
    # Story completion stats
    if global_stats.get("stories_completed"):
        console.print("\nStories Completed:", style="bold yellow")
        
        story_table = Table()
        story_table.add_column("Story", style="magenta")
        story_table.add_column("Times Completed", style="green")
        
        stories = get_available_stories()
        for story_id, count in global_stats["stories_completed"].items():
            story_name = stories.get(story_id, {}).get("title", story_id)
            story_table.add_row(story_name, str(count))
        
        console.print(story_table)
    
    Prompt.ask("\nPress Enter to continue", default="")


def save_story(story_data, console):
    """Save the story progress"""
    # Create saves directory if it doesn't exist
    if not os.path.exists("saves"):
        os.makedirs("saves")
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"saves/{story_data['player_name']}_{timestamp}.json"
    
    # Save data
    try:
        with open(filename, 'w') as f:
            json.dump(story_data, f, indent=2)
        console.print(f"Game saved successfully as {filename}", style="green")
    except Exception as e:
        console.print(f"Error saving game: {e}", style="red")


def load_saved_story(console):
    """Load a saved story"""
    if not os.path.exists("saves"):
        console.print("\nNo saved stories found!", style="yellow")
        return
    
    save_files = [f for f in os.listdir("saves") if f.endswith('.json')]
    
    if not save_files:
        console.print("\nNo saved stories found!", style="yellow")
        return
    
    # Show available saves
    console.print("\nAvailable saved stories:", style="bold yellow")
    
    saves_table = Table()
    saves_table.add_column("ID", style="cyan", width=3)
    saves_table.add_column("Player Name", style="magenta")
    saves_table.add_column("Story", style="blue")
    saves_table.add_column("Date Saved", style="green")
    saves_table.add_column("Scene", style="yellow")
    
    valid_saves = []
    for i, filename in enumerate(save_files, 1):
        try:
            with open(f"saves/{filename}", 'r') as f:
                save_data = json.load(f)
            
            # Extract info from filename and data
            date_str = filename.split('_')[1].replace('.json', '')
            date_formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            
            story_title = save_data.get('title', 'Unknown Story')
            
            saves_table.add_row(
                str(i),
                save_data.get('player_name', 'Unknown'),
                story_title,
                date_formatted,
                save_data.get('current_scene', 'Unknown')
            )
            valid_saves.append((str(i), filename, save_data))
            
        except Exception as e:
            console.print(f"Error reading save file {filename}: {e}", style="red")
    
    if not valid_saves:
        console.print("No valid save files found!", style="red")
        return
    
    console.print(saves_table)
    
    # Get user choice
    choice_options = [save[0] for save in valid_saves]
    choice = Prompt.ask("Choose save to load", choices=choice_options + ["cancel"], default="cancel")
    
    if choice == "cancel":
        return
    
    # Load the chosen save
    for save_id, filename, save_data in valid_saves:
        if save_id == choice:
            console.print(f"Loading story for {save_data['player_name']}...", style="green")
            console.clear()
            play_scene(save_data, save_data['current_scene'], console)
            break


def add_to_inventory(story_data, item):
    """Add an item to player's inventory"""
    if item not in story_data["inventory"]:
        story_data["inventory"].append(item)


def has_item(story_data, item):
    """Check if player has a specific item"""
    return item in story_data["inventory"]


def remove_from_inventory(story_data, item):
    """Remove an item from player's inventory"""
    if item in story_data["inventory"]:
        story_data["inventory"].remove(item)


def show_inventory(story_data, console):
    """Display player's inventory"""
    inventory = story_data.get("inventory", [])
    
    if not inventory:
        console.print("\nYour inventory is empty.", style="yellow")
        return
    
    console.print("\nYour Inventory:", style="bold cyan")
    inventory_table = Table(show_header=False, box=None)
    inventory_table.add_column("Item", style="green")
    
    for item in inventory:
        inventory_table.add_row(f"• {item}")
    
    console.print(inventory_table)
    Prompt.ask("Press Enter to continue", default="")


if __name__ == "__main__":
    main()