#!/usr/bin/env python3
"""Generate math exam-style graphs as PNG images.

Produces clean, black-and-white graphs suitable for Korean math exams (수능/모의고사).
Supports 고1~고3 curriculum: polynomials, trig, exp/log, conics, normal dist, etc.

Usage:
    from graph_generator import generate_graph
    png_path = generate_graph(graph_spec, output_path)
"""

import platform
from pathlib import Path

import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Font configuration
# ---------------------------------------------------------------------------
if platform.system() == "Darwin":
    mpl.rcParams["font.family"] = "AppleGothic"
elif platform.system() == "Windows":
    mpl.rcParams["font.family"] = "Malgun Gothic"
else:
    mpl.rcParams["font.family"] = "NanumGothic"

mpl.rcParams["axes.unicode_minus"] = False
mpl.rcParams["mathtext.fontset"] = "cm"  # Computer Modern for math


# ---------------------------------------------------------------------------
# Exam-style axes
# ---------------------------------------------------------------------------


def setup_exam_axes(
    ax, xlim=(-5, 5), ylim=(-5, 5), xlabel="x", ylabel="y", show_origin=True
):
    """Configure axes to look like Korean math exam graphs."""
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    ax.spines["left"].set_position(("data", 0))
    ax.spines["bottom"].set_position(("data", 0))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(1.0)
    ax.spines["bottom"].set_linewidth(1.0)

    # Arrow tips
    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False, markersize=4)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False, markersize=4)

    # Axis labels
    ax.text(
        1.02,
        0,
        xlabel,
        transform=ax.get_yaxis_transform(),
        ha="left",
        va="center",
        fontsize=11,
        fontstyle="italic",
    )
    ax.text(
        0,
        1.02,
        ylabel,
        transform=ax.get_xaxis_transform(),
        ha="center",
        va="bottom",
        fontsize=11,
        fontstyle="italic",
    )

    if show_origin:
        ax.text(
            -0.08,
            -0.06,
            "O",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=10,
        )

    ax.grid(False)
    ax.tick_params(
        axis="both", which="both", direction="in", length=3, width=0.7, labelsize=9
    )

    # Remove 0 from ticks
    ax.set_xticks([t for t in ax.get_xticks() if abs(t) > 0.01])
    ax.set_yticks([t for t in ax.get_yticks() if abs(t) > 0.01])
    return ax


def _new_fig(figsize=(2.8, 2.8), dpi=300):
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    return fig, ax


# ---------------------------------------------------------------------------
# Geometry helper functions
# ---------------------------------------------------------------------------


def _setup_geometry_axes(ax, xlim=None, ylim=None, padding=0.8):
    """Configure axes for geometry diagrams: no ticks, equal aspect, auto margins."""
    ax.set_aspect("equal")
    ax.axis("off")
    if xlim:
        ax.set_xlim(xlim[0] - padding, xlim[1] + padding)
    if ylim:
        ax.set_ylim(ylim[0] - padding, ylim[1] + padding)


def _draw_angle_mark(ax, center, p1, p2, radius=0.4, label=None):
    """Draw an arc mark between two rays from *center* through *p1* and *p2*."""
    c = np.array(center, dtype=float)
    v1 = np.array(p1, dtype=float) - c
    v2 = np.array(p2, dtype=float) - c
    a1 = np.degrees(np.arctan2(v1[1], v1[0]))
    a2 = np.degrees(np.arctan2(v2[1], v2[0]))
    # Ensure we draw the smaller arc (interior angle)
    if (a2 - a1) % 360 > 180:
        a1, a2 = a2, a1
    arc = mpatches.Arc(
        center,
        2 * radius,
        2 * radius,
        angle=0,
        theta1=a1,
        theta2=a2,
        color="k",
        linewidth=0.8,
    )
    ax.add_patch(arc)
    if label:
        mid_angle = np.radians((a1 + a2) / 2)
        lx = c[0] + (radius + 0.25) * np.cos(mid_angle)
        ly = c[1] + (radius + 0.25) * np.sin(mid_angle)
        ax.text(lx, ly, label, fontsize=8, ha="center", va="center")


def _draw_right_angle_mark(ax, corner, p1, p2, size=0.3):
    """Draw a right-angle square symbol at *corner*."""
    c = np.array(corner, dtype=float)
    d1 = np.array(p1, dtype=float) - c
    d2 = np.array(p2, dtype=float) - c
    d1 = d1 / np.linalg.norm(d1) * size
    d2 = d2 / np.linalg.norm(d2) * size
    pts = [c + d1, c + d1 + d2, c + d2]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, "k-", linewidth=0.7)


def _draw_equal_marks(ax, p1, p2, count=1):
    """Draw tick marks on a segment to indicate equal lengths."""
    p1, p2 = np.array(p1, dtype=float), np.array(p2, dtype=float)
    mid = (p1 + p2) / 2
    d = p2 - p1
    length = np.linalg.norm(d)
    if length < 1e-9:
        return
    perp = np.array([-d[1], d[0]]) / length  # perpendicular unit
    tang = d / length
    tick_len = 0.15
    spacing = 0.1
    for i in range(count):
        offset = (i - (count - 1) / 2) * spacing
        cp = mid + tang * offset
        ax.plot(
            [cp[0] - perp[0] * tick_len, cp[0] + perp[0] * tick_len],
            [cp[1] - perp[1] * tick_len, cp[1] + perp[1] * tick_len],
            "k-",
            linewidth=1.0,
        )


def _draw_parallel_marks(ax, p1, p2, count=1):
    """Draw arrow marks on a segment to indicate parallel sides."""
    p1, p2 = np.array(p1, dtype=float), np.array(p2, dtype=float)
    mid = (p1 + p2) / 2
    d = p2 - p1
    length = np.linalg.norm(d)
    if length < 1e-9:
        return
    tang = d / length
    perp = np.array([-d[1], d[0]]) / length
    arrow_len = 0.15
    spacing = 0.12
    for i in range(count):
        offset = (i - (count - 1) / 2) * spacing
        cp = mid + tang * offset
        # Draw a small ">" shape
        tip = cp + tang * arrow_len
        ax.plot(
            [
                cp[0] - tang[0] * arrow_len + perp[0] * arrow_len * 0.5,
                tip[0],
                cp[0] - tang[0] * arrow_len - perp[0] * arrow_len * 0.5,
            ],
            [
                cp[1] - tang[1] * arrow_len + perp[1] * arrow_len * 0.5,
                tip[1],
                cp[1] - tang[1] * arrow_len - perp[1] * arrow_len * 0.5,
            ],
            "k-",
            linewidth=0.8,
        )


def _draw_dashed_line(ax, p1, p2, **kwargs):
    """Draw a dashed auxiliary or hidden line."""
    ax.plot(
        [p1[0], p2[0]],
        [p1[1], p2[1]],
        color=kwargs.get("color", "k"),
        linestyle="--",
        linewidth=kwargs.get("linewidth", 0.7),
    )


def _project_3d(x, y, z, angle_deg=30, scale=0.5):
    """Oblique projection: 3D → 2D for exam-style solid figures."""
    rad = np.radians(angle_deg)
    x2 = x + z * np.cos(rad) * scale
    y2 = y + z * np.sin(rad) * scale
    return x2, y2


# ---------------------------------------------------------------------------
# Geometry shape implementations
# ---------------------------------------------------------------------------


def _plot_triangle(ax, spec):
    """Draw a triangle with labels, angle marks, side marks, auxiliary lines."""
    verts = [np.array(v, dtype=float) for v in spec["vertices"]]
    labels = spec.get("labels", {})
    show_angles = spec.get("show_angles", [False, False, False])
    angle_labels = spec.get("angle_labels", [None, None, None])
    side_labels = spec.get("side_labels", {})
    equal_marks = spec.get("equal_marks", {})

    # Auto bounding box
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    _setup_geometry_axes(
        ax, xlim=(min(xs), max(xs)), ylim=(min(ys), max(ys)), padding=1.0
    )

    # Draw the triangle
    tri = plt.Polygon(verts, fill=False, edgecolor="k", linewidth=1.5)
    ax.add_patch(tri)

    # Vertex labels
    for name, pos in labels.items():
        pos = np.array(pos, dtype=float)
        centroid = sum(verts) / 3
        direction = pos - centroid
        norm = np.linalg.norm(direction)
        if norm > 1e-9:
            direction = direction / norm
        lx = pos[0] + direction[0] * 0.35
        ly = pos[1] + direction[1] * 0.35
        ax.text(lx, ly, name, fontsize=10, ha="center", va="center", fontweight="bold")

    # Angle marks
    for i, show in enumerate(show_angles):
        if not show:
            continue
        c = verts[i]
        p1 = verts[(i + 1) % 3]
        p2 = verts[(i + 2) % 3]
        label = angle_labels[i] if i < len(angle_labels) else None
        if label and label.replace("°", "").strip() == "90":
            _draw_right_angle_mark(ax, c, p1, p2)
        else:
            _draw_angle_mark(ax, c, p1, p2, label=label)

    # Side labels
    name_to_pos = {name: np.array(pos, dtype=float) for name, pos in labels.items()}
    for side_key, text in side_labels.items():
        # side_key like "AB" → look up A and B positions
        if len(side_key) == 2:
            a_name, b_name = side_key[0], side_key[1]
            if a_name in name_to_pos and b_name in name_to_pos:
                pa, pb = name_to_pos[a_name], name_to_pos[b_name]
                mid = (pa + pb) / 2
                d = pb - pa
                perp = np.array([-d[1], d[0]])
                pnorm = np.linalg.norm(perp)
                if pnorm > 1e-9:
                    perp = perp / pnorm
                centroid = sum(verts) / 3
                # Place label on the outside of the triangle
                if np.dot(perp, mid - centroid) < 0:
                    perp = -perp
                ax.text(
                    mid[0] + perp[0] * 0.3,
                    mid[1] + perp[1] * 0.3,
                    text,
                    fontsize=9,
                    ha="center",
                    va="center",
                )

    # Equal marks on sides
    for side_key, count in equal_marks.items():
        if len(side_key) == 2:
            a_name, b_name = side_key[0], side_key[1]
            if a_name in name_to_pos and b_name in name_to_pos:
                _draw_equal_marks(ax, name_to_pos[a_name], name_to_pos[b_name], count)

    # Auxiliary lines
    for aux in spec.get("auxiliary_lines", []):
        aux_type = aux.get("type")
        vtx_name = aux.get("vertex", "")
        if vtx_name not in name_to_pos:
            continue
        vtx = name_to_pos[vtx_name]
        # Find the opposite side
        ordered_names = list(labels.keys())
        idx = ordered_names.index(vtx_name)
        opp_a = name_to_pos[ordered_names[(idx + 1) % 3]]
        opp_b = name_to_pos[ordered_names[(idx + 2) % 3]]

        if aux_type == "median":
            mid_opp = (opp_a + opp_b) / 2
            _draw_dashed_line(ax, vtx, mid_opp)
        elif aux_type == "altitude":
            d = opp_b - opp_a
            t = np.dot(vtx - opp_a, d) / np.dot(d, d)
            foot = opp_a + t * d
            _draw_dashed_line(ax, vtx, foot)
            _draw_right_angle_mark(ax, foot, vtx, opp_b if t < 1 else opp_a)
        elif aux_type == "bisector":
            da = opp_a - vtx
            db = opp_b - vtx
            da_n = da / np.linalg.norm(da)
            db_n = db / np.linalg.norm(db)
            bisect_dir = da_n + db_n
            # Intersect bisector with opposite side
            # Parametric: vtx + s * bisect_dir hits opp_a + t * (opp_b - opp_a)
            denom = bisect_dir[0] * (opp_b[1] - opp_a[1]) - bisect_dir[1] * (
                opp_b[0] - opp_a[0]
            )
            if abs(denom) > 1e-9:
                s = (
                    (opp_a[0] - vtx[0]) * (opp_b[1] - opp_a[1])
                    - (opp_a[1] - vtx[1]) * (opp_b[0] - opp_a[0])
                ) / denom
                target = vtx + s * bisect_dir
                _draw_dashed_line(ax, vtx, target)

    # Circumcircle
    if spec.get("show_circumcircle"):
        A, B, C = verts
        D = 2 * (A[0] * (B[1] - C[1]) + B[0] * (C[1] - A[1]) + C[0] * (A[1] - B[1]))
        if abs(D) > 1e-9:
            ux = (
                (A[0] ** 2 + A[1] ** 2) * (B[1] - C[1])
                + (B[0] ** 2 + B[1] ** 2) * (C[1] - A[1])
                + (C[0] ** 2 + C[1] ** 2) * (A[1] - B[1])
            ) / D
            uy = (
                (A[0] ** 2 + A[1] ** 2) * (C[0] - B[0])
                + (B[0] ** 2 + B[1] ** 2) * (A[0] - C[0])
                + (C[0] ** 2 + C[1] ** 2) * (B[0] - A[0])
            ) / D
            r = np.sqrt((A[0] - ux) ** 2 + (A[1] - uy) ** 2)
            circ = plt.Circle(
                (ux, uy), r, fill=False, edgecolor="gray", linestyle="--", linewidth=0.8
            )
            ax.add_patch(circ)

    # Incircle
    if spec.get("show_incircle"):
        A, B, C = verts
        a_len = np.linalg.norm(B - C)
        b_len = np.linalg.norm(A - C)
        c_len = np.linalg.norm(A - B)
        incenter = (a_len * A + b_len * B + c_len * C) / (a_len + b_len + c_len)
        s = (a_len + b_len + c_len) / 2
        in_r = np.sqrt((s - a_len) * (s - b_len) * (s - c_len) / s)
        circ = plt.Circle(
            incenter, in_r, fill=False, edgecolor="gray", linestyle="--", linewidth=0.8
        )
        ax.add_patch(circ)


def _plot_circle(ax, spec):
    """Draw a circle with points, chords, tangents, arcs, angle indicators."""
    center = np.array(spec.get("center", [0, 0]), dtype=float)
    radius = spec.get("radius", 3)
    show_center = spec.get("show_center", True)

    _setup_geometry_axes(
        ax,
        xlim=(center[0] - radius, center[0] + radius),
        ylim=(center[1] - radius, center[1] + radius),
        padding=1.5,
    )

    # Main circle
    circ = plt.Circle(center, radius, fill=False, edgecolor="k", linewidth=1.5)
    ax.add_patch(circ)

    if show_center:
        ax.plot(*center, "ko", markersize=3)
        ax.text(
            center[0] - 0.3, center[1] - 0.3, "O", fontsize=10, ha="center", va="center"
        )

    # Resolve named points on circle
    point_map = {}
    for pt in spec.get("points_on_circle", []):
        angle_rad = np.radians(pt["angle_deg"])
        pos = center + radius * np.array([np.cos(angle_rad), np.sin(angle_rad)])
        name = pt["label"]
        point_map[name] = pos
        ax.plot(*pos, "ko", markersize=4)
        direction = pos - center
        direction = direction / np.linalg.norm(direction)
        ax.text(
            pos[0] + direction[0] * 0.35,
            pos[1] + direction[1] * 0.35,
            name,
            fontsize=10,
            ha="center",
            va="center",
            fontweight="bold",
        )

    # Chords
    for chord in spec.get("chords", []):
        if len(chord) == 2 and chord[0] in point_map and chord[1] in point_map:
            pa, pb = point_map[chord[0]], point_map[chord[1]]
            ax.plot([pa[0], pb[0]], [pa[1], pb[1]], "k-", linewidth=1.0)

    # Tangent lines at points
    for tname in spec.get("tangent_at", []):
        if tname not in point_map:
            continue
        pt = point_map[tname]
        # Tangent is perpendicular to radius
        radial = pt - center
        tangent_dir = np.array([-radial[1], radial[0]])
        tangent_dir = tangent_dir / np.linalg.norm(tangent_dir)
        t_len = radius * 0.8
        ax.plot(
            [pt[0] - tangent_dir[0] * t_len, pt[0] + tangent_dir[0] * t_len],
            [pt[1] - tangent_dir[1] * t_len, pt[1] + tangent_dir[1] * t_len],
            "k-",
            linewidth=1.0,
        )

    # Arc highlight
    arc_spec = spec.get("arc_highlight")
    if arc_spec:
        fr = arc_spec.get("from", "")
        to = arc_spec.get("to", "")
        if fr in point_map and to in point_map:
            a1 = np.degrees(
                np.arctan2(point_map[fr][1] - center[1], point_map[fr][0] - center[0])
            )
            a2 = np.degrees(
                np.arctan2(point_map[to][1] - center[1], point_map[to][0] - center[0])
            )
            color = arc_spec.get("color", "gray")
            arc = mpatches.Arc(
                center,
                2 * radius,
                2 * radius,
                angle=0,
                theta1=a1,
                theta2=a2,
                color=color,
                linewidth=2.5,
            )
            ax.add_patch(arc)

    # Central angle
    if spec.get("central_angle"):
        pts_on = spec.get("points_on_circle", [])
        if len(pts_on) >= 2:
            a_name = pts_on[0]["label"]
            b_name = pts_on[1]["label"]
            if a_name in point_map and b_name in point_map:
                ax.plot(
                    [center[0], point_map[a_name][0]],
                    [center[1], point_map[a_name][1]],
                    "k-",
                    linewidth=0.8,
                )
                ax.plot(
                    [center[0], point_map[b_name][0]],
                    [center[1], point_map[b_name][1]],
                    "k-",
                    linewidth=0.8,
                )

    # Inscribed angle
    insc = spec.get("inscribed_angle")
    if insc:
        vtx_name = insc.get("vertex", "")
        arc_pts = insc.get("arc", [])
        if vtx_name in point_map and len(arc_pts) == 2:
            vtx = point_map[vtx_name]
            for an in arc_pts:
                if an in point_map:
                    ax.plot(
                        [vtx[0], point_map[an][0]],
                        [vtx[1], point_map[an][1]],
                        "k-",
                        linewidth=0.8,
                    )


def _plot_quadrilateral(ax, spec):
    """Draw a quadrilateral with diagonals, parallel/equal marks, labels."""
    verts = [np.array(v, dtype=float) for v in spec["vertices"]]
    labels = spec.get("labels", {})

    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    _setup_geometry_axes(
        ax, xlim=(min(xs), max(xs)), ylim=(min(ys), max(ys)), padding=1.0
    )

    # Draw quadrilateral
    quad = plt.Polygon(verts, fill=False, edgecolor="k", linewidth=1.5)
    ax.add_patch(quad)

    # Vertex labels
    centroid = sum(verts) / 4
    name_to_pos = {}
    for name, pos in labels.items():
        pos = np.array(pos, dtype=float)
        name_to_pos[name] = pos
        direction = pos - centroid
        norm = np.linalg.norm(direction)
        if norm > 1e-9:
            direction = direction / norm
        lx = pos[0] + direction[0] * 0.35
        ly = pos[1] + direction[1] * 0.35
        ax.text(lx, ly, name, fontsize=10, ha="center", va="center", fontweight="bold")

    # Diagonals
    if spec.get("show_diagonals"):
        _draw_dashed_line(ax, verts[0], verts[2])
        _draw_dashed_line(ax, verts[1], verts[3])
        # Intersection label
        int_label = spec.get("diagonal_intersection_label")
        if int_label:
            # Line verts[0]-verts[2] ∩ verts[1]-verts[3]
            p1, p2 = verts[0], verts[2]
            p3, p4 = verts[1], verts[3]
            d1 = p2 - p1
            d2 = p4 - p3
            denom = d1[0] * d2[1] - d1[1] * d2[0]
            if abs(denom) > 1e-9:
                t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / denom
                inter = p1 + t * d1
                ax.plot(*inter, "ko", markersize=3)
                ax.text(
                    inter[0] + 0.25,
                    inter[1] + 0.25,
                    int_label,
                    fontsize=9,
                    ha="center",
                    va="center",
                )

    # Side labels
    for side_key, text in spec.get("side_labels", {}).items():
        if len(side_key) == 2:
            a_name, b_name = side_key[0], side_key[1]
            if a_name in name_to_pos and b_name in name_to_pos:
                pa, pb = name_to_pos[a_name], name_to_pos[b_name]
                mid = (pa + pb) / 2
                d = pb - pa
                perp = np.array([-d[1], d[0]])
                pnorm = np.linalg.norm(perp)
                if pnorm > 1e-9:
                    perp = perp / pnorm
                if np.dot(perp, mid - centroid) < 0:
                    perp = -perp
                ax.text(
                    mid[0] + perp[0] * 0.3,
                    mid[1] + perp[1] * 0.3,
                    text,
                    fontsize=9,
                    ha="center",
                    va="center",
                )

    # Equal marks
    for side_key, count in spec.get("equal_marks", {}).items():
        if len(side_key) == 2:
            a_name, b_name = side_key[0], side_key[1]
            if a_name in name_to_pos and b_name in name_to_pos:
                _draw_equal_marks(ax, name_to_pos[a_name], name_to_pos[b_name], count)

    # Parallel marks  ("AB_DC": 1 means AB ∥ DC with 1 arrow mark)
    for key, count in spec.get("parallel_marks", {}).items():
        parts = key.split("_")
        if len(parts) == 2 and len(parts[0]) == 2 and len(parts[1]) == 2:
            for side_key in parts:
                a_name, b_name = side_key[0], side_key[1]
                if a_name in name_to_pos and b_name in name_to_pos:
                    _draw_parallel_marks(
                        ax, name_to_pos[a_name], name_to_pos[b_name], count
                    )

    # Right angle marks
    for corner_name in spec.get("show_right_angles", []):
        if corner_name not in name_to_pos:
            continue
        ordered = list(labels.keys())
        idx = ordered.index(corner_name)
        prev_name = ordered[(idx - 1) % len(ordered)]
        next_name = ordered[(idx + 1) % len(ordered)]
        if prev_name in name_to_pos and next_name in name_to_pos:
            _draw_right_angle_mark(
                ax,
                name_to_pos[corner_name],
                name_to_pos[prev_name],
                name_to_pos[next_name],
            )


def _plot_coordinate(ax, spec):
    """Draw shapes on a coordinate plane (axes + segments/polygons/points/lines)."""
    xlim = spec.get("xlim", (-1, 7))
    ylim = spec.get("ylim", (-1, 7))

    setup_exam_axes(ax, xlim=xlim, ylim=ylim)
    ax.set_aspect("equal")

    # Segments
    for seg in spec.get("segments", []):
        if len(seg) == 2:
            p1, p2 = seg
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], "k-", linewidth=1.2)

    # Fill polygon (shaded region)
    fill_poly = spec.get("fill_polygon")
    if fill_poly:
        alpha = spec.get("shade_alpha", 0.15)
        poly = plt.Polygon(
            fill_poly, alpha=alpha, facecolor="gray", edgecolor="k", linewidth=0.8
        )
        ax.add_patch(poly)

    # Points with labels
    for pt in spec.get("points", []):
        pos = pt["pos"]
        ax.plot(pos[0], pos[1], "ko", markersize=4)
        if "label" in pt:
            ax.text(pos[0] + 0.2, pos[1] + 0.3, pt["label"], fontsize=8)

    # Lines (infinite lines given by slope/intercept)
    for ln in spec.get("lines", []):
        slope = ln.get("slope")
        intercept = ln.get("intercept", 0)
        style = ln.get("style", "k-")
        if slope is not None:
            x = np.linspace(xlim[0], xlim[1], 500)
            y = slope * x + intercept
            ax.plot(x, y, style, linewidth=1.0)

    # Circles on coordinate plane
    for c in spec.get("circles", []):
        cc = plt.Circle(
            c["center"], c["radius"], fill=False, edgecolor="k", linewidth=1.2
        )
        ax.add_patch(cc)


def _plot_solid3d(ax, spec):
    """Draw 3D solids using oblique 2D projection (exam-style)."""
    kind = spec.get("kind", "cylinder")
    params = spec.get("params", {})
    solid_labels = spec.get("labels", {})
    show_hidden = spec.get("show_hidden", True)

    ax.set_aspect("equal")
    ax.axis("off")

    if kind == "cylinder":
        r = params.get("radius", 2)
        h = params.get("height", 4)
        # Bottom ellipse
        theta = np.linspace(0, 2 * np.pi, 200)
        bx = r * np.cos(theta)
        by = r * np.sin(theta) * 0.3  # foreshortened
        ax.plot(bx, by, "k-", linewidth=1.2)
        # Top ellipse
        ax.plot(bx, by + h, "k-", linewidth=1.2)
        # Side lines
        ax.plot([-r, -r], [0, h], "k-", linewidth=1.2)
        ax.plot([r, r], [0, h], "k-", linewidth=1.2)
        # Hidden back of bottom ellipse
        if show_hidden:
            bx_back = r * np.cos(np.linspace(0, np.pi, 100))
            by_back = r * np.sin(np.linspace(0, np.pi, 100)) * 0.3
            ax.plot(bx_back, by_back, "k--", linewidth=0.6)
        # Labels
        if "r" in solid_labels:
            ax.annotate(
                "",
                xy=(r, 0),
                xytext=(0, 0),
                arrowprops=dict(arrowstyle="<->", color="k", lw=0.8),
            )
            ax.text(r / 2, -0.5, solid_labels["r"], fontsize=9, ha="center")
        if "h" in solid_labels:
            ax.text(
                r + 0.4, h / 2, solid_labels["h"], fontsize=9, ha="left", va="center"
            )
        _setup_geometry_axes(
            ax, xlim=(-r, r), ylim=(-r * 0.3, h + r * 0.3), padding=1.0
        )

    elif kind == "cone":
        r = params.get("radius", 2)
        h = params.get("height", 4)
        theta = np.linspace(0, 2 * np.pi, 200)
        bx = r * np.cos(theta)
        by = r * np.sin(theta) * 0.3
        ax.plot(bx, by, "k-", linewidth=1.2)
        # Side lines to apex
        ax.plot([-r, 0], [0, h], "k-", linewidth=1.2)
        ax.plot([r, 0], [0, h], "k-", linewidth=1.2)
        if show_hidden:
            bx_back = r * np.cos(np.linspace(0, np.pi, 100))
            by_back = r * np.sin(np.linspace(0, np.pi, 100)) * 0.3
            ax.plot(bx_back, by_back, "k--", linewidth=0.6)
            _draw_dashed_line(ax, [0, 0], [0, h])
        if "r" in solid_labels:
            ax.text(r / 2, -0.5, solid_labels["r"], fontsize=9, ha="center")
        if "h" in solid_labels:
            ax.text(0.3, h / 2, solid_labels["h"], fontsize=9, ha="left", va="center")
        if "l" in solid_labels:
            ax.text(r / 2 + 0.3, h / 2, solid_labels["l"], fontsize=9, ha="left")
        _setup_geometry_axes(
            ax, xlim=(-r, r), ylim=(-r * 0.3, h + r * 0.3), padding=1.0
        )

    elif kind == "sphere":
        r = params.get("radius", 2)
        theta = np.linspace(0, 2 * np.pi, 200)
        ax.plot(r * np.cos(theta), r * np.sin(theta), "k-", linewidth=1.2)
        # Equator ellipse
        ax.plot(r * np.cos(theta), r * np.sin(theta) * 0.3, "k--", linewidth=0.6)
        ax.plot(0, 0, "ko", markersize=3)
        if "r" in solid_labels:
            ax.plot([0, r], [0, 0], "k-", linewidth=0.8)
            ax.text(r / 2, 0.25, solid_labels["r"], fontsize=9, ha="center")
        _setup_geometry_axes(ax, xlim=(-r, r), ylim=(-r, r), padding=0.8)

    elif kind == "rectangular_prism":
        w = params.get("width", 4)
        h = params.get("height", 3)
        d = params.get("depth", 2)
        # Front face
        front = [[0, 0], [w, 0], [w, h], [0, h], [0, 0]]
        fx = [p[0] for p in front]
        fy = [p[1] for p in front]
        ax.plot(fx, fy, "k-", linewidth=1.2)
        # Back face (oblique projected)
        bx0, by0 = _project_3d(0, 0, d)
        bx1, by1 = _project_3d(w, 0, d)
        bx2, by2 = _project_3d(w, h, d)
        bx3, by3 = _project_3d(0, h, d)
        # Visible back edges
        ax.plot([w, bx1], [h, by2], "k-", linewidth=1.2)  # top-right to back
        ax.plot([bx1, bx2], [by1, by2], "k-", linewidth=1.2)  # back right
        ax.plot([bx2, bx3], [by2, by3], "k-", linewidth=1.2)  # back top
        ax.plot([0, bx0], [h, by3], "k-", linewidth=1.2)  # top-left to back
        # Visible connecting edges
        ax.plot([w, bx1], [0, by1], "k-", linewidth=1.2)  # bottom-right to back
        # Hidden edges
        if show_hidden:
            _draw_dashed_line(ax, [0, 0], [bx0, by0])
            _draw_dashed_line(ax, [bx0, by0], [bx1, by1])
            _draw_dashed_line(ax, [bx0, by0], [bx3, by3])
        if "w" in solid_labels:
            ax.text(w / 2, -0.4, solid_labels["w"], fontsize=9, ha="center")
        if "h" in solid_labels:
            ax.text(-0.4, h / 2, solid_labels["h"], fontsize=9, ha="right", va="center")
        if "d" in solid_labels:
            mx, my = _project_3d(w, 0, d / 2)
            ax.text(mx + 0.3, my - 0.2, solid_labels["d"], fontsize=9)
        _setup_geometry_axes(
            ax, xlim=(0, max(w, bx1)), ylim=(0, max(h, by3)), padding=1.0
        )

    elif kind == "triangular_prism":
        # Front triangle
        base = params.get("base", 4)
        h = params.get("height", 3)
        d = params.get("depth", 2)
        ft = [[0, 0], [base, 0], [base / 2, h]]
        for i in range(3):
            j = (i + 1) % 3
            ax.plot([ft[i][0], ft[j][0]], [ft[i][1], ft[j][1]], "k-", linewidth=1.2)
        # Back triangle (projected)
        bt = []
        for p in ft:
            bx, by = _project_3d(p[0], p[1], d)
            bt.append([bx, by])
        # Back edges
        for i in range(3):
            j = (i + 1) % 3
            style = "k--" if show_hidden and i == 0 else "k-"
            lw = 0.6 if show_hidden and i == 0 else 1.2
            ax.plot([bt[i][0], bt[j][0]], [bt[i][1], bt[j][1]], style, linewidth=lw)
        # Connecting edges
        for i in range(3):
            is_hidden = show_hidden and i == 0
            if is_hidden:
                _draw_dashed_line(ax, ft[i], bt[i])
            else:
                ax.plot([ft[i][0], bt[i][0]], [ft[i][1], bt[i][1]], "k-", linewidth=1.2)
        all_x = [p[0] for p in ft + bt]
        all_y = [p[1] for p in ft + bt]
        _setup_geometry_axes(
            ax,
            xlim=(min(all_x), max(all_x)),
            ylim=(min(all_y), max(all_y)),
            padding=1.0,
        )

    elif kind == "pyramid":
        base = params.get("base", 4)
        h = params.get("height", 4)
        d = params.get("depth", 3)
        # Base rectangle (oblique)
        b0 = [0, 0]
        b1 = [base, 0]
        b2x, b2y = _project_3d(base, 0, d)
        b3x, b3y = _project_3d(0, 0, d)
        apex = [base / 2 + d * np.cos(np.radians(30)) * 0.5 / 2, h]
        # Visible base edges
        ax.plot([b0[0], b1[0]], [b0[1], b1[1]], "k-", linewidth=1.2)
        ax.plot([b1[0], b2x], [b1[1], b2y], "k-", linewidth=1.2)
        # Hidden base edges
        if show_hidden:
            _draw_dashed_line(ax, b0, [b3x, b3y])
            _draw_dashed_line(ax, [b3x, b3y], [b2x, b2y])
        else:
            ax.plot([b0[0], b3x], [b0[1], b3y], "k-", linewidth=1.2)
            ax.plot([b3x, b2x], [b3y, b2y], "k-", linewidth=1.2)
        # Side edges to apex
        ax.plot([b0[0], apex[0]], [b0[1], apex[1]], "k-", linewidth=1.2)
        ax.plot([b1[0], apex[0]], [b1[1], apex[1]], "k-", linewidth=1.2)
        ax.plot([b2x, apex[0]], [b2y, apex[1]], "k-", linewidth=1.2)
        if show_hidden:
            _draw_dashed_line(ax, [b3x, b3y], apex)
        else:
            ax.plot([b3x, apex[0]], [b3y, apex[1]], "k-", linewidth=1.2)
        # Height dashed line
        if show_hidden:
            base_center_x = (b0[0] + b1[0] + b2x + b3x) / 4
            base_center_y = (b0[1] + b1[1] + b2y + b3y) / 4
            _draw_dashed_line(ax, [base_center_x, base_center_y], apex)
        if "h" in solid_labels:
            ax.text(apex[0] + 0.3, h / 2, solid_labels["h"], fontsize=9, ha="left")
        all_x = [b0[0], b1[0], b2x, b3x, apex[0]]
        all_y = [b0[1], b1[1], b2y, b3y, apex[1]]
        _setup_geometry_axes(
            ax,
            xlim=(min(all_x), max(all_x)),
            ylim=(min(all_y), max(all_y)),
            padding=1.0,
        )

    else:
        ax.text(
            0.5,
            0.5,
            f"Unknown solid: {kind}",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=10,
        )
        _setup_geometry_axes(ax, xlim=(-1, 1), ylim=(-1, 1))


# ---------------------------------------------------------------------------
# Graph type implementations (functions / analytic)
# ---------------------------------------------------------------------------


def _plot_polynomial(ax, spec):
    """Plot a polynomial function. spec.coeffs = [a_n, ..., a_1, a_0]"""
    coeffs = spec.get("coeffs", [1, 0, 0, -1])  # default: x^3 - 1
    xlim = spec.get("xlim", (-5, 5))
    ylim = spec.get("ylim", (-5, 5))
    label = spec.get("label", "")

    setup_exam_axes(ax, xlim=xlim, ylim=ylim)

    x = np.linspace(xlim[0], xlim[1], 1000)
    y = np.polyval(coeffs, x)
    ax.plot(x, y, "k-", linewidth=1.5)

    if label:
        ax.text(
            0.95,
            0.95,
            f"${label}$",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=10,
        )

    # Mark special points
    for pt in spec.get("points", []):
        px, py = pt["x"], pt["y"]
        ax.plot(px, py, "ko", markersize=4)
        if "label" in pt:
            ax.text(px + 0.2, py + 0.3, pt["label"], fontsize=8)

    # Mark roots on x-axis
    for r in spec.get("roots", []):
        ax.plot(r, 0, "ko", markersize=4)
        ax.text(r, -0.5, str(r), ha="center", fontsize=9)


def _plot_quadratic(ax, spec):
    """Plot quadratic function y = a(x-p)^2 + q."""
    a = spec.get("a", 1)
    p = spec.get("p", 0)
    q = spec.get("q", 0)
    xlim = spec.get("xlim", (-5, 5))
    ylim = spec.get("ylim", (-5, 5))
    label = spec.get("label", "")

    setup_exam_axes(ax, xlim=xlim, ylim=ylim)

    x = np.linspace(xlim[0], xlim[1], 1000)
    y = a * (x - p) ** 2 + q
    ax.plot(x, y, "k-", linewidth=1.5)

    # Mark vertex
    if spec.get("show_vertex", True):
        ax.plot(p, q, "ko", markersize=4)
        ax.text(p + 0.2, q - 0.5, f"$({p},\\;{q})$", fontsize=9)

    # Axis of symmetry
    if spec.get("show_axis", False):
        ax.axvline(p, color="k", linestyle="--", linewidth=0.6)

    if label:
        ax.text(
            0.95,
            0.95,
            f"${label}$",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=10,
        )


def _plot_trig(ax, spec):
    """Plot trigonometric function."""
    func = spec.get("func", "sin")  # sin, cos, tan
    a = spec.get("amplitude", 1)
    b = spec.get("period_coeff", 1)  # period = 2pi/b
    c = spec.get("phase", 0)
    d = spec.get("shift", 0)
    xlim = spec.get("xlim", (-0.5, 2 * np.pi + 0.5))
    ylim = spec.get("ylim", (-2, 2))
    label = spec.get("label", "")

    setup_exam_axes(ax, xlim=xlim, ylim=ylim)

    x = np.linspace(xlim[0], xlim[1], 2000)
    trig_funcs = {"sin": np.sin, "cos": np.cos, "tan": np.tan}
    raw = trig_funcs[func](b * x + c)

    if func == "tan":
        raw[np.abs(raw) > 20] = np.nan
        # Asymptotes
        period = np.pi / abs(b)
        k_start = int(np.floor((xlim[0] + np.pi / (2 * b) - c / b) / period))
        k_end = int(np.ceil((xlim[1] + np.pi / (2 * b) - c / b) / period))
        for k in range(k_start, k_end + 1):
            asym_x = (k * np.pi - c + np.pi / 2) / b
            if xlim[0] < asym_x < xlim[1]:
                ax.axvline(asym_x, color="k", linestyle="--", linewidth=0.6)

    y = a * raw + d
    ax.plot(x, y, "k-", linewidth=1.5)

    # Pi tick labels
    if spec.get("pi_ticks", True) and func != "tan":
        period = 2 * np.pi / abs(b)
        ticks = []
        labels_list = []
        for mult in [0.5, 1, 1.5, 2, 2.5, 3]:
            val = mult * np.pi
            if xlim[0] < val < xlim[1]:
                ticks.append(val)
                if mult == 0.5:
                    labels_list.append(r"$\frac{\pi}{2}$")
                elif mult == 1:
                    labels_list.append(r"$\pi$")
                elif mult == 1.5:
                    labels_list.append(r"$\frac{3\pi}{2}$")
                elif mult == 2:
                    labels_list.append(r"$2\pi$")
                elif mult == 2.5:
                    labels_list.append(r"$\frac{5\pi}{2}$")
                elif mult == 3:
                    labels_list.append(r"$3\pi$")
        if ticks:
            ax.set_xticks(ticks)
            ax.set_xticklabels(labels_list, fontsize=8)

    if label:
        ax.text(
            0.95,
            0.95,
            f"${label}$",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=10,
        )


def _plot_exp_log(ax, spec):
    """Plot exponential and/or logarithmic functions."""
    kind = spec.get("kind", "exp")  # "exp", "log", "both"
    base = spec.get("base", np.e)
    xlim = spec.get("xlim", (-3, 4))
    ylim = spec.get("ylim", (-3, 5))
    label = spec.get("label", "")

    setup_exam_axes(ax, xlim=xlim, ylim=ylim)

    x_exp = np.linspace(xlim[0], min(xlim[1], 5), 500)
    x_log = np.linspace(0.01, xlim[1], 500)

    if kind in ("exp", "both"):
        if base == np.e:
            y_exp = np.exp(x_exp)
        else:
            y_exp = base**x_exp
        ax.plot(x_exp, y_exp, "k-", linewidth=1.5)
        ax.plot(0, 1, "ko", markersize=4)

    if kind in ("log", "both"):
        if base == np.e:
            y_log = np.log(x_log)
        else:
            y_log = np.log(x_log) / np.log(base)
        style = "k--" if kind == "both" else "k-"
        ax.plot(x_log, y_log, style, linewidth=1.5)
        ax.plot(1, 0, "ko", markersize=4)

    if kind == "both":
        # y = x reference line
        x_ref = np.linspace(xlim[0], xlim[1], 100)
        ax.plot(x_ref, x_ref, "k:", linewidth=0.5)

    if label:
        ax.text(
            0.95,
            0.95,
            f"${label}$",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=10,
        )


def _plot_rational(ax, spec):
    """Plot rational function y = (ax+b)/(cx+d) with asymptotes."""
    a = spec.get("a", 1)
    b = spec.get("b", 0)
    c = spec.get("c", 1)
    d = spec.get("d", -1)
    xlim = spec.get("xlim", (-5, 5))
    ylim = spec.get("ylim", (-5, 5))
    label = spec.get("label", "")

    setup_exam_axes(ax, xlim=xlim, ylim=ylim)

    # Vertical asymptote: cx + d = 0 → x = -d/c
    x_asym = -d / c if c != 0 else None
    # Horizontal asymptote: y = a/c
    y_asym = a / c if c != 0 else None

    x = np.linspace(xlim[0], xlim[1], 2000)
    denom = c * x + d
    y = (a * x + b) / denom
    y[np.abs(denom) < 0.05] = np.nan

    ax.plot(x, y, "k-", linewidth=1.5)

    if x_asym is not None and xlim[0] < x_asym < xlim[1]:
        ax.axvline(x_asym, color="k", linestyle="--", linewidth=0.6)
    if y_asym is not None and ylim[0] < y_asym < ylim[1]:
        ax.axhline(y_asym, color="k", linestyle="--", linewidth=0.6)

    if label:
        ax.text(
            0.95,
            0.95,
            f"${label}$",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=10,
        )


def _plot_conic(ax, spec):
    """Plot conic sections (circle, ellipse, hyperbola, parabola)."""
    kind = spec.get("kind", "ellipse")  # circle, ellipse, hyperbola, parabola
    a = spec.get("a", 3)
    b = spec.get("b", 2)
    h = spec.get("h", 0)  # center x
    k = spec.get("k", 0)  # center y
    xlim = spec.get("xlim", (-5, 5))
    ylim = spec.get("ylim", (-5, 5))
    label = spec.get("label", "")

    setup_exam_axes(ax, xlim=xlim, ylim=ylim)
    ax.set_aspect("equal")

    xg = np.linspace(xlim[0], xlim[1], 800)
    yg = np.linspace(ylim[0], ylim[1], 800)
    X, Y = np.meshgrid(xg, yg)

    if kind == "circle":
        Z = (X - h) ** 2 + (Y - k) ** 2
        ax.contour(X, Y, Z, [a**2], colors="k", linewidths=1.5)
    elif kind == "ellipse":
        Z = (X - h) ** 2 / a**2 + (Y - k) ** 2 / b**2
        ax.contour(X, Y, Z, [1], colors="k", linewidths=1.5)
        # Foci
        if a > b:
            c_val = np.sqrt(a**2 - b**2)
            ax.plot([h - c_val, h + c_val], [k, k], "ko", markersize=3)
        else:
            c_val = np.sqrt(b**2 - a**2)
            ax.plot([h, h], [k - c_val, k + c_val], "ko", markersize=3)
    elif kind == "hyperbola":
        Z = (X - h) ** 2 / a**2 - (Y - k) ** 2 / b**2
        ax.contour(X, Y, Z, [1], colors="k", linewidths=1.5)
        # Asymptotes
        x_asym = np.linspace(xlim[0], xlim[1], 100)
        ax.plot(x_asym, k + (b / a) * (x_asym - h), "k--", linewidth=0.6)
        ax.plot(x_asym, k - (b / a) * (x_asym - h), "k--", linewidth=0.6)
    elif kind == "parabola":
        # y^2 = 4px (horizontal) or x^2 = 4py (vertical)
        direction = spec.get("direction", "up")
        p = spec.get("p", 1)  # focal parameter
        if direction in ("up", "down"):
            x_para = np.linspace(xlim[0], xlim[1], 1000)
            sign = 1 if direction == "up" else -1
            y_para = sign * x_para**2 / (4 * p) + k
            ax.plot(x_para, y_para, "k-", linewidth=1.5)
            # Focus
            ax.plot(h, k + sign * p, "ko", markersize=3)
            # Directrix
            ax.axhline(k - sign * p, color="k", linestyle="--", linewidth=0.6)
        else:
            t = np.linspace(
                -np.sqrt(abs(ylim[1] - ylim[0]) * 4 * abs(p)),
                np.sqrt(abs(ylim[1] - ylim[0]) * 4 * abs(p)),
                1000,
            )
            sign = 1 if direction == "right" else -1
            x_para = sign * t**2 / (4 * p) + h
            ax.plot(x_para, t + k, "k-", linewidth=1.5)

    if label:
        ax.text(
            0.95,
            0.95,
            f"${label}$",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=10,
        )

    # Show special points
    for pt in spec.get("points", []):
        ax.plot(pt["x"], pt["y"], "ko", markersize=3)
        if "label" in pt:
            ax.text(pt["x"] + 0.2, pt["y"] + 0.2, pt["label"], fontsize=8)


def _plot_derivative(ax, spec):
    """Plot a function and/or its derivative."""
    coeffs = spec.get("coeffs", [1, 0, -3, 0])  # f(x) = x^3 - 3x
    show_f = spec.get("show_f", True)
    show_fp = spec.get("show_fp", True)
    xlim = spec.get("xlim", (-3, 3))
    ylim = spec.get("ylim", (-5, 5))
    label = spec.get("label", "")

    setup_exam_axes(ax, xlim=xlim, ylim=ylim)

    x = np.linspace(xlim[0], xlim[1], 1000)
    f_poly = np.poly1d(coeffs)
    fp_poly = f_poly.deriv()

    if show_f:
        ax.plot(x, f_poly(x), "k-", linewidth=1.5)
    if show_fp:
        style = "k--" if show_f else "k-"
        ax.plot(x, fp_poly(x), style, linewidth=1.5)

    # Mark extrema
    if spec.get("show_extrema", False) and show_f:
        roots = np.roots(fp_poly.coeffs)
        for r in roots:
            if np.isreal(r) and xlim[0] < r.real < xlim[1]:
                rx = r.real
                ry = f_poly(rx)
                ax.plot(rx, ry, "ko", markersize=4)

    if label:
        ax.text(
            0.95,
            0.95,
            f"${label}$",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=10,
        )


def _plot_integral_area(ax, spec):
    """Plot function with shaded integral area."""
    coeffs = spec.get("coeffs", [1, 0, -1])  # x^2 - 1
    a_val = spec.get("a", 0)
    b_val = spec.get("b", 2)
    xlim = spec.get("xlim", (-2, 3))
    ylim = spec.get("ylim", (-2, 4))
    label = spec.get("label", "")

    setup_exam_axes(ax, xlim=xlim, ylim=ylim)

    x = np.linspace(xlim[0], xlim[1], 1000)
    f_poly = np.poly1d(coeffs)
    y = f_poly(x)
    ax.plot(x, y, "k-", linewidth=1.5)

    # Shaded area
    x_fill = np.linspace(a_val, b_val, 500)
    y_fill = f_poly(x_fill)
    ax.fill_between(
        x_fill, y_fill, 0, alpha=0.25, color="gray", edgecolor="k", linewidth=0.5
    )

    # Boundary dashed lines
    for val in [a_val, b_val]:
        y_at = f_poly(val)
        if abs(y_at) > 0.01:
            ax.plot([val, val], [0, y_at], "k--", linewidth=0.6)

    # Labels on x-axis
    ax.text(a_val, -0.4, f"${a_val}$" if a_val != 0 else "$a$", ha="center", fontsize=9)
    ax.text(b_val, -0.4, f"${b_val}$" if b_val != 0 else "$b$", ha="center", fontsize=9)

    if label:
        ax.text(
            0.95,
            0.95,
            f"${label}$",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=10,
        )


def _plot_normal(ax, spec):
    """Plot normal distribution bell curve."""
    from scipy.stats import norm

    mu = spec.get("mu", 0)
    sigma = spec.get("sigma", 1)
    shade_from = spec.get("shade_from", None)
    shade_to = spec.get("shade_to", None)
    label = spec.get("label", "")

    x = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 1000)
    y = norm.pdf(x, mu, sigma)

    ax.plot(x, y, "k-", linewidth=1.5)

    # Clean axes for bell curve
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_position(("data", 0))
    ax.spines["bottom"].set_linewidth(1.0)
    ax.set_yticks([])

    # Mean and sigma marks
    for k_val, lbl in [(0, f"${mu}$" if mu != 0 else "$m$")]:
        ax.axvline(mu + k_val * sigma, ymax=0.03, color="k", linewidth=0.8)
        ax.text(mu + k_val * sigma, -0.02, lbl, ha="center", va="top", fontsize=9)

    # Shaded region
    if shade_from is not None and shade_to is not None:
        x_fill = np.linspace(shade_from, shade_to, 300)
        ax.fill_between(x_fill, norm.pdf(x_fill, mu, sigma), alpha=0.3, color="gray")

    if label:
        peak = norm.pdf(mu, mu, sigma)
        ax.text(mu, peak + 0.02, f"${label}$", ha="center", fontsize=10)


def _plot_number_line(ax, spec):
    """Plot number line with inequality solutions."""
    intervals = spec.get("intervals", [])  # [{from, to, open_left, open_right}]
    points = spec.get("points", [])
    xlim = spec.get("xlim", (-5, 5))

    ax.set_xlim(xlim)
    ax.set_ylim(-0.5, 0.5)
    ax.axhline(0, color="k", linewidth=1.0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    # Arrow at right end
    ax.annotate(
        "",
        xy=(xlim[1], 0),
        xytext=(xlim[1] - 0.3, 0),
        arrowprops=dict(arrowstyle="->", color="k", lw=1.0),
    )

    # Tick marks
    for tick in range(int(xlim[0]), int(xlim[1]) + 1):
        ax.plot(tick, 0, "|", color="k", markersize=8)
        ax.text(tick, -0.15, str(tick), ha="center", fontsize=8)

    # Intervals
    for iv in intervals:
        fr, to = iv["from"], iv["to"]
        ax.plot([fr, to], [0, 0], "k-", linewidth=3)
        # Open/closed circles
        for val, is_open in [
            (fr, iv.get("open_left", False)),
            (to, iv.get("open_right", False)),
        ]:
            if is_open:
                ax.plot(
                    val,
                    0,
                    "o",
                    markersize=7,
                    markerfacecolor="white",
                    markeredgecolor="k",
                    markeredgewidth=1.5,
                    zorder=5,
                )
            else:
                ax.plot(val, 0, "ko", markersize=5, zorder=5)

    # Individual points
    for pt in points:
        is_open = pt.get("open", False)
        if is_open:
            ax.plot(
                pt["x"],
                0,
                "o",
                markersize=7,
                markerfacecolor="white",
                markeredgecolor="k",
                markeredgewidth=1.5,
                zorder=5,
            )
        else:
            ax.plot(pt["x"], 0, "ko", markersize=5, zorder=5)

    ax.set_yticks([])


def _plot_custom(ax, spec):
    """Plot from custom expressions using eval (for flexibility)."""
    xlim = spec.get("xlim", (-5, 5))
    ylim = spec.get("ylim", (-5, 5))
    label = spec.get("label", "")

    setup_exam_axes(ax, xlim=xlim, ylim=ylim)

    x = np.linspace(xlim[0], xlim[1], 2000)

    for curve in spec.get("curves", []):
        expr = curve["expr"]
        style = curve.get("style", "k-")
        lw = curve.get("linewidth", 1.5)
        # Evaluate expression safely
        y = eval(
            expr,
            {
                "__builtins__": {},
                "np": np,
                "x": x,
                "sin": np.sin,
                "cos": np.cos,
                "tan": np.tan,
                "exp": np.exp,
                "log": np.log,
                "sqrt": np.sqrt,
                "abs": np.abs,
                "pi": np.pi,
                "e": np.e,
            },
        )
        if isinstance(y, (int, float)):
            y = np.full_like(x, y)
        ax.plot(x, y, style, linewidth=lw)
        if "label" in curve:
            ax.text(
                0.95,
                0.95 - 0.08 * spec.get("curves", []).index(curve),
                f"${curve['label']}$",
                transform=ax.transAxes,
                ha="right",
                va="top",
                fontsize=10,
            )

    for pt in spec.get("points", []):
        is_open = pt.get("open", False)
        if is_open:
            ax.plot(
                pt["x"],
                pt["y"],
                "o",
                markersize=6,
                markerfacecolor="white",
                markeredgecolor="k",
                markeredgewidth=1.5,
                zorder=5,
            )
        else:
            ax.plot(pt["x"], pt["y"], "ko", markersize=4, zorder=5)
        if "label" in pt:
            ax.text(pt["x"] + 0.2, pt["y"] + 0.3, pt["label"], fontsize=8)

    # Asymptotes
    for asym in spec.get("asymptotes", []):
        if asym.get("type") == "vertical":
            ax.axvline(asym["value"], color="k", linestyle="--", linewidth=0.6)
        elif asym.get("type") == "horizontal":
            ax.axhline(asym["value"], color="k", linestyle="--", linewidth=0.6)

    # Shaded region
    shade = spec.get("shade")
    if shade:
        x_fill = np.linspace(shade["from"], shade["to"], 500)
        y_upper = eval(
            shade["upper"],
            {
                "__builtins__": {},
                "np": np,
                "x": x_fill,
                "sin": np.sin,
                "cos": np.cos,
                "exp": np.exp,
                "log": np.log,
                "sqrt": np.sqrt,
                "abs": np.abs,
                "pi": np.pi,
                "e": np.e,
            },
        )
        y_lower = shade.get("lower", 0)
        if isinstance(y_lower, str):
            y_lower = eval(
                y_lower,
                {
                    "__builtins__": {},
                    "np": np,
                    "x": x_fill,
                    "sin": np.sin,
                    "cos": np.cos,
                    "exp": np.exp,
                    "log": np.log,
                    "sqrt": np.sqrt,
                    "abs": np.abs,
                    "pi": np.pi,
                    "e": np.e,
                },
            )
        ax.fill_between(x_fill, y_upper, y_lower, alpha=0.25, color="gray")

    if label:
        ax.text(
            0.95,
            0.95,
            f"${label}$",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=10,
        )


# ---------------------------------------------------------------------------
# Graph type dispatcher
# ---------------------------------------------------------------------------

GRAPH_TYPES = {
    "polynomial": _plot_polynomial,
    "quadratic": _plot_quadratic,
    "trig": _plot_trig,
    "exp_log": _plot_exp_log,
    "rational": _plot_rational,
    "conic": _plot_conic,
    "derivative": _plot_derivative,
    "integral_area": _plot_integral_area,
    "normal": _plot_normal,
    "number_line": _plot_number_line,
    "custom": _plot_custom,
    # Geometry shapes
    "triangle": _plot_triangle,
    "circle": _plot_circle,
    "quadrilateral": _plot_quadrilateral,
    "coordinate": _plot_coordinate,
    "solid3d": _plot_solid3d,
}


def generate_graph(spec: dict, output_path: str | Path) -> Path:
    """Generate a graph PNG from specification.

    Args:
        spec: Graph specification dict with "type" key and type-specific params.
              Common keys: xlim, ylim, label, points
        output_path: Where to save the PNG.

    Returns:
        Path to the generated PNG file.
    """
    output_path = Path(output_path)
    graph_type = spec.get("type", "custom")

    if graph_type not in GRAPH_TYPES:
        raise ValueError(
            f"Unknown graph type: {graph_type}. Available: {list(GRAPH_TYPES.keys())}"
        )

    _default_sizes = {
        "number_line": (3.5, 0.6),
        "normal": (3.0, 2.0),
    }
    figsize = spec.get("figsize", _default_sizes.get(graph_type, (2.8, 2.8)))

    fig, ax = _new_fig(figsize=figsize, dpi=300)
    GRAPH_TYPES[graph_type](ax, spec)

    fig.savefig(
        str(output_path),
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.05,
        facecolor="white",
        transparent=False,
    )
    plt.close(fig)
    return output_path


if __name__ == "__main__":
    # Quick test
    import tempfile

    specs = [
        # --- Existing graph types ---
        {
            "type": "quadratic",
            "a": 1,
            "p": 2,
            "q": -3,
            "xlim": (-1, 5),
            "ylim": (-4, 5),
            "label": "y = (x-2)^2 - 3",
        },
        {"type": "trig", "func": "sin", "amplitude": 2, "label": r"y = 2\sin x"},
        {
            "type": "conic",
            "kind": "ellipse",
            "a": 4,
            "b": 2,
            "label": r"\frac{x^2}{16}+\frac{y^2}{4}=1",
        },
        {
            "type": "normal",
            "mu": 0,
            "sigma": 1,
            "shade_from": -1,
            "shade_to": 1,
            "label": "N(0, 1)",
        },
        # --- Geometry shapes ---
        {
            "type": "triangle",
            "vertices": [[0, 0], [6, 0], [2, 5]],
            "labels": {"A": [2, 5], "B": [0, 0], "C": [6, 0]},
            "show_angles": [True, True, True],
            "angle_labels": ["80°", "50°", "50°"],
            "side_labels": {"AB": "5", "BC": "6", "AC": "5"},
            "equal_marks": {"AB": 1, "AC": 1},
        },
        {
            "type": "circle",
            "center": [0, 0],
            "radius": 3,
            "show_center": True,
            "points_on_circle": [
                {"angle_deg": 30, "label": "A"},
                {"angle_deg": 150, "label": "B"},
            ],
            "chords": [["A", "B"]],
            "central_angle": True,
        },
        {
            "type": "quadrilateral",
            "kind": "parallelogram",
            "vertices": [[0, 0], [5, 0], [7, 3], [2, 3]],
            "labels": {"A": [0, 0], "B": [5, 0], "C": [7, 3], "D": [2, 3]},
            "show_diagonals": True,
            "diagonal_intersection_label": "O",
            "parallel_marks": {"AB_DC": 1, "AD_BC": 2},
            "equal_marks": {"AB": 1, "DC": 1},
            "side_labels": {"AB": "10", "BC": "6"},
        },
        {
            "type": "coordinate",
            "xlim": [-1, 7],
            "ylim": [-1, 7],
            "segments": [[[0, 6], [2, 0]], [[2, 0], [6, 0]], [[0, 6], [6, 0]]],
            "points": [
                {"pos": [0, 6], "label": "(0, 6)"},
                {"pos": [2, 0], "label": "(2, 0)"},
                {"pos": [6, 0], "label": "(6, 0)"},
            ],
            "fill_polygon": [[0, 6], [2, 0], [6, 0]],
            "shade_alpha": 0.15,
        },
        {
            "type": "solid3d",
            "kind": "cylinder",
            "params": {"radius": 2, "height": 4},
            "labels": {"r": "2", "h": "4"},
            "show_hidden": True,
        },
        {
            "type": "solid3d",
            "kind": "rectangular_prism",
            "params": {"width": 4, "height": 3, "depth": 2},
            "labels": {"w": "4", "h": "3", "d": "2"},
            "show_hidden": True,
        },
    ]

    for i, s in enumerate(specs):
        out = Path(tempfile.gettempdir()) / f"test_graph_{i}.png"
        generate_graph(s, out)
        print(f"Generated: {out}")
