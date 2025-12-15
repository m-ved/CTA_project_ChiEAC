# CityPulse: Urban Sentiment & Mobility Dashboard

An integrated dashboard that visualizes public sentiment and mobility patterns in Chicago, combining social media sentiment analysis with official city transportation and 311 service data to reveal civic trends and commuter experiences.

## Project Overview

CityPulse integrates multiple data sources to provide insights into how Chicagoans' moods correlate with daily mobility challenges. The project demonstrates applied NLP, API integration, data wrangling, and visualization techniques.

## Features

- **Sentiment Analysis**: Analyzes Twitter/X posts using VADER and TextBlob to extract public sentiment
- **Data Integration**: Combines social media sentiment with CTA ridership and 311 service request data
- **Interactive Dashboard**: Real-time visualization of trends and correlations
- **Correlation Analysis**: Identifies relationships between sentiment, ridership, and complaints
- **Geospatial Visualization**: Maps complaint locations and sentiment patterns

## Technology Stack

- **Languages**: Python 3.8+
- **Libraries**: 
  - pandas, numpy - Data manipulation
  - matplotlib, seaborn, plotly - Visualization
  - snscrape - Twitter data collection
  - TextBlob, VADER - Sentiment analysis
  - requests - API integration
  - dash, dash-bootstrap-components - Interactive dashboard
- **Data Sources**:
  - Chicago 311 Service Requests API
  - Chicago Transit Authority (CTA) Ridership Data
  - Twitter/X (via snscrape)

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
│   └── README.md
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

Note: If `snscrape` installation fails, you may need to install it separately:
```bash
pip install git+https://github.com/JustAnotherArchivist/snscrape.git
```

## Usage

### 1. Data Collection

Collect data from all sources:

```bash
# Collect 311 service requests
python src/data_collection/collect_311_data.py

# Collect CTA ridership data
python src/data_collection/collect_cta_data.py

# Collect Twitter data
python src/data_collection/collect_tweets.py
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

### 3. Sentiment Analysis

Analyze tweet sentiment and aggregate by day:

```bash
# Analyze sentiment
python src/sentiment/sentiment_analyzer.py

# Aggregate by day
python src/sentiment/aggregate_sentiment.py

# Integrate all datasets
python src/sentiment/integrate_data.py
```

Or use the Week 2 notebook:
```bash
jupyter notebook notebooks/week2_sentiment_analysis.ipynb
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

Launch the interactive dashboard:

```bash
python src/visualization/dashboard.py
```

The dashboard will be available at `http://127.0.0.1:8050`

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

### Twitter/X Data
- **Source**: Twitter/X via snscrape
- **Hashtags**: #ChicagoCommute, #CTA, #RushHour, #Chicago, #ChiTransit, #ChicagoTraffic
- **Data**: Tweet content, timestamps, engagement metrics
- **Volume**: ~1,000-2,000 tweets per collection

## Methodology

### Sentiment Analysis

1. **VADER**: Valence Aware Dictionary and sEntiment Reasoner
   - Optimized for social media text
   - Provides compound polarity score (-1 to 1)

2. **TextBlob**: General-purpose sentiment analysis
   - Provides polarity (-1 to 1) and subjectivity (0 to 1) scores

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

### Documentation
- `docs/data_dictionary.md` - Complete data dictionary
- `docs/insights.md` - Key findings and insights

## Limitations

1. **Data Quality**: Social media data may not represent all demographics
2. **Sample Size**: Limited tweet volume may affect statistical significance
3. **Causation**: Correlations do not imply causation
4. **External Factors**: Weather, events, and news can influence sentiment
5. **Bias**: Social media users may not represent the full population

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
- snscrape developers for Twitter scraping capabilities
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

