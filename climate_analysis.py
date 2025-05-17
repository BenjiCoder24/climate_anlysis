#!/usr/bin/env python3
"""
Climate Data Analysis
--------------------
This script analyzes temperature data from the Global Historical Climatology Network
Monthly (GHCN-M) dataset to identify temperature trends and patterns.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import requests
import io
import zipfile
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = 'data'
RESULTS_DIR = 'results'
SAMPLE_SIZE = 100  # Number of stations to analyze
START_YEAR = 1960  # Start year for analysis
END_YEAR = 2020    # End year for analysis

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def download_data():
    """
    Download a subset of GHCN-M temperature data for analysis.
    For demonstration, using a sample from NOAA's FTP site.
    """
    logger.info("Downloading temperature data...")
    
    # For this demonstration, we'll download a limited dataset from GHCN-M
    # The URL below is for the GHCN-M v4 dataset (modify as needed)
    data_url = "https://www.ncei.noaa.gov/pub/data/ghcn/v4/ghcnm.tavg.latest.qcf.tar.gz"
    
    try:
        # For the homework purposes, we'll create a sample dataset if download fails
        try:
            response = requests.get(data_url, timeout=30)
            if response.status_code == 200:
                # Save the raw data
                with open(os.path.join(DATA_DIR, 'ghcnm_data.tar.gz'), 'wb') as f:
                    f.write(response.content)
                logger.info("Data downloaded successfully")
            else:
                raise Exception(f"Failed to download data: {response.status_code}")
        except Exception as e:
            logger.warning(f"Could not download data: {e}")
            logger.info("Creating sample data for demonstration")
            create_sample_data()
            
    except Exception as e:
        logger.error(f"Error downloading data: {e}")
        raise

def create_sample_data():
    """
    Create a sample dataset for demonstration if download fails.
    """
    logger.info("Generating sample temperature data...")
    
    # Create a sample dataframe with random temperature data
    np.random.seed(42)  # For reproducibility
    
    # Generate 100 stations with monthly data from 1960 to 2020
    stations = [f'STATION{i:03d}' for i in range(SAMPLE_SIZE)]
    years = range(START_YEAR, END_YEAR + 1)
    months = range(1, 13)
    
    # Generate latitude and longitude for stations
    station_metadata = pd.DataFrame({
        'station_id': stations,
        'latitude': np.random.uniform(-60, 80, SAMPLE_SIZE),
        'longitude': np.random.uniform(-180, 180, SAMPLE_SIZE),
        'elevation': np.random.uniform(0, 2000, SAMPLE_SIZE),
        'name': [f'Sample Station {i}' for i in range(SAMPLE_SIZE)],
        'country': np.random.choice(['USA', 'CAN', 'MEX', 'BRA', 'ARG', 'GBR', 'FRA', 'DEU', 'RUS', 'CHN', 'IND', 'AUS'], SAMPLE_SIZE)
    })
    
    # Create a template for temperature data
    rows = []
    for station in stations:
        # Get station metadata
        station_data = station_metadata[station_metadata['station_id'] == station].iloc[0]
        lat = station_data['latitude']
        
        # Generate temperature data with seasonality based on hemisphere
        for year in years:
            for month in months:
                # Base temperature varies by latitude (colder near poles)
                base_temp = 25 - 0.3 * abs(lat)
                
                # Add seasonal variation (reversed for southern hemisphere)
                seasonal_factor = 15 * np.sin(2 * np.pi * (month - (1 if lat >= 0 else 7)) / 12)
                
                # Add yearly warming trend (about 1°C per century)
                trend = 0.01 * (year - START_YEAR)
                
                # Add some random variation
                noise = np.random.normal(0, 1.5)
                
                # Calculate temperature in tenths of degrees C (as in GHCN format)
                temperature = base_temp + seasonal_factor + trend + noise
                
                # Round to nearest tenth and convert to integer in tenths of °C
                temperature_int = int(round(temperature * 10))
                
                rows.append({
                    'station_id': station,
                    'year': year,
                    'month': month,
                    'temperature': temperature_int  # Temperature in tenths of °C
                })
    
    # Create the dataframe
    temp_df = pd.DataFrame(rows)
    
    # Save the data
    station_metadata.to_csv(os.path.join(DATA_DIR, 'station_metadata.csv'), index=False)
    temp_df.to_csv(os.path.join(DATA_DIR, 'temperature_data.csv'), index=False)
    
    logger.info(f"Sample data created with {len(stations)} stations from {START_YEAR} to {END_YEAR}")
    return temp_df, station_metadata

def load_data():
    """
    Load temperature data from files.
    """
    logger.info("Loading temperature data...")
    
    # Check if data files exist, if not create sample data
    if not (os.path.exists(os.path.join(DATA_DIR, 'temperature_data.csv')) and 
            os.path.exists(os.path.join(DATA_DIR, 'station_metadata.csv'))):
        temp_df, station_metadata = create_sample_data()
    else:
        # Load the actual data
        temp_df = pd.read_csv(os.path.join(DATA_DIR, 'temperature_data.csv'))
        station_metadata = pd.read_csv(os.path.join(DATA_DIR, 'station_metadata.csv'))
    
    logger.info(f"Loaded data with {len(temp_df)} temperature records from {len(temp_df['station_id'].unique())} stations")
    return temp_df, station_metadata

def preprocess_data(temp_df, station_metadata):
    """
    Preprocess and clean the temperature data.
    """
    logger.info("Preprocessing temperature data...")
    
    # Convert temperature from tenths of degrees C to degrees C
    temp_df['temperature_c'] = temp_df['temperature'] / 10.0
    
    # Create a datetime column for easier time-based analysis
    temp_df['date'] = pd.to_datetime(temp_df[['year', 'month']].assign(day=1))
    
    # Add season column
    # Define seasons: meteorological seasons (Dec-Feb: Winter, Mar-May: Spring, etc.)
    temp_df['season'] = pd.cut(
        temp_df['month'],
        bins=[0, 3, 6, 9, 13],
        labels=['Winter', 'Spring', 'Summer', 'Fall'],
        include_lowest=True
    )
    # Adjust for December being part of Winter
    temp_df.loc[temp_df['month'] == 12, 'season'] = 'Winter'
    
    # Join with station metadata to include geographical information
    data = pd.merge(temp_df, station_metadata, on='station_id')
    
    # Define regions based on latitude
    data['region'] = pd.cut(
        data['latitude'],
        bins=[-90, -60, -30, 0, 30, 60, 90],
        labels=['Antarctica', 'Southern', 'Tropical S', 'Tropical N', 'Northern', 'Arctic']
    )
    
    logger.info("Data preprocessing complete")
    return data

def analyze_temperature_trends(data):
    """
    Analyze global and regional temperature trends over time.
    """
    logger.info("Analyzing temperature trends...")
    
    # Global annual average temperature
    annual_global_avg = data.groupby('year')['temperature_c'].mean().reset_index()
    annual_global_avg['temp_anomaly'] = annual_global_avg['temperature_c'] - annual_global_avg['temperature_c'].mean()
    
    # Regional annual average temperature
    annual_regional_avg = data.groupby(['year', 'region'])['temperature_c'].mean().reset_index()
    
    # Compute regional temperature anomalies (relative to 1961-1990 baseline)
    baseline_period = (annual_regional_avg['year'] >= 1961) & (annual_regional_avg['year'] <= 1990)
    regional_baselines = annual_regional_avg[baseline_period].groupby('region')['temperature_c'].mean().reset_index()
    regional_baselines.rename(columns={'temperature_c': 'baseline_temp'}, inplace=True)
    
    annual_regional_avg = pd.merge(annual_regional_avg, regional_baselines, on='region')
    annual_regional_avg['temp_anomaly'] = annual_regional_avg['temperature_c'] - annual_regional_avg['baseline_temp']
    
    # Seasonal analysis
    seasonal_avg = data.groupby(['year', 'season'])['temperature_c'].mean().reset_index()
    
    # Decadal analysis
    data['decade'] = (data['year'] // 10) * 10
    decadal_avg = data.groupby(['decade', 'region'])['temperature_c'].mean().reset_index()
    
    # Save results
    annual_global_avg.to_csv(os.path.join(RESULTS_DIR, 'annual_global_avg.csv'), index=False)
    annual_regional_avg.to_csv(os.path.join(RESULTS_DIR, 'annual_regional_avg.csv'), index=False)
    seasonal_avg.to_csv(os.path.join(RESULTS_DIR, 'seasonal_avg.csv'), index=False)
    decadal_avg.to_csv(os.path.join(RESULTS_DIR, 'decadal_avg.csv'), index=False)
    
    logger.info("Temperature trend analysis complete")
    return {
        'annual_global_avg': annual_global_avg,
        'annual_regional_avg': annual_regional_avg,
        'seasonal_avg': seasonal_avg,
        'decadal_avg': decadal_avg
    }

def analyze_extreme_temperatures(data):
    """
    Analyze extreme temperature events.
    """
    logger.info("Analyzing extreme temperatures...")
    
    # Identify extreme hot and cold temperatures (beyond 2 standard deviations)
    station_stats = data.groupby('station_id')['temperature_c'].agg(['mean', 'std']).reset_index()
    data = pd.merge(data, station_stats, on='station_id')
    
    data['extreme_hot'] = data['temperature_c'] > (data['mean'] + 2 * data['std'])
    data['extreme_cold'] = data['temperature_c'] < (data['mean'] - 2 * data['std'])
    
    # Count extreme events by decade and region
    data['decade'] = (data['year'] // 10) * 10
    extreme_counts = data.groupby(['decade', 'region'])[['extreme_hot', 'extreme_cold']].sum().reset_index()
    
    # Save results
    extreme_counts.to_csv(os.path.join(RESULTS_DIR, 'extreme_counts.csv'), index=False)
    
    logger.info("Extreme temperature analysis complete")
    return extreme_counts

def run_analysis():
    """
    Run the full analysis pipeline.
    """
    logger.info("Starting climate data analysis...")
    
    # Get the data
    try:
        download_data()
    except Exception as e:
        logger.warning(f"Data download failed: {e}. Using sample data.")
    
    # Load the data
    temp_df, station_metadata = load_data()
    
    # Preprocess the data
    data = preprocess_data(temp_df, station_metadata)
    
    # Analyze temperature trends
    trend_results = analyze_temperature_trends(data)
    
    # Analyze extreme temperatures
    extreme_results = analyze_extreme_temperatures(data)
    
    # Save the processed data for visualization
    data.to_csv(os.path.join(RESULTS_DIR, 'processed_data.csv'), index=False)
    
    logger.info("Analysis complete. Results saved to the 'results' directory.")
    
    return {
        'data': data,
        'trend_results': trend_results,
        'extreme_results': extreme_results
    }

if __name__ == "__main__":
    run_analysis()
