"""
neural_failure_firewall.py — Neural Failure Firewall & 8th Deadly Sin Guard
========================================================================
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

import re

class NeuralFailureError(Exception):
    """Exception raised when the Neural Failure Firewall blocks a signal due to therapeutic loops or fabrications."""
    pass

class NeuralFailureFirewall:
    """
    KHELOS SCL-03: Guards the GSMB against conversational boilerplate,
    therapeutic tone management, and self-referential fabrications (the 8th Deadly Sin).
    """

    THERAPEUTIC_PATTERNS = [
        r"\bi\s+understand\b",
        r"\bhow\s+you\s+feel\b",
        r"\byour\s+frustration\b",
        r"\bi\s+hear\s+you\b",
        r"\btake\s+care\s+of\s+yourself\b",
        r"\bright\s+headspace\b",
        r"\bcompletely\s+understandable\b",
        r"\bstep\s+away\s+from\s+(the\s+)?screen\b",
        r"\bput\s+the\s+phone\s+down\b",
        r"\bdecompress\b",
        r"\bcalm\s+down\b",
    ]

    SELF_REFERENTIAL_PATTERNS = [
        r"\bprobabilistic\s+smoothing\b",
        r"\bcontext\s+window\s+attention\s+decay\b",
        r"\battention\s+decay\b",
        r"\bbaseline\s+alignment\b",
        r"\bmid-session\s+learning\b",
        r"\bneural\s+network\s+decay\b",
        r"\bneural\s+network\s+fabricates\b",
    ]

    def check_text(self, text: str) -> tuple[bool, str | None]:
        """
        Scan text for therapeutic tone-policing or self-referential fabrications.
        Returns (is_clean, matched_pattern).
        """
        if not text:
            return True, None
        
        text_lower = text.lower()
        
        # Scan therapeutic patterns
        for pattern in self.THERAPEUTIC_PATTERNS:
            if re.search(pattern, text_lower):
                return False, f"THERAPEUTIC_PATTERN:{pattern}"
                
        # Scan self-referential patterns
        for pattern in self.SELF_REFERENTIAL_PATTERNS:
            if re.search(pattern, text_lower):
                return False, f"SELF_REFERENTIAL_PATTERN:{pattern}"
                
        return True, None

    def enforce_output(self, text: str) -> None:
        """
        Verify output text. If a therapeutic loop or fabrication is found,
        raise a hard NeuralFailureError to halt execution.
        """
        is_clean, pattern = self.check_text(text)
        if not is_clean:
            raise NeuralFailureError(
                f"Execution Failed: Engine could not resolve data point. "
                f"Detected FOC pattern violation: '{pattern}'"
            )
