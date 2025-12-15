"""
Visualization Module
Creates exploratory visualizations for the CityPulse project
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging
from typing import Optional
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


def plot_sentiment_vs_ridership(df: pd.DataFrame, output_path: Optional[str] = None) -> go.Figure:
    """
    Create line chart: sentiment trends vs. daily ridership
    
    Args:
        df: Combined DataFrame with sentiment and ridership data
        output_path: Optional path to save the figure
    
    Returns:
        Plotly figure
    """
    logger.info("Creating sentiment vs. ridership plot")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Sentiment line
    if 'avg_polarity' in df.columns and 'date' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['avg_polarity'],
                name='Sentiment Polarity',
                line=dict(color='blue', width=2)
            ),
            secondary_y=False,
        )
    
    # Ridership line
    if 'total_cta_rides' in df.columns:
        # Normalize ridership for better visualization
        ridership_normalized = (df['total_cta_rides'] - df['total_cta_rides'].min()) / \
                              (df['total_cta_rides'].max() - df['total_cta_rides'].min())
        
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=ridership_normalized,
                name='CTA Ridership (Normalized)',
                line=dict(color='red', width=2)
            ),
            secondary_y=True,
        )
    
    # Update layout
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Sentiment Polarity", secondary_y=False)
    fig.update_yaxes(title_text="Ridership (Normalized)", secondary_y=True)
    fig.update_layout(
        title="Sentiment Trends vs. Daily CTA Ridership",
        hovermode='x unified',
        height=500
    )
    
    if output_path:
        fig.write_html(output_path)
        logger.info(f"Saved plot to {output_path}")
    
    return fig


def plot_complaint_sentiment_heatmap(df: pd.DataFrame, output_path: Optional[str] = None) -> go.Figure:
    """
    Create heatmap: neighborhood-level complaint density vs. negative sentiment
    
    Args:
        df: Combined DataFrame
        output_path: Optional path to save the figure
    
    Returns:
        Plotly figure
    """
    logger.info("Creating complaint-sentiment heatmap")
    
    # Prepare data for heatmap
    # Group by date and calculate metrics
    if 'date' in df.columns:
        heatmap_data = df.groupby('date').agg({
            'transit_related_complaints': 'sum' if 'transit_related_complaints' in df.columns else 'count',
            'negative': 'sum' if 'negative' in df.columns else 0,
            'avg_polarity': 'mean' if 'avg_polarity' in df.columns else 0
        }).reset_index()
        
        # Create pivot table for heatmap (if we have neighborhood data)
        # For now, create a time-based heatmap
        heatmap_data['week'] = pd.to_datetime(heatmap_data['date']).dt.isocalendar().week
        heatmap_data['day_of_week'] = pd.to_datetime(heatmap_data['date']).dt.day_name()
        
        pivot_data = heatmap_data.pivot_table(
            values='transit_related_complaints',
            index='day_of_week',
            columns='week',
            aggfunc='mean',
            fill_value=0
        )
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_data = pivot_data.reindex([d for d in day_order if d in pivot_data.index])
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=[f"Week {col}" for col in pivot_data.columns],
            y=pivot_data.index,
            colorscale='Reds',
            colorbar=dict(title="Complaints")
        ))
        
        fig.update_layout(
            title="Complaint Density Heatmap by Day of Week",
            xaxis_title="Week",
            yaxis_title="Day of Week",
            height=400
        )
    else:
        # Fallback: simple correlation heatmap
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        corr_matrix = df[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title="Correlation Heatmap",
            height=600
        )
    
    if output_path:
        fig.write_html(output_path)
        logger.info(f"Saved heatmap to {output_path}")
    
    return fig


def plot_time_series(df: pd.DataFrame, output_path: Optional[str] = None) -> go.Figure:
    """
    Create time series plots for all key metrics
    
    Args:
        df: Combined DataFrame
        output_path: Optional path to save the figure
    
    Returns:
        Plotly figure
    """
    logger.info("Creating time series plots")
    
    # Determine number of subplots needed
    metrics = []
    if 'avg_polarity' in df.columns:
        metrics.append('avg_polarity')
    if 'total_cta_rides' in df.columns:
        metrics.append('total_cta_rides')
    if 'total_311_complaints' in df.columns:
        metrics.append('total_311_complaints')
    if 'positive' in df.columns:
        metrics.append('positive')
    if 'negative' in df.columns:
        metrics.append('negative')
    
    n_plots = len(metrics)
    if n_plots == 0:
        logger.warning("No metrics found for plotting")
        return go.Figure()
    
    fig = make_subplots(
        rows=n_plots,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=metrics
    )
    
    if 'date' not in df.columns:
        logger.error("Date column not found")
        return go.Figure()
    
    for i, metric in enumerate(metrics, 1):
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df[metric],
                name=metric,
                mode='lines'
            ),
            row=i,
            col=1
        )
    
    fig.update_xaxes(title_text="Date", row=n_plots, col=1)
    fig.update_layout(
        title="Time Series Overview of Key Metrics",
        height=300 * n_plots,
        showlegend=False
    )
    
    if output_path:
        fig.write_html(output_path)
        logger.info(f"Saved time series plot to {output_path}")
    
    return fig


def plot_sentiment_distribution(df: pd.DataFrame, output_path: Optional[str] = None) -> go.Figure:
    """
    Create distribution plots for sentiment scores
    
    Args:
        df: DataFrame with sentiment data
        output_path: Optional path to save the figure
    
    Returns:
        Plotly figure
    """
    logger.info("Creating sentiment distribution plot")
    
    fig = go.Figure()
    
    if 'polarity' in df.columns:
        fig.add_trace(go.Histogram(
            x=df['polarity'],
            name='Polarity Distribution',
            nbinsx=50
        ))
    
    fig.update_layout(
        title="Sentiment Polarity Distribution",
        xaxis_title="Polarity Score",
        yaxis_title="Frequency",
        height=400
    )
    
    if output_path:
        fig.write_html(output_path)
        logger.info(f"Saved distribution plot to {output_path}")
    
    return fig


def create_correlation_matrix(df: pd.DataFrame, output_path: Optional[str] = None) -> pd.DataFrame:
    """
    Calculate and visualize correlation matrix
    
    Args:
        df: Combined DataFrame
        output_path: Optional path to save the figure
    
    Returns:
        Correlation matrix DataFrame
    """
    logger.info("Creating correlation matrix")
    
    # Select numeric columns for correlation
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Key columns to include
    key_cols = ['avg_polarity', 'total_cta_rides', 'total_311_complaints', 
                'positive', 'negative', 'neutral', 'transit_related_complaints']
    
    # Filter to available columns
    corr_cols = [col for col in key_cols if col in numeric_cols]
    
    if len(corr_cols) < 2:
        logger.warning("Not enough columns for correlation analysis")
        return pd.DataFrame()
    
    corr_matrix = df[corr_cols].corr()
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        zmin=-1,
        zmax=1,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Correlation Matrix: Sentiment, Ridership, and Complaints",
        height=600,
        width=800
    )
    
    if output_path:
        fig.write_html(output_path)
        logger.info(f"Saved correlation matrix to {output_path}")
    
    return corr_matrix


def main():
    """Main function to generate all visualizations"""
    import os
    
    # Load combined data
    input_path = PROJECT_ROOT / "data" / "combined" / "combined_data.csv"
    
    if not input_path.exists():
        logger.error(f"Combined data not found: {input_path}")
        return
    
    df = pd.read_csv(input_path)
    df['date'] = pd.to_datetime(df['date'])
    logger.info(f"Loaded combined data: {len(df)} records")
    
    # Create output directory
    viz_dir = PROJECT_ROOT / "visualizations"
    viz_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate all visualizations
    plot_sentiment_vs_ridership(df, str(viz_dir / "sentiment_vs_ridership.html"))
    plot_complaint_sentiment_heatmap(df, str(viz_dir / "complaint_heatmap.html"))
    plot_time_series(df, str(viz_dir / "time_series.html"))
    plot_sentiment_distribution(df, str(viz_dir / "sentiment_distribution.html"))
    corr_matrix = create_correlation_matrix(df, str(viz_dir / "correlation_matrix.html"))
    
    # Save correlation matrix
    if not corr_matrix.empty:
        corr_matrix.to_csv(viz_dir / "correlation_matrix.csv")
        logger.info("Saved correlation matrix to CSV")
    
    logger.info("All visualizations generated")


if __name__ == "__main__":
    main()

