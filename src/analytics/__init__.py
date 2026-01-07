"""
Analytics module for advanced statistical and geographic analysis
"""

from .statistical_analysis import (
    calculate_confidence_interval,
    calculate_correlation_with_stats,
    calculate_effect_size,
    linear_regression,
    calculate_all_statistics
)

from .neighborhood_analysis import (
    aggregate_by_neighborhood,
    aggregate_by_ward,
    detect_hotspots,
    compare_neighborhoods,
    rank_hotspots_by_metric,
    get_top_hotspots,
    format_hotspot_description
)

from .temporal_analysis import (
    analyze_day_of_week_patterns,
    analyze_time_patterns,
    get_peak_days,
    format_temporal_insight,
    get_seasonal_patterns
)

from .simple_correlations import (
    calculate_simple_correlations,
    format_correlation_insight,
    get_top_correlations,
    get_correlation_summary
)

from .health_scores import (
    calculate_urban_health_index,
    get_health_status,
    calculate_route_efficiency_score,
    calculate_safety_index,
    calculate_trend_indicator
)

__all__ = [
    # Statistical analysis
    'calculate_confidence_interval',
    'calculate_correlation_with_stats',
    'calculate_effect_size',
    'linear_regression',
    'calculate_all_statistics',
    # Neighborhood analysis
    'aggregate_by_neighborhood',
    'aggregate_by_ward',
    'detect_hotspots',
    'compare_neighborhoods',
    'rank_hotspots_by_metric',
    'get_top_hotspots',
    'format_hotspot_description',
    # Temporal analysis
    'analyze_day_of_week_patterns',
    'analyze_time_patterns',
    'get_peak_days',
    'format_temporal_insight',
    'get_seasonal_patterns',
    # Simple correlations
    'calculate_simple_correlations',
    'format_correlation_insight',
    'get_top_correlations',
    'get_correlation_summary',
    # Health scores
    'calculate_urban_health_index',
    'get_health_status',
    'calculate_route_efficiency_score',
    'calculate_safety_index',
    'calculate_trend_indicator'
]

