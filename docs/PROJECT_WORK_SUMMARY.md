# CityPulse Project Work Summary

## Project Overview

**CityPulse: Urban Sentiment & Mobility Dashboard** is an integrated dashboard that visualizes public sentiment and mobility patterns in Chicago, combining social media sentiment analysis with official city transportation and 311 service data to reveal civic trends and commuter experiences.

**Project Goal**: Build a comprehensive analytics platform that demonstrates applied NLP, API integration, data wrangling, and visualization techniques while providing actionable insights for civic planners and transit operations.

---

## Complete Feature List

### Data Collection & Processing

#### 1. Twitter/X Data Collection
- **Implementation**: Twitter API v2 via `tweepy` library
- **Hashtags Tracked**: #CTA, #CTAFail, #CTADelays, #CTARedLine, #CTABlueLine, #ChicagoCommute, #CTABus
- **Volume**: 1,063+ tweets (exceeds 1,000 requirement)
- **Alternative**: Sample data generator for demonstration purposes
- **Features**:
  - Real-time tweet collection via official API
  - Realistic sample data generation with sentiment patterns
  - Time-based sentiment distribution (weekday/weekend patterns)
  - Hashtag extraction and categorization

#### 2. CTA Ridership Data Collection
- **Source**: Chicago Data Portal
- **Data Types**: Bus and Train (L) ridership
- **Implementation**: Automated API collection
- **Features**:
  - Daily ridership aggregation
  - Route-level data collection
  - Time series data processing

#### 3. 311 Service Requests Collection
- **Source**: Chicago 311 API
- **Complaint Types**: 37+ realistic complaint types including:
  - Infrastructure: Pothole, Street Light Out, Traffic Signal Out
  - Transit: Bus Stop Request, Transit Delay Report
  - Safety: Abandoned Vehicle, Graffiti Removal
  - Environmental: Tree Debris, Rodent Baiting
  - And many more...
- **Volume**: 2,351+ complaints
- **Features**:
  - Geospatial data with coordinates
  - Status tracking (Open, Closed, Completed)
  - Date tracking (created, updated, closed)
  - Ward and community area mapping

### Data Processing Pipeline

#### 1. Data Cleaning (`src/data_cleaning/clean_data.py`)
- **Features**:
  - Missing value handling
  - Duplicate removal
  - Timestamp normalization
  - Coordinate validation (Chicago city limits)
  - Data type standardization
  - Address normalization

#### 2. Sentiment Analysis (`src/sentiment/sentiment_analyzer.py`)
- **Methods**: Dual-method analysis
  - **VADER**: Optimized for social media sentiment
  - **TextBlob**: General-purpose sentiment analysis
- **Outputs**:
  - Polarity scores (-1 to 1)
  - Subjectivity scores (0 to 1)
  - Sentiment categorization (positive, neutral, negative)
  - Daily aggregation

#### 3. Data Integration (`src/sentiment/integrate_data.py`)
- **Features**:
  - Multi-source data merging by date
  - Date alignment across datasets
  - Missing value handling
  - Data validation
  - Combined dataset generation

### Analysis & Statistics

#### 1. Correlation Analysis (`src/visualization/correlation_analysis.py`)
- **Relationships Analyzed**:
  - Sentiment vs. Ridership
  - Sentiment vs. Complaints
  - Negative tweets vs. 311 complaints
- **Statistical Methods**:
  - Pearson correlation coefficients
  - Statistical significance testing (p < 0.05)
  - Confidence intervals (95%)
  - Effect sizes (Cohen's d, R-squared)
  - Linear regression analysis

#### 2. Advanced Statistical Analysis (`src/analytics/statistical_analysis.py`)
- **Features**:
  - Confidence interval calculation
  - P-value computation
  - Effect size measurement
  - Regression coefficient analysis
  - Comprehensive statistical reporting

#### 3. Geographic Analysis (`src/analytics/neighborhood_analysis.py`)
- **Features**:
  - Neighborhood-level aggregation
  - Ward-level analysis
  - Hotspot detection using DBSCAN clustering
  - Area comparison functionality
  - Geographic pattern identification

### Interactive Dashboard Features

#### Core Dashboard (`src/visualization/dashboard.py`)

**Layout & Design**:
- Professional header with branding
- Consistent color palette
- Responsive Bootstrap layout
- Font Awesome icons
- Custom CSS styling
- Professional footer

**Key Metrics Cards**:
- Average Sentiment Score
- Total CTA Rides
- Total 311 Complaints
- Total Tweets
- All with icons and formatted numbers

**Interactive Charts**:
1. **Sentiment vs. Ridership Scatter Plot**
   - Interactive hover tooltips
   - Correlation visualization
   - Trend line overlay

2. **Time Series Overview**
   - Multi-metric time series
   - Sentiment, ridership, and complaints
   - Interactive zoom and pan

3. **Sentiment Distribution**
   - Positive, neutral, negative breakdown
   - Percentage visualization
   - Color-coded categories

4. **Top Hashtags**
   - Horizontal bar chart
   - Frequency visualization
   - Interactive selection

5. **Complaint Density Map**
   - Geospatial visualization using Plotly Mapbox
   - Custom symbols per complaint type
   - Detailed hover information
   - Color-coded by complaint type
   - Legend for complaint types
   - Scroll zoom enabled
   - Coordinate validation (Chicago boundaries)

6. **Box & Violin Plots**
   - Sentiment distribution by day of week
   - Statistical distribution visualization
   - Outlier detection

7. **Gauge Charts**
   - Sentiment Score gauge
   - Complaint Rate gauge
   - Ridership Index gauge
   - Threshold indicators

8. **Sunburst Chart**
   - Hierarchical complaint breakdown
   - Status → Type hierarchy
   - Interactive drill-down

9. **Neighborhood Analysis**
   - Top neighborhoods by complaint count
   - Ward-level aggregation
   - Hotspot visualization

**Filtering Capabilities**:
- Date range picker (start and end dates)
- Complaint type filter (37+ types)
- Neighborhood/Ward filter
- Real-time chart updates

**Export Capabilities** (`src/utils/export_utils.py`):
- Export charts as PNG
- Export charts as PDF
- Export data as CSV
- Export data as Excel
- Generate comprehensive PDF reports

**Statistical Analysis Display**:
- Correlation coefficients with p-values
- Confidence intervals
- Effect sizes
- Regression coefficients
- Significance indicators

**Help & Documentation**:
- About modal with project information
- Help modal with user guide
- Keyboard shortcuts documentation
- Methodology explanations

### Static Visualizations (`src/visualization/visualizations.py`)

- Sentiment vs. ridership plots
- Time series overview charts
- Correlation matrices
- Complaint heatmaps
- Sentiment distribution charts
- HTML and PNG export formats

### Export & Integration

#### Tableau/Power BI Export (`scripts/export_for_tableau.py`)
- Optimized CSV export
- Excel export with formatting
- Calculated fields for analysis
- Date breakdowns
- Sentiment ratios
- Complaint rates
- Dashboard creation guide

---

## Technical Stack & Architecture

### Technology Stack

**Languages**:
- Python 3.8+

**Core Libraries**:
- **Data Manipulation**: pandas, numpy
- **Visualization**: matplotlib, seaborn, plotly
- **Dashboard**: dash, dash-bootstrap-components
- **Sentiment Analysis**: VADER, TextBlob
- **API Integration**: tweepy, requests
- **Statistical Analysis**: scipy, scikit-learn
- **Export**: reportlab, openpyxl, kaleido

**Data Sources**:
- Chicago 311 Service Requests API
- Chicago Transit Authority (CTA) Ridership Data
- Twitter/X API v2 (via tweepy)

### Architecture

**Modular Structure**:
```
src/
├── data_collection/    # API integration and data collection
├── data_cleaning/      # Data preprocessing and validation
├── sentiment/          # Sentiment analysis and aggregation
├── visualization/      # Dashboard and static visualizations
├── analytics/          # Advanced statistical and geographic analysis
└── utils/              # Utility functions and data generation
```

**Data Flow**:
1. Raw data collection → `data/raw/`
2. Data cleaning → `data/cleaned/`
3. Sentiment analysis → `data/cleaned/tweets_with_sentiment.csv`
4. Data integration → `data/combined/combined_data.csv`
5. Visualization → Interactive dashboard + static charts

---

## File Structure & Organization

### Project Structure
```
chieac-project/
├── data/
│   ├── raw/              # Raw data from APIs
│   ├── cleaned/          # Processed datasets
│   ├── combined/         # Integrated datasets
│   └── exports/          # Tableau/Power BI exports
├── notebooks/
│   ├── week1_data_cleaning.ipynb
│   ├── week2_sentiment_analysis.ipynb
│   └── week3_analysis.ipynb
├── src/
│   ├── data_collection/  # 6 scripts
│   ├── data_cleaning/    # 1 module
│   ├── sentiment/        # 3 modules
│   ├── visualization/    # 3 modules
│   ├── analytics/        # 2 modules
│   └── utils/            # 2 modules
├── docs/
│   ├── data_dictionary.md
│   ├── insights.md
│   ├── 1_page_insights.md
│   ├── tableau_dashboard_guide.md
│   └── [this document]
├── scripts/
│   └── export_for_tableau.py
├── visualizations/       # Generated static charts
├── requirements.txt
├── README.md
├── HOW_TO_RUN.md
├── complete_project.py
└── run_pipeline.py
```

### Code Statistics
- **Total Modules**: 16+ Python modules
- **Total Functions**: 85+ functions
- **Lines of Code**: ~5,000+ lines
- **Documentation**: Comprehensive README, guides, and inline docs

---

## Key Achievements & Milestones

### Week 1: Data Collection & Cleaning ✅
- ✅ Collected/generated data from all three sources
- ✅ Implemented comprehensive data cleaning pipeline
- ✅ Created data dictionary documentation
- ✅ Generated 37+ complaint types
- ✅ Validated coordinate bounds for Chicago

### Week 2: Sentiment Analysis & Integration ✅
- ✅ Implemented dual-method sentiment analysis (VADER + TextBlob)
- ✅ Created sentiment aggregation by day
- ✅ Integrated all datasets by date
- ✅ Validated data alignment

### Week 3: Correlation & Visualization ✅
- ✅ Performed comprehensive correlation analysis
- ✅ Generated statistical reports
- ✅ Created static visualizations
- ✅ Built prototype dashboard

### Week 4: Dashboard Finalization & Storytelling ✅
- ✅ Polished interactive dashboard
- ✅ Added advanced features (export, statistics, new charts)
- ✅ Created Tableau/Power BI export package
- ✅ Wrote 1-page data story
- ✅ Completed all documentation

### Additional Enhancements ✅
- ✅ Professional UI/UX improvements
- ✅ Advanced statistical analysis integration
- ✅ Geographic analysis with hotspot detection
- ✅ Export capabilities (PNG, PDF, CSV, Excel)
- ✅ Help and About documentation
- ✅ Map enhancements with custom symbols
- ✅ Coordinate validation and bounds adjustment

---

## Data Volumes & Quality

### Data Volumes
- **Tweets**: 1,063 (exceeds 1,000 requirement)
- **311 Complaints**: 2,351 with 37+ types
- **CTA Ridership**: Daily data for analysis period
- **Combined Dataset**: Fully integrated and validated

### Data Quality
- ✅ Valid coordinates (within Chicago city limits)
- ✅ Proper date formatting
- ✅ No duplicate records
- ✅ Missing values handled appropriately
- ✅ Consistent data types
- ✅ Coordinate bounds validation (Lakefront Trail boundary)

---

## Deliverables Completed

### Required Deliverables ✅
1. ✅ Cleaned datasets (CSV format)
2. ✅ Integrated dataset (combined_data.csv)
3. ✅ Sentiment analysis output
4. ✅ Correlation analysis report
5. ✅ Interactive dashboard
6. ✅ Static visualizations
7. ✅ Comprehensive documentation

### Additional Deliverables ✅
1. ✅ Tableau/Power BI export package
2. ✅ Dashboard creation guide
3. ✅ 1-page data story
4. ✅ Advanced statistical analysis
5. ✅ Geographic analysis
6. ✅ Export utilities
7. ✅ Sample data generators

---

## Technical Highlights

### Code Quality
- Modular code structure
- Proper error handling
- Comprehensive logging
- Code documentation
- Reusable functions
- Clean separation of concerns

### User Experience
- Professional, polished interface
- Intuitive navigation
- Responsive design
- Interactive visualizations
- Helpful error messages
- Comprehensive help documentation

### Performance
- Efficient data processing
- Optimized queries
- Lazy loading where applicable
- Map performance optimization (2,000 point limit)
- Fast dashboard updates

---

## Project Status

**Status**: ✅ **COMPLETE**

All core requirements have been met and exceeded. The project includes:
- Complete data pipeline
- Comprehensive analysis
- Professional dashboard
- Extensive documentation
- Additional advanced features

**Ready for**: Presentation, portfolio showcase, and future development

---

*Last Updated: December 2024*

