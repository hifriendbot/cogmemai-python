# CogmemAi Python SDK

Persistent memory for AI coding assistants. Give your AI tools memory that persists across sessions.

## Install

```bash
pip install cogmemai
```

## Quick Start

```python
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
for memory in results["memories"]:
    print(f"[{memory['importance']}] {memory['content']}")

# Load project context
context = client.get_project_context(project_id="my-project")

# Extract memories from conversation
client.extract_memories(
    user_message="Let's use PostgreSQL for the database",
    assistant_response="Good choice. I'll set up the schema with...",
)
```

## All Methods

### Core Memory
- `save_memory(content, memory_type, category, subject, importance, scope, project_id)` — Save a memory
- `recall_memories(query, limit, memory_type, scope)` — Semantic search
- `extract_memories(user_message, assistant_response, previous_context)` — Ai extracts facts from conversation
- `get_project_context(project_id, include_global, context)` — Load top memories with smart ranking
- `list_memories(memory_type, category, scope, limit, offset)` — Browse with filters
- `update_memory(memory_id, content, importance, scope)` — Edit a memory
- `delete_memory(memory_id)` — Delete permanently
- `get_usage()` — Check usage stats and tier

### Documents & Sessions
- `ingest_document(text, document_type, project_id)` — Extract memories from docs
- `save_session_summary(summary, project_id)` — Capture session accomplishments

### Import / Export
- `export_memories()` — Back up memories as JSON
- `import_memories(memories)` — Bulk import from JSON
- `get_memory_versions(memory_id)` — Version history

### Team & Collaboration
- `get_team_members(project_id)` — List team members
- `invite_team_member(email, project_id, role)` — Invite a member
- `remove_team_member(member_id)` — Remove a member

### Memory Relationships & Promotion
- `link_memories(memory_id, related_memory_id, relationship_type)` — Link related memories
- `get_memory_links(memory_id)` — Get linked memories
- `get_promotion_candidates()` — Find cross-project patterns
- `promote_to_global(memory_id)` — Promote to global scope

## Error Handling

```python
from cogmemai.client import CogmemAiError

try:
    client.save_memory(content="test")
except CogmemAiError as e:
    print(f"Error {e.status_code}: {e}")
```

## Get an API Key

1. Sign up at [hifriendbot.com/developer/](https://hifriendbot.com/developer/)
2. Generate an API key
3. Start saving memories

## Links

- [Developer Dashboard](https://hifriendbot.com/developer/)
- [JavaScript SDK (npm)](https://www.npmjs.com/package/cogmemai-sdk)
- [MCP Server (npm)](https://www.npmjs.com/package/cogmemai-mcp)
- [GitHub](https://github.com/hifriendbot/cogmemai-python)
