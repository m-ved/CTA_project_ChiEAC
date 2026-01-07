"""
Simple Correlation Analysis Module
Provides easy-to-understand correlation insights in plain language
"""

import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import logging

logger = logging.getLogger(__name__)


def calculate_simple_correlations(df: pd.DataFrame, 
                                  metric_cols: list = None) -> dict:
    """
    Calculate all pairwise correlations between metrics
    
    Args:
        df: DataFrame with metric columns
        metric_cols: List of columns to correlate (default: auto-detect numeric)
    
    Returns:
        Dictionary with correlation matrix and insights
    """
    if df.empty:
        return {}
    
    # Auto-detect metric columns if not provided
    if metric_cols is None:
        metric_cols = [col for col in df.columns 
                      if df[col].dtype in [np.int64, np.float64] 
                      and col not in ['date', 'day_of_week', 'month']]
    
    if len(metric_cols) < 2:
        logger.warning("Need at least 2 numeric columns for correlation")
        return {}
    
    # Calculate correlation matrix
    corr_matrix = df[metric_cols].corr()
    
    # Get all pairwise correlations
    correlations = []
    for i, col1 in enumerate(metric_cols):
        for col2 in metric_cols[i+1:]:
            # Remove NaN pairs
            mask = ~(df[col1].isna() | df[col2].isna())
            if mask.sum() < 3:
                continue
            
            x = df.loc[mask, col1]
            y = df.loc[mask, col2]
            
            corr, p_value = pearsonr(x, y)
            
            correlations.append({
                'var1': col1,
                'var2': col2,
                'correlation': corr,
                'p_value': p_value,
                'significant': p_value < 0.05,
                'n': len(x),
                'insight': format_correlation_insight(corr, col1, col2, p_value)
            })
    
    # Sort by absolute correlation
    correlations = sorted(correlations, key=lambda x: abs(x['correlation']), reverse=True)
    
    return {
        'correlation_matrix': corr_matrix,
        'pairwise_correlations': correlations,
        'metric_columns': metric_cols
    }


def format_correlation_insight(corr: float, var1: str, var2: str, 
                                p_value: float = None) -> str:
    """
    Convert correlation to plain language insight
    
    Args:
        corr: Correlation coefficient (-1 to 1)
        var1: First variable name
        var2: Second variable name
        p_value: P-value for significance (optional)
    
    Returns:
        Plain-language insight string
    """
    # Clean variable names for display
    var1_clean = format_variable_name(var1)
    var2_clean = format_variable_name(var2)
    
    abs_corr = abs(corr)
    
    # Determine strength
    if abs_corr >= 0.7:
        strength = "strong"
        strength_emoji = "🟢"
    elif abs_corr >= 0.4:
        strength = "moderate"
        strength_emoji = "🟡"
    elif abs_corr >= 0.2:
        strength = "weak"
        strength_emoji = "🟠"
    else:
        strength = "very weak"
        strength_emoji = "🔴"
    
    # Determine direction
    if corr > 0:
        direction = "increases"
        direction_text = "When {} increases, {} also increases"
    else:
        direction = "decreases"
        direction_text = "When {} increases, {} decreases"
    
    # Build insight
    if abs_corr < 0.2:
        insight = f"{var1_clean} and {var2_clean} have little relationship (correlation: {corr:.2f})"
    else:
        insight = f"{direction_text.format(var1_clean, var2_clean)} ({strength} relationship, r={corr:.2f})"
    
    # Add significance if provided
    if p_value is not None:
        if p_value < 0.05:
            insight += " - This relationship is statistically significant"
        else:
            insight += " - This relationship is not statistically significant"
    
    return {
        'text': insight,
        'strength': strength,
        'strength_emoji': strength_emoji,
        'correlation': corr,
        'direction': direction
    }


def format_variable_name(var_name: str) -> str:
    """
    Format variable name for display (remove underscores, capitalize)
    
    Args:
        var_name: Variable name
    
    Returns:
        Formatted name
    """
    # Common replacements
    replacements = {
        'total_cta_rides': 'CTA Ridership',
        'total_311_complaints': '311 Complaints',
        'total_crimes': 'Crimes',
        'total_traffic_volume': 'Traffic Volume',
        'total_arrests': 'Arrests',
        'bus_rides': 'Bus Rides',
        'train_rides': 'Train Rides'
    }
    
    if var_name in replacements:
        return replacements[var_name]
    
    # Otherwise, format the name
    formatted = var_name.replace('_', ' ').title()
    return formatted


def get_top_correlations(df: pd.DataFrame, n: int = 5, 
                        metric_cols: list = None) -> list:
    """
    Get top N most significant correlations
    
    Args:
        df: DataFrame with metric columns
        n: Number of top correlations to return
        metric_cols: List of columns to correlate
    
    Returns:
        List of top correlation dictionaries
    """
    corr_results = calculate_simple_correlations(df, metric_cols)
    
    if not corr_results or 'pairwise_correlations' not in corr_results:
        return []
    
    # Filter significant correlations and sort by absolute value
    significant = [c for c in corr_results['pairwise_correlations'] 
                   if c['significant']]
    
    if len(significant) >= n:
        return significant[:n]
    else:
        # If not enough significant, return top n by absolute value
        return corr_results['pairwise_correlations'][:n]


def get_correlation_summary(df: pd.DataFrame, 
                            metric_cols: list = None) -> dict:
    """
    Get summary of all correlations with plain language insights
    
    Args:
        df: DataFrame with metric columns
        metric_cols: List of columns to correlate
    
    Returns:
        Dictionary with summary statistics and insights
    """
    corr_results = calculate_simple_correlations(df, metric_cols)
    
    if not corr_results:
        return {}
    
    correlations = corr_results['pairwise_correlations']
    
    # Count by strength
    strong = sum(1 for c in correlations if abs(c['correlation']) >= 0.7)
    moderate = sum(1 for c in correlations if 0.4 <= abs(c['correlation']) < 0.7)
    weak = sum(1 for c in correlations if 0.2 <= abs(c['correlation']) < 0.4)
    very_weak = sum(1 for c in correlations if abs(c['correlation']) < 0.2)
    
    # Count significant
    significant = sum(1 for c in correlations if c['significant'])
    
    return {
        'total_relationships': len(correlations),
        'strong_relationships': strong,
        'moderate_relationships': moderate,
        'weak_relationships': weak,
        'very_weak_relationships': very_weak,
        'significant_relationships': significant,
        'top_insights': [c['insight'] for c in correlations[:3]]
    }

