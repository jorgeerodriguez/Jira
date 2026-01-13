"""
Slack Notifier Module
Sends notifications to Slack using webhooks
"""

import json
import urllib.request
import urllib.error
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Handles sending notifications to Slack via webhooks"""
    
    def __init__(self, webhook_url: str, channel: str = None):
        """
        Initialize Slack notifier
        
        Args:
            webhook_url: Slack incoming webhook URL
            channel: Default channel to post to (optional, can be overridden per message)
        """
        self.webhook_url = webhook_url
        self.default_channel = channel
    
    def send_message(self, text: str, channel: str = None, username: str = "Jira Bot") -> bool:
        """
        Send a simple text message to Slack
        
        Args:
            text: Message text
            channel: Channel to post to (overrides default)
            username: Bot username to display
            
        Returns:
            True if message sent successfully
        """
        payload = {
            "text": text,
            "username": username
        }
        
        if channel or self.default_channel:
            payload["channel"] = channel or self.default_channel
        
        return self._send_payload(payload)
    
    def send_blocks(self, blocks: List[Dict], text: str = None, channel: str = None) -> bool:
        """
        Send a message with Slack Block Kit formatting
        
        Args:
            blocks: List of block dictionaries
            text: Fallback text for notifications
            channel: Channel to post to
            
        Returns:
            True if message sent successfully
        """
        payload = {
            "blocks": blocks,
            "text": text or "New Jira Report"
        }
        
        if channel or self.default_channel:
            payload["channel"] = channel or self.default_channel
        
        return self._send_payload(payload)
    
    def send_report(self, digest: Dict) -> bool:
        """
        Send a formatted daily digest report to Slack
        
        Args:
            digest: Daily digest dictionary from ReportGenerator
            
        Returns:
            True if message sent successfully
        """
        logger.info("Formatting and sending digest to Slack...")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 Jira Daily Digest - {digest['date']}"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        for project in digest.get("projects", []):
            project_key = project["project_key"]
            
            # Project header
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📁 Project: {project_key}*"
                }
            })
            
            # Status Summary
            status = project["status_summary"]
            status_text = f"*Status Summary* (Total: {status['total_issues']} issues)\n"
            for status_name, data in list(status["by_status"].items())[:5]:  # Top 5 statuses
                status_text += f"• {status_name}: {data['count']} ({data['percentage']:.1f}%)\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": status_text
                }
            })
            
            # Blocked Issues
            blocked = project["blocked_issues"]
            if blocked["total_blocked"] > 0:
                blocked_text = f"*🚫 Blocked Issues:* {blocked['total_blocked']}\n"
                for issue in blocked["issues"][:3]:  # Show top 3
                    blocked_text += f"• `{issue['key']}` - {issue['summary'][:50]}...\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": blocked_text
                    }
                })
            
            # In Progress highlights
            in_prog = project["in_progress"]
            if in_prog["without_dates"] or in_prog["behind_schedule"]:
                in_prog_text = f"*🔄 In Progress Issues:* {in_prog['total_in_progress']}\n"
                if in_prog["without_dates"]:
                    in_prog_text += f"⚠️ {len(in_prog['without_dates'])} without dates\n"
                if in_prog["behind_schedule"]:
                    in_prog_text += f"⚠️ {len(in_prog['behind_schedule'])} behind schedule\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": in_prog_text
                    }
                })
            
            # Old Backlog
            old_backlog = project["old_backlog"]
            if old_backlog["total_old_backlog"] > 0:
                backlog_text = (
                    f"*⏰ Old Backlog* (>{old_backlog['age_threshold_days']} days): "
                    f"{old_backlog['total_old_backlog']} issues\n"
                )
                for issue in old_backlog["issues"][:2]:  # Show top 2
                    backlog_text += f"• `{issue['key']}` - {issue['age_days']} days old\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": backlog_text
                    }
                })
            
            blocks.append({"type": "divider"})
        
        # Footer
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Report generated at {digest['generated_at']}"
                }
            ]
        })
        
        return self.send_blocks(blocks, text=f"Jira Daily Digest - {digest['date']}")
    
    def send_simple_report(self, digest: Dict) -> bool:
        """
        Send a simplified text-only report to Slack
        
        Args:
            digest: Daily digest dictionary
            
        Returns:
            True if sent successfully
        """
        text_lines = [f"📊 *Jira Daily Digest - {digest['date']}*\n"]
        
        for project in digest.get("projects", []):
            project_key = project["project_key"]
            status = project["status_summary"]
            blocked = project["blocked_issues"]
            in_prog = project["in_progress"]
            old_backlog = project["old_backlog"]
            
            text_lines.append(f"\n*Project: {project_key}*")
            text_lines.append(f"📈 Total Issues: {status['total_issues']}")
            
            if blocked["total_blocked"] > 0:
                text_lines.append(f"🚫 Blocked: {blocked['total_blocked']}")
            
            if in_prog["total_in_progress"] > 0:
                text_lines.append(f"🔄 In Progress: {in_prog['total_in_progress']}")
                if in_prog["without_dates"]:
                    text_lines.append(f"  ⚠️ {len(in_prog['without_dates'])} without dates")
            
            if old_backlog["total_old_backlog"] > 0:
                text_lines.append(
                    f"⏰ Old Backlog (>{old_backlog['age_threshold_days']}d): "
                    f"{old_backlog['total_old_backlog']}"
                )
        
        text_lines.append(f"\n_Generated at {digest['generated_at']}_")
        
        return self.send_message("\n".join(text_lines))
    
    def _send_payload(self, payload: Dict) -> bool:
        """
        Send payload to Slack webhook
        
        Args:
            payload: Dictionary payload to send
            
        Returns:
            True if successful
        """
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                self.webhook_url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    logger.info("Successfully sent message to Slack")
                    return True
                else:
                    logger.error(f"Slack API returned status {response.status}")
                    return False
                    
        except urllib.error.HTTPError as e:
            logger.error(f"HTTP Error sending to Slack: {e.code} - {e.reason}")
            return False
        except urllib.error.URLError as e:
            logger.error(f"URL Error sending to Slack: {e.reason}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending to Slack: {e}")
            return False


def create_slack_notifier(config: dict) -> SlackNotifier:
    """
    Factory function to create Slack notifier
    
    Args:
        config: Slack configuration with keys:
               - webhook_url: Slack webhook URL (required)
               - channel: Default channel (optional)
    
    Returns:
        SlackNotifier instance
    """
    webhook_url = config.get('webhook_url')
    if not webhook_url:
        raise ValueError("Slack webhook_url is required")
    
    channel = config.get('channel')
    return SlackNotifier(webhook_url, channel)
