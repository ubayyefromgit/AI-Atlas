import re
from typing import List, Set

class CitationExtractor:
    """
    Extracts citation markers (e.g., [S1], [S2]) from the LLM's response.
    """
    
    def extract_markers(self, text: str) -> Set[str]:
        """
        Finds all unique markers like [S1], [S12] in the text.
        Returns a set of strings like {'S1', 'S2'}
        """
        # Regex to find [S followed by digits]
        matches = re.findall(r'\[(S\d+)\]', text)
        return set(matches)
