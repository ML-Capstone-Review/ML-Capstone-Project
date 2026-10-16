"""Notebook-derived input schema and customer-facing labels."""
NUMERIC_COLUMNS = [
    "Age", "Flight Distance", "Departure Delay", "Arrival Delay",
    "Departure and Arrival Time Convenience", "Ease of Online Booking",
    "Check-in Service", "Online Boarding", "Gate Location", "On-board Service",
    "Seat Comfort", "Leg Room Service", "Cleanliness", "Food and Drink",
    "In-flight Service", "In-flight Wifi Service", "In-flight Entertainment",
    "Baggage Handling",
]
CATEGORICAL_COLUMNS = ["Gender", "Customer Type", "Type of Travel", "Class"]
TARGET = "Satisfaction"
ID_COLUMN = "ID"
ENGINEERED_COLUMN = "Total Delay"
LABELS = {
    "Gender": "How do you describe your gender?",
    "Customer Type": "Which best describes you as a customer?",
    "Type of Travel": "What was the purpose of your trip?",
    "Class": "Which cabin did you travel in?",
    "Age": "Your age", "Flight Distance": "Flight distance (miles)",
    "Departure Delay": "Departure delay (minutes)",
    "Arrival Delay": "Arrival delay (minutes)",
    "Departure and Arrival Time Convenience": "Convenience of flight times",
    "Ease of Online Booking": "Ease of online booking", "Check-in Service": "Check-in service",
    "Online Boarding": "Online boarding", "Gate Location": "Gate location",
    "On-board Service": "On-board service", "Seat Comfort": "Seat comfort",
    "Leg Room Service": "Leg room", "Cleanliness": "Cabin cleanliness",
    "Food and Drink": "Food and drink", "In-flight Service": "In-flight service",
    "In-flight Wifi Service": "In-flight Wi-Fi", "In-flight Entertainment": "In-flight entertainment",
    "Baggage Handling": "Baggage handling",
}
RATING_COLUMNS = [c for c in NUMERIC_COLUMNS if c not in {
    "Age", "Flight Distance", "Departure Delay", "Arrival Delay"
}]
