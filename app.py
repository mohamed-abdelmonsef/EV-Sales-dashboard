import streamlit as st

# Page setup
dashpage = st.Page(
    "views/sales_dashboard.py",
    title="EV SALES DASHBOARD",
    icon=":material/bar_chart:",
    default=True,
)
chatpage = st.Page(
    "views/chatbot.py",
    title="AI CHAT BOT",
    icon=":material/smart_toy:",
)
markpage = st.Page(
    "views/market.py",
    title="MARKETING CONTENT CREATOR",
    icon=":material/smart_toy:",
)

# Navigation setup
pg = st.navigation(
    {
        "Toolbar": [dashpage, chatpage, markpage],
    }
)

# Set logo (ensure assets/midhun.png exists)
st.logo("assets/midhun.png")

# Run navigation
pg.run()