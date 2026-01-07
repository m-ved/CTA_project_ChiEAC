"""
Sample Data Generator
Creates realistic sample data for demonstration purposes
Use this if you can't access APIs or want consistent demo data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_sample_cta_data(n_days=30):
    """Generate sample CTA ridership data"""
    logger.info(f"Generating {n_days} days of CTA ridership data")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=n_days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    all_rides = []
    
    for date in dates:
        weekday = date.weekday()
        
        # Higher ridership on weekdays
        if weekday < 5:  # Weekday
            base_ridership = np.random.normal(600000, 50000)
            bus_ratio = 0.6
        else:  # Weekend
            base_ridership = np.random.normal(400000, 40000)
            bus_ratio = 0.55
        
        total_rides = max(int(base_ridership), 100000)  # Minimum 100k
        bus_rides = int(total_rides * bus_ratio)
        train_rides = total_rides - bus_rides
        
        # Create multiple records (different routes/stations)
        for mode in ['bus', 'train']:
            n_routes = 10 if mode == 'bus' else 5
            
            for i in range(n_routes):
                if mode == 'bus':
                    route_id = f"route_{i+1}"
                    route_name = f"Route {i+1}"
                    rides = int(bus_rides / n_routes * np.random.uniform(0.8, 1.2))
                else:
                    route_id = f"station_{i+1}"
                    route_name = f"Station {i+1}"
                    rides = int(train_rides / n_routes * np.random.uniform(0.8, 1.2))
                
                all_rides.append({
                    'date': date,
                    'mode': mode,
                    'route' if mode == 'bus' else 'station_id': route_id,
                    'route_name' if mode == 'bus' else 'station_name': route_name,
                    'rides': max(rides, 100),  # Minimum 100 rides
                    'daytype': 'W' if weekday < 5 else ('A' if weekday == 5 else 'U')
                })
    
    df = pd.DataFrame(all_rides)
    df['date'] = pd.to_datetime(df['date'])
    
    logger.info(f"Generated {len(df)} CTA records")
    
    return df


def generate_sample_311_data(n_days=30, complaints_per_day=50):
    """Generate sample 311 complaint data"""
    logger.info(f"Generating {n_days * complaints_per_day} sample 311 complaints")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=n_days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Comprehensive list of realistic Chicago 311 service request types
    complaint_types = [
        # Transit/Infrastructure Related
        "Street Light Out",
        "Street Light - All/Out",
        "Street Light Out Complaint",
        "Pothole in Street",
        "Pothole Complaint",
        "Sidewalk Issue",
        "Sidewalk Repair",
        "Alley Light Out",
        "Traffic Signal Out",
        "Traffic Signal Out Complaint",
        "Traffic Signal - All/Out",
        "Street Cut Complaint",
        "Street Defect",
        "Abandoned Vehicle",
        "Vehicle on Sidewalk",
        "Street Resurfacing Request",
        
        # General City Services
        "Garbage Cart Request",
        "Tree Debris",
        "Tree Trim Request",
        "Graffiti Removal",
        "Graffiti Removal Request",
        "Rodent Baiting / Rat Complaint",
        "Sanitation Code Violation",
        "Building Violation",
        "Water Leak",
        "Sewer Issue",
        "Sewer Backup",
        "Water Quality Complaint",
        
        # Transit-Specific
        "Bus Stop Request",
        "Transit Signal Issue",
        "CTA Station Issue",
        
        # Additional Common Types
        "Ice and Snow Removal Request",
        "Snow – Uncleared Sidewalk Complaint",
        "311 INFORMATION ONLY CALL",
        "Aircraft Noise Complaint",
        "Coyote Interaction Complaint",
        "Water Lead Test Kit Request"
    ]
    
    # More complaints on weekdays
    all_complaints = []
    complaint_id = 100000
    
    for date in dates:
        weekday = date.weekday()
        
        # Adjust complaints per day based on weekday
        if weekday < 5:  # Weekday
            n_complaints = int(complaints_per_day * np.random.uniform(1.0, 1.3))
        else:  # Weekend
            n_complaints = int(complaints_per_day * np.random.uniform(0.6, 0.9))
        
        for i in range(n_complaints):
            complaint_type = np.random.choice(complaint_types)
            
            # Chicago coordinates within city limits (excluding Lake Michigan)
            # Chicago land area bounds: Lat 41.64-42.02, Lon -87.94 to -87.60
            # Using -87.60 (Lakefront Trail boundary) to include downtown Chicago and east side neighborhoods
            lat = np.random.uniform(41.64, 42.02)
            lon = np.random.uniform(-87.94, -87.60)
            
            complaint = {
                'service_request_number': f"24-{complaint_id:08d}",
                'created_date': date + timedelta(hours=np.random.randint(8, 18),
                                                minutes=np.random.randint(0, 60)),
                'updated_date': date + timedelta(hours=np.random.randint(18, 22),
                                                minutes=np.random.randint(0, 60)),
                'closed_date': date + timedelta(days=np.random.randint(1, 5)) if np.random.random() > 0.3 else None,
                'status': np.random.choice(['Open', 'Closed', 'Completed'], p=[0.2, 0.5, 0.3]),
                'service_request_type': complaint_type,
                'description': f"Sample {complaint_type.lower()} complaint",
                'street_address': f"{np.random.randint(1, 9999)} Sample St",
                'zip_code': f"606{np.random.randint(1, 99):02d}",
                'ward': np.random.randint(1, 51),
                'community_area': f"Area {np.random.randint(1, 78)}",
                'latitude': lat,
                'longitude': lon
            }
            
            all_complaints.append(complaint)
            complaint_id += 1
    
    df = pd.DataFrame(all_complaints)
    df['created_date'] = pd.to_datetime(df['created_date'])
    df['updated_date'] = pd.to_datetime(df['updated_date'])
    df['closed_date'] = pd.to_datetime(df['closed_date'], errors='coerce')
    
    logger.info(f"Generated {len(df)} 311 complaints")
    
    return df


def main():
    """Generate all sample data files"""
    logger.info("="*60)
    logger.info("Generating Sample Data for CityPulse")
    logger.info("="*60)
    
    # Create output directories
    cleaned_dir = PROJECT_ROOT / "data" / "cleaned"
    cleaned_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate CTA data
    logger.info("\n1. Generating sample CTA ridership data...")
    cta_df = generate_sample_cta_data(n_days=30)
    cta_path = cleaned_dir / "cta_ridership.csv"
    cta_df.to_csv(cta_path, index=False)
    logger.info(f"✓ Saved to {cta_path}")
    
    # Generate 311 data
    logger.info("\n2. Generating sample 311 complaint data...")
    complaints_df = generate_sample_311_data(n_days=30, complaints_per_day=50)
    complaints_path = cleaned_dir / "311_data.csv"
    complaints_df.to_csv(complaints_path, index=False)
    logger.info(f"✓ Saved to {complaints_path}")
    
    logger.info("\n" + "="*60)
    logger.info("Sample Data Generation Complete!")
    logger.info("="*60)
    logger.info("\nNext steps:")
    logger.info("1. Run: python src/sentiment/integrate_data.py")
    logger.info("2. Run: python src/visualization/correlation_analysis.py")
    logger.info("3. Launch dashboard: python src/visualization/dashboard.py")
    logger.info("\nOr run everything at once:")
    logger.info("   python run_pipeline.py")


if __name__ == "__main__":
    main()

