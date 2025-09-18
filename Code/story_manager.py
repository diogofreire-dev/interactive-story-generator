"""
Story Manager Module - Handles story data and scenes
"""

class StoryManager:
    def get_available_stories(self):
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

    def _get_forest_scenes(self):
        """Return forest story scenes"""
        return {
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
            "forest_witch": {
                "title": "The Forest Witch",
                "description": "An old woman opens the door. She has kind eyes but a mysterious smile. 'I've been expecting you,' she says.",
                "choices": [
                    {"text": "Ask for help", "next_scene": "forest_help"},
                    {"text": "Ask about the forest", "next_scene": "forest_knowledge"},
                    {"text": "Politely excuse yourself", "next_scene": "forest_right"}
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
            "forest_escape_end": {
                "ending": True,
                "ending_title": "SAFE ESCAPE ENDING",
                "description": "With the witch's help, you safely escape the dark forest. You return home with magical herbs and incredible stories to tell."
            }
        }

    def _get_space_scenes(self):
        """Return space story scenes"""
        return {
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
            "space_computer": {
                "title": "Main Computer",
                "description": "The computer reveals that an alien organism was brought aboard for study. It has since escaped and infected the crew.",
                "choices": [
                    {"text": "Access quarantine protocols", "next_scene": "space_quarantine"},
                    {"text": "Search for survivor locations", "next_scene": "space_survivors"},
                    {"text": "Initiate self-destruct sequence", "next_scene": "space_destruct"}
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
            "space_escape": {
                "title": "Escape Plan",
                "description": "You and Dr. Chen make it to the escape pods. Earth's rescue ship arrives just as you launch.",
                "choices": [
                    {"text": "Launch the escape pod", "next_scene": "space_survivor_end", "ending": True, "ending_title": "SURVIVOR ENDING"}
                ]
            },
            "space_survivor_end": {
                "ending": True,
                "ending_title": "SURVIVOR ENDING",
                "description": "You and Dr. Chen escape the station and are rescued by Earth's ship. The station is later destroyed by military forces, but you both survive to tell the tale."
            }
        }

    def get_story_scenes(self, story_type):
        """Return scenes for the specified story type"""
        stories = {
            "castle": self._get_castle_scenes(),
            "forest": self._get_forest_scenes(),
            "space": self._get_space_scenes()
        }
        
        return stories.get(story_type, {})

    def _get_castle_scenes(self):
        """Return castle story scenes"""
        return {
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
        }