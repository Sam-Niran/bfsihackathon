import streamlit as st
import pandas as pd
import requests
import traceback

st.title("📄 Personal Loans Document Processor")

# Initialize session state for dataframe
if "processed_df" not in st.session_state:
    st.session_state.processed_df = None

# -------------------- File Uploader --------------------
uploaded_files = st.file_uploader(
    "Upload loan documents",
    accept_multiple_files=True,
    type=["pdf", "png", "jpg", "jpeg"]
)

# -------------------- Backend Submit Function --------------------
def send_data_to_backend(dataframe):
    try:
        backend_url = "http://localhost:5000/submit-loan-data"
        with st.spinner("Submitting data to backend..."):
            response = requests.post(backend_url, json=dataframe.to_dict(orient="records"))

        if response.ok:
            st.success("✅ Data submitted successfully!")
        else:
            st.error(f"❌ Failed to submit data: {response.text}")
    except Exception as e:
        st.error("❌ Error occurred while sending data to backend!")
        st.code(traceback.format_exc())

# -------------------- Document Processing --------------------
if uploaded_files and st.button("Process Documents"):
    with st.spinner("Extracting data..."):
        files = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]

        try:
            response = requests.post("http://localhost:5000/process-documents", files=files)
        except Exception as e:
            st.error("❌ Could not connect to the document processor service.")
            st.code(traceback.format_exc())
            st.stop()

        if response.ok:
            extracted_batch = response.json()
            df = pd.DataFrame([
                {
                    "Name": d.get("name", "n/a"),
                    "DOB": d.get("dateOfBirth", "n/a"),
                    "Address": d.get("address", "n/a"),
                }
                for d in extracted_batch
            ])
            st.session_state.processed_df = df
        else:
            st.error("❌ Failed to process documents.")
            st.code(response.text)

# -------------------- Display + Submit --------------------
if st.session_state.processed_df is not None:
    st.markdown("### ✏️ Review and Edit Extracted Data")
    edited_df = st.data_editor(st.session_state.processed_df, use_container_width=True)

    if st.button("Submit to Backend"):
        send_data_to_backend(edited_df)
