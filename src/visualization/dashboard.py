"""
Interactive Dashboard Module
Creates an interactive Dash dashboard for CityPulse
"""

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging
from datetime import datetime, timedelta
import os
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "CityPulse: Urban Sentiment & Mobility Dashboard"


def load_data():
    """Load combined data"""
    data_path = PROJECT_ROOT / "data" / "combined" / "combined_data.csv"
    if data_path.exists():
        df = pd.read_csv(data_path)
        df['date'] = pd.to_datetime(df['date'])
        return df
    else:
        logger.warning(f"Data file not found: {data_path}")
        return pd.DataFrame()


def create_dashboard_layout(df: pd.DataFrame):
    """Create dashboard layout"""
    
    if df.empty:
        return html.Div([
            html.H1("CityPulse Dashboard", className="text-center"),
            html.Hr(),
            html.Div("No data available. Please run data collection and processing scripts first.",
                    className="alert alert-warning")
        ])
    
    # Get date range
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    # Get available complaint types (if available)
    complaint_types = ['All']
    if 'service_request_type' in df.columns:
        complaint_types.extend(df['service_request_type'].dropna().unique().tolist()[:10])
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("CityPulse", className="text-center mb-4"),
                html.H2("Urban Sentiment & Mobility Dashboard", className="text-center text-muted mb-4"),
                html.Hr()
            ])
        ]),
        
        # Filters
        dbc.Row([
            dbc.Col([
                html.Label("Date Range:", className="fw-bold"),
                dcc.DatePickerRange(
                    id='date-picker',
                    start_date=min_date,
                    end_date=max_date,
                    display_format='YYYY-MM-DD',
                    className="mb-3"
                )
            ], md=6),
            dbc.Col([
                html.Label("Complaint Type:", className="fw-bold"),
                dcc.Dropdown(
                    id='complaint-type-filter',
                    options=[{'label': ct, 'value': ct} for ct in complaint_types],
                    value='All',
                    className="mb-3"
                )
            ], md=6)
        ], className="mb-4"),
        
        # Key Metrics Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Avg Sentiment", className="card-title"),
                        html.H2(id="avg-sentiment", className="text-primary")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Total CTA Rides", className="card-title"),
                        html.H2(id="total-rides", className="text-success")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("311 Complaints", className="card-title"),
                        html.H2(id="total-complaints", className="text-warning")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Tweets", className="card-title"),
                        html.H2(id="total-tweets", className="text-info")
                    ])
                ])
            ], md=3)
        ], className="mb-4"),
        
        # Main Charts
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="sentiment-ridership-chart")
            ], md=12)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="time-series-chart")
            ], md=12)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="sentiment-distribution-chart")
            ], md=6),
            dbc.Col([
                dcc.Graph(id="correlation-heatmap")
            ], md=6)
        ], className="mb-4"),
        
        # Top Hashtags Section
        dbc.Row([
            dbc.Col([
                html.H4("Top Hashtags", className="mb-3"),
                dcc.Graph(id="top-hashtags-chart")
            ], md=12)
        ], className="mb-4"),
        
        # Map Section (if geospatial data available)
        dbc.Row([
            dbc.Col([
                html.H4("Complaint Density Map", className="mb-3"),
                dcc.Graph(id="complaint-map")
            ], md=12)
        ], className="mb-4"),
        
        # Footer
        dbc.Row([
            dbc.Col([
                html.Hr(),
                html.P("CityPulse Dashboard - Chicago Urban Sentiment & Mobility Analysis",
                      className="text-center text-muted")
            ])
        ])
    ], fluid=True)


@app.callback(
    [Output('sentiment-ridership-chart', 'figure'),
     Output('time-series-chart', 'figure'),
     Output('sentiment-distribution-chart', 'figure'),
     Output('correlation-heatmap', 'figure'),
     Output('top-hashtags-chart', 'figure'),
     Output('complaint-map', 'figure'),
     Output('avg-sentiment', 'children'),
     Output('total-rides', 'children'),
     Output('total-complaints', 'children'),
     Output('total-tweets', 'children')],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('complaint-type-filter', 'value')]
)
def update_dashboard(start_date, end_date, complaint_type):
    """Update dashboard based on filters"""
    
    df = load_data()
    
    if df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5)
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "N/A", "N/A", "N/A", "N/A"
    
    # Filter by date
    if start_date and end_date:
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        df_filtered = df[mask].copy()
    else:
        df_filtered = df.copy()
    
    # Filter by complaint type (if applicable)
    # This would require additional data processing
    
    # 1. Sentiment vs Ridership Chart
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    
    if 'avg_polarity' in df_filtered.columns:
        fig1.add_trace(
            go.Scatter(
                x=df_filtered['date'],
                y=df_filtered['avg_polarity'],
                name='Sentiment Polarity',
                line=dict(color='blue', width=2),
                mode='lines+markers'
            ),
            secondary_y=False
        )
    
    if 'total_cta_rides' in df_filtered.columns:
        # Normalize ridership
        rides = df_filtered['total_cta_rides']
        if rides.max() > 0:
            rides_norm = (rides - rides.min()) / (rides.max() - rides.min())
            fig1.add_trace(
                go.Scatter(
                    x=df_filtered['date'],
                    y=rides_norm,
                    name='CTA Ridership (Normalized)',
                    line=dict(color='red', width=2),
                    mode='lines+markers'
                ),
                secondary_y=True
            )
    
    fig1.update_xaxes(title_text="Date")
    fig1.update_yaxes(title_text="Sentiment Polarity", secondary_y=False)
    fig1.update_yaxes(title_text="Ridership (Normalized)", secondary_y=True)
    fig1.update_layout(
        title="Sentiment Trends vs. Daily CTA Ridership",
        hovermode='x unified',
        height=400,
        hoverlabel=dict(bgcolor="white", font_size=12)
    )
    
    # 2. Time Series Chart
    fig2 = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Sentiment Polarity", "CTA Ridership", "311 Complaints")
    )
    
    if 'avg_polarity' in df_filtered.columns:
        fig2.add_trace(
            go.Scatter(x=df_filtered['date'], y=df_filtered['avg_polarity'],
                      name='Sentiment', mode='lines'),
            row=1, col=1
        )
    
    if 'total_cta_rides' in df_filtered.columns:
        fig2.add_trace(
            go.Scatter(x=df_filtered['date'], y=df_filtered['total_cta_rides'],
                      name='Ridership', mode='lines', line=dict(color='green')),
            row=2, col=1
        )
    
    if 'total_311_complaints' in df_filtered.columns:
        fig2.add_trace(
            go.Scatter(x=df_filtered['date'], y=df_filtered['total_311_complaints'],
                      name='Complaints', mode='lines', line=dict(color='orange')),
            row=3, col=1
        )
    
    fig2.update_xaxes(title_text="Date", row=3, col=1)
    fig2.update_layout(height=600, showlegend=False, title="Time Series Overview")
    
    # 3. Sentiment Distribution
    if 'avg_polarity' in df_filtered.columns:
        fig3 = go.Figure(data=[go.Histogram(x=df_filtered['avg_polarity'], nbinsx=30)])
        fig3.update_layout(
            title="Sentiment Polarity Distribution",
            xaxis_title="Polarity Score",
            yaxis_title="Frequency",
            height=300
        )
    else:
        fig3 = go.Figure()
        fig3.add_annotation(text="No sentiment data", xref="paper", yref="paper", x=0.5, y=0.5)
    
    # 4. Correlation Heatmap
    numeric_cols = df_filtered.select_dtypes(include=['number']).columns
    key_cols = ['avg_polarity', 'total_cta_rides', 'total_311_complaints', 
                'positive', 'negative', 'transit_related_complaints']
    corr_cols = [col for col in key_cols if col in numeric_cols]
    
    if len(corr_cols) >= 2:
        corr_matrix = df_filtered[corr_cols].corr()
        fig4 = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            colorbar=dict(title="Correlation")
        ))
        fig4.update_layout(
            title="Correlation Matrix",
            height=300
        )
    else:
        fig4 = go.Figure()
        fig4.add_annotation(text="Insufficient data for correlation", xref="paper", yref="paper", x=0.5, y=0.5)
    
    # 5. Top Hashtags Chart
    # Load tweet data to extract hashtags
    tweets_path = PROJECT_ROOT / "data" / "cleaned" / "tweets.csv"
    if tweets_path.exists():
        try:
            df_tweets = pd.read_csv(str(tweets_path))
            if 'hashtags' in df_tweets.columns:
                # Extract and count hashtags
                all_hashtags = []
                for hashtag_str in df_tweets['hashtags'].dropna():
                    if isinstance(hashtag_str, str):
                        hashtags = [h.strip() for h in hashtag_str.split(',')]
                        all_hashtags.extend(hashtags)
                
                if all_hashtags:
                    hashtag_counts = pd.Series(all_hashtags).value_counts().head(10)
                    fig5 = go.Figure(data=[
                        go.Bar(x=hashtag_counts.values, y=hashtag_counts.index, orientation='h')
                    ])
                    fig5.update_layout(
                        title="Top 10 Hashtags",
                        xaxis_title="Count",
                        yaxis_title="Hashtag",
                        height=400
                    )
                else:
                    fig5 = go.Figure()
                    fig5.add_annotation(text="No hashtag data available", xref="paper", yref="paper", x=0.5, y=0.5)
            else:
                fig5 = go.Figure()
                fig5.add_annotation(text="No hashtag data available", xref="paper", yref="paper", x=0.5, y=0.5)
        except Exception as e:
            logger.warning(f"Error loading hashtags: {e}")
            fig5 = go.Figure()
            fig5.add_annotation(text="No hashtag data available", xref="paper", yref="paper", x=0.5, y=0.5)
    else:
        fig5 = go.Figure()
        fig5.add_annotation(text="No hashtag data available", xref="paper", yref="paper", x=0.5, y=0.5)
    
    # 6. Complaint Map (if geospatial data available)
    complaints_path = PROJECT_ROOT / "data" / "cleaned" / "311_data.csv"
    if complaints_path.exists():
        try:
            df_complaints = pd.read_csv(str(complaints_path))
            if 'latitude' in df_complaints.columns and 'longitude' in df_complaints.columns:
                # Filter valid coordinates
                df_map = df_complaints[
                    (df_complaints['latitude'].notna()) & 
                    (df_complaints['longitude'].notna()) &
                    (df_complaints['latitude'] != 0) &
                    (df_complaints['longitude'] != 0)
                ]
                
                if len(df_map) > 0:
                    fig6 = px.scatter_mapbox(
                        df_map.head(1000),  # Limit for performance
                        lat='latitude',
                        lon='longitude',
                        hover_data=['service_request_type', 'created_date'],
                        zoom=10,
                        height=400,
                        mapbox_style="open-street-map"
                    )
                    fig6.update_layout(title="311 Complaint Locations")
                else:
                    fig6 = go.Figure()
                    fig6.add_annotation(text="No geospatial data available", xref="paper", yref="paper", x=0.5, y=0.5)
            else:
                fig6 = go.Figure()
                fig6.add_annotation(text="No geospatial data available", xref="paper", yref="paper", x=0.5, y=0.5)
        except Exception as e:
            logger.warning(f"Error creating map: {e}")
            fig6 = go.Figure()
            fig6.add_annotation(text="No geospatial data available", xref="paper", yref="paper", x=0.5, y=0.5)
    else:
        fig6 = go.Figure()
        fig6.add_annotation(text="No geospatial data available", xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Calculate metrics
    avg_sentiment = f"{df_filtered['avg_polarity'].mean():.3f}" if 'avg_polarity' in df_filtered.columns else "N/A"
    total_rides = f"{df_filtered['total_cta_rides'].sum():,.0f}" if 'total_cta_rides' in df_filtered.columns else "N/A"
    total_complaints = f"{df_filtered['total_311_complaints'].sum():,.0f}" if 'total_311_complaints' in df_filtered.columns else "N/A"
    total_tweets = f"{df_filtered['total_tweets'].sum():,.0f}" if 'total_tweets' in df_filtered.columns else "N/A"
    
    return fig1, fig2, fig3, fig4, fig5, fig6, avg_sentiment, total_rides, total_complaints, total_tweets


def run_dashboard(host='127.0.0.1', port=8050, debug=True):
    """Run the dashboard server"""
    df = load_data()
    app.layout = create_dashboard_layout(df)
    
    logger.info(f"Starting dashboard server on http://{host}:{port}")
    app.run_server(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_dashboard()

