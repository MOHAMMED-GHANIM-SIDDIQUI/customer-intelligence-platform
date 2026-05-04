"""Streamlit dashboard for the customer analytics case study."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from customer_analytics.config import CHURN_FEATURES, SEGMENT_FEATURES, SPEND_FEATURES, ProjectConfig  # noqa: E402
from customer_analytics.pipeline import PipelineResult, run_pipeline  # noqa: E402


RISK_ORDER = ["low", "medium", "high"]
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
    padding: 2.2rem 2.1rem 1.9rem;
    margin-bottom: 1.15rem;
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
    font-size: clamp(2rem, 4vw, 4.4rem);
    line-height: 1.02;
    font-weight: 900;
    letter-spacing: 0;
    background: linear-gradient(90deg, #f8fafc, #93c5fd 42%, #22d3ee 88%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    max-width: 720px;
    margin: 0.85rem 0 0;
    color: #bfdbfe;
    font-size: 1.08rem;
}

.hero-status {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    margin-top: 1.2rem;
    padding: 0.54rem 0.78rem;
    border: 1px solid rgba(34, 211, 238, 0.28);
    border-radius: 999px;
    color: #cffafe;
    background: rgba(8, 47, 73, 0.42);
    font-size: 0.82rem;
    font-weight: 700;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
    margin: 1rem 0 1.2rem;
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
    padding: 0.95rem;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: rgba(15, 23, 42, 0.58);
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
    gap: 0.4rem;
    border-bottom: 1px solid rgba(148, 163, 184, 0.14);
}

[data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    color: #cbd5e1;
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
    .kpi-grid,
    .metric-row {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .hero {
        padding: 1.45rem;
    }
}

@media (max-width: 640px) {
    .kpi-grid,
    .metric-row {
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


@st.cache_resource(show_spinner="📊 Building customer intelligence pipeline...")
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


def inject_global_css() -> None:
    """Apply the enterprise dashboard visual system."""

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_hero() -> None:
    """Render the executive product hero."""

    st.markdown(
        """
        <section class="hero">
            <div class="section-eyebrow">Enterprise Analytics Suite</div>
            <h1>📊 Customer Intelligence Platform</h1>
            <p>Predict churn, optimize retention, maximize revenue</p>
            <div class="hero-status">● Live intelligence workspace · Segments · Churn · Revenue · Actions</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Render a minimal product footer."""

    st.markdown(
        '<div class="footer">Customer Intelligence Platform • Built for Data-Driven Decisions</div>',
        unsafe_allow_html=True,
    )


def render_section_title(icon: str, title: str, subtitle: str = "", badge: str = "") -> None:
    """Render a styled section title."""

    badge_html = f'<span class="pill">{badge}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="section-title">
            <div>
                <div class="section-eyebrow">{icon} Insight Module</div>
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
            <strong>❌ Data or pipeline error</strong><br />
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_card_start() -> None:
    """Open a styled card wrapper for native Streamlit components."""

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)


def render_card_end() -> None:
    """Close a styled card wrapper."""

    st.markdown("</div>", unsafe_allow_html=True)


def trend_badge(current: float, benchmark: float, inverse: bool = False) -> tuple[str, str]:
    """Return a compact trend indicator for KPI cards."""

    if pd.isna(current) or pd.isna(benchmark) or benchmark == 0:
        return "trend-neutral", "→ benchmark unavailable"
    delta = (current - benchmark) / abs(benchmark)
    is_positive = delta >= 0
    if inverse:
        is_positive = not is_positive
    css_class = "trend-up" if is_positive else "trend-down"
    arrow = "↑" if delta >= 0 else "↓"
    return css_class, f"{arrow} {abs(delta):.1%} vs full base"


def render_kpi_card(label: str, value: str, trend: str, trend_class: str, tooltip: str) -> str:
    """Return a single KPI card as HTML."""

    return f"""
    <div class="kpi-card" title="{tooltip}">
        <div class="kpi-label"><span>{label}</span><span>ⓘ</span></div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-trend {trend_class}">{trend}</div>
    </div>
    """


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
        <div class="control-label">⚙️ Business Rules</div>
        """,
        unsafe_allow_html=True,
    )
    if st.sidebar.button("✨ Run Demo Pipeline", use_container_width=True):
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
        <div class="control-label">📂 Data Status</div>
        <div class="mini-card">
            <div class="label">Pipeline</div>
            <div class="value">Loaded</div>
        </div>
        <div class="control-label">📊 Filters</div>
        """,
        unsafe_allow_html=True,
    )

    selected_segments = st.sidebar.multiselect(
        "Segments",
        options=sorted(dashboard["segment"].unique()),
        default=sorted(dashboard["segment"].unique()),
    )
    selected_risk_bands = st.sidebar.multiselect(
        "Risk bands",
        options=RISK_ORDER,
        default=RISK_ORDER,
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
        value=(min_spend, max_spend),
        step=10.0,
    )

    if not selected_segments or not selected_risk_bands or not selected_countries:
        st.sidebar.markdown(
            '<div class="alert-card">❌ Select at least one value in each filter.</div>',
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

    churn_class, churn_trend = trend_badge(churn_rate, base_churn, inverse=True)
    revenue_class, revenue_trend = trend_badge(revenue_at_risk, base_revenue_at_risk, inverse=True)
    value_class, value_trend = trend_badge(avg_customer_value, base_customer_value)
    customer_class = "trend-neutral"
    customer_trend = f"→ {total_customers / max(len(dashboard), 1):.1%} of scored base"

    cards = [
        render_kpi_card(
            "Total Customers",
            f"{total_customers:,}",
            customer_trend,
            customer_class,
            "Number of customers included after the active filters.",
        ),
        render_kpi_card(
            "Churn Rate",
            format_percent(churn_rate),
            churn_trend,
            churn_class,
            "Average predicted churn probability across selected customers.",
        ),
        render_kpi_card(
            "Revenue at Risk",
            format_currency(revenue_at_risk),
            revenue_trend,
            revenue_class,
            "Predicted next-month revenue weighted by churn probability.",
        ),
        render_kpi_card(
            "Avg Customer Value",
            format_currency(avg_customer_value),
            value_trend,
            value_class,
            "Average historical customer spend for the selected population.",
        ),
    ]
    st.markdown(f'<div class="kpi-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


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
    cards = []
    for risk in RISK_ORDER:
        css = f"risk-{risk}"
        cards.append(
            f"""
            <div class="mini-card">
                <div class="label">{RISK_LABELS[risk]} Risk</div>
                <div class="value {css}">{int(counts[risk]):,}</div>
                <div class="kpi-trend">{counts[risk] / total:.1%} of selected customers</div>
            </div>
            """
        )
    st.markdown(f'<div class="metric-row">{"".join(cards)}</div>', unsafe_allow_html=True)
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
    st.dataframe(styled, use_container_width=True, hide_index=True)


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
        use_container_width=True,
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

    render_section_title("📊", "Executive KPI Strip", "A concise readout of customer health and revenue exposure.")
    render_kpis(dashboard, filtered)
    if render_empty_state(filtered):
        return

    render_section_title("📈", "Risk Distribution", "Low, medium, and high-risk customer composition.", "Live risk mix")
    render_card_start()
    render_risk_distribution(filtered)
    risk_mix = (
        filtered.groupby("risk_band", as_index=False)
        .agg(customers=("customer_id", "count"), revenue_at_risk=("revenue_at_risk", "sum"))
    )
    risk_mix["risk_band"] = pd.Categorical(risk_mix["risk_band"], categories=RISK_ORDER, ordered=True)
    risk_mix = risk_mix.sort_values("risk_band")
    st.bar_chart(risk_mix, x="risk_band", y="customers", use_container_width=True)
    render_card_end()

    render_section_title("💰", "Revenue at Risk Breakdown", "Prioritize the customers and segments with the most exposed revenue.")
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
        st.bar_chart(segment_risk, x="segment", y="revenue_at_risk", use_container_width=True)
        render_card_end()
    with right:
        render_card_start()
        st.markdown("#### Top 10 risky customers")
        top_risky = filtered.sort_values("revenue_at_risk", ascending=False).head(10)
        st.dataframe(
            top_risky[
                [
                    "customer_id",
                    "risk_label",
                    "churn_probability",
                    "predicted_next_month_spend",
                    "revenue_at_risk",
                ]
            ],
            use_container_width=True,
            hide_index=True,
            column_config={
                "customer_id": "Customer ID",
                "risk_label": "Risk",
                "churn_probability": st.column_config.NumberColumn("Churn probability", format="%.1%"),
                "predicted_next_month_spend": st.column_config.NumberColumn("Predicted spend", format="$%.0f"),
                "revenue_at_risk": st.column_config.NumberColumn("Revenue at risk", format="$%.0f"),
            },
        )
        render_card_end()

    render_section_title("🧬", "Customer Segments", "Segment economics and revenue exposure for targeted plays.")
    render_card_start()
    st.dataframe(
        segment_risk,
        use_container_width=True,
        hide_index=True,
        column_config={
            "segment": "Segment",
            "customers": st.column_config.NumberColumn("Customers", format="%d"),
            "forecast_revenue": st.column_config.NumberColumn("Forecast revenue", format="$%.0f"),
            "revenue_at_risk": st.column_config.NumberColumn("Revenue at risk", format="$%.0f"),
            "avg_churn_probability": st.column_config.NumberColumn("Avg churn", format="%.1%"),
        },
    )
    render_card_end()

    render_section_title("🎯", "Action Recommendations", "CRM-ready retention actions grouped by risk and business priority.")
    render_card_start()
    render_action_insights(filtered)
    render_card_end()

    render_section_title("📋", "Customer Intelligence Table", "Top customers ranked by risk, revenue exposure, and action priority.")
    render_card_start()
    render_customer_intelligence_table(filtered)
    render_card_end()


def render_segments(result: PipelineResult, filtered: pd.DataFrame) -> None:
    """Render segment profiles and PCA customer map."""

    if render_empty_state(filtered):
        return

    render_section_title("🧬", "Customer Segments", "Behavioral clusters for targeted growth and retention strategy.")
    profile = result.segmentation.segment_profile.reset_index()
    segment_counts = filtered.groupby("segment").size().rename("filtered_customers")
    profile = profile.merge(segment_counts, on="segment", how="left").fillna({"filtered_customers": 0})

    render_card_start()
    st.markdown("#### Segment profile")
    st.dataframe(
        profile,
        use_container_width=True,
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
        st.scatter_chart(
            pca_data,
            x="pca_1",
            y="pca_2",
            color="segment",
            size="churn_probability",
            use_container_width=True,
        )
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
        st.dataframe(
            segment_economics,
            use_container_width=True,
            hide_index=True,
            column_config={
                "avg_total_spend": st.column_config.NumberColumn("Avg historical spend", format="$%.0f"),
                "avg_predicted_spend": st.column_config.NumberColumn("Avg forecast spend", format="$%.0f"),
                "avg_churn_probability": st.column_config.NumberColumn("Avg churn", format="%.1%"),
            },
        )
        render_card_end()


def render_retention(filtered: pd.DataFrame) -> None:
    """Render churn risk and retention-priority views."""

    if render_empty_state(filtered):
        return

    render_section_title("🎯", "Retention Command Center", "Identify who needs attention and which action should happen next.")
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
    st.bar_chart(risk_mix, x="risk_band", y="customers", use_container_width=True)
    render_card_end()

    render_section_title("📋", "Retention Priority Queue", "Top customers sorted by action priority and exposed revenue.")
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
        use_container_width=True,
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

    render_section_title("💰", "Revenue Forecast", "Explore predicted next-month spend and business drivers.")
    left, right = st.columns(2)
    with left:
        render_card_start()
        st.markdown("#### Forecast revenue by segment")
        forecast_by_segment = (
            filtered.groupby("segment", as_index=False)["predicted_next_month_spend"]
            .sum()
            .sort_values("predicted_next_month_spend", ascending=False)
        )
        st.bar_chart(
            forecast_by_segment,
            x="segment",
            y="predicted_next_month_spend",
            use_container_width=True,
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
            use_container_width=True,
            column_config={"correlation": st.column_config.NumberColumn("Correlation", format="%.2f")},
        )
        render_card_end()

    render_card_start()
    st.markdown("#### Customer spend distribution")
    spend_bins = pd.cut(filtered["predicted_next_month_spend"], bins=10)
    spend_distribution = spend_bins.value_counts().sort_index().reset_index()
    spend_distribution.columns = ["predicted_spend_band", "customers"]
    spend_distribution["predicted_spend_band"] = spend_distribution["predicted_spend_band"].astype(str)
    st.bar_chart(spend_distribution, x="predicted_spend_band", y="customers", use_container_width=True)
    render_card_end()


def render_customer_explorer(result: PipelineResult, dashboard: pd.DataFrame, filtered: pd.DataFrame) -> None:
    """Render customer table and single-customer lookup."""

    render_section_title("📋", "Customer Intelligence Table", "Search, sort, and inspect customer-level predictions.")
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
        use_container_width=True,
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

    render_section_title("🔎", "Customer Lookup", "Drill into an individual customer profile and recommended action.")
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
    st.dataframe(detail, use_container_width=True, hide_index=True)
    render_card_end()


def render_manual_scorer(
    result: PipelineResult,
    medium_threshold: float,
    high_threshold: float,
    actions: dict[str, str],
) -> None:
    """Render a single-customer what-if scorer."""

    render_section_title("✨", "Single Customer Scorer", "Tune customer inputs and get an immediate retention recommendation.")
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

        submitted = st.form_submit_button("Score customer", use_container_width=True)

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

    render_section_title("📂", "Bulk CSV Scorer", "Upload company customer data, map columns, score, and export CRM-ready actions.")
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
        use_container_width=True,
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
        use_container_width=True,
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
        use_container_width=True,
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
    render_section_title("🧾", "Company Data Contract", "The feature contract needed to use the platform with production data.")
    render_card_start()
    st.dataframe(schema, use_container_width=True, hide_index=True)

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
    st.dataframe(formulas, use_container_width=True, hide_index=True)
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

    render_section_title("🧠", "Model Performance", "Diagnostics for churn classification and spend forecasting.")
    left, right = st.columns(2)
    with left:
        render_card_start()
        st.markdown("#### Churn model")
        st.dataframe(churn_metrics, use_container_width=True, hide_index=True)
        render_card_end()
    with right:
        render_card_start()
        st.markdown("#### Spend model")
        st.dataframe(spend_metrics, use_container_width=True, hide_index=True)
        render_card_end()

    st.markdown(
        '<div class="hero-status">Metrics are computed from synthetic case-study labels. Use diagnostics to compare models, not as proof of real production performance.</div>',
        unsafe_allow_html=True,
    )


def main() -> None:
    """Render the Streamlit dashboard."""

    inject_global_css()
    with st.status("📊 Building customer intelligence pipeline...", expanded=False) as status:
        st.write("🧠 Running predictive models...")
        st.write("⚡ Generating insights...")
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
