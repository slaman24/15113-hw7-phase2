Fireboy and Watergirl: 
This project is a high-performance reconstruction of the classic cooperative platformer, developed in Python using the Pygame library. The engine focuses on precise mechanical control and procedural animation, providing a polished visual experience without the need for external image assets or sprite sheets.

The game requires players to navigate two characters through environmental puzzles to collect gems and reach designated exits. Fireboy is immune to lava but destroyed by water, while Watergirl can traverse water but is vulnerable to lava. The system uses a state-machine approach to manage transitions between active gameplay, game-over sequences, and victory conditions.

The characters utilize a custom procedural animation system that transforms their shapes in real-time. A sine-wave function creates rhythmic walking cycles, while a squash-and-stretch effect adjusts character height based on vertical velocity to add visual weight to jumps. The physics engine is tuned with a 0.8 gravity constant and a -17 jump impulse to ensure responsive, grounded movement.

The interface features a 700-pixel game world and a 200-pixel sidebar to keep stats and instructions visible at all times. Fireboy is controlled with Arrow keys and Watergirl with WASD. If a character hits a hazard, the game enters a "Try Again" state, allowing for an immediate level reset via the R key.
