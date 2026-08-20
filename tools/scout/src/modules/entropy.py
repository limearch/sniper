# File: tools/scout/src/modules/entropy.py
# Description: module to calculate Shannon entropy and detect obfuscation/randomness.

import math
import re

class EntropyAnalyzer:
    """
    Analyzes strings for high entropy, which indicates randomness or encryption.
    High entropy in URLs often suggests DGA domains, encrypted payloads, or tokens.
    """

    def calculate_shannon_entropy(self, data):
        """
        Calculates the Shannon entropy of a string.
        Formula: H(X) = -sum(p(x) * log2(p(x)))
        """
        if not data:
            return 0.0
            
        entropy = 0.0
        length = len(data)
        
        # Calculate frequency of each character
        frequencies = {}
        for char in data:
            frequencies[char] = frequencies.get(char, 0) + 1
            
        # Calculate entropy
        for count in frequencies.values():
            p_x = float(count) / length
            if p_x > 0:
                entropy -= p_x * math.log(p_x, 2)
                
        return entropy

    def analyze(self, domain, path, query):
        """
        Analyzes URL components for suspicious entropy levels.
        Returns: (score_modifier, list_of_flags)
        """
        score = 0
        flags = []

        # 1. Domain Entropy (DGA Detection)
        # English text usually has entropy between 3.5 and 4.5.
        # Random strings (e.g., 'kjhsdgf876234') often exceed 4.5 or 5.0.
        domain_entropy = self.calculate_shannon_entropy(domain)
        if domain_entropy > 4.5:
            # We penalize high entropy, but exclude IPs which naturally have low char variety
            if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
                score += 20
                flags.append(f"High Entropy Domain ({domain_entropy:.2f})")

        # 2. Path/Query Entropy (Obfuscation/Token Detection)
        # Long, high-entropy paths often hide payloads.
        full_path = path + query
        if len(full_path) > 20:
            path_entropy = self.calculate_shannon_entropy(full_path)
            if path_entropy > 5.0:
                score += 15
                flags.append(f"High Entropy Path/Query ({path_entropy:.2f})")

        # 3. Base64/Hex Pattern Detection
        # Look for long strings that look like Base64 (a-zA-Z0-9+/=)
        # Heuristic: continuous string > 30 chars with valid b64 chars
        if re.search(r'[A-Za-z0-9+/]{40,}={0,2}', full_path):
            score += 15
            flags.append("Suspicious Base64-like String")

        return score, flags
