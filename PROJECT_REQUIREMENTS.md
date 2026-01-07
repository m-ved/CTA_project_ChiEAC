# CityPulse Project Requirements

## Project Overview

**CityPulse: Urban Sentiment & Mobility Dashboard**

An integrated dashboard that visualizes public sentiment and mobility patterns in Chicago, combining social media sentiment analysis with official city transportation and 311 service data to reveal civic trends and commuter experiences.

---

## Core Requirements

### 1. Data Collection
- ✅ **Twitter/X Data**: Collect tweets related to CTA and Chicago transit
  - Hashtags: #CTAFail, #CTADelays, #CTA, #CTARedLine, #CTABlueLine, #ChicagoCommute, #CTABus
  - Volume: At least 1,000+ tweets recommended
  - Method: Twitter API v2 via tweepy (or sample data generator)

- ✅ **CTA Ridership Data**: Collect daily ridership data
  - Bus ridership data
  - Train (L) ridership data
  - Source: Chicago Data Portal

- ✅ **311 Service Requests**: Collect transit-related complaints
  - Street lights, potholes, traffic signals, etc.
  - Source: Chicago 311 API
  - Multiple complaint types (37+ types implemented)

### 2. Data Processing
- ✅ **Data Cleaning**: Clean and normalize all collected data
  - Handle missing values
  - Normalize timestamps
  - Remove duplicates
  - Standardize formats

- ✅ **Sentiment Analysis**: Analyze tweet sentiment
  - Use VADER (optimized for social media)
  - Use TextBlob (general-purpose)
  - Categorize as positive, neutral, or negative
  - Calculate polarity and subjectivity scores

- ✅ **Data Integration**: Combine all datasets
  - Aggregate by day
  - Merge sentiment, ridership, and complaint data
  - Align dates across datasets

### 3. Analysis
- ✅ **Correlation Analysis**: Identify relationships
  - Sentiment vs. Ridership
  - Sentiment vs. Complaints
  - Negative tweets vs. 311 complaints
  - Statistical significance testing (p < 0.05)

- ✅ **Time Series Analysis**: Identify patterns
  - Daily trends
  - Weekly patterns
  - Rush hour patterns
  - Weekend vs. weekday differences

### 4. Visualization
- ✅ **Interactive Dashboard**: Dash-based web dashboard
  - Key metrics cards (sentiment, ridership, complaints, tweets)
  - Time series charts
  - Correlation heatmaps
  - Sentiment distributions
  - Geospatial map of complaints
  - Top hashtags visualization
  - Date range filters
  - Complaint type filters

- ✅ **Static Visualizations**: HTML/PNG charts
  - Sentiment vs. ridership plots
  - Time series overview
  - Correlation matrices
  - Complaint heatmaps
  - Sentiment distributions

### 5. Documentation
- ✅ **README**: Comprehensive project documentation
- ✅ **Data Dictionary**: Complete variable descriptions
- ✅ **Insights Document**: Key findings and recommendations
- ✅ **How-to Guides**: Step-by-step instructions

---

## Technical Requirements

### Technology Stack
- **Language**: Python 3.8+
- **Data Manipulation**: pandas, numpy
- **Visualization**: matplotlib, seaborn, plotly
- **Dashboard**: dash, dash-bootstrap-components
- **Sentiment Analysis**: VADER, TextBlob
- **API Integration**: tweepy, requests
- **Statistical Analysis**: scipy

### Data Sources
1. **Chicago 311 Service Requests API**
   - Endpoint: `https://data.cityofchicago.org/resource/v6vf-nfxy.json`
   - Transit-related complaints

2. **CTA Ridership Data**
   - Bus: `https://data.cityofchicago.org/resource/jyb9-n7fm.json`
   - Train: `https://data.cityofchicago.org/resource/5neh-572f.json`

3. **Twitter/X API v2**
   - Via tweepy library
   - Or sample data generator (for demo purposes)

---

## Deliverables

### Required Outputs

1. ✅ **Cleaned Datasets**
   - `data/cleaned/tweets.csv` - Processed tweets
   - `data/cleaned/tweets_with_sentiment.csv` - Tweets with sentiment scores
   - `data/cleaned/311_data.csv` - Cleaned 311 complaints
   - `data/cleaned/cta_ridership.csv` - Cleaned CTA data

2. ✅ **Integrated Dataset**
   - `data/combined/combined_data.csv` - All data merged by date
   - `data/combined/daily_sentiment.csv` - Daily sentiment aggregation

3. ✅ **Analysis Reports**
   - `docs/correlation_report.txt` - Statistical correlation analysis
   - `docs/insights.md` - Key findings and recommendations

4. ✅ **Visualizations**
   - Interactive HTML visualizations in `visualizations/` folder
   - Correlation matrices
   - Time series charts
   - Geospatial maps

5. ✅ **Interactive Dashboard**
   - Web-based dashboard accessible at http://127.0.0.1:8050
   - Multiple chart types
   - Filtering capabilities
   - Real-time updates

6. ✅ **Documentation**
   - README.md - Project overview and setup
   - HOW_TO_RUN.md - Step-by-step guide
   - Data dictionary
   - Code documentation

---

## Key Features Required

### 1. Sentiment Analysis
- ✅ Dual-method analysis (VADER + TextBlob)
- ✅ Sentiment categorization (positive/neutral/negative)
- ✅ Polarity and subjectivity scores
- ✅ Daily aggregation

### 2. Data Integration
- ✅ Multi-source data merging
- ✅ Date alignment
- ✅ Missing value handling
- ✅ Data validation

### 3. Correlation Analysis
- ✅ Pearson correlation coefficients
- ✅ Statistical significance testing
- ✅ Multiple relationship analysis
- ✅ Report generation

### 4. Interactive Dashboard
- ✅ Real-time data visualization
- ✅ Multiple chart types
- ✅ Filtering (date range, complaint type)
- ✅ Key metrics display
- ✅ Geospatial visualization
- ✅ Responsive design

### 5. Geospatial Features
- ✅ Complaint location mapping
- ✅ Coordinate validation (within Chicago bounds)
- ✅ Interactive map with hover data
- ✅ Proper map constraints (no auto-scrolling)

---

## Data Requirements

### Minimum Data Volume
- **Tweets**: 1,000+ tweets (currently: 1,063 tweets)
- **311 Complaints**: Multiple types, sufficient for analysis (currently: 2,351 complaints)
- **CTA Ridership**: Daily data for analysis period (currently: 22 days)

### Data Quality Requirements
- ✅ Valid coordinates (within Chicago city limits)
- ✅ Proper date formatting
- ✅ No duplicate records
- ✅ Missing values handled appropriately
- ✅ Consistent data types

---

## Functional Requirements

### 1. Pipeline Execution
- ✅ Automated pipeline script (`complete_project.py`)
- ✅ Step-by-step execution capability
- ✅ Error handling and logging
- ✅ Progress reporting

### 2. Dashboard Functionality
- ✅ Load and display combined data
- ✅ Filter by date range
- ✅ Filter by complaint type
- ✅ Update charts dynamically
- ✅ Display key metrics
- ✅ Handle missing data gracefully

### 3. Data Generation (Alternative)
- ✅ Sample data generator for tweets
- ✅ Sample data generator for 311 complaints
- ✅ Sample data generator for CTA ridership
- ✅ Realistic data patterns
- ✅ Proper coordinate bounds

---

## Quality Requirements

### Code Quality
- ✅ Modular code structure
- ✅ Proper error handling
- ✅ Logging and progress reporting
- ✅ Code documentation
- ✅ Reusable functions

### Data Quality
- ✅ Data validation
- ✅ Coordinate bounds checking
- ✅ Date alignment
- ✅ Missing value handling
- ✅ Duplicate removal

### User Experience
- ✅ Clear documentation
- ✅ Easy setup process
- ✅ Intuitive dashboard
- ✅ Helpful error messages
- ✅ Visual appeal

---

## Success Criteria

### Minimum Viable Project
- ✅ All data sources collected/generated
- ✅ Sentiment analysis completed
- ✅ Data integration successful
- ✅ Correlation analysis performed
- ✅ Dashboard functional
- ✅ Visualizations generated
- ✅ Documentation complete

### Project Completion Status

**Data Collection**: ✅ Complete
- Tweets: 1,063 (exceeds 1,000 requirement)
- 311 Complaints: 2,351 with 37+ types
- CTA Ridership: Available

**Data Processing**: ✅ Complete
- Sentiment analysis: VADER + TextBlob
- Data cleaning: All datasets cleaned
- Integration: All data merged

**Analysis**: ✅ Complete
- Correlation analysis: Multiple relationships identified
- Statistical testing: Significance tests performed
- Insights: Documented in insights.md

**Visualization**: ✅ Complete
- Interactive dashboard: Functional
- Static visualizations: Generated
- Geospatial maps: Working with proper bounds

**Documentation**: ✅ Complete
- README: Comprehensive
- How-to guides: Available
- Data dictionary: Complete
- Code: Documented

---

## Project Status: ✅ COMPLETE

All core requirements have been met. The project is fully functional and ready for presentation.

---

*Last Updated: Based on current project state*

