"""
Report Generator for Jira data
Consolidates various report types into reusable classes
"""

from typing import List, Dict
from datetime import datetime
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates various reports from Jira data"""
    
    def __init__(self, jira_client):
        """
        Initialize report generator
        
        Args:
            jira_client: JiraClient instance
        """
        self.jira_client = jira_client
    
    def generate_status_summary(self, project_key: str = None) -> Dict:
        """
        Generate status summary report
        
        Args:
            project_key: Optional project key to filter by
            
        Returns:
            Dictionary with status counts and details
        """
        logger.info("Generating status summary report...")
        
        issues_by_status = self.jira_client.get_issues_by_status(project_key)
        
        summary = {
            "total_issues": sum(len(issues) for issues in issues_by_status.values()),
            "by_status": {},
            "generated_at": datetime.now().isoformat()
        }
        
        for status, issues in issues_by_status.items():
            summary["by_status"][status] = {
                "count": len(issues),
                "percentage": 0  # Will calculate after
            }
        
        # Calculate percentages
        if summary["total_issues"] > 0:
            for status_data in summary["by_status"].values():
                status_data["percentage"] = (status_data["count"] / summary["total_issues"]) * 100
        
        return summary
    
    def generate_blocked_issues_report(self, project_key: str = None) -> Dict:
        """Generate report of blocked issues"""
        logger.info("Generating blocked issues report...")
        
        blocked_issues = self.jira_client.get_blocked_issues(project_key)
        
        report = {
            "total_blocked": len(blocked_issues),
            "issues": [],
            "generated_at": datetime.now().isoformat()
        }
        
        for issue in blocked_issues:
            report["issues"].append({
                "key": issue.key,
                "summary": issue.fields.summary,
                "assignee": str(issue.fields.assignee) if issue.fields.assignee else "Unassigned",
                "created": str(issue.fields.created),
                "priority": str(issue.fields.priority) if hasattr(issue.fields, 'priority') else "Unknown"
            })
        
        return report
    
    def generate_in_progress_report(self, project_key: str = None) -> Dict:
        """Generate report of issues in progress"""
        logger.info("Generating in-progress issues report...")
        
        in_progress = self.jira_client.get_issues_in_progress(project_key)
        
        report = {
            "total_in_progress": len(in_progress),
            "issues": [],
            "without_dates": [],
            "behind_schedule": [],
            "generated_at": datetime.now().isoformat()
        }
        
        for issue in in_progress:
            issue_data = {
                "key": issue.key,
                "summary": issue.fields.summary,
                "assignee": str(issue.fields.assignee) if issue.fields.assignee else "Unassigned",
                "created": str(issue.fields.created)
            }
            
            report["issues"].append(issue_data)
            
            # Check if due date is set
            if hasattr(issue.fields, 'duedate') and issue.fields.duedate:
                due_date = datetime.strptime(issue.fields.duedate, '%Y-%m-%d')
                if due_date < datetime.now():
                    report["behind_schedule"].append(issue_data)
            else:
                report["without_dates"].append(issue_data)
        
        return report
    
    def generate_old_backlog_report(self, project_key: str = None, days: int = 50) -> Dict:
        """
        Generate report of old backlog items
        
        Args:
            project_key: Optional project key
            days: Age threshold in days
            
        Returns:
            Report dictionary
        """
        logger.info(f"Generating old backlog report (>{days} days)...")
        
        old_issues = self.jira_client.get_old_backlog_issues(project_key, days)
        
        report = {
            "total_old_backlog": len(old_issues),
            "age_threshold_days": days,
            "issues": [],
            "generated_at": datetime.now().isoformat()
        }
        
        for issue in old_issues:
            created_date = datetime.strptime(str(issue.fields.created)[:10], '%Y-%m-%d')
            age_days = (datetime.now() - created_date).days
            
            report["issues"].append({
                "key": issue.key,
                "summary": issue.fields.summary,
                "created": str(issue.fields.created),
                "age_days": age_days,
                "assignee": str(issue.fields.assignee) if issue.fields.assignee else "Unassigned"
            })
        
        # Sort by age (oldest first)
        report["issues"].sort(key=lambda x: x["age_days"], reverse=True)
        
        return report
    
    def generate_assignee_distribution(self, project_key: str = None) -> Dict:
        """Generate distribution of issues by assignee"""
        logger.info("Generating assignee distribution report...")
        
        jql = f'project = {project_key}' if project_key else 'ORDER BY created DESC'
        issues = self.jira_client.search_issues(jql, max_results=1000)
        
        assignee_counts = Counter()
        for issue in issues:
            assignee = str(issue.fields.assignee) if issue.fields.assignee else "Unassigned"
            assignee_counts[assignee] += 1
        
        report = {
            "total_issues": len(issues),
            "distribution": [
                {"assignee": assignee, "count": count, "percentage": (count / len(issues)) * 100}
                for assignee, count in assignee_counts.most_common()
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def generate_daily_digest(self, project_keys: List[str] = None) -> Dict:
        """
        Generate comprehensive daily digest report
        
        Args:
            project_keys: List of project keys to include
            
        Returns:
            Comprehensive daily digest
        """
        logger.info("Generating daily digest...")
        
        digest = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "generated_at": datetime.now().isoformat(),
            "projects": []
        }
        
        projects = project_keys or [p.key for p in self.jira_client.get_projects()[:5]]
        
        for project_key in projects:
            try:
                project_data = {
                    "project_key": project_key,
                    "status_summary": self.generate_status_summary(project_key),
                    "blocked_issues": self.generate_blocked_issues_report(project_key),
                    "in_progress": self.generate_in_progress_report(project_key),
                    "old_backlog": self.generate_old_backlog_report(project_key, days=50)
                }
                digest["projects"].append(project_data)
            except Exception as e:
                logger.error(f"Error generating report for project {project_key}: {e}")
        
        return digest
    
    def format_digest_as_text(self, digest: Dict) -> str:
        """
        Format daily digest as plain text
        
        Args:
            digest: Daily digest dictionary
            
        Returns:
            Formatted text string
        """
        lines = [
            "=" * 80,
            f"JIRA DAILY DIGEST - {digest['date']}",
            "=" * 80,
            ""
        ]
        
        for project in digest["projects"]:
            lines.append(f"\n📊 PROJECT: {project['project_key']}")
            lines.append("-" * 80)
            
            # Status Summary
            status = project["status_summary"]
            lines.append(f"\n📈 STATUS SUMMARY (Total: {status['total_issues']} issues)")
            for status_name, data in status["by_status"].items():
                lines.append(f"  • {status_name}: {data['count']} ({data['percentage']:.1f}%)")
            
            # Blocked Issues
            blocked = project["blocked_issues"]
            if blocked["total_blocked"] > 0:
                lines.append(f"\n🚫 BLOCKED ISSUES: {blocked['total_blocked']}")
                for issue in blocked["issues"][:5]:  # Show top 5
                    lines.append(f"  • {issue['key']}: {issue['summary'][:60]}... (Assignee: {issue['assignee']})")
            
            # In Progress
            in_prog = project["in_progress"]
            lines.append(f"\n🔄 IN PROGRESS: {in_prog['total_in_progress']}")
            if in_prog["without_dates"]:
                lines.append(f"  ⚠️  {len(in_prog['without_dates'])} issues without dates")
            if in_prog["behind_schedule"]:
                lines.append(f"  ⚠️  {len(in_prog['behind_schedule'])} issues behind schedule")
            
            # Old Backlog
            old_backlog = project["old_backlog"]
            if old_backlog["total_old_backlog"] > 0:
                lines.append(f"\n⏰ OLD BACKLOG (>{old_backlog['age_threshold_days']} days): {old_backlog['total_old_backlog']}")
                for issue in old_backlog["issues"][:3]:  # Show top 3 oldest
                    lines.append(f"  • {issue['key']}: {issue['age_days']} days old - {issue['summary'][:50]}...")
            
            lines.append("")
        
        lines.append("=" * 80)
        lines.append(f"Report generated at: {digest['generated_at']}")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def format_digest_as_html(self, digest: Dict) -> str:
        """
        Format daily digest as HTML
        
        Args:
            digest: Daily digest dictionary
            
        Returns:
            Formatted HTML string
        """
        html_parts = [
            "<html><head><style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            "h1 { color: #0052CC; border-bottom: 3px solid #0052CC; }",
            "h2 { color: #172B4D; margin-top: 30px; }",
            "h3 { color: #5E6C84; }",
            ".status-item { margin: 10px 0; padding: 10px; background: #F4F5F7; border-radius: 3px; }",
            ".issue-item { margin: 5px 0; padding: 8px; background: #FAFBFC; border-left: 3px solid #0052CC; }",
            ".warning { border-left-color: #FF5630; }",
            ".blocked { border-left-color: #FF5630; background: #FFEBE6; }",
            "</style></head><body>",
            f"<h1>📊 JIRA Daily Digest - {digest['date']}</h1>",
        ]
        
        for project in digest["projects"]:
            html_parts.append(f"<h2>Project: {project['project_key']}</h2>")
            
            # Status Summary
            status = project["status_summary"]
            html_parts.append(f"<h3>📈 Status Summary (Total: {status['total_issues']} issues)</h3>")
            html_parts.append("<div>")
            for status_name, data in status["by_status"].items():
                html_parts.append(
                    f"<div class='status-item'><strong>{status_name}:</strong> "
                    f"{data['count']} issues ({data['percentage']:.1f}%)</div>"
                )
            html_parts.append("</div>")
            
            # Blocked Issues
            blocked = project["blocked_issues"]
            if blocked["total_blocked"] > 0:
                html_parts.append(f"<h3>🚫 Blocked Issues: {blocked['total_blocked']}</h3>")
                for issue in blocked["issues"][:5]:
                    html_parts.append(
                        f"<div class='issue-item blocked'><strong>{issue['key']}:</strong> "
                        f"{issue['summary']}<br/><small>Assignee: {issue['assignee']}</small></div>"
                    )
            
            # In Progress
            in_prog = project["in_progress"]
            html_parts.append(f"<h3>🔄 In Progress: {in_prog['total_in_progress']}</h3>")
            if in_prog["without_dates"]:
                html_parts.append(
                    f"<div class='issue-item warning'>"
                    f"⚠️ {len(in_prog['without_dates'])} issues without dates</div>"
                )
            if in_prog["behind_schedule"]:
                html_parts.append(
                    f"<div class='issue-item warning'>"
                    f"⚠️ {len(in_prog['behind_schedule'])} issues behind schedule</div>"
                )
            
            # Old Backlog
            old_backlog = project["old_backlog"]
            if old_backlog["total_old_backlog"] > 0:
                html_parts.append(
                    f"<h3>⏰ Old Backlog (>{old_backlog['age_threshold_days']} days): "
                    f"{old_backlog['total_old_backlog']}</h3>"
                )
                for issue in old_backlog["issues"][:3]:
                    html_parts.append(
                        f"<div class='issue-item'><strong>{issue['key']}:</strong> "
                        f"{issue['age_days']} days old<br/>{issue['summary']}</div>"
                    )
        
        html_parts.append(f"<p><small>Report generated at: {digest['generated_at']}</small></p>")
        html_parts.append("</body></html>")
        
        return "\n".join(html_parts)
