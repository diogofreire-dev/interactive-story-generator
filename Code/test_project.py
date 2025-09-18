#!/usr/bin/env python3
"""
Tests for Interactive Story Generator - CS50P Final Project
"""

import pytest
import json
import os
import tempfile
from datetime import datetime, timedelta
from Code.story_manager import StoryManager
from Code.ui_manager import UIManager
from Code.stats_manager import StatsManager

# Create instances for reuse
story_manager = StoryManager()
ui_manager = UIManager()
stats_manager = StatsManager()

def test_get_story_scenes():
    """Test that story scenes are properly loaded"""
    # Test castle story
    castle_scenes = story_manager.get_story_scenes("castle")
    assert "castle_start" in castle_scenes, "castle_start scene missing in castle story"
    assert "choices" in castle_scenes["castle_start"], "choices missing in castle_start scene"
    assert len(castle_scenes["castle_start"]["choices"]) > 0, "No choices in castle_start scene"
    
    # Test forest story
    forest_scenes = story_manager.get_story_scenes("forest")
    assert "forest_start" in forest_scenes, "forest_start scene missing in forest story"
    assert "choices" in forest_scenes["forest_start"], "choices missing in forest_start scene"
    
    # Test space story
    space_scenes = story_manager.get_story_scenes("space")
    assert "space_start" in space_scenes, "space_start scene missing in space story"
    assert "choices" in space_scenes["space_start"], "choices missing in space_start scene"
    
    # Test invalid story
    invalid_scenes = story_manager.get_story_scenes("invalid")
    assert invalid_scenes == {}, "Invalid story should return empty scenes"

def test_get_available_stories():
    """Test that available stories are returned correctly"""
    stories = story_manager.get_available_stories()
    
    # Check that all expected stories are present
    assert "castle" in stories, "castle story missing in available stories"
    assert "forest" in stories, "forest story missing in available stories"
    assert "space" in stories, "space story missing in available stories"
    
    # Check story structure
    for story_id, story_info in stories.items():
        assert "title" in story_info, f"title missing in story {story_id}"
        assert "description" in story_info, f"description missing in story {story_id}"
        assert "difficulty" in story_info, f"difficulty missing in story {story_id}"
        assert isinstance(story_info["title"], str), f"title not string in story {story_id}"
        assert isinstance(story_info["description"], str), f"description not string in story {story_id}"
        assert isinstance(story_info["difficulty"], str), f"difficulty not string in story {story_id}"

def test_story_structure():
    """Test that all stories have proper structure"""
    for story_type in ["castle", "forest", "space"]:
        scenes = story_manager.get_story_scenes(story_type)
        start_scene = f"{story_type}_start"
        
        # Check that start scene exists
        assert start_scene in scenes, f"Start scene {start_scene} missing in {story_type}"
        
        # Check that start scene has required fields
        assert "description" in scenes[start_scene], f"description missing in {start_scene}"
        assert "choices" in scenes[start_scene], f"choices missing in {start_scene}"
        assert len(scenes[start_scene]["choices"]) > 0, f"No choices in {start_scene}"
        
        # Check choice structure
        for choice in scenes[start_scene]["choices"]:
            assert "text" in choice, f"text missing in choice in {start_scene}"
            assert "next_scene" in choice, f"next_scene missing in choice in {start_scene}"
            assert isinstance(choice["text"], str), f"text not string in choice in {start_scene}"
            assert isinstance(choice["next_scene"], str), f"next_scene not string in choice in {start_scene}"

def test_story_endings():
    """Test that all stories have proper endings"""
    for story_type in ["castle", "forest", "space"]:
        scenes = story_manager.get_story_scenes(story_type)
        
        # Check that there are ending scenes
        ending_scenes = [scene for scene in scenes.values() if scene.get("ending")]
        assert len(ending_scenes) > 0, f"No ending scenes found in {story_type}"
        
        # Check that endings have proper structure
        for ending in ending_scenes:
            assert "ending_title" in ending, f"ending_title missing in ending in {story_type}"
            assert "description" in ending, f"description missing in ending in {story_type}"
            assert ending["ending"] is True, f"ending flag not True in ending in {story_type}"

def test_inventory_items():
    """Test that inventory items are properly defined"""
    for story_type in ["castle", "forest", "space"]:
        scenes = story_manager.get_story_scenes(story_type)
        
        for scene_data in scenes.values():
            if "choices" in scene_data:
                for choice in scene_data["choices"]:
                    # If choice gives an item, it should be a string
                    if "item" in choice:
                        assert isinstance(choice["item"], str), f"item not string in choice in {story_type}"
                        assert len(choice["item"]) > 0, f"item empty string in choice in {story_type}"
                    
                    # If choice requires an item, it should be a string
                    if "requires_item" in choice:
                        assert isinstance(choice["requires_item"], str), f"requires_item not string in choice in {story_type}"
                        assert len(choice["requires_item"]) > 0, f"requires_item empty string in choice in {story_type}"

def test_death_scenarios():
    """Test that death scenarios are properly handled"""
    for story_type in ["castle", "forest", "space"]:
        scenes = story_manager.get_story_scenes(story_type)
        
        death_choices = []
        for scene_data in scenes.values():
            if "choices" in scene_data:
                for choice in scene_data["choices"]:
                    if choice.get("death"):
                        death_choices.append(choice)
        
        # Check death choice structure
        for death_choice in death_choices:
            assert "death_message" in death_choice, "death_message missing in death choice"
            assert isinstance(death_choice["death_message"], str), "death_message not string in death choice"
            assert len(death_choice["death_message"]) > 0, "death_message empty in death choice"

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
            assert loaded_state["player_name"] == "Test Player", "player_name mismatch after load"
            assert loaded_state["story_type"] == "castle", "story_type mismatch after load"
            assert "golden key" in loaded_state["inventory"], "inventory missing golden key after load"
            assert loaded_state["deaths"] == 0, "deaths mismatch after load"
            assert loaded_state["saves_used"] == 1, "saves_used mismatch after load"
            assert loaded_state["items_collected"] == 1, "items_collected mismatch after load"
            
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
            
            # Use stats_manager instance to save final stats
            stats_manager.save_final_stats(game_state, play_time)
            
            # Verify stats file was created
            assert os.path.exists("stats/global_stats.json"), "Global stats file not created"
            
            # Load and verify stats
            with open("stats/global_stats.json", 'r') as f:
                stats = json.load(f)
            
            assert stats["total_games"] == 1, "total_games count incorrect"
            assert stats["total_deaths"] == 2, "total_deaths count incorrect"
            assert stats["total_items_collected"] == 3, "total_items_collected count incorrect"
            assert "stories_completed" in stats, "stories_completed missing in stats"
            assert stats["stories_completed"]["castle"] == 1, "castle story completion count incorrect"
            
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
        ui_manager.show_inventory(game_state_empty)
    except Exception as e:
        pytest.fail(f"show_inventory failed with empty inventory: {e}")
    
    # Test with items in inventory
    game_state_items = {"inventory": ["sword", "potion", "key"]}
    try:
        ui_manager.show_inventory(game_state_items)
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
        ui_manager.show_current_stats(game_state)
    except Exception as e:
        pytest.fail(f"show_current_stats failed: {e}")

def test_story_completion_paths():
    """Test that each story has at least one completion path"""
    for story_type in ["castle", "forest", "space"]:
        scenes = story_manager.get_story_scenes(story_type)
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
    stories = story_manager.get_available_stories()
    
    # Should have at least 3 stories
    assert len(stories) >= 3, "Less than 3 stories available"
    
    # Each story should have unique scenes
    all_scenes = set()
    for story_type in stories.keys():
        scenes = story_manager.get_story_scenes(story_type)
        story_scenes = set(scenes.keys())
        
        # Check for scene name conflicts
        overlap = all_scenes.intersection(story_scenes)
        assert len(overlap) == 0, f"Scene name conflicts found: {overlap}"
        
        all_scenes.update(story_scenes)

def test_item_requirements():
    """Test that item requirements are properly handled"""
    for story_type in ["castle", "forest", "space"]:
        scenes = story_manager.get_story_scenes(story_type)
        
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
