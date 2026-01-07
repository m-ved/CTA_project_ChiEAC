#!/usr/bin/env python3
"""
Quick start script to run the complete CityPulse data pipeline
"""

import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run the complete pipeline"""
    logger.info("=" * 60)
    logger.info("CityPulse Data Pipeline")
    logger.info("=" * 60)
    
    steps = [
        ("Data Collection", [
            ("311 Data", "data_collection.collect_311_data"),
            ("CTA Data", "data_collection.collect_cta_data"),
            ("Traffic Data", "data_collection.collect_traffic_data"),
            ("Crime Data", "data_collection.collect_crime_data")
        ]),
        ("Data Cleaning", [
            ("Clean All Data", "data_cleaning.clean_data")
        ]),
        ("Data Integration", [
            ("Integrate Data", "sentiment.integrate_data")
        ]),
        ("Analysis & Visualization", [
            ("Correlation Analysis", "visualization.correlation_analysis"),
            ("Generate Visualizations", "visualization.visualizations")
        ])
    ]
    
    for step_name, modules in steps:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Step: {step_name}")
        logger.info(f"{'=' * 60}")
        
        for module_name, module_path in modules:
            try:
                logger.info(f"\nRunning: {module_name}...")
                module = __import__(module_path, fromlist=['main'])
                if hasattr(module, 'main'):
                    module.main()
                else:
                    logger.warning(f"Module {module_path} has no main() function")
            except Exception as e:
                logger.error(f"Error in {module_name}: {e}")
                logger.info("Continuing with next step...")
    
    logger.info("\n" + "=" * 60)
    logger.info("Pipeline Complete!")
    logger.info("=" * 60)
    logger.info("\nNext steps:")
    logger.info("1. Review the data in data/combined/combined_data.csv")
    logger.info("2. Check visualizations in visualizations/")
    logger.info("3. Run the dashboard: python src/visualization/dashboard.py")
    logger.info("4. Review insights in docs/insights.md")

if __name__ == "__main__":
    main()

