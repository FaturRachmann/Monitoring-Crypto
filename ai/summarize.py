import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def summarize(text):
    """
    Simple text summarization function.
    In production, you could use OpenAI API, Hugging Face, or other AI services.
    """
    try:
        if not text or len(text) < 50:
            return text
        
        # Simple summarization - take first 150 characters and add ellipsis
        if len(text) > 150:
            summary = text[:150].strip()
            # Find the last complete word
            last_space = summary.rfind(' ')
            if last_space > 100:  # Ensure we don't cut too short
                summary = summary[:last_space]
            summary += "..."
            logger.info(f"Summarized text from {len(text)} to {len(summary)} characters")
            return summary
        
        return text
    
    except Exception as e:
        logger.error(f"Error in summarization: {str(e)}")
        return text[:100] + "..." if len(text) > 100 else text