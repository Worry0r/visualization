import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Read the JSON file
with open('heroes.json') as f:
    data = json.load(f)

# Extract all ticks and their hero positions
ticks = list(data["heroes"].keys())
hero_positions = {}

for tick in ticks:
    heroes = data["heroes"][tick]
    for hero_name, hero_data in heroes.items():
        position = hero_data.get("position", {})
        x = position.get("x", 0)
        y = position.get("y", 0)
        
        if hero_name not in hero_positions:
            hero_positions[hero_name] = []
        hero_positions[hero_name].append((float(tick), x, y))

# Calculate min and max for x and y coordinates
all_x = [pos[1] for positions in hero_positions.values() for pos in positions]
all_y = [pos[2] for positions in hero_positions.values() for pos in positions]

x_min, x_max = np.min(all_x), np.max(all_x)
y_min, y_max = np.min(all_y), np.max(all_y)

# Create the figure and axis
fig, ax = plt.subplots(figsize=(6, 6))
ax.grid(True)
ax.set_title("Hero Movement Over Time")
ax.set_xlabel("X Position")
ax.set_ylabel("Y Position")

# Initialize lines for each hero
lines = {}
for hero_name in hero_positions:
    line, = ax.plot([], [], 'o-', label=hero_name)
    lines[hero_name] = line

# Create the legend
ax.legend()

# Animation function
def animate(i):
    for name, line in lines.items():
        positions = hero_positions[name]
        x = [float(tick) for tick, _, _ in positions[:i+1]]
        y = [pos for _, pos, _ in positions[:i+1]]
        
        line.set_data(x, y)
    
    return tuple(lines.values())

# Animation settings
ani = FuncAnimation(fig, animate, frames=len(hero_positions[next(iter(hero_positions.keys()))]), interval=200)

# Set the axis limits based on min and max coordinates
ax.set_xlim(x_min - 100, x_max + 100)
ax.set_ylim(y_min - 100, y_max + 100)

# Display the plot
current_tick = len(hero_positions)
plt.title(f"Hero Positions - Current Tick: {current_tick}")

plt.show()
