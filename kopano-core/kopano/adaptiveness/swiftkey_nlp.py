"""
swiftkey_nlp.py — SwiftKey Adaptive Linguistic NLP Model
======================================================
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

class SwiftKeyNLP:
    """
    Implements H's SwiftKey adaptive model for South African township vernacular (Tsotsitaal, Zulu, Xhosa, Sepedi).
    Avoids the academic trap of training models from scratch by using an adaptive translation mapping layer.
    """

    def __init__(self):
        # Initial dictionary mapping township slang and local vernacular to semantic equivalents.
        self.local_dictionary = {
            "retswetswa ka soutu": "purged under pressure / salted with hardship",
            "kasi": "township community",
            "ekasi": "in the township",
            "grootman": "elder respected mentor",
            "mzansi": "South Africa",
            "bhuda": "brother / peer",
            "zotsital": "tsotsitaal dialect",
            "tsotsitaal": "township slang dialect",
            "danun": "Dunoon",
            "danoon": "Dunoon",
            "khayelitsha": "Khayelitsha",
            "gugulethu": "Gugulethu",
            "fonc": "fake of concept",
            "ponc": "proof of concept",
            "gsmb": "governance system membrane",
        }

    def translate(self, text: str) -> str:
        """
        Scan text for local slang and translate to clear semantic terms.
        This resolves the tokenizer gap by preventing word fragmentation.
        """
        if not text:
            return ""
            
        translated = text
        text_lower = text.lower()
        
        # Sort keys by length descending to match longer phrases first
        for slang in sorted(self.local_dictionary.keys(), key=len, reverse=True):
            if slang in text_lower:
                # Case-insensitive replacement
                import re
                pattern = re.compile(re.escape(slang), re.IGNORECASE)
                translated = pattern.sub(self.local_dictionary[slang], translated)
                
        return translated

    def learn_phrase(self, raw_phrase: str, translation: str) -> None:
        """
        Dynamically learn a new local vernacular slang word or phrase from edge user feedback.
        """
        if raw_phrase and translation:
            self.local_dictionary[raw_phrase.strip().lower()] = translation.strip()

    def calculate_token_footprint(self, text: str) -> int:
        """
        Simulate token count using a standard Western tokenizer logic where
        unstandardized slang is fragmented heavily.
        """
        if not text:
            return 0
            
        words = text.split()
        token_count = 0
        
        for word in words:
            word_lower = word.lower()
            # If word is in local dictionary keys (i.e. is vernacular slang)
            # simulate that a standard tokenizer would split it into 3-4 sub-tokens
            is_slang = any(slang in word_lower for slang in self.local_dictionary.keys() if len(slang) > 3)
            if is_slang:
                token_count += 4
            else:
                token_count += 1
                
        return token_count

    def calculate_savings(self, raw_text: str) -> dict:
        """
        Calculate token and cost savings by comparing raw text tokenization vs translated text.
        """
        translated_text = self.translate(raw_text)
        raw_tokens = self.calculate_token_footprint(raw_text)
        translated_tokens = len(translated_text.split())  # standard words map close to 1:1 tokens
        
        savings = max(0, raw_tokens - translated_tokens)
        cost_savings_factor = savings * 0.00015  # Simulated cost factor per token
        
        return {
            "raw_tokens": raw_tokens,
            "translated_tokens": translated_tokens,
            "tokens_saved": savings,
            "cost_savings_factor": round(cost_savings_factor, 6),
            "translated_text": translated_text,
        }
