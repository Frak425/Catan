To-do list:
-Create spritesheet for buttons and other ui
-Update button class to include:
  -Sprites
  -Hover effects
  -Drag-and-drop?
-Turn order logic
-Settings panel
-Add all game settings set-up buttons
-Fix logic for tile/node data structures

Create spritesheet for buttons and other ui
  I am working on this right now
  In progress:
  -Settings buttons
  -Home screen buttons
  -Game-setup buttons
  -Game ui buttons

Update button class
  Updating init
  This will probably be a difficult task and only possible after the spritesheets are finished
  Hover effects would include logic like checking mouse position as well as click and drag mechanics
  Not a high priority

Turn order logic
  This would include both the board-setup and actual play
  board-setup:
    -Determine first player
    -Counterclockwise until all players have placed first road and settlement. Gather resources of tiles touching settlement
    -Go back clockwise to place remaining settlements and roads. Game-setup finished
    -Proceed in order of the first player counterclockwise, rolling the dice every turn


  
