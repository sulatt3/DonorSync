class ContentGenerator:
    @staticmethod
    def generate_copy(cluster_id, urgency_score, crisis_name, ask_amount):
        """Generates dynamic copy based on urgency and persona."""
        
        # Logic: Higher urgency = More direct language
        if urgency_score > 0.7:
            tone = "URGENT ACTION REQUIRED"
            body = f"The situation with {crisis_name} is critical. Data indicates you are one of our most reliable supporters. We need you now."
        elif urgency_score > 0.4:
            tone = "Update on Crisis"
            body = f"We are monitoring {crisis_name} closely. Your support has always been vital. Can you help today?"
        else:
            tone = "Support Our Mission"
            body = f"As we look at the impact of {crisis_name}, we are reminded of the power of community. Join us."

        return {
            "headline": f"{tone}: Help {crisis_name} Victims",
            "body": body,
            "ask": f"Please donate ${ask_amount}."
        }
