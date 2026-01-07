# CityPulse: Urban Mobility & Service Dashboard

An integrated dashboard that visualizes mobility patterns and service requests in Chicago, combining transportation data, bike share usage, crime statistics, and 311 service data to reveal urban trends and patterns.

## Project Overview

CityPulse integrates multiple data sources to provide insights into how transportation usage, bike share patterns, crime, and service requests correlate with each other. The project demonstrates API integration, data wrangling, statistical analysis, and visualization techniques.

## Features

- **Data Integration**: Combines CTA ridership, traffic volume, crime data, and 311 service request data
- **Interactive Dashboard**: Real-time visualization of trends and correlations
- **Correlation Analysis**: Identifies relationships between ridership, complaints, bike trips, and crime
- **Geospatial Visualization**: Maps complaint locations with detailed information
- **Statistical Analysis**: Advanced statistical metrics including confidence intervals, p-values, and effect sizes

## Technology Stack

- **Languages**: Python 3.8+
- **Libraries**: 
  - pandas, numpy - Data manipulation
  - matplotlib, seaborn, plotly - Visualization
  - requests - API integration
  - dash, dash-bootstrap-components - Interactive dashboard
  - scipy, scikit-learn - Statistical analysis
  - python-dotenv - Environment variable management
- **Data Sources**:
  - Chicago 311 Service Requests API
  - Chicago Transit Authority (CTA) Ridership Data
  - Traffic Volume Data
  - Chicago Crime Data

## Project Structure

```
chieac-project/
├── data/
│   ├── raw/              # Raw data from APIs and scraping
│   ├── cleaned/          # Processed and cleaned datasets
│   └── combined/         # Integrated datasets
├── notebooks/
│   ├── week1_data_cleaning.ipynb
│   ├── week2_sentiment_analysis.ipynb
│   └── week3_analysis.ipynb
├── src/
│   ├── data_collection/  # Data collection scripts
│   ├── data_cleaning/   # Data cleaning modules
│   ├── sentiment/       # Sentiment analysis modules
│   └── visualization/   # Visualization and dashboard code
├── docs/
│   ├── data_dictionary.md
│   ├── insights.md
│   ├── 1_page_insights.md
│   ├── tableau_dashboard_guide.md
│   └── README.md
├── data/
│   └── exports/          # Tableau/Power BI export files
├── scripts/
│   └── export_for_tableau.py
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd "chieac project"
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables (if needed):
   - Create a `.env` file in the project root if you need to customize API endpoints or settings

## Quick Start

Follow these steps to get CityPulse up and running quickly:

### Option A: Run Everything at Once (Recommended)

```bash
python run_pipeline.py
```

This will run all steps sequentially: data collection, cleaning, and visualization.

### Option B: Step-by-Step

1. **Collect Data** (using Jupyter Notebooks - Recommended for first time):
   ```bash
   jupyter notebook
   # Then open and run: notebooks/week1_data_cleaning.ipynb
   ```

   Or run scripts directly:
   ```bash
   # Collect 311 data
   python src/data_collection/collect_311_data.py
   
   # Collect CTA ridership data
   python src/data_collection/collect_cta_data.py
   
   # Collect traffic volume data
   python src/data_collection/collect_traffic_data.py
   
   # Collect crime data
   python src/data_collection/collect_crime_data.py
   ```

2. **Clean the Data**:
   ```bash
   python src/data_cleaning/clean_data.py
   ```
   Or run the cleaning section in `notebooks/week1_data_cleaning.ipynb`

3. **Integrate Data**:
   ```bash
   # Integrate all datasets
   python src/sentiment/integrate_data.py
   ```

4. **Create Visualizations**:
   ```bash
   # Run correlation analysis
   python src/visualization/correlation_analysis.py
   
   # Generate visualizations
   python src/visualization/visualizations.py
   ```
   Or use `notebooks/week3_analysis.ipynb`

5. **Launch the Dashboard**:
   ```bash
   python src/visualization/dashboard.py
   ```
   Then open your browser to: **http://127.0.0.1:8050**

### What to Expect

After running the pipeline, you should have:
- **Data files** in `data/cleaned/` and `data/combined/`
- **Visualizations** in `visualizations/` folder
- **Correlation report** in `docs/correlation_report.txt`
- **Interactive dashboard** running on localhost

## Usage

### 1. Data Collection

Collect data from all sources:

```bash
# Collect 311 service requests
python src/data_collection/collect_311_data.py

# Collect CTA ridership data
python src/data_collection/collect_cta_data.py

# Collect traffic volume data
python src/data_collection/collect_traffic_data.py

# Collect crime data
python src/data_collection/collect_crime_data.py
```

Alternatively, run all collection scripts from the Week 1 notebook:
```bash
jupyter notebook notebooks/week1_data_cleaning.ipynb
```

### 2. Data Cleaning

Clean and preprocess all collected data:

```bash
python src/data_cleaning/clean_data.py
```

### 3. Data Integration

Integrate all datasets:

```bash
# Integrate all datasets
python src/sentiment/integrate_data.py
```

### 4. Analysis and Visualization

Perform correlation analysis and create visualizations:

```bash
# Correlation analysis
python src/visualization/correlation_analysis.py

# Generate visualizations
python src/visualization/visualizations.py
```

Or use the Week 3 notebook:
```bash
jupyter notebook notebooks/week3_analysis.ipynb
```

### 5. Interactive Dashboard

**Option A: Dash Dashboard (Python-based)**

Launch the interactive Dash dashboard:

```bash
python src/visualization/dashboard.py
```

The dashboard will be available at `http://127.0.0.1:8050`

**Option B: Tableau/Power BI Dashboard (Required by Project Spec)**

The project specification requires a Tableau or Power BI dashboard. To create one:

1. **Export data for Tableau/Power BI**:
   ```bash
   python scripts/export_for_tableau.py
   ```
   This creates optimized data files in `data/exports/`:
   - `combined_data_for_tableau.csv`
   - `combined_data_for_tableau.xlsx`

2. **Follow the dashboard guide**:
   - See `docs/tableau_dashboard_guide.md` for detailed step-by-step instructions
   - The guide covers both Tableau and Power BI dashboard creation
   - Includes all required features: time series, maps, filters, correlations

3. **Note on Data Sources**:
   - All data sources use official Chicago Data Portal APIs
   - Data is collected daily and aggregated by date
   - No external API credentials required for public data sources

## Data Sources

### Chicago 311 Service Requests
- **Source**: Chicago Data Portal - 311 Service Requests API
- **Endpoint**: `https://data.cityofchicago.org/resource/v6vf-nfxy.json`
- **Data**: Transit-related complaints (street lights, potholes, transit delays)
- **Update Frequency**: Real-time

### CTA Ridership Data
- **Source**: Chicago Data Portal
- **Endpoints**: 
  - Bus: `https://data.cityofchicago.org/resource/jyb9-n7fm.json`
  - Train: `https://data.cityofchicago.org/resource/fhrw-4uyv.json`
- **Data**: Daily ridership counts by route/station
- **Update Frequency**: Daily

### Traffic Volume Data
- **Source**: Chicago Data Portal
- **Endpoint**: `https://data.cityofchicago.org/resource/8v9j-bter.json`
- **Data**: Daily traffic volume counts, average speeds, traffic flow data
- **Update Frequency**: Daily

### Crime Data
- **Source**: Chicago Data Portal
- **Endpoint**: `https://data.cityofchicago.org/resource/ijzp-q8t2.json`
- **Data**: Daily crime counts by type, arrest rates, location data
- **Update Frequency**: Daily



## Methodology

### Data Integration

1. **Daily Aggregation**: All datasets are aggregated by date to enable correlation analysis
2. **Data Merging**: Multiple data sources are merged on date using outer joins to preserve all data points
3. **Missing Value Handling**: Missing values are filled with 0 for numeric columns to enable calculations

3. **Categorization**: 
   - Positive: polarity ≥ 0.05
   - Negative: polarity ≤ -0.05
   - Neutral: -0.05 < polarity < 0.05

### Data Integration

- All datasets are aggregated to daily granularity
- Merged by date with outer join to preserve all dates
- Missing values handled appropriately (0 for counts, mean for averages)

### Correlation Analysis

- Pearson correlation coefficients
- Statistical significance testing (p < 0.05)
- Focus on key relationships:
  - Sentiment vs. Ridership
  - Complaints vs. Negative Sentiment
  - Sentiment vs. Complaints

## Key Findings

See [docs/insights.md](docs/insights.md) for detailed findings. Summary:

1. **Monday Morning Rush**: Sentiment drops during Monday morning rush hours
2. **Sentiment-Complaint Correlation**: Moderate positive correlation between negative sentiment and 311 complaints
3. **Ridership-Sentiment Relationship**: Weak positive correlation between ridership and sentiment
4. **Weekly Patterns**: More positive sentiment on Fridays/weekends, complaints peak mid-week

## Visualizations

The project includes several types of visualizations:

1. **Time Series**: Sentiment trends vs. daily ridership
2. **Heatmaps**: Complaint density and correlation matrices
3. **Distribution Plots**: Sentiment score distributions
4. **Interactive Dashboard**: Multi-panel dashboard with filters
5. **Maps**: Geospatial visualization of complaints (if data available)

## Output Files

### Data Files
- `data/cleaned/311_data.csv` - Cleaned 311 service requests
- `data/cleaned/cta_ridership.csv` - Cleaned CTA ridership data
- `data/cleaned/tweets.csv` - Cleaned tweet data
- `data/cleaned/tweets_with_sentiment.csv` - Tweets with sentiment scores
- `data/combined/daily_sentiment.csv` - Daily aggregated sentiment
- `data/combined/combined_data.csv` - Fully integrated dataset

### Analysis Files
- `docs/correlation_report.txt` - Correlation analysis report
- `visualizations/correlation_matrix.csv` - Correlation matrix
- `visualizations/*.html` - Interactive visualizations

### Tableau/Power BI Export Files
- `data/exports/combined_data_for_tableau.csv` - Optimized data for Tableau/Power BI (CSV format)
- `data/exports/combined_data_for_tableau.xlsx` - Optimized data for Tableau/Power BI (Excel format)
- Created by running: `python scripts/export_for_tableau.py`

### Documentation
- `docs/data_dictionary.md` - Complete data dictionary
- `docs/insights.md` - Detailed findings and insights
- `docs/1_page_insights.md` - **1-page data story** (required by project spec)
- `docs/tableau_dashboard_guide.md` - Step-by-step guide for creating Tableau/Power BI dashboard

## Troubleshooting

### Issue: No data collected
- Check your internet connection
- Verify API endpoints are accessible
- Check the logs for error messages
- Ensure data collection scripts are running correctly

### Issue: Import errors
- Make sure you're in the project root directory
- Verify virtual environment is activated
- Check that all packages are installed: `pip list`
- Ensure you've installed tweepy: `pip install tweepy python-dotenv`

### Issue: Dashboard won't start
- Check if port 8050 is already in use
- Try changing the port in `dashboard.py`: `run_dashboard(port=8051)`

## Limitations

1. **Data Quality**: Data is dependent on API availability and data portal updates
2. **Sample Size**: Limited data periods may affect statistical significance
3. **Causation**: Correlations do not imply causation
4. **External Factors**: Weather, events, and news can influence patterns
5. **API Limits**: Some APIs may have rate limits or data availability constraints

## Future Extensions

See [docs/insights.md](docs/insights.md) for detailed future extensions:

1. Real-time data updates
2. Anomaly detection
3. Predictive analytics
4. Neighborhood-level analysis
5. Multi-modal integration
6. Advanced NLP features

## Contributing

This is a portfolio project. For questions or suggestions, please open an issue.

## License

This project is for educational and portfolio purposes.

## Acknowledgments

- Chicago Data Portal for providing open data APIs
- Twitter/X for providing the official API v2
- Tweepy developers for the excellent Twitter API wrapper
- VADER and TextBlob developers for sentiment analysis tools

## Author

**Mukul Ved**

Portfolio project demonstrating:
- Applied NLP and sentiment analysis
- API integration and data wrangling
- Data visualization and dashboard development
- Urban data science and public sentiment analytics

---

*CityPulse: Urban Sentiment & Mobility Dashboard - A comprehensive analysis of Chicago's transit sentiment and mobility patterns*

