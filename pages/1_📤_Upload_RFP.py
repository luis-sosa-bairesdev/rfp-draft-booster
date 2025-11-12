"""Upload RFP Page - Epic 2: PDF Processing & Upload."""

import logging
import streamlit as st
from datetime import datetime, date
import io

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.rfp import RFP, RFPStatus
from services.pdf_processor import PDFProcessor
from services.file_validator import FileValidator
from services.storage_manager import StorageManager
from exceptions import PDFProcessingError
from utils.session import init_session_state
from components.ai_assistant import render_ai_assistant_button, render_ai_assistant_modal

logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Upload RFP",
    page_icon="📤",
    layout="wide"
)

# Initialize
init_session_state()


def main():
    """Main upload page."""
    # Render AI Assistant modal FIRST if open (so it's visible at top)
    if st.session_state.get("show_ai_assistant", False):
        render_ai_assistant_modal(key_suffix="upload", page_context="upload")
        st.markdown("---")
    
    # Header with AI Assistant button
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("📤 Upload RFP Document")
        st.markdown("Upload your RFP PDF to begin automated processing")
    with col2:
        render_ai_assistant_button(key_suffix="upload")
    
    st.divider()
    
    # Show results if processing is complete
    if st.session_state.get("processing_complete") and st.session_state.get("current_rfp"):
        display_results(st.session_state.current_rfp)
        
        # Reset button
        if st.button("📤 Upload Another RFP", type="primary"):
            st.session_state.processing_complete = False
            st.session_state.current_rfp = None
            st.rerun()
        return
    
    # File upload section
    st.markdown("### 📄 Select PDF File")
    st.markdown("""
    **Requirements:**
    - File format: PDF only
    - Maximum size: 50MB
    - Must contain extractable text (not scanned images)
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Drag and drop or click to browse",
        key="pdf_uploader"
    )
    
    if uploaded_file is not None:
        handle_file_upload(uploaded_file)
    else:
        show_upload_instructions()


def handle_file_upload(uploaded_file):
    """Handle the uploaded file."""
    
    # Display file info
    st.success(f"✅ File selected: **{uploaded_file.name}**")
    file_size = len(uploaded_file.getvalue())
    st.info(f"📊 Size: {FileValidator.format_file_size(file_size)}")
    
    # Validation
    with st.spinner("🔍 Validating file..."):
        is_valid, error_msg = FileValidator.validate_file(
            file_name=uploaded_file.name,
            file_size=file_size,
            file_content=io.BytesIO(uploaded_file.getvalue())
        )
    
    if not is_valid:
        st.error(f"❌ **Validation Failed:** {error_msg}")
        st.stop()
    
    st.success("✅ File validation passed!")
    
    # Metadata form
    st.divider()
    st.markdown("### 📝 RFP Information (Optional)")
    
    with st.form("rfp_metadata_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            rfp_title = st.text_input(
                "RFP Title",
                value=uploaded_file.name.replace(".pdf", ""),
                help="Give this RFP a descriptive title"
            )
            client_name = st.text_input(
                "Client Name",
                help="Name of the client/organization"
            )
        
        with col2:
            deadline = st.date_input(
                "Deadline",
                value=None,
                help="RFP submission deadline"
            )
            notes = st.text_area(
                "Notes",
                help="Any additional notes or context"
            )
        
        submitted = st.form_submit_button(
            "🚀 Process RFP",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            process_rfp(
                uploaded_file=uploaded_file,
                rfp_title=rfp_title,
                client_name=client_name,
                deadline=deadline,
                notes=notes
            )


def process_rfp(
    uploaded_file,
    rfp_title: str,
    client_name: str,
    deadline: date,
    notes: str
):
    """Process the uploaded RFP."""
    
    try:
        # Create RFP object
        rfp = RFP(
            title=rfp_title or uploaded_file.name,
            file_name=uploaded_file.name,
            file_size=len(uploaded_file.getvalue()),
            client_name=client_name or "",
            deadline=datetime.combine(deadline, datetime.min.time()) if deadline else None,
            notes=notes or "",
            uploaded_by="current_user",  # TODO: Get from auth
            status=RFPStatus.PROCESSING
        )
        
        # Progress tracking
        progress_bar = st.progress(0, text="Starting processing...")
        status_text = st.empty()
        
        # Step 1: Save file
        status_text.text("💾 Saving file...")
        progress_bar.progress(20, text="Saving file...")
        storage = StorageManager()
        file_content = io.BytesIO(uploaded_file.getvalue())
        rfp.file_path = storage.save_upload(
            file_content=file_content,
            file_name=uploaded_file.name,
            rfp_id=rfp.id
        )
        logger.info(f"File saved: {rfp.file_path}")
        
        # Step 2: Validate PDF
        status_text.text("✓ Validating PDF...")
        progress_bar.progress(40, text="Validating PDF...")
        processor = PDFProcessor()
        file_content.seek(0)
        is_valid, error = processor.validate_pdf(file_content)
        
        if not is_valid:
            raise PDFProcessingError(error)
        
        # Step 3: Extract text
        status_text.text("📄 Extracting text...")
        progress_bar.progress(60, text="Extracting text from PDF...")
        
        rfp.processing_start = datetime.now()
        file_content.seek(0)
        
        full_text, text_by_page, page_count = processor.extract_text(
            pdf_file=file_content,
            preserve_layout=True
        )
        
        rfp.extracted_text = full_text
        rfp.extracted_text_by_page = text_by_page
        rfp.total_pages = page_count
        rfp.processing_end = datetime.now()
        rfp.processing_time = (
            rfp.processing_end - rfp.processing_start
        ).total_seconds()
        rfp.status = RFPStatus.COMPLETED
        
        # Step 4: Finalize
        status_text.text("✅ Finalizing...")
        progress_bar.progress(100, text="Complete!")
        
        # Store in session
        st.session_state.current_rfp = rfp
        st.session_state.processing_complete = True
        
        logger.info(f"RFP processing complete: {rfp.id}")
        
        # Show success
        st.balloons()
        st.success("🎉 **RFP Processing Complete!**")
        st.info("👇 Scroll down to see results or refresh the page")
        
        # Trigger rerun to show results outside form context
        st.rerun()
        
    except PDFProcessingError as e:
        logger.error(f"PDF processing error: {e}")
        st.error(f"❌ **Processing Failed:** {str(e)}")
        st.info("💡 **Tip:** Make sure your PDF contains selectable text, not just images.")
        
    except Exception as e:
        logger.error(f"Unexpected error processing RFP: {e}", exc_info=True)
        st.error(f"❌ **Unexpected Error:** {str(e)}")
        st.error("Please try again or contact support if the problem persists.")


def display_results(rfp: RFP):
    """Display extraction results."""
    
    st.divider()
    st.markdown("## 📊 Extraction Results")
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Pages Extracted", rfp.total_pages)
    
    with col2:
        word_count = len(rfp.extracted_text.split()) if rfp.extracted_text else 0
        st.metric("Words", f"{word_count:,}")
    
    with col3:
        char_count = len(rfp.extracted_text) if rfp.extracted_text else 0
        st.metric("Characters", f"{char_count:,}")
    
    with col4:
        st.metric("Processing Time", f"{rfp.processing_time:.2f}s")
    
    # Text preview
    st.markdown("### 📝 Text Preview")
    st.markdown("*First 1000 characters of extracted text:*")
    
    preview_text = rfp.extracted_text[:1000] if rfp.extracted_text else ""
    st.text_area(
        "Extracted Text",
        value=preview_text + ("..." if len(rfp.extracted_text) > 1000 else ""),
        height=200,
        disabled=True,
        label_visibility="collapsed"
    )
    
    # Download button
    if rfp.extracted_text:
        st.download_button(
            label="📥 Download Full Text",
            data=rfp.extracted_text,
            file_name=f"{rfp.title}_extracted.txt",
            mime="text/plain"
        )
    
    # Next steps
    st.divider()
    st.markdown("### 🎯 Next Steps")
    st.markdown("""
    Your RFP has been successfully processed! You can now:
    
    1. **📋 Review Requirements** - Go to the Requirements page to see extracted requirements
    2. **⚠️ Check Risks** - Review detected risk clauses
    3. **🤝 Match Services** - See which services match the requirements
    4. **📝 Generate Draft** - Create an automated proposal draft
    """)
    
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 View Requirements", use_container_width=True):
            st.switch_page("pages/2_📋_Requirements.py")
    
    with col2:
        if st.button("⚠️ Check Risks", use_container_width=True):
            st.switch_page("pages/3_⚠️_Risk_Analysis.py")
    
    with col3:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.switch_page("src/main.py")


def show_upload_instructions():
    """Show upload instructions when no file is selected."""
    
    st.info("👆 **Please upload a PDF file to get started**")
    
    st.markdown("### 💡 Tips for Best Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Supported Files:**
        - ✅ PDF files with selectable text
        - ✅ Up to 50MB in size
        - ✅ Up to 100 pages
        
        **Not Supported (yet):**
        - ❌ Scanned PDFs (images only)
        - ❌ Password-protected PDFs
        - ❌ Word documents (.doc, .docx)
        """)
    
    with col2:
        st.markdown("""
        **Processing Time:**
        - Small RFPs (< 10 pages): ~5-10 seconds
        - Medium RFPs (10-50 pages): ~15-30 seconds
        - Large RFPs (50-100 pages): ~30-60 seconds
        
        **What Happens Next:**
        1. File validation
        2. Text extraction
        3. Results preview
        4. Continue to requirement analysis
        """)


if __name__ == "__main__":
    main()

