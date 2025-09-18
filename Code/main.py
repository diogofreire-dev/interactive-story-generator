#!/usr/bin/env python3
"""
Interactive Story Generator - CS50P Final Project
Author: [Your Name]
Main entry point for the game
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt

from game_logic import GameLogic
from Code.stats_manager import StatsManager
from Code.ui_manager import UIManager

console = Console()

def main():
    """Main game loop"""
    console.clear()
    show_title()
    
    game_logic = GameLogic()
    stats_manager = StatsManager()
    ui_manager = UIManager()
    
    while True:
        choice = show_main_menu()
        
        if choice == "1":
            game_logic.play_game()
        elif choice == "2":
            game_logic.load_game()
        elif choice == "3":
            stats_manager.show_global_stats()
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

if __name__ == "__main__":
    main()