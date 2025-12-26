import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import dash_auth
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from database import NepseDatabase
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
db = NepseDatabase()

# Create Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

app.title = "NEPSE Investment Dashboard"

# Add password protection
VALID_USERNAME_PASSWORD_PAIRS = {
    Config.DASHBOARD_USERNAME: Config.DASHBOARD_PASSWORD
}

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

# Color scheme
COLORS = {
    'background': '#f8f9fa',
    'card': '#ffffff',
    'primary': '#3498db',
    'success': '#27ae60',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#16a085'
}

# Layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("📊 NEPSE Investment Dashboard", className="text-center mb-4 mt-4"),
            html.P(
                "Real-time analysis of Nepal Stock Exchange data for smarter investment decisions",
                className="text-center text-muted mb-4"
            )
        ])
    ]),

    # Navigation Tabs
    dbc.Tabs([
        dbc.Tab(label="📈 Overview", tab_id="overview"),
        dbc.Tab(label="🔄 Repeat Analysis", tab_id="repeat"),
        dbc.Tab(label="🏢 Broker Intelligence", tab_id="brokers"),
        dbc.Tab(label="🔍 Stock Lookup", tab_id="lookup"),
        dbc.Tab(label="🎯 IPO Tracker", tab_id="ipo"),
        dbc.Tab(label="📊 Signals & Alerts", tab_id="signals"),
    ], id="tabs", active_tab="overview", className="mb-4"),

    # Tab Content
    html.Div(id="tab-content"),

    # Footer
    html.Hr(),
    html.P(
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data retention: {Config.DATA_RETENTION_DAYS} days",
        className="text-center text-muted small"
    )
], fluid=True, style={'backgroundColor': COLORS['background']})


# Callback for tab content
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab_content(active_tab):
    if active_tab == "overview":
        return create_overview_tab()
    elif active_tab == "repeat":
        return create_repeat_analysis_tab()
    elif active_tab == "brokers":
        return create_broker_tab()
    elif active_tab == "lookup":
        return create_lookup_tab()
    elif active_tab == "ipo":
        return create_ipo_tab()
    elif active_tab == "signals":
        return create_signals_tab()


def create_overview_tab():
    """Overview tab with today's summary"""
    today = datetime.now().strftime('%Y-%m-%d')

    # Get today's data
    gainers = db.get_data('top_gainers', days=1)
    losers = db.get_data('top_losers', days=1)
    traded = db.get_data('top_traded', days=1)
    turnovers = db.get_data('top_turnovers', days=1)

    return dbc.Container([
        # Summary Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("📈 Top Gainers", className="card-title"),
                        html.H2(len(gainers), className="text-success"),
                        html.P("stocks today", className="text-muted")
                    ])
                ], color="light")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("📉 Top Losers", className="card-title"),
                        html.H2(len(losers), className="text-danger"),
                        html.P("stocks today", className="text-muted")
                    ])
                ], color="light")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("💹 Top Traded", className="card-title"),
                        html.H2(len(traded), className="text-info"),
                        html.P("stocks today", className="text-muted")
                    ])
                ], color="light")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("💰 Top Turnovers", className="card-title"),
                        html.H2(len(turnovers), className="text-warning"),
                        html.P("stocks today", className="text-muted")
                    ])
                ], color="light")
            ], width=3),
        ], className="mb-4"),

        # Top Gainers Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📈 Top Gainers Today")),
                    dbc.CardBody([
                        create_data_table(gainers, 'gainers')
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📉 Top Losers Today")),
                    dbc.CardBody([
                        create_data_table(losers, 'losers')
                    ])
                ])
            ], width=6),
        ], className="mb-4"),

        # Top Traded and Turnovers
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("💹 Top Traded Shares")),
                    dbc.CardBody([
                        create_data_table(traded, 'traded')
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("💰 Top Turnovers")),
                    dbc.CardBody([
                        create_data_table(turnovers, 'turnovers')
                    ])
                ])
            ], width=6),
        ]),
    ], fluid=True)


def create_repeat_analysis_tab():
    """Repeat Analysis tab with drill-down functionality"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("🔄 Repeat Analysis - Find Consistent Performers"),
                html.P("Identify stocks that repeatedly appear in top lists", className="text-muted")
            ])
        ], className="mb-4"),

        # Filters
        dbc.Row([
            dbc.Col([
                html.Label("Category:"),
                dcc.Dropdown(
                    id='repeat-category',
                    options=[
                        {'label': '📈 Top Gainers', 'value': 'top_gainers'},
                        {'label': '📉 Top Losers', 'value': 'top_losers'},
                        {'label': '💹 Top Traded', 'value': 'top_traded'},
                        {'label': '💰 Top Turnovers', 'value': 'top_turnovers'},
                        {'label': '🔄 Top Transactions', 'value': 'top_transactions'},
                    ],
                    value='top_gainers',
                    clearable=False
                )
            ], width=4),
            dbc.Col([
                html.Label("Time Period:"),
                dcc.Dropdown(
                    id='repeat-days',
                    options=[
                        {'label': 'Last 7 days', 'value': 7},
                        {'label': 'Last 14 days', 'value': 14},
                        {'label': 'Last 30 days', 'value': 30},
                        {'label': 'Last 60 days', 'value': 60},
                        {'label': 'Last 90 days', 'value': 90},
                    ],
                    value=30,
                    clearable=False
                )
            ], width=4),
            dbc.Col([
                html.Label("Min. Occurrences:"),
                dcc.Slider(
                    id='repeat-min-occur',
                    min=2,
                    max=10,
                    step=1,
                    value=3,
                    marks={i: str(i) for i in range(2, 11)},
                )
            ], width=4),
        ], className="mb-4"),

        # Results
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("🎯 Repeat Analysis Results")),
                    dbc.CardBody([
                        html.Div(id='repeat-results')
                    ])
                ])
            ])
        ], className="mb-4"),

        # Drill-down section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📅 Date-wise Drill-down")),
                    dbc.CardBody([
                        html.P("Click on a stock in the table above to see date-wise details", className="text-muted"),
                        html.Div(id='drilldown-content')
                    ])
                ])
            ])
        ])
    ], fluid=True)


def create_broker_tab():
    """Broker Intelligence tab"""
    brokers = db.get_data('top_brokers', days=30)

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("🏢 Broker Intelligence"),
                html.P("Analyze top brokers' activities", className="text-muted")
            ])
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                html.Label("Time Period:"),
                dcc.Dropdown(
                    id='broker-days',
                    options=[
                        {'label': 'Last 7 days', 'value': 7},
                        {'label': 'Last 30 days', 'value': 30},
                        {'label': 'Last 60 days', 'value': 60},
                        {'label': 'Last 90 days', 'value': 90},
                    ],
                    value=30,
                    clearable=False
                )
            ], width=4),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("🏆 Top Brokers by Total Amount")),
                    dbc.CardBody([
                        html.Div(id='broker-results')
                    ])
                ])
            ])
        ])
    ], fluid=True)


def create_lookup_tab():
    """Stock Lookup tab"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("🔍 Stock Lookup"),
                html.P("Search and analyze individual stocks", className="text-muted")
            ])
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                html.Label("Enter Stock Symbol:"),
                dcc.Input(
                    id='stock-symbol',
                    type='text',
                    placeholder='e.g., NABIL, UPPER, etc.',
                    className='form-control',
                    style={'textTransform': 'uppercase'}
                )
            ], width=6),
            dbc.Col([
                html.Label("Time Period:"),
                dcc.Dropdown(
                    id='lookup-days',
                    options=[
                        {'label': 'Last 7 days', 'value': 7},
                        {'label': 'Last 30 days', 'value': 30},
                        {'label': 'Last 60 days', 'value': 60},
                        {'label': 'Last 90 days', 'value': 90},
                        {'label': 'All available data', 'value': 365},
                    ],
                    value=30,
                    clearable=False
                )
            ], width=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Button("Search", id='lookup-button', color="primary", className="mb-4")
            ])
        ]),

        dbc.Row([
            dbc.Col([
                html.Div(id='lookup-results')
            ])
        ])
    ], fluid=True)


def create_ipo_tab():
    """IPO Tracker tab"""
    ipo_data = db.get_data('ipo_info', days=60)

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("🎯 IPO Tracker"),
                html.P("Track Initial Public Offerings", className="text-muted")
            ])
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📋 Current & Upcoming IPOs")),
                    dbc.CardBody([
                        create_ipo_table(ipo_data) if not ipo_data.empty else html.P("No IPO data available", className="text-muted")
                    ])
                ])
            ])
        ])
    ], fluid=True)


def create_signals_tab():
    """Signals & Alerts tab"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("📊 Signals & Alerts"),
                html.P("Investment signals based on historical patterns", className="text-muted")
            ])
        ], className="mb-4"),

        # Hot Stocks (Repeated Gainers)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("🔥 Hot Stocks - Repeated Gainers")),
                    dbc.CardBody([
                        html.Div(id='hot-stocks-signal')
                    ])
                ], color="success", outline=True)
            ])
        ], className="mb-4"),

        # Danger Stocks (Repeated Losers)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("⚠️ Danger Zone - Repeated Losers")),
                    dbc.CardBody([
                        html.Div(id='danger-stocks-signal')
                    ])
                ], color="danger", outline=True)
            ])
        ], className="mb-4"),

        # Consistent Performers
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("⭐ Most Active Stocks")),
                    dbc.CardBody([
                        html.Div(id='active-stocks-signal')
                    ])
                ], color="info", outline=True)
            ])
        ])
    ], fluid=True)


def create_data_table(df, table_type):
    """Create a formatted data table"""
    if df.empty:
        return html.P("No data available", className="text-muted")

    # Select columns based on table type
    if table_type == 'gainers' or table_type == 'losers':
        columns = ['symbol', 'ltp', 'change_percent', 'turnover']
        column_names = ['Symbol', 'LTP', 'Change %', 'Turnover']
    elif table_type == 'traded':
        columns = ['symbol', 'qty', 'ltp', 'change_percent']
        column_names = ['Symbol', 'Quantity', 'LTP', 'Change %']
    elif table_type == 'turnovers':
        columns = ['symbol', 'turnover', 'ltp', 'change_percent']
        column_names = ['Symbol', 'Turnover', 'LTP', 'Change %']
    else:
        columns = df.columns.tolist()[:4]
        column_names = columns

    # Filter columns that exist in dataframe
    available_columns = [col for col in columns if col in df.columns]

    if not available_columns:
        return html.P("No data available", className="text-muted")

    df_display = df[available_columns].head(10).copy()

    # Format numbers
    if 'change_percent' in df_display.columns:
        df_display['change_percent'] = df_display['change_percent'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
    if 'turnover' in df_display.columns:
        df_display['turnover'] = df_display['turnover'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
    if 'qty' in df_display.columns:
        df_display['qty'] = df_display['qty'].apply(lambda x: f"{x:,}" if pd.notna(x) else "N/A")

    return dash_table.DataTable(
        data=df_display.to_dict('records'),
        columns=[{"name": column_names[i] if i < len(column_names) else col, "id": col}
                 for i, col in enumerate(available_columns)],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': COLORS['primary'], 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ]
    )


def create_ipo_table(df):
    """Create IPO information table"""
    if df.empty:
        return html.P("No IPO data available", className="text-muted")

    columns = ['company_name', 'opening_date', 'closing_date', 'price_per_share', 'status']
    available_columns = [col for col in columns if col in df.columns]

    if not available_columns:
        return html.P("No data available", className="text-muted")

    df_display = df[available_columns].copy()

    return dash_table.DataTable(
        data=df_display.to_dict('records'),
        columns=[{"name": col.replace('_', ' ').title(), "id": col} for col in available_columns],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#9b59b6', 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        page_size=20
    )


# Callbacks for Repeat Analysis
@app.callback(
    Output('repeat-results', 'children'),
    [Input('repeat-category', 'value'),
     Input('repeat-days', 'value'),
     Input('repeat-min-occur', 'value')]
)
def update_repeat_analysis(category, days, min_occur):
    df = db.get_repeat_analysis(category, days=days, min_occurrences=min_occur)

    if df.empty:
        return html.P(f"No stocks found with {min_occur}+ occurrences in the last {days} days", className="text-muted")

    # Create interactive table
    df_display = df.copy()
    if 'avg_change' in df_display.columns:
        df_display['avg_change'] = df_display['avg_change'].apply(lambda x: f"{x:.2f}%")
    if 'max_change' in df_display.columns:
        df_display['max_change'] = df_display['max_change'].apply(lambda x: f"{x:.2f}%")
    if 'min_change' in df_display.columns:
        df_display['min_change'] = df_display['min_change'].apply(lambda x: f"{x:.2f}%")

    return dash_table.DataTable(
        id='repeat-table',
        data=df_display.to_dict('records'),
        columns=[{"name": col.replace('_', ' ').title(), "id": col} for col in df_display.columns if col != 'dates'],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': COLORS['primary'], 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            },
            {
                'if': {'column_id': 'occurrences'},
                'backgroundColor': '#ffffcc',
                'fontWeight': 'bold'
            }
        ],
        row_selectable='single',
        selected_rows=[],
        page_size=15
    )


# Callback for Broker Analysis
@app.callback(
    Output('broker-results', 'children'),
    Input('broker-days', 'value')
)
def update_broker_analysis(days):
    df = db.get_data('top_brokers', days=days)

    if df.empty:
        return html.P("No broker data available", className="text-muted")

    # Aggregate by broker
    broker_summary = df.groupby('broker_no').agg({
        'broker_name': 'first',
        'buy_amount': 'sum',
        'sell_amount': 'sum',
        'total_amount': 'sum'
    }).reset_index()

    broker_summary = broker_summary.sort_values('total_amount', ascending=False).head(20)

    # Format numbers
    broker_summary['buy_amount'] = broker_summary['buy_amount'].apply(lambda x: f"{x:,.0f}")
    broker_summary['sell_amount'] = broker_summary['sell_amount'].apply(lambda x: f"{x:,.0f}")
    broker_summary['total_amount'] = broker_summary['total_amount'].apply(lambda x: f"{x:,.0f}")

    return dash_table.DataTable(
        data=broker_summary.to_dict('records'),
        columns=[
            {"name": "Broker No", "id": "broker_no"},
            {"name": "Broker Name", "id": "broker_name"},
            {"name": "Buy Amount", "id": "buy_amount"},
            {"name": "Sell Amount", "id": "sell_amount"},
            {"name": "Total Amount", "id": "total_amount"},
        ],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': COLORS['info'], 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        page_size=20
    )


# Callback for Stock Lookup
@app.callback(
    Output('lookup-results', 'children'),
    [Input('lookup-button', 'n_clicks')],
    [State('stock-symbol', 'value'),
     State('lookup-days', 'value')]
)
def stock_lookup(n_clicks, symbol, days):
    if not n_clicks or not symbol:
        return html.P("Enter a stock symbol and click Search", className="text-muted")

    symbol = symbol.upper().strip()

    # Search in all tables
    tables = ['top_gainers', 'top_losers', 'top_traded', 'top_turnovers', 'top_transactions']
    results = []

    for table in tables:
        df = db.get_data(table, days=days)
        if not df.empty and 'symbol' in df.columns:
            stock_data = df[df['symbol'] == symbol]
            if not stock_data.empty:
                results.append((table.replace('_', ' ').title(), stock_data))

    if not results:
        return dbc.Alert(f"No data found for symbol: {symbol}", color="warning")

    # Create output
    output = [
        html.H5(f"📊 Results for {symbol}", className="mb-3"),
        dbc.Alert(f"Found {sum(len(df) for _, df in results)} records across {len(results)} categories", color="info")
    ]

    for category, df in results:
        output.append(
            dbc.Card([
                dbc.CardHeader(html.H6(f"{category} ({len(df)} occurrences)")),
                dbc.CardBody([
                    create_data_table(df, category.lower().replace(' ', '_'))
                ])
            ], className="mb-3")
        )

    return output


# Callbacks for Signals tab
@app.callback(
    Output('hot-stocks-signal', 'children'),
    Input('tabs', 'active_tab')
)
def update_hot_stocks(active_tab):
    if active_tab != 'signals':
        return ""

    df = db.get_repeat_analysis('top_gainers', days=7, min_occurrences=3)

    if df.empty:
        return html.P("No hot stocks detected in the last 7 days", className="text-muted")

    return create_signal_table(df, 'success')


@app.callback(
    Output('danger-stocks-signal', 'children'),
    Input('tabs', 'active_tab')
)
def update_danger_stocks(active_tab):
    if active_tab != 'signals':
        return ""

    df = db.get_repeat_analysis('top_losers', days=7, min_occurrences=3)

    if df.empty:
        return html.P("No danger stocks detected in the last 7 days", className="text-muted")

    return create_signal_table(df, 'danger')


@app.callback(
    Output('active-stocks-signal', 'children'),
    Input('tabs', 'active_tab')
)
def update_active_stocks(active_tab):
    if active_tab != 'signals':
        return ""

    df = db.get_repeat_analysis('top_traded', days=7, min_occurrences=3)

    if df.empty:
        return html.P("No highly active stocks detected", className="text-muted")

    return create_signal_table(df, 'info')


def create_signal_table(df, color):
    """Create signal table with color coding"""
    df_display = df.copy()

    if 'avg_change' in df_display.columns:
        df_display['avg_change'] = df_display['avg_change'].apply(lambda x: f"{x:.2f}%")

    color_map = {'success': '#27ae60', 'danger': '#e74c3c', 'info': '#16a085'}

    return dash_table.DataTable(
        data=df_display.head(10).to_dict('records'),
        columns=[{"name": col.replace('_', ' ').title(), "id": col}
                 for col in df_display.columns if col != 'dates'],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': color_map.get(color, COLORS['primary']),
                     'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ]
    )


if __name__ == '__main__':
    app.run_server(
        host=Config.DASHBOARD_HOST,
        port=Config.DASHBOARD_PORT,
        debug=Config.DEBUG_MODE
    )
