import enum

class CompanyStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class DiscoveryStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class SourceType(str, enum.Enum):
    COMPANY = "company"
    PROBLEM = "problem"
    SECTOR = "sector"
    NEWS = "news"
    DISCOVERY = "discovery"

class EmbeddingStatus(str, enum.Enum):
    PENDING = "pending"
    INDEXED = "indexed"
    FAILED = "failed"
