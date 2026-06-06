import numpy as np


SHAPES = {
    "Triangle": 3,
    "Square": 4,
    "Pentagon": 5,
    "Hexagon": 6,
    "Heptagon": 7,
    "Octagon": 8,
    "Decagon": 10,
}


def regular_polygon(side_count, radius=1.0, center=(0, 0)):
    angles = np.linspace(0, 2 * np.pi, side_count, endpoint=False)
    x = center[0] + radius * np.cos(angles)
    y = center[1] + radius * np.sin(angles)
    return np.column_stack((x, y))


def generate_chaos_game(vertices, ratio, point_count, start_point=None):
    if start_point is None:
        current = np.mean(vertices, axis=0)
    else:
        current = np.array(start_point, dtype=float)

    points = np.zeros((point_count, 2))
    vertex_choices = np.zeros(point_count, dtype=int)

    for i in range(point_count):
        chosen_index = np.random.randint(len(vertices))
        chosen_vertex = vertices[chosen_index]
        current = (1 - ratio) * current + ratio * chosen_vertex
        points[i] = current
        vertex_choices[i] = chosen_index

    return points, vertex_choices


def animation_frame_counts(point_count, animation_steps):
    return np.unique(np.linspace(1, point_count, animation_steps, dtype=int))
