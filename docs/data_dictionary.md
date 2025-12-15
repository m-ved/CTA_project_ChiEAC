# Data Dictionary

This document describes all variables in the cleaned datasets used in the CityPulse project.

## 1. Chicago 311 Service Requests (`311_data.csv`)

### Description
Transit-related service requests and complaints submitted to the City of Chicago 311 system.

### Variables

| Variable Name | Type | Description | Example |
|--------------|------|-------------|---------|
| `service_request_number` | String | Unique identifier for the service request | "12-00001234" |
| `created_date` | DateTime | Date and time when the request was created | "2024-01-15 10:30:00" |
| `updated_date` | DateTime | Date and time when the request was last updated | "2024-01-15 14:20:00" |
| `closed_date` | DateTime | Date and time when the request was closed (if applicable) | "2024-01-16 09:00:00" |
| `status` | String | Current status of the request | "Open", "Closed", "Completed" |
| `service_request_type` | String | Type of service requested | "Street Light Out", "Pothole in Street" |
| `description` | String | Detailed description of the issue | "Street light not working on Main St" |
| `street_address` | String | Street address where the issue is located | "123 Main St" |
| `zip_code` | String | ZIP code of the location | "60601" |
| `ward` | Integer | City ward number | 42 |
| `community_area` | String | Community area name | "Loop" |
| `latitude` | Float | Latitude coordinate (if available) | 41.8781 |
| `longitude` | Float | Longitude coordinate (if available) | -87.6298 |

### Notes
- Some fields may contain missing values (NaN)
- Date fields are normalized to datetime format
- Location data may not be available for all records

---

## 2. CTA Ridership Data (`cta_ridership.csv`)

### Description
Daily ridership data for Chicago Transit Authority (CTA) bus and train services.

### Variables

| Variable Name | Type | Description | Example |
|--------------|------|-------------|---------|
| `date` | DateTime | Date of the ridership record | "2024-01-15" |
| `mode` | String | Transportation mode | "bus" or "train" |
| `station_id` | String | Station identifier (for trains) | "40010" |
| `station_name` | String | Name of the station (for trains) | "Howard" |
| `route` | String | Route identifier (for buses) | "22" |
| `route_name` | String | Name of the route (for buses) | "Clark" |
| `rides` | Integer | Number of rides/boardings on this date | 1250 |
| `boardings` | Integer | Number of boardings (if available) | 1250 |
| `alightings` | Integer | Number of alightings (if available) | 1200 |
| `daytype` | String | Type of day | "W" (Weekday), "A" (Saturday), "U" (Sunday/Holiday) |

### Notes
- Data is aggregated at the daily level
- Some routes/stations may have missing data for certain dates
- Numeric fields default to 0 if missing

---

## 3. Twitter/X Data (`tweets.csv`)

### Description
Tweets collected from Chicago-related hashtags using snscrape.

### Variables

| Variable Name | Type | Description | Example |
|--------------|------|-------------|---------|
| `tweet_id` | String | Unique identifier for the tweet | "1234567890123456789" |
| `url` | String | URL of the tweet | "https://twitter.com/user/status/1234567890" |
| `date` | DateTime | Date and time when the tweet was posted | "2024-01-15 08:30:00" |
| `content` | String | Full text content of the tweet | "CTA delays are terrible today #ChicagoCommute" |
| `user` | String | Username of the tweet author | "chicago_user" |
| `retweet_count` | Integer | Number of retweets | 15 |
| `like_count` | Integer | Number of likes | 42 |
| `reply_count` | Integer | Number of replies | 3 |
| `quote_count` | Integer | Number of quote tweets | 2 |
| `hashtags` | String | Comma-separated list of hashtags in the tweet | "#ChicagoCommute, #CTA" |
| `coordinates` | String | Geographic coordinates (if available) | "41.8781, -87.6298" |
| `place` | String | Place name (if available) | "Chicago, IL" |

### Notes
- Tweet content is cleaned (whitespace normalized)
- Engagement metrics default to 0 if missing
- Geographic data may not be available for all tweets
- Date field is normalized to datetime format

---

## 4. Combined Dataset (`combined_data.csv`)

### Description
Merged dataset combining sentiment analysis results with CTA ridership and 311 complaint data, aggregated by date.

### Variables

| Variable Name | Type | Description | Example |
|--------------|------|-------------|---------|
| `date` | DateTime | Date of the record | "2024-01-15" |
| `avg_sentiment_polarity` | Float | Average sentiment polarity score (-1 to 1) | 0.15 |
| `avg_sentiment_subjectivity` | Float | Average sentiment subjectivity score (0 to 1) | 0.45 |
| `positive_tweets` | Integer | Number of positive tweets on this date | 120 |
| `neutral_tweets` | Integer | Number of neutral tweets on this date | 80 |
| `negative_tweets` | Integer | Number of negative tweets on this date | 50 |
| `total_tweets` | Integer | Total number of tweets on this date | 250 |
| `total_cta_rides` | Integer | Total CTA ridership (bus + train) | 500000 |
| `bus_rides` | Integer | Total bus ridership | 300000 |
| `train_rides` | Integer | Total train ridership | 200000 |
| `total_311_complaints` | Integer | Total number of 311 complaints on this date | 45 |
| `transit_related_complaints` | Integer | Number of transit-related complaints | 30 |

### Notes
- All metrics are aggregated at the daily level
- Missing dates may occur if no data is available
- Sentiment scores are calculated using VADER or TextBlob

---

## Data Quality Notes

1. **Missing Values**: Some fields may contain missing values. These are handled during the cleaning process.
2. **Date Alignment**: All datasets are normalized to use consistent date formats and timezones.
3. **Duplicates**: Duplicate records are removed during the cleaning process.
4. **Data Gaps**: Some dates may not have data from all sources. This is expected and handled during integration.

---

## Data Sources

- **311 Data**: Chicago Data Portal - 311 Service Requests API
- **CTA Data**: Chicago Data Portal - CTA Ridership Datasets
- **Twitter Data**: Collected via snscrape from public Twitter/X posts

---

*Last Updated: Generated during Week 1 of the CityPulse project*

