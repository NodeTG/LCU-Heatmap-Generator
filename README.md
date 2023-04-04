## LCU Heatmap Generator
This application integrates with LEGO City Undercover to create a heatmap/path that shows where the player has travelled in the hub world.

https://youtu.be/pL_0p8GlwCw

## Requirements

 - Python 3.10
 - Pygame
 - Pymeow (might need an old version)

## Usage

 1. Open LEGO City Undercover and load a save file.
 2. When you are in the overworld, open `main.py`
 3. You should see the map window appear. If not, something has gone wrong.
 4. Click and drag with the mouse to move the map around, and use the scroll wheel to zoom (you can also press Page Up/Down).
 5. There should be a green arrow on the map where your player is standing in-game. A blue path will appear behind them whenever they move, and a purple line will appear if they teleport or move very quickly.
 6. Use the Minus and Equals keys to change the thickness of the line.

## Troubleshooting / Known Issues

 - The line may appear invisible when combining certain thicknesses and zoom levels. This can be fixed by increasing line thickness or zooming in.
 - The player arrow will not automatically start updating after leaving and re-entering the city, or when opening the application before the city is loaded. This can be solved by pressing F5 while the application is in focus.
 - Player position on the map is slightly offset to their actual position in game (often slightly lower than they should be).
 - The rotation of the arrow on the map does not change when in a vehicle.
