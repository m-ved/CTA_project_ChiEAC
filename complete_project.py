#!/usr/bin/env python3
"""
Quick script to complete the CityPulse project pipeline
Runs all necessary steps to generate outputs for presentation
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent

def check_dependencies():
    """Check if required data files exist"""
    logger.info("Checking dependencies...")
    
    required_files = [
        PROJECT_ROOT / "data" / "cleaned" / "tweets.csv",
        PROJECT_ROOT / "data" / "cleaned" / "cta_ridership.csv",
        PROJECT_ROOT / "data" / "cleaned" / "311_data.csv"
    ]
    
    missing = []
    for file in required_files:
        if not file.exists():
            missing.append(str(file))
        else:
            logger.info(f"✓ Found: {file.name}")
    
    if missing:
        logger.warning(f"Missing files: {missing}")
        # Check if we can generate tweets
        if PROJECT_ROOT / "data" / "cleaned" / "tweets.csv" not in [Path(f) for f in missing]:
            pass  # Tweets exist
        else:
            logger.info("\n💡 Tip: You can generate sample CTA tweets using:")
            logger.info("   python src/data_collection/generate_cta_tweets.py")
        logger.warning("You may need to run data collection first")
        return False
    
    return True

def run_step(step_name, module_path, description=""):
    """Run a pipeline step"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Step: {step_name}")
    if description:
        logger.info(f"Description: {description}")
    logger.info(f"{'='*60}")
    
    try:
        module = __import__(module_path, fromlist=['main'])
        if hasattr(module, 'main'):
            module.main()
            logger.info(f"✓ {step_name} completed successfully")
            return True
        else:
            logger.warning(f"Module {module_path} has no main() function")
            return False
    except Exception as e:
        logger.error(f"✗ Error in {step_name}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Run complete pipeline"""
    logger.info("="*60)
    logger.info("CityPulse Project Completion Script")
    logger.info("="*60)
    
    # Check dependencies
    if not check_dependencies():
        logger.warning("\nSome required files are missing.")
        logger.warning("Attempting to continue anyway...\n")
    
    steps = [
        ("Sentiment Analysis", "sentiment.sentiment_analyzer", 
         "Analyze tweet sentiment using VADER and TextBlob"),
        ("Aggregate Sentiment", "sentiment.aggregate_sentiment",
         "Aggregate sentiment scores by day"),
        ("Integrate Data", "sentiment.integrate_data",
         "Combine sentiment, CTA, and 311 data"),
        ("Correlation Analysis", "visualization.correlation_analysis",
         "Calculate correlations between metrics"),
        ("Generate Visualizations", "visualization.visualizations",
         "Create charts and save to visualizations/")
    ]
    
    results = []
    for step_name, module_path, description in steps:
        success = run_step(step_name, module_path, description)
        results.append((step_name, success))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("Pipeline Summary")
    logger.info("="*60)
    
    for step_name, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        logger.info(f"{status}: {step_name}")
    
    # Check outputs
    logger.info("\n" + "="*60)
    logger.info("Checking Outputs")
    logger.info("="*60)
    
    output_files = [
        (PROJECT_ROOT / "data" / "cleaned" / "tweets_with_sentiment.csv", 
         "Tweets with sentiment scores"),
        (PROJECT_ROOT / "data" / "combined" / "daily_sentiment.csv",
         "Daily sentiment aggregation"),
        (PROJECT_ROOT / "data" / "combined" / "combined_data.csv",
         "Combined dataset (REQUIRED for dashboard)"),
        (PROJECT_ROOT / "docs" / "correlation_report.txt",
         "Correlation analysis report"),
    ]
    
    for file_path, description in output_files:
        if file_path.exists():
            size = file_path.stat().st_size
            logger.info(f"✓ {description}: {file_path.name} ({size:,} bytes)")
        else:
            logger.warning(f"✗ Missing: {description}")
    
    # Check visualizations
    viz_dir = PROJECT_ROOT / "visualizations"
    if viz_dir.exists():
        viz_files = list(viz_dir.glob("*"))
        if viz_files:
            logger.info(f"\n✓ Generated {len(viz_files)} visualization files")
            for viz_file in viz_files[:5]:  # Show first 5
                logger.info(f"  - {viz_file.name}")
        else:
            logger.warning("\n✗ No visualizations generated")
    else:
        logger.warning("\n✗ Visualizations directory not created")
    
    # Final instructions
    logger.info("\n" + "="*60)
    logger.info("Next Steps")
    logger.info("="*60)
    
    combined_data = PROJECT_ROOT / "data" / "combined" / "combined_data.csv"
    if combined_data.exists():
        logger.info("1. ✓ Combined data ready")
        logger.info("2. Launch dashboard: python src/visualization/dashboard.py")
        logger.info("3. Open browser to: http://127.0.0.1:8050")
    else:
        logger.warning("1. ✗ Combined data not generated - dashboard won't work")
        logger.warning("   Check errors above and fix issues")
    
    logger.info("\n4. Review visualizations in visualizations/ folder")
    logger.info("5. Check correlation report: docs/correlation_report.txt")
    logger.info("6. Review insights: docs/insights.md")
    
    logger.info("\n" + "="*60)
    logger.info("Pipeline Complete!")
    logger.info("="*60)

if __name__ == "__main__":
    main()

