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
st.title("GitHub Repository Momentum Dashboard")

st.markdown(
    """
    Explore repository-level momentum using recent commit growth,
    contributor participation, normalized score components, and
    percentile-based discovery zones.
    """
)

st.info(
    "Exploratory portfolio prototype based on historical public GitHub "
    "sample commit data — not a production GitHub ranking system."
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
    "Radar Zone",
    options=radar_zone_options,
    default=[],
    placeholder="All radar zones",
    help=(
        "Leave empty to show all radar zones, or select specific zones "
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


kpi_row_1_col_1, kpi_row_1_col_2 = st.columns(2)

with kpi_row_1_col_1:
    st.metric(
        label="Repositories Analyzed",
        value=repositories_analyzed,
    )

with kpi_row_1_col_2:
    st.metric(
        label="Highest Momentum Repository",
        value=highest_momentum_repository,
    )


kpi_row_2_col_1, kpi_row_2_col_2 = st.columns(2)

with kpi_row_2_col_1:
    st.metric(
        label="Average Momentum Score",
        value=(
            f"{average_momentum_score:.2f}"
            if average_momentum_score is not None
            else "—"
        ),
    )

with kpi_row_2_col_2:
    st.metric(
        label="New/Emerging Repositories",
        value=new_emerging_count,
    )

    # -------------------------------------------------------------------
# Dashboard chart tabs
# -------------------------------------------------------------------

st.divider()

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

    st.write(
        "Repositories ranked by the finalized normalized momentum score. "
        "Colour represents the repository's activity status."
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

        ranking_figure.update_layout(
            height=560,
            template="plotly_white",
            xaxis_title="Normalized Momentum Score",
            yaxis_title="",
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

    st.write(
        "This view compares recent growth with contributor participation. "
        "Bubble size represents the finalized momentum score."
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
                "growth_rate_plot": "Recent 30-Day Growth Rate (%)",
                "contributor_count": "Contributor Count",
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
            },
        )

        st.caption(
            "Repositories to the right of the dashed line show positive "
            "period-over-period growth. Contributor count adds context, "
            "so growth is not interpreted in isolation."
        )

with fingerprint_tab:
    st.subheader("Momentum Driver Fingerprint")

    st.write(
        "This heatmap shows how growth, recent activity, and contributor "
        "participation contribute to each repository's momentum score."
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
                    "growth_component": "Growth",
                    "recent_activity_component": "Recent Activity",
                    "contributor_component": "Contributor",
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
                "x": "Momentum Component",
                "y": "Repository",
                "color": "Component Value",
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
            },
        )

        st.caption(
            "The component values explain why repositories with high "
            "activity or broad contributor participation can still receive "
            "different overall momentum scores."
        )

with discovery_tab:
    st.subheader("Repository Discovery Zone Matrix")

    st.write(
        "This view classifies repositories using their relative growth "
        "and contributor percentiles. The dashed lines represent the "
        "50th-percentile thresholds used in the finalized zone logic."
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
            "Momentum Leader": "#FFD700",
            "Growing Candidate": "#14B8A6",
            "Stable Monitor": "#BDE063",
            "Watchlist": "#A8D5FF",
        }

        radar_zone_symbols = {
            "Momentum Leader": "star",
            "Growing Candidate": "triangle-up",
            "Stable Monitor": "diamond",
            "Watchlist": "circle-open",
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
                "contributor_percentile": (
                    "Contributor Strength Percentile"
                ),
                "growth_percentile": (
                    "Growth Momentum Percentile"
                ),
                "radar_zone": "Discovery Zone",
            },
        )

                # Add subtle background shading for the four discovery zones.
        # These rectangles are visual guides only; they do not change
        # the data or the classification logic.

        # Watchlist: lower growth and lower contributor strength
        discovery_figure.add_shape(
            type="rect",
            x0=-0.05,
            x1=0.5,
            y0=-0.05,
            y1=0.5,
            fillcolor="#A8D5FF",
            opacity=0.12,
            line_width=0,
            layer="below",
        )

        # Stable Monitor: lower growth and higher contributor strength
        discovery_figure.add_shape(
            type="rect",
            x0=0.5,
            x1=1.05,
            y0=-0.05,
            y1=0.5,
            fillcolor="#BDE063",
            opacity=0.12,
            line_width=0,
            layer="below",
        )

        # Growing Candidate: higher growth and lower contributor strength
        discovery_figure.add_shape(
            type="rect",
            x0=-0.05,
            x1=0.5,
            y0=0.5,
            y1=1.05,
            fillcolor="#14B8A6",
            opacity=0.10,
            line_width=0,
            layer="below",
        )

        # Momentum Leader: higher growth and higher contributor strength
        discovery_figure.add_shape(
            type="rect",
            x0=0.5,
            x1=1.05,
            y0=0.5,
            y1=1.05,
            fillcolor="#FFD700",
            opacity=0.12,
            line_width=0,
            layer="below",
        )


        # These two lines reproduce the 50th-percentile
        # thresholds used in the SQL classification logic.
        discovery_figure.add_vline(
            x=0.5,
            line_width=1,
            line_dash="dash",
            line_color="#64748B",
        )

        discovery_figure.add_hline(
            y=0.5,
            line_width=1,
            line_dash="dash",
            line_color="#64748B",
        )

        discovery_figure.update_traces(
            textposition="top center",
            marker={
                "size": 15,
                "opacity": 0.88,
                "line": {
                    "width": 1,
                    "color": "#475569",
                },
            },
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Discovery zone: %{customdata[1]}<br>"
                "Growth percentile: %{customdata[2]:.1%}<br>"
                "Contributor percentile: %{customdata[3]:.1%}<br>"
                "Radar score: %{customdata[4]:.2f}<br>"
                "Growth rate: %{customdata[5]}<br>"
                "Contributors: %{customdata[6]:,.0f}"
                "<extra></extra>"
            ),
        )

        discovery_figure.update_xaxes(
            range=[-0.05, 1.05],
            tickformat=".0%",
        )

        discovery_figure.update_yaxes(
            range=[-0.05, 1.05],
            tickformat=".0%",
        )

        discovery_figure.update_layout(
            height=620,
            template="plotly_white",
            legend_title="Discovery Zone",
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
                "t": 90,
                "b": 50,
            },
        )

        st.plotly_chart(
            discovery_figure,
            width="stretch",
            config={
                "displaylogo": False,
            },
        )

        st.caption(
    "The discovery zones are relative classifications within this "
    "historical sample window. Repositories without a prior-period "
    "baseline are treated as New/Emerging and may receive an imputed "
    "top growth percentile, so zone placement should be interpreted "
    "cautiously."
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
        **Momentum Ranking** compares repositories using the finalized
        normalized momentum score.

        **Momentum Drivers** separates recent growth from contributor
        participation, helping explain what supports each score.

        **Score Fingerprint** exposes the growth, recent activity, and
        contributor components so the composite score is not treated as
        a black box.

        **Discovery Matrix** classifies repositories using relative growth
        and contributor percentiles.
        """
    )

with limitations_column:
    st.subheader("Scope and Limitations")

    st.markdown(
        """
        - The analysis uses historical public GitHub sample commit data.
        - A fixed analysis date is used for reproducibility.
        - Results represent the selected sample window, not GitHub as a whole.
        - Stars, forks, issues, pull requests, and topics are not included.
        - Bot activity and repository metadata are not separately modelled.
        """
    )

st.caption(
    "Built with BigQuery, SQL, Python, Pandas, Plotly, and Streamlit."
)