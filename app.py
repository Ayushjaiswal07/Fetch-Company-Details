# app.py
import streamlit as st
import json
from form_handler import FormHandler
from mail_sender import EmailSender

# Initialize your classes
handler = FormHandler()
sender = EmailSender()

# Streamlit App
st.title("Company Data Extractor 🚀")

with st.form("company_form"):
    st.subheader("Enter Company Information")
    company_url = st.text_input("Company Website URL", placeholder="https://example.com")
    email = st.text_input("Your Email Address", placeholder="your@email.com")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not company_url.strip() or not email.strip():
            st.error("🚨 Both 'Company Website URL' and 'Your Email Address' are required!")
        else:
            with st.spinner("Processing the website... Please wait."):

                try:
                    result = handler.process_website(company_url)
                    if result:
                        result_str = json.dumps(result, indent=2)  # ✅ convert dict to formatted string
                        st.success("✅ Data extracted and emailed successfully!")
                        st.text_area("Extracted Data Preview", result_str, height=300)
                        sender.send_email(
                            to_email=email,
                            subject="Requested Details",
                            body=result_str
                        )
                    else:
                        st.error("❌ Failed to extract data. Please try another URL.")
                except Exception as e:
                    st.error(f"🚨 Error: {e}")
