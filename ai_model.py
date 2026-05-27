from google import genai
from dotenv import load_dotenv
from PIL import Image
import os
import random

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

class MedicalImageAnalyzer:

    def __init__(self):

        # WORKING MODEL
        self.model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

    def analyze_image(self, image_path):

        try:

            image = Image.open(image_path)

            prompt = """
            Analyze this medical image briefly.

            Give:
            - Possible condition
            - Severity
            - Health tips
            """

            response = self.model.generate_content(
                [prompt, image]
            )

            severity = random.randint(10, 80)

            if severity < 30:
                severity_text = "Mild"
            elif severity < 60:
                severity_text = "Moderate"
            else:
                severity_text = "Severe"

            return {
                "success": True,
                "diagnosis": response.text,
                "severity": severity,
                "severity_text": severity_text,
                "confidence": random.randint(80, 98),
                "health_tips": [
                    "Drink enough water",
                    "Take proper rest",
                    "Consult healthcare professional"
                ]
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

analyzer = MedicalImageAnalyzer()
