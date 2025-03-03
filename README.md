# Interplanetary Shipping Data Management System

A comprehensive solution for collecting, managing, and visualizing interplanetary shipping data with automated ETL processes and interactive dashboards.

## Overview

This project provides an end-to-end solution for managing shipping data across multiple solar systems and planets. It consists of three main components:

1. **PostgreSQL Database**: Stores all shipping data with a comprehensive schema
2. **Data Ingestion Service**: Automatically crawls web sources at regular intervals to collect shipping data
3. **Data Visualization Dashboard**: Interactive Streamlit application for analyzing shipping metrics and patterns

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Sudo privileges

### Installation & Running

Launch the entire system with a single command:

```bash
sudo docker compose up --build
```

This command builds and starts all required containers:
- PostgreSQL database
- PgAdmin interface
- Data collection service
- Streamlit visualization dashboard

### Accessing Components

Once running, access the system components:

1. **Data Visualization Dashboard**: 
   - URL: [http://localhost:8501](http://localhost:8501)

2. **PgAdmin Database Interface**:
   - URL: [http://localhost:5050](http://localhost:5050)
   - Email: pgadmin4@pgadmin.org
   - Password: admin

## System Architecture

### Database Schema

The system uses a single comprehensive table to store shipping information:

```python
class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    time: Mapped[int] = mapped_column(INTEGER)
    weight_kg: Mapped[float] = mapped_column(FLOAT)
    volume_m3: Mapped[float] = mapped_column(FLOAT)
    eta_min: Mapped[int] = mapped_column(INTEGER)
    status: Mapped[str] = mapped_column(VARCHAR(255))
    
    # Weather Forecast Data
    forecast_origin_wind_velocity_mph: Mapped[float] = mapped_column(FLOAT)
    forecast_origin_wind_direction: Mapped[str] = mapped_column(VARCHAR(255))
    forecast_origin_precipitation_chance: Mapped[float] = mapped_column(FLOAT)
    forecast_origin_precipitation_kind: Mapped[str] = mapped_column(VARCHAR(255))
    
    # Location Data
    origin_solar_system: Mapped[str] = mapped_column(VARCHAR(255))
    origin_planet: Mapped[str] = mapped_column(VARCHAR(255))
    origin_country: Mapped[str] = mapped_column(VARCHAR(255))
    origin_address: Mapped[str] = mapped_column(VARCHAR(255))
    destination_solar_system: Mapped[str] = mapped_column(VARCHAR(255))
    destination_planet: Mapped[str] = mapped_column(VARCHAR(255))
    destination_country: Mapped[str] = mapped_column(VARCHAR(255))
    destination_address: Mapped[str] = mapped_column(VARCHAR(255))
    
    # Record Management
    created_at: Mapped[bool] = mapped_column(TIMESTAMP, default=func.now())
    is_deleted: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    deleted_at: Mapped[bool] = mapped_column(TIMESTAMP, nullable=True)
    is_restored: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    restored_at: Mapped[bool] = mapped_column(TIMESTAMP, nullable=True)
```

### Data Ingestion Process

The ETL pipeline automatically:

1. Crawls designated web source(s) at regular intervals
2. Extracts relevant shipping data
3. Processes and transforms the data
4. Loads new entries into the database
5. Marks obsolete records as deleted
6. Restores previously deleted records when they reappear

This creates a self-maintaining database that reflects the current state of shipping operations.

### Data Visualization Dashboard

The Streamlit-based dashboard provides comprehensive visualization features:

#### Visual Analytics
- Status distribution pie chart
- Origin-destination flow analysis
- Weight vs volume scatter plot
- Weather condition visualizations
- Key performance metrics

#### Search & Filtering
- Global text search across all fields
- Status and location filters
- Numeric range filters for weight, volume, and ETA
- Pagination support for large datasets

#### Detailed Information
- Individual shipment detail views
- Origin and destination information
- Weather conditions at origin

#### Data Management
- Form interface for adding new shipments
- Input validation and error handling
- Direct database integration

## Technical Implementation

### Container Structure

The project uses Docker Compose to orchestrate multiple containers:

1. **PostgreSQL**: Primary data storage
2. **PgAdmin**: Database management interface
3. **Data Processor**: Runs ETL processes on schedule
4. **Streamlit App**: Provides the visualization interface

### Key Technologies

- **Backend**: Python, SQLAlchemy ORM
- **Database**: PostgreSQL
- **ETL Process**: Custom web crawler with scheduling
- **Frontend**: Streamlit for interactive visualizations
- **Deployment**: Docker for containerization

## Troubleshooting

### Common Issues

- **Database Connection Failed**: Check if PostgreSQL container is running
- **Data Not Updating**: Verify the data processor container logs
- **Visualization Not Loading**: Check Streamlit container status
