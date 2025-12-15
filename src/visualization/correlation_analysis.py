"""
Correlation Analysis Module
Calculates correlations between sentiment, ridership, and complaints
"""

import pandas as pd
import numpy as np
import logging
from scipy import stats
from typing import Dict, Tuple
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def calculate_correlations(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Calculate correlations between key metrics
    
    Args:
        df: Combined DataFrame with all metrics
    
    Returns:
        Dictionary of correlation results
    """
    logger.info("Calculating correlations")
    
    results = {}
    
    # Key metrics to correlate
    metrics = {
        'sentiment': 'avg_polarity',
        'ridership': 'total_cta_rides',
        'complaints': 'total_311_complaints',
        'transit_complaints': 'transit_related_complaints',
        'negative_tweets': 'negative',
        'positive_tweets': 'positive'
    }
    
    # Filter to available columns
    available_metrics = {k: v for k, v in metrics.items() if v in df.columns}
    
    if len(available_metrics) < 2:
        logger.warning("Not enough metrics for correlation analysis")
        return results
    
    # Calculate pairwise correlations
    for metric1_name, metric1_col in available_metrics.items():
        for metric2_name, metric2_col in available_metrics.items():
            if metric1_name >= metric2_name:  # Avoid duplicates
                continue
            
            # Remove NaN values
            data1 = df[metric1_col].dropna()
            data2 = df[metric2_col].dropna()
            
            # Align indices
            common_idx = data1.index.intersection(data2.index)
            if len(common_idx) < 10:  # Need at least 10 data points
                continue
            
            data1_aligned = data1.loc[common_idx]
            data2_aligned = data2.loc[common_idx]
            
            # Calculate Pearson correlation
            if len(data1_aligned) > 0 and len(data2_aligned) > 0:
                corr_coef, p_value = stats.pearsonr(data1_aligned, data2_aligned)
                
                key = f"{metric1_name}_vs_{metric2_name}"
                results[key] = {
                    'correlation': corr_coef,
                    'p_value': p_value,
                    'n_samples': len(common_idx),
                    'significant': p_value < 0.05
                }
                
                logger.info(f"{key}: r={corr_coef:.3f}, p={p_value:.4f}")
    
    return results


def generate_correlation_report(results: Dict[str, Dict[str, float]], output_path: str = None) -> str:
    """
    Generate a text report of correlation results
    
    Args:
        results: Dictionary of correlation results
        output_path: Optional path to save report
    
    Returns:
        Report text
    """
    report_lines = [
        "=" * 60,
        "CORRELATION ANALYSIS REPORT",
        "=" * 60,
        ""
    ]
    
    # Key correlations of interest
    key_correlations = [
        ('sentiment_vs_ridership', 'Sentiment Polarity vs. CTA Ridership'),
        ('complaints_vs_negative_tweets', '311 Complaints vs. Negative Tweets'),
        ('sentiment_vs_complaints', 'Sentiment Polarity vs. 311 Complaints'),
        ('ridership_vs_complaints', 'CTA Ridership vs. 311 Complaints')
    ]
    
    report_lines.append("KEY CORRELATIONS:")
    report_lines.append("-" * 60)
    
    for key, description in key_correlations:
        if key in results:
            r = results[key]
            sig_marker = "***" if r['significant'] else ""
            report_lines.append(
                f"{description}:"
            )
            report_lines.append(
                f"  Correlation: {r['correlation']:.3f} {sig_marker}"
            )
            report_lines.append(
                f"  P-value: {r['p_value']:.4f}"
            )
            report_lines.append(
                f"  Sample size: {r['n_samples']}"
            )
            report_lines.append("")
        else:
            report_lines.append(f"{description}: Data not available")
            report_lines.append("")
    
    report_lines.append("=" * 60)
    report_lines.append("ALL CORRELATIONS:")
    report_lines.append("-" * 60)
    
    for key, r in sorted(results.items()):
        sig_marker = "***" if r['significant'] else ""
        report_lines.append(
            f"{key}: r={r['correlation']:.3f}, p={r['p_value']:.4f} {sig_marker}"
        )
    
    report_lines.append("")
    report_lines.append("*** = Statistically significant (p < 0.05)")
    report_lines.append("=" * 60)
    
    report_text = "\n".join(report_lines)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(report_text)
        logger.info(f"Saved correlation report to {output_path}")
    
    return report_text


def main():
    """Main function to perform correlation analysis"""
    import os
    
    # Load combined data
    input_path = PROJECT_ROOT / "data" / "combined" / "combined_data.csv"
    
    if not input_path.exists():
        logger.error(f"Combined data not found: {input_path}")
        return
    
    df = pd.read_csv(input_path)
    logger.info(f"Loaded combined data: {len(df)} records")
    
    # Calculate correlations
    results = calculate_correlations(df)
    
    if not results:
        logger.warning("No correlations calculated")
        return
    
    # Generate report
    report_path = PROJECT_ROOT / "docs" / "correlation_report.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = generate_correlation_report(results, str(report_path))
    print(report)
    
    # Save correlation matrix
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    key_cols = ['avg_polarity', 'total_cta_rides', 'total_311_complaints', 
                'positive', 'negative', 'transit_related_complaints']
    corr_cols = [col for col in key_cols if col in numeric_cols]
    
    if len(corr_cols) >= 2:
        corr_matrix = df[corr_cols].corr()
        output_path = PROJECT_ROOT / "visualizations" / "correlation_matrix.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        corr_matrix.to_csv(output_path)
        logger.info("Saved correlation matrix to CSV")


if __name__ == "__main__":
    main()

