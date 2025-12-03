import streamlit as st

st.title("Overview")
st.write(
    "This page gives a quick overview of the app structure and purpose."
)

st.markdown(
    """
### App Structure

- `app.py` → Home page (this is what runs with `streamlit run app.py`)
- `pages/` → Additional pages (automatically discovered by Streamlit)
- `data/` → Example dataset(s)
- `.streamlit/config.toml` → Theme and server settings
- `requirements.txt` → Python dependencies
- `README.md` → Setup instructions for users

### How to extend

- Duplicate this file to make a new page  
- Change the title and content  
- Add your own logic, visualizations, or widgets
"""
)

