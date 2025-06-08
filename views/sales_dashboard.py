import pandas as pd
import plotly.express as px
import streamlit as st
import ollama
from fpdf import FPDF
import base64
import numpy as np

# Load dataset
df = pd.read_csv('data/global_ev_sales_2010_2024.csv')
df_cars = df[(df['mode'] == 'Cars') & (df['category'] == 'Historical')]
sales_df = df_cars[df_cars['parameter'] == 'EV sales'].pivot_table(
    values='value', index=['year', 'region', 'powertrain'], columns='unit', aggfunc='sum'
).reset_index()
sales_share_df = df_cars[df_cars['parameter'] == 'EV sales share'].pivot_table(
    values='value', index=['year', 'region'], columns='unit', aggfunc='sum'
).reset_index()

# Map regions to continents
continent_map = {
    'Australia': 'Oceania', 'Austria': 'Europe', 'Belgium': 'Europe', 'Brazil': 'South America',
    'Bulgaria': 'Europe', 'Canada': 'North America', 'Chile': 'South America', 'China': 'Asia',
    'Colombia': 'South America', 'Costa Rica': 'North America', 'Croatia': 'Europe', 'Cyprus': 'Europe',
    'Czech Republic': 'Europe', 'Denmark': 'Europe', 'Estonia': 'Europe', 'EU27': 'Europe',
    'Europe': 'Europe', 'Finland': 'Europe', 'France': 'Europe', 'Germany': 'Europe',
    'Greece': 'Europe', 'Hungary': 'Europe', 'Iceland': 'Europe', 'India': 'Asia',
    'Indonesia': 'Asia', 'Ireland': 'Europe', 'Israel': 'Asia', 'Italy': 'Europe',
    'Japan': 'Asia', 'Korea': 'Asia', 'Latvia': 'Europe', 'Lithuania': 'Europe',
    'Luxembourg': 'Europe', 'Mexico': 'North America', 'Netherlands': 'Europe', 'New Zealand': 'Oceania',
    'Norway': 'Europe', 'Poland': 'Europe', 'Portugal': 'Europe', 'Rest of the world': 'Other',
    'Romania': 'Europe', 'Seychelles': 'Africa', 'Slovakia': 'Europe', 'Slovenia': 'Europe',
    'South Africa': 'Africa', 'Spain': 'Europe', 'Sweden': 'Europe', 'Switzerland': 'Europe',
    'Thailand': 'Asia', 'Turkiye': 'Asia', 'United Arab Emirates': 'Asia', 'United Kingdom': 'Europe',
    'USA': 'North America', 'World': 'World'
}
sales_df['continent'] = sales_df['region'].map(continent_map).fillna('Other')

# Sidebar filters with URL persistence and optimization
st.sidebar.header("Filter EV Sales Data:")
params = st.query_params.to_dict()
region_options = list(sales_df['region'].unique())  # Convert to list
powertrain_options = list(sales_df['powertrain'].unique())  # Convert to list

# Handle region_param with Select All
region_param = params.get("Region", ["Select All"])
if isinstance(region_param, str):
    region_param = [region_param]
elif not isinstance(region_param, list):
    region_param = list(region_param)
# Validate region_param against options
region_param = [r for r in region_param if r in region_options or r == "Select All"]

# Handle powertrain_param
powertrain_param = params.get("Powertrain", powertrain_options)
if isinstance(powertrain_param, str):
    powertrain_param = [powertrain_param]
elif not isinstance(powertrain_param, list):
    powertrain_param = list(powertrain_param)
# Validate powertrain_param against options
powertrain_param = [p for p in powertrain_param if p in powertrain_options]

if "Region" not in st.session_state:
    st.session_state.Region = region_param if "Select All" in region_param else region_options
if "Powertrain" not in st.session_state:
    st.session_state.Powertrain = powertrain_param or powertrain_options

def regionCallback():
    st.session_state.Region = st.session_state.RegKey
    if "Select All" in st.session_state.RegKey:
        st.session_state.Region = region_options
    st.query_params["Region"] = st.session_state.RegKey

def powertrainCallback():
    st.session_state.Powertrain = st.session_state.PowKey
    st.query_params["Powertrain"] = st.session_state.PowKey

# Optimized Select Region with Select All
Region = st.sidebar.multiselect(
    "Select Region:", options=["Select All"] + region_options, default=st.session_state.Region,
    on_change=regionCallback, key='RegKey'
)
Powertrain = st.sidebar.multiselect(
    "Select Powertrain:", options=powertrain_options, default=st.session_state.Powertrain,
    on_change=powertrainCallback, key='PowKey'
)

# Filter data with fallback
df_selection = sales_df.query("region == @Region & powertrain == @Powertrain") if Region and Region != ["Select All"] and Powertrain else sales_df
if df_selection.empty:
    st.warning("No data available for selected filters!")
    st.stop()

# KPIs
total_sales = round(df_selection['Vehicles'].sum(), 2)
avg_sales_share = round(sales_share_df.query("region == @Region")['percent'].mean(), 2) if Region and Region != ["Select All"] else round(sales_share_df['percent'].mean(), 2)
yoy_growth = df_selection.groupby('year')['Vehicles'].sum().pct_change().mean() * 100
avg_yoy_growth = round(yoy_growth, 2)
total_regions = df_selection['region'].nunique()
avg_sales_per_region = round(total_sales / total_regions, 2) if total_regions > 0 else 0
avg_sales_per_year = round(df_selection.groupby('year')['Vehicles'].sum().mean(), 2)

# Store KPIs in session state
st.session_state.total_sales = total_sales
st.session_state.avg_sales_share = avg_sales_share
st.session_state.avg_yoy_growth = avg_yoy_growth
st.session_state.total_regions = total_regions
st.session_state.avg_sales_per_region = avg_sales_per_region
st.session_state.avg_sales_per_year = avg_sales_per_year

# Main page
st.header(":bar_chart: Global EV Sales Dashboard (2010-2024)")
st.markdown("### Key Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"### Total Sales\n**{total_sales:,} vehicles**")
with col2:
    st.markdown(f"### Avg Sales Share\n**{avg_sales_share}%**")
with col3:
    st.markdown(f"### Avg YoY Growth\n**{avg_yoy_growth}%**")

st.markdown("---")

# Visualizations
# Global Sales Over Time (Use full dataset for global view)
global_sales = sales_df[sales_df['region'] == 'World'].groupby('year')['Vehicles'].sum().reset_index()
if Region and Region != ["Select All"]:
    filtered_sales = df_selection[df_selection['region'] == 'World'].groupby('year')['Vehicles'].sum().reset_index()
    if not filtered_sales.empty:
        global_sales = filtered_sales
fig_global_sales = px.line(
    global_sales, x='year', y='Vehicles', title='Global EV Sales (2010-2024)',
    labels={'Vehicles': 'Sales (Units)', 'year': 'Year'}
)
fig_global_sales.update_layout(template='plotly_dark')
st.plotly_chart(fig_global_sales, use_container_width=True)

# Top Countries
top_countries = df_selection[df_selection['region'] != 'World'].groupby('region')['Vehicles'].sum().sort_values(ascending=False).head(5).reset_index()
fig_top_countries = px.bar(
    top_countries, x='region', y='Vehicles', title='EV Sales by Country',
    labels={'Vehicles': 'Sales (Units)', 'region': 'Country'}, text_auto=True
)
fig_top_countries.update_layout(template='plotly_dark')
st.plotly_chart(fig_top_countries, use_container_width=True)

# Powertrain Trends
powertrain_trends = df_selection.groupby(['year', 'powertrain'])['Vehicles'].sum().unstack().reset_index()
fig_powertrain = px.line(
    powertrain_trends, x='year', y=powertrain_trends.columns[1:], title='Powertrain Trends (2010-2024)',
    labels={'value': 'Sales (Units)', 'year': 'Year'}
)
fig_powertrain.update_layout(template='plotly_dark')
st.plotly_chart(fig_powertrain, use_container_width=True)

# Regional Breakdown
regional_sales = df_selection[df_selection['region'] != 'World'].copy()
regional_sales = regional_sales[regional_sales['region'] != 'Europe']  # Exclude "Europe" to avoid overlap with EU27
regional_sales['continent'] = regional_sales['region'].map(continent_map).fillna('Other')
regional_sales = regional_sales.groupby('continent')['Vehicles'].sum().reset_index()
total_sales = regional_sales['Vehicles'].sum()
regional_sales = regional_sales.assign(percentage=lambda x: (x['Vehicles'] / total_sales) * 100)

# Combine small slices into "Other" if less than 2%
threshold = 2.0
others = regional_sales[regional_sales['percentage'] < threshold].copy()
regional_sales = regional_sales[regional_sales['percentage'] >= threshold].copy()
if not others.empty:
    others_total = others['Vehicles'].sum()
    regional_sales = pd.concat([regional_sales, pd.DataFrame({'continent': ['Other'], 'Vehicles': [others_total], 'percentage': [(others_total / total_sales) * 100]})])

fig_regional = px.pie(
    regional_sales,
    values='Vehicles',
    names='continent',
    title='Regional Sales Breakdown (2010-2024)',
    hole=0.3,
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_regional.update_traces(
    textinfo='percent+label',
    textposition='inside',
    textfont=dict(size=12)
)
fig_regional.update_layout(
    template='plotly_dark',
    title_font_size=18,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
)
st.plotly_chart(fig_regional, use_container_width=True)

# Year-over-Year Growth
yoy_growth_data = df_selection.groupby('year')['Vehicles'].sum().pct_change().reset_index()
fig_yoy = px.line(
    yoy_growth_data, x='year', y='Vehicles', title='Year-over-Year Sales Growth (%)',
    labels={'Vehicles': 'Growth (%)', 'year': 'Year'}
)
fig_yoy.update_layout(template='plotly_dark')
st.plotly_chart(fig_yoy, use_container_width=True)

# Enhanced Global EV Sales Map with Natural Look
# Create a complete set of regions and years
all_years = range(2010, 2025)
all_regions = [r for r in sales_df['region'].unique() if r != 'World']
index = pd.MultiIndex.from_product([all_years, all_regions], names=['year', 'region'])
full_df = pd.DataFrame(index=index).reset_index()
country_sales = df_selection[df_selection['region'] != 'World'].groupby(['year', 'region'])['Vehicles'].sum().reset_index()
country_sales = full_df.merge(country_sales, on=['year', 'region'], how='left').fillna({'Vehicles': 0})

# Define custom earth-tone color scale
natural_colors = ['#F5F5DC', '#D9EAD3', '#A8D5BA', '#77C2A1', '#46AE88', '#158A6F']

# Create choropleth map
fig_map = px.choropleth(
    country_sales,
    locations='region',
    locationmode='country names',
    color=np.log10(country_sales['Vehicles'] + 1),  # Log scale, +1 to avoid log(0)
    animation_frame='year',
    title='Global EV Sales Map (2010-2024)',
    labels={'color': 'EV Sales'},
    color_continuous_scale=natural_colors,
    hover_data={
        'region': True,
        'year': True,
        'Vehicles': ':,.0f'  # Format numbers with commas
    }
)
fig_map.update_geos(
    projection_type='robinson',
    showcountries=True,
    countrycolor='#4A4A4A',
    countrywidth=0.5,
    showocean=True,
    oceancolor='#E6F3FF',
    showland=True,
    landcolor='#F5F5DC',
    fitbounds='locations'
)
fig_map.update_layout(
    template='plotly_dark',
    title_font=dict(size=22, family='Times New Roman'),
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor='#4A4A4A',
        coastlinewidth=0.3,
        bgcolor='white'
    ),
    coloraxis_colorbar=dict(
        title='EV Sales (Log Scale)',
        tickvals=[0, 1, 2, 3, 4, 5, 6],
        ticktext=['0', '10', '100', '1,000', '10,000', '100,000', '1,000,000'],
        len=0.6,
        thickness=15
    ),
    updatemenus=[{
        'type': 'buttons',
        'direction': 'left',
        'x': 0.1,
        'y': 0.1,
        'showactive': True,
        'buttons': [
            {
                'label': 'Play',
                'method': 'animate',
                'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}],
            },
            {
                'label': 'Pause',
                'method': 'animate',
                'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate'}],
            }
        ],
        'bgcolor': 'gray',  # Button background color
        'bordercolor': 'black',
        'font': {'color': 'blue', 'size': 14},  # Text color and size
    }],
    sliders=[{
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 16, 'family': 'Times New Roman'},
            'prefix': 'Year: ',
            'visible': True
        },
        'pad': {'b': 10, 't': 50}
    }]
)
fig_map.update_traces(
    selector=dict(type='choropleth'),
    zmin=0,
    zmax=6,  # Log scale up to 1,000,000
    hovertemplate='%{customdata[0]}<br>Year: %{customdata[1]}<br>Sales: %{customdata[2]:,.0f} vehicles<extra></extra>'
)
st.plotly_chart(fig_map, use_container_width=True)

# AI-Generated Insights
st.markdown("### AI-Generated Insights")
data_summary = (
    f"EV Sales Data (2010-2024):\n"
    f"Total Sales: {total_sales:,} vehicles\n"
    f"Average Sales Share: {avg_sales_share}%\n"
    f"Average YoY Growth: {avg_yoy_growth}%\n"
    f"Total Regions: {total_regions}\n"
    f"Average Sales per Region: {avg_sales_per_region:,} vehicles\n"
    f"Average Sales per Year: {avg_sales_per_year:,} vehicles\n\n"
    f"Analyze trends in EV sales, powertrain preferences, and regional adoption. Provide actionable insights to optimize EV market strategies."
)
if st.button("Generate Insights"):
    with st.spinner("Generating insights..."):
        try:
            response = ollama.chat(
                model='llama3.1:8b',
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are an expert in EV market analysis.'
                    },
                    {
                        'role': 'user',
                        'content': data_summary
                    }
                ],
                options={
                    'temperature': 1,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_tokens': 8192
                }
            )
            insights = response['message']['content'].strip()
            st.session_state["ollama_insights"] = insights
            st.write(insights)
        except Exception as e:
            st.error(f"Error generating insights: {e}")

# PDF Report Generation
def generate_pdf_report(kpis, visualizations, ollama_insights):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16, style="B")
    pdf.cell(200, 10, txt="EV Sales Dashboard Report", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=14, style="B")
    pdf.cell(200, 10, txt="Key Metrics", ln=True)
    pdf.set_font("Arial", size=12)
    for kpi, value in kpis.items():
        pdf.cell(200, 10, txt=f"{kpi}: {value}", ln=True)
    pdf.ln(10)
    if ollama_insights:
        pdf.set_font("Arial", size=14, style="B")
        pdf.cell(200, 10, txt="AI-Generated Insights", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, ollama_insights)
    pdf.ln(10)
    pdf.set_font("Arial", size=14, style="B")
    pdf.cell(200, 10, txt="Visualizations", ln=True)
    pdf.set_font("Arial", size=12)
    for viz_title, viz_path in visualizations.items():
        pdf.cell(200, 10, txt=viz_title, ln=True)
        try:
            pdf.image(viz_path, w=170)
        except:
            pdf.cell(200, 10, txt=f"(Image for {viz_title} not found)", ln=True)
        pdf.ln(10)
    return pdf

include_ai_insights = st.checkbox("Include AI Insights in the Report", value=False)
if st.button("Download PDF Report"):
    with st.spinner("Generating PDF report..."):
        try:
            kpis = {
                "Total Sales": f"{total_sales:,} vehicles",
                "Average Sales Share": f"{avg_sales_share}%",
                "Average YoY Growth": f"{avg_yoy_growth}%",
                "Total Regions": f"{total_regions}",
                "Average Sales per Region": f"{avg_sales_per_region:,} vehicles",
                "Average Sales per Year": f"{avg_sales_per_year:,} vehicles"
            }
            visualizations = {
                "Global EV Sales": "global_sales.png",
                "EV Sales by Country": "top_countries.png",
                "Powertrain Trends": "powertrain_trends.png",
                "Regional Sales Breakdown": "regional_breakdown.png",
                "Year-over-Year Sales Growth": "yoy_growth.png",
                "Global EV Sales Map": "global_map.png"
            }
            for fig, path in zip(
                [fig_global_sales, fig_top_countries, fig_powertrain, fig_regional, fig_yoy, fig_map],
                visualizations.values()
            ):
                try:
                    fig.write_image(path)
                except:
                    st.warning(f"Failed to save {path}")
            ollama_insights = st.session_state.get("ollama_insights", "No AI insights available.") if include_ai_insights else ""
            pdf = generate_pdf_report(kpis, visualizations, ollama_insights)
            pdf_path = "EV_Sales_Dashboard_Report.pdf"
            pdf.output(pdf_path)
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            b64 = base64.b64encode(pdf_data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="EV_Sales_Dashboard_Report.pdf">Click here to download the report</a>'
            st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error generating PDF report: {e}")
