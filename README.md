# Roblox Forsaken Generator Solver

Automatically solves the 6x6 wire connection puzzles in Roblox Forsaken's generator minigame.

## Usage

```bash
pip install -r requirements.txt
python main.py
```

Take a screenshot of the generator puzzle, save as `input.png` and run. The solver will:

1. **Extract** colored wire dots from the screenshot
2. **Match** pairs of similar colors
3. **Solve** connection paths without crossing using backtracking
4. **Visualize** solution as `solved_paths.png`

## Files

- `vision.py` - Image processing and visualization
- `solver.py` - Backtracking puzzle solver
- `main.py` - Main pipeline

Designed for Forsaken's 6x6 generator puzzles. Ensures all wire pairs can be connected.
