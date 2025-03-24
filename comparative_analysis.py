from typing import List, Dict, Any
import matplotlib.pyplot as plt
from collections import Counter
import json

class ComparativeAnalyzer:
    def __init__(self):
        """Initialize the comparative analyzer"""
        self.sentiment_weights = {
            "POSITIVE": 1,
            "NEUTRAL": 0,
            "NEGATIVE": -1
        }

    def analyze_distribution(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze sentiment distribution across articles.
        
        Args:
            articles (List[Dict]): List of articles with sentiment analysis
            
        Returns:
            Dict containing sentiment distribution and analysis
        """
        # Count sentiments
        sentiment_counts = Counter(article["sentiment"]["label"] for article in articles)
        
        # Calculate percentages
        total_articles = len(articles)
        sentiment_percentages = {
            label: (count / total_articles) * 100 
            for label, count in sentiment_counts.items()
        }
        
        # Calculate average sentiment score
        avg_sentiment_score = sum(article["sentiment"]["score"] for article in articles) / total_articles
        
        # Determine overall sentiment trend
        if avg_sentiment_score >= 0.6:
            overall_trend = "POSITIVE"
        elif avg_sentiment_score <= 0.4:
            overall_trend = "NEGATIVE"
        else:
            overall_trend = "NEUTRAL"
            
        # Generate summary text
        summary = self._generate_summary(sentiment_counts, sentiment_percentages, avg_sentiment_score)
        
        return {
            "distribution": dict(sentiment_counts),
            "percentages": sentiment_percentages,
            "average_score": avg_sentiment_score,
            "overall_trend": overall_trend,
            "summary": summary
        }
    
    def _generate_summary(self, counts: Dict[str, int], percentages: Dict[str, float], avg_score: float) -> str:
        """Generate a human-readable summary of the sentiment analysis"""
        # Sort sentiments by count
        sorted_sentiments = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        # Create summary
        main_sentiment = sorted_sentiments[0][0]
        main_percentage = percentages[main_sentiment]
        
        summary = f"Analysis shows predominantly {main_sentiment.lower()} sentiment "
        summary += f"({main_percentage:.1f}% of articles). "
        
        if len(sorted_sentiments) > 1:
            second_sentiment = sorted_sentiments[1][0]
            second_percentage = percentages[second_sentiment]
            summary += f"This is followed by {second_sentiment.lower()} sentiment "
            summary += f"({second_percentage:.1f}% of articles). "
        
        summary += f"The average sentiment score is {avg_score:.2f}, "
        if avg_score >= 0.6:
            summary += "indicating overall positive coverage."
        elif avg_score <= 0.4:
            summary += "indicating overall negative coverage."
        else:
            summary += "indicating balanced coverage."
            
        return summary
    
    def generate_visualization(self, analysis: Dict[str, Any], save_path: str = "sentiment_distribution.png"):
        """
        Generate and save a visualization of sentiment distribution.
        
        Args:
            analysis (Dict): Analysis results from analyze_distribution
            save_path (str): Path to save the visualization
        """
        # Create pie chart
        plt.figure(figsize=(10, 6))
        
        # Data for pie chart
        labels = analysis["distribution"].keys()
        sizes = analysis["distribution"].values()
        colors = {
            "POSITIVE": "#2ecc71",
            "NEUTRAL": "#f1c40f",
            "NEGATIVE": "#e74c3c"
        }
        pie_colors = [colors.get(label, "#95a5a6") for label in labels]
        
        # Plot pie chart
        plt.pie(sizes, labels=labels, colors=pie_colors, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title("Sentiment Distribution Across Articles")
        
        # Save plot
        plt.savefig(save_path)
        plt.close()

def analyze_articles(articles: List[Dict[str, Any]], save_visualization: bool = True) -> Dict[str, Any]:
    """
    Perform comparative analysis on a list of articles.
    
    Args:
        articles (List[Dict]): List of articles with sentiment analysis
        save_visualization (bool): Whether to save visualization
        
    Returns:
        Dict containing analysis results
    """
    analyzer = ComparativeAnalyzer()
    analysis = analyzer.analyze_distribution(articles)
    
    if save_visualization:
        analyzer.generate_visualization(analysis)
    
    return analysis

if __name__ == "__main__":
    # Example usage
    from news_scraper import get_news_articles
    from sentiment_analysis import process_articles
    
    print("\n=== News Comparative Analysis ===")
    
    # Get and process articles
    company = "Microsoft"
    articles = get_news_articles(company)
    articles_with_sentiment = process_articles(articles)
    
    # Perform comparative analysis
    analysis = analyze_articles(articles_with_sentiment)
    
    # Print results
    print("\nAnalysis Results:")
    print("-" * 80)
    print(f"Sentiment Distribution: {json.dumps(analysis['distribution'], indent=2)}")
    print(f"Average Sentiment Score: {analysis['average_score']:.2f}")
    print(f"Overall Trend: {analysis['overall_trend']}")
    print("\nSummary:")
    print(analysis['summary'])
    print("\nVisualization saved as 'sentiment_distribution.png'") 