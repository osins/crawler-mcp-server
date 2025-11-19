
from typing import Callable
from crawl4ai.models import CrawlResult

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