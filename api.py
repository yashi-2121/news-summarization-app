from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import os

# Import our components
from news_scraper import get_news_articles
from sentiment_analysis import process_articles
from comparative_analysis import analyze_articles
from tts import TextToSpeech

# Initialize FastAPI app
app = FastAPI(
    title="News Analysis API",
    description="API for news sentiment analysis and text-to-speech conversion",
    version="1.0.0"
)

class AnalysisRequest(BaseModel):
    company: str
    generate_audio: bool = True

class AnalysisResponse(BaseModel):
    articles: List[Dict]
    sentiment_analysis: Dict
    audio_file: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to News Analysis API",
        "endpoints": {
            "/analyze": "POST - Analyze news for a company",
            "/audio/{filename}": "GET - Retrieve generated audio file"
        }
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_company(request: AnalysisRequest):
    """
    Analyze news articles for a company
    
    - Fetches news articles
    - Performs sentiment analysis
    - Generates comparative analysis
    - Creates Hindi TTS audio (optional)
    """
    try:
        # Fetch and analyze articles
        print(f"\nProcessing request for company: {request.company}")
        
        # Get news articles
        articles = get_news_articles(request.company)
        if not articles:
            raise HTTPException(status_code=404, detail="No news articles found")
            
        # Process sentiment
        articles_with_sentiment = process_articles(articles)
        
        # Generate comparative analysis
        analysis = analyze_articles(articles_with_sentiment)
        
        # Generate audio if requested
        audio_file = None
        if request.generate_audio:
            tts = TextToSpeech()
            audio_file = tts.generate_summary_audio(analysis)
            if audio_file:
                # Convert to relative path for response
                audio_file = os.path.basename(audio_file)
        
        return {
            "articles": articles_with_sentiment,
            "sentiment_analysis": analysis,
            "audio_file": audio_file
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Retrieve generated audio file"""
    audio_path = os.path.join("audio_files", filename)
    
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
        
    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename=filename
    )

if __name__ == "__main__":
    # Run the API server
    print("\n=== Starting News Analysis API ===")
    uvicorn.run(app, host="0.0.0.0", port=8000) 