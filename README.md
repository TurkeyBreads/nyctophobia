# Nyctophobia

> **A text-based SUD where darkness is more than just the absence of light.**

Nyctophobia is a **Single-User Dungeon (SUD)** developed as a J1 Group Project.

The Player must navigate a strange underground maze, discover useful items, survive encounters with creatures, and ultimately defeat the creature responsible for the dungeon's shifting darkness.

## 🎮 Game Overview

The game takes place inside **Nyctophobia**, an underground maze where darkness seems to behave like a living force.

The environment is eerie and disorienting rather than purely grim. Shadows appear to move when the Player looks away, corridors seem different in darkness, and familiar dungeon features behave in unexpected ways.

The core gameplay loop is:

```text
Explore
  ↓
Discover Rooms
  ↓
Find Items / Encounter Creatures
  ↓
Fight or Flight
  ↓
Explore Further
  ↓
Confront the Monster
  ↓
Defeat the Monster
  ↓
Victory
```

## 🗺️ Gameplay

The maze consists of interconnected **Rooms**. The Player begins in a designated Start Room and can travel between rooms using available paths.

In a Room, the Player can:

* Explore available paths
* Attack Creatures
* Pick up Items
* Use Items
* Inspect their current situation

Creatures can attack the Player. The main Monster is capable of moving through the maze and interacting with Items, making the final encounter less predictable.

### Objective

The objective is simple:

> **Find and defeat the Monster.**

The Player must manage their health, items and position within the maze to survive long enough to reach the final encounter.

## 🌑 Theme

Nyctophobia focuses on **darkness, uncertainty and disorientation**.

Environmental descriptions may include:

* Fading or distorted light
* Unexplained sounds
* Moving shadows
* Unusual corridors
* Rooms that feel different when revisited
* Strange behaviour from otherwise ordinary objects

The game aims to create tension through **what the Player cannot see or predict**, rather than relying purely on frightening descriptions.

## 🧩 Game Structure

The game is built around several core entities:

* **Player** — explores the maze and interacts with the game world.
* **Room** — represents an area of the maze and its connections.
* **Creature** — an entity capable of attacking the Player.
* **Monster** — the main Creature that must be defeated to complete the game.
* **Item** — objects that can be collected and used by the Player.
* **Maze** — contains the Rooms, Creatures and Items that make up the game world.

## 🛠️ Technology

* **Language:** Python
* **Interface:** Text-based command-line interface
* **Dependencies:** None
* **Players:** Single-player

The project uses object-oriented programming and separates the game's entities and gameplay logic into manageable components.

## 🚧 Development Roadmap

| Priority | Feature            | Description                                                            |
| -------- | ------------------ | ---------------------------------------------------------------------- |
| **P1**   | Core Gameplay Loop | Room display, player decisions, basic controls and combat              |
| **P2**   | Entities           | Player, Rooms, Creatures, Items and Monster attributes/actions         |
| **P3**   | Monster AI         | Allow the Monster to act and move independently                        |
| **P4**   | Expansion          | Additional rooms, story, environmental details and dungeon progression |

The project will initially focus on a small, reliable game that can be thoroughly tested before expanding its content.

## 🧪 Testing

The game includes automated tests that simulate Player actions and verify that the expected outcomes occur.

Tests cover core behaviour such as:

* Moving between Rooms
* Picking up Items
* Using Items
* Attacking Creatures
* Taking damage
* Defeating Creatures
* Interacting with the Monster
* Completing the Maze

## 👥 Project Structure

This project is developed as a group project, with responsibilities divided between team members.

| Role                              | Responsibility                          |
| --------------------------------- | --------------------------------------- |
| **Technical Lead** (Jasper)       | Overall architecture and code structure |
| **Data Designer** (Evan)          | Game content and data schema            |
| **Game Programmer** (Christopher) | Core gameplay and game logic            |

## 📜 Project Requirements

The project follows these requirements:

* Written entirely in Python
* No external dependencies
* Entirely text-based
* Designed for a single player
* Developed collaboratively by the team

## Update 2.1.0 Notes

### 🛠️ Bug Fixes & Refactoring
* **Deferred Flee Display**: Resolved layout ordering where fleeing rendered status boxes prior to updating room viewports. Flee notifications now route into `turn_logs` and render directly beneath the newly entered room's map.
* **Buffered Entity Feedback**: Refactored `Player.move()`, `Player.pick_up()`, and `Player.use_item()` in `entities.py` to return formatted status strings instead of writing directly to stdout.
* **Fixed Combat Stats Crash**: Resolved an `AttributeError` when requesting stats during battle by adding a base `get_stats()` implementation to the `Entity` class.
* **Safe Combat Item Menu**: Attempting to use items in battle with an empty inventory no longer raises an index exception.
* **Context-Sensitive Room Actions**: The `Pick Up Item` menu option dynamically disappears when no items are inside a room.

### 🎮 Gameplay & Mechanics
* **Multiple Entities Per Room**: Standardized CSV loading to support multiple items or monsters per room using comma-separated values (e.g. `items: "W,L2"`).
* **Dynamic Player Name & Backstory**: Players can now input a custom explorer name which gets integrated into a newly added 2-paragraph introductory lore sequence.
* **Flee / Run Action in Combat**:
  * Run away from enemies into a random connected room.
  * Running while carrying items forces you to drop a random item in your hurry.
  * Running with no items causes you to trip and take `10-20` physical damage.
  * Trapped corners disable running.
* **Expanded Difficulty Scaling**: Difficulty selection now balances player starting stats (HP, Attack, Defence) in addition to Boss health and movement frequency.

### 🎨 UI & Presentation Improvements
* **Centralised Turn Logs**: Movement actions, item interactions, enemy movements, and combat flee results are unified into a single decorated notification frame below the map at the end of every turn cycle.
* **Item Info Display**: Moved item notifications into a decorated `Display.info` frame directly under the ASCII room display for improved readability.
* **Victories & Events in Boxes**: Defeated enemy gains, boss alerts, and flee outcomes are wrapped in clear UI boxes.
* **Buffered Stats & End Screens**: Viewing stats, victory screens, and the Game Over Recap now pause with an interactive buffer (`Press Enter`), preventing vital text from scrolling off the screen.
* **Decorated Game Flows**: Replaced raw menu prints in `game_loop()`, `battle()`, `options_menu()`, and `main_menu()` with standard `Display` frame decorators.

### 🎲 Miscellaneous Fixes
* **Erroneous Test Cases**
* **Error within CSV**

**Nyctophobia** — *When the darkness starts moving, run.*
