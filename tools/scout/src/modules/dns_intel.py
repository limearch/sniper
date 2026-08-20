# File: tools/scout/src/modules/dns_intel.py
# Description: Gathers intelligence from DNS records and WHOIS data.

import whois
import dns.resolver
import datetime
from urllib.parse import urlparse

class DnsIntel:
    """
    Performs network-based checks: Domain Age and DNS records.
    """
    
    def get_domain_age(self, domain):
        """
        Retrieves domain creation date via WHOIS.
        Returns: Age in days (int) or None if lookup fails.
        """
        try:
            w = whois.whois(domain)
            creation_date = w.creation_date
            
            # Handle cases where creation_date is a list (some registrars return multiple dates)
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            if isinstance(creation_date, datetime.datetime):
                age = (datetime.datetime.now() - creation_date).days
                return age
        except Exception:
            # WHOIS lookup failed or format unknown
            return None
        return None

    def check_mx_record(self, domain):
        """Checks if the domain has MX records (email capability)."""
        try:
            dns.resolver.resolve(domain, 'MX')
            return True
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.LifetimeTimeout):
            return False
        except Exception:
            return False # Assume false on error

    def analyze(self, url):
        """
        Analyzes DNS and Registration data.
        Returns: (score_modifier, list_of_flags)
        """
        score = 0
        flags = []
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.split(':')[0] # Strip port
            
            # Skip this check for direct IPs
            import re
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
                return 0, []

            # 1. Domain Age
            age = self.get_domain_age(domain)
            if age is not None:
                if age < 14: # Less than 2 weeks old
                    score += 40
                    flags.append(f"Newly Created Domain ({age} days old)")
                elif age < 30: # Less than a month
                    score += 20
                    flags.append(f"Young Domain ({age} days old)")
            
            # 2. DNS Hygiene (Missing MX)
            # Legitimate businesses usually have email set up. Phishing sites often don't.
            has_mx = self.check_mx_record(domain)
            if not has_mx:
                score += 10
                flags.append("No Email (MX) Records")

        except Exception:
            pass # Fail silently on network errors to keep the tool fast

        return score, flags
