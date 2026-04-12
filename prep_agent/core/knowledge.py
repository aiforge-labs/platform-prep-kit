"""Knowledge base -- manages study notes organized by topic."""
import math
import os
import re
from collections import Counter
from datetime import datetime


class KnowledgeBase:
    """Manages a collection of study notes organized by topic."""

    def __init__(self, prep_dir: str | None = None):
        self.prep_dir = prep_dir or os.path.expanduser("~/.prep")
        self.knowledge_dir = os.path.join(self.prep_dir, "knowledge")
        # Bundled knowledge packs shipped with the project
        self._packs_dir = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_packs")
        )

    def add_note(
        self, topic: str, content: str, source: str | None = None
    ) -> str:
        """Add a knowledge note under a topic. Appends to topic file.

        Creates the topic file if it doesn't exist, otherwise appends.
        Returns the file path written to.
        """
        os.makedirs(self.knowledge_dir, exist_ok=True)
        slug = self._topic_to_slug(topic)
        file_path = os.path.join(self.knowledge_dir, f"{slug}.md")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        source_line = f"**Source:** {source}\n\n" if source else ""

        if not os.path.isfile(file_path):
            # New topic file -- write header
            note_text = (
                f"# {topic}\n\n"
                f"## Note -- {timestamp}\n"
                f"{source_line}"
                f"{content}\n"
            )
        else:
            # Append to existing file
            note_text = (
                f"\n\n## Note -- {timestamp}\n"
                f"{source_line}"
                f"{content}\n"
            )

        with open(file_path, "a") as f:
            f.write(note_text)

        return file_path

    def get_topic(self, topic: str) -> str | None:
        """Retrieve all notes for a topic.

        Checks user's personal knowledge dir first, then falls back to
        bundled knowledge packs shipped with the project.
        Returns None if topic not found in either location.
        """
        slug = self._topic_to_slug(topic)

        # 1. User's personal notes
        file_path = os.path.join(self.knowledge_dir, f"{slug}.md")
        if os.path.isfile(file_path):
            try:
                with open(file_path) as f:
                    return f.read()
            except OSError:
                pass

        # 2. Bundled knowledge packs
        pack_path = os.path.join(self._packs_dir, f"{slug}.md")
        if os.path.isfile(pack_path):
            try:
                with open(pack_path) as f:
                    return f.read()
            except OSError:
                pass

        return None

    def list_topics(self) -> list[dict]:
        """List all topics with note counts and last updated.

        Returns:
            List of dicts: [{topic, slug, notes_count, last_updated, file_path}]
        """
        if not os.path.isdir(self.knowledge_dir):
            return []

        topics: list[dict] = []
        for filename in sorted(os.listdir(self.knowledge_dir)):
            if not filename.endswith(".md"):
                continue

            file_path = os.path.join(self.knowledge_dir, filename)
            slug = filename[:-3]  # strip .md

            try:
                with open(file_path) as f:
                    content = f.read()
            except OSError:
                continue

            # Extract topic name from first heading
            first_line = content.split("\n", 1)[0]
            topic_name = first_line.lstrip("# ").strip() if first_line.startswith("#") else slug

            # Count notes by counting "## Note" headings
            notes_count = content.count("## Note")

            # Last modified time
            mtime = os.path.getmtime(file_path)
            last_updated = datetime.fromtimestamp(mtime).isoformat()

            topics.append({
                "topic": topic_name,
                "slug": slug,
                "notes_count": notes_count,
                "last_updated": last_updated,
                "file_path": file_path,
            })

        return topics

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """Search knowledge notes using TF-IDF relevance scoring.

        Results are ranked by relevance (highest first) and include
        backward-compatible ``matching_lines`` plus a ``score`` field.

        Args:
            query: Search query text.
            top_k: Maximum number of results to return.

        Returns:
            List of dicts: [{topic, matching_lines, file_path, score}]
        """
        # Collect search directories: user notes + bundled packs
        search_dirs = []
        if os.path.isdir(self.knowledge_dir):
            search_dirs.append(self.knowledge_dir)
        if os.path.isdir(self._packs_dir):
            search_dirs.append(self._packs_dir)

        if not search_dirs:
            return []

        # Load all documents (deduplicate by slug — user notes take priority)
        seen_slugs: set[str] = set()
        docs: list[tuple[str, str, list[str], str]] = []  # (topic, text, lines, path)
        for search_dir in search_dirs:
            for filename in sorted(os.listdir(search_dir)):
                if not filename.endswith(".md"):
                    continue
                slug = filename[:-3]
                if slug in seen_slugs:
                    continue  # user note already loaded for this slug
                seen_slugs.add(slug)
                file_path = os.path.join(search_dir, filename)
                try:
                    with open(file_path) as f:
                        text = f.read()
                        lines = text.splitlines()
                except OSError:
                    continue

                first_line = lines[0].strip() if lines else filename
                topic_name = (
                    first_line.lstrip("# ").strip()
                    if first_line.startswith("#")
                    else slug
                )
                docs.append((topic_name, text, lines, file_path))

        if not docs:
            return []

        # Tokenize query and all documents
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        doc_token_lists = [self._tokenize(text) for _, text, _, _ in docs]

        # Compute IDF across corpus
        idf = self._compute_idf(doc_token_lists)

        # Score each document
        scored: list[tuple[float, int]] = []
        for i, doc_tokens in enumerate(doc_token_lists):
            score = self._score_tfidf(query_tokens, doc_tokens, idf)
            if score > 0:
                scored.append((score, i))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        # Build results with matching_lines for backward compat
        query_lower = query.lower()
        results: list[dict] = []
        for score, idx in scored[:top_k]:
            topic_name, _, lines, file_path = docs[idx]
            matching_lines = [
                line.strip()
                for line in lines
                if query_lower in line.lower()
            ]
            results.append({
                "topic": topic_name,
                "matching_lines": matching_lines,
                "file_path": file_path,
                "score": round(score, 4),
            })

        return results

    # ------------------------------------------------------------------
    # TF-IDF helpers (no external dependencies)
    # ------------------------------------------------------------------

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Split text into lowercase alphanumeric tokens."""
        return re.findall(r"[a-z0-9]+", text.lower())

    @staticmethod
    def _compute_tf(tokens: list[str]) -> dict[str, float]:
        """Compute term frequency: count(term) / total_tokens."""
        if not tokens:
            return {}
        counts = Counter(tokens)
        total = len(tokens)
        return {t: c / total for t, c in counts.items()}

    @staticmethod
    def _compute_idf(documents: list[list[str]]) -> dict[str, float]:
        """Compute inverse document frequency across the corpus."""
        n = len(documents)
        df: dict[str, int] = {}
        for doc_tokens in documents:
            for token in set(doc_tokens):
                df[token] = df.get(token, 0) + 1
        return {t: math.log((n + 1) / (freq + 1)) + 1 for t, freq in df.items()}

    @staticmethod
    def _score_tfidf(
        query_tokens: list[str],
        doc_tokens: list[str],
        idf: dict[str, float],
    ) -> float:
        """Compute TF-IDF similarity score between query and document."""
        tf = KnowledgeBase._compute_tf(doc_tokens)
        return sum(tf.get(qt, 0) * idf.get(qt, 0) for qt in query_tokens)

    def import_knowledge_pack(self, pack_id: str) -> bool:
        """Import a built-in knowledge pack into user's knowledge base.

        Copies from package knowledge_packs/ directory to ~/.prep/knowledge/.
        Returns True if imported successfully, False otherwise.
        """
        package_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "knowledge_packs"
        )
        pack_path = os.path.join(package_dir, f"{pack_id}.md")
        if not os.path.isfile(pack_path):
            return False

        os.makedirs(self.knowledge_dir, exist_ok=True)
        dest_path = os.path.join(self.knowledge_dir, f"{pack_id}.md")

        try:
            with open(pack_path) as src:
                content = src.read()
            # Append if target already exists, otherwise create
            if os.path.isfile(dest_path):
                with open(dest_path, "a") as dst:
                    dst.write(f"\n\n{content}")
            else:
                with open(dest_path, "w") as dst:
                    dst.write(content)
            return True
        except OSError:
            return False

    def export_all(self, format: str = "md") -> str:
        """Export entire knowledge base as a single document.

        Args:
            format: Output format. Currently only 'md' is supported.

        Returns:
            Combined content of all topic files.
        """
        if not os.path.isdir(self.knowledge_dir):
            return ""

        parts: list[str] = []
        for filename in sorted(os.listdir(self.knowledge_dir)):
            if not filename.endswith(".md"):
                continue
            file_path = os.path.join(self.knowledge_dir, filename)
            try:
                with open(file_path) as f:
                    parts.append(f.read())
            except OSError:
                continue

        separator = "\n\n---\n\n"
        return separator.join(parts)

    def _topic_to_slug(self, topic: str) -> str:
        """Convert topic name to file-safe slug.

        Examples:
            "OWASP LLM Top 10" -> "owasp-llm-top-10"
            "System Design & Architecture" -> "system-design-architecture"
        """
        slug = topic.lower().strip()
        # Replace non-alphanumeric chars (except hyphens) with hyphens
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        # Strip leading/trailing hyphens
        slug = slug.strip("-")
        return slug
