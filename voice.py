from gtts import gTTS
import os
import tempfile


def generate_voice_report(diagnosis, severity, health_tips, patient_name,
                           clinical_explanation="", key_findings=None,
                           recommended_followup=""):
    """
    Convert the full medical report to speech using Google Text-to-Speech.

    Now includes clinical explanation and key findings for a much more
    informative and industry-grade audio report.

    Returns: (audio_file_path, report_text_string)
    """
    key_findings = key_findings or []

    report_text = f"Hello {patient_name}, this is your medical analysis report.\n\n"

    report_text += f"Diagnosis: {diagnosis}.\n"
    report_text += f"Severity level: {severity} percent.\n\n"

    if clinical_explanation:
        report_text += (
            "Clinical explanation from the AI radiologist:\n"
            f"{clinical_explanation}\n\n"
        )

    if key_findings:
        report_text += "Key findings identified in your image:\n"
        for i, finding in enumerate(key_findings, 1):
            report_text += f"Finding {i}: {finding}.\n"
        report_text += "\n"

    if health_tips:
        report_text += "Health recommendations for your recovery:\n"
        for i, tip in enumerate(health_tips, 1):
            # Strip emoji prefix for clean TTS
            clean_tip = tip.lstrip("✓⚠ ").strip()
            report_text += f"Tip {i}: {clean_tip}.\n"
        report_text += "\n"

    if recommended_followup:
        report_text += f"Recommended next step: {recommended_followup}\n\n"

    report_text += (
        "Important disclaimer: This AI analysis is for informational purposes only "
        "and must be reviewed by a licensed physician before any clinical decision is made. "
        "If your symptoms worsen or you experience an emergency, please seek immediate medical care.\n\n"
        f"Thank you for using Medical Assistant, {patient_name}. Wishing you a speedy recovery."
    )

    try:
        tts = gTTS(text=report_text, lang='en', slow=False)
        audio_path = os.path.join(tempfile.gettempdir(), "medical_report.mp3")
        tts.save(audio_path)
        return audio_path, report_text
    except Exception as e:
        print(f"Error generating voice: {e}")
        return None, None


def generate_text_report(diagnosis, severity, health_tips, confidence,
                          clinical_explanation="", key_findings=None,
                          modality="", region="", recommended_followup="",
                          image_quality=""):
    """
    Generate a formatted plain-text report for display and download.
    Includes all new Claude Vision fields.
    """
    key_findings = key_findings or []

    severity_emoji = (
        "🟢" if severity == 0 else
        "🟡" if severity < 30 else
        "🟠" if severity < 60 else
        "🔴" if severity < 80 else
        "🚨"
    )

    lines = [
        "╔══════════════════════════════════════════════════════════╗",
        "║              MEDICAL ANALYSIS REPORT                    ║",
        "╠══════════════════════════════════════════════════════════╣",
        f"║  Diagnosis:      {diagnosis:<40}║",
    ]

    if modality:
        lines.append(f"║  Modality:       {modality:<40}║")
    if region:
        lines.append(f"║  Region:         {region:<40}║")
    if image_quality:
        lines.append(f"║  Image Quality:  {image_quality:<40}║")

    lines += [
        f"║  Severity:       {severity_emoji} {severity}%{'':<36}║",
        f"║  AI Confidence:  {confidence}%{'':<39}║",
        "╠══════════════════════════════════════════════════════════╣",
    ]

    if clinical_explanation:
        lines.append("║  CLINICAL EXPLANATION                                    ║")
        lines.append("╠══════════════════════════════════════════════════════════╣")
        # Word-wrap to 56 chars
        words = clinical_explanation.split()
        line_buf = ""
        for word in words:
            if len(line_buf) + len(word) + 1 <= 56:
                line_buf = (line_buf + " " + word).strip()
            else:
                lines.append(f"║  {line_buf:<56}║")
                line_buf = word
        if line_buf:
            lines.append(f"║  {line_buf:<56}║")

    if key_findings:
        lines.append("╠══════════════════════════════════════════════════════════╣")
        lines.append("║  KEY FINDINGS                                            ║")
        lines.append("╠══════════════════════════════════════════════════════════╣")
        for finding in key_findings:
            lines.append(f"║  • {finding:<54}║")

    lines.append("╠══════════════════════════════════════════════════════════╣")
    lines.append("║  HEALTH RECOMMENDATIONS                                  ║")
    lines.append("╠══════════════════════════════════════════════════════════╣")

    for tip in health_tips:
        lines.append(f"║  {tip:<56}║")

    if recommended_followup:
        lines.append("╠══════════════════════════════════════════════════════════╣")
        lines.append("║  RECOMMENDED NEXT STEPS                                  ║")
        lines.append("╠══════════════════════════════════════════════════════════╣")
        lines.append(f"║  {recommended_followup:<56}║")

    lines += [
        "╠══════════════════════════════════════════════════════════╣",
        "║  ⚠ DISCLAIMER: AI analysis only. Consult a physician.   ║",
        "╚══════════════════════════════════════════════════════════╝",
    ]

    return "\n".join(lines)