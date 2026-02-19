"""CogmemAi Python SDK client."""

from __future__ import annotations

from typing import Any, Optional

import requests


class CogmemAiError(Exception):
    """Base exception for CogmemAi API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class CogmemAi:
    """Client for the CogmemAi REST API.

    Args:
        api_key: Your CogmemAi API key (starts with ``cm_``).
        base_url: API base URL. Defaults to the hosted CogmemAi service.
        timeout: Request timeout in seconds. Defaults to 30.

    Example::

        from cogmemai import CogmemAi

        client = CogmemAi("cm_your_api_key_here")

        # Save a memory
        client.save_memory(
            content="This project uses React with TypeScript",
            memory_type="architecture",
            category="frontend",
            importance=8,
        )

        # Search memories
        results = client.recall_memories("what framework does this project use?")

        # Load project context
        context = client.get_project_context(project_id="my-project")
    """

    DEFAULT_BASE_URL = "https://hifriendbot.com/wp-json/hifriendbot/v1"

    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        timeout: int = 30,
    ):
        if not api_key or not api_key.startswith("cm_"):
            raise ValueError("API key must start with 'cm_'")

        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    # ── Internal helpers ───────────────────────────────

    def _request(self, method: str, path: str, **kwargs: Any) -> dict:
        url = f"{self.base_url}/cogmemai/{path}"
        kwargs.setdefault("timeout", self.timeout)
        resp = self._session.request(method, url, **kwargs)
        try:
            data = resp.json()
        except ValueError:
            raise CogmemAiError(f"Invalid JSON response: {resp.text}", resp.status_code)
        if resp.status_code >= 400:
            msg = data.get("error") or data.get("message") or resp.text
            raise CogmemAiError(msg, resp.status_code)
        return data

    def _get(self, path: str, params: dict | None = None) -> dict:
        return self._request("GET", path, params=params)

    def _post(self, path: str, data: dict | None = None) -> dict:
        return self._request("POST", path, json=data)

    def _patch(self, path: str, data: dict | None = None) -> dict:
        return self._request("PATCH", path, json=data)

    def _delete(self, path: str) -> dict:
        return self._request("DELETE", path)

    # ── Core Memory ────────────────────────────────────

    def save_memory(
        self,
        content: str,
        *,
        memory_type: str = "context",
        category: str = "general",
        subject: str = "",
        importance: int = 5,
        scope: str = "project",
        project_id: str = "",
    ) -> dict:
        """Save a memory.

        Args:
            content: The fact to remember (5-500 chars).
            memory_type: Type of memory (e.g. architecture, decision, bug, pattern).
            category: Category (e.g. frontend, backend, database, devops).
            subject: What this memory is about (max 100 chars).
            importance: Importance 1-10 (default 5). Reserve 9-10 for core architecture.
            scope: ``"project"`` or ``"global"``.
            project_id: Project identifier.

        Returns:
            Dict with ``memory_id``, ``stored``, and optional ``deduplicated``,
            ``conflict_detected``, ``warning`` fields.
        """
        return self._post(
            "store",
            {
                "content": content,
                "memory_type": memory_type,
                "category": category,
                "subject": subject,
                "importance": importance,
                "scope": scope,
                "project_id": project_id,
            },
        )

    def recall_memories(
        self,
        query: str,
        *,
        limit: int = 10,
        memory_type: str = "",
        scope: str = "all",
    ) -> dict:
        """Semantic search across memories.

        Args:
            query: Natural language search query (2-500 chars).
            limit: Max results (1-20, default 10).
            memory_type: Filter by type.
            scope: ``"global"``, ``"project"``, or ``"all"``.

        Returns:
            Dict with ``memories`` array ranked by relevance.
        """
        payload: dict[str, Any] = {"query": query, "limit": limit, "scope": scope}
        if memory_type:
            payload["memory_type"] = memory_type
        return self._post("recall", payload)

    def extract_memories(
        self,
        user_message: str,
        *,
        assistant_response: str = "",
        previous_context: str = "",
    ) -> dict:
        """Extract memories from a conversation exchange using Ai.

        Args:
            user_message: The developer's message (1-4000 chars).
            assistant_response: The assistant's response (max 4000 chars).
            previous_context: Previous exchange for context (max 2000 chars).

        Returns:
            Dict with ``extracted`` count and ``memories`` array.
        """
        payload: dict[str, Any] = {"user_message": user_message}
        if assistant_response:
            payload["assistant_response"] = assistant_response
        if previous_context:
            payload["previous_context"] = previous_context
        return self._post("extract", payload)

    def get_project_context(
        self,
        *,
        project_id: str = "",
        include_global: bool = True,
        context: str = "",
    ) -> dict:
        """Load project context with smart ranking.

        Args:
            project_id: Project identifier.
            include_global: Include global memories (default True).
            context: Current context for semantic ranking blend.

        Returns:
            Dict with ``memories`` array sorted by blended score.
        """
        params: dict[str, Any] = {"include_global": str(include_global).lower()}
        if project_id:
            params["project_id"] = project_id
        if context:
            params["context"] = context
        return self._get("context", params)

    def list_memories(
        self,
        *,
        memory_type: str = "",
        category: str = "",
        scope: str = "all",
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        """List memories with filters.

        Args:
            memory_type: Filter by type.
            category: Filter by category.
            scope: ``"global"``, ``"project"``, or ``"all"``.
            limit: Max results (default 50, max 100).
            offset: Pagination offset.

        Returns:
            Dict with ``memories`` array and pagination info.
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset, "scope": scope}
        if memory_type:
            params["memory_type"] = memory_type
        if category:
            params["category"] = category
        return self._get("memories", params)

    def update_memory(
        self,
        memory_id: int,
        *,
        content: str = "",
        importance: int | None = None,
        scope: str = "",
    ) -> dict:
        """Update a memory.

        Args:
            memory_id: ID of the memory to update.
            content: New content.
            importance: New importance (1-10).
            scope: New scope.

        Returns:
            Dict with ``updated`` status.
        """
        payload: dict[str, Any] = {}
        if content:
            payload["content"] = content
        if importance is not None:
            payload["importance"] = importance
        if scope:
            payload["scope"] = scope
        return self._patch(f"memory/{memory_id}", payload)

    def delete_memory(self, memory_id: int) -> dict:
        """Delete a memory permanently.

        Args:
            memory_id: ID of the memory to delete.

        Returns:
            Dict with ``deleted`` status.
        """
        return self._delete(f"memory/{memory_id}")

    def get_usage(self) -> dict:
        """Get usage stats and tier info.

        Returns:
            Dict with memory count, extraction count, tier limits, etc.
        """
        return self._get("usage")

    # ── Documents & Sessions ───────────────────────────

    def ingest_document(
        self,
        text: str,
        *,
        document_type: str = "",
        project_id: str = "",
    ) -> dict:
        """Extract memories from a document.

        Args:
            text: Document text (up to 50K chars).
            document_type: e.g. "README", "architecture doc", "meeting notes".
            project_id: Project identifier.

        Returns:
            Dict with ``chunks_processed``, ``extracted``, and ``memories`` array.
        """
        payload: dict[str, Any] = {"text": text}
        if document_type:
            payload["document_type"] = document_type
        if project_id:
            payload["project_id"] = project_id
        return self._post("ingest", payload)

    def save_session_summary(
        self,
        summary: str,
        *,
        project_id: str = "",
    ) -> dict:
        """Save a session summary.

        Args:
            summary: Session summary text (up to 2K chars).
            project_id: Project identifier.

        Returns:
            Dict with ``memory_id`` and ``stored`` status.
        """
        payload: dict[str, Any] = {"summary": summary}
        if project_id:
            payload["project_id"] = project_id
        return self._post("session-summary", payload)

    # ── Import / Export / Versions ─────────────────────

    def export_memories(self) -> dict:
        """Export all memories as JSON.

        Returns:
            Dict with ``version``, ``exported_at``, ``memory_count``, and ``memories``.
        """
        return self._get("export")

    def import_memories(self, memories: list[dict]) -> dict:
        """Bulk import memories.

        Args:
            memories: List of memory objects with ``content`` and optional fields.

        Returns:
            Dict with ``imported``, ``skipped``, and ``errors`` counts.
        """
        return self._post("import", {"memories": memories})

    def get_memory_versions(self, memory_id: int) -> dict:
        """Get version history for a memory.

        Args:
            memory_id: ID of the memory.

        Returns:
            Dict with ``versions`` array (content, importance, scope, changed_by, timestamp).
        """
        return self._get(f"memory/{memory_id}/versions")

    # ── Team & Collaboration ──────────────────────────

    def get_team_members(self, *, project_id: str = "") -> dict:
        """List team members. Requires Team or Enterprise tier.

        Args:
            project_id: Filter by project.

        Returns:
            Dict with ``members`` array.
        """
        params = {}
        if project_id:
            params["project_id"] = project_id
        return self._get("team/members", params)

    def invite_team_member(
        self,
        email: str,
        project_id: str,
        *,
        role: str = "member",
    ) -> dict:
        """Invite a team member. Requires Team or Enterprise tier.

        Args:
            email: Email of the user to invite.
            project_id: Project to share.
            role: ``"member"`` or ``"viewer"`` (default ``"member"``).

        Returns:
            Dict with invitation status.
        """
        return self._post(
            "team/invite",
            {"email": email, "project_id": project_id, "role": role},
        )

    def remove_team_member(self, member_id: int) -> dict:
        """Remove a team member.

        Args:
            member_id: ID of the team member record.

        Returns:
            Dict with removal status.
        """
        return self._delete(f"team/remove/{member_id}")

    # ── Memory Relationships & Promotion ──────────────

    def link_memories(
        self,
        memory_id: int,
        related_memory_id: int,
        relationship_type: str,
    ) -> dict:
        """Link two related memories.

        Args:
            memory_id: Source memory ID.
            related_memory_id: Target memory ID.
            relationship_type: ``"led_to"``, ``"contradicts"``, ``"extends"``, or ``"related"``.

        Returns:
            Dict with link status.
        """
        return self._post(
            f"memory/{memory_id}/link",
            {
                "related_memory_id": related_memory_id,
                "relationship_type": relationship_type,
            },
        )

    def get_memory_links(self, memory_id: int) -> dict:
        """Get linked memories.

        Args:
            memory_id: ID of the memory.

        Returns:
            Dict with ``links`` array.
        """
        return self._get(f"memory/{memory_id}/links")

    def get_promotion_candidates(self) -> dict:
        """Find cross-project patterns eligible for global promotion.

        Returns:
            Dict with ``candidates`` array.
        """
        return self._get("promotion-candidates")

    def promote_to_global(self, memory_id: int) -> dict:
        """Promote a project memory to global scope.

        Args:
            memory_id: ID of the memory to promote.

        Returns:
            Dict with promotion status.
        """
        return self._post(f"memory/{memory_id}/promote", {})
