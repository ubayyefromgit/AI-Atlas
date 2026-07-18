from abc import ABC, abstractmethod
from typing import List
from schemas.discovery import EvidenceItem

class DiscoveryProvider(ABC):
    @abstractmethod
    def search(self, query: str, max_results: int = 10) -> List[EvidenceItem]:
        """
        Executes a search query and returns collected evidence.
        """
        pass
