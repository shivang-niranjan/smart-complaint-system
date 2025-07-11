# backend/urgency_scorer.py
import re

class UrgencyScorer:
    def __init__(self):
        # Weights for different factors
        self.category_impact = {
            "Electricity": 0.9,
            "Water": 0.8,
            "Sanitation": 0.7,
            "Roads": 0.6,
            "Traffic": 0.5,
            "Encroachment": 0.4,
            "Animal Control": 0.8, 
            "Unknown": 0.1 
        }

        self.severity_weights = {
            "Critical": 1.0, 
            "High": 0.8,
            "Medium": 0.5,
            "Low": 0.2
        }

        self.location_impact_factors = {
            "hospital": 1.0,
            "school": 0.9,
            "park": 0.8, 
            "market": 0.7,
            "main road": 0.6,
            "highway": 0.6,
            "residential area": 0.5,
            "public place": 0.5,
            "city entrance": 0.6,
            "community center": 0.4,
            "bus stop": 0.4,
            "metro station": 0.4,
            "industrial area": 0.3,
            "unknown location": 0.1
        }

        # Keywords to determine severity levels
        self.severity_keywords = {
            "Critical": [
                "critical", "emergency", "immediate", "danger", "life threatening",
                "collapse", "explosion", "fire", "flooding", "sinkhole", "accident",
                "aggressive", "chased a child", "attacked", "bit", "rabid", 
                "blocked access", "no access", "fire lane" 
            ],
            "High": [
                "urgent", "severe", "major", "widespread", "hazardous", "health risk",
                "no power", "no water", "overflowing", "piling up", "dangerous",
                "aggressive", "pack of dogs", "roaming", 
                "significant blockage" 
            ],
            "Medium": [
                "leak", "flickering", "broken", "damaged", "minor", "nuisance",
                "slow", "congestion", "overdue", "smell", "noise", "stray" 
            ],
            "Low": [
                "minor inconvenience", "aesthetic", "faded", "suggestion", "small",
                "cosmetic", "lost pet" 
            ]
        }

    def get_severity_level(self, category, description):
        description_lower = description.lower()
        for keyword in self.severity_keywords["Critical"]:
            if keyword in description_lower:
                return "Critical"
        for keyword in self.severity_keywords["High"]:
            if keyword in description_lower:
                return "High"
        for keyword in self.severity_keywords["Medium"]:
            if keyword in description_lower:
                return "Medium"
        return "Low"

    def get_location_impact(self, location_text):
        location_text_lower = location_text.lower()
        for keyword, impact in self.location_impact_factors.items():
            if keyword in location_text_lower:
                return impact
        return self.location_impact_factors["unknown location"] 

    def score_complaint(self, category, severity, location, description):
        category_weight = self.category_impact.get(category, self.category_impact["Unknown"])
        
        determined_severity = self.get_severity_level(category, description)
        severity_weight = self.severity_weights.get(determined_severity, self.severity_weights["Low"])

        location_weight = self.get_location_impact(location)

        raw_score = (category_weight * 0.4) + (severity_weight * 0.4) + (location_weight * 0.2)

        scaled_score = max(1, round(raw_score * 10)) 

        return scaled_score

