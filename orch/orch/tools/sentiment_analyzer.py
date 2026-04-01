import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import json

# Ensure the vader lexicon is downloaded (can be slow, but usually quick)
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

def analyze_sentiment(text: str) -> str:
    """
    Analyzes the sentiment of a given text using NLTK VADER.
    Returns a JSON string with sentiment scores (positive, negative, neutral, compound).
    """
    try:
        sia = SentimentIntensityAnalyzer()
        scores = sia.polarity_scores(text)
        
        # Add a human-readable interpretation
        if scores['compound'] >= 0.05:
            sentiment = "Positive"
        elif scores['compound'] <= -0.05:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
            
        result = {
            "sentiment": sentiment,
            "scores": scores,
            "text_sample": text[:100] + "..." if len(text) > 100 else text
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error analyzing sentiment: {e}"
