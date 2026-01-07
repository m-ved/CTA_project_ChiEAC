# How to Run CityPulse Project

A comprehensive step-by-step guide to run the CityPulse: Urban Sentiment & Mobility Dashboard project from start to finish.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Data Setup](#data-setup)
4. [Running the Pipeline](#running-the-pipeline)
5. [Launching the Dashboard](#launching-the-dashboard)
6. [Understanding the Outputs](#understanding-the-outputs)
7. [Troubleshooting](#troubleshooting)
8. [Next Steps](#next-steps)

---

## Prerequisites

### System Requirements

- **Python**: Version 3.8 or higher
- **Operating System**: macOS, Linux, or Windows
- **Memory**: At least 4GB RAM recommended
- **Disk Space**: ~500MB for data and dependencies
- **Internet Connection**: Required for data collection (optional if using sample data)

### Required Knowledge

- Basic command line/terminal usage
- Basic understanding of Python (helpful but not required)

---

## Installation

### Step 1: Navigate to Project Directory

```bash
cd "/Users/mukul/Desktop/chieac project"
```

Or navigate to wherever you've placed the project folder.

### Step 2: Create Virtual Environment (Recommended)

Creating a virtual environment isolates project dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt when activated.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages:
- pandas, numpy (data manipulation)
- matplotlib, seaborn, plotly (visualization)
- dash, dash-bootstrap-components (dashboard)
- tweepy (Twitter API - optional)
- textblob, vaderSentiment (sentiment analysis)
- requests (API calls)
- scipy (statistical analysis)

**Expected Output:**
```
Collecting pandas>=2.0.0
Collecting numpy>=1.24.0
...
Successfully installed pandas-2.x.x numpy-1.x.x ...
```

### Step 4: Verify Installation

```bash
python -c "import pandas, dash, plotly; print('All packages installed successfully!')"
```

If you see "All packages installed successfully!", you're ready to proceed.

---

## Data Setup

You have three options for data setup:

### Option A: Generate Sample Data (Recommended for Quick Start)

This is the fastest way to get started. Sample data is realistic and doesn't require API access.

```bash
# Generate sample CTA tweets
python src/data_collection/generate_cta_tweets.py

# Generate sample 311 and CTA data (optional - if you want fresh sample data)
python src/utils/generate_sample_data.py
```

**What this creates:**
- `data/cleaned/tweets.csv` - Sample CTA tweets with diverse sentiments
- `data/cleaned/311_data.csv` - Sample 311 complaints (37+ types)
- `data/cleaned/cta_ridership.csv` - Sample CTA ridership data

**Expected Output:**
```
2025-12-30 09:32:41,457 - INFO - Generating 2250 sample 311 complaints
2025-12-30 09:32:41,548 - INFO - Generated 2351 311 complaints
Generated 2351 complaints with 37 unique types
```

### Option B: Collect Real Data from APIs

If you want to use real data from Chicago APIs:

#### 1. Collect 311 Data
```bash
python src/data_collection/collect_311_data.py
```

#### 2. Collect CTA Ridership Data
```bash
python src/data_collection/collect_cta_data.py
```

#### 3. Collect Twitter Data (Requires API Setup)

**First, set up Twitter API credentials:**

1. Get Twitter Developer Account: https://developer.twitter.com/
2. Create a `.env` file in the project root:
   ```bash
   # .env file
   TWITTER_BEARER_TOKEN=your_bearer_token_here
   ```

3. Collect tweets:
   ```bash
   python src/data_collection/collect_tweets_tweepy.py
   ```

**Note:** Twitter API has rate limits. Free tier allows 10,000 tweets per day.

### Option C: Use Existing Data Files

If you already have data files in `data/cleaned/`, you can skip data collection and proceed directly to the pipeline.

**Check existing data:**
```bash
ls -lh data/cleaned/*.csv
```

You should see:
- `tweets.csv` (or `tweets_with_sentiment.csv`)
- `311_data.csv`
- `cta_ridership.csv`

---

## Running the Pipeline

The pipeline processes data through sentiment analysis, aggregation, integration, and visualization.

### Quick Method: Run Everything at Once

This is the recommended approach for most users:

```bash
python complete_project.py
```

**What this does:**
1. Analyzes tweet sentiment using VADER and TextBlob
2. Aggregates sentiment by day
3. Integrates all datasets (sentiment + CTA + 311)
4. Performs correlation analysis
5. Generates visualizations

**Expected Output:**
```
============================================================
CityPulse Project Completion Script
============================================================
Checking dependencies...
✓ Found: tweets.csv
✓ Found: cta_ridership.csv
✓ Found: 311_data.csv

============================================================
Step: Sentiment Analysis
============================================================
...
✓ Sentiment Analysis completed successfully

============================================================
Step: Aggregate Sentiment
============================================================
...
✓ Aggregate Sentiment completed successfully

============================================================
Step: Integrate Data
============================================================
...
✓ Integrate Data completed successfully

============================================================
Step: Correlation Analysis
============================================================
...
✓ Correlation Analysis completed successfully

============================================================
Step: Generate Visualizations
============================================================
...
✓ Generate Visualizations completed successfully

============================================================
Pipeline Summary
============================================================
✓ SUCCESS: Sentiment Analysis
✓ SUCCESS: Aggregate Sentiment
✓ SUCCESS: Integrate Data
✓ SUCCESS: Correlation Analysis
✓ SUCCESS: Generate Visualizations
```

**Time:** Approximately 2-5 minutes depending on data size.

### Step-by-Step Method

If you prefer to run each step individually or encounter errors:

#### Step 1: Analyze Sentiment
```bash
python src/sentiment/sentiment_analyzer.py
```

**Creates:** `data/cleaned/tweets_with_sentiment.csv`

**Expected Output:**
```
Loaded 147 tweets from data/cleaned/tweets.csv
Starting sentiment analysis
Analyzing 147 tweets...
Sentiment analysis complete

=== Sentiment Distribution ===
positive    57
neutral     53
negative    37
```

#### Step 2: Aggregate Sentiment by Day
```bash
python src/sentiment/aggregate_sentiment.py
```

**Creates:** `data/combined/daily_sentiment.csv`

**Expected Output:**
```
Loaded 147 tweets with sentiment
Aggregating tweets by day
Aggregated 6 days of sentiment data
Saved daily sentiment aggregation to data/combined/daily_sentiment.csv
```

#### Step 3: Integrate All Data
```bash
python src/sentiment/integrate_data.py
```

**Creates:** `data/combined/combined_data.csv` (REQUIRED for dashboard)

**Expected Output:**
```
Integrating all datasets
Loaded sentiment data: 6 days
Aggregated 22 days of CTA data
Aggregated 47 days of 311 data
Integrated data: 69 days
Saved combined data to data/combined/combined_data.csv
```

#### Step 4: Correlation Analysis
```bash
python src/visualization/correlation_analysis.py
```

**Creates:** 
- `docs/correlation_report.txt`
- `visualizations/correlation_matrix.csv`

**Expected Output:**
```
Loaded combined data: 39 records
Calculating correlations
sentiment_vs_ridership: r=-0.356, p=0.0260
...
Saved correlation report to docs/correlation_report.txt
```

#### Step 5: Generate Visualizations
```bash
python src/visualization/visualizations.py
```

**Creates:** Multiple HTML visualization files in `visualizations/` folder

**Expected Output:**
```
Loaded combined data: 39 records
Creating sentiment vs. ridership plot
Saved plot to visualizations/sentiment_vs_ridership.html
...
All visualizations generated
```

---

## Launching the Dashboard

The interactive dashboard is the final step to visualize all your data.

### Step 1: Start the Dashboard Server

```bash
python src/visualization/dashboard.py
```

**Expected Output:**
```
2025-12-30 09:26:31,545 - INFO - Starting dashboard server on http://127.0.0.1:8050
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app 'src.visualization.dashboard'
 * Debug mode: on
```

### Step 2: Open in Browser

Open your web browser and navigate to:

**http://127.0.0.1:8050**

### Step 3: Using the Dashboard

The dashboard includes:

1. **Key Metrics Cards** - Summary statistics at the top
2. **Date Range Filter** - Select date range for analysis
3. **Complaint Type Filter** - Filter by specific 311 complaint types
4. **Sentiment vs. Ridership Chart** - Dual-axis time series
5. **Time Series Overview** - Multiple metrics over time
6. **Sentiment Distribution** - Histogram of sentiment scores
7. **Correlation Heatmap** - Relationships between metrics
8. **Top Hashtags** - Most common hashtags in tweets
9. **Complaint Density Map** - Geospatial visualization (if coordinates available)

### Step 4: Stop the Dashboard

Press `Ctrl+C` in the terminal to stop the dashboard server.

---

## Understanding the Outputs

After running the pipeline, you'll have several output files:

### Data Files

**Location:** `data/combined/`

- **`combined_data.csv`** - Main integrated dataset (required for dashboard)
  - Contains: sentiment, ridership, complaints aggregated by date
  - Columns: date, avg_polarity, total_cta_rides, total_311_complaints, etc.

- **`daily_sentiment.csv`** - Daily sentiment aggregation
  - Contains: average sentiment scores per day
  - Columns: date, avg_polarity, positive, neutral, negative, total_tweets

### Analysis Files

**Location:** `docs/`

- **`correlation_report.txt`** - Statistical correlation analysis
  - Shows relationships between sentiment, ridership, and complaints
  - Includes p-values and significance indicators

**Location:** `visualizations/`

- **`sentiment_vs_ridership.html`** - Interactive chart comparing sentiment and ridership
- **`time_series.html`** - Time series of all metrics
- **`correlation_matrix.html`** - Heatmap of correlations
- **`complaint_heatmap.html`** - Complaint density visualization
- **`sentiment_distribution.html`** - Distribution of sentiment scores
- **`correlation_matrix.csv`** - Correlation data in CSV format

### Viewing HTML Visualizations

Open any `.html` file in your web browser:
```bash
# On macOS:
open visualizations/sentiment_vs_ridership.html

# On Linux:
xdg-open visualizations/sentiment_vs_ridership.html

# On Windows:
start visualizations/sentiment_vs_ridership.html
```

---

## Troubleshooting

### Issue: "Module not found" Error

**Problem:** Python can't find required packages

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: "No data available" in Dashboard

**Problem:** Dashboard shows "No data available" message

**Solution:**
1. Check that `data/combined/combined_data.csv` exists:
   ```bash
   ls -lh data/combined/combined_data.csv
   ```

2. If missing, run the integration step:
   ```bash
   python src/sentiment/integrate_data.py
   ```

3. Verify the file has data:
   ```bash
   python -c "import pandas as pd; df = pd.read_csv('data/combined/combined_data.csv'); print(f'Rows: {len(df)}')"
   ```

### Issue: Dashboard Won't Start

**Problem:** Error when running `python src/visualization/dashboard.py`

**Solution:**
1. Check if port 8050 is already in use:
   ```bash
   # On macOS/Linux:
   lsof -i :8050
   
   # If port is in use, kill the process or change port in dashboard.py
   ```

2. Check for import errors:
   ```bash
   python -c "import dash; import plotly; print('OK')"
   ```

3. Verify combined_data.csv exists and has data

### Issue: "No complaint types" in Dropdown

**Problem:** Complaint type filter only shows "All"

**Solution:**
1. Check that `data/cleaned/311_data.csv` exists and has `service_request_type` column:
   ```bash
   python -c "import pandas as pd; df = pd.read_csv('data/cleaned/311_data.csv'); print('Types:', df['service_request_type'].nunique() if 'service_request_type' in df.columns else 'Column missing')"
   ```

2. If missing, regenerate 311 data:
   ```bash
   python src/utils/generate_sample_data.py
   ```

### Issue: Twitter API Errors

**Problem:** Can't collect Twitter data

**Solution:**
1. Use sample data instead (recommended):
   ```bash
   python src/data_collection/generate_cta_tweets.py
   ```

2. Or verify `.env` file exists with correct credentials:
   ```bash
   cat .env
   # Should show: TWITTER_BEARER_TOKEN=your_token_here
   ```

### Issue: "File not found" Errors

**Problem:** Scripts can't find data files

**Solution:**
1. Make sure you're in the project root directory:
   ```bash
   pwd
   # Should show: /Users/mukul/Desktop/chieac project
   ```

2. Check file paths are correct:
   ```bash
   ls data/cleaned/
   ```

### Issue: Pandas Warnings

**Problem:** DtypeWarning about mixed types

**Solution:**
This is a warning, not an error. The code handles it automatically. If you want to suppress:
```python
# Add to scripts: pd.read_csv(..., low_memory=False)
```

---

## Next Steps

### View Results

1. **Open the Dashboard:**
   ```bash
   python src/visualization/dashboard.py
   ```
   Then open http://127.0.0.1:8050

2. **View HTML Visualizations:**
   ```bash
   open visualizations/*.html
   ```

3. **Read Correlation Report:**
   ```bash
   cat docs/correlation_report.txt
   ```

### Explore the Data

1. **Open Jupyter Notebooks:**
   ```bash
   jupyter notebook
   ```
   Then open notebooks in the `notebooks/` folder

2. **Analyze Combined Data:**
   ```python
   import pandas as pd
   df = pd.read_csv('data/combined/combined_data.csv')
   print(df.describe())
   print(df.head())
   ```

### Customize Analysis

1. **Modify Date Range:** Edit scripts to change date ranges
2. **Add New Metrics:** Extend the integration script
3. **Create Custom Visualizations:** Modify `visualizations.py`
4. **Adjust Dashboard:** Edit `dashboard.py` to add new charts

### Share Your Results

1. **Screenshot the Dashboard:** Take screenshots of key visualizations
2. **Export Data:** Share CSV files for further analysis
3. **Create Presentation:** Use insights from `docs/insights.md`

---

## Quick Reference

### Essential Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Generate Sample Data
python src/data_collection/generate_cta_tweets.py
python src/utils/generate_sample_data.py

# Run Complete Pipeline
python complete_project.py

# Launch Dashboard
python src/visualization/dashboard.py
```

### File Locations

- **Data:** `data/cleaned/` and `data/combined/`
- **Visualizations:** `visualizations/`
- **Reports:** `docs/`
- **Scripts:** `src/`

### Key Files

- **Pipeline Runner:** `complete_project.py`
- **Dashboard:** `src/visualization/dashboard.py`
- **Combined Data:** `data/combined/combined_data.csv` (required for dashboard)

---

## Getting Help

If you encounter issues not covered here:

1. **Check Logs:** Look at terminal output for error messages
2. **Verify Data:** Ensure all required CSV files exist
3. **Read Documentation:** Check `README.md` and `QUICK_START.md`
4. **Review Code:** Check script files for comments and documentation

---

## Summary

**Complete Workflow:**

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Generate sample data: `python src/data_collection/generate_cta_tweets.py`
3. ✅ Run pipeline: `python complete_project.py`
4. ✅ Launch dashboard: `python src/visualization/dashboard.py`
5. ✅ Open browser: http://127.0.0.1:8050

**Total Time:** ~10-15 minutes for first-time setup, ~2-5 minutes for subsequent runs

---

*Happy analyzing! 🚀*

