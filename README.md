# Climate Data Analysis Project

## Project Overview
This project analyzes global temperature data from the Global Historical Climatology Network Monthly (GHCN-M) dataset to identify climate patterns, trends, and anomalies across different regions of the world. The analysis examines temperature changes over the 1960-2020 period, focusing on regional differences, seasonal patterns, and extreme temperature events.

## Data Source
The project uses temperature data from the Global Historical Climatology Network Monthly (GHCN-M) dataset, maintained by the National Oceanic and Atmospheric Administration (NOAA). GHCN-M is a comprehensive global climate dataset containing monthly mean temperatures from thousands of weather stations worldwide, some with records dating back to the 1700s.

### About GHCN-M
- **Provider**: National Centers for Environmental Information (NCEI), NOAA
- **Dataset**: GHCN-Monthly Version 4
- **Variables**: Monthly mean temperature data
- **Coverage**: Global, with data from over 25,000 stations
- **Time Period**: Full dataset from 1701 to present (this project focuses on 1960-2020)
- **Official Link**: [GHCN-M Documentation](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-monthly)
- **Data Format**: Originally in fixed-width ASCII format with temperature in tenths of degrees Celsius

### Automatic Sample Data Generation
If downloading the actual GHCN-M data fails, the system automatically generates a sample dataset with similar properties:
- Creates 100 simulated stations distributed globally
- Generates monthly temperature data for 1960-2020
- Simulates realistic seasonal cycles (reversed in northern/southern hemispheres)
- Includes a warming trend similar to observed global climate change
- Adds random variations to mimic natural climate variability

## Project Structure

### Data Processing Pipeline
```
Download/Generate Data → Load Data → Preprocessing → Analysis → Visualization → Interactive Dashboard
```

### Directory Structure
```
climate_analysis/
├── README.md                  # Project documentation
├── climate_analysis.py        # Main analysis script
├── visualization.py           # Static visualization script
├── app.py                     # FastAPI server for interactive dashboard
├── setup.sh                   # Setup script for installing dependencies
├── data/                      # Raw data storage
│   ├── ghcnm_data.tar.gz      # Downloaded GHCN-M data (if available)
│   ├── temperature_data.csv   # Processed temperature records
│   └── station_metadata.csv   # Station information
├── results/                   # Analysis results in CSV format
│   ├── annual_global_avg.csv  # Global annual temperature averages
│   ├── annual_regional_avg.csv# Regional annual temperature averages
│   ├── seasonal_avg.csv       # Seasonal temperature patterns
│   ├── decadal_avg.csv        # Decadal temperature averages by region
│   ├── extreme_counts.csv     # Extreme temperature event statistics
│   └── processed_data.csv     # Complete processed dataset
├── plots/                     # Static visualizations (PNG format)
│   ├── global_temperature_trend.png   # Global warming trend
│   ├── regional_temperature_trends.png# Regional comparison
│   └── ...                            # Additional static plots
├── static/                    # Static assets for web dashboard
├── templates/                 # HTML templates for web dashboard
│   └── dashboard.html         # Main dashboard template
```

## Technical Requirements

### System Requirements
- Python 3.6 or higher
- Sufficient storage space (approximately 50MB for sample data, more for actual GHCN-M data)
- Internet connection (for downloading data)

### Dependencies
```
# Core Data Analysis
- pandas 1.0.0+     # Data manipulation and analysis
- numpy 1.18.0+     # Numerical operations
- matplotlib 3.2.0+ # Basic plotting functionality
- seaborn 0.10.0+   # Enhanced visualization
- requests          # For downloading data

# Interactive Dashboard
- fastapi           # API framework for serving interactive dashboard
- uvicorn           # ASGI server for FastAPI
- jinja2            # Template engine for HTML
- plotly            # Interactive visualization library
- python-multipart  # For file uploads (optional)
- aiofiles          # For async file operations
```

## Installation and Setup

### Quick Setup

Use the provided setup script to install all required dependencies:

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

### Manual Installation

1. Clone or download this repository:
   ```
   git clone <repository-url>
   cd climate_analysis
   ```

2. Create and activate a virtual environment (recommended):
   ```
   # Using venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Or using conda
   conda create -n climate-analysis python=3.9
   conda activate climate-analysis
   ```

3. Install required packages:
   ```
   # Core analysis packages
   pip install pandas numpy matplotlib seaborn requests
   
   # Interactive dashboard packages
   pip install fastapi uvicorn jinja2 plotly
   ```

## Usage

### Data Analysis

1. Execute the main analysis script to download/generate data and perform the analysis:
   ```
   python climate_analysis.py
   ```
   This will:
   - Attempt to download GHCN-M data or create a sample dataset
   - Process and clean the temperature data
   - Perform various analyses on the data
   - Save results to the `results/` directory

### Static Visualizations

1. Generate static visualizations from the analysis results:
   ```
   python visualization.py
   ```
   This will:
   - Create various plots visualizing the analysis results
   - Generate an HTML dashboard with all visualizations
   - Save all visualizations to the `plots/` directory

### Interactive Dashboard

1. Start the FastAPI server to serve the interactive dashboard:
   ```
   python app.py
   ```
   
2. Open your web browser and navigate to:
   ```
   http://localhost:8000
   ```
   
3. Explore the interactive dashboard with dynamic Plotly visualizations:
   - Zoom, pan, and hover over data points
   - View detailed information with tooltips
   - Toggle visibility of series and data elements
   - Export visualizations as PNG files

## Analysis Methodology

### Data Preprocessing
1. **Temperature Conversion**: Converting raw temperature values from tenths of degrees to degrees Celsius
2. **Temporal Organization**: Adding date objects and seasonal classifications
3. **Geographic Classification**: Categorizing stations into regions based on latitude:
   - Antarctica: -90° to -60°
   - Southern: -60° to -30°
   - Tropical S: -30° to 0°
   - Tropical N: 0° to 30°
   - Northern: 30° to 60°
   - Arctic: 60° to 90°

### Analysis Techniques
1. **Global Temperature Trends**:
   - Computing annual global mean temperatures
   - Calculating temperature anomalies relative to the dataset mean
   - Fitting linear trend to identify warming rate

2. **Regional Analysis**:
   - Calculating regional annual mean temperatures
   - Computing anomalies relative to 1961-1990 regional baselines
   - Comparing warming rates across different latitude bands

3. **Seasonal Pattern Analysis**:
   - Aggregating temperatures by meteorological seasons
   - Tracking changes in seasonal temperatures over time
   - Measuring seasonal temperature variability changes

4. **Decadal Change Analysis**:
   - Grouping data into decades to identify longer-term patterns
   - Comparing temperature changes between consecutive decades
   - Identifying regions with accelerated warming

5. **Extreme Temperature Analysis**:
   - Identifying extreme temperatures (±2 standard deviations from station means)
   - Tracking changes in extreme event frequency over time
   - Comparing hot vs. cold extreme event ratios

## Visualization Components

### Interactive Dashboard Features

The interactive dashboard provides a modern, user-friendly interface built with:

- **FastAPI**: Efficient Python web framework for serving the dashboard
- **Plotly.js**: JavaScript library for interactive data visualizations
- **Argon Design System**: Modern UI component library based on Bootstrap
- **Responsive Design**: Adaptable layout for desktop and mobile devices

Key interactive features include:

- **Dynamic Filtering**: Toggle data series on/off for clearer visualization
- **Hover Information**: Detailed data tooltips when hovering over data points
- **Zoom and Pan**: Explore specific time periods or regions in detail
- **Export Options**: Download visualizations as PNG files
- **Responsive Layout**: Automatic resizing for different screen sizes
- **Smooth Navigation**: Quick access to different visualization sections

### Time Series Analyses
- **Global Temperature Trend**: Dual-axis plot showing absolute temperatures and anomalies with trend line
- **Regional Temperature Trends**: Multi-line plot comparing temperature anomalies across regions
- **Seasonal Trends**: Seasonal temperature trends with 5-year rolling averages

### Heatmap Visualizations
- **Regional Temperature Anomalies**: Region × Year heatmap showing warming patterns
- **Decade-to-Decade Changes**: Heatmap of temperature changes between consecutive decades
- **Extreme Temperature Events**: Heatmaps showing hot and cold event frequencies by region and decade

### Statistical Visualizations
- **Seasonal Variability**: Plot of annual temperature range between seasons with trend line
- **Hot-to-Cold Event Ratio**: Visualization of changing extreme event patterns

### Geographic Visualization
- **Global Temperature Map**: Interactive map showing average temperatures by station location on a world map

## Key Findings

The analysis reveals several important climate patterns (based on sample or real data):

1. **Global Warming Trend**: Clear warming trend in global temperatures over the study period
2. **Regional Differences**: Polar regions (especially Arctic) showing more rapid warming than tropical regions
3. **Seasonal Shifts**: Changes in seasonal temperature patterns, with winters warming faster than summers in many regions
4. **Extreme Event Changes**: Increasing frequency of extreme hot events and decreasing frequency of extreme cold events over time
5. **Decade-to-Decade Acceleration**: Warming rates accelerating in recent decades compared to earlier periods

## License and Attribution
This project is provided for educational and research purposes. When using GHCN-M data, please cite the appropriate source:

Menne, M. J., Williams, C. N., Gleason, B. E., Rennie, J. J., & Lawrimore, J. H. (2018). The Global Historical Climatology Network Monthly Temperature Dataset, Version 4. Journal of Climate, 31(24), 9835-9854.

## Acknowledgments
- NOAA National Centers for Environmental Information for providing the GHCN-M dataset
- Contributors to the pandas, matplotlib, seaborn, and plotly libraries
- FastAPI and Argon Design System for the interactive dashboard framework
- All other open-source projects that made this analysis possible
