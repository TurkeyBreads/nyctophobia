# Nyctophobia

> **A text-based MUD where darkness is more than just the absence of light.**

Nyctophobia is a single-player, text-based **Multi-User Dungeon (MUD)** developed as a J1 Group Project.

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
Fight or Prepare
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

## 🔧 Planned Updates & Fixes

- [ ] Prompt to rename Explorer
- [ ] Difficulty to change Explorer starting stats
- [ ] Fix `get_creature_stats`
- [ ] No pick up Item when no Item
- [ ] Doesn't show Item if defeating a Creature in a Room with Item
- [ ] Make Items Available box more obvious
- [ ] Make defeating Monster more obvious
- [ ] Move Info box below Room Display *
- [ ] Determine how difficulty affects Boss health
- [ ] Add multiple Items/Creatures per Room
- [ ] Make Boss only stay on Level 10
- [ ] Add ability to back out of fights
- [ ] Add Boss dialogue/conversation + 2 endings
- [ ] Make viewing Stats a menu which can be exited
- [ ] Fix use Item during battle
- [ ] Write Room numbers in double digits
- [ ] Update Battle, Game Loop, Options and Main Menu to use decorator
- [ ] Multiple Items/Monsters
- [ ] Make negative Room numbers letters instead
- [ ] Go back to Main Menu after Game Over

### After

- [ ] Add docstrings
- [ ] Make a Debug Mode (teleport + change stats)
- [ ] Power scaling throughout levels / balancing (algorithmically generated)
- [ ] New Monsters, new Items
- [ ] Add full story before and after (add NPCs)
- [ ] Possibly create an AI-generated maze

> **Note:** Player Level always assumes you start at 1, because it only changes on `move()`.

---

**Nyctophobia** — *When the darkness starts moving, run.*
