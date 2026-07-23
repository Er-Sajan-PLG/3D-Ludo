# Unity Game Engine Scaffold for 3D Ludo

This folder contains a Unity-compatible C# scaffold for the 3D Ludo game.

## What is included

- `Assets/Scripts/GameManager.cs` - core turn and piece logic translated to Unity C#.

## Usage

1. Open Unity and load the `unity` folder as a project.
2. Create an empty GameObject in the scene.
3. Attach the `GameManager` script to that GameObject.
4. Press Play to initialize the game and execute turns.

## Notes

- This scaffold is a starting point: it does not include 3D board or piece prefabs.
- The script uses simple `PlayerData` and `PieceData` classes for core game state.
- You can extend it with Unity UI buttons, piece rendering, and board layout.
