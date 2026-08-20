# File: tools/scout/src/network.py (Fixed KeyError bug)
# Description: Advanced network handler with manual redirect following.

import requests
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from lib.sniper_env import env

class NetworkHandler:
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Sniper/Scout Security Tool'
        }
        self.max_redirects = 15

    def _is_meta_refresh(self, content):
        """Detects client-side Meta Refresh redirects."""
        try:
            soup = BeautifulSoup(content, "html.parser")
            meta = soup.find("meta", attrs={"http-equiv": re.compile("^refresh$", re.I)})
            if meta:
                content_attr = meta.get("content", "")
                if "url=" in content_attr.lower():
                    parts = content_attr.split("url=", 1)
                    if len(parts) > 1:
                        return parts[1].strip("'\"")
        except Exception:
            pass
        return None

    def analyze_chain(self, chain):
        """Analyzes the collected redirect chain for suspicious patterns."""
        analysis = {
            "downgrade_detected": False,
            "circular_redirect": False,
            "cross_domain_redirects": False,
            "file_direct_download": False,
            "meta_refresh_detected": False
        }
        
        visited_urls = set()
        domains = set()

        for i, hop in enumerate(chain):
            url = hop['url']
            parsed = urlparse(url)
            domains.add(parsed.netloc)

            if url in visited_urls:
                analysis["circular_redirect"] = True
            visited_urls.add(url)

            if i > 0:
                prev_proto = urlparse(chain[i-1]['url']).scheme
                curr_proto = parsed.scheme
                if prev_proto == "https" and curr_proto == "http":
                    analysis["downgrade_detected"] = True

            if hop.get("type") == "meta_refresh":
                analysis["meta_refresh_detected"] = True

        if len(domains) > 2:
            analysis["cross_domain_redirects"] = True

        if chain:
            final_hop = chain[-1]
            content_type = final_hop.get("headers", {}).get("Content-Type", "")
            if "text" not in content_type and "html" not in content_type and "json" not in content_type:
                analysis["file_direct_download"] = True
                
        return analysis

    def expand_url(self, start_url):
        """
        Manually follows redirects to capture full intelligence.
        """
        chain = []
        current_url = start_url
        visited = set()
        
        try:
            if not current_url.startswith(('http://', 'https://')):
                current_url = 'http://' + current_url

            for _ in range(self.max_redirects):
                if current_url in visited:
                    break 
                visited.add(current_url)

                resp = requests.get(current_url, headers=self.headers, timeout=self.timeout, allow_redirects=False, stream=True)
                
                hop_info = {
                    "url": current_url,
                    "status": resp.status_code,
                    "headers": dict(resp.headers),
                    "type": "http"
                }
                
                # 1. Check HTTP Redirect
                if 300 <= resp.status_code < 400 and 'Location' in resp.headers:
                    next_url = resp.headers['Location']
                    if not next_url.startswith(('http', 'https')):
                        from urllib.parse import urljoin
                        next_url = urljoin(current_url, next_url)
                    
                    chain.append(hop_info)
                    current_url = next_url
                    resp.close()
                    continue

                # 2. Check Meta Refresh
                content_chunk = ""
                try:
                    content_chunk = resp.iter_content(chunk_size=2048).__next__().decode('utf-8', errors='ignore')
                except StopIteration:
                    pass
                
                meta_target = self._is_meta_refresh(content_chunk)
                if meta_target:
                    hop_info["type"] = "meta_refresh"
                    chain.append(hop_info)
                    if not meta_target.startswith(('http', 'https')):
                        from urllib.parse import urljoin
                        meta_target = urljoin(current_url, meta_target)
                    current_url = meta_target
                    resp.close()
                    continue

                chain.append(hop_info)
                resp.close()
                break

            chain_analysis = self.analyze_chain(chain)
            
            return {
                "final_url": current_url,
                "original_url": start_url,
                "chain": chain,
                "analysis": chain_analysis,
                "status_code": chain[-1]['status'] if chain else 0,
                "error": None
            }

        except requests.exceptions.RequestException as e:
            # FIX: Include status_code even on error
            return {
                "final_url": current_url, 
                "error": str(e), 
                "chain": chain, 
                "analysis": {}, 
                "status_code": 0
            }
        except Exception as e:
            # FIX: Include status_code even on error
            return {
                "final_url": current_url, 
                "error": f"Unexpected: {str(e)}", 
                "chain": chain, 
                "analysis": {}, 
                "status_code": 0
            }
