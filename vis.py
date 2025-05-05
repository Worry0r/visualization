import json
import matplotlib

matplotlib.use("TkAgg")  # Or 'Qt5Agg', 'WXAgg',
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from matplotlib.widgets import Button, Slider
from PIL import Image


def load_data(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {filepath} not found!")
        return None
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from file {filepath}")
        return None


def process_hero_data(data):
    hero_positions = {}
    last_positions = {}
    hero_colors = {}

    hero_teams = {}
    if data and "heroes" in data and "-1" in data["heroes"]:
        for hero_name, hero_data in data["heroes"]["-1"].items():
            hero_teams[hero_name] = hero_data.get("teamNum", 0)

    if data and "heroes" in data:
        for tick, heroes in data["heroes"].items():
            if tick == "-1":
                continue
            tick = float(tick)
            for hero_name, hero_data in heroes.items():
                team = hero_teams.get(hero_name, 0)
                color = "blue" if team == 2 else "red" if team == 3 else "gray"
                hero_colors[hero_name] = color

                position = hero_data.get("position")
                if position:
                    x, y = position.get("x", 0), position.get("y", 0)
                    last_positions[hero_name] = (x, y)
                else:
                    x, y = last_positions.get(hero_name, (8000, 8000))

                hero_positions.setdefault(hero_name, []).append((tick, x, y))

    return hero_positions, hero_colors


def process_building_data(data):
    building_positions = []
    building_colors = []
    if data and "buildings" in data:
        for tick, buildings in data["buildings"].items():
            for building_id, building_data in buildings.items():
                position = building_data.get("position")
                team = building_data.get("teamNum", 0)
                color = "blue" if team == 2 else "red" if team == 3 else "orange"

                if position:
                    x, y = position.get("x", 0), position.get("y", 0)
                    building_positions.append((x, y))
                    building_colors.append(color)
    return building_positions, building_colors


def process_creep_data(data):
    creep_positions = {}
    creep_colors = {}
    creep_death_times = {}

    if data and "creeps" in data:
        for tick, creeps in data["creeps"].items():
            tick = float(tick)
            for creep_id, creep_data in creeps.items():
                if creep_data.get("deleted", False):
                    creep_death_times[creep_id] = tick
                    continue

                position = creep_data.get("position")
                if position:
                    x, y = position.get("x", 0), position.get("y", 0)

                    team = creep_data.get("teamNum", 0)
                    color = (
                        "lightblue"
                        if team == 2
                        else "magenta"
                        if team == 3
                        else "orange"
                    )
                    creep_colors[creep_id] = color

                    if creep_id not in creep_positions:
                        creep_positions[creep_id] = []
                    creep_positions[creep_id].append((tick, x, y))

    return creep_positions, creep_colors, creep_death_times


def setup_plot(
    hero_positions,
    building_positions,
    building_colors,
    hero_colors,
    creep_positions,
    creep_colors,
    background_image_path="Game_map_7.33.webp",
):
    all_coords = (
        [(x, y) for positions in hero_positions.values() for _, x, y in positions]
        + building_positions
        + [
            (x, y)
            for positions in creep_positions.values()
            for _, x, y in positions
            if x is not None
        ]
    )

    if all_coords:
        x_min, x_max = (
            np.min([x for x, _ in all_coords]),
            np.max([x for x, _ in all_coords]),
        )
        y_min, y_max = (
            np.min([y for _, y in all_coords]),
            np.max([y for _, y in all_coords]),
        )
    else:
        x_min, x_max, y_min, y_max = -100, 100, -100, 100

    fig, ax = plt.subplots(figsize=(9, 9))
    plt.subplots_adjust(bottom=0.15)
    if background_image_path:
        img = Image.open(background_image_path)
        ax.imshow(
            img,
            extent=[x_min - 1500, x_max + 1500, y_min - 1000, y_max + 1600],
            aspect="auto",
        )
    ax.set_xlim(x_min - 100, x_max + 100)
    ax.set_ylim(y_min - 100, y_max + 100)
    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")
    ax.grid(True)

    lines = {
        hero: ax.plot([], [], "o", markersize=10, color=hero_colors[hero], label=hero)[
            0
        ]
        for hero in hero_positions
    }

    if building_positions:
        building_scatter = ax.scatter(
            *zip(*building_positions),
            marker="^",
            s=140,
            c=building_colors,
            label="Buildings",
        )
    else:
        building_scatter = ax.scatter(
            [], [], marker="^", s=100, color="gray", label="Buildings"
        )

    creep_scatter = ax.scatter([], [], marker="s", s=40, color="gray", label="Creeps")

    tick_text = ax.text(
        0.02,
        0.02,
        "Current Tick: 0",
        transform=ax.transAxes,
        fontsize=14,
        fontweight="bold",
        bbox=dict(facecolor="white", alpha=0.8, boxstyle="round"),
    )

    return fig, ax, lines, tick_text, building_scatter, creep_scatter


def animate(
    frame_number,
    lines,
    hero_positions,
    tick_text,
    creep_scatter,
    creep_positions,
    creep_colors,
    creep_death_times,
):
    tick_text.set_text(f"Current Tick: {frame_number}")

    for hero, line in lines.items():
        if frame_number < len(hero_positions[hero]):
            x, y = hero_positions[hero][frame_number][1:]
            line.set_data([x], [y])
        else:
            line.set_data([], [])

    creep_data = []
    creep_color_data = []
    for creep_id, positions in creep_positions.items():
        if (
            creep_id in creep_death_times
            and creep_death_times[creep_id] <= frame_number
        ):
            continue

        valid_positions = [
            (tick, x, y) for tick, x, y in positions if tick <= frame_number
        ]

        if valid_positions:
            last_tick, x, y = valid_positions[-1]
            creep_data.append((x, y))
            creep_color_data.append(creep_colors[creep_id])

    if creep_data:
        creep_scatter.set_offsets(np.array(creep_data))
        creep_scatter.set_color(creep_color_data)
    else:
        creep_scatter.set_offsets(np.empty((0, 2)))

    plt.draw()
    return tuple(lines.values()) + (tick_text, creep_scatter)


def main():
    data = load_data("dummy_data.json")
    if not data:
        return

    hero_positions, hero_colors = process_hero_data(data)
    building_positions, building_colors = process_building_data(data)
    creep_positions, creep_colors, creep_death_times = process_creep_data(data)

    fig, ax, lines, tick_text, building_scatter, creep_scatter = setup_plot(
        hero_positions,
        building_positions,
        building_colors,
        hero_colors,
        creep_positions,
        creep_colors,
        background_image_path="Game_map_7.33.webp",
    )

    frames_count = max(len(p) for p in hero_positions.values())
    ani = FuncAnimation(
        fig,
        lambda frame: animate(
            frame,
            lines,
            hero_positions,
            tick_text,
            creep_scatter,
            creep_positions,
            creep_colors,
            creep_death_times,
        ),
        frames=frames_count,
        interval=200,
        repeat=True,
        blit=False,
    )

    is_playing = True

    def toggle_play(_):
        nonlocal is_playing
        if is_playing:
            ani.event_source.stop()
            btn_playpause.label.set_text("Play")
        else:
            ani.event_source.start()
            btn_playpause.label.set_text("Pause")
        is_playing = not is_playing
        plt.draw()

    def reset_animation(_):
        ani.event_source.stop()
        slider.set_val(0)
        animate(
            0,
            lines,
            hero_positions,
            tick_text,
            creep_scatter,
            creep_positions,
            creep_colors,
            creep_death_times,
        )
        btn_playpause.label.set_text("Play")
        plt.draw()

    def slider_update(val):
        frame = int(val)
        ani.event_source.stop()
        animate(
            frame,
            lines,
            hero_positions,
            tick_text,
            creep_scatter,
            creep_positions,
            creep_colors,
            creep_death_times,
        )
        plt.draw()

    ax_playpause = plt.axes([0.4, 0.02, 0.1, 0.04])
    btn_playpause = Button(ax_playpause, "Pause")
    btn_playpause.on_clicked(toggle_play)

    ax_reset = plt.axes([0.52, 0.02, 0.1, 0.04])
    btn_reset = Button(ax_reset, "Reset")
    btn_reset.on_clicked(reset_animation)

    ax_slider = plt.axes([0.15, 0.02, 0.2, 0.04])
    slider = Slider(ax_slider, "Frame", 0, frames_count - 1, valinit=0, valstep=1)
    slider.on_changed(slider_update)

    plt.show()


if __name__ == "__main__":
    main()
