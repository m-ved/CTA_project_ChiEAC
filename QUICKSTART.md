# Quick Start Guide

Follow these steps to get CityPulse up and running:

## Step 1: Install Dependencies

```bash
# Make sure you're in the project directory
cd "/Users/mukul/Desktop/chieac project"

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR on Windows: venv\Scripts\activate

# Install all required packages
pip install -r requirements.txt

# If snscrape fails, try:
pip install git+https://github.com/JustAnotherArchivist/snscrape.git
```

## Step 2: Collect Data

You have two options:

### Option A: Use the Jupyter Notebooks (Recommended for first time)

```bash
# Start Jupyter
jupyter notebook

# Then open and run: notebooks/week1_data_cleaning.ipynb
```

### Option B: Run Scripts Directly

```bash
# Collect 311 data
python src/data_collection/collect_311_data.py

# Collect CTA ridership data
python src/data_collection/collect_cta_data.py

# Collect Twitter data (may take a while)
python src/data_collection/collect_tweets.py
```

**Note**: Twitter scraping might fail due to API changes. That's okay - you can still work with 311 and CTA data.

## Step 3: Clean the Data

```bash
python src/data_cleaning/clean_data.py
```

Or run the cleaning section in `notebooks/week1_data_cleaning.ipynb`

## Step 4: Analyze Sentiment

```bash
# Analyze tweet sentiment
python src/sentiment/sentiment_analyzer.py

# Aggregate by day
python src/sentiment/aggregate_sentiment.py

# Integrate all datasets
python src/sentiment/integrate_data.py
```

Or use `notebooks/week2_sentiment_analysis.ipynb`

## Step 5: Create Visualizations

```bash
# Run correlation analysis
python src/visualization/correlation_analysis.py

# Generate visualizations
python src/visualization/visualizations.py
```

Or use `notebooks/week3_analysis.ipynb`

## Step 6: Launch the Dashboard

```bash
python src/visualization/dashboard.py
```

Then open your browser to: **http://127.0.0.1:8050**

## Alternative: Run Everything at Once

```bash
python run_pipeline.py
```

This will run all steps sequentially.

## Troubleshooting

### Issue: snscrape not working
- Twitter/X API has changed. The script will create empty data structure.
- You can still use 311 and CTA data for the project.

### Issue: No data collected
- Check your internet connection
- Verify API endpoints are accessible
- Check the logs for error messages

### Issue: Import errors
- Make sure you're in the project root directory
- Verify virtual environment is activated
- Check that all packages are installed: `pip list`

### Issue: Dashboard won't start
- Check if port 8050 is already in use
- Try changing the port in `dashboard.py`: `run_dashboard(port=8051)`

## What to Expect

After running the pipeline, you should have:

1. **Data files** in `data/cleaned/` and `data/combined/`
2. **Visualizations** in `visualizations/` folder
3. **Correlation report** in `docs/correlation_report.txt`
4. **Interactive dashboard** running on localhost

## Next Steps

1. Explore the data in the Jupyter notebooks
2. Review insights in `docs/insights.md`
3. Customize the dashboard in `src/visualization/dashboard.py`
4. Add your own analysis in the notebooks

## Need Help?

- Check the README.md for detailed documentation
- Review the data dictionary in `docs/data_dictionary.md`
- Look at example outputs in the notebooks

