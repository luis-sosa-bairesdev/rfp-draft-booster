# Epic 10: Batch Upload & Processing - Technical Spike

## 📋 Overview

**Epic Title:** Batch Upload & Processing  
**Sprint:** TBD (Sprint 6 or 7)  
**Status:** Planning  
**Priority:** Medium-High (Scalability feature)  
**Estimated Effort:** 2-3 days (17-23 hours)

## 🎯 Business Goal

Enable users to process multiple RFPs simultaneously by uploading a ZIP file containing multiple PDFs. Automate text extraction, requirement analysis, and risk detection for each RFP in the batch, significantly improving productivity for users handling multiple proposals.

## 📐 Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Batch Upload Flow                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. USER UPLOADS ZIP FILE                                       │
│     ┌────────────────────────────────────────────┐             │
│     │ Upload RFP Page (with tabs)                │             │
│     │  Tab 1: Single RFP (existing)              │             │
│     │  Tab 2: Batch Upload (ZIP) 🆕              │             │
│     │                                             │             │
│     │  [Drag & Drop ZIP or Browse]               │             │
│     │  • Max 5 PDFs (free tier)                  │             │
│     │  • Max 100MB total                         │             │
│     │                                             │             │
│     │  Options:                                   │             │
│     │   ☑ Extract Requirements (AI)              │             │
│     │   ☑ Detect Risks (Pattern) ▼               │             │
│     │      ☐ Use AI Detection (slower)           │             │
│     │                                             │             │
│     │  [Process Batch] [Cancel]                  │             │
│     └────────────────────────────────────────────┘             │
│                          ▼                                       │
│  2. VALIDATION                                                  │
│     • Check ZIP is valid                                        │
│     • Count PDFs ≤ MAX_BATCH_FILES (5 default)                 │
│     • Check total size < 100MB                                 │
│     • Verify all files are PDFs                                │
│     • Check for duplicate names                                │
│     • Skip empty/corrupt PDFs (with warning)                   │
│                          ▼                                       │
│  3. BATCH PROCESSING (Sequential)                              │
│     ┌────────────────────────────────────────────┐             │
│     │ For each PDF in ZIP:                       │             │
│     │                                             │             │
│     │   Try:                                      │             │
│     │     a. Extract text (10s)                  │             │
│     │     b. Extract requirements with AI (60s)  │             │
│     │     c. Detect risks (pattern, 10s)         │             │
│     │     d. Track processing time               │             │
│     │     e. Save to batch_rfps list             │             │
│     │                                             │             │
│     │   Except Error:                             │             │
│     │     • Log error                             │             │
│     │     • Mark as "failed" in results          │             │
│     │     • Continue with next PDF ✅             │             │
│     │                                             │             │
│     │   Update UI:                                │             │
│     │     • Progress bar: (i+1)/total            │             │
│     │     • Status text: "Processing X.pdf..."   │             │
│     │     • Summary table: live updates          │             │
│     └────────────────────────────────────────────┘             │
│                          ▼                                       │
│  4. SUMMARY & RESULTS                                           │
│     ┌────────────────────────────────────────────┐             │
│     │ Summary Table (Interactive)                │             │
│     │ ┌──────────────────────────────────────┐  │             │
│     │ │ File │ Status │ Reqs │ Risks │ Time │  │             │
│     │ ├──────────────────────────────────────┤  │             │
│     │ │ rfp1 │ ✅     │  15  │   7   │  72s │  │  ← Click    │
│     │ │ rfp2 │ ✅     │  23  │  12   │  85s │  │             │
│     │ │ rfp3 │ ❌     │  --  │  --   │  --  │  │             │
│     │ │ rfp4 │ ✅     │  18  │   9   │  78s │  │             │
│     │ │ rfp5 │ ✅     │  20  │   8   │  81s │  │             │
│     │ ├──────────────────────────────────────┤  │             │
│     │ │ Total: 5 │ Success: 4 (80%) │ Avg 79s│ │             │
│     │ └──────────────────────────────────────┘  │             │
│     │                                             │             │
│     │ [View Batch Results] [Export JSON]         │             │
│     │ [Export Excel] [Retry Failed (1)]          │             │
│     └────────────────────────────────────────────┘             │
│                          ▼                                       │
│  5. NAVIGATION & EXPORT                                         │
│     • Go to "Batch Results" page                               │
│     • View individual RFP details                              │
│     • Load RFP to standard pages (Req/Risk)                    │
│     • Export all results (JSON/Excel)                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🗂️ Data Model

### Batch RFP Structure

```python
# Stored in st.session_state.batch_rfps: List[Dict]

batch_rfp_entry = {
    "rfp": RFP(
        file_name="sample_rfp_1.pdf",
        title="Software Development RFP",
        client_name="ABC Corp",
        deadline=datetime(...),
        text="...",
        uploaded_at=datetime.now()
    ),
    "requirements": [
        Requirement(...),
        Requirement(...),
        # ... list of requirements
    ],
    "risks": [
        Risk(...),
        Risk(...),
        # ... list of risks
    ],
    "draft": None,  # Not generated in batch
    "processing_time": 72.5,  # seconds
    "status": "success",  # "success" | "failed" | "processing"
    "error": None,  # Error message if failed
    "processed_at": datetime.now()
}

# Full batch structure
st.session_state.batch_info = {
    "batch_id": "batch_20250113_153045",
    "uploaded_at": datetime.now(),
    "total_files": 5,
    "successful": 4,
    "failed": 1,
    "options": {
        "extract_requirements": True,
        "detect_risks_pattern": True,
        "detect_risks_ai": False,
        "generate_drafts": False
    }
}

# Usage tracking (free tier)
st.session_state.batch_usage = {
    "batches_today": 1,
    "last_batch_date": "2025-01-13"
}
```

## 🎨 UI Components

### 1. Batch Upload Tab (in Upload Page)

```python
# pages/1_📤_Upload_RFP.py

def render_upload_page():
    """Upload page with Single and Batch tabs."""
    
    st.title("📤 Upload RFP")
    
    tab1, tab2 = st.tabs(["📄 Single RFP", "📦 Batch Upload (ZIP)"])
    
    with tab1:
        # Existing single upload UI
        render_single_upload()
    
    with tab2:
        # New batch upload UI
        render_batch_upload()


def render_batch_upload():
    """Render batch upload UI."""
    
    st.subheader("📦 Batch Upload & Processing")
    
    # Check free tier limits
    max_files = int(st.secrets.get("MAX_BATCH_FILES", 5))
    max_size_mb = 100
    
    # Usage tracking
    if "batch_usage" not in st.session_state:
        st.session_state.batch_usage = {
            "batches_today": 0,
            "last_batch_date": None
        }
    
    today = datetime.now().date()
    if st.session_state.batch_usage.get("last_batch_date") != today:
        st.session_state.batch_usage = {
            "batches_today": 0,
            "last_batch_date": today
        }
    
    # Check daily limit
    if st.session_state.batch_usage["batches_today"] >= 1:
        st.warning(
            "⚠️ **Daily Limit Reached**\n\n"
            "You've processed 1 batch today (free tier limit).\n\n"
            "Upgrade to Pro for unlimited batches."
        )
        return
    
    # Info box
    st.info(
        f"📦 **Batch Upload (Free Tier)**\n\n"
        f"• Upload ZIP file with up to **{max_files} PDFs**\n"
        f"• Maximum total size: **{max_size_mb}MB**\n"
        f"• Processing time: **~1-2 minutes per PDF**\n"
        f"• Limit: **1 batch per day** (free tier)\n\n"
        "💡 Upgrade to Pro for unlimited batches and faster processing"
    )
    
    # File uploader
    zip_file = st.file_uploader(
        "Upload ZIP file with PDFs",
        type=["zip"],
        help=f"Upload a ZIP containing up to {max_files} PDF files",
        key="batch_zip_upload"
    )
    
    if not zip_file:
        return
    
    # Processing options
    st.markdown("### ⚙️ Processing Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        extract_reqs = st.checkbox(
            "📋 Extract Requirements (AI)",
            value=True,
            help="Use AI to automatically extract requirements from each RFP",
            key="batch_opt_reqs"
        )
    
    with col2:
        detect_risks_pattern = st.checkbox(
            "⚠️ Detect Risks (Pattern Matching)",
            value=True,
            help="Fast, rule-based risk detection",
            key="batch_opt_risks_pattern"
        )
        
        if detect_risks_pattern:
            detect_risks_ai = st.checkbox(
                "🤖 Also use AI Detection (slower, more comprehensive)",
                value=False,
                help="AI-powered risk detection (adds ~60s per RFP)",
                key="batch_opt_risks_ai"
            )
        else:
            detect_risks_ai = False
    
    # Validate and process
    if st.button("🚀 Process Batch", type="primary", key="btn_process_batch"):
        # Validate ZIP
        is_valid, error_msg, pdf_files = validate_zip_upload(zip_file, max_files, max_size_mb)
        
        if not is_valid:
            st.error(f"❌ {error_msg}")
            return
        
        # Process batch
        st.markdown("---")
        st.subheader("⚙️ Processing Batch...")
        
        options = {
            "extract_requirements": extract_reqs,
            "detect_risks_pattern": detect_risks_pattern,
            "detect_risks_ai": detect_risks_ai,
            "generate_drafts": False
        }
        
        batch_results = process_batch(pdf_files, options)
        
        # Update usage
        st.session_state.batch_usage["batches_today"] += 1
        
        # Show results
        st.success(f"✅ Batch processing completed!")
        st.toast("✅ Batch processed!", icon="✅")
        st.balloons()
        
        render_batch_summary(batch_results)


def validate_zip_upload(zip_file, max_files: int, max_size_mb: int) -> tuple[bool, str, List]:
    """
    Validate ZIP file and extract PDF list.
    
    Returns:
        (is_valid, error_message, pdf_files)
    """
    import zipfile
    from io import BytesIO
    
    # Check file size
    zip_size_mb = zip_file.size / (1024 * 1024)
    if zip_size_mb > max_size_mb:
        return False, f"ZIP file too large ({zip_size_mb:.1f}MB). Maximum {max_size_mb}MB.", []
    
    # Try to open ZIP
    try:
        zip_bytes = BytesIO(zip_file.read())
        zip_ref = zipfile.ZipFile(zip_bytes)
    except zipfile.BadZipFile:
        return False, "Invalid ZIP file. Please upload a valid ZIP archive.", []
    
    # Extract PDF list
    pdf_files = []
    for file_info in zip_ref.filelist:
        # Skip directories and hidden files
        if file_info.is_dir() or file_info.filename.startswith('__MACOSX'):
            continue
        
        # Check if PDF
        if not file_info.filename.lower().endswith('.pdf'):
            logger.warning(f"Skipping non-PDF file: {file_info.filename}")
            continue
        
        # Extract file
        pdf_bytes = zip_ref.read(file_info.filename)
        
        # Skip empty files
        if len(pdf_bytes) == 0:
            logger.warning(f"Skipping empty file: {file_info.filename}")
            continue
        
        pdf_files.append({
            "filename": file_info.filename.split('/')[-1],  # Remove path
            "bytes": pdf_bytes,
            "size": len(pdf_bytes)
        })
    
    # Check PDF count
    if len(pdf_files) == 0:
        return False, "No valid PDF files found in ZIP.", []
    
    if len(pdf_files) > max_files:
        return False, f"Too many PDFs ({len(pdf_files)}). Maximum {max_files} for free tier.", []
    
    # Check for duplicate names
    filenames = [f["filename"] for f in pdf_files]
    if len(filenames) != len(set(filenames)):
        return False, "Duplicate file names detected in ZIP. Please rename files.", []
    
    return True, "", pdf_files


def process_batch(pdf_files: List[dict], options: dict) -> dict:
    """
    Process batch of PDFs.
    
    Args:
        pdf_files: List of {filename, bytes, size}
        options: Processing options dict
    
    Returns:
        batch_results dict
    """
    from services.pdf_extractor import PDFExtractor
    from services.requirement_extractor import RequirementExtractor
    from services.risk_detector import RiskDetector
    from services.llm_client import create_llm_client
    import time
    
    # Initialize services
    pdf_extractor = PDFExtractor()
    llm_client = create_llm_client() if options.get("extract_requirements") else None
    req_extractor = RequirementExtractor(llm_client) if llm_client else None
    risk_detector = RiskDetector(llm_client if options.get("detect_risks_ai") else None)
    
    # Setup progress tracking
    total_pdfs = len(pdf_files)
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Summary table placeholder
    summary_placeholder = st.empty()
    
    # Cancel button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("❌ Cancel Batch", key="btn_cancel_batch"):
            st.session_state.cancel_batch = True
            st.warning("⚠️ Batch processing cancelled")
            return None
    
    # Initialize results
    batch_results = []
    successful = 0
    failed = 0
    
    start_time = time.time()
    
    # Process each PDF
    for i, pdf_file in enumerate(pdf_files):
        # Check for cancellation
        if st.session_state.get("cancel_batch", False):
            st.session_state.cancel_batch = False
            break
        
        filename = pdf_file["filename"]
        
        # Update progress
        progress_bar.progress((i + 1) / total_pdfs)
        status_text.text(f"Processing {filename}... ({i+1}/{total_pdfs})")
        
        # Process single PDF
        try:
            pdf_start = time.time()
            
            # Create temp file for PDF bytes
            from io import BytesIO
            pdf_io = BytesIO(pdf_file["bytes"])
            
            # Extract text
            with st.spinner(f"📄 Extracting text from {filename}..."):
                text = pdf_extractor.extract_from_bytes(pdf_io)
            
            if not text or len(text.strip()) < 100:
                raise PDFError(f"No text extracted from {filename}")
            
            # Create RFP object
            rfp = RFP(
                file_name=filename,
                title=f"RFP - {filename.replace('.pdf', '')}",
                client_name="Unknown",  # User can edit later
                deadline=datetime.now() + timedelta(days=30),
                text=text,
                uploaded_at=datetime.now()
            )
            
            # Extract requirements
            requirements = []
            if options.get("extract_requirements") and req_extractor:
                with st.spinner(f"🤖 Extracting requirements from {filename}..."):
                    requirements = req_extractor.extract_requirements(text)
            
            # Detect risks
            risks = []
            if options.get("detect_risks_pattern"):
                with st.spinner(f"⚠️ Detecting risks in {filename}..."):
                    risks = risk_detector.detect_by_patterns(text)
            
            if options.get("detect_risks_ai") and risk_detector.llm_client:
                with st.spinner(f"🤖 AI risk detection for {filename}..."):
                    ai_risks = risk_detector.detect_by_ai(text)
                    # Merge and deduplicate
                    risks = risk_detector._deduplicate_risks(risks + ai_risks)
            
            pdf_end = time.time()
            processing_time = pdf_end - pdf_start
            
            # Store result
            result = {
                "rfp": rfp,
                "requirements": requirements,
                "risks": risks,
                "draft": None,
                "processing_time": processing_time,
                "status": "success",
                "error": None,
                "processed_at": datetime.now()
            }
            
            batch_results.append(result)
            successful += 1
            
            logger.info(f"Successfully processed {filename}: {len(requirements)} reqs, {len(risks)} risks")
        
        except Exception as e:
            logger.error(f"Failed to process {filename}: {e}", exc_info=True)
            
            # Store failed result
            result = {
                "rfp": RFP(
                    file_name=filename,
                    title=f"RFP - {filename.replace('.pdf', '')} [FAILED]",
                    client_name="Unknown",
                    deadline=datetime.now() + timedelta(days=30),
                    text="",
                    uploaded_at=datetime.now()
                ),
                "requirements": [],
                "risks": [],
                "draft": None,
                "processing_time": 0,
                "status": "failed",
                "error": str(e),
                "processed_at": datetime.now()
            }
            
            batch_results.append(result)
            failed += 1
        
        # Update summary table (live)
        update_summary_table(summary_placeholder, batch_results, total_pdfs, successful, failed)
    
    # Final progress
    progress_bar.progress(1.0)
    status_text.text("✅ Batch processing completed!")
    
    total_time = time.time() - start_time
    
    # Store in session state
    st.session_state.batch_rfps = batch_results
    st.session_state.batch_info = {
        "batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "uploaded_at": datetime.now(),
        "total_files": total_pdfs,
        "successful": successful,
        "failed": failed,
        "total_time": total_time,
        "options": options
    }
    
    return st.session_state.batch_info


def update_summary_table(placeholder, results: List[dict], total: int, successful: int, failed: int):
    """Update summary table with current results."""
    
    import pandas as pd
    
    if not results:
        return
    
    # Build dataframe
    rows = []
    for r in results:
        rows.append({
            "Filename": r["rfp"].file_name,
            "Status": "✅" if r["status"] == "success" else "❌",
            "Requirements": len(r["requirements"]) if r["status"] == "success" else "--",
            "Risks": len(r["risks"]) if r["status"] == "success" else "--",
            "Time (s)": f"{r['processing_time']:.1f}" if r["status"] == "success" else "--",
            "Error": r["error"] if r["status"] == "failed" else ""
        })
    
    df = pd.DataFrame(rows)
    
    # Add totals row
    if len(results) == total:
        avg_time = sum(r["processing_time"] for r in results if r["status"] == "success") / successful if successful > 0 else 0
        total_reqs = sum(len(r["requirements"]) for r in results if r["status"] == "success")
        total_risks = sum(len(r["risks"]) for r in results if r["status"] == "success")
        
        totals = pd.DataFrame([{
            "Filename": f"**Total: {total}**",
            "Status": f"**{successful}/{total}**",
            "Requirements": f"**{total_reqs}**",
            "Risks": f"**{total_risks}**",
            "Time (s)": f"**{avg_time:.1f}**",
            "Error": ""
        }])
        
        df = pd.concat([df, totals], ignore_index=True)
    
    # Render table
    placeholder.dataframe(df, use_container_width=True, hide_index=True)


def render_batch_summary(batch_info: dict):
    """Render batch summary with action buttons."""
    
    st.markdown("---")
    st.subheader("📊 Batch Summary")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total PDFs", batch_info["total_files"])
    col2.metric(
        "Successful",
        batch_info["successful"],
        delta=f"{batch_info['successful'] / batch_info['total_files'] * 100:.0f}%"
    )
    col3.metric("Failed", batch_info["failed"])
    col4.metric("Total Time", f"{batch_info['total_time']:.1f}s")
    
    # Action buttons
    st.markdown("### 🎯 Next Steps")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 View Batch Results", type="primary", use_container_width=True):
            st.switch_page("pages/5_📦_Batch_Results.py")
    
    with col2:
        # Export JSON
        json_data = export_batch_json(st.session_state.batch_rfps, batch_info)
        st.download_button(
            label="📥 Export JSON",
            data=json_data,
            file_name=f"{batch_info['batch_id']}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        # Export Excel
        excel_data = export_batch_excel(st.session_state.batch_rfps, batch_info)
        st.download_button(
            label="📊 Export Excel",
            data=excel_data,
            file_name=f"{batch_info['batch_id']}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col4:
        # Retry failed
        if batch_info["failed"] > 0:
            if st.button(f"🔄 Retry Failed ({batch_info['failed']})", use_container_width=True):
                retry_failed_pdfs()
```

### 2. Batch Results Page

```python
# pages/5_📦_Batch_Results.py

import streamlit as st
from typing import List, Dict
from models import RFP, Requirement, Risk

def main():
    """Batch results page."""
    
    st.title("📦 Batch Results")
    
    # Check if batch exists
    if "batch_rfps" not in st.session_state or not st.session_state.batch_rfps:
        st.warning("⚠️ No batch results found. Please upload and process a batch first.")
        
        if st.button("Go to Batch Upload"):
            st.switch_page("pages/1_📤_Upload_RFP.py")
        return
    
    batch_info = st.session_state.batch_info
    batch_rfps = st.session_state.batch_rfps
    
    # Summary
    st.markdown(f"**Batch ID:** `{batch_info['batch_id']}`")
    st.markdown(f"**Processed:** {batch_info['uploaded_at'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total RFPs", batch_info["total_files"])
    col2.metric("Successful", batch_info["successful"])
    col3.metric("Failed", batch_info["failed"])
    col4.metric("Avg Time", f"{batch_info['total_time'] / batch_info['total_files']:.1f}s")
    
    st.markdown("---")
    
    # Filters
    col1, col2 = st.columns([2, 1])
    
    with col1:
        filter_status = st.selectbox(
            "Filter by status",
            ["All", "Successful", "Failed"],
            key="filter_batch_status"
        )
    
    with col2:
        if st.button("🗑️ Clear Batch", key="btn_clear_batch"):
            if st.session_state.get("confirm_clear"):
                del st.session_state.batch_rfps
                del st.session_state.batch_info
                st.success("✅ Batch cleared")
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("⚠️ Click again to confirm")
    
    # Filter results
    filtered_rfps = batch_rfps
    if filter_status == "Successful":
        filtered_rfps = [r for r in batch_rfps if r["status"] == "success"]
    elif filter_status == "Failed":
        filtered_rfps = [r for r in batch_rfps if r["status"] == "failed"]
    
    # RFP cards
    st.markdown(f"### 📄 RFPs ({len(filtered_rfps)})")
    
    for i, rfp_data in enumerate(filtered_rfps):
        render_rfp_card(rfp_data, i)
    
    st.markdown("---")
    
    # Bulk actions
    st.markdown("### 🎯 Bulk Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export All to JSON", use_container_width=True):
            json_data = export_batch_json(batch_rfps, batch_info)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"{batch_info['batch_id']}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📊 Export All to Excel", use_container_width=True):
            excel_data = export_batch_excel(batch_rfps, batch_info)
            st.download_button(
                label="Download Excel",
                data=excel_data,
                file_name=f"{batch_info['batch_id']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col3:
        if batch_info["failed"] > 0:
            if st.button(f"🔄 Retry Failed ({batch_info['failed']})", use_container_width=True):
                retry_failed_pdfs()


def render_rfp_card(rfp_data: dict, index: int):
    """Render individual RFP card."""
    
    rfp = rfp_data["rfp"]
    status = rfp_data["status"]
    
    # Card container
    with st.expander(
        f"{'✅' if status == 'success' else '❌'} {rfp.file_name}",
        expanded=(index == 0)  # Expand first one
    ):
        if status == "failed":
            st.error(f"**Error:** {rfp_data['error']}")
            
            if st.button("🔄 Retry", key=f"retry_{index}"):
                # Retry this specific PDF
                st.info("Retrying... (not implemented yet)")
            return
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Requirements", len(rfp_data["requirements"]))
        col2.metric("Risks", len(rfp_data["risks"]))
        col3.metric("Processing Time", f"{rfp_data['processing_time']:.1f}s")
        
        # Details
        st.markdown("**RFP Details:**")
        st.markdown(f"• **Title:** {rfp.title}")
        st.markdown(f"• **Client:** {rfp.client_name}")
        st.markdown(f"• **Deadline:** {rfp.deadline.strftime('%Y-%m-%d')}")
        st.markdown(f"• **Text Length:** {len(rfp.text)} characters")
        
        # Requirements preview
        if rfp_data["requirements"]:
            with st.expander(f"📋 Requirements Preview ({len(rfp_data['requirements'])})"):
                for req in rfp_data["requirements"][:5]:
                    st.markdown(f"• **{req.category.value}:** {req.description[:100]}...")
                
                if len(rfp_data["requirements"]) > 5:
                    st.caption(f"... and {len(rfp_data['requirements']) - 5} more")
        
        # Risks preview
        if rfp_data["risks"]:
            with st.expander(f"⚠️ Risks Preview ({len(rfp_data['risks'])})"):
                for risk in rfp_data["risks"][:5]:
                    st.markdown(f"• **{risk.severity.value}:** {risk.clause_text[:100]}...")
                
                if len(rfp_data["risks"]) > 5:
                    st.caption(f"... and {len(rfp_data['risks']) - 5} more")
        
        # Actions
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👁️ View Details", key=f"view_{index}", use_container_width=True):
                # Load this RFP as current
                st.session_state.rfp = rfp
                st.session_state.requirements = rfp_data["requirements"]
                st.session_state.risks = rfp_data["risks"]
                st.session_state.draft = rfp_data["draft"]
                
                st.success(f"✅ Loaded {rfp.file_name}")
                st.info("Navigate to Requirements, Risks, or Draft pages to view/edit")
        
        with col2:
            # Export this RFP
            rfp_json = export_single_rfp_json(rfp_data)
            st.download_button(
                label="📥 Export JSON",
                data=rfp_json,
                file_name=f"{rfp.file_name.replace('.pdf', '')}_export.json",
                mime="application/json",
                key=f"export_{index}",
                use_container_width=True
            )
        
        with col3:
            if st.button("✍️ Generate Draft", key=f"draft_{index}", use_container_width=True):
                # Load RFP and navigate to Draft page
                st.session_state.rfp = rfp
                st.session_state.requirements = rfp_data["requirements"]
                st.session_state.risks = rfp_data["risks"]
                st.switch_page("pages/4_✍️_Draft_Generation.py")


if __name__ == "__main__":
    main()
```

### 3. Selector for Batch RFPs (in existing pages)

```python
# pages/2_📋_Requirements.py (add at top)

def render_batch_selector():
    """Render batch RFP selector if batch exists."""
    
    if "batch_rfps" not in st.session_state or not st.session_state.batch_rfps:
        return
    
    st.info("📦 Batch mode active. Select an RFP to view/edit:")
    
    rfp_options = ["Current RFP"] + [
        f"{r['rfp'].file_name} ({len(r['requirements'])} reqs)"
        for r in st.session_state.batch_rfps
        if r["status"] == "success"
    ]
    
    selected = st.selectbox(
        "Select RFP",
        rfp_options,
        key="batch_rfp_selector_requirements"
    )
    
    if selected != "Current RFP":
        # Load selected RFP
        index = rfp_options.index(selected) - 1
        rfp_data = st.session_state.batch_rfps[index]
        
        st.session_state.rfp = rfp_data["rfp"]
        st.session_state.requirements = rfp_data["requirements"]
        st.session_state.risks = rfp_data["risks"]
        st.session_state.draft = rfp_data["draft"]
        
        st.rerun()
```

## 📤 Export Functions

### JSON Export

```python
# src/utils/batch_export.py

import json
from typing import List, Dict
from models import RFP, Requirement, Risk
from datetime import datetime

def export_batch_json(batch_rfps: List[dict], batch_info: dict) -> str:
    """Export batch results to JSON."""
    
    export_data = {
        "batch_id": batch_info["batch_id"],
        "processed_at": batch_info["uploaded_at"].isoformat(),
        "total_files": batch_info["total_files"],
        "successful": batch_info["successful"],
        "failed": batch_info["failed"],
        "total_time": batch_info["total_time"],
        "options": batch_info["options"],
        "rfps": []
    }
    
    for rfp_data in batch_rfps:
        rfp_export = {
            "filename": rfp_data["rfp"].file_name,
            "status": rfp_data["status"],
            "processing_time": rfp_data["processing_time"],
            "processed_at": rfp_data["processed_at"].isoformat(),
            "error": rfp_data["error"],
            "rfp": rfp_data["rfp"].to_dict() if rfp_data["status"] == "success" else None,
            "requirements": [r.to_dict() for r in rfp_data["requirements"]],
            "risks": [r.to_dict() for r in rfp_data["risks"]],
            "draft": rfp_data["draft"].to_dict() if rfp_data["draft"] else None
        }
        
        export_data["rfps"].append(rfp_export)
    
    return json.dumps(export_data, indent=2, default=str)


def export_single_rfp_json(rfp_data: dict) -> str:
    """Export single RFP to JSON."""
    
    export_data = {
        "filename": rfp_data["rfp"].file_name,
        "exported_at": datetime.now().isoformat(),
        "rfp": rfp_data["rfp"].to_dict(),
        "requirements": [r.to_dict() for r in rfp_data["requirements"]],
        "risks": [r.to_dict() for r in rfp_data["risks"]],
        "draft": rfp_data["draft"].to_dict() if rfp_data["draft"] else None
    }
    
    return json.dumps(export_data, indent=2, default=str)
```

### Excel Export

```python
# src/utils/batch_export.py (continued)

import pandas as pd
from io import BytesIO

def export_batch_excel(batch_rfps: List[dict], batch_info: dict) -> bytes:
    """Export batch results to Excel with multiple sheets."""
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet 1: Summary
        summary_data = []
        for rfp_data in batch_rfps:
            summary_data.append({
                "Filename": rfp_data["rfp"].file_name,
                "Status": rfp_data["status"],
                "Requirements": len(rfp_data["requirements"]),
                "Risks": len(rfp_data["risks"]),
                "Processing Time (s)": rfp_data["processing_time"],
                "Error": rfp_data["error"] or ""
            })
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name="Summary", index=False)
        
        # Sheet 2: All Requirements
        all_reqs = []
        for rfp_data in batch_rfps:
            if rfp_data["status"] == "success":
                for req in rfp_data["requirements"]:
                    all_reqs.append({
                        "RFP": rfp_data["rfp"].file_name,
                        "Description": req.description,
                        "Category": req.category.value,
                        "Priority": req.priority.value,
                        "Confidence": f"{req.confidence:.0%}",
                        "Page": req.page_number,
                        "Verified": req.verified
                    })
        
        if all_reqs:
            df_reqs = pd.DataFrame(all_reqs)
            df_reqs.to_excel(writer, sheet_name="Requirements", index=False)
        
        # Sheet 3: All Risks
        all_risks = []
        for rfp_data in batch_rfps:
            if rfp_data["status"] == "success":
                for risk in rfp_data["risks"]:
                    all_risks.append({
                        "RFP": rfp_data["rfp"].file_name,
                        "Clause": risk.clause_text[:100],
                        "Category": risk.category.value,
                        "Severity": risk.severity.value,
                        "Confidence": f"{risk.confidence:.0%}",
                        "Page": risk.page_number,
                        "Acknowledged": risk.acknowledged
                    })
        
        if all_risks:
            df_risks = pd.DataFrame(all_risks)
            df_risks.to_excel(writer, sheet_name="Risks", index=False)
        
        # Sheet 4: Batch Info
        info_data = {
            "Metric": [
                "Batch ID",
                "Processed At",
                "Total Files",
                "Successful",
                "Failed",
                "Total Time (s)",
                "Avg Time (s)"
            ],
            "Value": [
                batch_info["batch_id"],
                batch_info["uploaded_at"].strftime("%Y-%m-%d %H:%M:%S"),
                batch_info["total_files"],
                batch_info["successful"],
                batch_info["failed"],
                f"{batch_info['total_time']:.1f}",
                f"{batch_info['total_time'] / batch_info['total_files']:.1f}"
            ]
        }
        
        df_info = pd.DataFrame(info_data)
        df_info.to_excel(writer, sheet_name="Batch Info", index=False)
    
    output.seek(0)
    return output.read()
```

## 🗂️ File Structure

```
src/
├── services/
│   └── batch_processor.py          # NEW: Batch processing logic
│       ├── process_batch()
│       ├── process_single_pdf()
│       └── retry_failed_pdfs()
│
├── utils/
│   ├── batch_export.py             # NEW: Export functions
│   │   ├── export_batch_json()
│   │   ├── export_single_rfp_json()
│   │   └── export_batch_excel()
│   │
│   └── zip_validator.py            # NEW: ZIP validation
│       ├── validate_zip_upload()
│       └── extract_pdfs_from_zip()
│
pages/
├── 1_📤_Upload_RFP.py             # MODIFIED: Add batch tab
│   ├── render_single_upload()     (existing)
│   └── render_batch_upload()      (new)
│
├── 5_📦_Batch_Results.py          # NEW: Batch results page
│   ├── render_rfp_card()
│   ├── render_batch_selector()
│   └── export functions
│
├── 2_📋_Requirements.py           # MODIFIED: Add batch selector
├── 3_⚠️_Risk_Analysis.py         # MODIFIED: Add batch selector
└── 4_✍️_Draft_Generation.py      # MODIFIED: Add batch selector

tests/
├── test_services/
│   └── test_batch_processor.py    # NEW: Batch processor tests
│
├── test_utils/
│   ├── test_batch_export.py       # NEW: Export tests
│   └── test_zip_validator.py      # NEW: ZIP validation tests
│
└── test_integration/
    └── test_batch_upload.py       # NEW: E2E batch tests
```

## 🧪 Testing Strategy

### Unit Tests

```python
# tests/test_services/test_batch_processor.py

def test_process_batch_success(mock_pdfs, mock_llm):
    """Test successful batch processing."""
    results = process_batch(mock_pdfs, {"extract_requirements": True})
    
    assert len(results) == len(mock_pdfs)
    assert all(r["status"] == "success" for r in results)
    assert all(len(r["requirements"]) > 0 for r in results)

def test_process_batch_with_failures(mock_pdfs_with_corrupt):
    """Test batch continues on individual failures."""
    results = process_batch(mock_pdfs_with_corrupt, {})
    
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]
    
    assert len(successful) == 2
    assert len(failed) == 1
    assert failed[0]["error"] is not None

def test_validate_zip_exceeds_limit():
    """Test ZIP with too many PDFs."""
    zip_with_6_pdfs = create_mock_zip(6)
    
    is_valid, error, _ = validate_zip_upload(zip_with_6_pdfs, max_files=5, max_size_mb=100)
    
    assert not is_valid
    assert "Too many PDFs" in error

def test_export_batch_json(mock_batch_results):
    """Test JSON export."""
    json_str = export_batch_json(mock_batch_results, mock_batch_info)
    
    data = json.loads(json_str)
    
    assert data["batch_id"] == mock_batch_info["batch_id"]
    assert len(data["rfps"]) == len(mock_batch_results)

def test_export_batch_excel(mock_batch_results):
    """Test Excel export."""
    excel_bytes = export_batch_excel(mock_batch_results, mock_batch_info)
    
    df_summary = pd.read_excel(BytesIO(excel_bytes), sheet_name="Summary")
    
    assert len(df_summary) == len(mock_batch_results)
    assert "Filename" in df_summary.columns
```

### Integration Tests

```python
# tests/test_integration/test_batch_upload.py

def test_upload_and_process_batch_e2e(test_client):
    """End-to-end test: Upload ZIP, process, view results."""
    
    # 1. Create ZIP with 3 PDFs
    zip_file = create_test_zip([
        "sample_rfp_1.pdf",
        "sample_rfp_2.pdf",
        "sample_rfp_3.pdf"
    ])
    
    # 2. Upload and process
    with patch('services.llm_client.create_llm_client') as mock_llm:
        mock_llm.return_value = Mock()
        
        batch_results = process_batch(
            extract_pdfs_from_zip(zip_file),
            {"extract_requirements": True, "detect_risks_pattern": True}
        )
    
    # 3. Verify results
    assert len(batch_results) == 3
    assert all(r["status"] == "success" for r in batch_results)
    
    # 4. Verify session state
    assert "batch_rfps" in st.session_state
    assert len(st.session_state.batch_rfps) == 3
    
    # 5. Test export
    json_str = export_batch_json(batch_results, st.session_state.batch_info)
    assert json_str is not None
    
    excel_bytes = export_batch_excel(batch_results, st.session_state.batch_info)
    assert len(excel_bytes) > 0

def test_batch_with_corrupt_pdf(test_client):
    """Test batch continues when one PDF is corrupt."""
    
    zip_file = create_test_zip([
        "valid_rfp_1.pdf",
        "corrupt_rfp.pdf",  # Corrupt file
        "valid_rfp_2.pdf"
    ])
    
    batch_results = process_batch(
        extract_pdfs_from_zip(zip_file),
        {"extract_requirements": True}
    )
    
    successful = [r for r in batch_results if r["status"] == "success"]
    failed = [r for r in batch_results if r["status"] == "failed"]
    
    assert len(successful) == 2
    assert len(failed) == 1
    assert "corrupt_rfp.pdf" in failed[0]["rfp"].file_name
```

## 📊 Success Criteria

- [ ] Batch upload tab added to Upload RFP page
- [ ] ZIP validation: max files, size, PDF only, no duplicates
- [ ] Sequential processing with progress bar and status text
- [ ] Live-updating summary table during processing
- [ ] Error handling: continue on failures, log errors
- [ ] Retry button for failed PDFs
- [ ] Cancel batch button (with confirmation)
- [ ] Batch Results page with individual RFP cards
- [ ] Export batch to JSON (consolidated format)
- [ ] Export batch to Excel (4 sheets: Summary, Reqs, Risks, Info)
- [ ] Batch selector dropdown in Requirements/Risk/Draft pages
- [ ] Usage tracking: 1 batch/day limit for free tier
- [ ] Session state persistence until "Clear Batch"
- [ ] All unit tests pass with >80% coverage
- [ ] Integration tests for success and failure scenarios
- [ ] Performance: <3 min per PDF, <15 min total timeout
- [ ] Epic 9 error handling integrated throughout

## 🔗 Related Documentation

- **Epic 9:** Error Handling & Loading States (used throughout)
- **PRD:** Batch processing requirements
- **Python Practices:** `.cursor/rules/python-practices.mdc`

## 📝 Notes

- **Scalability:** Sequential processing is MVP; parallel processing for Epic 11+
- **Free tier limits:** 5 PDFs/batch, 1 batch/day (configurable for paid)
- **No drafts in batch:** Too slow/expensive; user generates individually
- **ZIP format:** Standard Python `zipfile` library, widely supported
- **Excel export:** Requires `openpyxl` or `xlsxwriter` (add to requirements.txt)
- **Memory:** Be cautious with large PDFs; may need streaming for future

## 🎯 Next Steps After Epic 10

1. **Epic 11:** Batch optimization (parallel processing, caching)
2. **Epic 12:** RFP comparison and analytics (compare batch results)
3. **Epic 13:** User accounts and persistent storage (save batches long-term)

---

**Estimated Total Effort:** 2-3 days (17-23 hours)  
**Sprint Assignment:** TBD (Sprint 6 or 7)  
**Priority:** Medium-High (productivity multiplier)

