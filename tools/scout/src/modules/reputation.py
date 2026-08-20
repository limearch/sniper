# File: tools/scout/src/modules/reputation.py
# Description: Handles integration with external Threat Intelligence APIs.

import requests
import base64
import hashlib
from lib.sniper_env import env

class ReputationEngine:
    def __init__(self, config):
        """
        Args:
            config (dict): A dictionary containing API keys (from sniper-config.json).
        """
        self.keys = config
        self.results = {}

    def check_virustotal(self, url):
        api_key = self.keys.get("virustotal")
        if not api_key: return None

        try:
            # VT requires URL ID (base64 encoded URL without padding)
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            headers = {"x-apikey": api_key}
            response = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                stats = data['data']['attributes']['last_analysis_stats']
                return {
                    "malicious": stats['malicious'],
                    "suspicious": stats['suspicious'],
                    "harmless": stats['harmless']
                }
            elif response.status_code == 404:
                return {"status": "Not Found (Scan required)"}
        except Exception:
            return {"error": "Connection Failed"}
        return None

    def check_urlhaus(self, url):
        """Checks URLHaus (Open Threat Intel, no key strictly required for lookup usually, but using API)."""
        try:
            data = {'url': url}
            response = requests.post("https://urlhaus-api.abuse.ch/v1/url/", data=data, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result['query_status'] == 'ok':
                    return {
                        "status": result['url_status'], # online/offline
                        "tags": result.get('tags', []),
                        "threat": result.get('threat', 'unknown')
                    }
                elif result['query_status'] == 'no_results':
                    return {"status": "Clean / Not Found"}
        except Exception:
            pass
        return None

    def check_phishtank(self, url):
        """Simple check against PhishTank (Requires user_agent, key optional but recommended)."""
        # Note: PhishTank API is often heavy. We perform a basic check if a key exists or public endpoint.
        # For this implementation, we'll skip the XML DB download and assume an API key setup or skip.
        # Placeholder for future expansion.
        return None

    def check_google_safe_browsing(self, url):
        api_key = self.keys.get("google_safe_browsing")
        if not api_key: return None
        
        payload = {
            "client": {"clientId": "sniper-scout", "clientVersion": "1.0.0"},
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}]
            }
        }
        try:
            r = requests.post(f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}", json=payload, timeout=5)
            if r.status_code == 200:
                data = r.json()
                if "matches" in data:
                    return {"matches": [m['threatType'] for m in data['matches']]}
                return {"status": "Clean"}
        except Exception:
            pass
        return None

    def run_all_checks(self, url):
        """Aggregates results from all available and configured services."""
        report = {}
        
        # 1. VirusTotal
        vt = self.check_virustotal(url)
        if vt: report['VirusTotal'] = vt
        
        # 2. URLhaus
        uh = self.check_urlhaus(url)
        if uh: report['URLhaus'] = uh
        
        # 3. Google Safe Browsing
        gsb = self.check_google_safe_browsing(url)
        if gsb: report['GoogleSB'] = gsb

        return report
