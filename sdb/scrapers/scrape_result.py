from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ScrapeResult:
    article_list: List[dict] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None