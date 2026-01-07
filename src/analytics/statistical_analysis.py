"""
Advanced statistical analysis module
Provides confidence intervals, p-values, effect sizes, and regression analysis
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import pearsonr
import logging

logger = logging.getLogger(__name__)


def calculate_confidence_interval(data: pd.Series, confidence: float = 0.95):
    """
    Calculate confidence interval for a data series
    
    Args:
        data: pandas Series with numeric data
        confidence: Confidence level (default 0.95 for 95% CI)
    
    Returns:
        tuple: (lower_bound, upper_bound, mean)
    """
    if len(data) < 2:
        return None, None, data.mean() if len(data) > 0 else None
    
    mean = data.mean()
    std_err = stats.sem(data.dropna())
    h = std_err * stats.t.ppf((1 + confidence) / 2, len(data) - 1)
    
    return mean - h, mean + h, mean


def calculate_correlation_with_stats(x: pd.Series, y: pd.Series):
    """
    Calculate Pearson correlation with p-value and confidence interval
    
    Args:
        x: First variable
        y: Second variable
    
    Returns:
        dict: Contains correlation, p-value, CI, and significance
    """
    # Remove NaN pairs
    mask = ~(x.isna() | y.isna())
    x_clean = x[mask]
    y_clean = y[mask]
    
    if len(x_clean) < 3:
        return {
            'correlation': np.nan,
            'p_value': np.nan,
            'ci_lower': np.nan,
            'ci_upper': np.nan,
            'significant': False,
            'n': len(x_clean)
        }
    
    # Calculate correlation and p-value
    corr, p_value = pearsonr(x_clean, y_clean)
    
    # Calculate confidence interval using Fisher transformation
    n = len(x_clean)
    z = np.arctanh(corr)
    se = 1 / np.sqrt(n - 3)
    z_crit = stats.norm.ppf(0.975)  # 95% CI
    
    ci_lower = np.tanh(z - z_crit * se)
    ci_upper = np.tanh(z + z_crit * se)
    
    return {
        'correlation': corr,
        'p_value': p_value,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'significant': p_value < 0.05,
        'n': n
    }


def calculate_effect_size(x: pd.Series, y: pd.Series):
    """
    Calculate effect size (Cohen's d) for correlation
    
    Args:
        x: First variable
        y: Second variable
    
    Returns:
        dict: Contains Cohen's d, R-squared, and interpretation
    """
    # Remove NaN pairs
    mask = ~(x.isna() | y.isna())
    x_clean = x[mask]
    y_clean = y[mask]
    
    if len(x_clean) < 3:
        return {
            'cohens_d': np.nan,
            'r_squared': np.nan,
            'interpretation': 'Insufficient data'
        }
    
    # Calculate correlation
    corr, _ = pearsonr(x_clean, y_clean)
    
    # R-squared
    r_squared = corr ** 2
    
    # Cohen's d (approximation from correlation)
    # d ≈ 2r / sqrt(1 - r²)
    if abs(corr) < 0.999:
        cohens_d = 2 * corr / np.sqrt(1 - corr ** 2)
    else:
        cohens_d = np.inf if corr > 0 else -np.inf
    
    # Interpretation
    if abs(cohens_d) < 0.2:
        interpretation = 'Negligible'
    elif abs(cohens_d) < 0.5:
        interpretation = 'Small'
    elif abs(cohens_d) < 0.8:
        interpretation = 'Medium'
    else:
        interpretation = 'Large'
    
    return {
        'cohens_d': cohens_d,
        'r_squared': r_squared,
        'interpretation': interpretation
    }


def linear_regression(x: pd.Series, y: pd.Series):
    """
    Perform simple linear regression
    
    Args:
        x: Independent variable
        y: Dependent variable
    
    Returns:
        dict: Contains slope, intercept, R², p-value, and statistics
    """
    # Remove NaN pairs
    mask = ~(x.isna() | y.isna())
    x_clean = x[mask]
    y_clean = y[mask]
    
    if len(x_clean) < 3:
        return {
            'slope': np.nan,
            'intercept': np.nan,
            'r_squared': np.nan,
            'p_value': np.nan,
            'std_err': np.nan,
            'n': len(x_clean)
        }
    
    # Perform regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)
    
    return {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_value ** 2,
        'p_value': p_value,
        'std_err': std_err,
        'n': len(x_clean),
        'r_value': r_value
    }


def calculate_all_statistics(df: pd.DataFrame, x_col: str, y_col: str):
    """
    Calculate comprehensive statistics for two variables
    
    Args:
        df: DataFrame containing the variables
        x_col: Name of independent variable column
        y_col: Name of dependent variable column
    
    Returns:
        dict: Comprehensive statistics including correlation, regression, effect size
    """
    if x_col not in df.columns or y_col not in df.columns:
        logger.warning(f"Columns {x_col} or {y_col} not found in dataframe")
        return {}
    
    x = df[x_col]
    y = df[y_col]
    
    # Correlation with stats
    corr_stats = calculate_correlation_with_stats(x, y)
    
    # Effect size
    effect_size = calculate_effect_size(x, y)
    
    # Regression
    regression = linear_regression(x, y)
    
    # Combine results
    results = {
        'correlation': corr_stats['correlation'],
        'p_value': corr_stats['p_value'],
        'ci_lower': corr_stats['ci_lower'],
        'ci_upper': corr_stats['ci_upper'],
        'significant': corr_stats['significant'],
        'r_squared': effect_size['r_squared'],
        'cohens_d': effect_size['cohens_d'],
        'effect_interpretation': effect_size['interpretation'],
        'regression_slope': regression['slope'],
        'regression_intercept': regression['intercept'],
        'regression_p_value': regression['p_value'],
        'n': corr_stats['n']
    }
    
    return results

