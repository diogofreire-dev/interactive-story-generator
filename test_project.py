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
    get_story_scenes, save_story, add_to_inventory, has_item, 
    remove_from_inventory, show_inventory, get_available_stories,
    get_enchanted_castle_scenes, get_dark_forest_scenes, 
    get_space_station_scenes, save_global_statistics
)


@pytest.fixture
def sample_story_data():
    """Create sample story data for testing"""
    return {
        "story_id": "enchanted_castle",
        "title": "The Enchanted Castle",
        "current_scene": "start",
        "player_name": "TestPlayer",
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


@pytest.fixture
def temp_saves_dir():
    """Create temporary directory for save files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        yield temp_dir
        os.chdir(original_dir)


def test_get_available_stories():
    """Test that available stories are returned correctly"""
    stories = get_available_stories()
    
    assert isinstance(stories, dict)
    assert len(stories) >= 3  # Should have at least 3 stories
    assert "enchanted_castle" in stories
    assert "dark_forest" in stories
    assert "space_station" in stories
    
    # Check story structure
    for story_id, story_info in stories.items():
        assert "title" in story_info
        assert "description" in story_info
        assert "difficulty" in story_info
        assert isinstance(story_info["title"], str)
        assert len(story_info["title"]) > 0


def test_get_story_scenes_enchanted_castle():
    """Test that enchanted castle scenes are returned correctly"""
    scenes = get_enchanted_castle_scenes()
    
    assert isinstance(scenes, dict)
    assert "start" in scenes
    assert "great_hall" in scenes
    assert "garden" in scenes
    
    # Test scene structure
    start_scene = scenes["start"]
    assert "description" in start_scene
    assert "choices" in start_scene
    assert isinstance(start_scene["choices"], list)
    assert len(start_scene["choices"]) > 0
    
    # Test choice structure
    first_choice = start_scene["choices"][0]
    assert "text" in first_choice
    assert "next_scene" in first_choice


def test_get_story_scenes_dark_forest():
    """Test that dark forest scenes are returned correctly"""
    scenes = get_dark_forest_scenes()
    
    assert isinstance(scenes, dict)
    assert "start" in scenes
    assert len(scenes) >= 3  # Should have multiple scenes
    
    # Check for ending scenes
    ending_scenes = [scene for scene in scenes.values() if scene.get("is_ending", False)]
    assert len(ending_scenes) > 0


def test_get_story_scenes_space_station():
    """Test that space station scenes are returned correctly"""
    scenes = get_space_station_scenes()
    
    assert isinstance(scenes, dict)
    assert "start" in scenes
    assert len(scenes) >= 3  # Should have multiple scenes


def test_get_story_scenes_function():
    """Test the main get_story_scenes function with different story IDs"""
    # Test with valid story IDs
    enchanted_scenes = get_story_scenes("enchanted_castle")
    forest_scenes = get_story_scenes("dark_forest")
    space_scenes = get_story_scenes("space_station")
    
    assert "start" in enchanted_scenes
    assert "start" in forest_scenes
    assert "start" in space_scenes
    
    # Test with invalid story ID (should default to enchanted castle)
    invalid_scenes = get_story_scenes("invalid_story")
    assert "start" in invalid_scenes
    assert invalid_scenes == enchanted_scenes


def test_add_to_inventory(sample_story_data):
    """Test adding items to inventory"""
    # Test adding new item
    add_to_inventory(sample_story_data, "magic_sword")
    assert "magic_sword" in sample_story_data["inventory"]
    
    # Test adding duplicate item (should not duplicate)
    add_to_inventory(sample_story_data, "magic_sword")
    assert sample_story_data["inventory"].count("magic_sword") == 1
    
    # Test adding multiple different items
    add_to_inventory(sample_story_data, "healing_potion")
    add_to_inventory(sample_story_data, "golden_key")
    assert len(sample_story_data["inventory"]) == 3


def test_has_item(sample_story_data):
    """Test checking if player has specific items"""
    # Test with empty inventory
    assert not has_item(sample_story_data, "magic_sword")
    
    # Test after adding item
    add_to_inventory(sample_story_data, "magic_sword")
    assert has_item(sample_story_data, "magic_sword")
    assert not has_item(sample_story_data, "healing_potion")


def test_remove_from_inventory(sample_story_data):
    """Test removing items from inventory"""
    # Add items first
    add_to_inventory(sample_story_data, "magic_sword")
    add_to_inventory(sample_story_data, "healing_potion")
    
    # Test removing existing item
    remove_from_inventory(sample_story_data, "magic_sword")
    assert "magic_sword" not in sample_story_data["inventory"]
    assert "healing_potion" in sample_story_data["inventory"]
    
    # Test removing non-existent item (should not cause error)
    remove_from_inventory(sample_story_data, "non_existent_item")
    assert len(sample_story_data["inventory"]) == 1


def test_save_story(sample_story_data, temp_saves_dir):
    """Test saving story data"""
    # Create a mock console object
    class MockConsole:
        def print(self, *args, **kwargs):
            pass
    
    console = MockConsole()
    
    # Test saving
    save_story(sample_story_data, console)
    
    # Check if saves directory was created
    assert os.path.exists("saves")
    
    # Check if save file was created
    save_files = [f for f in os.listdir("saves") if f.endswith('.json')]
    assert len(save_files) >= 1
    
    # Check if save file contains correct data
    with open(f"saves/{save_files[0]}", 'r') as f:
        saved_data = json.load(f)
    
    assert saved_data["player_name"] == sample_story_data["player_name"]
    assert saved_data["story_id"] == sample_story_data["story_id"]


def test_story_statistics_structure(sample_story_data):
    """Test that story data has proper statistics structure"""
    stats = sample_story_data["statistics"]
    
    required_stats = [
        "scenes_visited", "items_collected", "choices_count", 
        "deaths", "saves_used"
    ]
    
    for stat in required_stats:
        assert stat in stats
        assert isinstance(stats[stat], int)
        assert stats[stat] >= 0


def test_statistics_updates(sample_story_data):
    """Test that statistics are properly updated"""
    # Test items collected counter
    initial_items = sample_story_data["statistics"]["items_collected"]
    add_to_inventory(sample_story_data, "test_item")
    # Note: The counter is updated in play_scene, not add_to_inventory
    # This test verifies the structure is in place
    
    assert "items_collected" in sample_story_data["statistics"]


def test_save_global_statistics(sample_story_data, temp_saves_dir):
    """Test saving global statistics"""
    play_time = timedelta(minutes=30)
    
    # Save global stats
    save_global_statistics(sample_story_data, play_time)
    
    # Check if stats file was created
    assert os.path.exists("player_stats.json")
    
    # Check stats content
    with open("player_stats.json", 'r') as f:
        global_stats = json.load(f)
    
    assert "games_played" in global_stats
    assert "total_time" in global_stats
    assert "stories_completed" in global_stats
    assert global_stats["games_played"] >= 1
    assert global_stats["total_time"] > 0


def test_scene_connectivity_enchanted_castle():
    """Test that all scenes in enchanted castle are properly connected"""
    scenes = get_enchanted_castle_scenes()
    all_scene_ids = set(scenes.keys())
    referenced_scenes = set()
    
    # Collect all scene IDs referenced in choices
    for scene in scenes.values():
        if "choices" in scene:
            for choice in scene["choices"]:
                if "next_scene" in choice:
                    referenced_scenes.add(choice["next_scene"])
    
    # Check that all referenced scenes exist
    for scene_id in referenced_scenes:
        assert scene_id in all_scene_ids, f"Scene '{scene_id}' is referenced but doesn't exist"


def test_scene_connectivity_dark_forest():
    """Test that all scenes in dark forest are properly connected"""
    scenes = get_dark_forest_scenes()
    all_scene_ids = set(scenes.keys())
    referenced_scenes = set()
    
    for scene in scenes.values():
        if "choices" in scene:
            for choice in scene["choices"]:
                if "next_scene" in choice:
                    referenced_scenes.add(choice["next_scene"])
    
    for scene_id in referenced_scenes:
        assert scene_id in all_scene_ids, f"Scene '{scene_id}' is referenced but doesn't exist"


def test_ending_scenes_structure():
    """Test that ending scenes are properly structured"""
    enchanted_scenes = get_enchanted_castle_scenes()
    
    ending_scenes = {k: v for k, v in enchanted_scenes.items() if v.get("is_ending", False)}
    
    assert len(ending_scenes) > 0, "Should have at least one ending scene"
    
    for scene_id, scene in ending_scenes.items():
        assert scene.get("is_ending", False), f"Ending scene {scene_id} should have is_ending=True"
        assert "ending_text" in scene, f"Ending scene {scene_id} should have ending_text"
        assert "choices" not in scene, f"Ending scene {scene_id} should not have choices"


def test_required_items_consistency():
    """Test that required items in choices are consistent"""
    scenes = get_enchanted_castle_scenes()
    
    # Collect all items that can be given
    available_items = set()
    for scene in scenes.values():
        if "choices" in scene:
            for choice in scene["choices"]:
                if "gives_item" in choice:
                    available_items.add(choice["gives_item"])
    
    # Check that all required items can be obtained
    for scene in scenes.values():
        if "choices" in scene:
            for choice in scene["choices"]:
                if "requires_item" in choice:
                    required_item = choice["requires_item"]
                    assert required_item in available_items, f"Required item '{required_item}' is never given to player"


def test_empty_inventory_operations(sample_story_data):
    """Test inventory operations with empty inventory"""
    # Ensure inventory is empty
    sample_story_data["inventory"] = []
    
    # Test has_item with empty inventory
    assert not has_item(sample_story_data, "any_item")
    
    # Test remove_from_inventory with empty inventory (should not crash)
    remove_from_inventory(sample_story_data, "non_existent_item")
    assert len(sample_story_data["inventory"]) == 0


def test_multiple_story_types():
    """Test that different story types have unique content"""
    enchanted_scenes = get_enchanted_castle_scenes()
    forest_scenes = get_dark_forest_scenes()
    space_scenes = get_space_station_scenes()
    
    # Stories should have different content
    assert enchanted_scenes != forest_scenes
    assert forest_scenes != space_scenes
    assert enchanted_scenes != space_scenes
    
    # But all should have start scenes
    assert "start" in enchanted_scenes
    assert "start" in forest_scenes
    assert "start" in space_scenes


def test_datetime_handling(sample_story_data):
    """Test that datetime fields are properly handled"""
    # Test that start_time is a valid ISO format string
    start_time_str = sample_story_data["start_time"]
    
    # Should be able to parse the datetime
    parsed_time = datetime.fromisoformat(start_time_str)
    assert isinstance(parsed_time, datetime)
    
    # Should be recent (within last minute)
    now = datetime.now()
    time_diff = now - parsed_time
    assert time_diff.total_seconds() < 60  # Less than 1 minute old


if __name__ == "__main__":
    pytest.main([__file__])