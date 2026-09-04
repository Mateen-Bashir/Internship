"""
NLP Text Preprocessor for Skill Extraction & Text Normalization.
Cleans raw job descriptions and intern skill statements while preserving
technical terms (e.g. scikit-learn, c++, node.js, ci/cd, vue.js, etc.).
"""

import re
import string

# Tech terms mapping/preservation dictionary
TECH_PRESERVE = {
    "c++": "cpp_lang",
    "c#": "csharp_lang",
    ".net": "dotnet_framework",
    "node.js": "nodejs",
    "express.js": "expressjs",
    "react.js": "react",
    "vue.js": "vuejs",
    "next.js": "nextjs",
    "scikit-learn": "scikitlearn",
    "ci/cd": "cicd_pipelines",
    "tcp/ip": "tcpip_networking",
    "power bi": "powerbi",
    "rest api": "rest_api",
    "restful api": "rest_api",
    "deep learning": "deep_learning",
    "machine learning": "machine_learning",
    "natural language processing": "nlp",
    "computer vision": "computer_vision",
    "network security": "network_security",
    "ethical hacking": "ethical_hacking",
    "data visualization": "data_visualization",
    "feature engineering": "feature_engineering",
    "statistical modeling": "statistical_modeling",
    "time series": "time_series"
}

# Standard English stopwords + generic filler words
STOPWORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers",
    "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if",
    "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most",
    "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd",
    "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the",
    "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd",
    "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why",
    "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
    "your", "yours", "yourself", "yourselves",
    # Generic hiring noise words
    "seeking", "looking", "responsibilities", "responsible", "join", "team", "motivated", "energetic",
    "candidate", "applicant", "work", "working", "experience", "required", "requirements", "including",
    "strong", "hands", "on", "key", "environments", "collaborative", "continuous", "agile", "must",
    "have", "ability", "proficient", "proficiency", "good", "knowledge", "years", "plus", "role"
])

def clean_text(text: str) -> str:
    """Cleans, normalizes, and tokenizes text while preserving key tech terms."""
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    
    # Replace compound tech terms
    for term, replacement in TECH_PRESERVE.items():
        text = text.replace(term, replacement)
    
    # Replace punctuation (except underscores which protect compound terms)
    punct_to_remove = string.punctuation.replace("_", "")
    translator = str.maketrans(punct_to_remove, " " * len(punct_to_remove))
    text = text.translate(translator)
    
    # Remove digits and multiple spaces
    text = re.sub(r"\d+", " ", text)
    tokens = text.split()
    
    # Filter stopwords and short tokens
    cleaned_tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    
    return " ".join(cleaned_tokens)

def parse_skills_list(skills_str: str) -> list:
    """Parses a comma/semicolon delimited string of skills into a normalized list."""
    if not isinstance(skills_str, str):
        return []
    
    skills = [s.strip() for s in re.split(r"[,;]+", skills_str) if s.strip()]
    return skills

if __name__ == "__main__":
    sample = "We are seeking a Machine Learning Engineer with experience in PyTorch, Scikit-Learn, CI/CD, and REST APIs."
    print("Raw Sample:", sample)
    print("Cleaned:", clean_text(sample))
