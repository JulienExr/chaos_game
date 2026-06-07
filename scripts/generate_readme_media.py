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

from src.chaos_game import generate_chaos_game, regular_polygon, star_polygon
from src.plotting import draw_fractal, vertex_colors


def setup_axis(ax, title=None):
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title)


def save_iteration_rule():
    vertices = regular_polygon(3)
    colors = vertex_colors(len(vertices))
    start = np.array([0.0, 0.0])
    chosen_indices = [0, 1]
    ratio = 0.5

    first_vertex = vertices[chosen_indices[0]]
    second_vertex = vertices[chosen_indices[1]]
    first_point = (1 - ratio) * start + ratio * first_vertex
    second_point = (1 - ratio) * first_point + ratio * second_vertex

    fig, ax = plt.subplots(figsize=(7.5, 5.4), dpi=160)
    setup_axis(ax, "Two Chaos Game steps")
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

    path_points = [start, first_point, second_point]
    path_colors = ["#d9480f", "#2f80ed"]
    chosen_vertices = [first_vertex, second_vertex]

    ax.scatter(*start, s=55, color="0.15")
    ax.scatter(*first_point, s=55, color=path_colors[0])
    ax.scatter(*second_point, s=55, color=path_colors[1])

    for source, target, chosen_vertex, color in zip(
        path_points,
        path_points[1:],
        chosen_vertices,
        path_colors,
    ):
        ax.plot(
            [source[0], chosen_vertex[0]],
            [source[1], chosen_vertex[1]],
            color=color,
            linewidth=1.2,
            alpha=0.28,
        )
        ax.annotate(
            "",
            xy=target,
            xytext=source,
            arrowprops={"arrowstyle": "->", "color": color, "lw": 1.8},
        )

    ax.text(start[0] - 0.11, start[1] - 0.12, "$P_0$", fontsize=13)
    ax.text(first_point[0] + 0.04, first_point[1] - 0.08, "$P_1$", fontsize=13)
    ax.text(second_point[0] - 0.13, second_point[1] + 0.04, "$P_2$", fontsize=13)
    ax.text(first_vertex[0] + 0.04, first_vertex[1] + 0.04, "$S_1$", fontsize=13, color=colors[chosen_indices[0]])
    ax.text(second_vertex[0] - 0.20, second_vertex[1] + 0.04, "$S_2$", fontsize=13, color=colors[chosen_indices[1]])
    ax.text(
        -0.95,
        -1.10,
        "$P_{n+1} = (1-r)P_n + rS$",
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


def save_vertex_set_modes():
    examples = [
        ("Regular triangle", regular_polygon(3), 0.50),
        ("Star vertices", star_polygon(5, inner_radius=0.45), 0.75),
        (
            "Manual points",
            np.array(
                [
                    [-0.95, 0.72],
                    [-0.36, -0.90],
                    [0.18, 0.48],
                    [0.92, -0.55],
                    [0.68, 0.86],
                ],
                dtype=float,
            ),
            0.62,
        ),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8), dpi=170)

    for index, (title, vertices, ratio) in enumerate(examples):
        np.random.seed(300 + index)
        points, choices = generate_chaos_game(
            vertices,
            ratio=ratio,
            point_count=80_000,
        )
        colors = vertex_colors(len(vertices))
        ax = axes[index]
        ax.scatter(
            points[:, 0],
            points[:, 1],
            s=0.035,
            c=colors[choices],
            alpha=0.82,
            linewidths=0,
        )
        ax.scatter(
            vertices[:, 0],
            vertices[:, 1],
            s=22,
            facecolors="none",
            edgecolors=colors,
            linewidths=1.0,
            alpha=0.75,
        )
        setup_axis(ax, f"{title}\nr = {ratio:.2f}")

    fig.suptitle("The rule works with any finite set of attractor points", y=1.04)
    fig.tight_layout()
    fig.savefig(MEDIA_DIR / "vertex_set_modes.png", bbox_inches="tight")
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
    save_vertex_set_modes()
    save_vertex_coloring()
    save_animation()


if __name__ == "__main__":
    main()
