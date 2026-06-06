from pathlib import Path
import os
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MEDIA_DIR = PROJECT_ROOT / "docs" / "media"

os.environ.setdefault("MPLCONFIGDIR", "/tmp/chaos_game_matplotlib")

import matplotlib

matplotlib.use("Agg")

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(PROJECT_ROOT))

from src.chaos_game import generate_chaos_game, regular_polygon
from src.plotting import draw_fractal, vertex_colors


def setup_axis(ax, title=None):
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title)


def save_iteration_rule():
    vertices = regular_polygon(3)
    colors = vertex_colors(len(vertices))
    current = np.array([-0.42, -0.18])
    chosen_index = 1
    chosen_vertex = vertices[chosen_index]
    ratio = 0.5
    next_point = (1 - ratio) * current + ratio * chosen_vertex

    fig, ax = plt.subplots(figsize=(7, 5), dpi=160)
    setup_axis(ax, "One Chaos Game step")
    ax.plot(
        np.append(vertices[:, 0], vertices[0, 0]),
        np.append(vertices[:, 1], vertices[0, 1]),
        color="0.25",
        linewidth=1.0,
        alpha=0.25,
    )
    ax.scatter(
        vertices[:, 0],
        vertices[:, 1],
        s=70,
        facecolors="white",
        edgecolors=colors,
        linewidths=2.0,
    )
    ax.scatter(*current, s=55, color="0.15", label="current point")
    ax.scatter(*next_point, s=55, color="#d9480f", label="next point")
    ax.plot(
        [current[0], chosen_vertex[0]],
        [current[1], chosen_vertex[1]],
        color="#d9480f",
        linewidth=1.4,
        alpha=0.45,
    )
    ax.annotate(
        "",
        xy=next_point,
        xytext=current,
        arrowprops={"arrowstyle": "->", "color": "#d9480f", "lw": 1.8},
    )
    ax.text(current[0] - 0.13, current[1] - 0.09, "$x_n$", fontsize=13)
    ax.text(next_point[0] + 0.03, next_point[1] + 0.03, "$x_{n+1}$", fontsize=13)
    ax.text(
        chosen_vertex[0] + 0.04,
        chosen_vertex[1] + 0.04,
        "$v_i$",
        fontsize=13,
        color=colors[chosen_index],
    )
    ax.text(
        -0.95,
        -1.10,
        "$x_{n+1} = (1-r)x_n + r v_i$",
        fontsize=14,
        color="0.15",
    )
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.25, 1.15)
    fig.tight_layout()
    fig.savefig(MEDIA_DIR / "iteration_rule.png", bbox_inches="tight")
    plt.close(fig)


def save_progression():
    np.random.seed(8)
    vertices = regular_polygon(3)
    point_count = 50_000
    points, choices = generate_chaos_game(vertices, ratio=0.5, point_count=point_count)
    frame_counts = [200, 1_000, 8_000, point_count]

    fig, axes = plt.subplots(2, 2, figsize=(8, 8), dpi=160)
    for ax, visible_count in zip(axes.ravel(), frame_counts):
        colors = vertex_colors(len(vertices))
        ax.scatter(
            points[:visible_count, 0],
            points[:visible_count, 1],
            s=0.18,
            c=colors[choices[:visible_count]],
            linewidths=0,
        )
        setup_axis(ax, f"{visible_count:,} points")

    fig.suptitle("The Sierpinski triangle emerges progressively", y=0.98)
    fig.tight_layout()
    fig.savefig(MEDIA_DIR / "sierpinski_progression.png", bbox_inches="tight")
    plt.close(fig)


def save_vertex_coloring():
    np.random.seed(13)
    ratio = 2 / 3
    point_count = 150_000
    vertices = regular_polygon(6)
    points, choices = generate_chaos_game(
        vertices,
        ratio=ratio,
        point_count=point_count,
    )
    fig = draw_fractal(
        points=points,
        vertex_choices=choices,
        vertices=vertices,
        shape_name="Hexagon",
        ratio=ratio,
        total_points=len(points),
        show_vertices=True,
        color_by_vertex=True,
    )
    fig.savefig(MEDIA_DIR / "vertex_coloring.png", bbox_inches="tight", dpi=180)
    plt.close(fig)


def save_ratio_comparison():
    vertices = regular_polygon(3)
    ratios = [0.40, 0.50, 0.58, 0.67]
    point_count = 70_000
    colors = vertex_colors(len(vertices))

    fig, axes = plt.subplots(2, 2, figsize=(8, 8), dpi=170)

    for ax, ratio in zip(axes.ravel(), ratios):
        np.random.seed(100 + int(ratio * 100))
        points, choices = generate_chaos_game(
            vertices,
            ratio=ratio,
            point_count=point_count,
        )
        contraction = 1 - ratio
        ax.scatter(
            points[:, 0],
            points[:, 1],
            s=0.035,
            c=colors[choices],
            alpha=0.82,
            linewidths=0,
        )
        setup_axis(ax, f"r = {ratio:.2f}, c = {contraction:.2f}")

    fig.suptitle("Changing the ratio changes the contraction scale", y=0.98)
    fig.tight_layout()
    fig.savefig(MEDIA_DIR / "ratio_comparison.png", bbox_inches="tight")
    plt.close(fig)


def save_animation():
    np.random.seed(21)
    vertices = regular_polygon(3)
    point_count = 25_000
    points, choices = generate_chaos_game(vertices, ratio=0.5, point_count=point_count)
    colors = vertex_colors(len(vertices))
    frame_counts = np.unique(np.linspace(100, point_count, 45, dtype=int))

    fig, ax = plt.subplots(figsize=(5.5, 5.5), dpi=120)
    setup_axis(ax)
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-0.95, 1.05)

    scatter = ax.scatter([], [], s=0.18, linewidths=0)
    title = ax.set_title("")

    def update(frame_count):
        visible_points = points[:frame_count]
        visible_choices = choices[:frame_count]
        scatter.set_offsets(visible_points)
        scatter.set_color(colors[visible_choices])
        title.set_text(f"{frame_count:,} points")
        return scatter, title

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=frame_counts,
        interval=70,
        blit=False,
    )
    ani.save(MEDIA_DIR / "chaos_game_emergence.gif", writer="pillow", fps=14)
    plt.close(fig)


def main():
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    save_iteration_rule()
    save_progression()
    save_ratio_comparison()
    save_vertex_coloring()
    save_animation()


if __name__ == "__main__":
    main()
