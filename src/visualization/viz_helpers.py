"""
Visualization Helper Functions
Creates simple, easy-to-understand charts for non-technical users
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional


def create_simple_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, 
                           title: str, color_scheme: Dict = None,
                           show_values: bool = True) -> go.Figure:
    """
    Create a clean, simple bar chart
    
    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Chart title
        color_scheme: Dictionary with color mappings (optional)
        show_values: Whether to show values on bars
    
    Returns:
        Plotly figure
    """
    if df.empty or x_col not in df.columns or y_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper", x=0.5, y=0.5,
            font=dict(size=14)
        )
        fig.update_layout(title=title, height=400)
        return fig
    
    # Default colors
    if color_scheme is None:
        colors = px.colors.qualitative.Set3
    else:
        colors = [color_scheme.get(row[x_col], '#3498db') for _, row in df.iterrows()]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[y_col],
        marker=dict(
            color=colors if isinstance(colors, list) else colors[0],
            line=dict(color='rgba(0,0,0,0.1)', width=1)
        ),
        text=[f"{val:,.0f}" if isinstance(val, (int, float)) else str(val) 
              for val in df[y_col]] if show_values else None,
        textposition='outside',
        hovertemplate=f'<b>%{{x}}</b><br>{y_col}: %{{y:,.0f}}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, family="Arial, sans-serif"),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=x_col,
            tickangle=-45 if len(df) > 7 else 0,
            showgrid=False
        ),
        yaxis=dict(
            title=y_col,
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        margin=dict(l=50, r=50, t=80, b=100)
    )
    
    return fig


def create_insight_card(title: str, value: str, insight_text: str, 
                       icon: str = "info-circle", color: str = "#3498db") -> Dict:
    """
    Create data for an insight card component
    
    Args:
        title: Card title
        value: Main value to display
        insight_text: Plain-language insight
        icon: Font Awesome icon name
        color: Accent color
    
    Returns:
        Dictionary with card data
    """
    return {
        'title': title,
        'value': value,
        'insight': insight_text,
        'icon': icon,
        'color': color
    }


def create_correlation_heatmap(corr_matrix: pd.DataFrame, 
                               labels: Dict = None,
                               title: str = "Correlation Matrix") -> go.Figure:
    """
    Create an easy-to-read correlation heatmap
    
    Args:
        corr_matrix: Correlation matrix DataFrame
        labels: Dictionary mapping column names to display labels
        title: Chart title
    
    Returns:
        Plotly figure
    """
    if corr_matrix.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No correlation data available",
            xref="paper", yref="paper", x=0.5, y=0.5,
            font=dict(size=14)
        )
        fig.update_layout(title=title, height=400)
        return fig
    
    # Apply labels if provided
    if labels:
        corr_matrix = corr_matrix.rename(columns=labels, index=labels)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(
            title="Correlation",
            titleside="right"
        ),
        hovertemplate='%{y} vs %{x}<br>Correlation: %{z:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, family="Arial, sans-serif"),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(title=""),
        yaxis=dict(title=""),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,
        margin=dict(l=100, r=50, t=80, b=100)
    )
    
    return fig


def create_health_gauge(score: float, title: str = "Health Score",
                      color_ranges: Dict = None) -> go.Figure:
    """
    Create a gauge chart for health scores
    
    Args:
        score: Score value (0-10)
        title: Chart title
        color_ranges: Dictionary with color ranges (default: green/yellow/orange/red)
    
    Returns:
        Plotly figure
    """
    if color_ranges is None:
        color_ranges = {
            'excellent': {'min': 8, 'max': 10, 'color': '#28a745'},
            'good': {'min': 6, 'max': 8, 'color': '#ffc107'},
            'fair': {'min': 4, 'max': 6, 'color': '#fd7e14'},
            'needs_attention': {'min': 0, 'max': 4, 'color': '#dc3545'}
        }
    
    # Determine current range
    current_range = 'needs_attention'
    for range_name, range_data in color_ranges.items():
        if range_data['min'] <= score <= range_data['max']:
            current_range = range_name
            break
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        gauge={
            'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color_ranges[current_range]['color']},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 4], 'color': 'lightgray'},
                {'range': [4, 6], 'color': 'gray'},
                {'range': [6, 8], 'color': 'lightgray'},
                {'range': [8, 10], 'color': 'gray'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 10
            }
        },
        number={'font': {'size': 40, 'color': color_ranges[current_range]['color']}}
    ))
    
    fig.update_layout(
        height=400,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig


def format_number_for_display(value: float, metric_type: str = "count") -> str:
    """
    Format numbers with appropriate units for display
    
    Args:
        value: Numeric value
        metric_type: Type of metric (count, percentage, currency, etc.)
    
    Returns:
        Formatted string
    """
    if pd.isna(value) or value == 0:
        return "0"
    
    if metric_type == "count":
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value/1_000:.1f}K"
        else:
            return f"{value:,.0f}"
    elif metric_type == "percentage":
        return f"{value:.1f}%"
    elif metric_type == "score":
        return f"{value:.1f}/10"
    else:
        return f"{value:,.0f}"


def create_multi_metric_bar_chart(df: pd.DataFrame, x_col: str, 
                                  y_cols: List[str], title: str,
                                  colors: List[str] = None) -> go.Figure:
    """
    Create a bar chart with multiple metrics
    
    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_cols: List of column names for y-axis (multiple metrics)
        title: Chart title
        colors: List of colors for each metric
    
    Returns:
        Plotly figure
    """
    if df.empty or x_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper", x=0.5, y=0.5,
            font=dict(size=14)
        )
        fig.update_layout(title=title, height=400)
        return fig
    
    if colors is None:
        colors = px.colors.qualitative.Set3[:len(y_cols)]
    
    fig = go.Figure()
    
    for i, y_col in enumerate(y_cols):
        if y_col not in df.columns:
            continue
        
        fig.add_trace(go.Bar(
            name=y_col.replace('_', ' ').title(),
            x=df[x_col],
            y=df[y_col],
            marker=dict(color=colors[i % len(colors)]),
            hovertemplate=f'<b>%{{x}}</b><br>{y_col}: %{{y:,.0f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, family="Arial, sans-serif"),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=x_col,
            tickangle=-45 if len(df) > 7 else 0,
            showgrid=False
        ),
        yaxis=dict(
            title="Value",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)'
        ),
        barmode='group',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        margin=dict(l=50, r=50, t=80, b=100),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

