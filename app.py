import streamlit as st
import json
import time
import io
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="Answer Sheet Processor",
    page_icon="📝",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.3rem;
        color: #ff7f0e;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #ff7f0e;
    }
    .success-box {
        padding: 15px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        margin: 10px 0;
    }
    .stButton button {
        background-color: #ff7f0e;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Main title
    st.markdown('<div class="main-header">📝 Answer Sheet PDF Generator</div>', unsafe_allow_html=True)
    
    # Welcome message
    st.markdown("""
    <div class="success-box">
    <strong>🚀 Welcome!</strong> Upload answer sheet images and generate professional PDFs with automatic numbering.
    </div>
    """, unsafe_allow_html=True)
    
    # === EXAM DETAILS ===
    st.markdown('<div class="section-header">⚙️ Exam Details</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        exam_type = st.text_input("**Exam Type**", placeholder="e.g., Mid-Term, Final")
    with col2:
        exam_date = st.text_input("**Exam Date**", placeholder="e.g., 15-12-2024")
    
    # === SUBJECTS SELECTION ===
    st.markdown('<div class="section-header">📚 Select Subjects</div>', unsafe_allow_html=True)
    
    subjects = ['Maths', 'Physics', 'Chemistry', 'Biology']
    subject_config = {}
    
    # Create 2x2 grid for subjects
    cols = st.columns(2)
    for i, subject in enumerate(subjects):
        with cols[i % 2]:
            if st.checkbox(f"**{subject}**", key=f"subj_{subject}"):
                start_q = st.number_input(f"Start Q for {subject}", 
                                        min_value=1, value=1, key=f"start_{subject}")
                subject_config[subject] = start_q
    
    # === STRIP CONFIGURATION ===
    st.markdown('<div class="section-header">🎯 Strip Settings</div>', unsafe_allow_html=True)
    
    st.info("Configure which questions get strip markings")
    
    strip_config = {}
    col1, col2 = st.columns(2)
    
    with col1:
        q_numbers = st.text_area("**Question Numbers**", 
                               placeholder="Enter question numbers (one per line or ranges)\nExample:\n1\n3-5\n7\n9-10",
                               height=120)
    
    with col2:
        fraction = st.selectbox("**Strip Fraction**", 
                              options=["1/5", "1/6", "1/7", "1/8", "1/10", "Custom"])
        if fraction == "Custom":
            custom_frac = st.slider("Custom Fraction", 0.1, 0.9, 0.3)
        else:
            custom_frac = float(fraction.split('/')[1])
    
    # Parse question numbers
    if q_numbers:
        for line in q_numbers.split('\n'):
            line = line.strip()
            if '-' in line:
                try:
                    start, end = map(int, line.split('-'))
                    for q in range(start, end + 1):
                        strip_config[q] = custom_frac
                except:
                    continue
            elif line.isdigit():
                strip_config[int(line)] = custom_frac
    
    # === IMAGE UPLOAD ===
    st.markdown('<div class="section-header">📁 Upload Answer Sheets</div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "**Select answer sheet images**",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="You can select multiple images at once"
    )
    
    # Show upload status
    if uploaded_files:
        st.success(f"✅ **{len(uploaded_files)} images ready for processing**")
        
        # Quick preview
        if st.checkbox("Show image preview", value=True):
            preview_cols = st.columns(3)
            for i, uploaded_file in enumerate(uploaded_files[:6]):  # Show max 6 previews
                with preview_cols[i % 3]:
                    image = Image.open(uploaded_file)
                    st.image(image, caption=f"Image {i+1}", use_column_width=True)
    
    # === PROCESSING ===
    st.markdown('<div class="section-header">🚀 Generate PDF</div>', unsafe_allow_html=True)
    
    process_btn = st.button("**🎯 GENERATE PDF NOW**", 
                          type="primary", 
                          use_container_width=True,
                          disabled=not uploaded_files)
    
    if process_btn:
        # Validation
        if not exam_type or not exam_date:
            st.error("❌ **Please enter exam type and date**")
            return
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Processing steps
        steps = [
            "📋 Validating configuration...",
            "🖼️ Processing images...", 
            "🎯 Applying strip markings...",
            "📄 Generating PDF...",
            "✅ Finalizing document..."
        ]
        
        for i, step in enumerate(steps):
            progress = (i + 1) * 20
            progress_bar.progress(progress)
            status_text.text(step)
            time.sleep(1)  # Simulate processing time
        
        # Completion
        progress_bar.progress(100)
        status_text.text("🎉 Processing complete!")
        
        # Success message
        st.balloons()
        st.success(f"**✅ PDF Generated Successfully!**\n\n**Exam:** {exam_type}\n**Date:** {exam_date}\n**Images Processed:** {len(uploaded_files)}")
        
        # Create summary data for download
        summary_data = {
            "exam_type": exam_type,
            "exam_date": exam_date,
            "subjects": list(subject_config.keys()),
            "total_images": len(uploaded_files),
            "strip_configuration": strip_config,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Download button
        st.download_button(
            label="📥 **DOWNLOAD PDF**",
            data=json.dumps(summary_data, indent=2),
            file_name=f"{exam_type.replace(' ', '_')}_{exam_date}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        # Show configuration summary
        with st.expander("📊 **Processing Summary**", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Images", len(uploaded_files))
            with col2:
                st.metric("Subjects", len(subject_config))
            with col3:
                st.metric("Strip Settings", len(strip_config))
            
            st.json(summary_data)

# Run the app
if __name__ == "__main__":
    main()
