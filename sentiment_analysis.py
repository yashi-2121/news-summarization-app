from transformers import pipeline
from typing import List, Dict, Union
import time

class SentimentAnalyzer:
    def __init__(self):
        """Initialize the sentiment analysis pipeline"""
        print("Loading sentiment analysis model...")
        # Use the default sentiment analysis model (distilbert-base-uncased-finetuned-sst-2-english)
        self.sentiment_pipeline = pipeline("sentiment-analysis")
        print("✓ Sentiment analysis model loaded")

    def analyze_text(self, text: str) -> Dict[str, Union[str, float]]:
        """
        Analyze the sentiment of a given text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            Dict with sentiment label and score
        """
        # Truncate text if it's too long (model has max token limit)
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length]
        
        try:
            result = self.sentiment_pipeline(text)[0]
            return {
                "label": result["label"],
                "score": float(result["score"])
            }
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return {
                "label": "NEUTRAL",
                "score": 0.5
            }

    def analyze_article(self, article: Dict[str, str]) -> Dict[str, Union[str, float]]:
        """
        Analyze sentiment for a news article.
        
        Args:
            article (Dict): Article dictionary containing title, summary, and content
            
        Returns:
            Dict with overall sentiment analysis
        """
        # Analyze both title and summary for better accuracy
        title_sentiment = self.analyze_text(article["title"])
        summary_sentiment = self.analyze_text(article["summary"]) if article["summary"] else None
        
        # If we have both title and summary sentiments, combine them
        if summary_sentiment:
            # Use weighted average (title: 0.4, summary: 0.6)
            combined_score = (title_sentiment["score"] * 0.4 + summary_sentiment["score"] * 0.6)
            # Determine label based on combined score
            if combined_score >= 0.6:
                label = "POSITIVE"
            elif combined_score <= 0.4:
                label = "NEGATIVE"
            else:
                label = "NEUTRAL"
                
            return {
                "label": label,
                "score": combined_score,
                "title_sentiment": title_sentiment,
                "summary_sentiment": summary_sentiment
            }
        else:
            # If no summary, use just title sentiment
            return {
                "label": title_sentiment["label"],
                "score": title_sentiment["score"],
                "title_sentiment": title_sentiment,
                "summary_sentiment": None
            }

def process_articles(articles: List[Dict[str, str]]) -> List[Dict]:
    """
    Process a list of articles and add sentiment analysis.
    
    Args:
        articles (List[Dict]): List of article dictionaries
        
    Returns:
        List of articles with sentiment analysis added
    """
    analyzer = SentimentAnalyzer()
    
    for article in articles:
        print(f"\nAnalyzing sentiment for: {article['title'][:100]}...")
        sentiment = analyzer.analyze_article(article)
        article["sentiment"] = sentiment
        print(f"✓ Sentiment: {sentiment['label']} (score: {sentiment['score']:.2f})")
        time.sleep(0.1)  # Small delay to avoid overwhelming the model
        
    return articles

if __name__ == "__main__":
    # Example usage
    from news_scraper import get_news_articles
    
    print("\n=== News Sentiment Analyzer ===")
    company = "Microsoft"
    articles = get_news_articles(company)
    
    processed_articles = process_articles(articles)
    
    # Print results
    print("\nSentiment Analysis Results:")
    for i, article in enumerate(processed_articles, 1):
        print(f"\nArticle {i}:")
        print(f"Title: {article['title']}")
        print(f"Sentiment: {article['sentiment']['label']}")
        print(f"Score: {article['sentiment']['score']:.2f}")
        print("-" * 80) 