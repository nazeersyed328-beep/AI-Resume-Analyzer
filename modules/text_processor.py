"""
Text Processor Module
Responsible for cleaning, normalizing, sanitizing, and tokenizing text data
from resumes and job descriptions while preserving programming symbols (C++, C#, .NET, Node.js).
"""

import re
from typing import List, Set, Dict

# Standard English stopwords (common grammatical words with no domain meaning)
STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", 
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", 
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", 
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", 
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", 
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", 
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", 
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", 
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", 
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", 
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", 
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", 
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", 
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", 
    "they've", "this", "those", "through", "to", "too", "under", "until", "up", 
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", 
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", 
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", 
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", 
    "yourself", "yourselves"
}

# Regex patterns for PII detection
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
PHONE_REGEX = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,5}'
URL_REGEX = r'https?://\S+|www\.\S+|linkedin\.com/\S+|github\.com/\S+'


def detect_pii(text: str) -> Dict[str, List[str]]:
    """
    Detects Personally Identifiable Information (PII) such as emails, phone numbers,
    and profile URLs from resume text.
    """
    if not text or not isinstance(text, str):
        return {"emails": [], "phones": [], "urls": []}

    emails = re.findall(EMAIL_REGEX, text)
    phones = re.findall(PHONE_REGEX, text)
    urls = re.findall(URL_REGEX, text, re.IGNORECASE)

    # Filter out false-positive short phone numbers
    valid_phones = [p.strip() for p in phones if len(re.sub(r'\D', '', p)) >= 10]

    return {
        "emails": sorted(list(set(emails))),
        "phones": sorted(list(set(valid_phones))),
        "urls": sorted(list(set(urls)))
    }


def sanitize_pii(text: str, mask: bool = False) -> str:
    """
    Removes or masks emails, phone numbers, and URLs to ensure privacy.
    """
    if not text or not isinstance(text, str):
        return ""

    replacement = "[REDACTED]" if mask else " "
    sanitized = re.sub(EMAIL_REGEX, replacement, text)
    sanitized = re.sub(PHONE_REGEX, replacement, sanitized)
    sanitized = re.sub(URL_REGEX, replacement, sanitized, flags=re.IGNORECASE)
    return sanitized


def clean_text(text: str) -> str:
    """
    Cleans raw text while strictly preserving technology identifiers
    (e.g., C++, C#, .NET, Node.js, Scikit-learn).
    
    Steps:
    1. Converts text to lowercase.
    2. Removes PII (emails, phone numbers, URLs).
    3. Preserves alphanumeric characters, spaces, and specific symbols (+, #, -, .).
    4. Collapses multiple spaces and newlines into single spaces.
    """
    if not text or not isinstance(text, str):
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove PII (emails, phones, URLs)
    text = sanitize_pii(text, mask=False)

    # Replace special punctuation with space, but preserve +, #, -, and dots inside words
    # e.g., preserve c++, c#, .net, node.js, scikit-learn
    text = re.sub(r'[^\w\s\+\#\-\.]', ' ', text)

    # Replace standalone dots/hyphens that are not part of words
    text = re.sub(r'(?<=\s)[-\.](?=\s)', ' ', text)

    # Collapse multiple whitespaces and tabs into a single space
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def tokenize(text: str) -> List[str]:
    """
    Splits cleaned text into individual word tokens.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []
    return cleaned.split()


def remove_stopwords(tokens: List[str]) -> List[str]:
    """
    Filters out common grammatical English stopwords from a token list.
    """
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]
