import pandas as pd
import streamlit as st
import ollama

# Streamlit UI setup
st.title("EV Sales Chatbot")

# Load dataset
df = pd.read_csv('data/global_ev_sales_2010_2024.csv')

# Filter for 'Cars' mode and 'Historical' category
df_cars = df[(df['mode'] == 'Cars') & (df['category'] == 'Historical')]

# Calculate KPIs
sales_df = df_cars[df_cars['parameter'] == 'EV sales'].pivot_table(
    values='value', index=['year', 'region', 'powertrain'], columns='unit', aggfunc='sum'
).reset_index()
total_sales = round(sales_df['Vehicles'].sum(), 2)
total_regions = sales_df['region'].nunique()
avg_sales_per_year = round(sales_df.groupby('year')['Vehicles'].sum().mean(), 2)
sales_share_df = df_cars[df_cars['parameter'] == 'EV sales share'].pivot_table(
    values='value', index=['year', 'region'], columns='unit', aggfunc='sum'
).reset_index()
avg_sales_share = round(sales_share_df['percent'].mean(), 2)
sales_by_powertrain = sales_df.groupby('powertrain')['Vehicles'].sum().reset_index()
yoy_growth = sales_df[sales_df['region'] == 'World'].groupby('year')['Vehicles'].sum().pct_change().mean() * 100
avg_yoy_growth = round(yoy_growth, 2)

# Initialize session state keys
if "total_sales" not in st.session_state:
    st.session_state.total_sales = total_sales
if "total_regions" not in st.session_state:
    st.session_state.total_regions = total_regions
if "avg_sales_per_year" not in st.session_state:
    st.session_state.avg_sales_per_year = avg_sales_per_year
if "avg_sales_share" not in st.session_state:
    st.session_state.avg_sales_share = avg_sales_share
if "sales_by_powertrain" not in st.session_state:
    st.session_state.sales_by_powertrain = sales_by_powertrain
if "avg_yoy_growth" not in st.session_state:
    st.session_state.avg_yoy_growth = avg_yoy_growth

# Define data summary context
data_summary = (
    f"EV Sales Data Summary (2010-2024):\n"
    f"Total EV Sales: {st.session_state.total_sales:,} vehicles\n"
    f"Number of Regions: {st.session_state.total_regions}\n"
    f"Average Sales per Year: {st.session_state.avg_sales_per_year:,} vehicles\n"
    f"Average EV Sales Share: {st.session_state.avg_sales_share}% of total vehicle sales\n"
    f"Average YoY Sales Growth: {st.session_state.avg_yoy_growth}%\n"
    f"Sales by Powertrain:\n{st.session_state.sales_by_powertrain.to_string(index=False)}\n\n"
    "You are an intelligent assistant providing insights on global EV sales trends (2010-2024). "
    "Answer queries about sales trends, powertrain performance, regional adoption, or growth rates. "
    "Provide actionable insights to guide EV market strategies."
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question about EV sales data:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
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
                    },
                    {
                        'role': 'user',
                        'content': f"Answer this: {prompt}"
                    }
                ],
                options={
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_tokens': 550
                }
            )
            assistant_response = response['message']['content'].strip()
            st.markdown(assistant_response)
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    except Exception as e:
        st.error(f"Error generating response: {e}")