import json
import matplotlib.pyplot as plt

# Read the JSON file
file_path = 'heroes.json'
with open(file_path) as f:
    data = json.load(f)

heroes_data = data["heroes"]

# Extract all hero positions and calculate min/max x and y
positions = []
all_x = []
all_y = []

for tick in heroes_data.values():
    for hero, info in tick.items():
        if "position" in info:
            x = info["position"]["x"]
            y = info["position"]["y"]
            positions.append((x, y))
            all_x.append(x)
            all_y.append(y)

# Calculate min and max for x and y
min_x, max_x = min(all_x), max(all_x)
min_y, max_y = min(all_y), max(all_y)

# Create the plot
plt.figure(figsize=(7, 7))
for pos in positions:
    plt.plot(pos[0], pos[1], 'bo', markersize=4)

plt.title('Hero Positions')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.grid(True)
plt.axis([min_x, max_x, min_y, max_y])

# Print the limits
print(f"Minimum X: {min_x}")
print(f"Maximum X: {max_x}")
print(f"Minimum Y: {min_y}")
print(f"Maximum Y: {max_y}")

plt.show()
