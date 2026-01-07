# Tableau/Power BI Dashboard Creation Guide

This guide provides step-by-step instructions for creating the CityPulse dashboard in Tableau or Power BI, as required by the project specification.

## Prerequisites

1. **Data Files**: Ensure you have exported the data using:
   ```bash
   python scripts/export_for_tableau.py
   ```
   This creates files in `data/exports/`:
   - `combined_data_for_tableau.csv` (primary)
   - `combined_data_for_tableau.xlsx` (alternative)

2. **Software**: 
   - Tableau Desktop (free trial available) OR
   - Power BI Desktop (free)

## Data Overview

The exported dataset contains:
- **69 days** of data (September 9 - December 31, 2025)
- **25 columns** including:
  - Date fields (date, year, month, week, day_of_week)
  - Sentiment metrics (avg_polarity, sentiment_category, positive/negative/neutral ratios)
  - CTA ridership (total_cta_rides, bus_rides, train_rides)
  - 311 complaints (total_311_complaints, transit_related_complaints)

## Tableau Dashboard Instructions

### Step 1: Import Data

1. Open Tableau Desktop
2. Click "Connect to Data" → "Text file" or "Excel"
3. Navigate to `data/exports/combined_data_for_tableau.csv` (or .xlsx)
4. Click "Open"
5. Drag the data source to "Drag sheets here"

### Step 2: Create Time Series Chart (Sentiment vs Ridership)

1. **Create a dual-axis chart**:
   - Drag `date` to Columns
   - Drag `avg_polarity` to Rows (first measure)
   - Right-click `total_cta_rides` → "Add to Sheet" → "Dual Axis"
   - Format: Right-click axis → "Synchronize Axis" (uncheck for different scales)

2. **Add formatting**:
   - Color: `avg_polarity` (green to red gradient)
   - Size: `total_tweets` (if available)
   - Tooltip: Include date, sentiment, ridership, complaints

3. **Title**: "Daily Sentiment vs CTA Ridership"

### Step 3: Create Geospatial Map (Complaint Locations)

**Note**: For this, you'll need the 311 data with coordinates:

1. **Import 311 data**:
   - Connect to `data/cleaned/311_data.csv`
   - Filter for records with valid `latitude` and `longitude`

2. **Create map**:
   - Drag `longitude` to Columns
   - Drag `latitude` to Rows
   - Tableau will automatically create a map

3. **Add details**:
   - Drag `service_request_type` to Color
   - Drag `created_date` to Size or Label
   - Add filters: Date range, Complaint type

4. **Title**: "311 Complaint Locations in Chicago"

### Step 4: Create Correlation Heatmap

1. **Create correlation matrix**:
   - Create a new sheet
   - Drag key metrics to both Rows and Columns:
     - `avg_polarity`
     - `total_cta_rides`
     - `total_311_complaints`
     - `negative_ratio`
   
2. **Calculate correlations**:
   - Use Tableau's built-in CORR() function
   - Format as heatmap with color gradient

3. **Title**: "Correlation Matrix: Sentiment, Ridership, Complaints"

### Step 5: Create Sentiment Distribution Chart

1. **Create bar chart**:
   - Drag `sentiment_category` to Columns
   - Drag `total_tweets` to Rows
   - Color by `sentiment_category`

2. **Title**: "Sentiment Distribution"

### Step 6: Create Top Hashtags Visualization

**Note**: This requires tweet-level data from `data/cleaned/tweets.csv`:

1. **Import tweet data**:
   - Connect to `data/cleaned/tweets.csv`
   - Extract hashtags (may need data preparation)

2. **Create visualization**:
   - Count hashtags
   - Sort by frequency
   - Display top 10-20

### Step 7: Add Interactive Filters

1. **Date Range Filter**:
   - Drag `date` to Filters
   - Select "Range of Dates"
   - Show filter on dashboard

2. **Complaint Type Filter** (if using 311 detail data):
   - Drag `service_request_type` to Filters
   - Show filter on dashboard

3. **Sentiment Category Filter**:
   - Drag `sentiment_category` to Filters
   - Show filter on dashboard

### Step 8: Create Dashboard Layout

1. **Create new dashboard**:
   - Click "New Dashboard"
   - Set size: 1200 x 800 (or custom)

2. **Add sheets**:
   - Time series chart (top, full width)
   - Map (left, 50% width)
   - Correlation heatmap (right, 50% width)
   - Sentiment distribution (bottom left)
   - Top hashtags (bottom right)

3. **Add filters**:
   - Place filters in a sidebar or top bar
   - Make them apply to all relevant sheets

4. **Add tooltips**:
   - Customize tooltips for each chart
   - Include key metrics and insights

### Step 9: Finalize Dashboard

1. **Add title**: "CityPulse: Urban Sentiment & Mobility Dashboard"
2. **Add subtitle**: "Chicago Transit Sentiment Analysis"
3. **Format colors**: Use consistent color scheme
4. **Test interactivity**: Ensure all filters work correctly
5. **Save**: Save as `.twbx` (packaged workbook)

## Power BI Dashboard Instructions

### Step 1: Import Data

1. Open Power BI Desktop
2. Click "Get Data" → "Text/CSV" or "Excel"
3. Navigate to `data/exports/combined_data_for_tableau.csv` (or .xlsx)
4. Click "Load"

### Step 2: Create Time Series Chart

1. **Insert Line Chart**:
   - Visualizations → Line chart
   - Axis: `date`
   - Values: `avg_polarity` and `total_cta_rides` (add both)
   - Format: Adjust colors and scales

2. **Title**: "Daily Sentiment vs CTA Ridership"

### Step 3: Create Map Visualization

1. **Import 311 data** (if available):
   - Get Data → CSV → `data/cleaned/311_data.csv`
   - Filter for valid coordinates

2. **Insert Map**:
   - Visualizations → Map
   - Location: Use `latitude` and `longitude` fields
   - Size: `total_311_complaints`
   - Color: `service_request_type`

3. **Title**: "311 Complaint Locations"

### Step 4: Create Correlation Matrix

1. **Insert Matrix**:
   - Visualizations → Matrix
   - Rows: Key metrics
   - Values: Use DAX formula for correlation:
     ```DAX
     Correlation = CORREL(Table[avg_polarity], Table[total_cta_rides])
     ```

2. **Format as heatmap**:
   - Conditional formatting → Color scale

### Step 5: Create Sentiment Distribution

1. **Insert Bar Chart**:
   - Visualizations → Bar chart
   - Axis: `sentiment_category`
   - Values: `total_tweets`
   - Color: `sentiment_category`

### Step 6: Add Filters

1. **Date Slicer**:
   - Insert → Slicer
   - Field: `date`
   - Type: Between

2. **Complaint Type Slicer** (if applicable):
   - Insert → Slicer
   - Field: `service_request_type`

### Step 7: Arrange Dashboard

1. **Arrange visuals** on canvas
2. **Sync slicers** to apply to all visuals
3. **Add title**: Text box with "CityPulse Dashboard"
4. **Format**: Consistent theme and colors

### Step 8: Publish

1. **Save**: Save as `.pbix` file
2. **Publish** (optional): Publish to Power BI Service for sharing

## Required Dashboard Features (Per Project Spec)

Based on the project requirements, ensure your dashboard includes:

✅ **Time Series Overview**
- Sentiment trends vs daily ridership
- Daily complaint trends

✅ **Interactive Filters**
- Date range filter
- Complaint type filter (if detail data available)
- Neighborhood filter (if detail data available)

✅ **Map Layers**
- Complaint locations (geospatial)
- Sentiment patterns by location (if available)

✅ **Top Hashtags**
- Most common hashtags from tweets
- Frequency visualization

✅ **Tooltips for Hover Insights**
- Key metrics on hover
- Contextual information

✅ **Correlation Visualizations**
- Sentiment vs ridership correlation
- Complaints vs negativity correlation

## Alternative: Using Dash Dashboard as Reference

If you don't have access to Tableau or Power BI, you can:

1. **Use the existing Dash dashboard** as a reference:
   ```bash
   python src/visualization/dashboard.py
   ```
   Access at: http://127.0.0.1:8050

2. **Screenshot the Dash dashboard** for documentation

3. **Note in documentation** that Dash was used as an alternative visualization tool

## Data Field Descriptions

For reference when building visualizations:

| Field | Type | Description |
|-------|------|-------------|
| `date` | Date | Date of the record |
| `avg_polarity` | Float | Average sentiment (-1 to 1) |
| `sentiment_category` | String | Negative/Neutral/Positive |
| `total_tweets` | Integer | Total tweets on date |
| `total_cta_rides` | Integer | Total CTA ridership |
| `total_311_complaints` | Integer | Total 311 complaints |
| `positive_ratio` | Float | Ratio of positive tweets |
| `negative_ratio` | Float | Ratio of negative tweets |
| `complaints_per_1000_rides` | Float | Complaint rate metric |

## Troubleshooting

**Issue**: Map not showing
- **Solution**: Ensure latitude/longitude fields are recognized as geographic data
- In Tableau: Right-click field → "Geographic Role" → "Latitude/Longitude"
- In Power BI: Ensure fields are numeric, not text

**Issue**: Correlations not calculating
- **Solution**: Use built-in correlation functions (CORR in Tableau, CORREL in Power BI DAX)

**Issue**: Date filter not working
- **Solution**: Ensure date field is recognized as date type, not text

## Next Steps

After creating the dashboard:

1. **Test all filters and interactions**
2. **Verify data accuracy**
3. **Add annotations for key insights**
4. **Export/save the dashboard**
5. **Document any custom calculations or formulas used**

---

*This guide supports the CityPulse project requirement for a Tableau or Power BI dashboard as specified in the project documentation.*

