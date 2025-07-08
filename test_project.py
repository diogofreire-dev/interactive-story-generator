#!/usr/bin/env python3
"""
Tests for Interactive Story Generator - CS50P Final Project
"""

import pytest
import json
import os
import tempfile
from datetime import datetime, timedelta
from interactive_story_generator import (
    get_story_scenes,
    get_available_stories,
    save_final_stats,
    show_inventory,
    show_current_stats
)

def test_get_story_scenes():
    """Test that story scenes are properly loaded"""
    # Test castle story
    castle_scenes = get_story_scenes("castle")
    assert "castle_start" in castle_scenes
    assert "choices" in castle_scenes["castle_start"]
    assert len(castle_scenes["castle_start"]["choices"]) > 0
    
    # Test forest story
    forest_scenes = get_story_scenes("forest")
    assert "forest_start" in forest_scenes
    assert "choices" in forest_scenes["forest_start"]
    
    # Test space story
    space_scenes = get_story_scenes("space")
    assert "space_start" in space_scenes
    assert "choices" in space_scenes["space_start"]
    
    # Test invalid story
    invalid_scenes = get_story_scenes("invalid")
    assert invalid_scenes == {}

def test_get_available_stories():
    """Test that available stories are returned correctly"""
    stories = get_available_stories()
    
    # Check that all expected stories are present
    assert "castle" in stories
    assert "forest" in stories
    assert "space" in stories
    
    # Check story structure
    for story_id, story_info in stories.items():
        assert "title" in story_info
        assert "description" in story_info
        assert "difficulty" in story_info
        assert isinstance(story_info["title"], str)
        assert isinstance(story_info["description"], str)
        assert isinstance(story_info["difficulty"], str)

def test_story_structure():
    """Test that all stories have proper structure"""
    for story_type in ["castle", "forest", "space"]:
        scenes = get_story_scenes(story_type)
        start_scene = f"{story_type}_start"
        
        # Check that start scene exists
        assert start_scene in scenes
        
        # Check that start scene has required fields
        assert "description" in scenes[start_scene]
        assert "choices" in scenes[start_scene]
        assert len(scenes[start_scene]["choices"]) > 0
        
        # Check choice structure
        for choice in scenes[start_scene]["choices"]:
            assert "text" in choice
            assert "next_scene" in choice
            assert isinstance(choice["text"], str)
            assert isinstance(choice["next_scene"], str)

def test_story_endings():
    """Test that all stories have proper endings"""
    for story_type in ["castle", "forest", "space"]:
        scenes = get_story_scenes(story_type)
        
        # Check that there are ending scenes
        ending_scenes = [scene for scene in scenes.values() if scene.get("ending")]
        assert len(ending_scenes) > 0, f"No ending scenes found in {story_type}"
        
        # Check that endings have proper structure
        for ending in ending_scenes:
            assert "ending_title" in ending
            assert "description" in ending
            assert ending["ending"] == True

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

def test_death_scenarios():
    """Test that death scenarios are properly handled"""
    for story_type in ["castle", "forest", "space"]:
        scenes = get_story_scenes(story_type)
        
        death_choices = []
        for scene_data in scenes.values():
            if "choices" in scene_data:
                for choice in scene_data["choices"]:
                    if choice.get("death"):
                        death_choices.append(choice)
        
        # Check death choice structure
        for death_choice in death_choices:
            assert "death_message" in death_choice
            assert isinstance(death_choice["death_message"], str)
            assert len(death_choice["death_message"]) > 0

def test_save_and_load_functionality():
    """Test save and load game functionality"""
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock game state
        game_state = {
            "player_name": "Test Player",
            "story_type": "castle",
            "current_scene": "castle_start",
            "inventory": ["golden key"],
            "visited_scenes": ["castle_start"],
            "choices_made": [
                {
                    "scene": "castle_start",
                    "choice": "Enter through the main doors",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "deaths": 0,
            "saves_used": 1,
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
            
            # Verify loaded data
            assert loaded_state["player_name"] == "Test Player"
            assert loaded_state["story_type"] == "castle"
            assert "golden key" in loaded_state["inventory"]
            assert loaded_state["deaths"] == 0
            assert loaded_state["saves_used"] == 1
            assert loaded_state["items_collected"] == 1
            
        finally:
            os.chdir(original_cwd)

def test_statistics_functionality():
    """Test statistics calculation and storage"""
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Mock game state
            game_state = {
                "player_name": "Test Player",
                "story_type": "castle",
                "deaths": 2,
                "items_collected": 3,
                "choices_made": ["choice1", "choice2"],
                "visited_scenes": ["scene1", "scene2", "scene3"]
            }
            
            play_time = timedelta(minutes=15)
            
            # Test save_final_stats function
            save_final_stats(game_state, play_time)
            
            # Verify stats file was created
            assert os.path.exists("stats/global_stats.json")
            
            # Load and verify stats
            with open("stats/global_stats.json", 'r') as f:
                stats = json.load(f)
            
            assert stats["total_games"] == 1
            assert stats["total_deaths"] == 2
            assert stats["total_items_collected"] == 3
            assert "stories_completed" in stats
            assert stats["stories_completed"]["castle"] == 1
            
        finally:
            os.chdir(original_cwd)

def test_game_state_validation():
    """Test that game state contains required fields"""
    required_fields = [
        "player_name",
        "story_type", 
        "current_scene",
        "inventory",
        "visited_scenes",
        "choices_made",
        "deaths",
        "saves_used",
        "start_time",
        "items_collected"
    ]
    
    # Create a mock game state
    game_state = {
        "player_name": "Test",
        "story_type": "castle",
        "current_scene": "castle_start",
        "inventory": [],
        "visited_scenes": [],
        "choices_made": [],
        "deaths": 0,
        "saves_used": 0,
        "start_time": datetime.now().isoformat(),
        "items_collected": 0
    }
    
    # Check that all required fields are present
    for field in required_fields:
        assert field in game_state, f"Required field {field} missing from game state"

def test_show_inventory():
    """Test inventory display functionality"""
    # Test with empty inventory
    game_state_empty = {"inventory": []}
    # This would normally print to console, just ensure no errors
    try:
        show_inventory(game_state_empty)
    except Exception as e:
        pytest.fail(f"show_inventory failed with empty inventory: {e}")
    
    # Test with items in inventory
    game_state_items = {"inventory": ["sword", "potion", "key"]}
    try:
        show_inventory(game_state_items)
    except Exception as e:
        pytest.fail(f"show_inventory failed with items: {e}")

def test_show_current_stats():
    """Test current statistics display"""
    game_state = {
        "player_name": "Test Player",
        "story_type": "castle",
        "start_time": datetime.now().isoformat(),
        "visited_scenes": ["scene1", "scene2"],
        "choices_made": ["choice1", "choice2"],
        "items_collected": 2,
        "deaths": 1,
        "saves_used": 0
    }
    
    try:
        show_current_stats(game_state)
    except Exception as e:
        pytest.fail(f"show_current_stats failed: {e}")

def test_story_completion_paths():
    """Test that each story has at least one completion path"""
    for story_type in ["castle", "forest", "space"]:
        scenes = get_story_scenes(story_type)
        start_scene = f"{story_type}_start"
        
        # Use breadth-first search to find if any ending is reachable
        visited = set()
        queue = [start_scene]
        found_ending = False
        
        while queue and not found_ending:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            if current in scenes:
                scene = scenes[current]
                
                # Check if this is an ending
                if scene.get("ending"):
                    found_ending = True
                    break
                
                # Add next scenes to queue
                if "choices" in scene:
                    for choice in scene["choices"]:
                        if "next_scene" in choice:
                            queue.append(choice["next_scene"])
        
        assert found_ending, f"No reachable ending found in {story_type} story"

def test_multiple_story_support():
    """Test that the system supports multiple stories correctly"""
    stories = get_available_stories()
    
    # Should have at least 3 stories
    assert len(stories) >= 3
    
    # Each story should have unique scenes
    all_scenes = set()
    for story_type in stories.keys():
        scenes = get_story_scenes(story_type)
        story_scenes = set(scenes.keys())
        
        # Check for scene name conflicts
        overlap = all_scenes.intersection(story_scenes)
        assert len(overlap) == 0, f"Scene name conflicts found: {overlap}"
        
        all_scenes.update(story_scenes)

def test_item_requirements():
    """Test that item requirements are properly handled"""
    for story_type in ["castle", "forest", "space"]:
        scenes = get_story_scenes(story_type)
        
        # Find all items that can be collected
        available_items = set()
        for scene_data in scenes.values():
            if "choices" in scene_data:
                for choice in scene_data["choices"]:
                    if "item" in choice:
                        available_items.add(choice["item"])
        
        # Find all item requirements
        for scene_data in scenes.values():
            if "choices" in scene_data:
                for choice in scene_data["choices"]:
                    if "requires_item" in choice:
                        required_item = choice["requires_item"]
                        # Required item should be obtainable in the story
                        assert required_item in available_items, f"Required item {required_item} not obtainable in {story_type}"

if __name__ == "__main__":
    pytest.main([__file__])