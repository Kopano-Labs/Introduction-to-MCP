"""
civic_utility_router.py — Civic Utility Telemetry Router
======================================================
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

import hashlib
from datetime import datetime, timezone

class CivicUtilityRouter:
    """
    Routs telemetry signals to concrete physical utilities.
    Instead of academic translation, maps pothole and grid reports to government-compliant APIs.
    """

    CIVIC_KEYWORDS = {
        "pothole": "INFRASTRUCTURE_POTHOLE",
        "load shedding": "ENERGY_GRID_FAILURE",
        "loadshedding": "ENERGY_GRID_FAILURE",
        "power outage": "ENERGY_GRID_FAILURE",
        "water leak": "INFRASTRUCTURE_WATER_LEAK",
        "sewage": "INFRASTRUCTURE_SEWAGE",
        "road": "INFRASTRUCTURE_ROAD",
    }

    def parse_signal(self, text: str) -> dict:
        """
        Scan text for civic utility keywords and return category if found.
        """
        if not text:
            return {"detected": False, "category": None}
            
        text_lower = text.lower()
        for kw, category in self.CIVIC_KEYWORDS.items():
            if kw in text_lower:
                return {"detected": True, "category": category, "keyword": kw}
                
        return {"detected": False, "category": None}

    def route_civic_signal(self, text: str, location: str = "Unknown") -> dict:
        """
        Compile and route civic reports to mock municipality reporting service.
        """
        analysis = self.parse_signal(text)
        if not analysis["detected"]:
            return {
                "routed": False,
                "reason": "No civic utility intent detected in signal content",
            }

        ts = datetime.now(timezone.utc).isoformat()
        sig_hash = hashlib.sha256(f"{text}:{ts}:{location}".encode()).hexdigest()[:12]
        
        report_payload = {
            "routed": True,
            "civic_id": f"KPGS-CIVIC-{sig_hash.upper()}",
            "category": analysis["category"],
            "trigger_keyword": analysis["keyword"],
            "description": text.strip(),
            "location_context": location,
            "timestamp": ts,
            "government_endpoint": "https://api.capetown.gov.za/v1/service-requests/mock",
            "verdict": "ROUTED_TO_GOVERNMENT",
            "schema": "kpgs_civic_utility_report_v1",
        }
        
        return report_payload
