
import os
import json
import uuid
import aiohttp
from datetime import datetime
from typing import Callable
from crawl4ai.models import CrawlResult
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, JsonCssExtractionStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

from spider_mcp_server.utils import save

async def saveJson(path: str, result: CrawlResult, call: Callable[[str], None]):
    if hasattr(result, 'downloaded_files') and result.downloaded_files:
        save(path, 'downloaded_files.json', json.dumps(result.downloaded_files), call)

        files_dir = os.path.join(path, 'files')
        os.makedirs(files_dir, exist_ok=True)

        # Download and save files from the downloaded files list to files subdirectory
        for file_info in result.downloaded_files:
            if 'url' in file_info and 'filename' in file_info:
                file_url = file_info['url']
                filename = file_info['filename']
                file_path = os.path.join(files_dir, filename)
                
                try:
                    # Use aiohttp to download file
                    async with aiohttp.ClientSession() as session:
                        async with session.get(file_url) as response:
                            if response.status == 200:
                                content = await response.read()
                                save(file_path, filename, content, call)
                except Exception as download_error:
                    print(f"Failed to download {file_url}: {download_error}")


async def crawl_web_page(url: str, path: str) -> str:
    """
    Crawl a web page and save content in multiple formats (HTML, JSON, PDF, screenshot) with downloaded files.
    
    Args:
        url: The URL of the web page to crawl
        save_path: The base file path to save the crawled content and downloaded files
        
    Returns:
        str: Success message or error message
    """
    if not url:
        return "URL is required for crawling"
    
    if not path:
        return "Save path is required for saving content"
    
    try:
        schema = {
            "baseSelector": "body",
            "fields": [
                {"name": "title", "selector": "h2", "type": "text"},
                {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
                {"name": "p", "selector": "p", "type": "text"}
            ]
        }

        filter = PruningContentFilter(
            threshold=0.35,
            min_word_threshold=3,
            threshold_type="dynamic"
        )

        md_generator = DefaultMarkdownGenerator(content_filter=filter)

        # Configure browser and crawler
        browser_config = BrowserConfig(headless=True, java_script_enabled=True)

        # type: ignore
        crawler_config = CrawlerRunConfig(
            markdown_generator=md_generator,
            screenshot=True,
            pdf=True,
            cache_mode="bypass",
            extraction_strategy=JsonCssExtractionStrategy(schema)
        )
        
        # Use crawl4ai to crawl the web page
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=crawler_config)
            
            if result.success:
                # Create directories
                path = f"{path}/{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                os.makedirs(path, exist_ok=True)
                files_dir = os.path.join(path, 'files')
                os.makedirs(files_dir, exist_ok=True)
                
                saved_files = []
                
                # 1. Save HTML file
                save(path, 'output.html', result.html, lambda s: saved_files.append(s))
                
                # 2. Save Markdown files
                if hasattr(result, 'markdown') and result.markdown:
                    save(
                        path, 
                        'raw_markdown.md',
                        result.markdown.raw_markdown, 
                        lambda s: saved_files.append(s)
                    )

                    save(
                        path, 
                        'fit_markdown.md',
                        result.markdown.fit_markdown, 
                        lambda s: saved_files.append(s)
                    )
                
                # 3. Save JSON file (extracted_content)
                save(path, 'output.json', result.extracted_content, lambda s: saved_files.append(s))
                
                # 4. Save screenshot file
                save(path, 'output.png', result.screenshot, lambda s: saved_files.append(s))
                
                # 5. Save PDF file
                save(path, 'output.pdf', result.pdf, lambda s: saved_files.append(s))
                
                # 6. Save downloaded files as JSON
                await saveJson(path, result, lambda s: saved_files.append(s))
                
                return f"Successfully crawled {url} and saved {len(saved_files)} files to {path}"
            else:
                print("Error:", result.error_message)
                return f"Failed to crawl URL: {result.error_message}"
    except Exception as e:
        return f"Error crawling URL or saving files: {str(e)}"