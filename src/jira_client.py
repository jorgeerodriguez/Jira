"""
Jira Client for connecting to Jira and fetching data
"""

from jira import JIRA
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JiraClient:
    """Wrapper for Jira API interactions"""
    
    def __init__(self, server: str, email: str, api_token: str):
        """
        Initialize Jira client
        
        Args:
            server: Jira server URL
            email: User email for authentication
            api_token: API token for authentication
        """
        self.server = server
        self.email = email
        self.api_token = api_token
        self.jira = None
        
    def connect(self) -> bool:
        """
        Establish connection to Jira
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            jira_options = {'server': self.server}
            self.jira = JIRA(options=jira_options, basic_auth=(self.email, self.api_token))
            logger.info(f"Successfully connected to Jira at {self.server}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to Jira: {e}")
            return False
    
    def get_projects(self) -> List:
        """Get all projects"""
        if not self.jira:
            raise RuntimeError("Not connected to Jira. Call connect() first.")
        return self.jira.projects()
    
    def get_boards(self) -> List:
        """Get all boards"""
        if not self.jira:
            raise RuntimeError("Not connected to Jira. Call connect() first.")
        return self.jira.boards()
    
    def search_issues(self, jql: str, max_results: int = 1000, fields: str = '*all') -> List:
        """
        Search for issues using JQL
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results to return
            fields: Fields to retrieve
            
        Returns:
            List of issues
        """
        if not self.jira:
            raise RuntimeError("Not connected to Jira. Call connect() first.")
        
        try:
            issues = self.jira.search_issues(jql, maxResults=max_results, fields=fields)
            logger.info(f"Found {len(issues)} issues matching query")
            return issues
        except Exception as e:
            logger.error(f"Error searching issues: {e}")
            return []
    
    def get_project_issues(self, project_key: str, status: Optional[str] = None) -> List:
        """
        Get issues for a specific project
        
        Args:
            project_key: Project key (e.g., 'DEVOPS')
            status: Optional status filter
            
        Returns:
            List of issues
        """
        jql = f'project = {project_key}'
        if status:
            jql += f' AND status = "{status}"'
        
        return self.search_issues(jql)
    
    def get_issues_by_status(self, project_key: str = None) -> Dict[str, List]:
        """
        Get issues grouped by status
        
        Args:
            project_key: Optional project key to filter by
            
        Returns:
            Dictionary mapping status to list of issues
        """
        jql = f'project = {project_key}' if project_key else 'ORDER BY created DESC'
        issues = self.search_issues(jql)
        
        status_map = {}
        for issue in issues:
            status = str(issue.fields.status)
            if status not in status_map:
                status_map[status] = []
            status_map[status].append(issue)
        
        return status_map
    
    def get_issues_in_progress(self, project_key: str = None) -> List:
        """Get issues currently in progress"""
        jql = 'status = "In Progress"'
        if project_key:
            jql = f'project = {project_key} AND {jql}'
        
        return self.search_issues(jql)
    
    def get_blocked_issues(self, project_key: str = None) -> List:
        """Get blocked issues"""
        jql = 'status = "Blocked"'
        if project_key:
            jql = f'project = {project_key} AND {jql}'
        
        return self.search_issues(jql)
    
    def get_old_backlog_issues(self, project_key: str = None, days: int = 50) -> List:
        """
        Get backlog issues older than specified days
        
        Args:
            project_key: Optional project key
            days: Number of days threshold
            
        Returns:
            List of old backlog issues
        """
        jql = f'status = "Backlog" AND created <= -{days}d'
        if project_key:
            jql = f'project = {project_key} AND {jql}'
        
        return self.search_issues(jql)
    
    def get_custom_fields(self) -> Dict[str, str]:
        """
        Get mapping of custom field IDs to names
        
        Returns:
            Dictionary mapping field ID to field name
        """
        if not self.jira:
            raise RuntimeError("Not connected to Jira. Call connect() first.")
        
        all_fields = self.jira.fields()
        return {field['id']: field['name'] for field in all_fields if field.get('custom', False)}
