# File: tools/scout/src/analyzer.py (Bug Fixed)
# Description: Updated analyzer to handle complex URLs (Auth, Ports) correctly.

import json
import re
import ipaddress
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

try:
    from .modules.entropy import EntropyAnalyzer
    from .modules.homoglyph import HomoglyphAnalyzer
    from .modules.dns_intel import DnsIntel
    from .modules.reputation import ReputationEngine
except ImportError:
    from modules.entropy import EntropyAnalyzer
    from modules.homoglyph import HomoglyphAnalyzer
    from modules.dns_intel import DnsIntel
    from modules.reputation import ReputationEngine

class UrlAnalyzer:
    def __init__(self, offline_mode=False, use_reputation=False, api_config=None):
        self.offline = offline_mode
        self.use_reputation = use_reputation
        self.api_config = api_config or {}
        
        self.trackers = self._load_trackers()
        self.entropy_engine = EntropyAnalyzer()
        self.homoglyph_engine = HomoglyphAnalyzer()
        self.dns_engine = DnsIntel()
        self.reputation_engine = ReputationEngine(self.api_config)
        
        self.suspicious_tlds = ['.zip', '.mov', '.xyz', '.top', '.gq', '.cn', '.ru', '.work', '.click', '.loan', '.kim']

    def _load_trackers(self):
        try:
            config_path = Path(__file__).resolve().parents[1] / "config" / "trackers.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except Exception:
            return {"utm_source", "fbclid"}

    def clean_url(self, url):
        parsed = urlparse(url)
        query = parse_qs(parsed.query, keep_blank_values=True)
        cleaned = {k: v for k, v in query.items() if k.lower() not in self.trackers}
        removed = [k for k in query if k.lower() in self.trackers]
        new_query = urlencode(cleaned, doseq=True)
        return urlunparse(parsed._replace(query=new_query)), removed

    def assess_risk(self, url, network_analysis=None):
        total_score = 0
        all_flags = []
        reputation_data = {}

        try:
            parsed = urlparse(url)
            
            # --- FIX: Use hostname to properly extract domain/IP ignoring auth and ports ---
            domain = parsed.hostname 
            if not domain: 
                # Fallback if hostname is None (rare edge cases)
                domain = parsed.netloc.split('@')[-1].split(':')[0]
                
            path = parsed.path
            query = parsed.query

            # 1. Network Analysis Integration
            if network_analysis:
                if network_analysis.get("downgrade_detected"):
                    total_score += 30
                    all_flags.append("Protocol Downgrade (HTTPS -> HTTP)")
                
                if network_analysis.get("circular_redirect"):
                    total_score += 15
                    all_flags.append("Circular Redirect Loop")
                
                if network_analysis.get("meta_refresh_detected"):
                    total_score += 20
                    all_flags.append("Meta Refresh (Client-side Redirect)")
                
                if network_analysis.get("file_direct_download"):
                    total_score += 15
                    all_flags.append("Direct File Download Target")

            # 2. Static Analysis
            
            # Check: Embedded Credentials
            # We check parsed.netloc for '@' because parsed.username might decode it
            if '@' in parsed.netloc: 
                total_score += 40
                all_flags.append("Embedded Credentials (@)")

            # Check: Direct IP Usage
            try:
                # Remove enclosing brackets for IPv6 if present
                clean_domain = domain.strip("[]")
                ipaddress.ip_address(clean_domain)
                total_score += 25
                all_flags.append("Direct IP Usage")
            except ValueError:
                pass # Not an IP

            # Check: Suspicious TLD
            if any(domain.endswith(tld) for tld in self.suspicious_tlds): 
                total_score += 15
                all_flags.append("Suspicious TLD")

            # Check: Executable Extensions
            if path.lower().endswith(('.exe', '.scr', '.bat', '.sh', '.apk', '.msi')):
                total_score += 20
                all_flags.append("Executable File Extension")

            # 3. Modules
            e_score, e_flags = self.entropy_engine.analyze(domain, path, query)
            total_score += e_score; all_flags.extend(e_flags)

            h_score, h_flags = self.homoglyph_engine.analyze(url)
            total_score += h_score; all_flags.extend(h_flags)

            if not self.offline:
                d_score, d_flags = self.dns_engine.analyze(url)
                total_score += d_score; all_flags.extend(d_flags)

            # 4. Reputation
            if self.use_reputation and not self.offline:
                rep_report = self.reputation_engine.run_all_checks(url)
                reputation_data = rep_report
                if rep_report.get('VirusTotal', {}).get('malicious', 0) > 0: total_score += 100; all_flags.append("Flagged by VirusTotal")
                if rep_report.get('URLhaus', {}).get('threat'): total_score += 100; all_flags.append("Flagged by URLhaus")
                if rep_report.get('GoogleSB', {}).get('matches'): total_score += 100; all_flags.append("Flagged by Google Safe Browsing")

        except Exception as e:
            all_flags.append(f"Analysis Error: {str(e)}")

        # Level
        if total_score >= 80: level = "CRITICAL"
        elif total_score >= 46: level = "MALICIOUS"
        elif total_score >= 16: level = "SUSPICIOUS"
        else: level = "SAFE"

        return total_score, level, all_flags, reputation_data
