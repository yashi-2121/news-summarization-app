import gradio as gr
import requests
import json
import os
from typing import Tuple, Dict, Any

class NewsAnalyzer:
    def __init__(self, api_url: str = "http://localhost:8000"):
        """Initialize with API URL"""
        self.api_url = api_url
        self.latest_analysis = None
        
    def analyze_company(self, company_name: str) -> Tuple[str, str, str]:
        """
        Analyze company news and return results
        
        Returns:
            Tuple[str, str, str]: Summary text, visualization path, audio path
        """
        try:
            # Call API to analyze company
            response = requests.post(
                f"{self.api_url}/analyze",
                json={"company": company_name, "generate_audio": True}
            )
            response.raise_for_status()
            
            # Get analysis results
            result = response.json()
            self.latest_analysis = result
            
            # Get sentiment distribution
            distribution = result["sentiment_analysis"]["distribution"]
            total = sum(distribution.values())
            distribution_text = "Sentiment Distribution:\n"
            for sentiment, count in distribution.items():
                percentage = (count / total) * 100
                distribution_text += f"- {sentiment}: {percentage:.1f}%\n"
            
            # Format summary
            summary = (
                f"Analysis Results for {company_name}:\n\n"
                f"{distribution_text}\n"
                f"Overall Trend: {result['sentiment_analysis']['overall_trend']}\n"
                f"Average Score: {result['sentiment_analysis']['average_score']:.2f}\n\n"
                f"Summary:\n{result['sentiment_analysis']['summary']}"
            )
            
            # Get visualization path
            viz_path = "sentiment_distribution.png"
            
            # Get audio file if generated
            audio_path = None
            if result.get("audio_file"):
                audio_path = os.path.join("audio_files", result["audio_file"])
            
            return summary, viz_path, audio_path
            
        except Exception as e:
            error_msg = f"Error analyzing company: {str(e)}"
            return error_msg, None, None
    
    def get_detailed_results(self) -> str:
        """Get detailed analysis results as formatted text"""
        if not self.latest_analysis:
            return "No analysis results available. Please analyze a company first."
            
        # Format detailed results
        articles = self.latest_analysis["articles"]
        
        text = "Detailed Article Analysis:\n\n"
        for i, article in enumerate(articles, 1):
            text += f"Article {i}:\n"
            text += f"Title: {article['title']}\n"
            text += f"Sentiment: {article['sentiment']['label']}"
            text += f" (Score: {article['sentiment']['score']:.2f})\n"
            text += f"Summary: {article['summary'][:200]}...\n"
            text += "-" * 80 + "\n"
            
        return text

# Create Gradio interface
def create_interface() -> gr.Interface:
    """Create and configure the Gradio interface"""
    analyzer = NewsAnalyzer()
    
    def process_request(company: str) -> Tuple[str, str, str, str]:
        """Handle interface request"""
        # Analyze company
        summary, viz_path, audio_path = analyzer.analyze_company(company)
        
        # Get detailed results
        details = analyzer.get_detailed_results()
        
        return summary, details, viz_path, audio_path
    
    # Define interface
    iface = gr.Interface(
        fn=process_request,
        inputs=[
            gr.Textbox(
                label="Enter Company Name",
                placeholder="e.g., Microsoft",
                lines=1
            )
        ],
        outputs=[
            gr.Textbox(label="Analysis Summary", lines=10),
            gr.Textbox(label="Detailed Results", lines=15),
            gr.Image(label="Sentiment Distribution"),
            gr.Audio(label="Hindi Summary (Audio)")
        ],
        title="News Sentiment Analyzer",
        description=(
            "Enter a company name to analyze recent news sentiment and get a Hindi audio summary. "
            "The analysis includes sentiment distribution, overall trend, and detailed article analysis."
        ),
        examples=[["Microsoft"], ["Apple"], ["Google"]],
        theme="default"
    )
    
    return iface

if __name__ == "__main__":
    # Create and launch the interface
    print("\n=== Starting News Analysis Web Interface ===")
    print("Make sure the API server (api.py) is running on http://localhost:8000")
    
    iface = create_interface()
    iface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True  # Creates a public URL
    ) 