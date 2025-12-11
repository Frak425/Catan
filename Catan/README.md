# Catan - Python Board Game

A digital implementation of the classic board game *Catan* built using Python and Pygame.  
This project showcases modular game architecture using manager classes to handle input, graphics, game state, and UI.

---

## Table of Contents

- [About](#about)  
- [Features](#features)  
- [Installation](#installation)  
- [How to Play](#how-to-play)  
- [Project Structure](#project-structure)  
- [Usage](#usage)  
- [Contributing](#contributing)  
- [License](#license)  

---

## About

As a board game lover, I have many board games, but nobody to play them with. Since my family is very busy, I have found myself lacking the players to play my favorite game: Settlers of  My inspiration for this project was to fix that problem while also teaching myself the essence of game development. Although this is my first game development project, I hope you enjoy it!

---

## Features

- Turn-based resource management gameplay
- Interactive game board with nodes and tiles  
- Custom UI components and menus   
- Singleplayer / multiplayer(TODO) compatibility

---

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/Frak425/git
   cd catan
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
---

## How to Play

-Run the game:
   ```bash
   python main.py
   ```

-Use mouse clicks to navigate menus and interact with the game board.

-Follow on-screen prompts to build roads, settlements, and cities.

-Manage your resources wisely to become the dominant player!

---

## Usage

-The main.py file initializes all managers and starts the game loop.

-Managers communicate via setter methods to avoid circular dependencies.

-Input is handled via the InputManager based on current game state.

-Drawing and rendering are performed in the GraphicsManager.

-Game logic and state transitions are controlled by the GameManager.

---

## Contributing

Contributions are welcome!
Please fork the repo and create a pull request with your improvements or bug fixes.
Make sure to update tests and documentation accordingly.

---

## Liscence

This project is licensed under the MIT License. See the LICENSE file for details.