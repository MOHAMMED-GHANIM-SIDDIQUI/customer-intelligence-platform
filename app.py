"""Streamlit dashboard for the customer analytics case study."""

from __future__ import annotations

import sys
from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from customer_analytics.config import CHURN_FEATURES, SEGMENT_FEATURES, SPEND_FEATURES, ProjectConfig  # noqa: E402
from customer_analytics.pipeline import PipelineResult, run_pipeline  # noqa: E402


RISK_ORDER = ["low", "medium", "high"]
RISK_COLORS = {
    "low": "#22c55e",
    "medium": "#f59e0b",
    "high": "#ef4444",
    "Low": "#22c55e",
    "Medium": "#f59e0b",
    "High": "#ef4444",
}
RISK_LABELS = {
    "low": "Low",
    "medium": "Medium",
    "high": "High",
}
DEFAULT_ACTIONS = {
    "low": "standard nurture",
    "medium": "engagement campaign",
    "high": "retention offer review",
}
ACTION_PRIORITY = {
    "retention offer review": 1,
    "engagement campaign": 2,
    "standard nurture": 3,
}
SCORING_FEATURES = sorted(set(SEGMENT_FEATURES + CHURN_FEATURES + SPEND_FEATURES))


CUSTOM_CSS = """
<style>
:root {
    --bg-0: #030712;
    --bg-1: #07111f;
    --panel: rgba(15, 23, 42, 0.72);
    --panel-strong: rgba(15, 23, 42, 0.9);
    --border: rgba(148, 163, 184, 0.20);
    --text: #e5eefc;
    --muted: #94a3b8;
    --primary: #6366f1;
    --blue: #3b82f6;
    --cyan: #22d3ee;
    --green: #22c55e;
    --orange: #f59e0b;
    --red: #ef4444;
    --shadow: 0 24px 70px rgba(0, 0, 0, 0.36);
}

html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 20% 0%, rgba(59, 130, 246, 0.18), transparent 30%),
        radial-gradient(circle at 80% 10%, rgba(34, 211, 238, 0.10), transparent 26%),
        linear-gradient(135deg, #071426 0%, #030712 48%, #020617 100%) !important;
    color: var(--text);
}

[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(148, 163, 184, 0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(148, 163, 184, 0.045) 1px, transparent 1px);
    background-size: 34px 34px;
    mask-image: linear-gradient(to bottom, rgba(0,0,0,0.72), rgba(0,0,0,0.12));
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { right: 1rem; }

.block-container {
    max-width: 1480px;
    padding-top: 1.4rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(2, 6, 23, 0.98), rgba(15, 23, 42, 0.94)) !important;
    border-right: 1px solid var(--border);
    box-shadow: 24px 0 70px rgba(0, 0, 0, 0.22);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #dbeafe !important;
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #f8fafc !important;
    letter-spacing: 0;
}

.sidebar-brand {
    padding: 1rem 0.85rem;
    margin-bottom: 0.9rem;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: rgba(15, 23, 42, 0.72);
    box-shadow: var(--shadow);
}

.sidebar-brand .eyebrow,
.section-eyebrow {
    color: var(--cyan);
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.sidebar-brand .title {
    color: #f8fafc;
    font-size: 1.05rem;
    font-weight: 800;
    margin-top: 0.25rem;
}

.control-label {
    margin: 1.15rem 0 0.45rem;
    padding-top: 0.8rem;
    border-top: 1px solid rgba(148, 163, 184, 0.14);
    color: #e0f2fe;
    font-size: 0.82rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 1.35rem 1.55rem 1.25rem;
    margin-bottom: 0.65rem;
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 8px;
    background:
        linear-gradient(120deg, rgba(30, 41, 59, 0.82), rgba(15, 23, 42, 0.62)),
        radial-gradient(circle at 88% 10%, rgba(34, 211, 238, 0.22), transparent 34%);
    box-shadow: var(--shadow);
    animation: fadeUp 720ms ease both;
}

.hero::after {
    content: "";
    position: absolute;
    inset: auto 1.2rem 0 1.2rem;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.7), transparent);
}

.hero h1 {
    margin: 0;
    font-size: clamp(2rem, 3.4vw, 3.45rem);
    line-height: 1.02;
    font-weight: 900;
    letter-spacing: 0;
    background: linear-gradient(90deg, #f8fafc, #93c5fd 42%, #22d3ee 88%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    max-width: 720px;
    margin: 0.55rem 0 0;
    color: #bfdbfe;
    font-size: 1.08rem;
}

.hero-status {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    margin-top: 0.8rem;
    padding: 0.54rem 0.78rem;
    border: 1px solid rgba(34, 211, 238, 0.28);
    border-radius: 999px;
    color: #cffafe;
    background: rgba(8, 47, 73, 0.42);
    font-size: 0.82rem;
    font-weight: 700;
}

.kpi-card,
.glass-card,
.alert-card,
.insight-card {
    border: 1px solid var(--border);
    border-radius: 8px;
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.76), rgba(15, 23, 42, 0.52));
    backdrop-filter: blur(18px);
    box-shadow: var(--shadow);
    animation: fadeUp 620ms ease both;
}

.kpi-card {
    min-height: 142px;
    padding: 1.05rem;
    transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}

.kpi-card:hover,
.glass-card:hover,
.insight-card:hover {
    transform: translateY(-3px);
    border-color: rgba(34, 211, 238, 0.34);
    box-shadow: 0 28px 80px rgba(0, 0, 0, 0.42);
}

.kpi-label {
    display: flex;
    justify-content: space-between;
    gap: 0.75rem;
    color: #bfdbfe;
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

.kpi-value {
    margin-top: 0.62rem;
    color: #f8fafc;
    font-size: clamp(1.65rem, 2.8vw, 2.55rem);
    font-weight: 900;
    line-height: 1;
}

.kpi-trend {
    margin-top: 0.75rem;
    color: var(--muted);
    font-size: 0.86rem;
}

.trend-up { color: var(--green); }
.trend-down { color: var(--red); }
.trend-neutral { color: var(--cyan); }

.decision-grid,
.insight-grid,
.top-insight-grid {
    display: grid;
    gap: 0.9rem;
    margin: 0.9rem 0 1.2rem;
}

.decision-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
}

.insight-grid,
.top-insight-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
}

.decision-kpi,
.insight-banner,
.top-insight-panel,
.executive-alert {
    position: relative;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(15, 23, 42, 0.58));
    box-shadow: var(--shadow);
    animation: fadeUp 620ms ease both;
}

.decision-kpi {
    min-height: 148px;
    padding: 1rem;
    transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}

.decision-kpi:hover,
.insight-banner:hover,
.top-insight-panel:hover {
    transform: translateY(-4px);
}

.decision-kpi.good {
    border-color: rgba(34, 197, 94, 0.36);
    box-shadow: 0 24px 70px rgba(34, 197, 94, 0.10);
}

.decision-kpi.risk {
    border-color: rgba(239, 68, 68, 0.38);
    box-shadow: 0 24px 70px rgba(239, 68, 68, 0.12);
}

.decision-kpi.neutral {
    border-color: rgba(34, 211, 238, 0.36);
    box-shadow: 0 24px 70px rgba(34, 211, 238, 0.10);
}

.kpi-topline {
    display: flex;
    justify-content: space-between;
    gap: 0.75rem;
    color: #bfdbfe;
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

.kpi-icon {
    width: 2.05rem;
    height: 2.05rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(148, 163, 184, 0.24);
}

.kpi-main-value {
    margin-top: 0.7rem;
    color: #f8fafc;
    font-size: clamp(1.65rem, 2.5vw, 2.35rem);
    line-height: 1;
    font-weight: 900;
}

.kpi-delta {
    margin-top: 0.72rem;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.86rem;
    font-weight: 800;
}

.kpi-delta.good { color: #86efac; }
.kpi-delta.risk { color: #fca5a5; }
.kpi-delta.neutral { color: #67e8f9; }

.executive-alert {
    padding: 1rem 1.1rem;
    margin: 0.85rem 0 1.1rem;
    border-color: rgba(239, 68, 68, 0.34);
    background:
        linear-gradient(90deg, rgba(127, 29, 29, 0.52), rgba(15, 23, 42, 0.76)),
        radial-gradient(circle at 92% 10%, rgba(239, 68, 68, 0.30), transparent 36%);
}

.executive-alert strong {
    color: #fee2e2;
    font-size: 1rem;
}

.executive-alert span {
    display: block;
    color: #fecaca;
    margin-top: 0.25rem;
}

.insight-banner,
.top-insight-panel {
    min-height: 128px;
    padding: 1rem;
    transition: transform 180ms ease, border-color 180ms ease;
}

.insight-banner::before,
.top-insight-panel::before {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 3px;
    background: linear-gradient(180deg, var(--cyan), var(--blue));
}

.insight-label {
    color: #67e8f9;
    font-size: 0.74rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.insight-value {
    margin-top: 0.45rem;
    color: #f8fafc;
    font-size: 1.1rem;
    font-weight: 850;
    line-height: 1.32;
}

.insight-note {
    margin-top: 0.45rem;
    color: #bfdbfe;
    font-size: 0.88rem;
}

.narrative-step {
    margin: 0.35rem 0 0.85rem;
    color: #93c5fd;
    font-size: 0.82rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.section-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin: 1.2rem 0 0.75rem;
}

.section-title h2 {
    margin: 0;
    color: #f8fafc;
    font-size: 1.12rem;
    font-weight: 850;
    letter-spacing: 0;
}

.section-title p {
    margin: 0.28rem 0 0;
    color: var(--muted);
    font-size: 0.9rem;
}

.glass-card {
    padding: 1rem;
    margin-bottom: 1rem;
}

.metric-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
}

.mini-card {
    padding: 0.88rem;
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 8px;
    background: rgba(2, 6, 23, 0.32);
}

.mini-card .label {
    color: var(--muted);
    font-size: 0.78rem;
    font-weight: 750;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

.mini-card .value {
    margin-top: 0.35rem;
    color: #f8fafc;
    font-size: 1.25rem;
    font-weight: 900;
}

.risk-high { color: var(--red); }
.risk-medium { color: var(--orange); }
.risk-low { color: var(--green); }

.pill {
    display: inline-flex;
    align-items: center;
    padding: 0.35rem 0.62rem;
    border-radius: 999px;
    border: 1px solid rgba(148, 163, 184, 0.18);
    background: rgba(15, 23, 42, 0.64);
    color: #dbeafe;
    font-size: 0.78rem;
    font-weight: 800;
}

.alert-card {
    padding: 1rem;
    border-color: rgba(239, 68, 68, 0.42);
    background: linear-gradient(135deg, rgba(127, 29, 29, 0.42), rgba(15, 23, 42, 0.72));
    color: #fee2e2;
}

.footer {
    margin: 2.5rem 0 0.4rem;
    text-align: center;
    color: #93a4ba;
    font-size: 0.88rem;
}

[data-testid="stMetric"] {
    min-height: 108px;
    padding: 0.9rem;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.76), rgba(15, 23, 42, 0.52));
    backdrop-filter: blur(18px);
    box-shadow: var(--shadow);
    transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: rgba(34, 211, 238, 0.34);
    box-shadow: 0 28px 80px rgba(0, 0, 0, 0.42);
}

[data-testid="stMetricLabel"] {
    color: #bfdbfe !important;
    font-weight: 850;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

[data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-weight: 900;
}

[data-testid="stMetricDelta"] {
    font-weight: 800;
}

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid rgba(148, 163, 184, 0.16);
}

.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] button {
    border: 1px solid rgba(34, 211, 238, 0.32) !important;
    border-radius: 8px !important;
    background: linear-gradient(90deg, rgba(79, 70, 229, 0.94), rgba(14, 165, 233, 0.9)) !important;
    color: #f8fafc !important;
    font-weight: 800 !important;
    box-shadow: 0 0 24px rgba(34, 211, 238, 0.16);
    transition: transform 180ms ease, box-shadow 180ms ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 34px rgba(34, 211, 238, 0.34);
}

[data-baseweb="tab-list"] {
    width: 100%;
    gap: 0.35rem;
    border-bottom: 1px solid rgba(148, 163, 184, 0.14);
}

[data-baseweb="tab"] {
    flex: 1 1 0;
    min-width: max-content;
    justify-content: center;
    padding: 0.75rem 0.85rem;
    border-radius: 8px 8px 0 0;
    color: #cbd5e1;
    font-weight: 800;
}

[aria-selected="true"] {
    color: #f8fafc !important;
    background: rgba(59, 130, 246, 0.16);
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 980px) {
    .metric-row {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .decision-grid,
    .insight-grid,
    .top-insight-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .hero {
        padding: 1.45rem;
    }
}

@media (max-width: 640px) {
    .metric-row {
        grid-template-columns: 1fr;
    }
    .decision-grid,
    .insight-grid,
    .top-insight-grid {
        grid-template-columns: 1fr;
    }
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>
"""


st.set_page_config(
    page_title="Customer Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner="Building customer intelligence pipeline...")
def load_pipeline_data() -> PipelineResult:
    """Run and cache the synthetic data, segmentation, churn, and spend models."""

    return run_pipeline(ProjectConfig())


def format_currency(value: float) -> str:
    """Format money values consistently across the app."""

    if pd.isna(value):
        return "N/A"
    return f"${value:,.0f}"


def format_percent(value: float) -> str:
    """Format percentage values while handling empty filtered states."""

    return "N/A" if pd.isna(value) else f"{value:.1%}"


def plotly_layout(fig: go.Figure, height: int = 390) -> go.Figure:
    """Apply the dashboard visual system to Plotly charts."""

    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(2, 6, 23, 0.22)",
        font={"color": "#dbeafe"},
        margin={"l": 18, "r": 18, "t": 48, "b": 20},
        legend_title_text="",
        hoverlabel={"bgcolor": "#020617", "font_color": "#f8fafc", "bordercolor": "#334155"},
    )
    fig.update_xaxes(gridcolor="rgba(148, 163, 184, 0.12)", zerolinecolor="rgba(148, 163, 184, 0.18)")
    fig.update_yaxes(gridcolor="rgba(148, 163, 184, 0.12)", zerolinecolor="rgba(148, 163, 184, 0.18)")
    return fig


def risk_bar_chart(data: pd.DataFrame, x: str, y: str, title: str, color: str = "risk_band") -> go.Figure:
    """Render a risk-colored bar chart with consistent enterprise styling."""

    fig = px.bar(
        data,
        x=x,
        y=y,
        color=color if color in data.columns else None,
        color_discrete_map=RISK_COLORS,
        title=title,
        text_auto=True,
        hover_data=[column for column in data.columns if column not in {x, y}],
    )
    fig.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False)
    return plotly_layout(fig)


def segment_bar_chart(data: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    fig = px.bar(
        data,
        x=x,
        y=y,
        color=y,
        color_continuous_scale=["#22d3ee", "#3b82f6", "#ef4444"],
        title=title,
        hover_data=[column for column in data.columns if column not in {x, y}],
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(coloraxis_showscale=False)
    return plotly_layout(fig)


def render_decision_kpi_grid(cards: list[dict[str, str]]) -> None:
    """Render KPI cards with native Streamlit metrics.

    Native metrics avoid raw HTML leakage in Streamlit's markdown renderer while
    still inheriting the premium styling from the global CSS metric selectors.
    """

    columns = st.columns(len(cards))
    for column, card in zip(columns, cards, strict=True):
        tone = card.get("tone", "neutral")
        delta_color = "inverse" if tone == "risk" else "normal"
        if tone == "neutral":
            delta_color = "off"
        column.metric(
            card["label"],
            card["value"],
            card["delta"],
            delta_color=delta_color,
        )


def render_insight_grid(insights: list[dict[str, str]]) -> None:
    """Render insight cards with native Streamlit containers."""

    columns = st.columns(min(len(insights), 3))
    for column, item in zip(columns, insights, strict=False):
        with column.container(border=True):
            st.caption(str(item["label"]).upper())
            st.markdown(f"**{item['value']}**")
            st.write(item["note"])


def render_top_insights_panel(insights: list[dict[str, str]]) -> None:
    """Render top insights with native Streamlit containers."""

    columns = st.columns(min(len(insights), 3))
    for column, item in zip(columns, insights, strict=False):
        with column.container(border=True):
            st.caption(str(item["label"]).upper())
            st.markdown(f"**{item['value']}**")
            st.write(item["note"])


def inject_global_css() -> None:
    """Apply the enterprise dashboard visual system."""

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_hero() -> None:
    """Render the executive product hero."""

    st.markdown(
        """
        <section class="hero">
            <div class="section-eyebrow">Enterprise Analytics Suite</div>
            <h1>Customer Intelligence Platform</h1>
            <p>Predict churn, optimize retention, maximize revenue</p>
            <div class="hero-status">Live intelligence workspace | Segments | Churn | Revenue | Actions</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Render a minimal product footer."""

    st.markdown(
        '<div class="footer">Customer Intelligence Platform | Built for Data-Driven Decisions</div>',
        unsafe_allow_html=True,
    )


def render_section_title(icon: str, title: str, subtitle: str = "", badge: str = "") -> None:
    """Render a styled section title."""

    badge_html = f'<span class="pill">{badge}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="section-title">
            <div>
                <div class="section-eyebrow">Insight Module</div>
                <h2>{title}</h2>
                <p>{subtitle}</p>
            </div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_alert(message: str) -> None:
    """Render a styled error or empty-state card."""

    st.markdown(
        f"""
        <div class="alert-card">
            <strong>Data or pipeline error</strong><br />
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_card_start() -> None:
    """No-op retained for layout compatibility.

    Streamlit does not reliably wrap native components inside arbitrary HTML divs.
    Leaving this as a no-op prevents empty glass tiles from appearing in the UI.
    """


def render_card_end() -> None:
    """No-op retained for layout compatibility."""


def trend_badge(current: float, benchmark: float, inverse: bool = False) -> tuple[str, str]:
    """Return a compact trend indicator for KPI cards."""

    if pd.isna(current) or pd.isna(benchmark) or benchmark == 0:
        return "trend-neutral", "â†’ benchmark unavailable"
    delta = (current - benchmark) / abs(benchmark)
    is_positive = delta >= 0
    if inverse:
        is_positive = not is_positive
    css_class = "trend-up" if is_positive else "trend-down"
    arrow = "â†‘" if delta >= 0 else "â†“"
    return css_class, f"{arrow} {abs(delta):.1%} vs full base"


def metric_delta(current: float, benchmark: float, inverse: bool = False) -> tuple[str, str]:
    """Return a Streamlit-safe KPI delta and color direction."""

    if pd.isna(current) or pd.isna(benchmark) or benchmark == 0:
        return "Benchmark unavailable", "off"
    delta = (current - benchmark) / abs(benchmark)
    color = "inverse" if inverse else "normal"
    return f"{delta:+.1%} vs full base", color


def kpi_delta_card(current: float, benchmark: float, inverse: bool = False) -> tuple[str, str, str]:
    """Return card delta text, visual tone, and arrow for custom KPIs."""

    if pd.isna(current) or pd.isna(benchmark) or benchmark == 0:
        return "Benchmark unavailable", "neutral", "â€¢"
    delta = (current - benchmark) / abs(benchmark)
    is_good = delta < 0 if inverse else delta >= 0
    tone = "good" if is_good else "risk"
    arrow = "â†‘" if delta >= 0 else "â†“"
    return f"{delta:+.1%} vs full base", tone, arrow


def build_executive_insights(dashboard: pd.DataFrame, filtered: pd.DataFrame) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Create business-readable insight cards from existing model outputs."""

    if filtered.empty:
        empty = [{"label": "No active selection", "value": "Filters removed all customers", "note": "Adjust filters to restore insight generation."}]
        return empty, empty

    total_revenue_at_risk = filtered["revenue_at_risk"].sum()
    total_forecast = filtered["predicted_next_month_spend"].sum()
    exposure_share = total_revenue_at_risk / max(total_forecast, 1)

    high_risk = filtered[filtered["risk_band"] == "high"]
    high_risk_exposure = high_risk["revenue_at_risk"].sum()
    high_risk_share = high_risk_exposure / max(total_revenue_at_risk, 1)

    segment_risk = (
        filtered.groupby("segment", as_index=False)
        .agg(
            avg_churn=("churn_probability", "mean"),
            revenue_at_risk=("revenue_at_risk", "sum"),
            customers=("customer_id", "count"),
        )
        .sort_values(["avg_churn", "revenue_at_risk"], ascending=False)
    )
    top_risk_segment = segment_risk.iloc[0] if not segment_risk.empty else None
    top_revenue_segment = segment_risk.sort_values("revenue_at_risk", ascending=False).iloc[0] if not segment_risk.empty else None

    action_mix = (
        filtered.groupby("recommended_action", as_index=False)
        .agg(customers=("customer_id", "count"), revenue_at_risk=("revenue_at_risk", "sum"))
        .sort_values(["customers", "revenue_at_risk"], ascending=False)
    )
    common_action = action_mix.iloc[0] if not action_mix.empty else None

    recent_risk = filtered[filtered["recency_days"] <= filtered["recency_days"].median()]["churn_probability"].mean()
    base_churn = dashboard["churn_probability"].mean()

    insights = [
        {
            "label": "Revenue Exposure",
            "value": f"High-risk customers contribute {high_risk_share:.0%} of selected revenue at risk.",
            "note": f"{len(high_risk):,} high-risk customers expose {format_currency(high_risk_exposure)}.",
        },
        {
            "label": "Segment Signal",
            "value": f"Segment {int(top_risk_segment['segment']) if top_risk_segment is not None else 'N/A'} has the highest churn probability.",
            "note": f"Average churn is {format_percent(top_risk_segment['avg_churn']) if top_risk_segment is not None else 'N/A'}.",
        },
        {
            "label": "Behavior Pattern",
            "value": f"Recent customers show {format_percent(recent_risk)} churn versus {format_percent(base_churn)} full-base churn.",
            "note": "Use this to distinguish true retention risk from normal activity recency.",
        },
    ]

    top_panel = [
        {
            "label": "Top Risky Segment",
            "value": f"Segment {int(top_risk_segment['segment']) if top_risk_segment is not None else 'N/A'}",
            "note": f"{int(top_risk_segment['customers']) if top_risk_segment is not None else 0:,} customers in current view.",
        },
        {
            "label": "Top Revenue Segment",
            "value": f"Segment {int(top_revenue_segment['segment']) if top_revenue_segment is not None else 'N/A'}",
            "note": f"{format_currency(top_revenue_segment['revenue_at_risk']) if top_revenue_segment is not None else 'N/A'} exposed.",
        },
        {
            "label": "Most Common Action",
            "value": str(common_action["recommended_action"]) if common_action is not None else "N/A",
            "note": f"{int(common_action['customers']) if common_action is not None else 0:,} customers affected.",
        },
    ]

    insights[0]["note"] += f" Total exposure is {exposure_share:.0%} of forecast revenue."
    return insights, top_panel


def render_executive_alert(filtered: pd.DataFrame) -> None:
    """Render the attention-grabbing executive exposure banner."""

    if filtered.empty:
        return
    high_risk = filtered[filtered["risk_band"] == "high"]
    high_risk_share = len(high_risk) / max(len(filtered), 1)
    exposure = high_risk["revenue_at_risk"].sum()
    st.markdown(
        f"""
        <div class="executive-alert">
            <strong>Critical exposure: {high_risk_share:.0%} of selected customers are high-risk, contributing {format_currency(exposure)} in revenue exposure.</strong>
            <span>Prioritize the highest-value accounts before reviewing lower-risk cohorts.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_dashboard_table(result: PipelineResult) -> pd.DataFrame:
    """Join scored actions with customer attributes for filtering and exploration."""

    customer_columns = [
        "customer_id",
        "country",
        "age",
        "income",
        "tenure_months",
        "visits_per_month",
        "total_orders",
        "total_spend",
        "average_order_value",
        "discount_rate",
        "recency_days",
        "orders_per_active_month",
        "spend_per_visit",
    ]
    dashboard = result.customer_actions.merge(
        result.customer_data[customer_columns],
        on="customer_id",
        how="left",
    )
    dashboard["recommended_action"] = dashboard["recommended_action"].astype(str)
    dashboard["revenue_at_risk"] = (
        dashboard["churn_probability"] * dashboard["predicted_next_month_spend"]
    )
    dashboard["action_priority"] = dashboard["recommended_action"].map(ACTION_PRIORITY).fillna(99)
    return dashboard


def render_business_rules() -> tuple[float, float, dict[str, str]]:
    """Collect company-specific risk thresholds and CRM action labels."""

    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <div class="eyebrow">Control Panel</div>
            <div class="title">Customer Intelligence</div>
        </div>
        <div class="control-label">Business Rules</div>
        """,
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Run Demo Pipeline", width="stretch"):
        load_pipeline_data.clear()
        st.rerun()

    medium_threshold_pct = st.sidebar.slider(
        "Medium risk starts at",
        min_value=1,
        max_value=80,
        value=20,
        step=1,
        help="Customers at or above this churn probability are medium risk.",
    )
    high_threshold_pct = st.sidebar.slider(
        "High risk starts at",
        min_value=medium_threshold_pct + 1,
        max_value=95,
        value=max(50, medium_threshold_pct + 1),
        step=1,
        help="Customers at or above this churn probability are high risk.",
    )

    action_options = [
        "standard nurture",
        "engagement campaign",
        "retention offer review",
        "customer success call",
        "loyalty incentive",
        "win-back journey",
    ]
    with st.sidebar.expander("Action mapping", expanded=True):
        low_action = st.selectbox(
            "Low-risk action",
            action_options,
            index=action_options.index(DEFAULT_ACTIONS["low"]),
        )
        medium_action = st.selectbox(
            "Medium-risk action",
            action_options,
            index=action_options.index(DEFAULT_ACTIONS["medium"]),
        )
        high_action = st.selectbox(
            "High-risk action",
            action_options,
            index=action_options.index(DEFAULT_ACTIONS["high"]),
        )

    return (
        medium_threshold_pct / 100,
        high_threshold_pct / 100,
        {
            "low": low_action.strip() or DEFAULT_ACTIONS["low"],
            "medium": medium_action.strip() or DEFAULT_ACTIONS["medium"],
            "high": high_action.strip() or DEFAULT_ACTIONS["high"],
        },
    )


def assign_risk_band(
    churn_probability: pd.Series,
    medium_threshold: float,
    high_threshold: float,
) -> pd.Series:
    """Convert churn probabilities into business-friendly risk bands."""

    bands = pd.cut(
        churn_probability,
        bins=[0, medium_threshold, high_threshold, 1.0],
        labels=["low", "medium", "high"],
        include_lowest=True,
    )
    return bands.astype(str)


def apply_business_rules(
    scored: pd.DataFrame,
    medium_threshold: float,
    high_threshold: float,
    actions: dict[str, str],
) -> pd.DataFrame:
    """Apply company risk thresholds and action labels to scored customers."""

    output = scored.copy()
    output["risk_band"] = assign_risk_band(
        output["churn_probability"],
        medium_threshold=medium_threshold,
        high_threshold=high_threshold,
    )
    output["risk_label"] = output["risk_band"].map(RISK_LABELS)
    output["recommended_action"] = output["risk_band"].map(actions).astype(str)
    output["revenue_at_risk"] = output["churn_probability"] * output["predicted_next_month_spend"]
    output["action_priority"] = output["risk_band"].map({"high": 1, "medium": 2, "low": 3}).fillna(99)
    return output


def score_customer_features(
    result: PipelineResult,
    customer_features: pd.DataFrame,
    medium_threshold: float,
    high_threshold: float,
    actions: dict[str, str],
) -> pd.DataFrame:
    """Score uploaded or manually entered customer features with trained artifacts."""

    scored = customer_features.copy()
    if "customer_id" not in scored.columns:
        scored.insert(0, "customer_id", range(1, len(scored) + 1))

    scored["segment"] = result.segmentation.model.predict(scored[SEGMENT_FEATURES])
    scored["churn_probability"] = result.churn.selected_model.predict_proba(scored[CHURN_FEATURES])[:, 1]
    scored["predicted_next_month_spend"] = result.spend.champion_model.predict(scored[SPEND_FEATURES]).clip(min=0)
    return apply_business_rules(scored, medium_threshold, high_threshold, actions)


def apply_sidebar_filters(dashboard: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar controls and return the filtered customer table."""

    st.sidebar.markdown(
        """
        <div class="control-label">Data Status</div>
        <div class="mini-card">
            <div class="label">Pipeline</div>
            <div class="value">Loaded</div>
        </div>
        <div class="control-label">Filters</div>
        """,
        unsafe_allow_html=True,
    )

    quick_view = st.sidebar.selectbox(
        "Quick View Mode",
        ["All Customers", "High Risk Only", "High Value Customers", "Retention Priority"],
        help="Applies a decision-ready filter preset before manual filters.",
    )

    if quick_view == "High Risk Only":
        segment_defaults = sorted(dashboard["segment"].unique())
        risk_defaults = ["high"]
        min_spend_default = float(dashboard["predicted_next_month_spend"].min())
    elif quick_view == "High Value Customers":
        segment_defaults = sorted(dashboard["segment"].unique())
        risk_defaults = RISK_ORDER
        min_spend_default = float(dashboard["predicted_next_month_spend"].quantile(0.75))
    elif quick_view == "Retention Priority":
        priority_pool = dashboard[dashboard["action_priority"] <= 2]
        segment_defaults = sorted(priority_pool["segment"].unique()) if not priority_pool.empty else sorted(dashboard["segment"].unique())
        risk_defaults = ["medium", "high"]
        min_spend_default = float(dashboard["predicted_next_month_spend"].min())
    else:
        segment_defaults = sorted(dashboard["segment"].unique())
        risk_defaults = RISK_ORDER
        min_spend_default = float(dashboard["predicted_next_month_spend"].min())

    selected_segments = st.sidebar.multiselect(
        "Segments",
        options=sorted(dashboard["segment"].unique()),
        default=segment_defaults,
    )
    selected_risk_bands = st.sidebar.multiselect(
        "Risk bands",
        options=RISK_ORDER,
        default=risk_defaults,
        format_func=lambda value: RISK_LABELS[value],
    )
    selected_countries = st.sidebar.multiselect(
        "Countries",
        options=sorted(dashboard["country"].unique()),
        default=sorted(dashboard["country"].unique()),
    )

    min_age, max_age = int(dashboard["age"].min()), int(dashboard["age"].max())
    selected_age = st.sidebar.slider("Age range", min_age, max_age, (min_age, max_age))

    min_spend = float(dashboard["predicted_next_month_spend"].min())
    max_spend = float(dashboard["predicted_next_month_spend"].max())
    selected_spend = st.sidebar.slider(
        "Predicted spend range",
        min_value=min_spend,
        max_value=max_spend,
        value=(min_spend_default, max_spend),
        step=10.0,
    )

    if not selected_segments or not selected_risk_bands or not selected_countries:
        st.sidebar.markdown(
            '<div class="alert-card">Select at least one value in each filter.</div>',
            unsafe_allow_html=True,
        )
        return dashboard.iloc[0:0]

    return dashboard[
        dashboard["segment"].isin(selected_segments)
        & dashboard["risk_band"].isin(selected_risk_bands)
        & dashboard["country"].isin(selected_countries)
        & dashboard["age"].between(selected_age[0], selected_age[1])
        & dashboard["predicted_next_month_spend"].between(selected_spend[0], selected_spend[1])
    ].copy()


def render_kpis(dashboard: pd.DataFrame, filtered: pd.DataFrame) -> None:
    """Show executive KPIs for the current filter context."""

    total_customers = len(filtered)
    revenue_at_risk = filtered["revenue_at_risk"].sum()
    churn_rate = filtered["churn_probability"].mean()
    avg_customer_value = filtered["total_spend"].mean()

    base_churn = dashboard["churn_probability"].mean()
    base_revenue_at_risk = dashboard["revenue_at_risk"].sum()
    base_customer_value = dashboard["total_spend"].mean()

    churn_delta, churn_tone, churn_arrow = kpi_delta_card(churn_rate, base_churn, inverse=True)
    revenue_delta, revenue_tone, revenue_arrow = kpi_delta_card(revenue_at_risk, base_revenue_at_risk, inverse=True)
    value_delta, value_tone, value_arrow = kpi_delta_card(avg_customer_value, base_customer_value)
    selected_share = total_customers / max(len(dashboard), 1)
    render_decision_kpi_grid(
        [
            {
                "icon": "ðŸ‘¥",
                "label": "Total Customers",
                "value": f"{total_customers:,}",
                "delta": f"{selected_share:.1%} selected",
                "tone": "neutral",
                "arrow": "â€¢",
            },
            {
                "icon": "âš ",
                "label": "Churn Rate",
                "value": format_percent(churn_rate),
                "delta": churn_delta,
                "tone": churn_tone,
                "arrow": churn_arrow,
            },
            {
                "icon": "ðŸ’¸",
                "label": "Revenue at Risk",
                "value": format_currency(revenue_at_risk),
                "delta": revenue_delta,
                "tone": revenue_tone,
                "arrow": revenue_arrow,
            },
            {
                "icon": "ðŸ’Ž",
                "label": "Avg Customer Value",
                "value": format_currency(avg_customer_value),
                "delta": value_delta,
                "tone": value_tone,
                "arrow": value_arrow,
            },
        ]
    )


def render_empty_state(filtered: pd.DataFrame) -> bool:
    """Stop a tab cleanly when filters remove all customers."""

    if not filtered.empty:
        return False
    render_alert("No customers match the current filters. Adjust the sidebar selections.")
    return True


def render_risk_distribution(filtered: pd.DataFrame) -> None:
    """Render color-coded risk distribution indicators."""

    counts = filtered["risk_band"].value_counts().reindex(RISK_ORDER, fill_value=0)
    total = max(int(counts.sum()), 1)
    high_count = int(counts["high"])
    render_decision_kpi_grid(
        [
            {
                "icon": {"low": "âœ“", "medium": "!", "high": "âš "}[risk],
                "label": f"{RISK_LABELS[risk]} Risk",
                "value": f"{int(counts[risk]):,}",
                "delta": f"{counts[risk] / total:.1%} of selected customers",
                "tone": {"low": "good", "medium": "neutral", "high": "risk"}[risk],
                "arrow": {"low": "â†‘", "medium": "â€¢", "high": "â†“"}[risk],
            }
            for risk in RISK_ORDER
        ]
    )
    st.markdown(
        f'<div class="hero-status">High Risk Customers: {high_count:,} require priority review</div>',
        unsafe_allow_html=True,
    )


def style_customer_rows(row: pd.Series) -> list[str]:
    """Apply risk and value highlighting to customer tables."""

    styles = [""] * len(row)
    risk = row.get("risk_label", "")
    revenue_at_risk = row.get("revenue_at_risk", 0)
    if risk == "High":
        styles = ["background-color: rgba(239, 68, 68, 0.18); color: #fee2e2"] * len(row)
    elif risk == "Medium":
        styles = ["background-color: rgba(245, 158, 11, 0.14); color: #ffedd5"] * len(row)
    elif risk == "Low":
        styles = ["background-color: rgba(34, 197, 94, 0.10); color: #dcfce7"] * len(row)

    if "revenue_at_risk" in row.index and pd.notna(revenue_at_risk):
        revenue_index = list(row.index).index("revenue_at_risk")
        styles[revenue_index] = "background-color: rgba(34, 211, 238, 0.24); color: #ecfeff; font-weight: 800"
    return styles


def render_customer_intelligence_table(customers: pd.DataFrame, limit: int = 150) -> None:
    """Render the executive customer table with conditional formatting."""

    table = customers.sort_values(
        ["action_priority", "revenue_at_risk", "churn_probability"],
        ascending=[True, False, False],
    ).head(limit).copy()
    table["churn_probability_pct"] = table["churn_probability"] * 100
    display_columns = [
        "customer_id",
        "country",
        "segment",
        "risk_label",
        "churn_probability_pct",
        "predicted_next_month_spend",
        "revenue_at_risk",
        "recommended_action",
    ]
    styled = table[display_columns].style.apply(style_customer_rows, axis=1).format(
        {
            "churn_probability_pct": "{:.1f}%",
            "predicted_next_month_spend": "${:,.2f}",
            "revenue_at_risk": "${:,.2f}",
        }
    )
    st.dataframe(styled, width="stretch", hide_index=True)


def render_action_insights(filtered: pd.DataFrame) -> None:
    """Render retention action recommendations with priority levels."""

    action_mix = (
        filtered.groupby(["recommended_action", "risk_band"], as_index=False)
        .agg(customers=("customer_id", "count"), revenue_at_risk=("revenue_at_risk", "sum"))
        .sort_values(["risk_band", "revenue_at_risk"], ascending=[False, False])
    )
    priority_lookup = {"high": "Priority 1", "medium": "Priority 2", "low": "Priority 3"}
    action_mix["priority"] = action_mix["risk_band"].map(priority_lookup)
    st.dataframe(
        action_mix[["priority", "recommended_action", "customers", "revenue_at_risk"]],
        width="stretch",
        hide_index=True,
        column_config={
            "priority": "Priority",
            "recommended_action": "Recommended action",
            "customers": st.column_config.NumberColumn("Customers", format="%d"),
            "revenue_at_risk": st.column_config.NumberColumn("Revenue at risk", format="$%.0f"),
        },
    )


def render_executive_summary(dashboard: pd.DataFrame, filtered: pd.DataFrame) -> None:
    """Render the primary business overview."""

    render_section_title("ðŸ“Š", "Executive KPI Strip", "WHAT: customer health, churn risk, and revenue exposure.")
    st.markdown('<div class="narrative-step">1. WHAT changed</div>', unsafe_allow_html=True)
    render_kpis(dashboard, filtered)
    if render_empty_state(filtered):
        return

    render_executive_alert(filtered)
    insights, top_panel = build_executive_insights(dashboard, filtered)
    render_section_title("ðŸ§ ", "Key Insights", "WHY: AI-style business readouts generated from model outputs.", "Decision layer")
    st.markdown('<div class="narrative-step">2. WHY it matters</div>', unsafe_allow_html=True)
    render_insight_grid(insights)
    render_section_title("ðŸ§¾", "Top Insights Panel", "The fastest read on segment risk, revenue concentration, and recommended action.")
    render_top_insights_panel(top_panel)

    render_section_title("ðŸ“ˆ", "Risk Distribution", "Low, medium, and high-risk customer composition.", "Live risk mix")
    st.markdown('<div class="narrative-step">3. WHERE risk is concentrated</div>', unsafe_allow_html=True)
    render_card_start()
    render_risk_distribution(filtered)
    risk_mix = (
        filtered.groupby("risk_band", as_index=False)
        .agg(customers=("customer_id", "count"), revenue_at_risk=("revenue_at_risk", "sum"))
    )
    risk_mix["risk_band"] = pd.Categorical(risk_mix["risk_band"], categories=RISK_ORDER, ordered=True)
    risk_mix = risk_mix.sort_values("risk_band")
    st.plotly_chart(risk_bar_chart(risk_mix, "risk_band", "customers", "Customers by risk band"), width="stretch")
    render_card_end()

    render_section_title("ðŸ’°", "Revenue at Risk Breakdown", "Prioritize the customers and segments with the most exposed revenue.")
    left, right = st.columns([1, 1])
    with left:
        render_card_start()
        st.markdown("#### Revenue at risk by segment")
        segment_risk = (
            filtered.groupby("segment", as_index=False)
            .agg(
                customers=("customer_id", "count"),
                forecast_revenue=("predicted_next_month_spend", "sum"),
                revenue_at_risk=("revenue_at_risk", "sum"),
                avg_churn_probability=("churn_probability", "mean"),
            )
            .sort_values("revenue_at_risk", ascending=False)
        )
        st.plotly_chart(segment_bar_chart(segment_risk, "segment", "revenue_at_risk", "Revenue at risk by segment"), width="stretch")
        render_card_end()
    with right:
        render_card_start()
        st.markdown("#### Top 10 risky customers")
        top_risky = filtered.sort_values("revenue_at_risk", ascending=False).head(10).copy()
        top_risky["churn_probability_pct"] = top_risky["churn_probability"] * 100
        st.dataframe(
            top_risky[
                [
                    "customer_id",
                    "risk_label",
                    "churn_probability_pct",
                    "predicted_next_month_spend",
                    "revenue_at_risk",
                ]
            ],
            width="stretch",
            hide_index=True,
            column_config={
                "customer_id": "Customer ID",
                "risk_label": "Risk",
                "churn_probability_pct": st.column_config.NumberColumn("Churn probability", format="%.1f%%"),
                "predicted_next_month_spend": st.column_config.NumberColumn("Predicted spend", format="$%.0f"),
                "revenue_at_risk": st.column_config.NumberColumn("Revenue at risk", format="$%.0f"),
            },
        )
        render_card_end()

    render_section_title("ðŸ§¬", "Customer Segments", "Segment economics and revenue exposure for targeted plays.")
    render_card_start()
    segment_risk["avg_churn_probability_pct"] = segment_risk["avg_churn_probability"] * 100
    st.dataframe(
        segment_risk.drop(columns=["avg_churn_probability"]),
        width="stretch",
        hide_index=True,
        column_config={
            "segment": "Segment",
            "customers": st.column_config.NumberColumn("Customers", format="%d"),
            "forecast_revenue": st.column_config.NumberColumn("Forecast revenue", format="$%.0f"),
            "revenue_at_risk": st.column_config.NumberColumn("Revenue at risk", format="$%.0f"),
            "avg_churn_probability_pct": st.column_config.NumberColumn("Avg churn", format="%.1f%%"),
        },
    )
    render_card_end()

    render_section_title("ðŸŽ¯", "Action Recommendations", "CRM-ready retention actions grouped by risk and business priority.")
    st.markdown('<div class="narrative-step">4. WHAT TO DO next</div>', unsafe_allow_html=True)
    render_card_start()
    render_action_insights(filtered)
    render_card_end()

    render_section_title("ðŸ“‹", "Customer Intelligence Table", "Top customers ranked by risk, revenue exposure, and action priority.")
    render_card_start()
    render_customer_intelligence_table(filtered)
    render_card_end()


def render_segments(result: PipelineResult, filtered: pd.DataFrame) -> None:
    """Render segment profiles and PCA customer map."""

    if render_empty_state(filtered):
        return

    render_section_title("ðŸ§¬", "Customer Segments", "Behavioral clusters for targeted growth and retention strategy.")
    profile = result.segmentation.segment_profile.reset_index()
    segment_counts = filtered.groupby("segment").size().rename("filtered_customers")
    profile = profile.merge(segment_counts, on="segment", how="left").fillna({"filtered_customers": 0})

    render_card_start()
    st.markdown("#### Segment profile")
    st.dataframe(
        profile,
        width="stretch",
        hide_index=True,
        column_config={"filtered_customers": st.column_config.NumberColumn("Customers in filter", format="%d")},
    )
    render_card_end()

    left, right = st.columns([1.25, 1])
    with left:
        render_card_start()
        st.markdown("#### Segment map")
        pca_data = result.segmentation.pca_coordinates.merge(
            filtered[["customer_id", "risk_band", "churn_probability"]],
            on="customer_id",
            how="inner",
        )
        pca_fig = px.scatter(
            pca_data,
            x="pca_1",
            y="pca_2",
            color="risk_band",
            size="churn_probability",
            color_discrete_map=RISK_COLORS,
            hover_data=["customer_id", "segment", "churn_probability"],
            title="Segment map by risk band",
        )
        st.plotly_chart(plotly_layout(pca_fig, height=430), width="stretch")
        st.caption(
            f"PCA is used for visualization only and explains "
            f"{result.segmentation.explained_variance_2d:.1%} of scaled feature variance."
        )
        render_card_end()

    with right:
        render_card_start()
        st.markdown("#### Segment economics")
        segment_economics = (
            filtered.groupby("segment", as_index=False)
            .agg(
                avg_total_spend=("total_spend", "mean"),
                avg_predicted_spend=("predicted_next_month_spend", "mean"),
                avg_churn_probability=("churn_probability", "mean"),
            )
            .sort_values("avg_predicted_spend", ascending=False)
        )
        segment_economics["avg_churn_probability_pct"] = segment_economics["avg_churn_probability"] * 100
        st.dataframe(
            segment_economics.drop(columns=["avg_churn_probability"]),
            width="stretch",
            hide_index=True,
            column_config={
                "avg_total_spend": st.column_config.NumberColumn("Avg historical spend", format="$%.0f"),
                "avg_predicted_spend": st.column_config.NumberColumn("Avg forecast spend", format="$%.0f"),
                "avg_churn_probability_pct": st.column_config.NumberColumn("Avg churn", format="%.1f%%"),
            },
        )
        render_card_end()


def render_retention(filtered: pd.DataFrame) -> None:
    """Render churn risk and retention-priority views."""

    if render_empty_state(filtered):
        return

    render_section_title("ðŸŽ¯", "Retention Command Center", "Identify who needs attention and which action should happen next.")
    render_card_start()
    st.markdown("#### Risk mix")
    render_risk_distribution(filtered)
    risk_mix = (
        filtered.groupby("risk_band", as_index=False)
        .agg(
            customers=("customer_id", "count"),
            forecast_revenue=("predicted_next_month_spend", "sum"),
            revenue_at_risk=("revenue_at_risk", "sum"),
        )
    )
    risk_mix["risk_band"] = pd.Categorical(risk_mix["risk_band"], categories=RISK_ORDER, ordered=True)
    risk_mix = risk_mix.sort_values("risk_band")
    st.plotly_chart(risk_bar_chart(risk_mix, "risk_band", "customers", "Retention risk mix"), width="stretch")
    render_card_end()

    render_section_title("ðŸ“‹", "Retention Priority Queue", "Top customers sorted by action priority and exposed revenue.")
    render_card_start()
    queue_columns = [
        "customer_id",
        "segment",
        "country",
        "risk_label",
        "churn_probability",
        "predicted_next_month_spend",
        "revenue_at_risk",
        "recommended_action",
    ]
    priority_queue = filtered.sort_values(
        ["action_priority", "revenue_at_risk", "churn_probability"],
        ascending=[True, False, False],
    ).copy()
    priority_queue["churn_probability_pct"] = priority_queue["churn_probability"] * 100
    queue_columns[queue_columns.index("churn_probability")] = "churn_probability_pct"
    st.dataframe(
        priority_queue[queue_columns].head(250),
        width="stretch",
        hide_index=True,
        column_config={
            "customer_id": "Customer ID",
            "segment": "Segment",
            "country": "Country",
            "risk_label": "Risk",
            "churn_probability_pct": st.column_config.ProgressColumn(
                "Churn probability",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "predicted_next_month_spend": st.column_config.NumberColumn(
                "Predicted spend",
                format="$%.2f",
            ),
            "revenue_at_risk": st.column_config.NumberColumn("Revenue at risk", format="$%.2f"),
            "recommended_action": "Recommended action",
        },
    )
    render_card_end()


def render_forecast(filtered: pd.DataFrame) -> None:
    """Render next-month spend forecast exploration."""

    if render_empty_state(filtered):
        return

    render_section_title("ðŸ’°", "Revenue Forecast", "Explore predicted next-month spend and business drivers.")
    left, right = st.columns(2)
    with left:
        render_card_start()
        st.markdown("#### Forecast revenue by segment")
        forecast_by_segment = (
            filtered.groupby("segment", as_index=False)["predicted_next_month_spend"]
            .sum()
            .sort_values("predicted_next_month_spend", ascending=False)
        )
        st.plotly_chart(
            segment_bar_chart(forecast_by_segment, "segment", "predicted_next_month_spend", "Forecast revenue by segment"),
            width="stretch",
        )
        render_card_end()

    with right:
        render_card_start()
        st.markdown("#### Spend drivers")
        driver_view = filtered[
            ["predicted_next_month_spend", "total_spend", "visits_per_month", "recency_days"]
        ].corr(numeric_only=True)[["predicted_next_month_spend"]].drop("predicted_next_month_spend")
        st.dataframe(
            driver_view.rename(columns={"predicted_next_month_spend": "correlation"}),
            width="stretch",
            column_config={"correlation": st.column_config.NumberColumn("Correlation", format="%.2f")},
        )
        render_card_end()

    render_card_start()
    st.markdown("#### Customer spend distribution")
    spend_bins = pd.cut(filtered["predicted_next_month_spend"], bins=10)
    spend_distribution = spend_bins.value_counts().sort_index().reset_index()
    spend_distribution.columns = ["predicted_spend_band", "customers"]
    spend_distribution["predicted_spend_band"] = spend_distribution["predicted_spend_band"].astype(str)
    spend_fig = px.bar(
        spend_distribution,
        x="predicted_spend_band",
        y="customers",
        title="Customer spend distribution",
        color="customers",
        color_continuous_scale=["#22d3ee", "#3b82f6"],
    )
    spend_fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(plotly_layout(spend_fig, height=360), width="stretch")
    render_card_end()


def render_customer_explorer(result: PipelineResult, dashboard: pd.DataFrame, filtered: pd.DataFrame) -> None:
    """Render customer table and single-customer lookup."""

    render_section_title("ðŸ“‹", "Customer Intelligence Table", "Search, sort, and inspect customer-level predictions.")
    render_card_start()
    table_columns = [
        "customer_id",
        "country",
        "age",
        "segment",
        "risk_label",
        "churn_probability",
        "predicted_next_month_spend",
        "total_spend",
        "recency_days",
        "recommended_action",
    ]
    source = (filtered if not filtered.empty else dashboard).copy()
    source["churn_probability_pct"] = source["churn_probability"] * 100
    table_columns[table_columns.index("churn_probability")] = "churn_probability_pct"
    st.dataframe(
        source.sort_values("revenue_at_risk", ascending=False)[table_columns],
        width="stretch",
        hide_index=True,
        column_config={
            "customer_id": "Customer ID",
            "country": "Country",
            "age": st.column_config.NumberColumn("Age", format="%d"),
            "segment": "Segment",
            "risk_label": "Risk",
            "churn_probability_pct": st.column_config.ProgressColumn(
                "Churn probability",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "predicted_next_month_spend": st.column_config.NumberColumn(
                "Predicted spend",
                format="$%.2f",
            ),
            "total_spend": st.column_config.NumberColumn("Historical spend", format="$%.2f"),
            "recency_days": st.column_config.NumberColumn("Recency days", format="%d"),
            "recommended_action": "Recommended action",
        },
    )
    render_card_end()

    render_section_title("ðŸ”Ž", "Customer Lookup", "Drill into an individual customer profile and recommended action.")
    render_card_start()
    customer_id = st.number_input(
        "Customer ID",
        min_value=int(dashboard["customer_id"].min()),
        max_value=int(dashboard["customer_id"].max()),
        value=int(dashboard["customer_id"].min()),
        step=1,
    )
    customer = dashboard.loc[dashboard["customer_id"] == customer_id].iloc[0]
    profile = result.customer_data.loc[result.customer_data["customer_id"] == customer_id].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Segment", int(customer["segment"]))
    col2.metric("Risk", str(customer["risk_label"]))
    col3.metric("Churn probability", format_percent(customer["churn_probability"]))
    col4.metric("Predicted spend", format_currency(customer["predicted_next_month_spend"]))

    detail = pd.DataFrame(
        [
            {
                "country": profile["country"],
                "age": int(profile["age"]),
                "income": format_currency(profile["income"]),
                "tenure_months": int(profile["tenure_months"]),
                "visits_per_month": int(profile["visits_per_month"]),
                "total_orders": int(profile["total_orders"]),
                "total_spend": format_currency(profile["total_spend"]),
                "recency_days": int(profile["recency_days"]),
                "discount_rate": f"{profile['discount_rate']:.1%}",
                "recommended_action": customer["recommended_action"],
            }
        ]
    )
    st.dataframe(detail, width="stretch", hide_index=True)
    render_card_end()


def render_manual_scorer(
    result: PipelineResult,
    medium_threshold: float,
    high_threshold: float,
    actions: dict[str, str],
) -> None:
    """Render a single-customer what-if scorer."""

    render_section_title("âœ¨", "Single Customer Scorer", "Tune customer inputs and get an immediate retention recommendation.")
    render_card_start()
    with st.form("manual_customer_scorer"):
        col1, col2, col3 = st.columns(3)
        with col1:
            income = st.number_input("Income", min_value=0.0, value=60000.0, step=1000.0)
            tenure_months = st.number_input("Tenure months", min_value=0, value=24, step=1)
            visits_per_month = st.number_input("Visits per month", min_value=0, value=6, step=1)
            recency_days = st.number_input("Recency days", min_value=0, value=30, step=1)
        with col2:
            total_orders = st.number_input("Total orders", min_value=0, value=8, step=1)
            total_spend = st.number_input("Historical total spend", min_value=0.0, value=650.0, step=25.0)
            average_order_value = st.number_input("Average order value", min_value=0.0, value=80.0, step=5.0)
            order_value_std = st.number_input("Order value standard deviation", min_value=0.0, value=25.0, step=5.0)
        with col3:
            discount_rate = st.slider("Discount usage rate", min_value=0.0, max_value=1.0, value=0.30, step=0.01)
            orders_per_active_month = st.number_input(
                "Orders per active month",
                min_value=0.0,
                value=1.2,
                step=0.1,
            )
            spend_per_visit = st.number_input("Spend per visit", min_value=0.0, value=100.0, step=10.0)

        submitted = st.form_submit_button("Score customer", width="stretch")

    if not submitted:
        render_card_end()
        return

    customer = pd.DataFrame(
        [
            {
                "income": income,
                "tenure_months": tenure_months,
                "visits_per_month": visits_per_month,
                "total_orders": total_orders,
                "total_spend": total_spend,
                "average_order_value": average_order_value,
                "discount_rate": discount_rate,
                "recency_days": recency_days,
                "orders_per_active_month": orders_per_active_month,
                "spend_per_visit": spend_per_visit,
                "order_value_std": order_value_std,
            }
        ]
    )
    scored = score_customer_features(result, customer, medium_threshold, high_threshold, actions).iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Segment", int(scored["segment"]))
    col2.metric("Risk", str(scored["risk_label"]))
    col3.metric("Churn probability", format_percent(scored["churn_probability"]))
    col4.metric("Predicted spend", format_currency(scored["predicted_next_month_spend"]))
    st.markdown(
        f'<div class="hero-status">Recommended action: {str(scored["recommended_action"]).title()}</div>',
        unsafe_allow_html=True,
    )
    render_card_end()


def select_source_column(
    uploaded_columns: list[str],
    target_column: str,
    optional: bool = False,
) -> str | None:
    """Render a compact source-column selector with best-effort defaults."""

    choices = ["-- not provided --"] + uploaded_columns if optional else uploaded_columns
    normalized_lookup = {column.lower().strip(): column for column in uploaded_columns}
    default_column = normalized_lookup.get(target_column.lower())
    index = choices.index(default_column) if default_column in choices else 0
    selected = st.selectbox(target_column, choices, index=index)
    if selected == "-- not provided --":
        return None
    return selected


def map_uploaded_columns(uploaded: pd.DataFrame) -> pd.DataFrame | None:
    """Let companies map their own CSV column names onto the model schema."""

    mapped = pd.DataFrame(index=uploaded.index)
    uploaded_columns = uploaded.columns.tolist()

    with st.expander("Column mapping", expanded=True):
        customer_id_column = select_source_column(uploaded_columns, "customer_id", optional=True)
        if customer_id_column:
            mapped["customer_id"] = uploaded[customer_id_column]

        col1, col2, col3 = st.columns(3)
        for index, feature in enumerate(SCORING_FEATURES):
            with [col1, col2, col3][index % 3]:
                source_column = select_source_column(uploaded_columns, feature)
            mapped[feature] = uploaded[source_column]

    mapped[SCORING_FEATURES] = mapped[SCORING_FEATURES].apply(pd.to_numeric, errors="coerce")
    invalid_columns = mapped[SCORING_FEATURES].columns[mapped[SCORING_FEATURES].isna().any()].tolist()
    if invalid_columns:
        render_alert("These mapped columns contain blank or non-numeric values: " + ", ".join(invalid_columns))
        return None
    return mapped


def render_upload_scorer(
    result: PipelineResult,
    medium_threshold: float,
    high_threshold: float,
    actions: dict[str, str],
) -> None:
    """Render CSV upload scoring for user-provided customer data."""

    render_section_title("ðŸ“‚", "Bulk CSV Scorer", "Upload company customer data, map columns, score, and export CRM-ready actions.")
    render_card_start()
    template = pd.DataFrame(
        [
            {
                "customer_id": 1,
                "income": 60000,
                "tenure_months": 24,
                "visits_per_month": 6,
                "total_orders": 8,
                "total_spend": 650,
                "average_order_value": 80,
                "discount_rate": 0.30,
                "recency_days": 30,
                "orders_per_active_month": 1.2,
                "spend_per_visit": 100,
                "order_value_std": 25,
            }
        ]
    )
    st.download_button(
        "Download CSV template",
        data=template.to_csv(index=False),
        file_name="customer_scoring_template.csv",
        mime="text/csv",
        width="stretch",
    )

    uploaded_file = st.file_uploader("Upload customer feature CSV", type=["csv"])
    if uploaded_file is None:
        st.markdown(
            '<div class="hero-status">Upload a CSV with the required feature columns to score customers in bulk.</div>',
            unsafe_allow_html=True,
        )
        render_card_end()
        return

    uploaded = pd.read_csv(uploaded_file)
    mapped_upload = map_uploaded_columns(uploaded)
    if mapped_upload is None:
        render_card_end()
        return

    scored = score_customer_features(result, mapped_upload, medium_threshold, high_threshold, actions)
    display_columns = [
        "customer_id",
        "segment",
        "risk_label",
        "churn_probability",
        "predicted_next_month_spend",
        "revenue_at_risk",
        "recommended_action",
    ]
    scored_display = scored.copy()
    scored_display["churn_probability_pct"] = scored_display["churn_probability"] * 100
    display_columns[display_columns.index("churn_probability")] = "churn_probability_pct"

    render_kpis(scored_display, scored_display)
    st.dataframe(
        scored_display[display_columns].sort_values("revenue_at_risk", ascending=False),
        width="stretch",
        hide_index=True,
        column_config={
            "customer_id": "Customer ID",
            "segment": "Segment",
            "risk_label": "Risk",
            "churn_probability_pct": st.column_config.ProgressColumn(
                "Churn probability",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "predicted_next_month_spend": st.column_config.NumberColumn("Predicted spend", format="$%.2f"),
            "revenue_at_risk": st.column_config.NumberColumn("Revenue at risk", format="$%.2f"),
            "recommended_action": "Recommended action",
        },
    )
    st.download_button(
        "Download scored results",
        data=scored.to_csv(index=False),
        file_name="customer_scored_results.csv",
        mime="text/csv",
        width="stretch",
    )
    render_card_end()


def render_data_contract() -> None:
    """Show the company-facing feature contract for production data onboarding."""

    schema = pd.DataFrame(
        [
            {"field": "income", "meaning": "Customer income or value proxy", "typical_source": "CRM/profile"},
            {"field": "tenure_months", "meaning": "Months since signup", "typical_source": "CRM/subscription"},
            {"field": "visits_per_month", "meaning": "Recent monthly visits or sessions", "typical_source": "Web/app analytics"},
            {"field": "total_orders", "meaning": "Lifetime completed orders", "typical_source": "Orders table"},
            {"field": "total_spend", "meaning": "Lifetime net spend", "typical_source": "Orders/payments"},
            {"field": "average_order_value", "meaning": "Average net order amount", "typical_source": "Orders table"},
            {"field": "discount_rate", "meaning": "Share of orders with a discount, 0 to 1", "typical_source": "Promotions/orders"},
            {"field": "recency_days", "meaning": "Days since last order", "typical_source": "Orders table"},
            {"field": "orders_per_active_month", "meaning": "Order frequency while active", "typical_source": "Derived metric"},
            {"field": "spend_per_visit", "meaning": "Lifetime spend divided by monthly visits", "typical_source": "Derived metric"},
            {"field": "order_value_std", "meaning": "Variation in order amounts", "typical_source": "Orders table"},
        ]
    )
    render_section_title("ðŸ§¾", "Company Data Contract", "The feature contract needed to use the platform with production data.")
    render_card_start()
    st.dataframe(schema, width="stretch", hide_index=True)

    st.markdown("#### Example feature formulas")
    formulas = pd.DataFrame(
        [
            {"metric": "average_order_value", "formula": "total_spend / total_orders"},
            {"metric": "discount_rate", "formula": "discounted_orders / total_orders"},
            {"metric": "recency_days", "formula": "scoring_date - last_order_date"},
            {"metric": "orders_per_active_month", "formula": "total_orders / active_months"},
            {"metric": "spend_per_visit", "formula": "total_spend / max(visits_per_month, 1)"},
            {"metric": "order_value_std", "formula": "standard deviation of historical order amount"},
        ]
    )
    st.dataframe(formulas, width="stretch", hide_index=True)
    render_card_end()


def render_user_scoring(
    result: PipelineResult,
    medium_threshold: float,
    high_threshold: float,
    actions: dict[str, str],
) -> None:
    """Render user-controlled scoring workflows."""

    st.markdown(
        '<div class="hero-status">Use trained intelligence models to score custom values or uploaded customer data.</div>',
        unsafe_allow_html=True,
    )
    manual_tab, upload_tab, contract_tab = st.tabs(["Manual Entry", "CSV Upload", "Data Contract"])
    with manual_tab:
        render_manual_scorer(result, medium_threshold, high_threshold, actions)
    with upload_tab:
        render_upload_scorer(result, medium_threshold, high_threshold, actions)
    with contract_tab:
        render_data_contract()


def render_model_performance(result: PipelineResult) -> None:
    """Render compact model diagnostics."""

    churn_metrics = pd.DataFrame(
        [
            {"model": "Baseline Logistic Regression", **result.churn.baseline_metrics},
            {"model": "Gradient Boosting", **result.churn.gradient_boosting_metrics},
            {"model": "Selected Model", **result.churn.selected_metrics},
        ]
    ).drop(columns=["confusion_matrix"])
    spend_metrics = pd.DataFrame(
        [
            {"model": "Baseline Linear Regression", **result.spend.baseline_metrics},
            {"model": "Gradient Boosting Regressor", **result.spend.champion_metrics},
        ]
    )

    render_section_title("ðŸ§ ", "Model Performance", "Diagnostics for churn classification and spend forecasting.")
    left, right = st.columns(2)
    with left:
        render_card_start()
        st.markdown("#### Churn model")
        st.dataframe(churn_metrics, width="stretch", hide_index=True)
        render_card_end()
    with right:
        render_card_start()
        st.markdown("#### Spend model")
        st.dataframe(spend_metrics, width="stretch", hide_index=True)
        render_card_end()

    st.markdown(
        '<div class="hero-status">Metrics are computed from synthetic case-study labels. Use diagnostics to compare models, not as proof of real production performance.</div>',
        unsafe_allow_html=True,
    )


def main() -> None:
    """Render the Streamlit dashboard."""

    inject_global_css()
    with st.status("Building customer intelligence pipeline...", expanded=False) as status:
        st.write("Running predictive models...")
        st.write("Generating insights...")
        result = load_pipeline_data()
        status.update(label="Pipeline ready", state="complete")

    dashboard = build_dashboard_table(result)
    medium_threshold, high_threshold, actions = render_business_rules()
    dashboard = apply_business_rules(dashboard, medium_threshold, high_threshold, actions)
    filtered = apply_sidebar_filters(dashboard)

    render_hero()

    tabs = st.tabs(["Executive", "Segments", "Retention", "Forecast", "Customers", "Score New Data", "Models"])
    with tabs[0]:
        render_executive_summary(dashboard, filtered)
    with tabs[1]:
        render_segments(result, filtered)
    with tabs[2]:
        render_retention(filtered)
    with tabs[3]:
        render_forecast(filtered)
    with tabs[4]:
        render_customer_explorer(result, dashboard, filtered)
    with tabs[5]:
        render_user_scoring(result, medium_threshold, high_threshold, actions)
    with tabs[6]:
        render_model_performance(result)

    render_footer()


if __name__ == "__main__":
    main()
