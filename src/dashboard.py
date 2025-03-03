import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from model import Shipment, Base
from core.connection.postgres import DATABASE_URL

# Page configuration
st.set_page_config(
    page_title="Shipment Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create a header
st.title("Shipment Tracking Dashboard")
st.write("Interactive visualization and management of interplanetary shipments")

# Database connection function - cache it to improve performance
@st.cache_resource
def get_engine():
    connection_string = DATABASE_URL
    return create_engine(connection_string)

# Data loading function
@st.cache_data
def load_shipment_data():
    engine = get_engine()
    with Session(engine) as session:
        # Query only non-deleted shipments
        query = select(Shipment).where(Shipment.is_deleted == False)
        result = session.execute(query).scalars().all()
        
        # Convert SQLAlchemy objects to dictionaries
        shipments = []
        for shipment in result:
            shipment_dict = {
                "id": shipment.id,
                "time": shipment.time,
                "weight_kg": shipment.weight_kg,
                "volume_m3": shipment.volume_m3,
                "eta_min": shipment.eta_min,
                "status": shipment.status,
                "forecast_origin_wind_velocity_mph": shipment.forecast_origin_wind_velocity_mph,
                "forecast_origin_wind_direction": shipment.forecast_origin_wind_direction,
                "forecast_origin_precipitation_chance": shipment.forecast_origin_precipitation_chance,
                "forecast_origin_precipitation_kind": shipment.forecast_origin_precipitation_kind,
                "origin_solar_system": shipment.origin_solar_system,
                "origin_planet": shipment.origin_planet,
                "origin_country": shipment.origin_country,
                "origin_address": shipment.origin_address,
                "destination_solar_system": shipment.destination_solar_system,
                "destination_planet": shipment.destination_planet,
                "destination_country": shipment.destination_country,
                "destination_address": shipment.destination_address,
                "created_at": shipment.created_at,
                "is_restored": shipment.is_restored,
                "restored_at": shipment.restored_at
            }
            shipments.append(shipment_dict)
        
        return pd.DataFrame(shipments)

# Load the data
try:
    df = load_shipment_data()
    st.success(f"Successfully loaded {len(df)} shipment records")
except Exception as e:
    st.error(f"Error connecting to database: {e}")
    st.stop()

# Display sample data
st.subheader("Sample Data")
st.dataframe(df.head(5), use_container_width=True)


# Create sidebar for search and filters
st.sidebar.title("Shipment Search & Filters")

# Global search across all text fields
search_term = st.sidebar.text_input("Search all fields:")

# Apply the search filter
if search_term:
    # Convert all columns to string for searching across different data types
    filtered_df = df[df.astype(str).apply(lambda row: row.str.contains(search_term, case=False).any(), axis=1)]
else:
    filtered_df = df.copy()

# Add specific filters in collapsible sections
with st.sidebar.expander("Status Filter"):
    status_options = sorted(df['status'].unique().tolist())
    selected_statuses = st.multiselect("Select status:", status_options, default=status_options)
    if selected_statuses:
        filtered_df = filtered_df[filtered_df['status'].isin(selected_statuses)]

with st.sidebar.expander("Origin Location Filter"):
    # Solar System Filter
    origin_systems = sorted(df['origin_solar_system'].unique().tolist())
    selected_origin_systems = st.multiselect("Origin Solar System:", origin_systems, default=[])
    
    # Planet Filter - dynamically updated based on selected solar systems
    if selected_origin_systems:
        filtered_df = filtered_df[filtered_df['origin_solar_system'].isin(selected_origin_systems)]
        origin_planets = sorted(filtered_df['origin_planet'].unique().tolist())
    else:
        origin_planets = sorted(df['origin_planet'].unique().tolist())
        
    selected_origin_planets = st.multiselect("Origin Planet:", origin_planets, default=[])
    if selected_origin_planets:
        filtered_df = filtered_df[filtered_df['origin_planet'].isin(selected_origin_planets)]

with st.sidebar.expander("Destination Location Filter"):
    # Solar System Filter
    dest_systems = sorted(df['destination_solar_system'].unique().tolist())
    selected_dest_systems = st.multiselect("Destination Solar System:", dest_systems, default=[])
    
    # Planet Filter - dynamically updated
    if selected_dest_systems:
        filtered_df = filtered_df[filtered_df['destination_solar_system'].isin(selected_dest_systems)]
        dest_planets = sorted(filtered_df['destination_planet'].unique().tolist())
    else:
        dest_planets = sorted(df['destination_planet'].unique().tolist())
        
    selected_dest_planets = st.multiselect("Destination Planet:", dest_planets, default=[])
    if selected_dest_planets:
        filtered_df = filtered_df[filtered_df['destination_planet'].isin(selected_dest_planets)]

with st.sidebar.expander("Shipment Metrics Filter"):
    # Weight range slider
    min_weight = float(df['weight_kg'].min())
    max_weight = float(df['weight_kg'].max())
    weight_range = st.slider(
        "Weight Range (kg):",
        min_weight, max_weight, (min_weight, max_weight)
    )
    filtered_df = filtered_df[
        (filtered_df['weight_kg'] >= weight_range[0]) & 
        (filtered_df['weight_kg'] <= weight_range[1])
    ]
    
    # Volume range slider
    min_volume = float(df['volume_m3'].min())
    max_volume = float(df['volume_m3'].max())
    volume_range = st.slider(
        "Volume Range (m³):",
        min_volume, max_volume, (min_volume, max_volume)
    )
    filtered_df = filtered_df[
        (filtered_df['volume_m3'] >= volume_range[0]) & 
        (filtered_df['volume_m3'] <= volume_range[1])
    ]
    
    # ETA range slider
    min_eta = int(df['eta_min'].min())
    max_eta = int(df['eta_min'].max())
    eta_range = st.slider(
        "ETA Range (minutes):",
        min_eta, max_eta, (min_eta, max_eta)
    )
    filtered_df = filtered_df[
        (filtered_df['eta_min'] >= eta_range[0]) & 
        (filtered_df['eta_min'] <= eta_range[1])
    ]

# Display the filtered data with pagination
st.subheader("Filtered Shipment Data")
st.write(f"Showing {len(filtered_df)} of {len(df)} shipments")

# Add pagination for large datasets
page_size = st.selectbox("Rows per page:", [10, 25, 50, 100])
total_pages = (len(filtered_df) - 1) // page_size + 1
if total_pages > 1:
    page_number = st.number_input("Page:", min_value=1, max_value=total_pages, step=1)
    start_idx = (page_number - 1) * page_size
    end_idx = min(start_idx + page_size, len(filtered_df))
    page_df = filtered_df.iloc[start_idx:end_idx]
else:
    page_df = filtered_df.head(page_size)

# Display the data table
st.dataframe(page_df, use_container_width=True)

# Add download functionality
st.download_button(
    label="Download filtered data as CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='shipment_data.csv',
    mime='text/csv',
)


# Create dashboard sections using tabs
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Visualizations", "Shipment Details", "Add New Shipment"])

with tab1:
    # Key metrics in cards
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Active Shipments",
            value=len(df[df['status'] != 'Delivered']),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Average Weight (kg)",
            value=f"{df['weight_kg'].mean():.2f}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Average Volume (m³)",
            value=f"{df['volume_m3'].mean():.2f}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Average ETA (min)",
            value=f"{df['eta_min'].mean():.0f}",
            delta=None
        )

    # Status distribution pie chart
    st.subheader("Shipment Status Distribution")
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    
    fig = px.pie(
        status_counts, 
        values='Count', 
        names='Status',
        title='Shipment Status Distribution',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig, use_container_width=True)

    # Distribution of Origin and Destination Systems and Planets
    st.subheader("Interplanetary Distribution")
    dist_cols = st.columns(2)
    
    with dist_cols[0]:
        # Origin Solar Systems Distribution
        origin_system_counts = df['origin_solar_system'].value_counts().reset_index()
        origin_system_counts.columns = ['Solar System', 'Count']
        
        fig = px.bar(
            origin_system_counts,
            x='Solar System',
            y='Count',
            title='Origin Solar Systems Distribution',
            color='Count',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis_title="Solar System", yaxis_title="Number of Shipments")
        st.plotly_chart(fig, use_container_width=True)
    
    with dist_cols[1]:
        # Destination Solar Systems Distribution
        dest_system_counts = df['destination_solar_system'].value_counts().reset_index()
        dest_system_counts.columns = ['Solar System', 'Count']
        
        fig = px.bar(
            dest_system_counts,
            x='Solar System',
            y='Count',
            title='Destination Solar Systems Distribution',
            color='Count',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis_title="Solar System", yaxis_title="Number of Shipments")
        st.plotly_chart(fig, use_container_width=True)
    
    # Planet distributions
    planet_cols = st.columns(2)
    
    with planet_cols[0]:
        # Origin Planets Distribution
        origin_planet_counts = df['origin_planet'].value_counts().reset_index()
        origin_planet_counts.columns = ['Planet', 'Count']
        origin_planet_counts = origin_planet_counts.sort_values('Count', ascending=False).head(10)
        
        fig = px.bar(
            origin_planet_counts,
            x='Planet',
            y='Count',
            title='Top 10 Origin Planets',
            color='Count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(xaxis_title="Planet", yaxis_title="Number of Shipments")
        st.plotly_chart(fig, use_container_width=True)
    
    with planet_cols[1]:
        # Destination Planets Distribution
        dest_planet_counts = df['destination_planet'].value_counts().reset_index()
        dest_planet_counts.columns = ['Planet', 'Count']
        dest_planet_counts = dest_planet_counts.sort_values('Count', ascending=False).head(10)
        
        fig = px.bar(
            dest_planet_counts,
            x='Planet',
            y='Count',
            title='Top 10 Destination Planets',
            color='Count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(xaxis_title="Planet", yaxis_title="Number of Shipments")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Shipment Visualizations")
    
    # Create a two-column layout for charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Origin-Destination Solar System Flow
        st.subheader("Origin-Destination Flow")
        
        # Create a dataframe with count of shipments between each origin-destination pair
        flow_df = df.groupby(['origin_solar_system', 'destination_solar_system']).size().reset_index()
        flow_df.columns = ['Origin', 'Destination', 'Count']
        flow_df = flow_df.sort_values('Count', ascending=False)
        
        # Bar chart showing the top origin-destination pairs
        fig = px.bar(
            flow_df.head(10),
            x='Count',
            y='Origin',
            color='Destination',
            title='Top 10 Shipment Routes by Solar System',
            orientation='h'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_col2:
        # Weight vs Volume scatter plot
        st.subheader("Weight vs Volume Analysis")
        
        fig = px.scatter(
            df,
            x='weight_kg',
            y='volume_m3',
            color='status',
            size='eta_min',
            hover_name='id',
            title='Shipment Weight vs Volume',
            labels={
                'weight_kg': 'Weight (kg)',
                'volume_m3': 'Volume (m³)',
                'status': 'Status',
                'eta_min': 'ETA (minutes)'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Create another row of charts
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        # Wind conditions at origin
        st.subheader("Origin Weather Conditions")
        
        # Create bins for wind velocity
        wind_bins = [0, 5, 10, 15, 20, float('inf')]
        wind_labels = ['0-5 mph', '5-10 mph', '10-15 mph', '15-20 mph', '20+ mph']
        
        df['wind_category'] = pd.cut(df['forecast_origin_wind_velocity_mph'], bins=wind_bins, labels=wind_labels)
        wind_counts = df.groupby(['wind_category', 'forecast_origin_wind_direction']).size().reset_index()
        wind_counts.columns = ['Wind Speed', 'Wind Direction', 'Count']
        
        fig = px.bar(
            wind_counts,
            x='Wind Direction',
            y='Count',
            color='Wind Speed',
            title='Wind Conditions at Origin Locations',
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_col4:
        # Precipitation analysis
        st.subheader("Precipitation Conditions")
        
        precip_df = df.groupby(['forecast_origin_precipitation_kind']).agg({
            'forecast_origin_precipitation_chance': 'mean',
            'id': 'count'
        }).reset_index()
        
        precip_df.columns = ['Precipitation Type', 'Average Chance', 'Shipment Count']
        
        # Sort by shipment count
        precip_df = precip_df.sort_values('Shipment Count', ascending=False)
        
        fig = px.bar(
            precip_df,
            x='Precipitation Type',
            y='Shipment Count',
            color='Average Chance',
            color_continuous_scale='Blues',
            title='Shipments by Precipitation Type and Chance'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Add a new section for detailed distribution analysis
    st.subheader("Interplanetary Distribution Analysis")
    
    # Create tabs for different distribution views
    dist_tab1, dist_tab2 = st.tabs(["Solar Systems", "Planets"])
    
    with dist_tab1:
        # Create a heatmap showing relationship between origin and destination solar systems
        cross_systems = pd.crosstab(df['origin_solar_system'], df['destination_solar_system'])
        
        fig = px.imshow(
            cross_systems,
            labels=dict(x="Destination Solar System", y="Origin Solar System", color="Shipment Count"),
            title="Origin-Destination Solar System Heatmap",
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        st.markdown("""
        The heatmap above shows the distribution of shipments between different solar systems. 
        Darker colors indicate higher numbers of shipments between a particular origin-destination pair.
        """)
    
    with dist_tab2:
        # Let user select specific solar systems to see planet distributions
        system_col1, system_col2 = st.columns(2)
        
        with system_col1:
            selected_origin_system = st.selectbox(
                "Select Origin Solar System:",
                options=sorted(df['origin_solar_system'].unique().tolist())
            )
            
            # Filter data for selected origin system
            origin_system_data = df[df['origin_solar_system'] == selected_origin_system]
            
            # Get planet distribution
            planet_counts = origin_system_data['origin_planet'].value_counts().reset_index()
            planet_counts.columns = ['Planet', 'Count']
            
            # Create pie chart
            fig = px.pie(
                planet_counts,
                values='Count',
                names='Planet',
                title=f"Planet Distribution in {selected_origin_system} (Origin)",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with system_col2:
            selected_dest_system = st.selectbox(
                "Select Destination Solar System:",
                options=sorted(df['destination_solar_system'].unique().tolist())
            )
            
            # Filter data for selected destination system
            dest_system_data = df[df['destination_solar_system'] == selected_dest_system]
            
            # Get planet distribution
            planet_counts = dest_system_data['destination_planet'].value_counts().reset_index()
            planet_counts.columns = ['Planet', 'Count']
            
            # Create pie chart
            fig = px.pie(
                planet_counts,
                values='Count',
                names='Planet',
                title=f"Planet Distribution in {selected_dest_system} (Destination)",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Add a planet-to-planet flow chart
        planet_flow = df.groupby(['origin_planet', 'destination_planet']).size().reset_index()
        planet_flow.columns = ['Origin Planet', 'Destination Planet', 'Count']
        planet_flow = planet_flow.sort_values('Count', ascending=False).head(15)  # Top 15 routes
        
        fig = px.bar(
            planet_flow,
            x='Count',
            y='Origin Planet',
            color='Destination Planet',
            title='Top 15 Planet-to-Planet Routes',
            orientation='h'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Shipment Details")
    
    # Allow selection of a specific shipment
    selected_id = st.selectbox(
        "Select Shipment ID:", 
        options=df['id'].tolist(),
        format_func=lambda x: f"Shipment #{x}"
    )
    
    # Display detailed information for the selected shipment
    if selected_id:
        shipment = df[df['id'] == selected_id].iloc[0]
        
        # Create column layout for shipment details
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.subheader("Shipment Information")
            st.write(f"**ID:** {shipment['id']}")
            st.write(f"**Status:** {shipment['status']}")
            st.write(f"**Weight:** {shipment['weight_kg']} kg")
            st.write(f"**Volume:** {shipment['volume_m3']} m³")
            st.write(f"**ETA:** {shipment['eta_min']} minutes")
            st.write(f"**Created At:** {shipment['created_at']}")
            
        with detail_col2:
            st.subheader("Route Information")
            st.write("**Origin:**")
            st.write(f"- Solar System: {shipment['origin_solar_system']}")
            st.write(f"- Planet: {shipment['origin_planet']}")
            st.write(f"- Country: {shipment['origin_country']}")
            st.write(f"- Address: {shipment['origin_address']}")
            
            st.write("**Destination:**")
            st.write(f"- Solar System: {shipment['destination_solar_system']}")
            st.write(f"- Planet: {shipment['destination_planet']}")
            st.write(f"- Country: {shipment['destination_country']}")
            st.write(f"- Address: {shipment['destination_address']}")
        
        # Weather section 
        st.subheader("Origin Weather Conditions")
        weather_cols = st.columns(4)
        
        with weather_cols[0]:
            st.metric(
                label="Wind Velocity", 
                value=f"{shipment['forecast_origin_wind_velocity_mph']} mph"
            )
        
        with weather_cols[1]:
            st.metric(
                label="Wind Direction", 
                value=shipment['forecast_origin_wind_direction']
            )
        
        with weather_cols[2]:
            st.metric(
                label="Precipitation Chance", 
                value=f"{shipment['forecast_origin_precipitation_chance']}%"
            )
        
        with weather_cols[3]:
            st.metric(
                label="Precipitation Type", 
                value=shipment['forecast_origin_precipitation_kind']
            )

with tab4:
    st.subheader("Add New Shipment")
    
    # Create a form for adding new data
    with st.form("new_shipment_form"):
        st.write("Enter shipment details:")
        
        # Create a multi-column layout for the form
        form_col1, form_col2 = st.columns(2)
        
        with form_col1:
            # Shipment basic details
            time = st.number_input("Time", min_value=0, step=1)
            weight_kg = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
            volume_m3 = st.number_input("Volume (m³)", min_value=0.0, step=0.1)
            eta_min = st.number_input("ETA (minutes)", min_value=0, step=1)
            
            status_options = ["Pending", "In Transit", "Delayed", "Delivered", "Cancelled"]
            status = st.selectbox("Status", options=status_options)
            
            # Origin information
            st.subheader("Origin")
            origin_solar_system = st.text_input("Solar System (Origin)")
            origin_planet = st.text_input("Planet (Origin)")
            origin_country = st.text_input("Country (Origin)")
            origin_address = st.text_input("Address (Origin)")
        
        with form_col2:
            # Weather forecast
            st.subheader("Weather Forecast")
            forecast_wind_velocity = st.number_input("Wind Velocity (mph)", min_value=0.0, step=0.1)
            
            wind_direction_options = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
            forecast_wind_direction = st.selectbox("Wind Direction", options=wind_direction_options)
            
            forecast_precip_chance = st.slider("Precipitation Chance (%)", min_value=0.0, max_value=100.0, step=1.0)
            
            precip_kind_options = ["None", "Rain", "Snow", "Hail", "Acid Rain", "Methane Rain"]
            forecast_precip_kind = st.selectbox("Precipitation Kind", options=precip_kind_options)
            
            # Destination information
            st.subheader("Destination")
            dest_solar_system = st.text_input("Solar System (Destination)")
            dest_planet = st.text_input("Planet (Destination)")
            dest_country = st.text_input("Country (Destination)")
            dest_address = st.text_input("Address (Destination)")
        
        # Submit button
        submit_button = st.form_submit_button("Add Shipment")
        
        if submit_button:
            try:
                # Create a new Shipment object
                new_shipment = Shipment(
                    time=time,
                    weight_kg=weight_kg,
                    volume_m3=volume_m3,
                    eta_min=eta_min,
                    status=status,
                    forecast_origin_wind_velocity_mph=forecast_wind_velocity,
                    forecast_origin_wind_direction=forecast_wind_direction,
                    forecast_origin_precipitation_chance=forecast_precip_chance,
                    forecast_origin_precipitation_kind=forecast_precip_kind,
                    origin_solar_system=origin_solar_system,
                    origin_planet=origin_planet,
                    origin_country=origin_country,
                    origin_address=origin_address,
                    destination_solar_system=dest_solar_system,
                    destination_planet=dest_planet,
                    destination_country=dest_country,
                    destination_address=dest_address
                )
                
                # Add to database
                engine = get_engine()
                with Session(engine) as session:
                    session.add(new_shipment)
                    session.commit()
                
                # Success message
                st.success("Shipment added successfully!")
                
                # Clear the cache to refresh data
                load_shipment_data.clear()
                
                # Recommend rerunning the app to see new data
                st.info("Refresh the page to see the new shipment in the dashboard.")
                
            except Exception as e:
                st.error(f"Error adding shipment: {e}")
