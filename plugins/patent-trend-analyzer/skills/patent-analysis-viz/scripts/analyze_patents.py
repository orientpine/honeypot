#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standard Patent Analysis & Visualization Script
================================================
Config-driven patent classification, trend analysis, and dashboard generation.
Produces a fixed set of outputs regardless of research topic.

Usage:
    python analyze_patents.py --config classification_config.json
    python analyze_patents.py --config config.json --input data.xlsx --output-dir output/

Mandatory outputs (11 files):
    output/patent_analysis_report.xlsx
    output/patent_classification_summary.md
    output/visualizations/axis1_distribution.png
    output/visualizations/axis2_distribution.png
    output/visualizations/cross_tabulation_heatmap.png
    output/visualizations/yearly_trend.png
    output/visualizations/white_space_analysis.png
    output/visualizations/top_institutions.png
    output/visualizations/institution_by_category.png
    output/visualizations/combined_dashboard.png
    output/visualizations/patent_dashboard.html
"""

import argparse
import json
import os
import re
import importlib

import numpy as np
import pandas as pd

matplotlib = importlib.import_module("matplotlib")
matplotlib.use("Agg")
plt = importlib.import_module("matplotlib.pyplot")
fm_mod = importlib.import_module("matplotlib.font_manager")
go = importlib.import_module("plotly.graph_objects")
sns = importlib.import_module("seaborn")
get_plotlyjs = importlib.import_module("plotly.offline").get_plotlyjs

try:
    from html import escape
except ImportError:
    from cgi import escape


# ── 0. Korean Font Setup ─────────────────────────────────────────────────────


def setup_korean_font():
    candidates = ["NanumGothic", "NanumSquare", "Noto Sans CJK KR", "NanumMyeongjo"]
    for fc in candidates:
        if any(fc in f.name for f in fm_mod.fontManager.ttflist):
            plt.rcParams["font.family"] = fc
            plt.rcParams["axes.unicode_minus"] = False
            return fc
    nanum_paths = [
        p for p in fm_mod.findSystemFonts() if "NanumGothic" in p and "Coding" not in p
    ]
    if nanum_paths:
        fe = fm_mod.FontEntry(nanum_paths[0], "NanumGothic")
        fm_mod.fontManager.ttflist.insert(0, fe)
        plt.rcParams["font.family"] = "NanumGothic"
        plt.rcParams["axes.unicode_minus"] = False
        return "NanumGothic"
    plt.rcParams["axes.unicode_minus"] = False
    return None


FONT_NAME = setup_korean_font()
sns.set_theme(style="whitegrid", font=FONT_NAME or "sans-serif")


# ── 1. Config Loading ────────────────────────────────────────────────────────


def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    required_keys = ["metadata", "classification"]
    for k in required_keys:
        if k not in cfg:
            raise ValueError(f"Config missing required key: {k}")

    cls = cfg["classification"]
    for axis in ["axis1", "axis2"]:
        if axis not in cls:
            raise ValueError(f"Config missing classification.{axis}")
        ax = cls[axis]
        for field in ["name", "order", "colors"]:
            if field not in ax:
                raise ValueError(f"Config missing classification.{axis}.{field}")
        if "other_label" not in ax:
            ax["other_label"] = "기타"
        if "ipc_map" not in ax:
            ax["ipc_map"] = {}
        if "keywords" not in ax:
            ax["keywords"] = {}

    if "year_range" not in cfg:
        cfg["year_range"] = [2020, 2027]
    if "input" not in cfg:
        cfg["input"] = {"file": "output/deduplicated_patents.xlsx"}
    if "output" not in cfg:
        cfg["output"] = {"dir": "output", "viz_dir": "output/visualizations"}

    return cfg


# ── 2. Classification Functions ──────────────────────────────────────────────


def normalize_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def parse_ipcs(ipc_text):
    text = normalize_text(ipc_text).upper()
    if not text:
        return []
    return [x.strip() for x in re.split(r"[|,;/]+", text) if x.strip()]


def match_by_ipc(ipc_list, ipc_map):
    for category, prefixes in ipc_map.items():
        for ipc in ipc_list:
            for pref in prefixes:
                if ipc.startswith(pref.upper()):
                    return category
    return None


def match_by_keywords(text, kw_map):
    scores = {}
    for category, kws in kw_map.items():
        score = sum(1 for kw in kws if kw.lower() in text)
        if score > 0:
            scores[category] = score
    if not scores:
        return None
    return sorted(scores.items(), key=lambda x: (-x[1], x[0]))[0][0]


def classify_axis(ipc_text, combined_text, ipc_map, keywords, other_label="기타"):
    ipcs = parse_ipcs(ipc_text)
    by_ipc = match_by_ipc(ipcs, ipc_map)
    if by_ipc:
        return by_ipc
    by_kw = match_by_keywords(combined_text, keywords)
    if by_kw:
        return by_kw
    return other_label


# ── 3. Utility Functions ─────────────────────────────────────────────────────


def pct(v, total):
    if total == 0:
        return 0.0
    return round(100.0 * v / total, 2)


def markdown_table(df):
    headers = list(df.columns)
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(x) for x in row.tolist()) + " |")
    return "\n".join(lines)


# ── 4. Chart Functions ───────────────────────────────────────────────────────


def draw_axis1_pie(axis1_counts, colors, axis1_name, viz_dir):
    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)
    labels = axis1_counts.index.tolist()
    values = axis1_counts.values.tolist()
    clrs = [colors.get(l, "#95A5A6") for l in labels]
    ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=120,
        colors=clrs,
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
        textprops={"fontsize": 10},
    )
    ax.set_title(f"{axis1_name} 분포", fontsize=14, fontweight="bold")
    plt.tight_layout()
    fig.savefig(os.path.join(viz_dir, "axis1_distribution.png"), dpi=150)
    plt.close(fig)


def draw_axis2_bar(axis2_counts, colors, axis2_name, viz_dir):
    fig, ax = plt.subplots(figsize=(11, 7), dpi=150)
    ordered = axis2_counts.sort_values(ascending=True)
    y = ordered.index.tolist()
    x = ordered.values.tolist()
    clrs = [colors.get(k, "#95A5A6") for k in y]
    ax.barh(y, x, color=clrs)
    for idx, val in enumerate(x):
        ax.text(val + 0.5, idx, str(val), va="center", fontsize=9)
    ax.set_title(f"{axis2_name} 분포", fontsize=14, fontweight="bold")
    ax.set_xlabel("특허 건수")
    ax.set_ylabel(axis2_name)
    plt.tight_layout()
    fig.savefig(os.path.join(viz_dir, "axis2_distribution.png"), dpi=150)
    plt.close(fig)


def draw_cross_heatmap(cross_tab, axis1_name, axis2_name, viz_dir):
    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    sns.heatmap(
        cross_tab,
        annot=True,
        fmt="d",
        cmap="YlOrRd",
        linewidths=0.5,
        cbar_kws={"label": "특허 건수"},
        ax=ax,
    )
    ax.set_title(
        f"{axis1_name} × {axis2_name} 교차분석", fontsize=14, fontweight="bold"
    )
    ax.set_xlabel(axis2_name)
    ax.set_ylabel(axis1_name)
    plt.tight_layout()
    fig.savefig(os.path.join(viz_dir, "cross_tabulation_heatmap.png"), dpi=150)
    plt.close(fig)


def draw_yearly_trend(yearly_axis1, axis1_colors, axis1_order, viz_dir):
    fig, ax = plt.subplots(figsize=(13, 7), dpi=150)
    for col in yearly_axis1.columns:
        ax.plot(
            yearly_axis1.index,
            yearly_axis1[col],
            marker="o",
            linewidth=2,
            label=col,
            color=axis1_colors.get(col, "#7F8C8D"),
        )
    years = yearly_axis1.index.tolist()
    ax.set_title(
        f"연도별 기술 유형 출원 추이 ({min(years)}-{max(years)})",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlabel("출원연도")
    ax.set_ylabel("특허 건수")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=True)
    ax.set_xticks(years)
    plt.tight_layout()
    fig.savefig(os.path.join(viz_dir, "yearly_trend.png"), dpi=150)
    plt.close(fig)


def draw_white_space(cross_tab, white_space_threshold, axis1_name, axis2_name, viz_dir):
    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    ws = cross_tab.copy()
    mask_low = ws <= white_space_threshold
    cmap = sns.color_palette("RdYlGn_r", as_cmap=True)
    sns.heatmap(
        ws,
        annot=True,
        fmt="d",
        cmap=cmap,
        linewidths=0.5,
        cbar_kws={"label": "특허 밀도(낮을수록 기회영역)"},
        ax=ax,
    )
    for i in range(ws.shape[0]):
        for j in range(ws.shape[1]):
            if mask_low.iloc[i, j]:
                ax.text(
                    j + 0.5,
                    i + 0.5,
                    f"{ws.iloc[i, j]}\n★",
                    ha="center",
                    va="center",
                    color="black",
                    fontsize=9,
                )
    ax.set_title(
        f"화이트스페이스 분석 (임계치: {white_space_threshold}건 이하)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlabel(axis2_name)
    ax.set_ylabel(axis1_name)
    plt.tight_layout()
    fig.savefig(os.path.join(viz_dir, "white_space_analysis.png"), dpi=150)
    plt.close(fig)


def draw_top_institutions(df, axis1_colors, axis1_order, viz_dir):
    applicant_col = "applicantName"
    top20 = df[applicant_col].fillna("미상").value_counts().head(20).index.tolist()
    subset = df[df[applicant_col].fillna("미상").isin(top20)].copy()
    pivot = pd.crosstab(
        subset[applicant_col].fillna("미상"), subset["axis1_category"]
    ).reindex(top20)

    fig, ax = plt.subplots(figsize=(14, 10), dpi=150)
    bottom = np.zeros(len(pivot))
    x = np.arange(len(pivot))
    for col in axis1_order:
        vals = pivot[col].values if col in pivot.columns else np.zeros(len(pivot))
        ax.bar(
            x, vals, bottom=bottom, label=col, color=axis1_colors.get(col, "#95A5A6")
        )
        bottom = bottom + np.asarray(vals, dtype=float)

    ax.set_title("상위 20개 출원인 기술유형 누적 분포", fontsize=14, fontweight="bold")
    ax.set_xlabel("출원인")
    ax.set_ylabel("특허 건수")
    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index.tolist(), rotation=70, ha="right", fontsize=8)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=8)
    plt.tight_layout()
    fig.savefig(os.path.join(viz_dir, "top_institutions.png"), dpi=150)
    plt.close(fig)

    return pivot


def draw_institution_by_category(top20_pivot, axis1_colors, axis1_order, viz_dir):
    top10 = top20_pivot.sum(axis=1).sort_values(ascending=False).head(10).index.tolist()
    top_categories = [c for c in axis1_order if c in top20_pivot.columns][:4]
    if not top_categories or not top10:
        fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
        ax.text(0.5, 0.5, "데이터 부족", ha="center", va="center")
        ax.set_title("주요 출원인별 핵심 기술유형 비교", fontsize=14, fontweight="bold")
        plt.tight_layout()
        fig.savefig(os.path.join(viz_dir, "institution_by_category.png"), dpi=150)
        plt.close(fig)
        return

    data = top20_pivot.loc[top10, top_categories]
    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
    x = np.arange(len(data.index))
    width = 0.18
    for i, cat in enumerate(top_categories):
        ax.bar(
            x + (i - (len(top_categories) - 1) / 2) * width,
            data[cat].values,
            width=width,
            label=cat,
            color=axis1_colors.get(cat, "#95A5A6"),
        )

    ax.set_title("주요 출원인별 핵심 기술유형 비교", fontsize=14, fontweight="bold")
    ax.set_xlabel("출원인")
    ax.set_ylabel("특허 건수")
    ax.set_xticks(x)
    ax.set_xticklabels(data.index.tolist(), rotation=55, ha="right", fontsize=9)
    ax.legend()
    plt.tight_layout()
    fig.savefig(os.path.join(viz_dir, "institution_by_category.png"), dpi=150)
    plt.close(fig)


def draw_combined_dashboard(
    axis1_counts,
    axis2_counts,
    cross_tab,
    yearly_axis1,
    top20_pivot,
    axis1_colors,
    axis2_colors,
    axis1_order,
    dashboard_title,
    viz_dir,
):
    fig, axes = plt.subplots(3, 3, figsize=(20, 16), dpi=150)

    # [0,0] Axis1 pie
    ax = axes[0, 0]
    labels = axis1_counts.index.tolist()
    vals = axis1_counts.values.tolist()
    ax.pie(
        vals,
        labels=labels,
        autopct="%1.1f%%",
        startangle=120,
        colors=[axis1_colors.get(l, "#95A5A6") for l in labels],
        textprops={"fontsize": 8},
    )
    ax.set_title("기술유형 분포")

    # [0,1] Axis2 bar
    ax = axes[0, 1]
    ordered = axis2_counts.sort_values(ascending=True)
    ax.barh(
        ordered.index.tolist(),
        ordered.values.tolist(),
        color=[axis2_colors.get(k, "#95A5A6") for k in ordered.index],
    )
    ax.set_title("적용분야 분포")

    # [0,2] Cross heatmap mini
    ax = axes[0, 2]
    sns.heatmap(cross_tab, annot=False, cmap="YlOrRd", cbar=False, ax=ax)
    ax.set_title("교차 히트맵")

    # [1,0] Yearly trend
    ax = axes[1, 0]
    for col in yearly_axis1.columns:
        ax.plot(
            yearly_axis1.index,
            yearly_axis1[col],
            marker="o",
            linewidth=1.5,
            label=col,
            color=axis1_colors.get(col, "#888888"),
        )
    ax.set_title("연도별 추이")
    ax.set_xticks(yearly_axis1.index.tolist())

    # [1,1] White space mini
    ax = axes[1, 1]
    ws_threshold = max(1, int(np.floor(cross_tab.values.flatten().mean() * 0.5)))
    sns.heatmap(cross_tab, annot=False, cmap="RdYlGn_r", cbar=False, ax=ax)
    ax.set_title(f"화이트스페이스(<= {ws_threshold})")

    # [1,2] Top institutions
    ax = axes[1, 2]
    top10 = top20_pivot.sum(axis=1).sort_values(ascending=False).head(10)
    ax.barh(top10.index[::-1], top10.values[::-1], color="#546E7A")
    ax.set_title("상위 출원인 Top10")

    # [2,0] Institution by category
    ax = axes[2, 0]
    top_categories = [c for c in axis1_order if c in top20_pivot.columns][:4]
    if top_categories and len(top10) > 0:
        d = top20_pivot.loc[top10.index, top_categories]
        x_pos = np.arange(len(d.index))
        w = 0.2
        for i, c in enumerate(top_categories):
            ax.bar(
                x_pos + (i - 1.5) * w,
                d[c].values,
                width=w,
                label=c,
                color=axis1_colors.get(c, "#888888"),
            )
        ax.set_xticks(x_pos)
        ax.set_xticklabels(d.index.tolist(), rotation=55, ha="right", fontsize=7)
    ax.set_title("기관별 기술유형")

    # [2,1] Total by axis1
    ax = axes[2, 1]
    totals = cross_tab.sum(axis=1)
    ax.bar(
        totals.index,
        totals.values,
        color=[axis1_colors.get(k, "#95A5A6") for k in totals.index],
    )
    ax.set_title("기술유형 총량")
    ax.tick_params(axis="x", rotation=45)

    # [2,2] Summary text
    ax = axes[2, 2]
    ax.axis("off")
    total = int(axis1_counts.sum())
    top_axis1 = axis1_counts.idxmax()
    top_axis2 = axis2_counts.idxmax()
    top_inst = top20_pivot.sum(axis=1).idxmax() if len(top20_pivot) > 0 else "N/A"
    text = (
        "요약 지표\n\n"
        f"총 특허: {total}건\n"
        f"최다 기술유형: {top_axis1} ({axis1_counts.max()}건)\n"
        f"최다 적용분야: {top_axis2} ({axis2_counts.max()}건)\n"
        f"최다 출원인: {top_inst}\n"
    )
    ax.text(0.02, 0.98, text, va="top", fontsize=13)

    fig.suptitle(dashboard_title, fontsize=18, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(viz_dir, "combined_dashboard.png"), dpi=150)
    plt.close(fig)


# ── 5. Interactive HTML Dashboard ─────────────────────────────────────────────


def build_plotly_dashboard(
    df,
    axis1_counts,
    axis2_counts,
    cross_tab,
    yearly_axis1,
    white_space_df,
    axis1_colors,
    axis2_colors,
    axis1_order,
    axis2_order,
    dashboard_title,
    metadata,
    viz_dir,
):
    # Pie chart — Axis 1
    pie_fig = go.Figure(
        data=[
            go.Pie(
                labels=axis1_counts.index,
                values=axis1_counts.values,
                hole=0.35,
                marker={
                    "colors": [
                        axis1_colors.get(k, "#95A5A6") for k in axis1_counts.index
                    ]
                },
                textinfo="label+percent",
            )
        ]
    )
    pie_fig.update_layout(
        title=f"{metadata.get('axis1_name', '기술 유형')} 분포",
        font={"family": FONT_NAME or "sans-serif"},
    )

    # Bar chart — Axis 2
    bar_fig = go.Figure(
        data=[
            go.Bar(
                x=axis2_counts.values,
                y=axis2_counts.index,
                orientation="h",
                marker_color=[
                    axis2_colors.get(k, "#95A5A6") for k in axis2_counts.index
                ],
            )
        ]
    )
    bar_fig.update_layout(
        title=f"{metadata.get('axis2_name', '적용 분야')} 분포",
        yaxis={"categoryorder": "total ascending"},
        font={"family": FONT_NAME or "sans-serif"},
    )

    # Heatmap — Cross tab
    heatmap_fig = go.Figure(
        data=[
            go.Heatmap(
                z=cross_tab.values,
                x=cross_tab.columns.tolist(),
                y=cross_tab.index.tolist(),
                colorscale="YlOrRd",
                colorbar={"title": "건수"},
            )
        ]
    )
    heatmap_fig.update_layout(
        title=f"{metadata.get('axis1_name', '기술 유형')} × {metadata.get('axis2_name', '적용 분야')}",
        font={"family": FONT_NAME or "sans-serif"},
    )

    # Trend lines
    trend_fig = go.Figure()
    for col in yearly_axis1.columns:
        trend_fig.add_trace(
            go.Scatter(
                x=yearly_axis1.index,
                y=yearly_axis1[col],
                mode="lines+markers",
                name=col,
                line={"color": axis1_colors.get(col, "#95A5A6")},
            )
        )
    trend_fig.update_layout(
        title="연도별 기술유형 추이",
        xaxis_title="연도",
        yaxis_title="특허 건수",
        font={"family": FONT_NAME or "sans-serif"},
    )

    # White space heatmap
    ws_grid = (
        pd.pivot_table(
            white_space_df,
            index="axis1_category",
            columns="axis2_category",
            values="count",
            fill_value=0,
        )
        .reindex(index=axis1_order, columns=axis2_order)
        .fillna(0)
    )
    ws_fig = go.Figure(
        data=[
            go.Heatmap(
                z=ws_grid.values,
                x=ws_grid.columns.tolist(),
                y=ws_grid.index.tolist(),
                colorscale="RdYlGn_r",
                colorbar={"title": "낮을수록 기회"},
            )
        ]
    )
    ws_fig.update_layout(
        title="화이트스페이스 히트맵", font={"family": FONT_NAME or "sans-serif"}
    )

    # Institution ranking
    applicant_col = "applicantName"
    top20 = df[applicant_col].fillna("미상").value_counts().head(20).index.tolist()
    top20_df = df[df[applicant_col].fillna("미상").isin(top20)].copy()
    top20_pivot = pd.crosstab(
        top20_df[applicant_col].fillna("미상"), top20_df["axis1_category"]
    ).reindex(top20)
    rank_fig = go.Figure()
    for col in axis1_order:
        if col in top20_pivot.columns:
            rank_fig.add_trace(
                go.Bar(
                    x=top20_pivot.index,
                    y=top20_pivot[col],
                    name=col,
                    marker_color=axis1_colors.get(col, "#95A5A6"),
                )
            )
    rank_fig.update_layout(
        title="상위 20개 출원인 카테고리 분해",
        barmode="stack",
        xaxis_tickangle=-55,
        font={"family": FONT_NAME or "sans-serif"},
    )

    # Stats
    total = int(len(df))
    top_axis1 = axis1_counts.idxmax()
    top_axis1_pct = pct(axis1_counts.max(), total)
    top_axis2 = axis2_counts.idxmax()
    top_axis2_pct = pct(axis2_counts.max(), total)
    top_applicant = df[applicant_col].fillna("미상").value_counts().idxmax()

    plotly_js = get_plotlyjs()

    pie_div = pie_fig.to_html(full_html=False, include_plotlyjs=False)
    bar_div = bar_fig.to_html(full_html=False, include_plotlyjs=False)
    heatmap_div = heatmap_fig.to_html(full_html=False, include_plotlyjs=False)
    trend_div = trend_fig.to_html(full_html=False, include_plotlyjs=False)
    ws_div = ws_fig.to_html(full_html=False, include_plotlyjs=False)
    rank_div = rank_fig.to_html(full_html=False, include_plotlyjs=False)

    # Data table rows
    display_cols = [
        "applicationNumber",
        "applicationDate",
        "inventionTitle",
        "applicantName",
        "ipcNumber",
        "axis1_category",
        "axis2_category",
    ]
    available_cols = [c for c in display_cols if c in df.columns]
    table_rows = []
    for _, row in df[available_cols].fillna("").iterrows():
        cells = "".join(f"<td>{escape(str(row[c]))}</td>" for c in available_cols)
        axis1_val = escape(str(row.get("axis1_category", "")))
        axis2_val = escape(str(row.get("axis2_category", "")))
        year_val = escape(str(row.get("year", "")))
        raw = " ".join(str(row[c]) for c in available_cols).lower()
        table_rows.append(
            f'<tr data-axis1="{axis1_val}" data-axis2="{axis2_val}" data-year="{year_val}" data-text="{escape(raw)}">{cells}</tr>'
        )

    axis1_options = "".join(
        [f'<option value="{escape(k)}">{escape(k)}</option>' for k in axis1_order]
    )
    axis2_options = "".join(
        [f'<option value="{escape(k)}">{escape(k)}</option>' for k in axis2_order]
    )
    year_options = "".join(
        [
            f'<option value="{y}">{y}</option>'
            for y in sorted(df["year"].dropna().unique().tolist())
            if y > 0
        ]
    )

    period = metadata.get("period", "")
    analysis_date = metadata.get("analysis_date", "")

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(dashboard_title)}</title>
  <style>
    body {{ font-family: NanumGothic, sans-serif; margin: 0; padding: 20px; background: #f7f9fc; }}
    h1 {{ margin: 0 0 16px 0; }}
    .cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }}
    .card {{ background: white; border-radius: 10px; padding: 12px 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.12); }}
    .card .k {{ color: #5f6b7a; font-size: 13px; }}
    .card .v {{ font-size: 24px; font-weight: 700; margin-top: 4px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
    .panel {{ background: white; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.12); padding: 8px; }}
    .full {{ grid-column: 1 / -1; }}
    .filters {{ margin: 18px 0 8px 0; display: flex; gap: 8px; flex-wrap: wrap; }}
    input, select {{ border: 1px solid #cfd6df; border-radius: 6px; padding: 8px; font-family: NanumGothic, sans-serif; }}
    table {{ width: 100%; border-collapse: collapse; background: white; font-size: 12px; }}
    th, td {{ border: 1px solid #e3e8ef; padding: 6px; vertical-align: top; text-align: left; }}
    th {{ position: sticky; top: 0; background: #f1f4f8; z-index: 1; }}
    .table-wrap {{ max-height: 480px; overflow: auto; background: white; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.12); }}
    @media (max-width: 1200px) {{ .cards {{ grid-template-columns: 1fr 1fr; }} .grid {{ grid-template-columns: 1fr; }} }}
  </style>
  <script>{plotly_js}</script>
</head>
<body>
  <h1>{escape(dashboard_title)}</h1>
  <p style="color:#666; margin-top:-12px;">분석 기간: {escape(period)} | 분석 일자: {escape(analysis_date)}</p>
  <div class="cards">
    <div class="card"><div class="k">총 특허 건수</div><div class="v">{total}</div></div>
    <div class="card"><div class="k">최다 기술유형 비중</div><div class="v">{escape(top_axis1)} {top_axis1_pct}%</div></div>
    <div class="card"><div class="k">최다 적용분야 비중</div><div class="v">{escape(top_axis2)} {top_axis2_pct}%</div></div>
    <div class="card"><div class="k">최다 출원인</div><div class="v">{escape(top_applicant)}</div></div>
  </div>

  <div class="grid">
    <div class="panel">{pie_div}</div>
    <div class="panel">{bar_div}</div>
    <div class="panel">{heatmap_div}</div>
    <div class="panel">{trend_div}</div>
    <div class="panel">{ws_div}</div>
    <div class="panel">{rank_div}</div>
  </div>

  <h2>특허 상세 데이터</h2>
  <div class="filters">
    <input id="searchInput" type="text" placeholder="제목/출원인/IPC 검색" />
    <select id="axis1Filter"><option value="">기술유형(전체)</option>{axis1_options}</select>
    <select id="axis2Filter"><option value="">적용분야(전체)</option>{axis2_options}</select>
    <select id="yearFilter"><option value="">연도(전체)</option>{year_options}</select>
  </div>
  <div class="table-wrap">
    <table>
      <thead>
        <tr><th>출원번호</th><th>출원일</th><th>발명명칭</th><th>출원인</th><th>IPC</th><th>기술유형</th><th>적용분야</th></tr>
      </thead>
      <tbody id="patentBody">
        {"".join(table_rows)}
      </tbody>
    </table>
  </div>

  <script>
    const searchInput = document.getElementById('searchInput');
    const axis1Filter = document.getElementById('axis1Filter');
    const axis2Filter = document.getElementById('axis2Filter');
    const yearFilter = document.getElementById('yearFilter');
    const rows = Array.from(document.querySelectorAll('#patentBody tr'));

    function applyFilter() {{
      const q = searchInput.value.trim().toLowerCase();
      const a1 = axis1Filter.value;
      const a2 = axis2Filter.value;
      const y = yearFilter.value;
      rows.forEach(r => {{
        const okQ = !q || (r.dataset.text || '').includes(q);
        const okA1 = !a1 || r.dataset.axis1 === a1;
        const okA2 = !a2 || r.dataset.axis2 === a2;
        const okY = !y || r.dataset.year === y;
        r.style.display = (okQ && okA1 && okA2 && okY) ? '' : 'none';
      }});
    }}

    [searchInput, axis1Filter, axis2Filter, yearFilter].forEach(el => el.addEventListener('input', applyFilter));
    [axis1Filter, axis2Filter, yearFilter].forEach(el => el.addEventListener('change', applyFilter));
  </script>
</body>
</html>
"""
    html_path = os.path.join(viz_dir, "patent_dashboard.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)


# ── 6. Excel & Markdown Export ────────────────────────────────────────────────


def write_excel(
    df,
    axis1_counts,
    axis2_counts,
    cross_tab,
    yearly_axis1,
    white_space_df,
    top20_sheet,
    output_dir,
):
    distribution_df = pd.concat(
        [
            pd.DataFrame(
                {
                    "axis": "기술 유형",
                    "category": axis1_counts.index,
                    "count": axis1_counts.values,
                }
            ),
            pd.DataFrame(
                {
                    "axis": "적용 분야",
                    "category": axis2_counts.index,
                    "count": axis2_counts.values,
                }
            ),
        ],
        ignore_index=True,
    )

    yearly_sheet = yearly_axis1.reset_index().rename(columns={"year": "연도"})

    excel_path = os.path.join(output_dir, "patent_analysis_report.xlsx")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="All_Patents")
        distribution_df.to_excel(writer, index=False, sheet_name="Distribution")
        cross_tab.to_excel(writer, sheet_name="Cross_Tabulation")
        yearly_sheet.to_excel(writer, index=False, sheet_name="Yearly_Trends")
        white_space_df.to_excel(writer, index=False, sheet_name="White_Space")
        top20_sheet.to_excel(writer, index=False, sheet_name="Top_Institutions")


def write_markdown_summary(
    df,
    axis1_counts,
    axis2_counts,
    yearly_axis1,
    white_space_df,
    top20_sheet,
    axis1_name,
    axis2_name,
    metadata,
    output_dir,
):
    total = len(df)
    top_axis1 = axis1_counts.idxmax()
    top_axis2 = axis2_counts.idxmax()
    applicant_col = "applicantName"
    top_applicant = df[applicant_col].fillna("미상").value_counts().idxmax()
    top_applicant_count = int(df[applicant_col].fillna("미상").value_counts().max())

    ws_top = white_space_df.sort_values(
        ["count", "axis1_category", "axis2_category"]
    ).head(10)
    ws_desc = ", ".join(
        [
            f"{r.axis1_category}×{r.axis2_category}({int(r.count)}건)"
            for r in ws_top.itertuples()
        ]
    )

    axis1_table = pd.DataFrame(
        {
            axis1_name: axis1_counts.index,
            "건수": axis1_counts.values,
            "비중(%)": [pct(v, total) for v in axis1_counts.values],
        }
    )
    axis2_table = pd.DataFrame(
        {
            axis2_name: axis2_counts.index,
            "건수": axis2_counts.values,
            "비중(%)": [pct(v, total) for v in axis2_counts.values],
        }
    )

    year_totals = yearly_axis1.sum(axis=1)
    year_lines = [
        f"- {y}년: 총 {int(year_totals.loc[y])}건" for y in yearly_axis1.index
    ]

    top5_inst = top20_sheet.head(5).copy()
    inst_lines = []
    for r in top5_inst.itertuples():
        focus = r.primary_axis1 if isinstance(r.primary_axis1, str) else "-"
        inst_lines.append(
            f"- {r.applicantName}: {int(r.total_count)}건 (주력: {focus})"
        )

    title = metadata.get("title", "특허 분류 및 동향 분석 요약")
    period = metadata.get("period", "")

    md = f"""# {title}

## 1. Executive summary
- 총 분석 건수: **{total}건**
- 핵심 기술 분야({axis1_name}): **{top_axis1}** ({axis1_counts.max()}건, {pct(axis1_counts.max(), total)}%)
- 핵심 적용 분야({axis2_name}): **{top_axis2}** ({axis2_counts.max()}건, {pct(axis2_counts.max(), total)}%)
- 주요 출원인: **{top_applicant}** ({top_applicant_count}건)
- 주요 화이트스페이스: {ws_desc}

## 2. 주요 발견사항
- 특허 포트폴리오는 {top_axis1} 및 {top_axis2} 중심으로 집중되어 있다.
- {axis1_name}별로는 상위 카테고리가 전체의 과반을 차지하며, 기술 집중도가 높다.
- {axis2_name}별로는 특정 적용 분야에 출원이 편중되어 있어 다각화 여지가 존재한다.
- 상위 출원인들은 특정 기술축에 전문화된 포트폴리오를 구축하는 경향이 뚜렷하다.
- 교차분석 기준 저밀도 셀(화이트스페이스)은 향후 차별화된 R&D 기획 및 특허 선점 가능성이 높은 영역이다.

## 3. {axis1_name}별 분포
{markdown_table(axis1_table)}

## 4. {axis2_name}별 분포
{markdown_table(axis2_table)}

## 5. 연도별 출원 추이
{period} 구간에서 연도별 출원 건수는 다음과 같다.
{chr(10).join(year_lines)}

## 6. 화이트스페이스 분석
화이트스페이스는 {axis1_name}과 {axis2_name} 교차 셀 중 저밀도 영역(저출원 구간)을 의미한다.

- 우선 기회영역 Top 10: {ws_desc}
- 저밀도 영역은 기존 경쟁이 상대적으로 낮아 신규 기술조합 진입 및 선제 특허 전략 수립에 유리하다.

## 7. 기관 분석
상위 출원기관 및 주력 분야는 다음과 같다.
{chr(10).join(inst_lines)}

기관별로 보유 기술축이 상이하므로, 협업/라이선싱/공동개발 전략 수립 시 카테고리 보완성을 기반으로 파트너십 설계가 필요하다.
"""

    md_path = os.path.join(output_dir, "patent_classification_summary.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)


# ── 7. Main Pipeline ─────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Standard Patent Analysis Script")
    parser.add_argument(
        "--config", required=True, help="Path to classification_config.json"
    )
    parser.add_argument("--input", default=None, help="Override input Excel file path")
    parser.add_argument("--output-dir", default=None, help="Override output directory")
    args = parser.parse_args()

    cfg = load_config(args.config)

    # Paths
    input_file = args.input or cfg["input"]["file"]
    output_dir = args.output_dir or cfg["output"].get("dir", "output")
    viz_dir = cfg["output"].get("viz_dir", os.path.join(output_dir, "visualizations"))

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(viz_dir, exist_ok=True)

    # Classification config
    cls = cfg["classification"]
    axis1_cfg = cls["axis1"]
    axis2_cfg = cls["axis2"]
    axis1_name = axis1_cfg["name"]
    axis2_name = axis2_cfg["name"]
    axis1_order = axis1_cfg["order"]
    axis2_order = axis2_cfg["order"]
    axis1_colors = axis1_cfg["colors"]
    axis2_colors = axis2_cfg["colors"]
    axis1_ipc_map = axis1_cfg.get("ipc_map", {})
    axis1_keywords = axis1_cfg.get("keywords", {})
    axis2_ipc_map = axis2_cfg.get("ipc_map", {})
    axis2_keywords = axis2_cfg.get("keywords", {})
    axis1_other = axis1_cfg.get("other_label", "기타")
    axis2_other = axis2_cfg.get("other_label", "기타")

    year_range = cfg.get("year_range", [2020, 2027])
    metadata = cfg.get("metadata", {})

    # ─ Load data
    print(f"\n[1] 데이터 로드 중... ({input_file})")
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"입력 파일이 없습니다: {input_file}")

    df = pd.read_excel(input_file)
    required_cols = [
        "applicationNumber",
        "applicationDate",
        "inventionTitle",
        "applicantName",
        "ipcNumber",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"필수 컬럼 누락: {missing}")

    print(f"  총 {len(df)}건 로드 완료")

    # ─ Prepare text for classification
    abstract_col = "astrtCont" if "astrtCont" in df.columns else None
    query_col = "source_query" if "source_query" in df.columns else None

    text_parts = [df["inventionTitle"].fillna("").astype(str)]
    if abstract_col:
        text_parts.append(df[abstract_col].fillna("").astype(str))
    if query_col:
        text_parts.append(df[query_col].fillna("").astype(str))

    df["title_abstract"] = pd.concat(text_parts, axis=1).apply(
        lambda row: " ".join(row).lower(), axis=1
    )

    # ─ Classify
    print("\n[2] 분류 체계 적용 중...")
    df["axis1_category"] = df.apply(
        lambda r: classify_axis(
            r["ipcNumber"],
            r["title_abstract"],
            axis1_ipc_map,
            axis1_keywords,
            axis1_other,
        ),
        axis=1,
    )
    df["axis2_category"] = df.apply(
        lambda r: classify_axis(
            r["ipcNumber"],
            r["title_abstract"],
            axis2_ipc_map,
            axis2_keywords,
            axis2_other,
        ),
        axis=1,
    )

    axis1_other_ratio = (df["axis1_category"] == axis1_other).mean()
    axis2_other_ratio = (df["axis2_category"] == axis2_other).mean()
    print(f"  축1 '{axis1_other}' 비율: {axis1_other_ratio:.1%}")
    print(f"  축2 '{axis2_other}' 비율: {axis2_other_ratio:.1%}")

    # ─ Year extraction
    date_str = df["applicationDate"].astype(str).str.extract(r"(\d{4})", expand=False)
    df["year"] = pd.to_numeric(date_str, errors="coerce").fillna(0).astype(int)

    # ─ Aggregation
    print("\n[3] 데이터 집계 중...")
    axis1_counts = (
        df["axis1_category"].value_counts().reindex(axis1_order, fill_value=0)
    )
    axis2_counts = (
        df["axis2_category"].value_counts().reindex(axis2_order, fill_value=0)
    )

    cross_tab = pd.crosstab(df["axis1_category"], df["axis2_category"]).reindex(
        index=axis1_order, columns=axis2_order, fill_value=0
    )

    years = list(range(year_range[0], year_range[1]))
    yearly_axis1 = pd.crosstab(df["year"], df["axis1_category"]).reindex(
        index=years, columns=axis1_order, fill_value=0
    )

    # White space
    white_space_threshold = max(
        1, int(np.floor(np.quantile(cross_tab.values.flatten(), 0.25)))
    )
    white_space_records = []
    for a1 in axis1_order:
        for a2 in axis2_order:
            cnt = int(cross_tab.loc[a1, a2])
            white_space_records.append(
                {
                    "axis1_category": a1,
                    "axis2_category": a2,
                    "count": cnt,
                    "is_low_density": "Y" if cnt <= white_space_threshold else "N",
                }
            )
    white_space_df = (
        pd.DataFrame(white_space_records)
        .sort_values(["count", "axis1_category", "axis2_category"])
        .reset_index(drop=True)
    )

    # Top 20 institutions
    applicant_col = "applicantName"
    top20_names = (
        df[applicant_col].fillna("미상").value_counts().head(20).index.tolist()
    )
    top20_data = []
    for name in top20_names:
        subset = df[df[applicant_col].fillna("미상") == name]
        axis1_vc = pd.Series(subset["axis1_category"]).value_counts()
        primary = axis1_vc.idxmax() if len(axis1_vc) > 0 else "-"
        top20_data.append(
            {
                "applicantName": name,
                "total_count": len(subset),
                "primary_axis1": primary,
            }
        )
    top20_sheet = pd.DataFrame(top20_data)

    # ─ Charts
    print("\n[4] 차트 생성 중...")
    draw_axis1_pie(axis1_counts, axis1_colors, axis1_name, viz_dir)
    print("  ✓ axis1_distribution.png")

    draw_axis2_bar(axis2_counts, axis2_colors, axis2_name, viz_dir)
    print("  ✓ axis2_distribution.png")

    draw_cross_heatmap(cross_tab, axis1_name, axis2_name, viz_dir)
    print("  ✓ cross_tabulation_heatmap.png")

    draw_yearly_trend(yearly_axis1, axis1_colors, axis1_order, viz_dir)
    print("  ✓ yearly_trend.png")

    draw_white_space(cross_tab, white_space_threshold, axis1_name, axis2_name, viz_dir)
    print("  ✓ white_space_analysis.png")

    top20_pivot = draw_top_institutions(df, axis1_colors, axis1_order, viz_dir)
    print("  ✓ top_institutions.png")

    draw_institution_by_category(top20_pivot, axis1_colors, axis1_order, viz_dir)
    print("  ✓ institution_by_category.png")

    dashboard_title = metadata.get(
        "dashboard_title", metadata.get("title", "특허 분석 대시보드")
    )
    draw_combined_dashboard(
        axis1_counts,
        axis2_counts,
        cross_tab,
        yearly_axis1,
        top20_pivot,
        axis1_colors,
        axis2_colors,
        axis1_order,
        dashboard_title,
        viz_dir,
    )
    print("  ✓ combined_dashboard.png")

    # ─ HTML Dashboard
    print("\n[5] 인터랙티브 대시보드 생성 중...")
    dash_meta = {
        "axis1_name": axis1_name,
        "axis2_name": axis2_name,
        "period": metadata.get("period", ""),
        "analysis_date": metadata.get("analysis_date", ""),
    }
    build_plotly_dashboard(
        df,
        axis1_counts,
        axis2_counts,
        cross_tab,
        yearly_axis1,
        white_space_df,
        axis1_colors,
        axis2_colors,
        axis1_order,
        axis2_order,
        dashboard_title,
        dash_meta,
        viz_dir,
    )
    print("  ✓ patent_dashboard.html")

    # ─ Excel report
    print("\n[6] Excel 보고서 생성 중...")
    write_excel(
        df,
        axis1_counts,
        axis2_counts,
        cross_tab,
        yearly_axis1,
        white_space_df,
        top20_sheet,
        output_dir,
    )
    print(f"  ✓ patent_analysis_report.xlsx")

    # ─ Markdown summary
    print("\n[7] Markdown 보고서 작성 중...")
    write_markdown_summary(
        df,
        axis1_counts,
        axis2_counts,
        yearly_axis1,
        white_space_df,
        top20_sheet,
        axis1_name,
        axis2_name,
        metadata,
        output_dir,
    )
    print(f"  ✓ patent_classification_summary.md")

    # ─ Output verification
    print("\n[8] 출력물 검증 중...")
    required_outputs = [
        os.path.join(output_dir, "patent_analysis_report.xlsx"),
        os.path.join(output_dir, "patent_classification_summary.md"),
        os.path.join(viz_dir, "axis1_distribution.png"),
        os.path.join(viz_dir, "axis2_distribution.png"),
        os.path.join(viz_dir, "cross_tabulation_heatmap.png"),
        os.path.join(viz_dir, "yearly_trend.png"),
        os.path.join(viz_dir, "white_space_analysis.png"),
        os.path.join(viz_dir, "top_institutions.png"),
        os.path.join(viz_dir, "institution_by_category.png"),
        os.path.join(viz_dir, "combined_dashboard.png"),
        os.path.join(viz_dir, "patent_dashboard.html"),
    ]
    missing_outputs = [p for p in required_outputs if not os.path.exists(p)]
    if missing_outputs:
        raise RuntimeError(f"일부 산출물이 생성되지 않았습니다: {missing_outputs}")

    # ─ Summary
    axis1_other_pct = pct((df["axis1_category"] == axis1_other).sum(), len(df))
    axis2_other_pct = pct((df["axis2_category"] == axis2_other).sum(), len(df))

    print("\n" + "=" * 60)
    print("  분석 완료!")
    print(f"  총 특허 수: {len(df)}")
    print(f"  축1 '{axis1_other}' 비율: {axis1_other_pct}%")
    print(f"  축2 '{axis2_other}' 비율: {axis2_other_pct}%")
    print(f"  엑셀 보고서: {os.path.join(output_dir, 'patent_analysis_report.xlsx')}")
    print(
        f"  마크다운 요약: {os.path.join(output_dir, 'patent_classification_summary.md')}"
    )
    print(f"  인터랙티브 대시보드: {os.path.join(viz_dir, 'patent_dashboard.html')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
