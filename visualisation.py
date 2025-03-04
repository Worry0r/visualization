import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from matplotlib.widgets import Button

# Read the JSON file
with open("heroes.json") as f:
    data = json.load(f)

# Extract all ticks and their hero positions
ticks = list(data["heroes"].keys())
hero_positions = {}

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

all_x = [pos[1] for positions in hero_positions.values() for pos in positions]
all_y = [pos[2] for positions in hero_positions.values() for pos in positions]

x_min, x_max = np.min(all_x), np.max(all_x)
y_min, y_max = np.min(all_y), np.max(all_y)

# Create figure with space for tick display
fig, ax = plt.subplots(figsize=(8, 7))
plt.subplots_adjust(top=0.9)  # Make room for tick display
ax.grid(True)

ax.set_xlabel("X Position")
ax.set_ylabel("Y Position")

# Set the axis limits based on min and max coordinates
ax.set_xlim(x_min - 100, x_max + 100)
ax.set_ylim(y_min - 100, y_max + 100)

# Create a text object for current tick display
tick_text = ax.text(
    0.02,
    0.95,
    "Current Tick: 0",
    transform=ax.transAxes,
    fontsize=14,
    fontweight="bold",
    bbox=dict(facecolor="white", alpha=0.8, boxstyle="round"),
)

# Initialize lines for each hero
lines = {}
for hero_name in hero_positions:
    (line,) = ax.plot([], [], "o", markersize=8, label=hero_name)
    lines[hero_name] = line


# Animation function
def animate(frame_number):
    """
    Update the plot for each animation frame, showing only the current position
    of each hero as a dot without movement history.
    """
    # Update the tick text
    tick_text.set_text(f"Current Tick: {frame_number}")

    # Update each hero's position data
    for hero_name, hero_line in lines.items():
        # Get all recorded positions for this hero
        hero_data = hero_positions[hero_name]

        # Make sure we have data for this frame
        if frame_number < len(hero_data):
            # Extract only the current position (not the history)
            current_x = [hero_data[frame_number][1]]  # Just the x at current frame
            current_y = [hero_data[frame_number][2]]  # Just the y at current frame

            # Update the line data with new coordinates
            hero_line.set_data(current_x, current_y)
        else:
            # If no data for this frame, show nothing
            hero_line.set_data([], [])

    # Return all updated lines and the tick text
    return tuple(lines.values()) + (tick_text,)


# Animation settings
frames_count = len(hero_positions[next(iter(hero_positions.keys()))])
ani = FuncAnimation(
    fig,
    animate,
    frames=frames_count,
    interval=100,  # Fast animation (10ms per frame)
    repeat=True,
    blit=True,
)

# Add buttons for playback control
ax_playpause = plt.axes([0.45, 0.02, 0.1, 0.04])
btn_playpause = Button(ax_playpause, "Pause")

is_playing = True


def toggle_play(event):
    global is_playing
    if is_playing:
        ani.event_source.stop()
        btn_playpause.label.set_text("Play")
    else:
        ani.event_source.start()
        btn_playpause.label.set_text("Pause")
    is_playing = not is_playing
    plt.draw()


btn_playpause.on_clicked(toggle_play)

plt.tight_layout()
plt.show()
