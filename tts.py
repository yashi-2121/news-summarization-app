from gtts import gTTS
import os
from typing import Optional
import tempfile
import hashlib

class TextToSpeech:
    def __init__(self, language: str = 'hi'):
        """
        Initialize TTS with specified language.
        
        Args:
            language (str): Language code ('hi' for Hindi)
        """
        self.language = language
        self.output_dir = "audio_files"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_filename(self, text: str) -> str:
        """Generate a unique filename based on the text content"""
        # Create a hash of the text to use as filename
        text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
        return f"{text_hash}.mp3"

    def text_to_speech(self, text: str, output_file: Optional[str] = None) -> str:
        """
        Convert text to speech and save as audio file.
        
        Args:
            text (str): Text to convert to speech
            output_file (Optional[str]): Output file path. If None, generates automatically.
            
        Returns:
            str: Path to the generated audio file
        """
        try:
            print(f"\nConverting text to Hindi speech...")
            
            # Generate output filename if not provided
            if output_file is None:
                output_file = os.path.join(self.output_dir, self.generate_filename(text))
            
            # Create gTTS object
            tts = gTTS(text=text, lang=self.language, slow=False)
            
            # Save to file
            tts.save(output_file)
            print(f"✓ Successfully generated audio file: {output_file}")
            
            return output_file
            
        except Exception as e:
            print(f"✗ Error generating speech: {str(e)}")
            return ""

    def generate_summary_audio(self, analysis_result: dict) -> str:
        """
        Generate audio for analysis summary.
        
        Args:
            analysis_result (dict): Analysis results containing summary
            
        Returns:
            str: Path to the generated audio file
        """
        # Get the summary text
        summary = analysis_result.get('summary', '')
        
        # Translate company names or technical terms if needed
        # This is a simple example - you might want to expand this
        translations = {
            "POSITIVE": "सकारात्मक",
            "NEGATIVE": "नकारात्मक",
            "NEUTRAL": "तटस्थ",
            "sentiment": "भावना",
            "articles": "लेख",
            "analysis": "विश्लेषण",
            "coverage": "कवरेज"
        }
        
        # Replace English terms with Hindi equivalents
        hindi_summary = summary
        for eng, hin in translations.items():
            hindi_summary = hindi_summary.replace(eng.lower(), hin)
        
        return self.text_to_speech(hindi_summary)

def process_text(text: str, output_file: Optional[str] = None) -> str:
    """
    Process text and convert to Hindi speech.
    
    Args:
        text (str): Text to convert
        output_file (Optional[str]): Output file path
        
    Returns:
        str: Path to the generated audio file
    """
    tts = TextToSpeech()
    return tts.text_to_speech(text, output_file)

if __name__ == "__main__":
    # Example usage
    from news_scraper import get_news_articles
    from sentiment_analysis import process_articles
    from comparative_analysis import analyze_articles
    
    print("\n=== Text to Speech Converter ===")
    
    # Get and analyze articles
    company = "Microsoft"
    articles = get_news_articles(company)
    articles_with_sentiment = process_articles(articles)
    analysis = analyze_articles(articles_with_sentiment)
    
    # Convert analysis summary to speech
    tts = TextToSpeech()
    audio_file = tts.generate_summary_audio(analysis)
    
    if audio_file:
        print(f"\nTest the audio file by playing: {audio_file}")
        print("You should hear the Hindi translation of the analysis summary.") 