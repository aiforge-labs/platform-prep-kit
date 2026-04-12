"""Reminder scheduler -- installs/manages OS-level scheduled reminders."""

import json
import os
import shutil
import subprocess
import sys
import textwrap
from datetime import datetime, timedelta
from pathlib import Path


class Scheduler:
    """Cross-platform scheduler for prep reminders using OS-native mechanisms."""

    PLIST_PREFIX = "com.career-prep-agent"
    CRON_MARKER = "# career-prep-agent reminder"
    TASK_PREFIX = "CareerPrepAgent"

    def __init__(self, prep_dir: str | None = None):
        self.prep_dir = prep_dir or os.path.expanduser("~/.prep")
        self.schedule_file = os.path.join(self.prep_dir, "schedule.json")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def install(
        self, morning_time: str = "07:00", evening_time: str = "19:00"
    ) -> bool:
        """Install scheduled reminders. Returns True if successful."""
        os.makedirs(self.prep_dir, exist_ok=True)

        success = False
        if sys.platform == "darwin":
            success = self._install_macos(morning_time, evening_time)
        elif sys.platform.startswith("linux"):
            success = self._install_linux(morning_time, evening_time)
        elif sys.platform == "win32":
            success = self._install_windows(morning_time, evening_time)

        if success:
            self._save_state(
                {
                    "installed": True,
                    "paused": False,
                    "morning_time": morning_time,
                    "evening_time": evening_time,
                    "installed_at": datetime.now().isoformat(),
                }
            )
        return success

    def uninstall(self) -> bool:
        """Remove all scheduled reminders."""
        success = False
        if sys.platform == "darwin":
            success = self._uninstall_macos()
        elif sys.platform.startswith("linux"):
            success = self._uninstall_linux()
        elif sys.platform == "win32":
            success = self._uninstall_windows()

        if success:
            state = self._load_state()
            state["installed"] = False
            state["paused"] = False
            self._save_state(state)
        return success

    def pause(
        self, until: str | None = None, hours: int | None = None
    ) -> bool:
        """Pause reminders. Optionally set a resume time.

        Args:
            until: ISO datetime string for when to resume.
            hours: Number of hours to pause.

        Returns:
            True if pause was applied successfully.
        """
        state = self._load_state()
        if not state.get("installed"):
            return False

        paused_until = None
        if hours is not None:
            paused_until = (datetime.now() + timedelta(hours=hours)).isoformat()
        elif until is not None:
            paused_until = until

        state["paused"] = True
        state["paused_until"] = paused_until
        self._save_state(state)

        # Unload the schedules while paused
        if sys.platform == "darwin":
            self._unload_macos_agents()
        elif sys.platform.startswith("linux"):
            self._comment_cron_entries()

        return True

    def resume(self) -> bool:
        """Resume paused reminders. Returns True if successful."""
        state = self._load_state()
        if not state.get("installed") or not state.get("paused"):
            return False

        state["paused"] = False
        state.pop("paused_until", None)
        self._save_state(state)

        morning = state.get("morning_time", "07:00")
        evening = state.get("evening_time", "19:00")

        if sys.platform == "darwin":
            self._load_macos_agents()
        elif sys.platform.startswith("linux"):
            self._uncomment_cron_entries()
        elif sys.platform == "win32":
            # Re-enable Windows tasks
            self._install_windows(morning, evening)

        return True

    def update_time(
        self, morning: str | None = None, evening: str | None = None
    ) -> bool:
        """Change reminder times. Reinstalls schedule.

        Returns True if successful.
        """
        state = self._load_state()
        m = morning or state.get("morning_time", "07:00")
        e = evening or state.get("evening_time", "19:00")
        self.uninstall()
        return self.install(morning_time=m, evening_time=e)

    def is_paused(self) -> bool:
        """Check if reminders are currently paused."""
        state = self._load_state()
        if not state.get("paused"):
            return False

        # Auto-resume if paused_until has passed
        paused_until = state.get("paused_until")
        if paused_until:
            try:
                resume_at = datetime.fromisoformat(paused_until)
                if datetime.now() >= resume_at:
                    self.resume()
                    return False
            except ValueError:
                pass

        return True

    def get_status(self) -> dict:
        """Get current schedule status.

        Returns:
            Dict with keys: installed, paused, morning_time, evening_time,
            paused_until, installed_at.
        """
        state = self._load_state()
        # Re-check pause expiry
        if state.get("paused") and not self.is_paused():
            state = self._load_state()
        return {
            "installed": state.get("installed", False),
            "paused": state.get("paused", False),
            "morning_time": state.get("morning_time"),
            "evening_time": state.get("evening_time"),
            "paused_until": state.get("paused_until"),
            "installed_at": state.get("installed_at"),
        }

    # ------------------------------------------------------------------
    # macOS (launchd)
    # ------------------------------------------------------------------

    def _plist_dir(self) -> Path:
        return Path.home() / "Library" / "LaunchAgents"

    def _plist_path(self, notify_type: str) -> Path:
        return self._plist_dir() / f"{self.PLIST_PREFIX}.{notify_type}.plist"

    def _generate_plist(
        self, label: str, time_str: str, notify_type: str
    ) -> str:
        """Generate launchd plist XML content."""
        hour, minute = (int(p) for p in time_str.split(":"))
        python_path = sys.executable
        return textwrap.dedent(f"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
              "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
                <key>Label</key>
                <string>{label}</string>
                <key>ProgramArguments</key>
                <array>
                    <string>{python_path}</string>
                    <string>-m</string>
                    <string>prep_agent</string>
                    <string>_notify</string>
                    <string>{notify_type}</string>
                </array>
                <key>StartCalendarInterval</key>
                <dict>
                    <key>Hour</key>
                    <integer>{hour}</integer>
                    <key>Minute</key>
                    <integer>{minute}</integer>
                </dict>
                <key>StandardOutPath</key>
                <string>{self.prep_dir}/scheduler-{notify_type}.log</string>
                <key>StandardErrorPath</key>
                <string>{self.prep_dir}/scheduler-{notify_type}.err</string>
            </dict>
            </plist>
        """)

    def _install_macos(self, morning: str, evening: str) -> bool:
        """Create and load launchd plist files."""
        plist_dir = self._plist_dir()
        plist_dir.mkdir(parents=True, exist_ok=True)

        # Remove any existing agents first
        self._uninstall_macos()

        for notify_type, time_str in [
            ("morning", morning),
            ("evening", evening),
        ]:
            label = f"{self.PLIST_PREFIX}.{notify_type}"
            content = self._generate_plist(label, time_str, notify_type)
            plist_path = self._plist_path(notify_type)
            try:
                plist_path.write_text(content)
            except OSError as exc:
                print(f"Error writing plist {plist_path}: {exc}")
                return False

        return self._load_macos_agents()

    def _load_macos_agents(self) -> bool:
        """Load all career-prep-agent launchd agents."""
        ok = True
        for notify_type in ("morning", "evening"):
            plist_path = self._plist_path(notify_type)
            if not plist_path.exists():
                continue
            try:
                subprocess.run(
                    ["launchctl", "load", str(plist_path)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
                print(f"Error loading {plist_path}: {exc}")
                ok = False
        return ok

    def _unload_macos_agents(self) -> bool:
        """Unload all career-prep-agent launchd agents."""
        ok = True
        for notify_type in ("morning", "evening"):
            plist_path = self._plist_path(notify_type)
            if not plist_path.exists():
                continue
            try:
                subprocess.run(
                    ["launchctl", "unload", str(plist_path)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                ok = False
        return ok

    def _uninstall_macos(self) -> bool:
        """Unload and remove launchd plists."""
        self._unload_macos_agents()
        ok = True
        for notify_type in ("morning", "evening"):
            plist_path = self._plist_path(notify_type)
            if plist_path.exists():
                try:
                    plist_path.unlink()
                except OSError as exc:
                    print(f"Error removing {plist_path}: {exc}")
                    ok = False
        return ok

    # ------------------------------------------------------------------
    # Linux (crontab)
    # ------------------------------------------------------------------

    def _build_cron_line(self, time_str: str, notify_type: str) -> str:
        """Build a crontab entry line."""
        hour, minute = (int(p) for p in time_str.split(":"))
        python_path = sys.executable
        return (
            f"{minute} {hour} * * * "
            f"{python_path} -m prep_agent _notify {notify_type} "
            f"{self.CRON_MARKER}"
        )

    def _get_crontab(self) -> str:
        """Read current user crontab. Returns empty string if none."""
        try:
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        return ""

    def _set_crontab(self, content: str) -> bool:
        """Write content as user crontab."""
        try:
            result = subprocess.run(
                ["crontab", "-"],
                input=content,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
            print(f"Error setting crontab: {exc}")
            return False

    def _strip_cron_entries(self, crontab: str) -> list[str]:
        """Return crontab lines with career-prep-agent entries removed."""
        return [
            line
            for line in crontab.splitlines()
            if self.CRON_MARKER not in line
        ]

    def _install_linux(self, morning: str, evening: str) -> bool:
        """Add entries to user crontab."""
        if not shutil.which("crontab"):
            print("crontab command not found.")
            return False

        existing = self._get_crontab()
        lines = self._strip_cron_entries(existing)

        lines.append(self._build_cron_line(morning, "morning"))
        lines.append(self._build_cron_line(evening, "evening"))

        # Ensure trailing newline
        content = "\n".join(lines).rstrip("\n") + "\n"
        return self._set_crontab(content)

    def _uninstall_linux(self) -> bool:
        """Remove career-prep-agent entries from crontab."""
        existing = self._get_crontab()
        lines = self._strip_cron_entries(existing)
        content = "\n".join(lines).rstrip("\n") + "\n" if lines else ""
        return self._set_crontab(content)

    def _comment_cron_entries(self) -> bool:
        """Comment out career-prep-agent cron entries (for pause)."""
        existing = self._get_crontab()
        lines: list[str] = []
        for line in existing.splitlines():
            if self.CRON_MARKER in line and not line.startswith("#PAUSED# "):
                lines.append(f"#PAUSED# {line}")
            else:
                lines.append(line)
        content = "\n".join(lines).rstrip("\n") + "\n"
        return self._set_crontab(content)

    def _uncomment_cron_entries(self) -> bool:
        """Uncomment paused career-prep-agent cron entries (for resume)."""
        existing = self._get_crontab()
        lines: list[str] = []
        for line in existing.splitlines():
            if line.startswith("#PAUSED# ") and self.CRON_MARKER in line:
                lines.append(line.removeprefix("#PAUSED# "))
            else:
                lines.append(line)
        content = "\n".join(lines).rstrip("\n") + "\n"
        return self._set_crontab(content)

    # ------------------------------------------------------------------
    # Windows (schtasks)
    # ------------------------------------------------------------------

    def _task_name(self, notify_type: str) -> str:
        return f"{self.TASK_PREFIX}-{notify_type}"

    def _install_windows(self, morning: str, evening: str) -> bool:
        """Create Windows scheduled tasks."""
        self._uninstall_windows()
        python_path = sys.executable
        ok = True

        for notify_type, time_str in [
            ("morning", morning),
            ("evening", evening),
        ]:
            task = self._task_name(notify_type)
            cmd = (
                f'"{python_path}" -m prep_agent _notify {notify_type}'
            )
            try:
                result = subprocess.run(
                    [
                        "schtasks",
                        "/Create",
                        "/SC", "DAILY",
                        "/TN", task,
                        "/TR", cmd,
                        "/ST", time_str,
                        "/F",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                if result.returncode != 0:
                    print(
                        f"Error creating task {task}: {result.stderr.strip()}"
                    )
                    ok = False
            except (
                subprocess.TimeoutExpired,
                FileNotFoundError,
                OSError,
            ) as exc:
                print(f"Error creating task {task}: {exc}")
                ok = False

        return ok

    def _uninstall_windows(self) -> bool:
        """Remove Windows scheduled tasks."""
        ok = True
        for notify_type in ("morning", "evening"):
            task = self._task_name(notify_type)
            try:
                subprocess.run(
                    ["schtasks", "/Delete", "/TN", task, "/F"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                # Ignore errors -- task may not exist
            except (
                subprocess.TimeoutExpired,
                FileNotFoundError,
                OSError,
            ):
                ok = False
        return ok

    # ------------------------------------------------------------------
    # State persistence
    # ------------------------------------------------------------------

    def _save_state(self, state: dict) -> None:
        """Save schedule state to JSON."""
        os.makedirs(self.prep_dir, exist_ok=True)
        try:
            with open(self.schedule_file, "w") as f:
                json.dump(state, f, indent=2)
        except OSError as exc:
            print(f"Error saving schedule state: {exc}")

    def _load_state(self) -> dict:
        """Load schedule state from JSON."""
        if not os.path.exists(self.schedule_file):
            return {}
        try:
            with open(self.schedule_file) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}
