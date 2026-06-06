import time

import streamlit as st

from src.chaos_game import (
    SHAPES,
    animation_frame_counts,
    generate_chaos_game,
    regular_polygon,
)
from src.plotting import close_figure, draw_fractal


st.set_page_config(page_title="Chaos Game", layout="wide")

DEFAULTS = {
    "shape": "Triangle",
    "ratio": 0.67,
    "point_count": 50_000,
    "show_vertices": True,
    "color_by_vertex": True,
    "animation_steps": 60,
    "frame_delay": 0.03,
}


def reset_app():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value

    st.session_state.pop("points", None)
    st.session_state.pop("vertex_choices", None)
    st.session_state.pop("last_shape", None)
    st.session_state.pop("last_ratio", None)
    st.session_state.pop("last_point_count", None)


def save_fractal(points, vertex_choices, shape, ratio, point_count):
    st.session_state.points = points
    st.session_state.vertex_choices = vertex_choices
    st.session_state.last_shape = shape
    st.session_state.last_ratio = ratio
    st.session_state.last_point_count = point_count


for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)

st.title("Chaos Game / Polygon Fractals")

with st.sidebar:
    st.header("Controls")
    st.caption("Tune the fractal, then render a static image or play the reveal animation.")

    st.subheader("Geometry")

    shape = st.selectbox("Choose a shape", list(SHAPES.keys()), key="shape")
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
    )
    left_button, right_button = st.columns(2)
    with left_button:
        animate_clicked = st.button("Animate", use_container_width=True)
    with right_button:
        st.button("Reset", on_click=reset_app, use_container_width=True)

    st.caption(
        f"{shape} - {point_count:,} points - ratio {ratio:.2f}"
    )

side_count = SHAPES[shape]
vertices = regular_polygon(side_count)
image = st.empty()

if generate_clicked or animate_clicked:
    points, vertex_choices = generate_chaos_game(vertices, ratio, point_count)
    save_fractal(points, vertex_choices, shape, ratio, point_count)

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
        vertices=regular_polygon(SHAPES[st.session_state.last_shape]),
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
