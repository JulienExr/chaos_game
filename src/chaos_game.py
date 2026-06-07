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

CONSTRAINTS = [
    "None",
    "No same vertex twice",
    "No neighboring vertex",
    "Only jumps of N",
]


def regular_polygon(side_count, radius=1.0, center=(0, 0)):
    angles = np.linspace(0, 2 * np.pi, side_count, endpoint=False)
    x = center[0] + radius * np.cos(angles)
    y = center[1] + radius * np.sin(angles)
    return np.column_stack((x, y))


def star_polygon(point_count, outer_radius=1.0, inner_radius=0.45, center=(0, 0)):
    angles = np.linspace(0, 2 * np.pi, point_count * 2, endpoint=False)
    radii = np.where(np.arange(point_count * 2) % 2 == 0, outer_radius, inner_radius)
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return np.column_stack((x, y))


def allowed_vertex_indices(previous_index, vertex_count, constraint="None", jump_size=1):
    if previous_index is None or constraint == "None":
        return np.arange(vertex_count)

    indices = np.arange(vertex_count)

    if constraint == "No same vertex twice":
        return indices[indices != previous_index]

    if constraint == "No neighboring vertex":
        left_neighbor = (previous_index - 1) % vertex_count
        right_neighbor = (previous_index + 1) % vertex_count
        return indices[(indices != left_neighbor) & (indices != right_neighbor)]

    if constraint == "Only jumps of N":
        jump_size = int(jump_size) % vertex_count
        return np.unique(
            [
                (previous_index - jump_size) % vertex_count,
                (previous_index + jump_size) % vertex_count,
            ]
        )

    return indices


def generate_chaos_game(
    vertices,
    ratio,
    point_count,
    start_point=None,
    constraint="None",
    jump_size=1,
):
    if start_point is None:
        current = np.mean(vertices, axis=0)
    else:
        current = np.array(start_point, dtype=float)

    points = np.zeros((point_count, 2))
    vertex_choices = np.zeros(point_count, dtype=int)
    previous_index = None
    vertex_count = len(vertices)

    for i in range(point_count):
        if constraint == "None":
            chosen_index = np.random.randint(vertex_count)
        else:
            allowed_indices = allowed_vertex_indices(
                previous_index,
                vertex_count,
                constraint,
                jump_size,
            )
            chosen_index = np.random.choice(allowed_indices)
        chosen_vertex = vertices[chosen_index]
        current = (1 - ratio) * current + ratio * chosen_vertex
        points[i] = current
        vertex_choices[i] = chosen_index
        previous_index = chosen_index

    return points, vertex_choices


def animation_frame_counts(point_count, animation_steps):
    return np.unique(np.linspace(1, point_count, animation_steps, dtype=int))
