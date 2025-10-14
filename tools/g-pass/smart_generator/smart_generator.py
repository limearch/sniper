# smart_generator/smart_generator.py
import sys
import random
import string

# A simple wordlist for generating human-readable passphrases
WORDLIST = [
    "Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel",
    "India", "Juliett", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa",
    "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", "Whiskey",
    "Xray", "Yankee", "Zulu", "Red", "Blue", "Green", "Gold", "Silver"
]

# Keyword analysis mapping
# Maps keywords to password generation parameter adjustments
KEYWORD_MAP = {
    # Security Level
    ("bank", "secure", "strong", "crypto", "root", "admin", "wallet"): {
        "length_mod": 6, "symbols": True, "numbers": True, "uppercase": True, "lowercase": True
    },
    # Memorability
    ("easy", "remember", "memorable", "human"): {
        "length_mod": -4, "use_words": True, "symbols": True, "numbers": True
    },
    # Context
    ("wifi", "network"): {
        "length": 12, "symbols": False, "exclude": "Il1O0"
    },
    ("email", "website", "login", "account"): {
        "length": 16, "symbols": True
    },
    # Simplicity
    ("simple", "basic", "weak", "test"): {
        "length": 8, "symbols": False, "uppercase": False
    }
}

def generate_random_string(length, charset):
    """Generates a truly random string from a given charset."""
    if not charset:
        return ""
    return ''.join(random.choice(charset) for _ in range(length))

def generate_human_readable(length, use_symbols=True, use_numbers=True):
    """Generates an XKCD-style passphrase."""
    words = random.sample(WORDLIST, k=min(4, len(WORDLIST)))
    password = "-".join(words)
    if use_numbers:
        password += str(random.randint(10, 99))
    if use_symbols:
        password += random.choice("!@#$%*")
    return password

def analyze_prompt(prompt):
    """Analyzes the prompt and returns a set of password generation parameters."""
    params = {
        "length": 16,
        "length_mod": 0,
        "lowercase": True,
        "uppercase": True,
        "numbers": True,
        "symbols": True,
        "use_words": False,
        "exclude": ""
    }
    
    prompt_lower = prompt.lower()
    
    for keywords, adjustments in KEYWORD_MAP.items():
        for keyword in keywords:
            if keyword in prompt_lower:
                params.update(adjustments)
                
    params["length"] += params["length_mod"]
    params["length"] = max(8, min(params["length"], 64)) # Clamp length between 8 and 64
    
    return params

def main():
    if len(sys.argv) < 2:
        print("Error: No prompt provided.", file=sys.stderr)
        sys.exit(1)
        
    prompt = sys.argv[1]
    params = analyze_prompt(prompt)
    
    if params["use_words"]:
        password = generate_human_readable(
            params["length"],
            params["symbols"],
            params["numbers"]
        )
    else:
        charset = ""
        if params["lowercase"]: charset += string.ascii_lowercase
        if params["uppercase"]: charset += string.ascii_uppercase
        if params["numbers"]: charset += string.digits
        if params["symbols"]: charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Filter excluded characters
        if params["exclude"]:
            charset = ''.join(c for c in charset if c not in params["exclude"])

        password = generate_random_string(params["length"], charset)

    # Print the final password to stdout for the C++ parent to capture
    print(password)

if __name__ == "__main__":
    main()
