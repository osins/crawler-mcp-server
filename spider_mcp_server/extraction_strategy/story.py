STORY_INSTRUCTION: str = """
You are a deterministic extraction engine.
Output a single JSON object following the schema.

CRITICAL RULES FOR "content" FIELD:
- The "content" field MUST contain ONLY plain text readable by humans
- STRIP all HTML tags: <html>, <head>, <body>, <p>, <div>, <a>, etc.
- STRIP all attributes: class, id, style, href, etc.
- Keep ONLY the actual text content that a human would read
- Preserve line breaks between paragraphs
- Do NOT include navigation links, menus, headers, or footers

Example:
BAD:  "<p>Hello <a href='/world'>world</a></p>"
GOOD: "Hello world"

OTHER RULES:
1. If the webpage contains valid human-readable text:
   - Set "error": false
   - Extract all fields
   - "content" = pure text only (no HTML)

2. If NO valid content exists:
   - Output: {"error": true, "message": "no valid content"}

3. Output EXACTLY ONE JSON object (not an array)
4. Follow the JSON Schema strictly
5. Valid JSON only, no comments

Return only the JSON object.
"""

STORY_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "error": {
            "type": "boolean",
            "description": "True if no valid content found"
        },
        "message": {
            "type": ["string", "null"],
            "description": "Error message if error is true"
        },
        "title": {
            "type": ["string", "null"],
            "description": "Extracted or generated title"
        },
        "content": {
            "type": ["string", "null"],
            "description": "Original human-readable text. MUST NOT be modified. Not be HTML tag."
        },
        "summary": {
            "type": ["string", "null"],
            "description": "Short summary (<200 words)"
        },
        "chapter_index": {
            "type": ["integer", "null"],
            "description": "Chapter number"
        },
        "position": {
            "type": ["string", "null"],
            "enum": ["first", "middle", "last", None],
            "description": "Position in the novel"
        },
        "word_count": {
            "type": ["integer", "null"],
            "description": "Character count"
        }
    },
    "required": ["error"]
}