# File: tools/scout/src/modules/homoglyph.py
# Description: Detects IDN homograph attacks, script mixing, and typosquatting.

import tldextract
import unicodedata

# List of high-value targets often spoofed
HIGH_VALUE_TARGETS = {
    "google", "facebook", "twitter", "paypal", "apple", "microsoft", 
    "amazon", "netflix", "instagram", "linkedin", "whatsapp", "telegram",
    "binance", "coinbase", "blockchain", "bankofamerica", "chase", "wellsfargo"
}

class HomoglyphAnalyzer:
    """
    Analyzes domains for visual spoofing attempts.
    """

    def is_mixed_script(self, domain_label):
        """
        Checks if a domain label contains characters from mixed scripts (e.g., Latin + Cyrillic).
        This is a strong indicator of a homograph attack.
        """
        scripts = set()
        for char in domain_label:
            try:
                # Get the script name (e.g., 'LATIN', 'CYRILLIC', 'GREEK')
                name = unicodedata.name(char).split()[0]
                scripts.add(name)
            except ValueError:
                pass # Ignore unknown chars
        
        # Allow only one script type per label (excluding COMMON chars like numbers/hyphens)
        # Note: This is a simplified check.
        main_scripts = {s for s in scripts if s not in ['DIGIT', 'HYPHEN-MINUS', 'FULL']}
        return len(main_scripts) > 1

    def levenshtein_distance(self, s1, s2):
        """Calculates the edit distance between two strings."""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def analyze(self, url):
        """
        Analyzes the URL for spoofing techniques.
        Returns: (score_modifier, list_of_flags)
        """
        score = 0
        flags = []
        
        extracted = tldextract.extract(url)
        domain_label = extracted.domain
        
        # 1. IDN / Punycode Check
        # If the domain starts with 'xn--', it's an encoded IDN.
        if domain_label.startswith('xn--'):
            try:
                decoded_label = domain_label.encode('ascii').decode('idna')
                score += 20
                flags.append(f"Punycode Domain Detected ({decoded_label})")
                
                # Check mixed script on the decoded label
                if self.is_mixed_script(decoded_label):
                    score += 30
                    flags.append("Script Mixing Attack (Homoglyph)")
            except UnicodeError:
                pass

        # 2. Typosquatting / Levenshtein Distance
        # Check if the domain is "close" to a high-value target but not identical.
        # Only verify if it's not the target itself.
        if domain_label not in HIGH_VALUE_TARGETS:
            for target in HIGH_VALUE_TARGETS:
                dist = self.levenshtein_distance(domain_label, target)
                
                # Distance of 1 means one insertion/deletion/subst (e.g. gogle vs google)
                if dist == 1:
                    score += 30
                    flags.append(f"Typosquatting Detected (Target: {target})")
                    break # Stop after finding one match

        return score, flags
