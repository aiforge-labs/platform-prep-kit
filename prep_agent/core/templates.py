"""Template loader -- discovers and loads role templates."""

import os
from pathlib import Path

import yaml


class TemplateLoader:
    """Discovers, loads, and validates career-prep role templates.

    Templates are YAML files that define learning tracks, topics, resources,
    and interview questions for a specific career target role.

    Search order:
        1. Package templates/ directory (shipped with prep-agent)
        2. User's ~/.prep/templates/ directory (custom templates)
    """

    # Fields required at the top level of every template
    REQUIRED_FIELDS = {"name", "description", "version", "tracks"}

    # Optional top-level fields
    OPTIONAL_FIELDS = {
        "suggested_timeline",
        "content_suggestions",
        "certifications_suggested",
        "interview_questions",
        "bridge_from",
    }

    # Fields required for each track
    TRACK_REQUIRED = {"id", "name", "topics"}

    # Fields required for each topic
    TOPIC_REQUIRED = {"id", "name", "estimated_hours", "priority"}

    # Valid priority values
    VALID_PRIORITIES = {"high", "medium", "low"}

    def __init__(self, prep_dir: str | None = None) -> None:
        self.prep_dir = prep_dir or os.path.expanduser("~/.prep")

    # -- Public API --

    def list_templates(self) -> list[dict]:
        """List available templates with name, description, and source path.

        Returns a list of dicts, each containing:
            - id: template identifier (filename stem)
            - name: human-readable name from the template
            - description: one-line description
            - path: absolute path to the template file
            - source: 'built-in' or 'user'
        """
        templates: list[dict] = []
        seen_ids: set[str] = set()

        for source_label, directory in self._search_dirs():
            if not os.path.isdir(directory):
                continue
            for entry in sorted(os.listdir(directory)):
                if not entry.endswith((".yml", ".yaml")):
                    continue
                if entry.startswith("_"):
                    continue  # skip schema and internal files

                template_id = Path(entry).stem
                if template_id in seen_ids:
                    continue  # first found takes precedence
                seen_ids.add(template_id)

                filepath = os.path.join(directory, entry)
                try:
                    data = self._read_yaml(filepath)
                    templates.append({
                        "id": template_id,
                        "name": data.get("name", template_id),
                        "description": data.get("description", ""),
                        "path": filepath,
                        "source": source_label,
                    })
                except Exception:
                    # Skip files that fail to parse
                    continue

        return templates

    def load_template(self, template_id: str) -> dict:
        """Load a specific template by id or absolute path.

        Args:
            template_id: Either a template slug (e.g., 'cloud-security-lead')
                or an absolute path to a YAML file.

        Returns:
            Parsed template dict with all fields.

        Raises:
            FileNotFoundError: If no template matches the id.
            ValueError: If the file is not valid YAML.
        """
        # If it looks like an absolute path, load directly
        if os.path.isabs(template_id) and os.path.isfile(template_id):
            return self._read_yaml(template_id)

        # Search package and user directories
        for _label, directory in self._search_dirs():
            if not os.path.isdir(directory):
                continue
            for ext in (".yml", ".yaml"):
                filepath = os.path.join(directory, f"{template_id}{ext}")
                if os.path.isfile(filepath):
                    return self._read_yaml(filepath)

        raise FileNotFoundError(
            f"Template '{template_id}' not found. "
            f"Run 'prep template list' to see available templates."
        )

    def validate_template(self, template: dict) -> list[str]:
        """Validate template structure and return a list of issues.

        Returns an empty list if the template is valid.

        Args:
            template: Parsed template dict to validate.

        Returns:
            List of human-readable validation error strings.
        """
        errors: list[str] = []

        # Check required top-level fields
        for field in sorted(self.REQUIRED_FIELDS):
            if field not in template:
                errors.append(f"Missing required field: '{field}'")

        # Validate version
        version = template.get("version")
        if version is not None and not isinstance(version, int):
            errors.append(
                f"'version' must be an integer, got {type(version).__name__}"
            )

        # Validate tracks
        tracks = template.get("tracks")
        if tracks is not None:
            if not isinstance(tracks, list):
                errors.append("'tracks' must be a list")
            else:
                track_ids: set[str] = set()
                for i, track in enumerate(tracks):
                    if not isinstance(track, dict):
                        errors.append(f"Track {i} must be a dict")
                        continue

                    # Check required track fields
                    for field in sorted(self.TRACK_REQUIRED):
                        if field not in track:
                            errors.append(
                                f"Track {i} ('{track.get('id', '?')}'): "
                                f"missing required field '{field}'"
                            )

                    # Check for duplicate track ids
                    tid = track.get("id")
                    if tid:
                        if tid in track_ids:
                            errors.append(f"Duplicate track id: '{tid}'")
                        track_ids.add(tid)

                    # Validate topics within this track
                    self._validate_topics(track, tid or f"track-{i}", errors)

        return errors

    @staticmethod
    def get_template_dir() -> str:
        """Get the path to the built-in templates directory.

        Returns:
            Absolute path to the package's templates/ directory.
        """
        package_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        return os.path.join(os.path.dirname(package_dir), "templates")

    # -- Private helpers --

    def _search_dirs(self) -> list[tuple[str, str]]:
        """Return (label, directory) pairs in search order."""
        return [
            ("built-in", self.get_template_dir()),
            ("user", os.path.join(self.prep_dir, "templates")),
        ]

    def _validate_topics(
        self, track: dict, tid: str, errors: list[str]
    ) -> None:
        """Validate topics within a track, appending errors in place."""
        topics = track.get("topics")
        if topics is None:
            return

        if not isinstance(topics, list):
            errors.append(f"Track '{tid}': 'topics' must be a list")
            return

        topic_ids: set[str] = set()
        for j, topic in enumerate(topics):
            if not isinstance(topic, dict):
                errors.append(f"Track '{tid}', topic {j}: must be a dict")
                continue

            topic_label = topic.get("id", f"topic-{j}")

            for field in sorted(self.TOPIC_REQUIRED):
                if field not in topic:
                    errors.append(
                        f"Track '{tid}', topic '{topic_label}': "
                        f"missing required field '{field}'"
                    )

            # Validate priority value
            priority = topic.get("priority")
            if priority is not None and priority not in self.VALID_PRIORITIES:
                errors.append(
                    f"Track '{tid}', topic '{topic_label}': "
                    f"invalid priority '{priority}' "
                    f"(must be one of: {', '.join(sorted(self.VALID_PRIORITIES))})"
                )

            # Check for duplicate topic ids within this track
            topic_id = topic.get("id")
            if topic_id:
                if topic_id in topic_ids:
                    errors.append(
                        f"Track '{tid}': duplicate topic id '{topic_id}'"
                    )
                topic_ids.add(topic_id)

            # Validate estimated_hours type
            hours = topic.get("estimated_hours")
            if hours is not None and not isinstance(hours, (int, float)):
                errors.append(
                    f"Track '{tid}', topic '{topic_label}': "
                    f"'estimated_hours' must be a number"
                )

            # Validate resources if present
            self._validate_resources(tid, topic_label, topic, errors)

    @staticmethod
    def _validate_resources(
        tid: str, topic_label: str, topic: dict, errors: list[str]
    ) -> None:
        """Validate resources within a topic."""
        resources = topic.get("resources")
        if resources is None:
            return

        if not isinstance(resources, list):
            errors.append(
                f"Track '{tid}', topic '{topic_label}': "
                f"'resources' must be a list"
            )
            return

        for k, res in enumerate(resources):
            if not isinstance(res, dict):
                errors.append(
                    f"Track '{tid}', topic '{topic_label}', "
                    f"resource {k}: must be a dict"
                )
                continue
            if "title" not in res:
                errors.append(
                    f"Track '{tid}', topic '{topic_label}', "
                    f"resource {k}: missing 'title'"
                )
            if "url" not in res:
                errors.append(
                    f"Track '{tid}', topic '{topic_label}', "
                    f"resource {k}: missing 'url'"
                )

    @staticmethod
    def _read_yaml(filepath: str) -> dict:
        """Read and parse a YAML file.

        Raises:
            ValueError: If the file cannot be parsed or is not a mapping.
        """
        try:
            with open(filepath, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML in {filepath}: {exc}") from exc

        if not isinstance(data, dict):
            raise ValueError(
                f"Template {filepath} must be a YAML mapping, "
                f"got {type(data).__name__}"
            )

        return data


# -- Module-level convenience functions (backward compatible) --

def _get_loader() -> TemplateLoader:
    return TemplateLoader()


def list_templates() -> list[dict]:
    """List all available templates (built-in + user)."""
    return _get_loader().list_templates()


def load_template(template_id: str) -> dict | None:
    """Load a template by ID. Returns None if not found."""
    try:
        return _get_loader().load_template(template_id)
    except FileNotFoundError:
        return None


def validate_template(template: dict) -> list[str]:
    """Validate template structure. Returns list of errors (empty = valid)."""
    return _get_loader().validate_template(template)
