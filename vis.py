import json
import matplotlib.pyplot as plt
from collections import defaultdict

# Read the JSON file
with open('heroes.json') as f:
    data = json.load(f)

# Extract hero positions by tick and hero
hero_positions = defaultdict(list)
tick_data = []

for tick, heroes in data["heroes"].items():
    tick_time = int(tick)  # Convert to integer if it's a string representation of number
    for hero_name, hero_info in heroes.items():
        x = hero_info.get("position", {}).get("x", None)
        y = hero_info.get("position", {}).get("y", None)
        if x is not None and y is not None:
            # Store position as a tuple of (time, x, y)
            tick_data.append((tick_time, hero_name, float(x), float(y)))

# Determine the min and max for x and y to set grid limits
x_coords = [pos[2] for pos in tick_data]
y_coords = [pos[3] for pos in tick_data]
min_x, max_x = min(x_coords), max(x_coords)
min_y, max_y = min(y_coords), max(y_coords)

# Create subplots: one for distribution of positions and another for movement over time
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))

# Plotting the position distribution on a grid
for tick_time, hero_name, x, y in tick_data:
    ax1.scatter(x, y, marker='o', color='blue', alpha=0.5)
ax1.set_xlabel('X Position')
ax1.set_ylabel('Y Position')
ax1.set_title('Distribution of Hero Positions')
ax1.grid(True)

# Adding grid limits
ax1.set_xlim(min_x - 100, max_x + 100)  # Adding padding to the limits
ax1.set_ylim(min_y - 100, max_y + 100)

plt.tight_layout()
plt.show()
