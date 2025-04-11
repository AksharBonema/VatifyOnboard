# live_demo.py

import streamlit as st
import streamlit.components.v1 as components

def render_live_demo_page():
    st.title("VATIFY Live Demo")
    st.write(
        """
        **VATIFY** is an innovative application that helps you manage your VAT records. With VATIFY you can:
        - Take pictures of your invoices and slips.
        - Automatically recognize key fields using AI.
        - Store your original invoice along with the extracted data.
        - Create VAT returns and submit them to SARS.
        
        Explore the live demo below or click the link to visit the demo site.
        """
    )
    st.markdown("[Visit Live Demo](https://vatifyapp.replit.app)")
    
    # Embed the demo inside an iframe.
    demo_html = """
    <iframe src="https://vatifyapp.replit.app" width="100%" height="600" frameborder="0" allowfullscreen></iframe>
    """
    components.html(demo_html, height=620)
