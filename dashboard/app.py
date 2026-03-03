import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from data.loaders import CSVDataLoader
from data.validator import DataValidator
from processing.preprocessor import DataPreprocessor
from processing.feature_engineer import FeatureEngineer
from analysis.eda_engine import EDAEngine
from utils.logger import logger

# ─────────────────────────────────────────────
#  Load & prepare data
# ─────────────────────────────────────────────
loader = CSVDataLoader()
raw_df = loader.load_data("./data/internet_firewall_data.csv")

preprocessor = DataPreprocessor()
df = preprocessor.preprocess(raw_df.copy())

engineer = FeatureEngineer()
df = engineer.engineer_features(df)

eda = EDAEngine(df)

numeric_cols = df.select_dtypes(include="number").columns.tolist()
raw_numeric_cols = raw_df.select_dtypes(include="number").columns.tolist()
default_feature = raw_numeric_cols[0] if raw_numeric_cols else "Source Port"

# ─────────────────────────────────────────────
#  KPI computations
# ─────────────────────────────────────────────
total_records = len(df)

# Action distribution from raw data
action_col = "Action" if "Action" in raw_df.columns else "action"
if action_col in raw_df.columns:
    action_counts = raw_df[action_col].value_counts()
    allow_count = int(action_counts.get("allow", action_counts.get("ALLOW", 0)))
    deny_count  = int(action_counts.get("deny",  action_counts.get("DENY",  0)))
    drop_count  = int(action_counts.get("drop",  action_counts.get("DROP",  0)))
else:
    allow_count = deny_count = drop_count = 0

# High-traffic anomalies (top 5%)
anomaly_cols = [c for c in df.columns if c.startswith("anomaly_") or c == "total_bytes"]
if "total_bytes" in df.columns:
    threshold = df["total_bytes"].quantile(0.95)
    anomaly_count = int((df["total_bytes"] > threshold).sum())
else:
    anomaly_count = 0

threat_pct = round((deny_count + drop_count) / max(total_records, 1) * 100, 1)

# ─────────────────────────────────────────────
#  Colour palette — White / Green / Violet
# ─────────────────────────────────────────────
GREEN         = "#22C55E"   # vibrant green
GREEN_DARK    = "#166534"   # deep forest green
GREEN_LIGHT   = "#4ADE80"   # bright mint
GREEN_PALE    = "#BBF7D0"   # very light mint
VIOLET        = "#7C3AED"   # deep violet
VIOLET_LIGHT  = "#A78BFA"   # lavender
VIOLET_PALE   = "#EDE9FE"   # near-white violet
WHITE         = "#FFFFFF"
OFF_WHITE     = "#F0FFF4"   # mint-tinted white
TEXT_DARK     = "#14532D"   # dark green for text on light bg
CARD_BG       = "rgba(255, 255, 255, 0.80)"
CARD_BORDER   = "rgba(34,197,94,0.30)"
BG_GRADIENT   = "linear-gradient(135deg, #F0FFF4 0%, #ECFDF5 40%, #F5F3FF 80%, #EDE9FE 100%)"
CHART_BG      = "rgba(255,255,255,0.60)"
GRID_COLOR    = "rgba(34,197,94,0.18)"
FONT_FAMILY   = "'Inter', 'Segoe UI', 'Helvetica Neue', sans-serif"

# Aliases so old callback code still works
AMBER         = GREEN
AMBER_DARK    = GREEN_DARK
AMBER_LIGHT   = GREEN_LIGHT
RED           = VIOLET
RED_DARK      = "#4C1D95"
YELLOW        = VIOLET_LIGHT

plotly_template = dict(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=CHART_BG,
        font=dict(family=FONT_FAMILY, color=TEXT_DARK, size=13),
        title=dict(font=dict(size=16, color=GREEN_DARK, family=FONT_FAMILY, weight=700), x=0.01),
        xaxis=dict(
            gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
            tickfont=dict(color=TEXT_DARK), title_font=dict(color=GREEN_DARK),
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
            tickfont=dict(color=TEXT_DARK), title_font=dict(color=GREEN_DARK),
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.70)",
            bordercolor=CARD_BORDER, borderwidth=1,
            font=dict(color=TEXT_DARK),
        ),
        margin=dict(l=20, r=20, t=50, b=20),
    )
)

WARM_SCALE    = ["#F0FFF4", "#BBF7D0", "#4ADE80", "#22C55E", "#166534", "#A78BFA"]
ACCENT_COLORS = [GREEN_LIGHT, GREEN, VIOLET, VIOLET_LIGHT, WHITE, VIOLET_PALE]

# ─────────────────────────────────────────────
#  Shared CSS helpers
# ─────────────────────────────────────────────
def glass_card(extra=None):
    style = dict(
        background   = CARD_BG,
        border       = f"1px solid {CARD_BORDER}",
        borderRadius = "16px",
        backdropFilter = "blur(16px)",
        WebkitBackdropFilter = "blur(16px)",
        padding      = "24px",
        boxShadow    = "0 4px 24px rgba(34,197,94,0.12), 0 1px 4px rgba(124,58,237,0.08)",
    )
    if extra:
        style.update(extra)
    return style

# ─────────────────────────────────────────────
#  Build KPI card
# ─────────────────────────────────────────────
def kpi_card(icon, label, value, colour=GREEN_LIGHT, subtitle=None):
    return html.Div(
        className="kpi-card",
        style={
            **glass_card(),
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "textAlign": "center",
            "transition": "transform 0.2s ease",
            "cursor": "default",
            "minWidth": "160px",
        },
        children=[
            html.Div(icon, style={
                "fontSize": "36px",
                "marginBottom": "8px",
            }),
            html.Div(str(value), style={
                "fontSize": "32px",
                "fontWeight": "800",
                "color": colour,
                "lineHeight": "1",
                "textShadow": f"0 2px 12px {colour}40",
            }),
            html.Div(label, style={
                "fontSize": "12px",
                "color": TEXT_DARK,
                "marginTop": "6px",
                "textTransform": "uppercase",
                "letterSpacing": "1.2px",
                "fontWeight": "600",
            }),
            *(
                [html.Div(subtitle, style={"fontSize": "11px", "color": VIOLET_LIGHT, "marginTop": "4px"})]
                if subtitle else []
            ),
        ],
    )

# ─────────────────────────────────────────────
#  Custom CSS injected via assets
# ─────────────────────────────────────────────
# CSS is loaded from assets/style.css automatically by Dash

# ─────────────────────────────────────────────
#  App initialization
# ─────────────────────────────────────────────
app = dash.Dash(
    __name__,
    title="Firewall Analyzer",
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

# ── Inject critical CSS directly into <head> for Dash 4 Radix UI Dropdown ──
app.index_string = """<!DOCTYPE html>
<html>
  <head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <style>
      button.dash-dropdown, .dash-dropdown {
          background-color: #ffffff !important;
          border: 1.5px solid #22C55E !important;
          border-radius: 10px !important;
          color: #166534 !important;
          box-shadow: 0 2px 8px rgba(34,197,94,0.12) !important;
      }
      button.dash-dropdown:hover, .dash-dropdown:hover {
          border-color: #7C3AED !important;
          box-shadow: 0 0 0 3px rgba(124,58,237,0.12) !important;
      }
      .dash-dropdown-value { color: #166534 !important; font-weight: 600 !important; }
      .dash-dropdown-content {
          background-color: #ffffff !important;
          border: 1.5px solid #22C55E !important;
          border-radius: 10px !important;
          box-shadow: 0 8px 32px rgba(34,197,94,0.18), 0 2px 8px rgba(0,0,0,0.08) !important;
          z-index: 9999 !important;
          padding: 4px !important;
      }
      input.dash-dropdown-search, .dash-dropdown-search {
          background-color: transparent !important;
          color: #166534 !important;
          caret-color: #7C3AED !important;
          border: none !important;
          border-bottom: 1px solid rgba(34,197,94,0.30) !important;
          margin-bottom: 4px !important;
          padding: 8px 12px !important;
      }
      .dash-dropdown-search::placeholder { color: rgba(22,101,52,0.40) !important; }
      .dash-dropdown-search:focus { outline:none !important; border-bottom-color: #7C3AED !important; }
      label.dash-dropdown-option, .dash-dropdown-option {
          background-color: transparent !important;
          color: #166534 !important;
          padding: 10px 14px !important;
          cursor: pointer !important;
          border-radius: 6px !important;
          transition: background 0.15s !important;
          font-weight: 500 !important;
      }
      label.dash-dropdown-option:hover, .dash-dropdown-option:hover,
      .dash-dropdown-option[data-highlighted] {
          background-color: rgba(34,197,94,0.10) !important;
          color: #14532d !important;
      }
      label.dash-dropdown-option.selected, .dash-dropdown-option.selected,
      .dash-dropdown-option[data-state="checked"] {
          background-color: rgba(124,58,237,0.12) !important;
          color: #5B21B6 !important;
          font-weight: 700 !important;
      }
    </style>
  </head>
  <body>
    {%app_entry%}
    <footer>
      {%config%}
      {%scripts%}
      {%renderer%}
    </footer>
  </body>
</html>"""


# ─────────────────────────────────────────────
#  Layout
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
#  Layout  (two-view architecture)
# ─────────────────────────────────────────────
app.layout = html.Div(
    style={"minHeight": "100vh", "background": BG_GRADIENT, "fontFamily": FONT_FAMILY, "color": WHITE},
    children=[
        # Decorative orbs
        html.Div(style={
            "position": "fixed", "top": "-180px", "right": "-180px",
            "width": "500px", "height": "500px", "borderRadius": "50%",
            "background": "radial-gradient(circle, rgba(249,115,22,0.22) 0%, transparent 70%)",
            "pointerEvents": "none", "zIndex": "0",
        }),
        html.Div(style={
            "position": "fixed", "bottom": "-200px", "left": "-150px",
            "width": "450px", "height": "450px", "borderRadius": "50%",
            "background": "radial-gradient(circle, rgba(239,68,68,0.18) 0%, transparent 70%)",
            "pointerEvents": "none", "zIndex": "0",
        }),

        # Hidden store: current view ('main' | 'detail')
        dcc.Store(id="current-view", data="main"),

        # ── Main Content ──────────────────────────────────────────────
        html.Div(style={"position": "relative", "zIndex": "1", "padding": "0"}, children=[

            # ── Sticky Header ──────────────────────────────────────────
            html.Div(style={
                "background": "linear-gradient(90deg, #166534 0%, #14532D 50%, #4C1D95 100%)",
                "borderBottom": f"2px solid {CARD_BORDER}",
                "padding": "0 32px",
                "marginBottom": "32px",
                "position": "sticky", "top": "0", "zIndex": "100",
                "boxShadow": "0 4px 24px rgba(22,101,52,0.25), 0 1px 0 rgba(124,58,237,0.15)",
                # full-width: no inner maxWidth wrapper
            }, children=[
                html.Div(style={
                    "display": "flex", "alignItems": "center",
                    "justifyContent": "space-between", "height": "68px",
                }, children=[
                    # Logo
                    html.Div(style={"display": "flex", "alignItems": "center", "gap": "14px"}, children=[
                        html.Div("🔥", style={"fontSize": "28px", "filter": "drop-shadow(0 0 12px #FBBF24)"}),
                        html.Div([
                            html.Div("FIREWALL ANALYZER", style={
                                "fontSize": "18px", "fontWeight": "800",
                                "letterSpacing": "2px",
                                "background": f"linear-gradient(90deg, {AMBER_LIGHT}, {WHITE})",
                                "WebkitBackgroundClip": "text",
                                "WebkitTextFillColor": "transparent",
                            }),
                            html.Div("AI-Powered Security Intelligence", style={
                                "fontSize": "11px", "color": "rgba(255,255,255,0.60)",
                                "letterSpacing": "1px", "marginTop": "1px",
                            }),
                        ]),
                    ]),
                    # Nav pills
                    html.Div(style={"display": "flex", "alignItems": "center", "gap": "12px"}, children=[
                        # «Back to Main» button – only shown in detail view
                        html.Button(
                            "⬅  Main Dashboard",
                            id="back-to-main-btn",
                            n_clicks=0,
                            style={
                                "display": "none",   # hidden by default
                                "background": f"linear-gradient(135deg, {GREEN_DARK}, {VIOLET})",
                                "color": GREEN_LIGHT,
                                "border": f"1.5px solid {VIOLET_LIGHT}",
                                "borderRadius": "10px",
                                "padding": "8px 18px",
                                "fontWeight": "700",
                                "fontSize": "13px",
                                "cursor": "pointer",
                                "letterSpacing": "0.8px",
                                "transition": "all 0.2s ease",
                            },
                        ),
                        html.Div([
                            html.Span(className="pulse-dot"),
                            html.Span("LIVE", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "1.5px"}),
                        ], style={"display": "flex", "alignItems": "center"}),
                        html.Div(f"{total_records:,} Records", className="nav-pill"),
                    ]),
                ]),
            ]),

            # ── Body ──────────────────────────────────────────────────
            html.Div(style={"maxWidth": "1400px", "margin": "0 auto", "padding": "0 24px"}, children=[

                # ── VIEW 1: Main Dashboard ─────────────────────────────
                html.Div(id="main-view", children=[

                    # Big gradient heading — same Inter font weight as FIREWALL ANALYZER
                    html.Div(style={"marginBottom": "24px"}, children=[
                        html.Div("Key Metrics", style={
                            "fontFamily": FONT_FAMILY,
                            "fontSize": "28px",
                            "fontWeight": "800",
                            "letterSpacing": "0.5px",
                            "background": "linear-gradient(90deg, #166534 30%, #7C3AED 100%)",
                            "WebkitBackgroundClip": "text",
                            "WebkitTextFillColor": "transparent",
                            "backgroundClip": "text",
                        }),
                        html.Div("Live firewall statistics overview", style={
                            "fontSize": "13px",
                            "color": "rgba(20, 83, 45, 0.60)",
                            "marginTop": "4px",
                            "fontWeight": "400",
                        }),
                    ]),

                    # KPI row
                    html.Div(
                        id="kpi-row",
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(auto-fit, minmax(160px, 1fr))",
                            "gap": "16px",
                            "marginBottom": "40px",
                        },
                        children=[
                            kpi_card("📦", "Total Records",  f"{total_records:,}",  GREEN_LIGHT),
                            kpi_card("✅", "Allowed",         f"{allow_count:,}",    GREEN),
                            kpi_card("🚫", "Denied",          f"{deny_count:,}",     VIOLET),
                            kpi_card("❌", "Dropped",         f"{drop_count:,}",     VIOLET_LIGHT),
                            kpi_card("⚠️", "Anomalies (95%)", f"{anomaly_count:,}", "#F59E0B"),
                            kpi_card("🛡️", "Threat %",        f"{threat_pct}%",      TEXT_DARK, "Deny + Drop"),
                        ],
                    ),

                    # Feature selector card
                    html.Div(style={"position": "relative", "zIndex": "1000"}, children=[
                        html.Div(style=glass_card({"marginBottom": "0", "padding": "28px 32px"}), children=[
                            html.Div(style={"textAlign": "center", "marginBottom": "20px"}, children=[
                                html.Div("🔍  Explore a Feature", style={
                                    "fontSize": "22px", "fontWeight": "800",
                                    "background": "linear-gradient(90deg, #166534, #7C3AED)",
                                    "WebkitBackgroundClip": "text",
                                    "WebkitTextFillColor": "transparent",
                                    "backgroundClip": "text",
                                    "marginBottom": "8px",
                                }),
                                html.Div(
                                    "Pick any column below to deep-dive into its distribution, trend, and action breakdown.",
                                    style={"color": "rgba(20, 83, 45, 0.65)", "fontSize": "14px"},
                                ),
                            ]),
                            html.Div(style={"display": "flex", "justifyContent": "center"}, children=[
                                dcc.Dropdown(
                                    id="feature-dropdown",
                                    options=[{"label": str(c), "value": c} for c in raw_numeric_cols],
                                    value=None,
                                    clearable=True,
                                    placeholder="Select a feature to explore…",
                                    style={
                                        "width": "420px",
                                        "backgroundColor": "#2A0800",
                                        "color": "#FCD34D",
                                        "border": "1.5px solid #F97316",
                                        "borderRadius": "10px",
                                    },
                                    className="warm-dropdown",
                                ),
                            ]),
                        ]),
                    ]),

                    html.Div(style={
                        "textAlign": "center",
                        "padding": "40px 0 8px",
                        "borderTop": f"1px solid {CARD_BORDER}",
                        "color": "rgba(252,211,77,0.45)",
                        "fontSize": "12px",
                        "letterSpacing": "1px",
                        "marginTop": "40px",
                    }, children=[
                        "🔥 FIREWALL ANALYZER  •  AI-Powered Security Intelligence  •  Built with Plotly Dash & scikit-learn",
                    ]),
                ]),  # end #main-view

                # ── VIEW 2: Feature Detail ──────────────────────────────
                html.Div(id="detail-view", style={"display": "none"}, children=[

                    # Breadcrumb / title
                    html.Div(id="detail-title", style={
                        "fontSize": "20px", "fontWeight": "800",
                        "color": AMBER_LIGHT,
                        "marginBottom": "28px",
                        "letterSpacing": "1px",
                    }),

                    # Chart 1: Histogram
                    html.Div(style={"marginBottom": "20px"}, children=[
                        html.Div(className="chart-card", style=glass_card({"transition": "box-shadow 0.3s ease"}),
                                 children=[dcc.Graph(id="feature-histogram", config={"displayModeBar": False})]),
                    ]),

                    # Charts 2 & 3 side-by-side
                    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px", "marginBottom": "20px"}, children=[
                        html.Div(className="chart-card", style=glass_card({"transition": "box-shadow 0.3s ease"}),
                                 children=[dcc.Graph(id="traffic-over-time", config={"displayModeBar": False})]),
                        html.Div(className="chart-card", style=glass_card({"transition": "box-shadow 0.3s ease"}),
                                 children=[dcc.Graph(id="action-pie", config={"displayModeBar": False})]),
                    ]),

                    html.Div(style={
                        "textAlign": "center",
                        "padding": "20px 0 12px",
                        "borderTop": "2px solid rgba(124, 58, 237, 0.30)",
                        "color": "#7C3AED",
                        "fontSize": "13px",
                        "fontWeight": "600",
                        "letterSpacing": "1.2px",
                        "marginTop": "20px",
                    }, children=[
                        "🔥 FIREWALL ANALYZER  •  AI-Powered Security Intelligence  •  Built with Plotly Dash & scikit-learn",
                    ]),
                ]),  # end #detail-view

            ]),
        ]),

        dcc.Interval(id="interval", interval=30_000, n_intervals=0),
    ],
)

# ─────────────────────────────────────────────
#  Helper: apply template to figure
# ─────────────────────────────────────────────
def apply_theme(fig, title=""):
    fig.update_layout(plotly_template["layout"])
    if title:
        fig.update_layout(title_text=title)
    return fig


# ─────────────────────────────────────────────
#  Callback: View Toggle (Main ↔ Detail)
# ─────────────────────────────────────────────
@app.callback(
    [
        Output("main-view", "style"),
        Output("detail-view", "style"),
        Output("back-to-main-btn", "style"),
        Output("detail-title", "children"),
    ],
    [
        Input("feature-dropdown", "value"),
        Input("back-to-main-btn", "n_clicks"),
    ],
    prevent_initial_call=False,
)
def toggle_view(feature, back_clicks):
    from dash import ctx
    btn_base = {
        "background": f"linear-gradient(135deg, {AMBER_DARK}, {RED_DARK})",
        "color": AMBER_LIGHT,
        "border": f"1.5px solid {AMBER}",
        "borderRadius": "10px",
        "padding": "8px 18px",
        "fontWeight": "700",
        "fontSize": "13px",
        "cursor": "pointer",
        "letterSpacing": "0.8px",
        "transition": "all 0.2s ease",
    }

    triggered = ctx.triggered_id if ctx.triggered_id else ""

    # If back button clicked → go back to main
    if triggered == "back-to-main-btn":
        return (
            {"display": "block"},               # main-view visible
            {"display": "none"},                # detail-view hidden
            {**btn_base, "display": "none"},    # back-btn hidden
            "",
        )

    # If a feature is selected → show detail view
    if feature:
        return (
            {"display": "none"},                # main-view hidden
            {"display": "block"},               # detail-view visible
            {**btn_base, "display": "inline-block"},  # back-btn shown
            f"📈  Deep Dive: {feature}",
        )

    # Default → main view
    return (
        {"display": "block"},
        {"display": "none"},
        {**btn_base, "display": "none"},
        "",
    )


# ─────────────────────────────────────────────
#  Callback: Action Pie Chart
# ─────────────────────────────────────────────
@app.callback(
    Output("action-pie", "figure"),
    [Input("interval", "n_intervals"), Input("feature-dropdown", "value")]
)
def update_action_pie(_, __):
    try:
        action_col_raw = "Action" if "Action" in raw_df.columns else "action"
        if action_col_raw not in raw_df.columns:
            raise ValueError("No action column found")

        counts = raw_df[action_col_raw].value_counts().reset_index()
        counts.columns = ["Action", "Count"]

        fig = go.Figure(go.Pie(
            labels=counts["Action"],
            values=counts["Count"],
            hole=0.62,
            marker=dict(
                colors=["#4ADE80", AMBER, RED, AMBER_LIGHT],
                line=dict(color="rgba(0,0,0,0.4)", width=2),
            ),
            textinfo="label+percent",
            textfont=dict(color=WHITE, size=13),
            hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>",
        ))

        # Centre annotation
        total = counts["Count"].sum()
        fig.add_annotation(
            text=f"<b>{total:,}</b><br><span style='font-size:11px'>Total</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color=WHITE),
            align="center",
        )

        fig = apply_theme(fig, "🛡️  Action Distribution")
        fig.update_layout(transition={"duration": 600, "easing": "cubic-in-out"})
        return fig
    except Exception as e:
        logger.error(f"Action pie error: {e}")
        return _error_fig(str(e))



# ─────────────────────────────────────────────
#  Callback: Feature Histogram
# ─────────────────────────────────────────────
@app.callback(Output("feature-histogram", "figure"), Input("feature-dropdown", "value"))
def update_histogram(feature):
    try:
        if not feature or feature not in raw_df.columns:
            feature = default_feature
        valid_data = raw_df[feature].dropna()
        fig = go.Figure(go.Histogram(
            x=valid_data,
            nbinsx=60,
            marker=dict(color=AMBER, opacity=0.85, line=dict(color=AMBER_DARK, width=0.5)),
            hovertemplate="Range: %{x}<br>Count: %{y:,}<extra></extra>",
        ))
        fig.update_traces(marker_colorscale=[[0, AMBER_DARK], [1, AMBER_LIGHT]])
        fig = apply_theme(fig, f"📈  {str(feature)} — Histogram")
        fig.update_layout(
            xaxis_title=str(feature), yaxis_title="Frequency", bargap=0.03,
            transition={"duration": 600, "easing": "cubic-in-out"}
        )
        return fig
    except Exception as e:
        logger.error(f"Histogram error: {e}")
        return _error_fig(str(e))


# ─────────────────────────────────────────────
#  Callback: Traffic Over Time
# ─────────────────────────────────────────────
@app.callback(Output("traffic-over-time", "figure"), Input("feature-dropdown", "value"))
def update_traffic(feature):
    try:
        if not feature or feature not in raw_df.columns:
            feature = default_feature
        sample = raw_df[[feature]].dropna().reset_index(drop=True)
        if len(sample) > 3000:
            sample = sample.iloc[::len(sample) // 3000].reset_index(drop=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sample.index, y=sample[feature], mode="lines",
            line=dict(color=AMBER_LIGHT, width=1.5, shape="spline", smoothing=0.8),
            fill="tozeroy", fillcolor="rgba(249,115,22,0.20)",
            hovertemplate="Record: %{x}<br>Value: %{y:,.0f}<extra></extra>",
            name=str(feature),
        ))
        fig = apply_theme(fig, f"📉  {str(feature)} Over Records")
        fig.update_layout(
            xaxis_title="Record Index", yaxis_title=str(feature), showlegend=False,
            transition={"duration": 600, "easing": "cubic-in-out"}
        )
        return fig
    except Exception as e:
        logger.error(f"Traffic chart error: {e}")
        return _error_fig(str(e))



# ─────────────────────────────────────────────
#  Error figure helper
# ─────────────────────────────────────────────
def _error_fig(msg):
    fig = go.Figure()
    fig.add_annotation(
        text=f"⚠️ {msg}",
        x=0.5, y=0.5, xref="paper", yref="paper",
        showarrow=False,
        font=dict(color="#EF4444", size=14),
    )
    apply_theme(fig)
    return fig


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Starting Firewall Analyzer Dashboard (violet theme)...")
    app.run(debug=True, port=8050)
