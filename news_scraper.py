import requests
from bs4 import BeautifulSoup
from newspaper import Article
import nltk
from typing import List, Dict, Optional
import time
import urllib.parse

# Download all required NLTK data
def download_nltk_resources():
    """Download required NLTK resources"""
    try:
        # Download the punkt tokenizer data
        print("Downloading NLTK resources...")
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        print("✓ Successfully downloaded NLTK resources")
    except Exception as e:
        print(f"✗ Error downloading NLTK resources: {str(e)}")
        raise

# Download NLTK resources before processing
download_nltk_resources()

def clean_url(url: str) -> str:
    """Clean and decode URL if needed"""
    try:
        return urllib.parse.unquote(url)
    except:
        return url

def get_news_articles(company_name: str) -> List[Dict[str, str]]:
    """
    Fetch top 10 news articles about a company from Bing News RSS feed.
    
    Args:
        company_name (str): Name of the company to search for
        
    Returns:
        List[Dict[str, str]]: List of dictionaries containing article information
    """
    # Encode company name for URL
    search_url = f"https://www.bing.com/news/search?q={urllib.parse.quote(company_name)}&format=rss"
    
    try:
        # Fetch RSS feed
        print(f"\nFetching news about {company_name}...")
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        
        # Parse RSS feed
        soup = BeautifulSoup(response.content, features='xml')
        
        articles = []
        items = soup.find_all('item')[:10]
        print(f"Found {len(items)} news items to process")
        
        for item in items:
            # Extract title and description from RSS feed
            rss_title = item.title.text if item.title else ""
            rss_description = item.description.text if item.description else ""
            url = clean_url(item.link.text if item.link else item.link.string)
            
            try:
                print(f"\nProcessing: {rss_title}")
                
                # Initialize Article object with longer timeout
                article = Article(url, timeout=20)
                article.download()
                time.sleep(1)  # Add small delay to avoid overwhelming servers
                article.parse()
                
                try:
                    article.nlp()  # This generates summary
                except Exception as nlp_error:
                    print(f"  → Using RSS data due to NLP error: {str(nlp_error)}")
                    # Continue with RSS data if NLP fails
                    article.summary = rss_description
                
                # Create article dictionary with extracted information
                article_data = {
                    "title": article.title or rss_title,  # Fallback to RSS title if needed
                    "url": url,
                    "summary": article.summary or rss_description,  # Fallback to RSS description
                    "content": article.text,
                    "publish_date": str(article.publish_date) if article.publish_date else None,
                    "authors": article.authors if article.authors else []
                }
                
                articles.append(article_data)
                print(f"✓ Successfully processed article")
                
            except Exception as e:
                print(f"✗ Error processing article: {str(e)}")
                # Try to add article with RSS data if article processing fails
                if rss_title and rss_description:
                    article_data = {
                        "title": rss_title,
                        "url": url,
                        "summary": rss_description,
                        "content": rss_description,
                        "publish_date": None,
                        "authors": []
                    }
                    articles.append(article_data)
                    print(f"  → Added article using RSS data")
                continue
                
        return articles
        
    except requests.RequestException as e:
        print(f"Error fetching news: {str(e)}")
        return []

if __name__ == "__main__":
    # Example usage
    print("\n=== News Article Fetcher ===")
    company = "Microsoft"
    articles = get_news_articles(company)
    
    # Print results
    print(f"\nSuccessfully retrieved {len(articles)} articles:")
    for i, article in enumerate(articles, 1):
        print(f"\nArticle {i}:")
        print(f"Title: {article['title']}")
        print(f"URL: {article['url']}")
        if article['summary']:
            print(f"Summary: {article['summary'][:200]}...")
        else:
            print("Summary: No summary available")
        if article['authors']:
            print(f"Authors: {', '.join(article['authors'])}")
        print("-" * 80) 