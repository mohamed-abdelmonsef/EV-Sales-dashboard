# Global EV Sales Dashboard (2010-2024)

This project provides an interactive dashboard to explore global electric vehicle (EV) sales data from 2010 to 2024, using the Kaggle dataset. Built with Python, Pandas, Plotly, and Streamlit, it includes a chatbot for insights and a marketing module for promoting EV adoption in low-performing regions. AI-powered insights and content are generated using Ollama with a local Llama 3.1 model.

## Project Structure
- `app.py`: Entry point for the Streamlit multi-page app.
- `views/sales_dashboard.py`: Main dashboard with EV sales visualizations.
- `views/chatbot.py`: Chatbot for querying EV sales insights.
- `views/market.py`: Module for creating promotional campaigns.
- `data/`: Contains `global_ev_sales_2010_2024.csv` and `campaigns.csv`.
- `assets/`: Contains `midhun.jpg` for logo.
- `requirements.txt`: Dependencies.
- `README.md`: Documentation.

## Setup Instructions
1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd ev-sales-dashboard
   ```
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Install Ollama**:
   - Download and install Ollama from [ollama.com](https://ollama.com/).
   - Pull the Llama 3.1 model:
     ```bash
     ollama pull llama3.1:8b
     ```
   - Start the Ollama server:
     ```bash
     ollama serve
     ```
4. **Prepare data and assets**:
   - Place `global_ev_sales_2010_2024.csv` in the `data/` folder.
   - Ensure `midhun.jpg` is in the `assets/` folder.
5. **Run the app**:
   ```bash
   streamlit run app.py
   ```
6. **Access the app** at `http://localhost:8501`.

## Visualizations
- Global EV Sales (Line Chart)
- EV Sales by Country (Bar Chart)
- Powertrain Trends (Line Chart)
- Regional Sales Breakdown (Pie Chart)
- Year-over-Year Sales Growth (Line Chart)
- Global EV Sales Map (Animated Choropleth)

## Notes
- Ensure the Ollama server is running before starting the app.
- The `continent_map` in `sales_dashboard.py` and `market.py` includes all regions from the dataset.
- Requires a machine with at least 8GB RAM (16GB recommended) for running the Llama 3.1 model.