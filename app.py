#!/usr/bin/env python3
"""
Climate Data Analysis FastAPI Server
-----------------------------------
This script provides a web server for interactive climate data visualizations.
"""

import os
import json
import pandas as pd
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import uvicorn

# Constants
RESULTS_DIR = 'results'
STATIC_DIR = 'static'
TEMPLATES_DIR = 'templates'

# Create directories if they don't exist
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(TEMPLATES_DIR), exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="Climate Data Analysis Dashboard",
    description="Interactive visualization of climate data analysis results",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

def load_results():
    """
    Load analysis results from CSV files.
    """
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
    
    if not results:
        raise FileNotFoundError("No result files found in the 'results' directory. Run climate_analysis.py first.")
    
    return results

def create_global_temperature_plot(results):
    """
    Create interactive global temperature trend plot.
    """
    annual_global_avg = results['annual_global_avg']
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add temperature line
    fig.add_trace(
        go.Scatter(
            x=annual_global_avg['year'], 
            y=annual_global_avg['temperature_c'],
            mode='lines+markers',
            name='Annual Average Temperature',
            marker=dict(size=6)
        ),
        secondary_y=False,
    )
    
    # Add anomaly line
    fig.add_trace(
        go.Scatter(
            x=annual_global_avg['year'], 
            y=annual_global_avg['temp_anomaly'],
            mode='lines',
            name='Temperature Anomaly',
            line=dict(color='red')
        ),
        secondary_y=True,
    )
    
    # Add trend line
    z = np.polyfit(annual_global_avg['year'], annual_global_avg['temperature_c'], 1)
    p = np.poly1d(z)
    
    fig.add_trace(
        go.Scatter(
            x=annual_global_avg['year'], 
            y=p(annual_global_avg['year']),
            mode='lines',
            name=f'Trend: {z[0]:.4f}°C/year',
            line=dict(color='black', dash='dash')
        ),
        secondary_y=False,
    )
    
    # Customize layout
    fig.update_layout(
        title='Global Average Temperature Trend (1960-2020)',
        xaxis_title='Year',
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)'),
        hovermode='x unified',
        template='plotly_white',
        annotations=[
            dict(
                x=0.02,
                y=0.05,
                xref="paper",
                yref="paper",
                text=f"Warming rate: {z[0] * 100:.2f}°C per century",
                showarrow=False,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="black",
                borderwidth=1,
                borderpad=4
            )
        ]
    )
    
    # Set y-axes titles
    fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False)
    fig.update_yaxes(title_text="Temperature Anomaly (°C)", secondary_y=True)
    
    return fig

def create_regional_temperature_plot(results):
    """
    Create interactive regional temperature trends plot.
    """
    annual_regional_avg = results['annual_regional_avg']
    
    fig = go.Figure()
    
    # Plot each region
    for region in sorted(annual_regional_avg['region'].unique()):
        region_data = annual_regional_avg[annual_regional_avg['region'] == region]
        
        # Skip if no data for this region
        if len(region_data) == 0:
            continue
            
        fig.add_trace(
            go.Scatter(
                x=region_data['year'], 
                y=region_data['temp_anomaly'],
                mode='lines+markers',
                name=region,
                marker=dict(size=3)
            )
        )
    
    # Add horizontal line at zero
    fig.add_shape(
        type="line",
        x0=min(annual_regional_avg['year']),
        y0=0,
        x1=max(annual_regional_avg['year']),
        y1=0,
        line=dict(color="black", width=1, dash="dash")
    )
    
    # Customize layout
    fig.update_layout(
        title='Temperature Anomalies by Region (1960-2020)',
        xaxis_title='Year',
        yaxis_title='Temperature Anomaly (°C)',
        legend=dict(x=0.01, y=0.99),
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_regional_heatmap(results):
    """
    Create interactive regional temperature heatmap.
    """
    annual_regional_avg = results['annual_regional_avg']
    
    # Create pivot table
    pivot_data = annual_regional_avg.pivot(index='region', columns='year', values='temp_anomaly')
    
    # Get years and regions for plotting
    years = sorted(annual_regional_avg['year'].unique())
    regions = sorted(annual_regional_avg['region'].unique())
    
    # Create z values
    z_values = []
    for region in regions:
        if region in pivot_data.index:
            z_values.append(pivot_data.loc[region].values)
        else:
            z_values.append([None] * len(years))
    
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=years,
        y=regions,
        colorscale='RdBu_r',
        zmid=0,
        colorbar=dict(title='Temperature Anomaly (°C)'),
    ))
    
    fig.update_layout(
        title='Temperature Anomalies by Region and Year',
        xaxis_title='Year',
        yaxis_title='Region',
        template='plotly_white'
    )
    
    return fig

def create_seasonal_trends_plot(results):
    """
    Create interactive seasonal temperature trends plot.
    """
    seasonal_avg = results['seasonal_avg']
    
    # Create pivot table
    pivot_data = seasonal_avg.pivot(index='year', columns='season', values='temperature_c')
    
    # Calculate rolling average
    rolling_data = pivot_data.rolling(window=5, center=True).mean()
    
    fig = go.Figure()
    
    # Seasons order
    seasons = ['Winter', 'Spring', 'Summer', 'Fall']
    colors = ['blue', 'green', 'red', 'orange']
    
    # Add each season
    for i, season in enumerate([s for s in seasons if s in pivot_data.columns]):
        color = colors[i % len(colors)]
        
        # Add smooth line
        fig.add_trace(
            go.Scatter(
                x=pivot_data.index,
                y=rolling_data[season],
                mode='lines',
                name=f'{season} (5-yr average)',
                line=dict(width=3, color=color)
            )
        )
        
        # Add raw data with low opacity
        fig.add_trace(
            go.Scatter(
                x=pivot_data.index,
                y=pivot_data[season],
                mode='lines',
                name=f'{season} (raw)',
                line=dict(width=1, color=color),
                opacity=0.3,
                showlegend=False
            )
        )
    
    # Customize layout
    fig.update_layout(
        title='Global Seasonal Temperature Trends (1960-2020)',
        xaxis_title='Year',
        yaxis_title='Temperature (°C)',
        legend=dict(x=0.01, y=0.99),
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_seasonal_variability_plot(results):
    """
    Create interactive seasonal variability plot.
    """
    seasonal_avg = results['seasonal_avg']
    
    # Create pivot table
    pivot_data = seasonal_avg.pivot(index='year', columns='season', values='temperature_c')
    
    # Calculate temperature range between seasons for each year
    yearly_range = pivot_data.max(axis=1) - pivot_data.min(axis=1)
    
    fig = go.Figure()
    
    # Add range line
    fig.add_trace(
        go.Scatter(
            x=pivot_data.index,
            y=yearly_range,
            mode='lines',
            name='Seasonal Range',
            line=dict(color='blue', width=2)
        )
    )
    
    # Add trend line
    z = np.polyfit(pivot_data.index, yearly_range, 1)
    p = np.poly1d(z)
    
    fig.add_trace(
        go.Scatter(
            x=pivot_data.index,
            y=p(pivot_data.index),
            mode='lines',
            name=f'Trend: {z[0]:.4f}°C/year',
            line=dict(color='red', dash='dash')
        )
    )
    
    # Customize layout
    fig.update_layout(
        title='Seasonal Temperature Variability (1960-2020)',
        xaxis_title='Year',
        yaxis_title='Temperature Range (°C)',
        legend=dict(x=0.01, y=0.99),
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_decadal_changes_plot(results):
    """
    Create interactive decadal temperature changes plot.
    """
    decadal_avg = results['decadal_avg']
    
    # Create pivot table
    pivot_data = decadal_avg.pivot(index='decade', columns='region', values='temperature_c')
    
    fig = go.Figure()
    
    # Add each region
    for region in sorted(pivot_data.columns):
        fig.add_trace(
            go.Scatter(
                x=pivot_data.index,
                y=pivot_data[region],
                mode='lines+markers',
                name=region,
                marker=dict(size=10)
            )
        )
    
    # Customize layout
    fig.update_layout(
        title='Decadal Average Temperatures by Region',
        xaxis_title='Decade',
        yaxis_title='Average Temperature (°C)',
        legend=dict(x=0.01, y=0.99),
        hovermode='x unified',
        template='plotly_white'
    )
    
    fig.update_xaxes(tickvals=pivot_data.index)
    
    return fig

def create_decadal_heatmap(results):
    """
    Create interactive decadal changes heatmap.
    """
    decadal_avg = results['decadal_avg']
    
    # Create pivot table
    pivot_data = decadal_avg.pivot(index='decade', columns='region', values='temperature_c')
    
    # Calculate temperature changes
    temperature_changes = pivot_data.diff()
    
    fig = go.Figure(data=go.Heatmap(
        z=temperature_changes.values,
        x=sorted(decadal_avg['region'].unique()),
        y=temperature_changes.index,
        colorscale='RdBu_r',
        zmid=0,
        colorbar=dict(title='Temperature Change (°C)'),
        text=np.round(temperature_changes.values, 2),
        texttemplate="%{text:.2f}",
    ))
    
    fig.update_layout(
        title='Temperature Change Between Decades by Region',
        xaxis_title='Region',
        yaxis_title='Decade',
        template='plotly_white'
    )
    
    return fig

def create_extreme_events_plots(results):
    """
    Create interactive extreme events plots.
    """
    extreme_counts = results['extreme_counts']
    
    # Create pivot tables
    hot_pivot = extreme_counts.pivot(index='decade', columns='region', values='extreme_hot')
    cold_pivot = extreme_counts.pivot(index='decade', columns='region', values='extreme_cold')
    
    # Hot events
    hot_fig = go.Figure(data=go.Heatmap(
        z=hot_pivot.values,
        x=sorted(extreme_counts['region'].unique()),
        y=hot_pivot.index,
        colorscale='YlOrRd',
        colorbar=dict(title='Number of Events'),
        text=hot_pivot.values.astype(int),
        texttemplate="%{text}",
    ))
    
    hot_fig.update_layout(
        title='Extreme Hot Temperature Events by Decade and Region',
        xaxis_title='Region',
        yaxis_title='Decade',
        template='plotly_white'
    )
    
    # Cold events
    cold_fig = go.Figure(data=go.Heatmap(
        z=cold_pivot.values,
        x=sorted(extreme_counts['region'].unique()),
        y=cold_pivot.index,
        colorscale='Blues',
        colorbar=dict(title='Number of Events'),
        text=cold_pivot.values.astype(int),
        texttemplate="%{text}",
    ))
    
    cold_fig.update_layout(
        title='Extreme Cold Temperature Events by Decade and Region',
        xaxis_title='Region',
        yaxis_title='Decade',
        template='plotly_white'
    )
    
    # Ratio of hot to cold
    ratio_pivot = hot_pivot / cold_pivot
    
    ratio_fig = go.Figure(data=go.Heatmap(
        z=ratio_pivot.values,
        x=sorted(extreme_counts['region'].unique()),
        y=ratio_pivot.index,
        colorscale='RdBu',
        zmid=1,
        colorbar=dict(title='Ratio (Hot/Cold)'),
        text=np.round(ratio_pivot.values, 2),
        texttemplate="%{text:.2f}",
    ))
    
    ratio_fig.update_layout(
        title='Ratio of Extreme Hot to Cold Events by Decade and Region',
        xaxis_title='Region',
        yaxis_title='Decade',
        template='plotly_white'
    )
    
    return {
        'hot': hot_fig,
        'cold': cold_fig,
        'ratio': ratio_fig
    }

def create_global_map(results):
    """
    Create interactive global map visualization.
    """
    processed_data = results['processed_data']
    
    # Filter to most recent decade
    recent_data = processed_data[processed_data['year'] >= 2010]
    
    # Calculate average temperature for each station
    station_avg = recent_data.groupby(['station_id', 'latitude', 'longitude'])['temperature_c'].mean().reset_index()
    
    fig = px.scatter_geo(
        station_avg,
        lat='latitude',
        lon='longitude',
        color='temperature_c',
        color_continuous_scale=px.colors.diverging.RdBu_r,
        range_color=[-10, 30],
        size_max=15,
        size=[10] * len(station_avg),  # Fixed size
        hover_name='station_id',
        hover_data={
            'latitude': ':.2f',
            'longitude': ':.2f',
            'temperature_c': ':.1f'
        },
        projection='natural earth',
        title='Global Average Temperatures (2010-2020)'
    )
    
    fig.update_layout(
        template='plotly_white',
        coloraxis_colorbar=dict(title='Temperature (°C)')
    )
    
    return fig

def generate_dashboard_template():
    """
    Generate the HTML template for the dashboard.
    """
    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Climate Data Analysis Dashboard</title>
        <!-- Argon CSS -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.15.4/css/all.min.css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/argon-design-system-free@1.2.0/assets/css/argon-design-system.min.css">
        <style>
            .visualization-card {
                margin-bottom: 30px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            .visualization-card:hover {
                transform: translateY(-5px);
            }
            .card-body {
                padding: 1.5rem;
            }
            .header-overlay {
                position: relative;
                background-image: url('https://images.unsplash.com/photo-1528164344705-47542687000d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80');
                background-size: cover;
                background-position: center;
            }
            .header-overlay:before {
                content: '';
                position: absolute;
                top: 0;
                right: 0;
                bottom: 0;
                left: 0;
                background: linear-gradient(135deg, rgba(40,60,120,0.9), rgba(50,140,190,0.9));
            }
            .navbar {
                margin-bottom: 0;
            }
            .section {
                padding: 70px 0;
            }
            .section-title {
                margin-bottom: 30px;
            }
            .section-heading {
                font-weight: 600;
                margin-bottom: 20px;
            }
            .plotly-graph {
                width: 100%;
                height: 500px;
            }
            .footer {
                background-color: #172b4d;
                padding: 30px 0;
                color: #ced4da;
            }
        </style>
    </head>
    <body>
        <!-- Navigation -->
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="#">Climate Analysis Dashboard</a>
                <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbar-primary" aria-controls="navbar-primary" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbar-primary">
                    <ul class="navbar-nav ml-lg-auto">
                        <li class="nav-item">
                            <a class="nav-link" href="#global-trends">Global Trends</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#regional-analysis">Regional Analysis</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#seasonal-patterns">Seasonal Patterns</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#extreme-events">Extreme Events</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#global-map">Global Map</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
        
        <!-- Header -->
        <header class="header-overlay">
            <div class="container py-5 text-center text-white position-relative">
                <div class="row py-5">
                    <div class="col-md-8 mx-auto">
                        <h1 class="display-2">Climate Data Analysis</h1>
                        <p class="lead">Interactive visualization of temperature trends and patterns from the Global Historical Climatology Network</p>
                        <a href="#global-trends" class="btn btn-outline-light mt-4">
                            <i class="fas fa-chart-line mr-2"></i>Explore Visualizations
                        </a>
                    </div>
                </div>
            </div>
        </header>
        
        <!-- Global Trends Section -->
        <section id="global-trends" class="section bg-default">
            <div class="container">
                <div class="row">
                    <div class="col-md-12 text-center section-title">
                        <h2 class="section-heading text-primary">Global Temperature Trends</h2>
                        <p class="lead">Analysis of global average temperature trends from 1960 to 2020</p>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-12">
                        <div class="card shadow visualization-card">
                            <div class="card-header">
                                <h5 class="mb-0">Global Average Temperature Trend</h5>
                            </div>
                            <div class="card-body">
                                <div id="global-temperature-trend" class="plotly-graph"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Regional Analysis Section -->
        <section id="regional-analysis" class="section bg-secondary">
            <div class="container">
                <div class="row">
                    <div class="col-md-12 text-center section-title">
                        <h2 class="section-heading text-white">Regional Temperature Analysis</h2>
                        <p class="lead text-white">Comparison of temperature trends across different regions</p>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-12">
                        <div class="card shadow visualization-card">
                            <div class="card-header">
                                <h5 class="mb-0">Regional Temperature Anomalies</h5>
                            </div>
                            <div class="card-body">
                                <div id="regional-temperature-trends" class="plotly-graph"></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-12">
                        <div class="card shadow visualization-card">
                            <div class="card-header">
                                <h5 class="mb-0">Temperature Anomalies Heatmap</h5>
                            </div>
                            <div class="card-body">
                                <div id="regional-heatmap" class="plotly-graph"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Seasonal Patterns Section -->
        <section id="seasonal-patterns" class="section bg-white">
            <div class="container">
                <div class="row">
                    <div class="col-md-12 text-center section-title">
                        <h2 class="section-heading text-primary">Seasonal Temperature Patterns</h2>
                        <p class="lead">Analysis of seasonal temperature trends and variability</p>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-12">
                        <div class="card shadow visualization-card">
                            <div class="card-header">
                                <h5 class="mb-0">Seasonal Temperature Trends</h5>
                            </div>
                            <div class="card-body">
                                <div id="seasonal-trends" class="plotly-graph"></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-12">
                        <div class="card shadow visualization-card">
                            <div class="card-header">
                                <h5 class="mb-0">Seasonal Temperature Variability</h5>
                            </div>
                            <div class="card-body">
                                <div id="seasonal-variability" class="plotly-graph"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Decadal Changes Section -->
        <section id="decadal-changes" class="section bg-gradient-primary">
            <div class="container">
                <div class="row">
                    <div class="col-md-12 text-center section-title">
                        <h2 class="section-heading text-white">Decadal Temperature Changes</h2>
                        <p class="lead text-white">Analysis of temperature changes by decade</p>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-12">
                        <div class="card shadow visualization-card">
                            <div class="card-header">
                                <h5 class="mb-0">Decadal Average Temperatures</h5>
                            </div>
                            <div class="card-body">
                                <div id="decadal-changes" class="plotly-graph"></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-12">
                        <div class="card shadow visualization-card">
                            <div class="card-header">
                                <h5 class="mb-0">Temperature Change Between Decades</h5>
                            </div>
                            <div class="card-body">
                                <div id="decadal-changes-heatmap" class="plotly-graph"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Extreme Events Section -->
        <section id="extreme-events" class="section bg-light">
            <div class="container">
                <div class="row">
                    <div class="col-md-12 text-center section-title">
                        <h2 class="section-heading text-primary">Extreme Temperature Events</h2>
                        <p class="lead">Analysis of extreme hot and cold temperature events</p>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-12">
                        <div class="card shadow visualization-card">
                            <div class="card-header">
                                <h5 class="mb-0">Extreme Hot Temperature Events</h5>
                            </div>
                            <div class="card-body">
                                <div id="extreme-hot-events" class="plotly-graph"></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-12">
                        <div class="card shadow visualization-card">
                            <div class="card-header">
                                <h5 class="mb-0">Extreme Cold Temperature Events</h5>
                            </div>
                            <div class="card-body">
                                <div id="extreme-cold-events" class="plotly-graph"></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-12">
                        <div class="card shadow visualization-card">
                            <div class="card-header">
                                <h5 class="mb-0">Ratio of Hot to Cold Events</h5>
                            </div>
                            <div class="card-body">
                                <div id="extreme-ratio" class="plotly-graph"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Global Map Section -->
        <section id="global-map" class="section bg-white">
            <div class="container">
                <div class="row">
                    <div class="col-md-12 text-center section-title">
                        <h2 class="section-heading text-primary">Global Temperature Map</h2>
                        <p class="lead">Geographic visualization of recent global temperatures</p>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-12">
                        <div class="card shadow visualization-card">
                            <div class="card-header">
                                <h5 class="mb-0">Global Average Temperatures (2010-2020)</h5>
                            </div>
                            <div class="card-body">
                                <div id="global-map-plot" class="plotly-graph"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Footer -->
        <footer class="footer">
            <div class="container">
                <div class="row align-items-center">
                    <div class="col-md-6">
                        <div class="copyright">
                            © 2025 Climate Data Analysis Project
                        </div>
                    </div>
                    <div class="col-md-6">
                        <ul class="nav nav-footer justify-content-end">
                            <li class="nav-item">
                                <a href="https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-monthly" class="nav-link" target="_blank">GHCN-M Dataset</a>
                            </li>
                            <li class="nav-item">
                                <a href="https://plotly.com/" class="nav-link" target="_blank">Plotly</a>
                            </li>
                            <li class="nav-item">
                                <a href="https://fastapi.tiangolo.com/" class="nav-link" target="_blank">FastAPI</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </footer>
        
        <!-- Core JavaScript -->
        <script src="https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/argon-design-system-free@1.2.0/assets/js/argon-design-system.min.js"></script>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        
        <!-- Dashboard JavaScript -->
        <script>
            // Load plots from API
            document.addEventListener('DOMContentLoaded', function() {
                // Global temperature trend
                fetch('/api/plots/global-temperature-trend')
                    .then(response => response.json())
                    .then(fig => Plotly.newPlot('global-temperature-trend', fig.data, fig.layout, {responsive: true}));
                
                // Regional temperature trends
                fetch('/api/plots/regional-temperature-trends')
                    .then(response => response.json())
                    .then(fig => Plotly.newPlot('regional-temperature-trends', fig.data, fig.layout, {responsive: true}));
                
                // Regional heatmap
                fetch('/api/plots/regional-heatmap')
                    .then(response => response.json())
                    .then(fig => Plotly.newPlot('regional-heatmap', fig.data, fig.layout, {responsive: true}));
                
                // Seasonal trends
                fetch('/api/plots/seasonal-trends')
                    .then(response => response.json())
                    .then(fig => Plotly.newPlot('seasonal-trends', fig.data, fig.layout, {responsive: true}));
                
                // Seasonal variability
                fetch('/api/plots/seasonal-variability')
                    .then(response => response.json())
                    .then(fig => Plotly.newPlot('seasonal-variability', fig.data, fig.layout, {responsive: true}));
                
                // Decadal changes
                fetch('/api/plots/decadal-changes')
                    .then(response => response.json())
                    .then(fig => Plotly.newPlot('decadal-changes', fig.data, fig.layout, {responsive: true}));
                
                // Decadal changes heatmap
                fetch('/api/plots/decadal-changes-heatmap')
                    .then(response => response.json())
                    .then(fig => Plotly.newPlot('decadal-changes-heatmap', fig.data, fig.layout, {responsive: true}));
                
                // Extreme hot events
                fetch('/api/plots/extreme-hot-events')
                    .then(response => response.json())
                    .then(fig => Plotly.newPlot('extreme-hot-events', fig.data, fig.layout, {responsive: true}));
                
                // Extreme cold events
                fetch('/api/plots/extreme-cold-events')
                    .then(response => response.json())
                    .then(fig => Plotly.newPlot('extreme-cold-events', fig.data, fig.layout, {responsive: true}));
                
                // Extreme ratio
                fetch('/api/plots/extreme-ratio')
                    .then(response => response.json())
                    .then(fig => Plotly.newPlot('extreme-ratio', fig.data, fig.layout, {responsive: true}));
                
                // Global map
                fetch('/api/plots/global-map')
                    .then(response => response.json())
                    .then(fig => Plotly.newPlot('global-map-plot', fig.data, fig.layout, {responsive: true}));
            });

            // Smooth scrolling for anchor links
            $(document).ready(function() {
                $('a[href*="#"]').not('[href="#"]').not('[href="#0"]').click(function(event) {
                    if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
                        let target = $(this.hash);
                        target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
                        if (target.length) {
                            event.preventDefault();
                            $('html, body').animate({
                                scrollTop: target.offset().top - 70
                            }, 1000);
                        }
                    }
                });
            });
        </script>
    </body>
    </html>
    """
    
    # Save the template
    with open(os.path.join(TEMPLATES_DIR, 'dashboard.html'), 'w') as f:
        f.write(template)

# API Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Serve the main dashboard.
    """
    # Generate the dashboard template if it doesn't exist
    template_path = os.path.join(TEMPLATES_DIR, 'dashboard.html')
    if not os.path.exists(template_path):
        generate_dashboard_template()
    
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/plots/global-temperature-trend")
async def get_global_temperature_plot():
    """
    API endpoint for global temperature trend plot.
    """
    results = load_results()
    fig = create_global_temperature_plot(results)
    return fig.to_dict()

@app.get("/api/plots/regional-temperature-trends")
async def get_regional_temperature_plot():
    """
    API endpoint for regional temperature trends plot.
    """
    results = load_results()
    fig = create_regional_temperature_plot(results)
    return fig.to_dict()

@app.get("/api/plots/regional-heatmap")
async def get_regional_heatmap():
    """
    API endpoint for regional temperature heatmap.
    """
    results = load_results()
    fig = create_regional_heatmap(results)
    return fig.to_dict()

@app.get("/api/plots/seasonal-trends")
async def get_seasonal_trends_plot():
    """
    API endpoint for seasonal trends plot.
    """
    results = load_results()
    fig = create_seasonal_trends_plot(results)
    return fig.to_dict()

@app.get("/api/plots/seasonal-variability")
async def get_seasonal_variability_plot():
    """
    API endpoint for seasonal variability plot.
    """
    results = load_results()
    fig = create_seasonal_variability_plot(results)
    return fig.to_dict()

@app.get("/api/plots/decadal-changes")
async def get_decadal_changes_plot():
    """
    API endpoint for decadal changes plot.
    """
    results = load_results()
    fig = create_decadal_changes_plot(results)
    return fig.to_dict()

@app.get("/api/plots/decadal-changes-heatmap")
async def get_decadal_changes_heatmap():
    """
    API endpoint for decadal changes heatmap.
    """
    results = load_results()
    fig = create_decadal_heatmap(results)
    return fig.to_dict()

@app.get("/api/plots/extreme-hot-events")
async def get_extreme_hot_events_plot():
    """
    API endpoint for extreme hot events plot.
    """
    results = load_results()
    figs = create_extreme_events_plots(results)
    return figs['hot'].to_dict()

@app.get("/api/plots/extreme-cold-events")
async def get_extreme_cold_events_plot():
    """
    API endpoint for extreme cold events plot.
    """
    results = load_results()
    figs = create_extreme_events_plots(results)
    return figs['cold'].to_dict()

@app.get("/api/plots/extreme-ratio")
async def get_extreme_ratio_plot():
    """
    API endpoint for extreme ratio plot.
    """
    results = load_results()
    figs = create_extreme_events_plots(results)
    return figs['ratio'].to_dict()

@app.get("/api/plots/global-map")
async def get_global_map_plot():
    """
    API endpoint for global map plot.
    """
    results = load_results()
    fig = create_global_map(results)
    return fig.to_dict()

if __name__ == "__main__":
    # Make sure the template exists
    generate_dashboard_template()
    
    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=8000) 