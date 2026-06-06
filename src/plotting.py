import matplotlib.pyplot as plt
import numpy as np


def vertex_colors(vertex_count):
    color_map = plt.get_cmap("tab10" if vertex_count <= 10 else "hsv")
    return color_map(np.linspace(0, 1, vertex_count, endpoint=False))


def draw_fractal(
    points,
    vertex_choices,
    vertices,
    shape_name,
    ratio,
    total_points,
    show_vertices,
    color_by_vertex,
    visible_count=None,
):
    if visible_count is None:
        visible_count = len(points)

    visible_points = points[:visible_count]
    visible_choices = vertex_choices[:visible_count]
    colors = vertex_colors(len(vertices))

    fig, ax = plt.subplots(figsize=(8, 8))

    if color_by_vertex:
        ax.scatter(
            visible_points[:, 0],
            visible_points[:, 1],
            s=0.1,
            c=colors[visible_choices],
        )
    else:
        ax.scatter(visible_points[:, 0], visible_points[:, 1], s=0.1, c="black")

    if show_vertices:
        ax.scatter(
            vertices[:, 0],
            vertices[:, 1],
            s=26,
            facecolors="none",
            edgecolors=colors,
            linewidths=1.2,
            alpha=0.75,
        )
        ax.plot(
            np.append(vertices[:, 0], vertices[0, 0]),
            np.append(vertices[:, 1], vertices[0, 1]),
            color="0.25",
            linewidth=0.8,
            alpha=0.18,
        )

    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        f"{shape_name} - ratio = {ratio:.2f} - {visible_count:,}/{total_points:,} points"
    )

    return fig


def close_figure(fig):
    plt.close(fig)
