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

## DevMode Commands

Available commands:
   - 0: toggle devmode

   Position & Size:
   - x+number -> set x position. Example: x150
   - y+number -> set y position. Example: y300
   - w+number -> set width. Example: w200
   - h+number -> set height. Example: h100
   
   Colors:
   - c+r,g,b -> set background/fill color. Example: c255,0,0 (red)
   - tc+r,g,b -> set text color. Example: tc0,255,0 (green)
   - hc+r,g,b -> set handle color (toggles). Example: hc100,100,100
   
   Text:
   - t+text -> set text. Example: tHello World
   - fs+number -> set font size. Example: fs24
   - align+value -> set text alignment (left/center/right). Example: aligncenter
   
   Slider:
   - sv+number -> set slider value. Example: sv75
   - smin+number -> set slider min value. Example: smin0
   - smax+number -> set slider max value. Example: smax200
   
   Toggle:
   - ton -> turn toggle on
   - toff -> turn toggle off
   - tflip -> flip toggle state
   
   General:
   - n+name -> set element name. Example: nmy_button
   - a+number -> set alpha/opacity (0-255). Example: a200
   
   System:
   - add+type -> add new element (button/slider/toggle/image/text_display)
   - overridel -> save layout config
   - overrides -> save settings config
   - refreshui -> refresh UI elements
   - centertext -> center text in element
   - del -> delete ui element **(CANT UNDO. USE WITH CAUTION)**

## Contributing

Contributions are welcome!
Please fork the repo and create a pull request with your improvements or bug fixes.
Make sure to update tests and documentation accordingly.

---

## Liscence

This project is licensed under the MIT License. See the LICENSE file for details.