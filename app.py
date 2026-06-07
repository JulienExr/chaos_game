from copy import deepcopy
import time

import numpy as np
from PIL import Image, ImageDraw
import streamlit as st
try:
    from streamlit_image_coordinates import streamlit_image_coordinates
except ImportError:
    streamlit_image_coordinates = None

from src.chaos_game import (
    SHAPES,
    animation_frame_counts,
    generate_chaos_game,
    regular_polygon,
    star_polygon,
)
from src.plotting import close_figure, draw_fractal


st.set_page_config(page_title="Chaos Game", layout="wide")


VERTEX_SOURCES = [
    "Regular polygon",
    "Star",
    "Manual points",
]

SOURCE_DEFAULT_RATIOS = {
    "Regular polygon": 0.50,
    "Star": 0.75,
    "Manual points": 0.67,
}

CANVAS_SIZE = 540
CANVAS_RANGE = 1.15


def point_to_pixel(point):
    x, y = point
    px = int((x + CANVAS_RANGE) / (2 * CANVAS_RANGE) * (CANVAS_SIZE - 1))
    py = int((CANVAS_RANGE - y) / (2 * CANVAS_RANGE) * (CANVAS_SIZE - 1))
    return px, py


def pixel_to_point(px, py):
    x = (px / (CANVAS_SIZE - 1)) * (2 * CANVAS_RANGE) - CANVAS_RANGE
    y = CANVAS_RANGE - (py / (CANVAS_SIZE - 1)) * (2 * CANVAS_RANGE)
    return [float(x), float(y)]


def draw_manual_canvas(vertices):
    image = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), "#fbfaf7")
    draw = ImageDraw.Draw(image)

    grid_color = "#e8e2d8"
    axis_color = "#c8beb0"
    border_color = "#9f9588"

    for i in range(9):
        offset = int(i * (CANVAS_SIZE - 1) / 8)
        draw.line([(offset, 0), (offset, CANVAS_SIZE)], fill=grid_color, width=1)
        draw.line([(0, offset), (CANVAS_SIZE, offset)], fill=grid_color, width=1)

    center = CANVAS_SIZE // 2
    draw.line([(center, 0), (center, CANVAS_SIZE)], fill=axis_color, width=1)
    draw.line([(0, center), (CANVAS_SIZE, center)], fill=axis_color, width=1)
    draw.rectangle([(0, 0), (CANVAS_SIZE - 1, CANVAS_SIZE - 1)], outline=border_color, width=2)

    if len(vertices) > 1:
        pixels = [point_to_pixel(vertex) for vertex in vertices]
        draw.line(pixels, fill="#667085", width=2)

    for index, vertex in enumerate(vertices, start=1):
        x, y = point_to_pixel(vertex)
        radius = 8
        draw.ellipse(
            [(x - radius, y - radius), (x + radius, y + radius)],
            fill="#2f80ed",
            outline="#173b6d",
            width=2,
        )
        draw.text((x + 10, y - 10), str(index), fill="#173b6d")

    return image


DEFAULTS = {
    "vertex_source": "Regular polygon",
    "regular_shape": "Triangle",
    "star_points": 5,
    "star_inner_radius": 0.45,
    "manual_points": [],
    "ratio": 0.50,
    "point_count": 150_000,
    "show_vertices": True,
    "color_by_vertex": True,
    "animation_steps": 60,
    "frame_delay": 0.03,
}


def reset_app():
    for key, value in DEFAULTS.items():
        st.session_state[key] = deepcopy(value)

    st.session_state.pop("points", None)
    st.session_state.pop("vertex_choices", None)
    st.session_state.pop("last_vertices", None)
    st.session_state.pop("last_shape", None)
    st.session_state.pop("last_ratio", None)
    st.session_state.pop("last_point_count", None)
    st.session_state.pop("last_manual_click", None)


def apply_vertex_source_defaults():
    st.session_state.ratio = SOURCE_DEFAULT_RATIOS[st.session_state.vertex_source]


def save_fractal(points, vertex_choices, vertices, shape, ratio, point_count):
    st.session_state.points = points
    st.session_state.vertex_choices = vertex_choices
    st.session_state.last_vertices = np.array(vertices, copy=True)
    st.session_state.last_shape = shape
    st.session_state.last_ratio = ratio
    st.session_state.last_point_count = point_count


def rows_to_vertices(rows):
    if hasattr(rows, "to_dict"):
        rows = rows.to_dict("records")

    vertices = []
    for row in rows:
        try:
            vertices.append([float(row["x"]), float(row["y"])])
        except (KeyError, TypeError, ValueError):
            continue

    return np.array(vertices, dtype=float)


def current_manual_vertices():
    return rows_to_vertices(st.session_state.manual_points)


for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = deepcopy(value)

if st.session_state.vertex_source not in VERTEX_SOURCES:
    st.session_state.vertex_source = DEFAULTS["vertex_source"]

st.title("Chaos Game / Polygon Fractals")

with st.sidebar:
    st.header("Controls")
    st.caption("Tune the fractal, then render a static image or play the reveal animation.")

    st.subheader("Geometry")

    vertex_source = st.radio(
        "Vertex source",
        VERTEX_SOURCES,
        key="vertex_source",
        on_change=apply_vertex_source_defaults,
    )

    if vertex_source == "Regular polygon":
        regular_shape = st.selectbox("Shape", list(SHAPES.keys()), key="regular_shape")
        shape = regular_shape
        vertices = regular_polygon(SHAPES[regular_shape])
    elif vertex_source == "Star":
        star_points = st.slider("Tips", min_value=3, max_value=12, key="star_points")
        star_inner_radius = st.slider(
            "Inner radius",
            min_value=0.10,
            max_value=0.90,
            step=0.05,
            key="star_inner_radius",
        )
        shape = f"{star_points}-point star"
        vertices = star_polygon(star_points, inner_radius=star_inner_radius)
    else:
        st.caption("Click on the placement canvas to add attractor points.")
        shape = "Manual points"
        vertices = current_manual_vertices()
        undo_clicked = st.button("Undo last point", use_container_width=True)
        clear_clicked = st.button("Clear points", use_container_width=True)

        if undo_clicked and st.session_state.manual_points:
            st.session_state.manual_points = st.session_state.manual_points[:-1]
            st.session_state.pop("last_manual_click", None)
            vertices = current_manual_vertices()

        if clear_clicked:
            st.session_state.manual_points = []
            st.session_state.pop("last_manual_click", None)
            vertices = current_manual_vertices()

    has_enough_vertices = len(vertices) >= 2
    if not has_enough_vertices:
        st.warning("Add at least two valid points.")

    ratio = st.slider(
        "Ratio",
        min_value=0.01,
        max_value=0.99,
        step=0.01,
        help="How far each new point moves toward the selected vertex.",
        key="ratio",
    )
    point_count = st.slider(
        "Point count",
        min_value=1_000,
        max_value=200_000,
        step=1_000,
        help="Higher values create a denser fractal but take longer to render.",
        key="point_count",
    )

    st.subheader("Display")
    color_by_vertex = st.checkbox(
        "Color points by selected vertex",
        key="color_by_vertex",
    )
    show_vertices = st.checkbox("Show vertex guides", key="show_vertices")

    with st.expander("Animation", expanded=False):
        st.caption("These settings only affect the Animate button.")
        animation_steps = st.slider(
            "Frames",
            min_value=10,
            max_value=200,
            step=10,
            key="animation_steps",
        )
        frame_delay = st.slider(
            "Frame delay (seconds)",
            min_value=0.00,
            max_value=0.20,
            step=0.01,
            key="frame_delay",
        )

    st.divider()

    generate_clicked = st.button(
        "Generate",
        type="primary",
        use_container_width=True,
        disabled=not has_enough_vertices,
    )
    left_button, right_button = st.columns(2)
    with left_button:
        animate_clicked = st.button(
            "Animate",
            use_container_width=True,
            disabled=not has_enough_vertices,
        )
    with right_button:
        st.button("Reset", on_click=reset_app, use_container_width=True)

    st.caption(
        f"{shape} - {len(vertices)} vertices - {point_count:,} points - ratio {ratio:.2f}"
    )

if vertex_source == "Manual points":
    st.subheader("Manual vertex placement")

    if streamlit_image_coordinates is None:
        st.error(
            "Install dependencies with `pip install -r requirements.txt` to enable click placement."
        )
    else:
        clicked = streamlit_image_coordinates(
            draw_manual_canvas(vertices),
            key="manual_canvas",
            width=CANVAS_SIZE,
        )

        if clicked and "x" in clicked and "y" in clicked:
            click_key = (clicked["x"], clicked["y"])
            if click_key != st.session_state.get("last_manual_click"):
                point = pixel_to_point(clicked["x"], clicked["y"])
                manual_points = st.session_state.manual_points
                if hasattr(manual_points, "to_dict"):
                    manual_points = manual_points.to_dict("records")

                st.session_state.manual_points = [
                    *manual_points,
                    {"x": point[0], "y": point[1]},
                ]
                st.session_state.last_manual_click = click_key
                st.rerun()

image = st.empty()

if generate_clicked or animate_clicked:
    points, vertex_choices = generate_chaos_game(vertices, ratio, point_count)
    save_fractal(points, vertex_choices, vertices, shape, ratio, point_count)

    if animate_clicked:
        progress = st.progress(0)
        frame_counts = animation_frame_counts(point_count, animation_steps)

        for frame_index, visible_count in enumerate(frame_counts, start=1):
            fig = draw_fractal(
                points=points,
                vertex_choices=vertex_choices,
                vertices=vertices,
                shape_name=shape,
                ratio=ratio,
                total_points=point_count,
                show_vertices=show_vertices,
                color_by_vertex=color_by_vertex,
                visible_count=visible_count,
            )
            image.pyplot(fig)
            close_figure(fig)
            progress.progress(frame_index / len(frame_counts))
            time.sleep(frame_delay)
    else:
        fig = draw_fractal(
            points=points,
            vertex_choices=vertex_choices,
            vertices=vertices,
            shape_name=shape,
            ratio=ratio,
            total_points=point_count,
            show_vertices=show_vertices,
            color_by_vertex=color_by_vertex,
        )
        image.pyplot(fig)
        close_figure(fig)
elif "points" in st.session_state and "vertex_choices" in st.session_state:
    fig = draw_fractal(
        points=st.session_state.points,
        vertex_choices=st.session_state.vertex_choices,
        vertices=st.session_state.last_vertices,
        shape_name=st.session_state.last_shape,
        ratio=st.session_state.last_ratio,
        total_points=st.session_state.last_point_count,
        show_vertices=show_vertices,
        color_by_vertex=color_by_vertex,
    )
    image.pyplot(fig)
    close_figure(fig)
else:
    st.info("Choose parameters in the sidebar, then generate or animate the fractal.")
