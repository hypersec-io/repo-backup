from github import Github
from typing import List
from .base import Repository, RepositoryManager
import logging
import os

class GitHubManager(RepositoryManager):
    def __init__(self, token: str, exclude_personal: bool = True):
        super().__init__(token, exclude_personal)
        self.client = Github(token)
        self.user = self.client.get_user()
        
        # Get organization filters from environment
        include_orgs_env = os.getenv('GITHUB_INCLUDE_ORGS', '')
        self.include_orgs = [o.strip() for o in include_orgs_env.split(',') if o.strip()] if include_orgs_env else None
        
        if self.include_orgs:
            self.logger.info(f"Filtering to GitHub organizations: {', '.join(self.include_orgs)}")
        else:
            self.logger.info(f"[CONFIG] Including all accessible GitHub repositories (user + all organizations)")
        
    def get_repositories(self) -> List[Repository]:
        repos = []
        
        # Check if we should include user repos
        include_user_repos = not self.include_orgs or 'user' in self.include_orgs
        
        # Get user's own repositories
        if include_user_repos:
            self.logger.info(f"[CONFIG] Fetching user's own GitHub repositories")
            for repo in self.client.get_user().get_repos():
                if self.exclude_personal and self.is_personal_repo(repo):
                    continue
                    
                repos.append(Repository(
                    name=repo.name,
                    clone_url=repo.clone_url.replace('https://', f'https://{self.token}@'),
                    owner=repo.owner.login,
                    is_private=repo.private,
                    is_fork=repo.fork,
                    is_owned_by_user=(repo.owner.login == self.user.login),
                    platform='github',
                    size_kb=repo.size,
                    default_branch=repo.default_branch
                ))
        
        # Get organization repositories
        if self.include_orgs:
            # If specific orgs are listed, try to access them directly
            for org_name in self.include_orgs:
                if org_name == 'user':
                    continue  # Already handled above
                    
                try:
                    org = self.client.get_organization(org_name)
                    self.logger.info(f"[CONFIG] Fetching repositories from GitHub organization: {org.login}")
                    
                    for repo in org.get_repos():
                        repos.append(Repository(
                            name=repo.name,
                            clone_url=repo.clone_url.replace('https://', f'https://{self.token}@'),
                            owner=repo.owner.login,
                            is_private=repo.private,
                            is_fork=repo.fork,
                            is_owned_by_user=False,
                            platform='github',
                            size_kb=repo.size,
                            default_branch=repo.default_branch
                        ))
                except Exception as e:
                    self.logger.warning(f"Could not access organization {org_name}: {e}")
        else:
            # Get all organizations the user is a member of
            for org in self.user.get_orgs():
                self.logger.info(f"[CONFIG] Fetching repositories from GitHub organization: {org.login}")
                
                for repo in org.get_repos():
                    repos.append(Repository(
                        name=repo.name,
                        clone_url=repo.clone_url.replace('https://', f'https://{self.token}@'),
                        owner=repo.owner.login,
                        is_private=repo.private,
                        is_fork=repo.fork,
                        is_owned_by_user=False,
                        platform='github',
                        size_kb=repo.size,
                        default_branch=repo.default_branch
                    ))
        
        return self.filter_corporate_repos(repos)
    
    def is_personal_repo(self, repo) -> bool:
        return repo.owner.login == self.user.login
    
    def is_corporate_repo(self, repo_data) -> bool:
        return repo_data.owner.type == 'Organization'