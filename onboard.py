# onboard.py

import streamlit as st
from supabase import Client

def upload_document_to_supabase(supabase: Client, file_obj, file_name: str):
    """
    Upload a file to Supabase Storage and return the public URL.
    Assumes you have a bucket named 'documents'.
    The filename will include the sanitized user's email.
    """
    if not file_obj:
        return None

    # Use the storage client property (not callable)
    storage = supabase.storage
    bucket_name = "documents"
    
    # Get the user's email from session and sanitize it (replace "@" and "." with underscores)
    user_email = st.session_state.get("user_email", "user")
    sanitized_email = user_email.replace("@", "_").replace(".", "_")
    
    # Create file path with user_id and sanitized email in the filename
    file_path = f"{st.session_state['user_id']}/{sanitized_email}_{file_name}"
    
    # Read file bytes and detect content type
    file_bytes = file_obj.read()
    content_type = getattr(file_obj, "type", "application/octet-stream")
    
    # Upload the file with the appropriate content-type
    storage.from_(bucket_name).upload(file_path, file_bytes, file_options={"content-type": content_type})
    
    # Return the public URL (already a string)
    return storage.from_(bucket_name).get_public_url(file_path)

def render_onboarding_form(supabase: Client):
    """
    Renders the onboarding form and handles saving user data and documents.
    This form includes:
      - Side-by-side fields for contact and company details.
      - eFiling credentials (or an option to indicate lack thereof).
      - A Power of Attorney expander with an eSign checkbox.
      - Document uploads (6 items arranged in 2 columns and 3 rows).
    
    If data exists from a previous session, the page shows a view mode displaying your details.
    The "Uploaded Documents" section appears inside an expander as a preview.
    A button allows the user to switch to edit mode, and in edit mode there is a "Cancel and Return to View" button.
    """
    st.title("Onboarding Form")
    st.write(
        "Welcome to the VATIFY Onboarding Page. Please complete this form with your company and contact details, "
        "provide your SARS eFiling credentials if available, and upload all required documents. Your information will "
        "be used to verify your identity and facilitate your SARS eFiling registration securely. Ensure all details "
        "are accurate and the uploaded files are clear and legible."
    )

    # Fetch existing onboarding data and document uploads
    user_id = st.session_state["user_id"]
    user_details_response = supabase.table("user_onboarding").select("*").eq("user_id", user_id).execute()
    user_details = user_details_response.data[0] if user_details_response.data else None

    doc_response = supabase.table("document_uploads").select("*").eq("user_id", user_id).execute()
    existing_docs = doc_response.data[0] if doc_response.data else {}

    # Determine if we should be in edit mode.
    if "edit_mode" not in st.session_state:
        st.session_state["edit_mode"] = True if (not user_details or not existing_docs) else False

    # ----------------- VIEW MODE -----------------
    if user_details and existing_docs and not st.session_state["edit_mode"]:
        st.markdown("## Your Onboarding Details")
        st.markdown("---")
        with st.container():
            st.subheader("Personal and Company Information")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Contact Name:** {user_details.get('contact_name', '')}")
                st.markdown(f"**Contact Details:** {user_details.get('contact_details', '')}")
                st.markdown(f"**Company Name:** {user_details.get('company_name', '')}")
            with col2:
                st.markdown(f"**Address:** {user_details.get('address', '')}")
                st.markdown(f"**ID/Passport Number:** {user_details.get('id_number', '')}")
                st.markdown(f"**Citizenship:** {user_details.get('citizenship', '')}")
                st.markdown(f"**Company Tax Number:** {user_details.get('company_tax_number', '')}")
                st.markdown(f"**Email Address:** {user_details.get('email_address', '')}")
                st.markdown(f"**Mobile:** {user_details.get('mobile', '')}")

        st.markdown("---")
        with st.container():
            st.subheader("eFiling Details")
            efiling = user_details.get("efiling_login_details", {})
            if efiling:
                st.markdown(f"**Username:** {efiling.get('username', '')}")
                st.markdown(f"**Password:** {'*' * len(efiling.get('password', '')) if efiling.get('password') else ''}")
            else:
                st.markdown("Not provided")

        st.markdown("---")
        with st.expander("Show Uploaded Documents"):
            st.subheader("Uploaded Documents")
            if existing_docs.get("cipc_document_url"):
                st.markdown(f"**CIPC Document:** [View Document]({existing_docs.get('cipc_document_url')})")
            if existing_docs.get("id_document_url"):
                st.markdown(f"**ID Document:** [View Document]({existing_docs.get('id_document_url')})")
            if existing_docs.get("tax_clearance_url"):
                st.markdown(f"**Tax Clearance Document:** [View Document]({existing_docs.get('tax_clearance_url')})")
            if existing_docs.get("power_of_attorney_url"):
                st.markdown(f"**Signed Power of Attorney:** [View Document]({existing_docs.get('power_of_attorney_url')})")
            if existing_docs.get("proof_of_address_url"):
                st.markdown(f"**Proof of Address:** [View Document]({existing_docs.get('proof_of_address_url')})")
            if existing_docs.get("other_documents_url"):
                st.markdown(f"**Other Documents:** [View Document]({existing_docs.get('other_documents_url')})")
        
        st.markdown("---")
        if st.button("Edit Onboarding Details"):
            st.session_state["edit_mode"] = True
            st.rerun()
        return

    # ----------------- EDIT MODE -----------------
    # Provide a button to cancel editing and return to view mode (if data exists)
    if st.session_state.get("edit_mode") and user_details and existing_docs:
        if st.button("Cancel and Return to View"):
            st.session_state["edit_mode"] = False
            st.rerun()

    # Pre-fill fields for edit mode if data exists; otherwise, use empty defaults
    contact_name = user_details["contact_name"] if user_details else ""
    contact_details = user_details["contact_details"] if user_details else ""
    company_name = user_details["company_name"] if user_details else ""
    address = user_details["address"] if user_details else ""
    id_number = user_details["id_number"] if user_details else ""
    citizenship = user_details["citizenship"] if user_details else "South African"
    company_tax_number = user_details["company_tax_number"] if user_details else ""
    email_address = user_details["email_address"] if user_details else ""
    mobile = user_details["mobile"] if user_details else ""

    # eFiling details stored as JSON
    efiling_json = user_details["efiling_login_details"] if (user_details and user_details.get("efiling_login_details")) else {}
    efiling_username = efiling_json.get("username", "")
    efiling_password = efiling_json.get("password", "")

    st.markdown("---")
    st.subheader("Personal and Company Information")
    # Row 1: Contact Name & Contact Details
    col1, col2 = st.columns(2)
    with col1:
        contact_name = st.text_input("Contact Name", contact_name)
    with col2:
        contact_details = st.text_input("Contact Details", contact_details)

    st.markdown("---")
    # Row 2: Company Name & Address
    col3, col4 = st.columns(2)
    with col3:
        company_name = st.text_input("Company Name", company_name)
    with col4:
        address = st.text_area("Address", address)

    st.markdown("---")
    # Row 3: ID/Passport & Citizenship
    col5, col6 = st.columns(2)
    with col5:
        id_number = st.text_input("ID Number/Passport Number", id_number)
    with col6:
        citizenship = st.selectbox(
            "Citizenship",
            ["South African", "Non South African"],
            index=["South African", "Non South African"].index(citizenship)
        )

    st.markdown("---")
    # Row 4: Company Tax Number & Email Address
    col7, col8 = st.columns(2)
    with col7:
        company_tax_number = st.text_input("Company Tax Number", company_tax_number)
    with col8:
        email_address = st.text_input("Email Address", email_address)

    st.markdown("---")
    # Row 5: Mobile (single column)
    mobile = st.text_input("Mobile", mobile)

    st.markdown("---")
    st.subheader("eFiling Details")
    no_efiling = st.checkbox("I do NOT have eFiling credentials")
    if no_efiling:
        efiling_username = ""
        efiling_password = ""
    else:
        col9, col10 = st.columns(2)
        with col9:
            efiling_username = st.text_input("eFiling Username", efiling_username)
        with col10:
            efiling_password = st.text_input("eFiling Password", efiling_password, type="password")

    st.markdown("---")
    # Power of Attorney Expander
    with st.expander("Power of Attorney - Please Read & eSign"):
        st.write(
            """
            **Power of Attorney**  
            By granting this Power of Attorney, you authorize VATIFY to access and manage your SARS eFiling account for the purposes of VAT submissions, income tax returns, and communication with SARS on your behalf. Please review the terms carefully and eSign below if you agree.
            """
        )
        e_sign = st.checkbox("I agree and electronically sign this Power of Attorney.")

    st.markdown("---")
    st.subheader("Document Uploads")
    st.write(
        "Please upload the required documents using the buttons below. Ensure all files are clear and legible, as they will be used to verify your identity, address, and company details for your SARS eFiling registration. Accepted formats include PDF, JPG, and PNG."
    )

    # Create 3 rows with 2 columns each (2 cols, 3 rows)
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        cipc_doc = st.file_uploader("CIPC Document", type=["pdf", "jpg", "png"])
    with row1_col2:
        id_doc = st.file_uploader("ID Document", type=["pdf", "jpg", "png"])

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        tax_clearance_doc = st.file_uploader("Tax Clearance Document", type=["pdf", "jpg", "png"])
    with row2_col2:
        power_of_attorney_doc = st.file_uploader("Signed Power of Attorney", type=["pdf", "jpg", "png"])

    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        proof_of_address_doc = st.file_uploader("Proof of Address", type=["pdf", "jpg", "png"])
    with row3_col2:
        other_documents_doc = st.file_uploader("Other Documents", type=["pdf", "jpg", "png"])

    if st.button("Submit Onboarding"):
        # 1. Build eFiling JSON
        efiling_details = {}
        if not no_efiling:
            efiling_details["username"] = efiling_username
            efiling_details["password"] = efiling_password

        # 2. Create data payload for user_onboarding
        data_payload = {
            "user_id": user_id,
            "contact_name": contact_name,
            "contact_details": contact_details,
            "company_name": company_name,
            "address": address,
            "id_number": id_number,
            "citizenship": citizenship,
            "company_tax_number": company_tax_number,
            "email_address": email_address,
            "mobile": mobile,
            "efiling_login_details": efiling_details,
            "e_sign": e_sign
        }

        if user_details:
            supabase.table("user_onboarding").update(data_payload).eq("user_id", user_id).execute()
        else:
            supabase.table("user_onboarding").insert(data_payload).execute()

        # 3. Upload documents (replace if new file provided; otherwise, keep existing)
        cipc_url = upload_document_to_supabase(supabase, cipc_doc, "cipc_doc") \
            if cipc_doc else existing_docs.get("cipc_document_url", "")
        id_url = upload_document_to_supabase(supabase, id_doc, "id_doc") \
            if id_doc else existing_docs.get("id_document_url", "")
        tax_url = upload_document_to_supabase(supabase, tax_clearance_doc, "tax_clearance_doc") \
            if tax_clearance_doc else existing_docs.get("tax_clearance_url", "")
        power_url = upload_document_to_supabase(supabase, power_of_attorney_doc, "power_of_attorney_doc") \
            if power_of_attorney_doc else existing_docs.get("power_of_attorney_url", "")
        proof_url = upload_document_to_supabase(supabase, proof_of_address_doc, "proof_of_address_doc") \
            if proof_of_address_doc else existing_docs.get("proof_of_address_url", "")
        other_url = upload_document_to_supabase(supabase, other_documents_doc, "other_documents_doc") \
            if other_documents_doc else existing_docs.get("other_documents_url", "")

        doc_payload = {
            "user_id": user_id,
            "cipc_document_url": cipc_url,
            "id_document_url": id_url,
            "tax_clearance_url": tax_url,
            "power_of_attorney_url": power_url,
            "proof_of_address_url": proof_url,
            "other_documents_url": other_url
        }

        if existing_docs:
            supabase.table("document_uploads").update(doc_payload).eq("user_id", user_id).execute()
        else:
            supabase.table("document_uploads").insert(doc_payload).execute()

        st.success("Onboarding details submitted successfully!")
        st.session_state["edit_mode"] = False
        st.rerun()
