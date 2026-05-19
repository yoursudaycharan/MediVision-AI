from datetime import datetime

class MedicineReminder:
    def __init__(self):
        self.reminders = []

    def add_reminder(self, medicine_name, dosage, timing):
        reminder = {
            "medicine": medicine_name,
            "dosage": dosage,
            "timing": timing,
            "created_at": datetime.now()
        }

        self.reminders.append(reminder)

        return f"Reminder added for {medicine_name}"