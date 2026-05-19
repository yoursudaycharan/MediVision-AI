import streamlit as st
import os
import pandas as pd
from datetime import datetime, time
import base64
from PIL import Image

# Import our custom modules
from database import init_database, add_patient, save_medical_record, get_patient_records, add_medicine, get_patient_medicines
from ai_model import analyzer
from voice import generate_voice_report, generate_text_report
from reminders import MedicineReminder

# Page configuration
st.set_page_config(
    page_title="Medical Assistant",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if 'patient_id' not in st.session_state:
    st.session_state.patient_id = None
if 'patient_name' not in st.session_state:
    st.session_state.patient_name = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Initialize database
init_database()

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .severity-normal { color: #2ECC71; }
    .severity-mild { color: #F1C40F; }
    .severity-moderate { color: #E67E22; }
    .severity-severe { color: #E74C3C; }
    .severity-critical { color: #C0392B; font-weight: bold; }
    .tip-card {
    background: #1E293B;
    color: white;
    padding: 1rem;
    border-radius: 12px;
    border-left: 5px solid #00D4AA;
    margin: 0.7rem 0;
    font-size: 16px;
    font-weight: 500;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
    .warning-card {
    background: #3B1F1F;
    color: white;
    padding: 1rem;
    border-radius: 12px;
    border-left: 5px solid #FF4B4B;
    margin: 0.7rem 0;
    font-size: 16px;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 Medical Image Analysis & Health Assistant</h1>
        <p>AI-Powered Health Analysis • Voice Reports • Medicine Reminders</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["🏠 Home", "📤 Upload & Analyze", "📋 Medical History", "💊 Medicine Reminders", "📊 Recovery Progress", "🗣️ Voice Reports"]
    )
    
    if page == "🏠 Home":
        show_home_page()
    elif page == "📤 Upload & Analyze":
        show_upload_page()
    elif page == "📋 Medical History":
        show_history_page()
    elif page == "💊 Medicine Reminders":
        show_reminders_page()
    elif page == "📊 Recovery Progress":
        show_progress_page()
    elif page == "🗣️ Voice Reports":
        show_voice_page()

def show_home_page():
    """Display home page with overview"""
    st.header("Welcome to Medical Assistant! 👋")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📤", "Upload medical images for AI analysis", "")
    
    with col2:
        st.metric("💊", "Set medicine reminders", "")
    
    with col3:
        st.metric("🗣️", "Listen to reports with voice", "")
    
    st.markdown("---")
    
    st.subheader("🚀 How to Get Started")
    
    st.markdown("""
    **Step 1: Upload Medical Image**
    - Go to "Upload & Analyze" section
    - Upload your X-ray, MRI, CT scan, or other medical images
    
    **Step 2: Get AI Analysis**
    - Our AI will analyze your image
    - Get instant diagnosis and severity assessment
    
    **Step 3: Follow Health Tips**
    - Receive personalized recovery recommendations
    - Follow the suggested health tips
    
    **Step 4: Set Reminders**
    - Add your medicines with reminder times
    - Never miss a dose!
    
    **Step 5: Listen to Reports**
    - Generate voice reports for easy understanding
    - Perfect for elderly patients
    """)
    
    st.info("ℹ️ This is a demo application. Always consult healthcare professionals for medical advice.")

def show_upload_page():
    """Handle image upload and analysis"""
    st.header("📤 Upload Medical Image for Analysis")
    
    # Patient registration (first time)
    if st.session_state.patient_id is None:
        with st.form("patient_form"):
            st.subheader("👤 Patient Registration")
            name = st.text_input("Patient Name", placeholder="Enter your name")
            age = st.number_input("Age", min_value=1, max_value=120, value=30)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            phone = st.text_input("Phone Number", placeholder="Enter phone number")
            
            submitted = st.form_submit_button("Register & Continue")
            
            if submitted and name:
                patient_id = add_patient(name, age, gender, phone)
                st.session_state.patient_id = patient_id
                st.session_state.patient_name = name
                st.success(f"✅ Registered successfully! Welcome, {name}!")
                st.rerun()
    else:
        st.success(f"👤 Logged in as: {st.session_state.patient_name}")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a medical image",
            type=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'dicom'],
            help="Supported formats: X-ray, MRI, CT Scan, Ultrasound images"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📷 Uploaded Image")
                st.image(uploaded_file, caption="Medical Image", use_container_width=True)
                
                # Analysis button
                if st.button("🔍 Analyze Image", type="primary", use_container_width=True):
                    with st.spinner("Analyzing image... Please wait..."):
                        # Save uploaded file
                        upload_dir = "uploads"
                        os.makedirs(upload_dir, exist_ok=True)
                        
                        file_path = os.path.join(upload_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Run AI analysis
                        result = analyzer.analyze_image(file_path)
                        
                        if result["success"]:
                            # Save to database
                            health_tips_text = "\n".join(result["health_tips"])
                            record_id = save_medical_record(
                                st.session_state.patient_id,
                                file_path,
                                result["diagnosis"],
                                result["severity"],
                                health_tips_text
                            )
                            
                            # Store result in session
                            st.session_state.last_result = result
                            st.session_state.last_record_id = record_id
                            st.success("✅ Analysis complete!")
                            st.rerun()
                        else:
                            st.error(f"❌ Analysis failed: {result['error']}")
            
            with col2:
                st.subheader("📊 Analysis Results")
                
                if 'last_result' in st.session_state:
                    result = st.session_state.last_result

                    # ── Diagnosis header ──────────────────────────────────
                    st.markdown(f"### 🎯 Diagnosis: **{result['diagnosis']}**")

                    # Modality & region badges
                    modality = result.get('modality', '')
                    region   = result.get('region', '')
                    if modality or region:
                        st.markdown(
                            f"🩻 **Modality:** {modality} &nbsp;|&nbsp; 📍 **Region:** {region}",
                            unsafe_allow_html=True
                        )

                    # ── Severity meter ────────────────────────────────────
                    severity = result['severity']
                    if severity == 0:
                        severity_class, emoji = "severity-normal", "🟢"
                    elif severity < 30:
                        severity_class, emoji = "severity-mild", "🟡"
                    elif severity < 60:
                        severity_class, emoji = "severity-moderate", "🟠"
                    elif severity < 80:
                        severity_class, emoji = "severity-severe", "🔴"
                    else:
                        severity_class, emoji = "severity-critical", "🚨"

                    st.markdown(
                        f'<p class="{severity_class}"><h2>{emoji} Severity: {severity}%</h2>'
                        f'<h4>{result["severity_text"]}</h4>'
                        f'<p>AI Confidence: {result["confidence"]}%</p></p>',
                        unsafe_allow_html=True
                    )
                    st.progress(severity / 100)

                    # ── Image quality ────────────────────────────────────
                    iq = result.get('image_quality', '')
                    if iq:
                        iq_color = {"Good": "✅", "Moderate": "🟡", "Poor": "🔴"}.get(iq, "ℹ️")
                        st.caption(f"{iq_color} Image Quality: **{iq}**")

                    # ── Clinical Explanation ─────────────────────────────
                    explanation = result.get('clinical_explanation', '')
                    if explanation:
                        st.markdown("---")
                        st.markdown("### 🔬 Clinical Explanation")
                        st.info(explanation)

                    # ── Key Findings ─────────────────────────────────────
                    key_findings = result.get('key_findings', [])
                    if key_findings:
                        st.markdown("### 📋 Key Findings")
                        for finding in key_findings:
                            st.markdown(f"- {finding}")

                    # ── Health Recommendations ───────────────────────────
                    st.markdown("---")
                    st.markdown("### 💡 Health Recommendations")
                    for tip in result['health_tips']:
                        if tip.startswith("⚠"):
                            st.markdown(f'<div class="warning-card">{tip}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="tip-card">{tip}</div>', unsafe_allow_html=True)

                    # ── Recommended Follow-up ────────────────────────────
                    followup = result.get('recommended_followup', '')
                    if followup:
                        st.markdown("---")
                        st.markdown("### 🏥 Recommended Next Steps")
                        st.success(followup)

                    # ── Disclaimer ───────────────────────────────────────
                    st.markdown("---")
                    st.warning(
                        result.get(
                            'disclaimer',
                            "⚠️ This AI analysis is for informational purposes only. "
                            "Always consult a licensed physician before making clinical decisions."
                        )
                    )

                    # ── Text Report ──────────────────────────────────────
                    st.markdown("---")
                    st.subheader("📝 Full Text Report")
                    report = generate_text_report(
                        result['diagnosis'],
                        result['severity'],
                        result['health_tips'],
                        result['confidence']
                    )
                    st.code(report)

                else:
                    st.info("👆 Click 'Analyze Image' to get your results")

def show_history_page():
    """Display medical history"""
    st.header("📋 Medical History")
    
    if st.session_state.patient_id is None:
        st.warning("Please register first in the Upload section")
        return
    
    records = get_patient_records(st.session_state.patient_id)
    
    if records:
        # Convert to DataFrame for display
        df = pd.DataFrame(records, columns=[
            "ID", "Patient ID", "Image Path", "Diagnosis", 
            "Severity", "Health Tips", "Date"
        ])
        
        # Format date
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(df[['Date', 'Diagnosis', 'Severity']], use_container_width=True)
        
        # Show detailed records
        st.markdown("---")
        for idx, row in df.iterrows():
            with st.expander(f"📄 Record from {row['Date']} - {row['Diagnosis']}"):
                st.write(f"**Severity:** {row['Severity']}%")
                st.write(f"**Diagnosis:** {row['Diagnosis']}")
                st.write("**Health Tips:**")
                st.text(row['Health Tips'])
    else:
        st.info("No medical records yet. Upload an image to get started!")

def show_reminders_page():
    """Medicine reminders page"""
    st.header("💊 Medicine Reminders")
    
    if st.session_state.patient_id is None:
        st.warning("Please register first in the Upload section")
        return
    
    # Add new medicine
    with st.form("medicine_form"):
        st.subheader("➕ Add New Medicine")
        
        col1, col2 = st.columns(2)
        
        with col1:
            medicine_name = st.text_input("Medicine Name", placeholder="e.g., Aspirin")
            dosage = st.text_input("Dosage", placeholder="e.g., 500mg")
        
        with col2:
            frequency = st.selectbox("Frequency", ["Once daily", "Twice daily", "Three times daily", "Every 8 hours"])
            reminder_time = st.time_input("Reminder Time", time(9, 0))
        
        start_date = st.date_input("Start Date", datetime.now())
        end_date = st.date_input("End Date (optional)", None)
        
        if st.form_submit_button("Add Reminder"):
            add_medicine(
                st.session_state.patient_id,
                medicine_name,
                dosage,
                frequency,
                reminder_time.strftime("%H:%M"),
                start_date.isoformat(),
                end_date.isoformat() if end_date else None
            )
            st.success(f"✅ Added reminder for {medicine_name}!")
            st.rerun()
    
    # Display current medicines
    st.markdown("---")
    st.subheader("📋 Your Medicines")
    
    medicines = get_patient_medicines(st.session_state.patient_id)
    
    if medicines:
        for med in medicines:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    **💊 {med[2]}** - {med[3]}
                    
                    Frequency: {med[4]} | Time: ⏰ {med[6]}
                    """)
                
                with col2:
                    if st.button(f"✓ Took it", key=f"took_{med[0]}"):
                        st.balloons()
                        st.success(f"Great job taking {med[2]}! 🎉")
    else:
        st.info("No medicines added yet. Add your first reminder above!")

def show_progress_page():
    """Show recovery progress over time"""
    st.header("📊 Recovery Progress")
    
    if st.session_state.patient_id is None:
        st.warning("Please register first in the Upload section")
        return
    
    records = get_patient_records(st.session_state.patient_id)
    
    if len(records) >= 2:
        # Create progress data
        dates = [datetime.strptime(r[4], '%Y-%m-%d %H:%M:%S') for r in records]
        severities = [r[5] for r in records]
        
        # Create chart
        import plotly.express as px
        
        df = pd.DataFrame({
            'Date': dates,
            'Severity': severities
        })
        
        fig = px.line(df, x='Date', y='Severity', title='Health Progress Over Time',
                     markers=True, labels={'Severity': 'Disease Severity (%)'})
        fig.update_layout(yaxis_range=[0, 100])
        
        st.plotly_chart(fig)
        
        # Progress summary
        first_severity = severities[-1]
        last_severity = severities[0]
        improvement = first_severity - last_severity
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Initial Severity", f"{first_severity}%")
        
        with col2:
            st.metric("Current Severity", f"{last_severity}%")
        
        with col3:
            st.metric("Improvement", f"{improvement}%", 
                     delta="Better!" if improvement > 0 else "Monitor closely")
    
    elif len(records) == 1:
        st.info("📈 Keep uploading images to track your progress over time!")
    else:
        st.info("No data for progress tracking yet. Upload an image to get started!")

def show_voice_page():
    """Generate and play voice reports"""
    st.header("🗣️ Voice Reports")
    
    if 'last_result' not in st.session_state:
        st.info("📤 Please upload and analyze an image first to generate a voice report!")
        return
    
    result = st.session_state.last_result
    
    st.subheader("📝 Report Content")
    report = generate_text_report(
        result['diagnosis'],
        result['severity'],
        result['health_tips'],
        result['confidence']
    )
    st.code(report)
    
    st.markdown("---")
    
    # Generate voice report
    if st.button("🔊 Generate Voice Report", type="primary"):
        with st.spinner("Generating voice report..."):
            audio_path, text = generate_voice_report(
                result['diagnosis'],
                result['severity'],
                result['health_tips'],
                st.session_state.patient_name
            )
            
            if audio_path:
                st.success("✅ Voice report generated!")
                
                # Play audio
                st.audio(audio_path, format='audio/mp3')
                
                # Download button
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()
                    st.download_button(
                        label="📥 Download Voice Report",
                        data=audio_bytes,
                        file_name="medical_report.mp3",
                        mime="audio/mp3"
                    )
            else:
                st.error("Failed to generate voice report")

if __name__ == "__main__":
    main()