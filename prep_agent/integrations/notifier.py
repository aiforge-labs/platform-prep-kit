"""Desktop notifications -- cross-platform notification delivery."""

import shutil
import subprocess
import sys
import os


class Notifier:
    """Cross-platform desktop notification sender."""

    def send(self, title: str, message: str, sound: bool = True) -> bool:
        """Send a desktop notification. Returns True if successful."""
        if sys.platform == "darwin":
            return self._macos_notify(title, message, sound)
        elif sys.platform.startswith("linux"):
            return self._linux_notify(title, message)
        elif sys.platform == "win32":
            return self._windows_notify(title, message)
        return False

    def _macos_notify(self, title: str, message: str, sound: bool) -> bool:
        """macOS notification via osascript."""
        escaped_title = title.replace('"', '\\"')
        escaped_message = message.replace('"', '\\"')
        sound_clause = ' sound name "default"' if sound else ""
        script = (
            f'display notification "{escaped_message}" '
            f'with title "{escaped_title}"{sound_clause}'
        )
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    def _linux_notify(self, title: str, message: str) -> bool:
        """Linux notification via notify-send."""
        if not shutil.which("notify-send"):
            return False
        try:
            result = subprocess.run(
                ["notify-send", title, message],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    def _windows_notify(self, title: str, message: str) -> bool:
        """Windows notification via PowerShell toast."""
        escaped_title = title.replace("'", "''")
        escaped_message = message.replace("'", "''")
        ps_script = (
            "[Windows.UI.Notifications.ToastNotificationManager, "
            "Windows.UI.Notifications, ContentType = WindowsRuntime] > $null; "
            "$template = [Windows.UI.Notifications.ToastNotificationManager]::"
            "GetTemplateContent("
            "[Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
            "$textNodes = $template.GetElementsByTagName('text'); "
            f"$textNodes.Item(0).AppendChild($template.CreateTextNode('{escaped_title}')) > $null; "
            f"$textNodes.Item(1).AppendChild($template.CreateTextNode('{escaped_message}')) > $null; "
            "$toast = [Windows.UI.Notifications.ToastNotification]::new($template); "
            "[Windows.UI.Notifications.ToastNotificationManager]::"
            "CreateToastNotifier('platform-prep-kit').Show($toast)"
        )
        try:
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=15,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    @staticmethod
    def is_available() -> bool:
        """Check if notifications are available on this platform."""
        if sys.platform == "darwin":
            return shutil.which("osascript") is not None
        elif sys.platform.startswith("linux"):
            return shutil.which("notify-send") is not None
        elif sys.platform == "win32":
            return shutil.which("powershell") is not None
        return False


def build_morning_notification(tracker_data: dict) -> tuple[str, str]:
    """Build contextual morning notification content.

    Args:
        tracker_data: Dict with keys like 'current_day', 'total_days',
            'today_topic', 'streak', 'missed_days'.

    Returns:
        (title, message) tuple.
    """
    day = tracker_data.get("current_day", 1)
    total = tracker_data.get("total_days", 30)
    topic = tracker_data.get("today_topic", "your next session")
    streak = tracker_data.get("streak", 0)

    title = f"Day {day}/{total} -- Time to Prep"

    parts: list[str] = [f"Today: {topic}"]

    if streak >= 7:
        parts.append(f"Incredible {streak}-day streak! Keep it going.")
    elif streak >= 3:
        parts.append(f"{streak}-day streak -- nice momentum!")
    elif streak == 0:
        missed = tracker_data.get("missed_days", 0)
        if missed > 0:
            parts.append("Fresh start today. You've got this.")

    # Milestone callouts
    if day == total:
        parts.append("Final day -- bring it home!")
    elif day == total // 2:
        parts.append("Halfway there!")

    message = " ".join(parts)
    return title, message


def build_evening_notification(tracker_data: dict) -> tuple[str, str]:
    """Build contextual evening notification content.

    Args:
        tracker_data: Dict with keys like 'current_day', 'total_days',
            'evening_focus', 'completed_today'.

    Returns:
        (title, message) tuple.
    """
    day = tracker_data.get("current_day", 1)
    total = tracker_data.get("total_days", 30)
    focus = tracker_data.get("evening_focus", "review today's material")
    completed = tracker_data.get("completed_today", False)

    if completed:
        title = f"Day {day}/{total} -- Great Work Today"
        message = f"Evening focus: {focus}. You already crushed today's session."
    else:
        title = f"Day {day}/{total} -- Evening Check-in"
        message = f"Still time to finish today. Focus: {focus}."

    return title, message


def build_weekly_summary(tracker_data: dict) -> tuple[str, str]:
    """Build weekly summary notification.

    Args:
        tracker_data: Dict with keys like 'days_studied', 'total_days_in_week',
            'quiz_avg', 'next_week_topic', 'streak'.

    Returns:
        (title, message) tuple.
    """
    studied = tracker_data.get("days_studied", 0)
    total_week = tracker_data.get("total_days_in_week", 7)
    quiz_avg = tracker_data.get("quiz_avg")
    next_topic = tracker_data.get("next_week_topic", "more practice")

    title = "Weekly Prep Summary"

    parts: list[str] = [f"Studied {studied}/{total_week} days this week."]

    if quiz_avg is not None:
        parts.append(f"Quiz avg: {quiz_avg:.0f}%.")

    if studied == total_week:
        parts.append("Perfect week!")
    elif studied >= total_week - 1:
        parts.append("Almost perfect -- strong effort.")
    elif studied < total_week // 2:
        parts.append("Room to grow next week.")

    parts.append(f"Up next: {next_topic}.")

    message = " ".join(parts)
    return title, message
