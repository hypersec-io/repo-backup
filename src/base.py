from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass

@dataclass
class Repository:
    name: str
    clone_url: str
    owner: str
    is_private: bool
    is_fork: bool
    is_owned_by_user: bool
    platform: str
    size_kb: Optional[int] = None
    default_branch: Optional[str] = None

class RepositoryManager(ABC):
    def __init__(self, token: str, exclude_personal: bool = True):
        self.token = token
        self.exclude_personal = exclude_personal
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def get_repositories(self) -> List[Repository]:
        pass
    
    @abstractmethod
    def is_corporate_repo(self, repo_data: Any) -> bool:
        pass
    
    def filter_corporate_repos(self, repos: List[Repository]) -> List[Repository]:
        if self.exclude_personal:
            return [r for r in repos if not r.is_owned_by_user and not r.is_fork]
        return repos