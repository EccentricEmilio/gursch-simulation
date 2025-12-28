# Gursch Game Engine (AI & Simulation Focus)

## Purpose
This project implements a **Python card game engine** for the game *Gursch*.  
The primary goal is to **simulate large numbers of games**, collect statistics, and **train/evaluate AI strategies**.

UI (terminal or web) is **secondary** and used only for debugging or visualization.

---

## Core Design Principles
- Game logic is **pure, deterministic, and UI-agnostic**
- No input/output or networking inside the core engine
- Same engine supports:
  - AI vs AI simulation
  - Terminal debugging
  - Optional future UI

---

## Architecture Overview
- **GameState**
  - Holds all mutable game data
  - No I/O, no rules
- **GameEngine**
  - Applies rules and transitions GameState
  - Validates moves and processes turns/rounds
- **PlayerPolicy (interface)**
  - Chooses moves based on state
  - Used for AI, random play, or human adapters

Optional:
- Terminal UI (debug)
- FastAPI/Web UI (viewer/playground only)

---

## Simulation Model
- Core loop is pure Python:
  ```python
  for _ in range(N):
      engine.play_game(policies)
  ```
- No web-driven game loop
- Web/API (if used) is event-driven and non-authoritative

---

## Card Representation
- Uses `pydealer` internally
- Cards are immediately converted to:
  - Strings (e.g. `"AH"`, `"7D"`) or simple value objects
- No external module depends on `pydealer`

---

## State Ownership Rules
- Only **GameEngine** mutates GameState
- UI / policies may read state and propose moves
- No direct state mutation outside engine

---

## Status
- Game rules mostly implemented
- Terminal version used to validate logic
- Actively refactoring toward:
  - Cleaner engine/state separation
  - High-performance simulation and AI training

---

**One-line summary:**  
*A simulation-first Python card game engine designed for AI training and statistical analysis, with UI as an optional visualization layer.*