from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Configure the browser page before displaying anything.
st.set_page_config(
    page_title="GitHub Repository Momentum Dashboard",
    page_icon="📈",
    layout="wide",
)

# -------------------------------------------------------------------
# Page-wide visual design foundation
# -------------------------------------------------------------------

st.markdown(
    """
    <style>
        /* -----------------------------------------------------------
           Core design tokens
           ----------------------------------------------------------- */

        :root {
            --momentum-ink: #0F172A;
            --momentum-muted: #64748B;
            --momentum-soft: #94A3B8;
            --momentum-border: #E2E8F0;
            --momentum-surface: #FFFFFF;
            --momentum-canvas: #F6F8FC;
            --momentum-indigo: #6366F1;
            --momentum-violet: #8B5CF6;
            --momentum-cyan: #22D3EE;
            --momentum-teal: #14B8A6;
            --momentum-gold: #EAB308;
        }


        /* -----------------------------------------------------------
           Application canvas
           ----------------------------------------------------------- */

        html,
        body,
        [class*="css"] {
            font-family:
                Inter,
                ui-sans-serif,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }

        .stApp {
            color: var(--momentum-ink);
            background:
                radial-gradient(
                    circle at 82% 3%,
                    rgba(99, 102, 241, 0.08),
                    transparent 24rem
                ),
                radial-gradient(
                    circle at 18% 14%,
                    rgba(34, 211, 238, 0.055),
                    transparent 22rem
                ),
                var(--momentum-canvas);
        }

        [data-testid="stAppViewContainer"] {
            background: transparent;
        }

        [data-testid="stHeader"] {
            background: rgba(246, 248, 252, 0.82);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(226, 232, 240, 0.72);
        }


        /* -----------------------------------------------------------
           Main content width and spacing
           ----------------------------------------------------------- */

        .main .block-container {
            max-width: 1440px;
            padding-top: 2.4rem;
            padding-right: 2.4rem;
            padding-bottom: 4rem;
            padding-left: 2.4rem;
        }

        [data-testid="stVerticalBlock"] {
            gap: 0.85rem;
        }


        /* -----------------------------------------------------------
           Typography
           ----------------------------------------------------------- */

        h1,
        h2,
        h3 {
            color: var(--momentum-ink);
            letter-spacing: -0.025em;
        }

        h1 {
            font-size: clamp(2.15rem, 3vw, 3.35rem);
            font-weight: 760;
            line-height: 1.04;
            margin-bottom: 0.7rem;
        }

        h2 {
            font-size: clamp(1.45rem, 2vw, 1.9rem);
            font-weight: 720;
            line-height: 1.18;
            margin-top: 0.25rem;
        }

        h3 {
            font-size: 1.15rem;
            font-weight: 700;
            line-height: 1.3;
        }

        p,
        li {
            color: #334155;
            line-height: 1.65;
        }

        strong {
            color: var(--momentum-ink);
            font-weight: 700;
        }

        [data-testid="stCaptionContainer"] {
            color: var(--momentum-muted);
            line-height: 1.55;
        }


        /* -----------------------------------------------------------
           Dividers
           ----------------------------------------------------------- */

        hr {
            margin-top: 1.6rem;
            margin-bottom: 1.6rem;
            border: none;
            border-top: 1px solid var(--momentum-border);
        }


        /* -----------------------------------------------------------
           Sidebar foundation
           ----------------------------------------------------------- */

        [data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    rgba(255, 255, 255, 0.98) 0%,
                    rgba(248, 250, 252, 0.98) 100%
                );
            border-right: 1px solid var(--momentum-border);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.75rem;
        }

        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            letter-spacing: -0.015em;
        }

        [data-testid="stSidebar"] label {
            color: #334155;
            font-weight: 620;
        }


        /* -----------------------------------------------------------
           Form controls
           ----------------------------------------------------------- */

        [data-baseweb="select"] > div {
            min-height: 2.75rem;
            background: rgba(255, 255, 255, 0.96);
            border-color: var(--momentum-border);
            border-radius: 10px;
            transition:
                border-color 160ms ease,
                box-shadow 160ms ease;
        }

        [data-baseweb="select"] > div:hover {
            border-color: #A5B4FC;
        }

        [data-baseweb="select"] > div:focus-within {
            border-color: var(--momentum-indigo);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.11);
        }


        /* -----------------------------------------------------------
           Accessible keyboard focus
           ----------------------------------------------------------- */

        button:focus-visible,
        a:focus-visible,
        input:focus-visible {
            outline: 3px solid rgba(99, 102, 241, 0.32);
            outline-offset: 2px;
        }


        /* -----------------------------------------------------------
           Responsive layout
           ----------------------------------------------------------- */

        @media (max-width: 900px) {
            .main .block-container {
                padding-top: 1.5rem;
                padding-right: 1.1rem;
                padding-left: 1.1rem;
            }

            h1 {
                font-size: 2.1rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# Hero and KPI presentation
# -------------------------------------------------------------------

st.html(
    """
    <style>
        /* -----------------------------------------------------------
           Momentum Signal Brief hero
           ----------------------------------------------------------- */

        .momentum-hero {
            position: relative;
            overflow: hidden;
            margin-bottom: 1.7rem;
            padding: clamp(1.5rem, 3vw, 2.5rem);
            background:
                linear-gradient(
                    135deg,
                    rgba(255, 255, 255, 0.98) 0%,
                    rgba(245, 247, 255, 0.98) 58%,
                    rgba(238, 252, 255, 0.96) 100%
                );
            border: 1px solid rgba(203, 213, 225, 0.88);
            border-radius: 24px;
            box-shadow:
                0 18px 45px rgba(15, 23, 42, 0.07),
                0 2px 8px rgba(15, 23, 42, 0.035);
        }

        .momentum-hero::before {
            content: "";
            position: absolute;
            inset: 0;
            background-image:
                linear-gradient(
                    rgba(99, 102, 241, 0.055) 1px,
                    transparent 1px
                ),
                linear-gradient(
                    90deg,
                    rgba(99, 102, 241, 0.055) 1px,
                    transparent 1px
                );
            background-size: 34px 34px;
            mask-image:
                linear-gradient(
                    90deg,
                    transparent 8%,
                    rgba(0, 0, 0, 0.3) 58%,
                    rgba(0, 0, 0, 0.8) 100%
                );
            pointer-events: none;
        }

        .momentum-hero::after {
            content: "";
            position: absolute;
            width: 320px;
            height: 320px;
            top: -210px;
            right: -80px;
            border: 1px solid rgba(99, 102, 241, 0.17);
            border-radius: 50%;
            box-shadow:
                0 0 0 48px rgba(99, 102, 241, 0.035),
                0 0 0 96px rgba(34, 211, 238, 0.025);
            pointer-events: none;
        }

        .momentum-hero-content {
            position: relative;
            z-index: 1;
        }

        .momentum-hero-topline {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.35rem;
        }

        .momentum-eyebrow {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            color: #4F46E5;
            font-size: 0.73rem;
            font-weight: 760;
            letter-spacing: 0.13em;
            text-transform: uppercase;
        }

        .momentum-eyebrow-dot {
            width: 8px;
            height: 8px;
            background: var(--momentum-cyan);
            border: 2px solid rgba(34, 211, 238, 0.22);
            border-radius: 50%;
            box-shadow: 0 0 0 5px rgba(34, 211, 238, 0.1);
        }

        .momentum-status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.46rem 0.72rem;
            color: #475569;
            background: rgba(255, 255, 255, 0.75);
            border: 1px solid rgba(203, 213, 225, 0.92);
            border-radius: 999px;
            font-size: 0.73rem;
            font-weight: 650;
            white-space: nowrap;
        }

        .momentum-status-badge::before {
            content: "";
            width: 7px;
            height: 7px;
            background: var(--momentum-indigo);
            border-radius: 50%;
        }

        .momentum-hero-main {
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(260px, 0.36fr);
            align-items: end;
            gap: 2.5rem;
        }

        .momentum-hero-title {
            max-width: 850px;
            margin: 0;
            color: var(--momentum-ink);
            font-size: clamp(2.25rem, 4vw, 4rem);
            font-weight: 780;
            line-height: 1.02;
            letter-spacing: -0.045em;
        }

        .momentum-hero-title span {
            color: var(--momentum-indigo);
        }

        .momentum-hero-description {
            max-width: 780px;
            margin: 1rem 0 0;
            color: #475569;
            font-size: clamp(0.97rem, 1.2vw, 1.08rem);
            line-height: 1.65;
        }

        .momentum-lens {
            padding: 1rem 1.05rem;
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(203, 213, 225, 0.86);
            border-radius: 15px;
        }

        .momentum-lens-label {
            display: block;
            margin-bottom: 0.35rem;
            color: #64748B;
            font-size: 0.66rem;
            font-weight: 750;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .momentum-lens strong {
            display: block;
            color: var(--momentum-ink);
            font-size: 0.93rem;
            line-height: 1.45;
        }

        .momentum-signal-track {
            display: flex;
            align-items: center;
            margin-top: 0.9rem;
        }

        .momentum-signal-line {
            height: 2px;
            flex: 1;
            background:
                linear-gradient(
                    90deg,
                    var(--momentum-indigo),
                    var(--momentum-violet),
                    var(--momentum-cyan)
                );
        }

        .momentum-signal-node {
            width: 9px;
            height: 9px;
            margin: 0 -1px;
            background: #FFFFFF;
            border: 2px solid var(--momentum-indigo);
            border-radius: 50%;
            z-index: 1;
        }

        .momentum-signal-node:last-child {
            border-color: var(--momentum-cyan);
        }

        .momentum-hero-note {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            margin-top: 1.55rem;
            padding-top: 1.1rem;
            color: #475569;
            border-top: 1px solid rgba(203, 213, 225, 0.82);
            font-size: 0.82rem;
            line-height: 1.55;
        }

        .momentum-note-mark {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex: 0 0 22px;
            width: 22px;
            height: 22px;
            color: #4F46E5;
            background: rgba(99, 102, 241, 0.1);
            border-radius: 7px;
            font-size: 0.78rem;
            font-weight: 800;
        }


        /* -----------------------------------------------------------
           KPI section
           ----------------------------------------------------------- */

        .momentum-section-intro {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 1rem;
            margin: 0.3rem 0 0.85rem;
        }

        .momentum-section-kicker {
            color: #4F46E5;
            font-size: 0.69rem;
            font-weight: 760;
            letter-spacing: 0.13em;
            text-transform: uppercase;
        }

        .momentum-section-note {
            color: #64748B;
            font-size: 0.78rem;
            text-align: right;
        }

        .momentum-kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1rem;
            margin-bottom: 1.6rem;
        }

        .momentum-kpi-card {
            position: relative;
            overflow: hidden;
            min-height: 148px;
            padding: 1.05rem 1.1rem 1rem;
            background: rgba(255, 255, 255, 0.93);
            border: 1px solid rgba(203, 213, 225, 0.84);
            border-radius: 17px;
            box-shadow: 0 7px 22px rgba(15, 23, 42, 0.045);
        }

        .momentum-kpi-card::before {
            content: "";
            position: absolute;
            top: 0;
            right: 0;
            left: 0;
            height: 3px;
            background: var(--card-accent);
        }

        .momentum-kpi-card::after {
            content: "";
            position: absolute;
            width: 80px;
            height: 80px;
            top: -43px;
            right: -31px;
            background: var(--card-glow);
            border-radius: 50%;
        }

        .momentum-kpi-indigo {
            --card-accent: var(--momentum-indigo);
            --card-glow: rgba(99, 102, 241, 0.09);
        }

        .momentum-kpi-violet {
            --card-accent: var(--momentum-violet);
            --card-glow: rgba(139, 92, 246, 0.09);
        }

        .momentum-kpi-cyan {
            --card-accent: var(--momentum-cyan);
            --card-glow: rgba(34, 211, 238, 0.1);
        }

        .momentum-kpi-gold {
            --card-accent: var(--momentum-gold);
            --card-glow: rgba(234, 179, 8, 0.09);
        }

        .momentum-kpi-topline {
            display: flex;
            justify-content: space-between;
            gap: 0.5rem;
            margin-bottom: 0.82rem;
        }

        .momentum-kpi-label {
            color: #64748B;
            font-size: 0.68rem;
            font-weight: 730;
            letter-spacing: 0.08em;
            line-height: 1.4;
            text-transform: uppercase;
        }

        .momentum-kpi-index {
            color: #94A3B8;
            font-size: 0.66rem;
            font-weight: 700;
            letter-spacing: 0.08em;
        }

        .momentum-kpi-value {
            color: var(--momentum-ink);
            font-size: clamp(1.75rem, 2.6vw, 2.35rem);
            font-weight: 745;
            line-height: 1.08;
            letter-spacing: -0.035em;
        }

        .momentum-kpi-value-repository {
            font-size: clamp(1.05rem, 1.65vw, 1.48rem);
            line-height: 1.22;
            overflow-wrap: anywhere;
        }

        .momentum-kpi-context {
            margin-top: 0.68rem;
            color: #64748B;
            font-size: 0.75rem;
            line-height: 1.45;
        }


        /* -----------------------------------------------------------
           Responsive hero and KPI layouts
           ----------------------------------------------------------- */

        @media (max-width: 1050px) {
            .momentum-hero-main {
                grid-template-columns: 1fr;
                gap: 1.3rem;
            }

            .momentum-lens {
                max-width: 480px;
            }

            .momentum-kpi-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 650px) {
            .momentum-hero {
                padding: 1.3rem;
                border-radius: 18px;
            }

            .momentum-hero-topline,
            .momentum-section-intro {
                align-items: flex-start;
                flex-direction: column;
            }

            .momentum-section-note {
                text-align: left;
            }

            .momentum-status-badge {
                white-space: normal;
            }

            .momentum-kpi-grid {
                grid-template-columns: 1fr;
            }
        }

                /* -----------------------------------------------------------
           Evidence navigation and chart panels
           ----------------------------------------------------------- */

        .momentum-evidence-intro {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 1.5rem;
            margin-top: 2.4rem;
            margin-bottom: 0.8rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--momentum-border);
        }

        .momentum-evidence-kicker {
            margin-bottom: 0.35rem;
            color: #4F46E5;
            font-size: 0.69rem;
            font-weight: 760;
            letter-spacing: 0.13em;
            text-transform: uppercase;
        }

        .momentum-evidence-title {
            margin: 0;
            color: var(--momentum-ink);
            font-size: clamp(1.35rem, 2vw, 1.75rem);
            font-weight: 735;
            line-height: 1.2;
            letter-spacing: -0.025em;
        }

        .momentum-evidence-description {
            max-width: 520px;
            margin: 0;
            color: #64748B;
            font-size: 0.8rem;
            line-height: 1.55;
            text-align: right;
        }


        /* Remove automatic heading-link icons. */

        [data-testid="stHeaderActionElements"] {
            display: none;
        }

        /* -----------------------------------------------------------
           Native Streamlit tabs
           ----------------------------------------------------------- */

        div[data-testid="stTabs"] {
            margin-top: 0.45rem;
        }

        div[data-testid="stTabs"] div[role="tabpanel"] {
            padding-top: 0.7rem;
        }


        /* -----------------------------------------------------------
           Plotly evidence panels
           ----------------------------------------------------------- */

        [data-testid="stPlotlyChart"] {
            overflow: visible;
            margin-top: 0.7rem;
            padding: 0.5rem 0.6rem 0.75rem;
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid rgba(203, 213, 225, 0.86);
            border-radius: 18px;
            box-shadow:
                0 10px 30px rgba(15, 23, 42, 0.045),
                0 2px 6px rgba(15, 23, 42, 0.025);
        }


        /* -----------------------------------------------------------
           Analytical takeaway notes
           ----------------------------------------------------------- */

        div[role="tabpanel"]
        [data-testid="stCaptionContainer"] {
            margin-top: 0.55rem;
            padding: 0.8rem 0.95rem;
            color: #475569;
            background:
                linear-gradient(
                    90deg,
                    rgba(99, 102, 241, 0.075),
                    rgba(34, 211, 238, 0.035)
                );
            border-left: 3px solid var(--momentum-indigo);
            border-radius: 0 10px 10px 0;
            font-size: 0.78rem;
            line-height: 1.55;
        }


        /* -----------------------------------------------------------
           Responsive evidence introduction
           ----------------------------------------------------------- */

        @media (max-width: 800px) {
            .momentum-evidence-intro {
                align-items: flex-start;
                flex-direction: column;
                gap: 0.55rem;
            }

            .momentum-evidence-description {
                text-align: left;
            }
        }
         
    </style>
    """
)

# Find the main repository folder.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Build the paths to the two finalized CSV files.
NORMALIZED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "normalized_momentum_score.csv"
)

RADAR_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "repository_discovery_radar.csv"
)


# Store loaded data so Streamlit does not reread the files unnecessarily.
@st.cache_data
def load_data():
    normalized_df = pd.read_csv(NORMALIZED_DATA_PATH)
    radar_df = pd.read_csv(RADAR_DATA_PATH)

    return normalized_df, radar_df


normalized_df, radar_df = load_data()


# Dashboard title and introduction.
# -------------------------------------------------------------------
# Momentum Signal Brief hero
# -------------------------------------------------------------------

st.html(
    """
    <section class="momentum-hero">
        <div class="momentum-hero-content">

            <div class="momentum-hero-topline">
                <div class="momentum-eyebrow">
                    <span class="momentum-eyebrow-dot"></span>
                    Developer intelligence brief
                </div>

                <div class="momentum-status-badge">
                    Fixed historical sample
                </div>
            </div>

            <div class="momentum-hero-main">
                <div>
                    <h1 class="momentum-hero-title">
                        GitHub Repository
                        <span>Momentum Dashboard</span>
                    </h1>

                    <p class="momentum-hero-description">
                        Explore which repositories show momentum, what
                        supports their scores, and how growth and contributor
                        signals shape their discovery position.
                    </p>
                </div>

                <div class="momentum-lens">
                    <span class="momentum-lens-label">
                        Analytical lens
                    </span>

                    <strong>
                        Growth · Recent activity · Contributor breadth
                    </strong>

                    <div class="momentum-signal-track">
                        <span class="momentum-signal-node"></span>
                        <span class="momentum-signal-line"></span>
                        <span class="momentum-signal-node"></span>
                        <span class="momentum-signal-line"></span>
                        <span class="momentum-signal-node"></span>
                    </div>
                </div>
            </div>

            <div class="momentum-hero-note">
                <span class="momentum-note-mark">i</span>

                <span>
                    Exploratory portfolio prototype based on historical
                    public GitHub sample commit data — not a production
                    GitHub ranking system.
                </span>
            </div>

        </div>
    </section>
    """
)

# -------------------------------------------------------------------
# Momentum definition and scoring overview
# -------------------------------------------------------------------

st.html(
    """
    <style>
        .momentum-definition {
            margin: 0 0 1.5rem;
            padding: 1.25rem 1.35rem 1.3rem;
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid rgba(203, 213, 225, 0.86);
            border-radius: 18px;
            box-shadow: 0 7px 22px rgba(15, 23, 42, 0.04);
        }

        .momentum-definition-kicker {
            margin-bottom: 0.35rem;
            color: #4F46E5;
            font-size: 0.69rem;
            font-weight: 760;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .momentum-definition-title {
            margin: 0;
            color: #0F172A;
            font-size: 1.25rem;
            font-weight: 720;
            line-height: 1.3;
        }

        .momentum-definition-copy {
            max-width: 1050px;
            margin: 0.6rem 0 0;
            color: #475569;
            font-size: 0.9rem;
            line-height: 1.65;
        }

        .momentum-definition-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.8rem;
            margin-top: 1rem;
        }

        .momentum-definition-item {
            padding: 0.9rem 1rem;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
        }

        .momentum-definition-item strong {
            display: block;
            margin-bottom: 0.25rem;
            color: #0F172A;
            font-size: 0.88rem;
        }

        .momentum-definition-item span {
            color: #64748B;
            font-size: 0.78rem;
            line-height: 1.5;
        }

        @media (max-width: 800px) {
            .momentum-definition-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>

    <section class="momentum-definition">
        <div class="momentum-definition-kicker">
            Metric definition
        </div>

        <h2 class="momentum-definition-title">
            What does momentum mean in this dashboard?
        </h2>

        <p class="momentum-definition-copy">
            Repository momentum describes the direction and strength of recent repository 
            activity. In this prototype, it combines recent change in commit activity, 
            current commit volume, and recent contributor breadth. Together, these 
            signals help distinguish repositories showing stronger recent movement from 
            those whose activity is more stable or weaker within the comparison set. The 
            resulting score is comparative and exploratory; it is not a measure of repository 
            quality, popularity, or long-term success.
        </p>

        <div class="momentum-definition-grid">

            <div class="momentum-definition-item">
                <strong>Growth · 50%</strong>
                <span>
                    Change in commit activity between the recent 30-day
                    window and the preceding 30-day window.
                </span>
            </div>

            <div class="momentum-definition-item">
                <strong>Recent activity · 30%</strong>
                <span>
                    Number of commits recorded during the recent
                    30-day analysis window.
                </span>
            </div>

            <div class="momentum-definition-item">
                <strong>Contributor breadth · 20%</strong>
                <span>
                    Number of distinct contributors active during the
                    recent 30-day window.
                </span>
            </div>

        </div>
    </section>
    """
)

with st.expander("How is the momentum score calculated?"):
    st.markdown(
        """
        **1. Growth rate**

        Growth compares commit activity in the recent 30-day period with
        activity in the preceding 30-day period:

        `((recent commits - previous commits) / previous commits) × 100`

        **2. Normalize the signals**

        Growth rate, recent commit activity, and recent distinct-contributor count operate 
        on different scales. Each is therefore normalized relative to the maximum 
        observed value in the comparison set before weighting.

        **3. Apply the momentum weights**

        - Growth: **50%**
        - Recent activity: **30%**
        - Contributor breadth: **20%**

        `Momentum Score = Growth Component + Recent Activity Component + Contributor Component`

        Growth receives the largest weight because the analytical question
        focuses on momentum rather than repository size alone. Recent
        activity confirms current activity, while contributor breadth adds
        evidence of participation beyond commit volume.

        Repositories without a usable prior-period baseline are labelled
        **New/Emerging**. Their direct growth contribution is treated as zero
        in the normalized momentum score.

        The analysis also requires more than 20 commits in the recent
        30-day window to reduce very small, noisy observations.
        """
    )

with st.expander("What data does this dashboard use?"):
    st.markdown(
        """
        **Data source**

        `bigquery-public-data.github_repos.sample_commits`

        This prototype is based on a historical public GitHub sample commit dataset
        available through Google BigQuery. The dashboard uses processed analytical
        outputs generated from the SQL analysis rather than querying BigQuery live.

        **Fixed analysis cutoff:** June 22, 2016.

        **Source fields used**

        - **repo_name** — identifies the repository
        - **commit** — used to count repository commit activity
        - **committer.date** — used to place commits into the recent and previous 30-day periods
        - **author.name** — used to derive distinct-contributor measures

        **Derived analytical fields**

        From those source attributes, the SQL creates:

        - recent 30-day commits
        - previous 30-day commits
        - growth rate
        - recent 30-day distinct-contributor count
        - normalized score components
        - momentum score
        - observed contributor breadth across the available sample history
        - growth-rate and observed-contributor-breadth percentiles
        - discovery-zone classification

        The current prototype does not use stars, forks, issues, pull requests,
        topics, bot filtering, or broader repository metadata.
        """
    )

# -------------------------------------------------------------------
# Sidebar filters
# -------------------------------------------------------------------

st.sidebar.header("Dashboard Filters")

# Create a complete repository list using both datasets.
repository_options = sorted(
    set(normalized_df["repo_name"]).union(
        set(radar_df["repo_name"])
    )
)

activity_status_options = sorted(
    normalized_df["activity_status"]
    .dropna()
    .unique()
    .tolist()
)

radar_zone_options = sorted(
    radar_df["radar_zone"]
    .dropna()
    .unique()
    .tolist()
)


# Repository filter: applies to both datasets.
selected_repositories = st.sidebar.multiselect(
    "Repositories",
    options=repository_options,
    default=[],
    placeholder="All repositories",
    help=(
        "Leave empty to show all repositories, or select specific "
        "repositories to filter the dashboard."
    ),
)


# Activity-status filter: applies to momentum-score data.
selected_activity_statuses = st.sidebar.multiselect(
    "Activity Status",
    options=activity_status_options,
    default=[],
    placeholder="All activity statuses",
    help=(
        "Leave empty to show all activity statuses, or select specific "
        "statuses to filter the momentum views."
    ),
)

# Radar-zone filter: applies to discovery-radar data.
selected_radar_zones = st.sidebar.multiselect(
    "Discovery Zone",
    options=radar_zone_options,
    default=[],
    placeholder="All discovery zones",
    help=(
        "Leave empty to show all discovery zones, or select specific zones "
        "to filter the discovery matrix."
    ),
)

st.sidebar.divider()

st.sidebar.caption(
    "Data source: historical public GitHub sample commit data."
)


# If a filter is completely cleared, treat it as showing all values.
active_repositories = (
    selected_repositories
    if selected_repositories
    else repository_options
)

active_activity_statuses = (
    selected_activity_statuses
    if selected_activity_statuses
    else activity_status_options
)

active_radar_zones = (
    selected_radar_zones
    if selected_radar_zones
    else radar_zone_options
)


# Create filtered copies of the two datasets.
filtered_normalized_df = normalized_df[
    normalized_df["repo_name"].isin(active_repositories)
    & normalized_df["activity_status"].isin(
        active_activity_statuses
    )
].copy()

filtered_radar_df = radar_df[
    radar_df["repo_name"].isin(active_repositories)
    & radar_df["radar_zone"].isin(active_radar_zones)
].copy()


# -------------------------------------------------------------------
# Filter-responsive KPI cards
# -------------------------------------------------------------------

repositories_analyzed = filtered_normalized_df[
    "repo_name"
].nunique()


if filtered_normalized_df.empty:
    highest_momentum_repository = "—"
    average_momentum_score = None
else:
    top_repository_index = filtered_normalized_df[
        "momentum_score"
    ].idxmax()

    highest_momentum_repository = filtered_normalized_df.loc[
        top_repository_index,
        "repo_name",
    ]

    average_momentum_score = filtered_normalized_df[
        "momentum_score"
    ].mean()


new_emerging_count = filtered_normalized_df.loc[
    filtered_normalized_df["activity_status"] == "New/Emerging",
    "repo_name",
].nunique()


average_momentum_display = (
    f"{average_momentum_score:.2f}"
    if average_momentum_score is not None
    else "—"
)


st.html(
    """
    <div class="momentum-section-intro">
        <div class="momentum-section-kicker">
            Signal summary
        </div>

        <div class="momentum-section-note">
            Updates with repository and activity-status filters
        </div>
    </div>
    """
)


st.html(
    f"""
    <section class="momentum-kpi-grid">

        <article class="momentum-kpi-card momentum-kpi-indigo">
            <div class="momentum-kpi-topline">
                <span class="momentum-kpi-label">
                    Repositories analyzed
                </span>

                <span class="momentum-kpi-index">01</span>
            </div>

            <div class="momentum-kpi-value">
                {repositories_analyzed}
            </div>

            <div class="momentum-kpi-context">
                Repositories visible in the current momentum view
            </div>
        </article>


        <article class="momentum-kpi-card momentum-kpi-violet">
            <div class="momentum-kpi-topline">
                <span class="momentum-kpi-label">
                    Highest momentum repository
                </span>

                <span class="momentum-kpi-index">02</span>
            </div>

            <div class="
                momentum-kpi-value
                momentum-kpi-value-repository
            ">
                {highest_momentum_repository}
            </div>

            <div class="momentum-kpi-context">
                Highest normalized momentum score within current filters
            </div>
        </article>


        <article class="momentum-kpi-card momentum-kpi-cyan">
            <div class="momentum-kpi-topline">
                <span class="momentum-kpi-label">
                    Average momentum score
                </span>

                <span class="momentum-kpi-index">03</span>
            </div>

            <div class="momentum-kpi-value">
                {average_momentum_display}
            </div>

            <div class="momentum-kpi-context">
                Mean score across the visible repository set
            </div>
        </article>


        <article class="momentum-kpi-card momentum-kpi-gold">
            <div class="momentum-kpi-topline">
                <span class="momentum-kpi-label">
                    New / Emerging repositories
                </span>

                <span class="momentum-kpi-index">04</span>
            </div>

            <div class="momentum-kpi-value">
                {new_emerging_count}
            </div>

            <div class="momentum-kpi-context">
                Repositories without a usable prior-period baseline
            </div>
        </article>

    </section>
    """
)

    # -------------------------------------------------------------------
# Dashboard chart tabs
# -------------------------------------------------------------------

st.html(
    """
    <section class="momentum-evidence-intro">
        <div>
            <div class="momentum-evidence-kicker">
                Evidence views
            </div>

            <h2 class="momentum-evidence-title">
                Follow the momentum signal
            </h2>
        </div>

        <p class="momentum-evidence-description">
            Move from repository ranking to driver explanation,
            score composition, and discovery-zone classification.
        </p>
    </section>
    """
)

ranking_tab, drivers_tab, fingerprint_tab, discovery_tab = st.tabs(
    [
        "Momentum Ranking",
        "Momentum Drivers",
        "Score Fingerprint",
        "Discovery Matrix",
    ]
)


# -------------------------------------------------------------------
# Chart 1: Repository Momentum Ranking
# -------------------------------------------------------------------

with ranking_tab:
    st.subheader("Repository Momentum Ranking")

    st.markdown(
        """
        Repositories are ranked by their **composite momentum score**, which combines
        normalized growth, recent commit activity, and contributor breadth using the
        weights defined above.
        
        **How to read this chart:** A longer bar represents a stronger combined momentum
         signal within this comparison set. Scores above zero indicate that the positive 
         contributions from growth, recent activity, and contributor breadth outweigh any 
         negative growth contribution. Scores below zero indicate that declining growth is 
         strong enough to outweigh the positive contributions from recent activity and 
         contributor breadth. Bar colour indicates the repository's activity status.
        """
        )

    if filtered_normalized_df.empty:
        st.warning(
            "No repositories match the current repository and "
            "activity-status filters."
        )

    else:
        ranking_df = filtered_normalized_df.copy()

        ranking_df["growth_rate_label"] = ranking_df[
            "growth_rate"
        ].apply(
            lambda value: (
                f"{value:+.2f}%"
                if pd.notnull(value)
                else "New/Emerging"
            )
        )

        ranking_df = ranking_df.sort_values(
            "momentum_score",
            ascending=True,
        )

        activity_status_colors = {
            "Growing": "#6366F1",
            "Stable": "#CBD5E1",
            "New/Emerging": "#22D3EE",
        }

        ranking_figure = px.bar(
            ranking_df,
            x="momentum_score",
            y="repo_name",
            orientation="h",
            color="activity_status",
            color_discrete_map=activity_status_colors,
            custom_data=[
                "repo_name",
                "momentum_score",
                "growth_rate_label",
                "contributor_count",
                "activity_status",
                "commits_last_30_days",
            ],
            labels={
                "momentum_score": "Normalized Momentum Score",
                "repo_name": "Repository",
                "activity_status": "Activity Status",
            },
        )

        ranking_figure.update_traces(
            texttemplate="%{x:.2f}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Momentum score: %{customdata[1]:.2f}<br>"
                "Growth rate: %{customdata[2]}<br>"
                "Contributors: %{customdata[3]:,.0f}<br>"
                "Activity status: %{customdata[4]}<br>"
                "Recent commits: %{customdata[5]:,.0f}"
                "<extra></extra>"
            ),
        )

        ranking_figure.add_vline(
            x=0,
            line_width=1.5,
            line_dash="dash",
            line_color="#94A3B8",
        )

        ranking_figure.update_layout(
            height=560,
            template="plotly_white",
            xaxis_title="Normalized Momentum Score",
            yaxis_title="Repository",
            legend_title="Activity Status",
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "left",
                "x": 0,
                "itemsizing": "constant",
                "bgcolor": "rgba(0, 0, 0, 0)",
                "font": {
                    "size": 11,
                    "color": "#475569",
                },
            },
            margin={
                "l": 20,
                "r": 70,
                "t": 80,
                "b": 40,
            },
        )

        ranking_figure.update_yaxes(
    categoryorder="array",
    categoryarray=ranking_df["repo_name"].tolist(),
)

        st.plotly_chart(
            ranking_figure,
            width="stretch",
            config={
                "displaylogo": False,
                "displayModeBar": False,
                "responsive": True,
            },
        )

        current_leader = filtered_normalized_df.loc[
            filtered_normalized_df["momentum_score"].idxmax()
        ]

        st.caption(
            f"Within the current filters, "
            f"**{current_leader['repo_name']}** has the highest "
            f"momentum score at "
            f"**{current_leader['momentum_score']:.2f}**."
        )


# Temporary messages for the remaining tabs.
with drivers_tab:
    st.subheader("What Drives Repository Momentum?")

    st.markdown(
            """
            This view compares two of the main signals behind repository momentum:
            **change in recent commit activity** and **contributor breadth**.

            **How to read this chart:**

            - **X-axis — Commit Growth Rate (%):** percentage change in commits between
            the recent 30-day period and the preceding 30-day period. Values to the
            right of zero indicate increasing activity; values to the left indicate
            declining activity.
            - **Y-axis — Distinct Contributors (Recent 30 Days):** number of distinct 
            contributors observed during the recent 30-day period.
            - **Bubble size — Momentum score:** larger bubbles represent higher composite
            momentum scores within the comparison set.
            - **Colour — Activity status:** shows whether a repository is classified as
            Growing, Stable, or New/Emerging.

            **New/Emerging repositories:** repositories without a usable prior-period
            baseline are positioned at zero on the growth axis for visualization only.
            This does not represent an observed 0% growth rate; their hover label identifies
            them as New/Emerging.
            """
        )

    if filtered_normalized_df.empty:
        st.warning(
            "No repositories match the current repository and "
            "activity-status filters."
        )

    else:
        drivers_df = filtered_normalized_df.copy()

        # Repositories without a previous-period baseline have a null
        # growth rate. For plotting only, place them at zero growth.
        drivers_df["growth_rate_plot"] = drivers_df[
            "growth_rate"
        ].fillna(0)

        # Create readable hover text for growth rate.
        drivers_df["growth_rate_label"] = drivers_df[
            "growth_rate"
        ].apply(
            lambda value: (
                f"{value:+.2f}%"
                if pd.notnull(value)
                else "New/Emerging"
            )
        )

        # Plotly bubble sizes must be positive.
        # Shift all existing momentum scores upward without changing
        # their ranking or analytical meaning.
        minimum_momentum_score = drivers_df[
            "momentum_score"
        ].min()

        drivers_df["visual_size"] = (
            drivers_df["momentum_score"]
            - minimum_momentum_score
            + 1
        )

        driver_status_colors = {
            "Growing": "#6366F1",
            "Stable": "#CBD5E1",
            "New/Emerging": "#22D3EE",
        }

        drivers_figure = px.scatter(
            drivers_df,
            x="growth_rate_plot",
            y="contributor_count",
            size="visual_size",
            size_max=50,
            color="activity_status",
            color_discrete_map=driver_status_colors,
            text="repo_name",
            custom_data=[
                "repo_name",
                "growth_rate_label",
                "contributor_count",
                "commits_last_30_days",
                "momentum_score",
                "activity_status",
            ],
            labels={
                "growth_rate_plot": "Commit Growth Rate (%)",
                "contributor_count": "Distinct Contributors (Recent 30 Days)",
                "activity_status": "Activity Status",
            },
        )

        # The zero line separates positive growth from negative growth.
        drivers_figure.add_vline(
            x=0,
            line_width=1,
            line_dash="dash",
            line_color="#64748B",
        )

        drivers_figure.update_traces(
            textposition="top center",
            marker={
                "opacity": 0.82,
            },
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Growth rate: %{customdata[1]}<br>"
                "Contributors: %{customdata[2]:,.0f}<br>"
                "Recent commits: %{customdata[3]:,.0f}<br>"
                "Momentum score: %{customdata[4]:.2f}<br>"
                "Activity status: %{customdata[5]}"
                "<extra></extra>"
            ),
        )

        drivers_figure.update_layout(
            height=600,
            template="plotly_white",
            legend_title="Activity Status",
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
            },
            margin={
                "l": 20,
                "r": 30,
                "t": 80,
                "b": 50,
            },
        )

        st.plotly_chart(
            drivers_figure,
            width="stretch",
            config={
                "displaylogo": False,
                "displayModeBar": False,
                "responsive": True,
            },
        )

        st.caption(
            "Repositories to the right of the dashed line show positive "
            "period-over-period growth. Recent distinct-contributor count adds "
            "context, so growth is not interpreted in isolation."
        )

with fingerprint_tab:
    st.subheader("Momentum Driver Fingerprint")

    st.markdown(
            """
            This heatmap breaks each repository's **final momentum score** into its
            three weighted components: growth, recent activity, and contributor breadth.

            **How to read this chart:**

            - **Rows — Repositories:** each row represents one repository.
            - **Columns — Momentum components:** Growth (50%), Recent Activity (30%),
            and Contributor Breadth (20%).
            - **Cell value — Weighted contribution:** the amount that each component
            contributes to the repository's final momentum score after normalization
            and weighting.
            - **Colour intensity:** shows the direction and relative strength of each
            contribution. Growth can contribute positively or negatively, while recent
            activity and contributor breadth contribute positively.

            The three component values across a repository's row add up to its
            **final momentum score**.
            """
        )

    if filtered_normalized_df.empty:
        st.warning(
            "No repositories match the current repository and "
            "activity-status filters."
        )

    else:
        fingerprint_df = (
            filtered_normalized_df
            .sort_values(
                "momentum_score",
                ascending=False,
            )
            .set_index("repo_name")
            [
                [
                    "growth_component",
                    "recent_activity_component",
                    "contributor_component",
                ]
            ]
            .rename(
                columns={
                    "growth_component": "Growth (50%)",
                    "recent_activity_component": "Recent Activity (30%)",
                    "contributor_component": "Contributor Breadth (20%)",
                }
            )
        )

        fingerprint_figure = px.imshow(
            fingerprint_df,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu",
            color_continuous_midpoint=0,
            labels={
                "x": "Momentum Score Component",
                "y": "Repository",
                "color": "Weighted Contribution",
            },
        )

        fingerprint_figure.update_layout(
            height=560,
            template="plotly_white",
            margin={
                "l": 20,
                "r": 30,
                "t": 40,
                "b": 50,
            },
        )

        fingerprint_figure.update_xaxes(
            side="top",
        )

        st.plotly_chart(
            fingerprint_figure,
            width="stretch",
            config={
                "displaylogo": False,
                "displayModeBar": False,
                "responsive": True,
            },
        )

        st.caption(
            "Reading across a row shows how the three weighted signals combine into "
            "the repository's final momentum score. This makes it possible to see "
            "whether momentum is being driven primarily by growth, recent activity, "
            "contributor breadth, or a combination of the three."
        )

with discovery_tab:
    st.subheader("Repository Discovery Zone Matrix")
    st.markdown(
        """
        This view combines two different perspectives on repository activity:
        **observed contributor breadth** and **recent commit growth rate**. Unlike the
        Momentum Ranking, this matrix does not use the full composite momentum score.

        **How to read this chart:**

        - **X-axis — Observed Contributor Breadth Percentile:** ranks repositories by
        the number of distinct commit authors observed across the available sample
        timeline through the analysis cutoff. Higher percentiles indicate broader
        observed participation relative to the other repositories in the comparison set.
        - **Y-axis — Commit Growth Rate Percentile:** ranks repositories by their
        recent commit-growth rate relative to the comparison set. Growth compares
        the recent 30-day period with the preceding 30-day period.
        - **50% threshold lines:** the horizontal and vertical lines divide repositories
        at the 50th percentile on each dimension, creating four discovery zones.
        - **Each point:** represents one repository. Its position determines its
        discovery-zone classification.

        **Percentiles are relative rankings, not raw percentages.** For example,
        a contributor-breadth percentile of 75% means the repository ranks above
        roughly 75% of the comparison set on observed contributor breadth. It does
        not mean contributor count increased by 75%.
        """
    )

    st.markdown(
            """
                **Discovery zones**

    - **Momentum Leader:** at or above the 50th percentile on recent growth and observed contributor breadth
    - **Growing Candidate:** at or above the 50th percentile on recent growth and below the 50th percentile on observed contributor breadth
    - **Stable Monitor:** below the 50th percentile on recent growth and at or above the 50th percentile on observed contributor breadth
    - **Watchlist:** below the 50th percentile on both dimensions
            """
        )

    if filtered_radar_df.empty:
        st.warning(
            "No repositories match the current repository and "
            "radar-zone filters."
        )

    else:
        discovery_df = filtered_radar_df.copy()

        discovery_df["growth_rate_label"] = discovery_df[
            "growth_rate"
        ].apply(
            lambda value: (
                f"{value:+.2f}%"
                if pd.notnull(value)
                else "New/Emerging"
            )
        )

        radar_zone_colors = {
            "Momentum Leader": "#F2B84B",
            "Growing Candidate": "#2A9D8F",
            "Stable Monitor": "#849B78",
            "Watchlist": "#5969C9",
        }

        radar_zone_symbols = {
            "Momentum Leader": "star",
            "Growing Candidate": "triangle-up",
            "Stable Monitor": "diamond",
            "Watchlist": "circle",
        }

        discovery_figure = px.scatter(
            discovery_df,
            x="contributor_percentile",
            y="growth_percentile",
            color="radar_zone",
            symbol="radar_zone",
            color_discrete_map=radar_zone_colors,
            symbol_map=radar_zone_symbols,
            text="repo_name",
            custom_data=[
                "repo_name",
                "radar_zone",
                "growth_percentile",
                "contributor_percentile",
                "repository_radar_score",
                "growth_rate_label",
                "contributor_count",
            ],
            labels={
                "contributor_percentile": "Observed Contributor Breadth Percentile",
                "growth_percentile": "Commit Growth Rate Percentile",
                "radar_zone": "Discovery Zone",
            },
        )

        # Finalized 50th-percentile classification thresholds.
        discovery_figure.add_vline(
            x=0.5,
            line_width=1.5,
            line_dash="solid",
            line_color="rgba(99, 102, 241, 0.28)",
        )

        discovery_figure.add_hline(
            y=0.5,
            line_width=1.5,
            line_dash="solid",
            line_color="rgba(99, 102, 241, 0.28)",
        )

        # Consistently positioned quadrant labels.
        quadrant_labels = [
            {
                "x": 0.035,
                "y": 0.965,
                "text": "GROWING CANDIDATE",
                "xanchor": "left",
                "yanchor": "top",
            },
            {
                "x": 0.965,
                "y": 0.965,
                "text": "MOMENTUM LEADER",
                "xanchor": "right",
                "yanchor": "top",
            },
            {
                "x": 0.035,
                "y": 0.465,
                "text": "WATCHLIST",
                "xanchor": "left",
                "yanchor": "top",
            },
            {
                "x": 0.965,
                "y": 0.465,
                "text": "STABLE MONITOR",
                "xanchor": "right",
                "yanchor": "top",
            },
        ]

        for label in quadrant_labels:
            discovery_figure.add_annotation(
                x=label["x"],
                y=label["y"],
                text=f"<b>{label['text']}</b>",
                xanchor=label["xanchor"],
                yanchor=label["yanchor"],
                showarrow=False,
                font={
                    "size": 10,
                    "color": "#5B6780",
                },
                bgcolor="rgba(248, 250, 252, 0.94)",
                bordercolor="rgba(203, 213, 225, 0.95)",
                borderwidth=1,
                borderpad=5,
                opacity=0.96,
            )

        zone_marker_styles = {
            "Momentum Leader": {
                "size": 28,
                "border_color": "#8A5A00",
            },
            "Growing Candidate": {
                "size": 23,
                "border_color": "#0B5F57",
            },
            "Stable Monitor": {
                "size": 23,
                "border_color": "#506247",
            },
            "Watchlist": {
                "size": 22,
                "border_color": "#35428F",
            },
        }

        for trace in discovery_figure.data:
            zone_name = trace.name
            marker_style = zone_marker_styles[zone_name]

            trace.update(
                textposition="top center",
                textfont={
                    "size": 12,
                    "color": "#172033",
                },
                cliponaxis=False,
                marker={
                    "size": marker_style["size"],
                    "color": radar_zone_colors[zone_name],
                    "opacity": 1,
                    "line": {
                        "width": 2.2,
                        "color": marker_style["border_color"],
                    },
                },
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Discovery Zone: %{customdata[1]}<br>"
                    "Commit Growth Rate Percentile: %{customdata[2]:.1%}<br>"
                    "Observed Contributor Breadth Percentile: %{customdata[3]:.1%}<br>"
                    "Commit Growth Rate: %{customdata[5]}<br>"
                    "Observed Distinct Contributors: %{customdata[6]:,.0f}"
                    "<extra></extra>"
                ),
            )

        discovery_figure.update_xaxes(
            range=[-0.03, 1.03],
            tickvals=[0, 0.25, 0.5, 0.75, 1],
            ticktext=["0%", "25%", "50%", "75%", "100%"],
            title_text="<b>Observed Contributor Breadth Percentile</b>",
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor="#CBD5E1",
            linewidth=1.2,
            ticks="outside",
            ticklen=5,
            tickcolor="#94A3B8",
            tickfont={
                "size": 11,
                "color": "#64748B",
            },
            title_font={
                "size": 15,
                "color": "#253047",
            },
            automargin=True,
            title_standoff=12,
        )

        discovery_figure.update_yaxes(
            range=[-0.03, 1.05],
            tickvals=[0, 0.25, 0.5, 0.75, 1],
            ticktext=["0%", "25%", "50%", "75%", "100%"],
            title_text="<b>Commit Growth Rate Percentile</b>",
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor="#CBD5E1",
            linewidth=1.2,
            ticks="outside",
            ticklen=5,
            tickcolor="#94A3B8",
            tickfont={
                "size": 11,
                "color": "#64748B",
            },
            title_font={
                "size": 15,
                "color": "#253047",
            },
            automargin=True,
            title_standoff=12,
        )

        discovery_figure.update_layout(
            height=550,
            template="plotly_white",
            paper_bgcolor="rgba(0, 0, 0, 0)",
            plot_bgcolor="#FCFDFE",
            font={
                "family": "Inter, Arial, sans-serif",
                "color": "#334155",
                "size": 12,
            },
            legend_title={
                "text": "<b>DISCOVERY ZONES</b>",
                "font": {
                    "size": 10,
                    "color": "#64748B",
                },
            },
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.06,
                "xanchor": "left",
                "x": 0,
                "itemsizing": "constant",
                "bgcolor": "rgba(255, 255, 255, 0.98)",
                "bordercolor": "#D8E0EC",
                "borderwidth": 1,
                "font": {
                    "size": 11,
                    "color": "#334155",
                },
            },
            hoverlabel={
                "bgcolor": "#0F172A",
                "bordercolor": "#0F172A",
                "font": {
                    "color": "#FFFFFF",
                    "size": 12,
                },
            },
            margin={
                "l": 80,
                "r": 45,
                "t": 100,
                "b": 80,
            },
        )

        st.plotly_chart(
            discovery_figure,
            width="stretch",
            config={
                "displaylogo": False,
                "displayModeBar": False,
                "responsive": True,
            },
        )

        st.caption(
            "New/Emerging repositories require special interpretation. Where no usable "
            "prior-period baseline exists, the discovery analysis may assign an adjusted "
            "growth value before percentile ranking. This is not directly observed "
            "period-over-period growth, so the resulting discovery-zone position should "
            "be interpreted separately from repositories with a measured growth rate."
        )

        st.caption(
            "Observed contributor breadth reflects distinct commit authors represented "
            "in the historical sample dataset, not a guaranteed complete lifetime count "
            "of all contributors to the repository."
        )
# -------------------------------------------------------------------
# Interpretation and limitations
# -------------------------------------------------------------------

st.divider()

insight_column, limitations_column = st.columns(2)

with insight_column:
    st.subheader("How to Read the Dashboard")

    st.markdown(
        """
        **Momentum Ranking** compares repositories using the composite
        momentum score built from growth, recent activity, and recent
        contributor breadth.

        **Momentum Drivers** shows how recent commit growth and recent
        distinct-contributor count differ across repositories.

        **Score Fingerprint** breaks the composite score into its three weighted
        components so the result is not treated as a black box.

        **Discovery Matrix** provides a separate discovery lens by comparing
        recent commit-growth position with observed contributor breadth across
        the available sample history.
        """
    )

with limitations_column:
    st.subheader("Scope and Limitations")

    st.markdown(
        """
        - The analysis uses historical public GitHub sample commit data, not live GitHub activity.
        - The fixed analysis cutoff is **June 22, 2016**, supporting reproducible period comparisons.
        - Results describe repositories represented in the sample and should not be generalized to GitHub as a whole.
        - In the Discovery Matrix, observed contributor breadth reflects distinct commit authors represented across the available sample history, not a guaranteed complete lifetime contributor count.
        - Stars, forks, issues, pull requests, topics, and broader repository metadata are not included.
        - Bot activity is not separately identified or removed in this prototype.
        """
    )

st.caption(
    "Built with BigQuery, SQL, Python, Pandas, Plotly, and Streamlit."
)