#!/usr/bin/env python3
"""
Climate Data Visualization
-------------------------
This script creates visualizations of climate data analysis results.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
RESULTS_DIR = 'results'
PLOTS_DIR = 'plots'

# Ensure directories exist
os.makedirs(PLOTS_DIR, exist_ok=True)

# Set plot style
plt.style.use('ggplot')
sns.set(style="whitegrid")

# Custom color maps
temperature_cmap = LinearSegmentedColormap.from_list(
    'temperature',
    ['#2e4787', '#599eb5', '#c6d5d9', '#f6e7d2', '#faad60', '#d64b40', '#9e0142']
)

def load_results():
    """
    Load analysis results from CSV files.
    """
    logger.info("Loading analysis results...")
    
    # Check if results files exist
    required_files = [
        'annual_global_avg.csv',
        'annual_regional_avg.csv',
        'seasonal_avg.csv',
        'decadal_avg.csv',
        'extreme_counts.csv',
        'processed_data.csv'
    ]
    
    results = {}
    for file in required_files:
        file_path = os.path.join(RESULTS_DIR, file)
        if os.path.exists(file_path):
            results[file.split('.')[0]] = pd.read_csv(file_path)
        else:
            logger.warning(f"Missing result file: {file}")
    
    if not results:
        logger.error("No result files found. Run climate_analysis.py first.")
        raise FileNotFoundError("No result files found in the 'results' directory.")
    
    return results

def plot_global_temperature_trend(results):
    """
    Plot global temperature trend over time.
    """
    logger.info("Creating global temperature trend plot...")
    
    annual_global_avg = results['annual_global_avg']
    
    plt.figure(figsize=(12, 6))
    
    # Plot average temperature
    ax1 = plt.gca()
    line1 = ax1.plot(annual_global_avg['year'], annual_global_avg['temperature_c'], 
              marker='o', markersize=4, linewidth=2, label='Annual Average Temperature')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Temperature (°C)')
    
    # Add temperature anomaly on second y-axis
    ax2 = ax1.twinx()
    line2 = ax2.plot(annual_global_avg['year'], annual_global_avg['temp_anomaly'], 
              'r-', linewidth=2, label='Temperature Anomaly')
    ax2.set_ylabel('Temperature Anomaly (°C)')
    
    # Add trend line
    z = np.polyfit(annual_global_avg['year'], annual_global_avg['temperature_c'], 1)
    p = np.poly1d(z)
    line3 = ax1.plot(annual_global_avg['year'], p(annual_global_avg['year']), 
              'k--', linewidth=1.5, label=f'Trend: {z[0]:.4f}°C/year')
    
    # Combine legends
    lines = line1 + line2 + line3
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')
    
    # Set title and grid
    plt.title('Global Average Temperature Trend (1960-2020)')
    ax1.grid(True, alpha=0.3)
    
    # Add annotation about warming rate
    warming_rate = z[0] * 100  # Convert to °C per century
    plt.annotate(f'Warming rate: {warming_rate:.2f}°C per century', 
                 xy=(0.02, 0.05), xycoords='axes fraction', fontsize=10, 
                 bbox=dict(boxstyle="round,pad=0.3", alpha=0.2))
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'global_temperature_trend.png'), dpi=300)
    plt.close()

def plot_regional_temperature_trends(results):
    """
    Plot temperature trends by region.
    """
    logger.info("Creating regional temperature trend plot...")
    
    annual_regional_avg = results['annual_regional_avg']
    
    # Create a plot for each region
    regions = annual_regional_avg['region'].unique()
    
    plt.figure(figsize=(14, 8))
    
    for i, region in enumerate(regions):
        region_data = annual_regional_avg[annual_regional_avg['region'] == region]
        
        # Skip if no data for this region
        if len(region_data) == 0:
            continue
            
        plt.plot(region_data['year'], region_data['temp_anomaly'], 
                 label=region, linewidth=2, marker='o', markersize=3)
    
    plt.xlabel('Year')
    plt.ylabel('Temperature Anomaly (°C)')
    plt.title('Temperature Anomalies by Region (1960-2020)')
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'regional_temperature_trends.png'), dpi=300)
    plt.close()
    
    # Create a heatmap of temperature anomalies by region and year
    pivot_data = annual_regional_avg.pivot(index='region', columns='year', values='temp_anomaly')
    
    plt.figure(figsize=(18, 8))
    sns.heatmap(pivot_data, cmap=temperature_cmap, center=0, 
                linewidths=0, cbar_kws={'label': 'Temperature Anomaly (°C)'})
    plt.title('Temperature Anomalies by Region and Year')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'regional_heatmap.png'), dpi=300)
    plt.close()

def plot_seasonal_trends(results):
    """
    Plot seasonal temperature trends.
    """
    logger.info("Creating seasonal temperature trend plot...")
    
    seasonal_avg = results['seasonal_avg']
    
    # Create pivot table for seasons across years
    pivot_data = seasonal_avg.pivot(index='year', columns='season', values='temperature_c')
    
    # Calculate rolling average for smoother trends
    rolling_data = pivot_data.rolling(window=5, center=True).mean()
    
    # Plot seasonal temperatures
    plt.figure(figsize=(12, 6))
    
    for season in pivot_data.columns:
        plt.plot(pivot_data.index, rolling_data[season], 
                 label=season, linewidth=2.5)
        plt.plot(pivot_data.index, pivot_data[season], 
                 alpha=0.2, linewidth=1)
    
    plt.xlabel('Year')
    plt.ylabel('Temperature (°C)')
    plt.title('Global Seasonal Temperature Trends (1960-2020)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'seasonal_trends.png'), dpi=300)
    plt.close()
    
    # Plot seasonal variability
    plt.figure(figsize=(12, 6))
    
    # Calculate temperature range between seasons for each year
    yearly_range = pivot_data.max(axis=1) - pivot_data.min(axis=1)
    
    # Plot the range
    plt.plot(pivot_data.index, yearly_range, 'b-', linewidth=2)
    
    # Add trend line
    z = np.polyfit(pivot_data.index, yearly_range, 1)
    p = np.poly1d(z)
    plt.plot(pivot_data.index, p(pivot_data.index), 'r--', linewidth=1.5, 
             label=f'Trend: {z[0]:.4f}°C/year')
    
    plt.xlabel('Year')
    plt.ylabel('Temperature Range (°C)')
    plt.title('Seasonal Temperature Variability (1960-2020)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'seasonal_variability.png'), dpi=300)
    plt.close()

def plot_decadal_changes(results):
    """
    Plot temperature changes by decade.
    """
    logger.info("Creating decadal temperature change plot...")
    
    decadal_avg = results['decadal_avg']
    
    # Create a pivot table of decade vs region
    pivot_data = decadal_avg.pivot(index='decade', columns='region', values='temperature_c')
    
    # Plot decadal average temperatures by region
    plt.figure(figsize=(14, 8))
    
    # Plot each region
    for region in pivot_data.columns:
        plt.plot(pivot_data.index, pivot_data[region], 'o-', 
                 linewidth=2, label=region, markersize=8)
    
    plt.xlabel('Decade')
    plt.ylabel('Average Temperature (°C)')
    plt.title('Decadal Average Temperatures by Region')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(pivot_data.index)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'decadal_changes.png'), dpi=300)
    plt.close()
    
    # Create a heatmap of temperature changes between decades
    temperature_changes = pivot_data.diff()
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(temperature_changes, cmap=temperature_cmap, center=0,
                annot=True, fmt='.2f', linewidths=0.5, 
                cbar_kws={'label': 'Temperature Change (°C)'})
    plt.title('Temperature Change Between Decades by Region')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'decadal_changes_heatmap.png'), dpi=300)
    plt.close()

def plot_extreme_temperatures(results):
    """
    Plot extreme temperature events.
    """
    logger.info("Creating extreme temperature events plot...")
    
    extreme_counts = results['extreme_counts']
    
    # Plot extreme hot events by decade and region
    plt.figure(figsize=(14, 8))
    
    # Create pivot tables
    hot_pivot = extreme_counts.pivot(index='decade', columns='region', values='extreme_hot')
    cold_pivot = extreme_counts.pivot(index='decade', columns='region', values='extreme_cold')
    
    # Plot extreme hot events
    plt.figure(figsize=(14, 8))
    ax = sns.heatmap(hot_pivot, annot=True, fmt='g', cmap='YlOrRd',
                     linewidths=0.5, cbar_kws={'label': 'Number of Extreme Hot Events'})
    plt.title('Extreme Hot Temperature Events by Decade and Region')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'extreme_hot_events.png'), dpi=300)
    plt.close()
    
    # Plot extreme cold events
    plt.figure(figsize=(14, 8))
    ax = sns.heatmap(cold_pivot, annot=True, fmt='g', cmap='Blues_r',
                     linewidths=0.5, cbar_kws={'label': 'Number of Extreme Cold Events'})
    plt.title('Extreme Cold Temperature Events by Decade and Region')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'extreme_cold_events.png'), dpi=300)
    plt.close()
    
    # Plot ratio of hot to cold events
    ratio_pivot = hot_pivot / cold_pivot
    
    plt.figure(figsize=(14, 8))
    sns.heatmap(ratio_pivot, annot=True, fmt='.2f', cmap='coolwarm',
                linewidths=0.5, center=1.0, cbar_kws={'label': 'Ratio of Hot to Cold Events'})
    plt.title('Ratio of Extreme Hot to Cold Events by Decade and Region')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'extreme_ratio.png'), dpi=300)
    plt.close()

def plot_global_map(results):
    """
    Create a global map visualization of temperature trends.
    """
    logger.info("Creating global map visualization...")
    
    # For a simplified version, we'll create a scatter plot on a world map
    processed_data = results['processed_data']
    
    # Filter to most recent decade
    recent_data = processed_data[processed_data['year'] >= 2010]
    
    # Calculate average temperature for each station in recent years
    station_avg = recent_data.groupby(['station_id', 'latitude', 'longitude'])['temperature_c'].mean().reset_index()
    
    # Create world map plot
    plt.figure(figsize=(18, 9))
    
    # Create a scatter plot on a world map background
    plt.scatter(station_avg['longitude'], station_avg['latitude'], 
                c=station_avg['temperature_c'], cmap=temperature_cmap,
                s=50, alpha=0.7, edgecolors='k', linewidths=0.5)
    
    # Add color bar
    cbar = plt.colorbar()
    cbar.set_label('Average Temperature (°C)')
    
    # Set plot limits and labels
    plt.xlim(-180, 180)
    plt.ylim(-90, 90)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Global Average Temperatures (2010-2020)')
    plt.grid(True, alpha=0.3)
    
    # Add simple continent outlines
    # Note: In a real-world scenario, you would use cartopy or basemap libraries
    # for proper map visualization. This is a simplified version.
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'global_map.png'), dpi=300)
    plt.close()

def create_visualization_dashboard():
    """
    Create an HTML dashboard with all the visualizations.
    """
    logger.info("Creating visualization dashboard...")
    
    # Get all the plot files
    plot_files = [f for f in os.listdir(PLOTS_DIR) if f.endswith('.png')]
    
    # Create HTML content
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Climate Data Analysis Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
            h1 { color: #333; text-align: center; }
            .plot-container { background-color: white; margin: 20px 0; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .plot-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
            .plot-image { width: 100%; max-width: 100%; height: auto; }
            .footer { text-align: center; margin-top: 30px; font-size: 12px; color: #777; }
        </style>
    </head>
    <body>
        <h1>Climate Data Analysis Dashboard</h1>
    """
    
    # Add each plot to the dashboard
    for plot_file in plot_files:
        plot_name = plot_file.replace('.png', '').replace('_', ' ').title()
        html_content += f"""
        <div class="plot-container">
            <div class="plot-title">{plot_name}</div>
            <img class="plot-image" src="{os.path.join('..', PLOTS_DIR, plot_file)}" alt="{plot_name}">
        </div>
        """
    
    # Add footer and close HTML
    html_content += """
        <div class="footer">
            Climate Data Analysis Project - Created using GHCN-M dataset
        </div>
    </body>
    </html>
    """
    
    # Save the HTML file
    with open(os.path.join(PLOTS_DIR, 'dashboard.html'), 'w') as f:
        f.write(html_content)
    
    logger.info(f"Dashboard created: {os.path.join(PLOTS_DIR, 'dashboard.html')}")

def run_visualization():
    """
    Run all visualization functions.
    """
    logger.info("Starting data visualization...")
    
    # Load analysis results
    results = load_results()
    
    # Create various plots
    plot_global_temperature_trend(results)
    plot_regional_temperature_trends(results)
    plot_seasonal_trends(results)
    plot_decadal_changes(results)
    plot_extreme_temperatures(results)
    plot_global_map(results)
    
    # Create dashboard
    create_visualization_dashboard()
    
    logger.info("All visualizations created successfully.")
    logger.info(f"View the dashboard at: {os.path.join(PLOTS_DIR, 'dashboard.html')}")

if __name__ == "__main__":
    run_visualization()
