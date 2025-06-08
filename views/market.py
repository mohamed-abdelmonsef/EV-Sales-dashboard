import streamlit as st
import pandas as pd
import ollama

# Load dataset
file_path = "data/global_ev_sales_2010_2024.csv"
def load_data():
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.write("File not found, creating empty DataFrame.")
        return pd.DataFrame(columns=['region', 'category', 'parameter', 'mode', 'powertrain', 'year', 'unit', 'value'])

df = load_data()
df_cars = df[(df['mode'] == 'Cars') & (df['category'] == 'Historical')]
sales_df = df_cars[df_cars['parameter'] == 'EV sales'].pivot_table(
    values='value', index=['year', 'region', 'powertrain'], columns='unit', aggfunc='sum'
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
    'Japan': 'Asia', 'Korea': 'Asia', 'Netherlands': 'Europe', 'New Zealand': 'Oceania',
    'Norway': 'Europe', 'Poland': 'Europe', 'Portugal': 'Europe', 'Rest of the world': 'Other',
    'Romania': 'Europe', 'Seychelles': 'Africa', 'Slovakia': 'Europe', 'Slovenia': 'Europe',
    'South Africa': 'Africa', 'Spain': 'Europe', 'Sweden': 'Europe', 'Switzerland': 'Europe',
    'Thailand': 'Asia', 'Turkiye': 'Asia', 'United Arab Emirates': 'Asia', 'United Kingdom': 'Europe',
    'USA': 'North America', 'World': 'World'
}
sales_df['continent'] = sales_df['region'].map(continent_map).fillna('Other')

# Display data
st.subheader("EV Sales Data")
st.write(sales_df[['year', 'region', 'powertrain', 'Vehicles']])

# Performance classification by region
region_performance = sales_df.groupby('region')['Vehicles'].sum().reset_index()
threshold = region_performance['Vehicles'].median()
region_performance['Performance'] = region_performance['Vehicles'].apply(
    lambda x: "High Performing" if x > threshold else "Low Performing"
)
st.session_state.region_performance = region_performance

# Display performance
high_performing_regions = region_performance[region_performance['Performance'] == 'High Performing']
st.write("### High Performing Regions")
st.write(high_performing_regions[['region', 'Vehicles']])

low_performing_regions = region_performance[region_performance['Performance'] == 'Low Performing']
st.write("### Low Performing Regions")
st.write(low_performing_regions[['region', 'Vehicles']])

# Form for creating promotional campaigns
operation = st.radio("Choose Operation", ('Create New Campaign',))
with st.form(key='campaign_form'):
    new_region = st.selectbox("Select Region for Campaign", options=low_performing_regions['region'])
    new_description = st.text_area("Campaign Description", value="Promote EV adoption with incentives and awareness.")
    new_tagline = st.text_input("Campaign Tagline", value="Drive Electric, Save the Planet!")
    new_budget = st.number_input("Campaign Budget ($)", value=10000.0, min_value=0.0)
    submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        new_campaign = {
            'Region': new_region,
            'Description': new_description,
            'Tagline': new_tagline,
            'Budget': new_budget
        }
        campaign_df = pd.DataFrame([new_campaign])
        campaign_df.to_csv('data/campaigns.csv', mode='a', index=False, header=not pd.io.common.file_exists('data/campaigns.csv'))
        st.success("Campaign added successfully!")

# Ollama integration for promotional content
def generate_promotion(content_type, campaign_data):
    try:
        prompt = (
            f"Create a one-paragraph {content_type} for an EV adoption campaign:\n"
            f"Region: {campaign_data['Region']}\n"
            f"Description: {campaign_data['Description']}\n"
            f"Tagline: {campaign_data['Tagline']}\n"
            f"Budget: ${campaign_data['Budget']:,}\n"
        )
        response = ollama.chat(
            model='llama3.1:8b',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are an expert marketing assistant creating promotional content for EV adoption.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            options={
                'temperature': 1,
                'top_p': 0.95,
                'top_k': 40,
                'max_tokens': 8192
            }
        )
        st.subheader(f"{content_type} for {campaign_data['Region']}")
        promotion_text = response['message']['content'].strip()
        st.write(promotion_text)
        st.session_state["ollama_promotion"] = promotion_text
    except Exception as e:
        st.error(f"Error generating promotion: {e}")

if st.button("Generate promotional content for Low Performing Regions"):
    for _, region in low_performing_regions.iterrows():
        campaign_data = {
            'Region': region['region'],
            'Description': f"Promote EV adoption in {region['region']} with incentives.",
            'Tagline': "Drive Electric, Save the Planet!",
            'Budget': 10000.0
        }
        generate_promotion("Social Media Promotion Text", campaign_data)