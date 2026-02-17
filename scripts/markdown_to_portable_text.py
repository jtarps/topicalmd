#!/usr/bin/env python3
"""Convert markdown text to Sanity Portable Text blocks.

Pure Python, regex-based. No external dependencies.
Handles: headings, bold, italic, links, bullet/numbered lists, blockquotes.
"""

import re
import uuid


def _generate_key(prefix="k"):
    """Generate a short unique key for Sanity blocks/spans."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _parse_inline(text):
    """Parse inline markdown (bold, italic, links) into Portable Text spans + markDefs.

    Returns (spans_list, mark_defs_list).
    """
    spans = []
    mark_defs = []

    # Tokenize: split text into segments of plain, bold, italic, bold-italic, links
    # Pattern matches: [text](url), ***bold-italic***, **bold**, *italic*
    pattern = re.compile(
        r'(\[([^\]]+)\]\(([^)]+)\))'   # [text](url)
        r'|(\*\*\*(.+?)\*\*\*)'        # ***bold italic***
        r'|(\*\*(.+?)\*\*)'            # **bold**
        r'|(\*(.+?)\*)'                # *italic*
    )

    last_end = 0
    for match in pattern.finditer(text):
        start = match.start()

        # Add plain text before this match
        if start > last_end:
            plain = text[last_end:start]
            if plain:
                spans.append({
                    "_type": "span",
                    "_key": _generate_key("s"),
                    "text": plain,
                    "marks": [],
                })

        if match.group(1):  # Link: [text](url)
            link_text = match.group(2)
            link_url = match.group(3)
            link_key = _generate_key("ln")
            mark_defs.append({
                "_type": "link",
                "_key": link_key,
                "href": link_url,
            })
            spans.append({
                "_type": "span",
                "_key": _generate_key("s"),
                "text": link_text,
                "marks": [link_key],
            })
        elif match.group(4):  # Bold italic: ***text***
            spans.append({
                "_type": "span",
                "_key": _generate_key("s"),
                "text": match.group(5),
                "marks": ["strong", "em"],
            })
        elif match.group(6):  # Bold: **text**
            inner = match.group(7)
            # Check if the bold text contains a link like **[text](url)**
            link_in_bold = re.match(r'^\[([^\]]+)\]\(([^)]+)\)(.*)$', inner)
            if link_in_bold:
                link_key = _generate_key("ln")
                mark_defs.append({
                    "_type": "link",
                    "_key": link_key,
                    "href": link_in_bold.group(2),
                })
                spans.append({
                    "_type": "span",
                    "_key": _generate_key("s"),
                    "text": link_in_bold.group(1),
                    "marks": ["strong", link_key],
                })
                trailing = link_in_bold.group(3)
                if trailing:
                    spans.append({
                        "_type": "span",
                        "_key": _generate_key("s"),
                        "text": trailing,
                        "marks": ["strong"],
                    })
            else:
                spans.append({
                    "_type": "span",
                    "_key": _generate_key("s"),
                    "text": inner,
                    "marks": ["strong"],
                })
        elif match.group(8):  # Italic: *text*
            inner_it = match.group(9)
            # Check if italic text contains a link like *[text](url)*
            link_in_italic = re.match(r'^\[([^\]]+)\]\(([^)]+)\)(.*)$', inner_it)
            if link_in_italic:
                link_key = _generate_key("ln")
                mark_defs.append({
                    "_type": "link",
                    "_key": link_key,
                    "href": link_in_italic.group(2),
                })
                spans.append({
                    "_type": "span",
                    "_key": _generate_key("s"),
                    "text": link_in_italic.group(1),
                    "marks": ["em", link_key],
                })
                trailing = link_in_italic.group(3)
                if trailing:
                    spans.append({
                        "_type": "span",
                        "_key": _generate_key("s"),
                        "text": trailing,
                        "marks": ["em"],
                    })
            else:
                spans.append({
                    "_type": "span",
                    "_key": _generate_key("s"),
                    "text": inner_it,
                    "marks": ["em"],
                })

        last_end = match.end()

    # Remaining plain text
    if last_end < len(text):
        remaining = text[last_end:]
        if remaining:
            spans.append({
                "_type": "span",
                "_key": _generate_key("s"),
                "text": remaining,
                "marks": [],
            })

    # If no spans were created, return the full text as a single plain span
    if not spans:
        spans.append({
            "_type": "span",
            "_key": _generate_key("s"),
            "text": text,
            "marks": [],
        })

    return spans, mark_defs


def _make_block(style, text, list_item=None, level=None):
    """Build a single Portable Text block dict."""
    spans, mark_defs = _parse_inline(text)
    block = {
        "_type": "block",
        "_key": _generate_key("b"),
        "style": style,
        "children": spans,
        "markDefs": mark_defs,
    }
    if list_item:
        block["listItem"] = list_item
        block["level"] = level or 1
    return block


def markdown_to_portable_text(markdown_str):
    """Convert a markdown string to a list of Sanity Portable Text block dicts.

    Handles:
    - ## h2, ### h3, #### h4 headings
    - **bold**, *italic*, [links](url)
    - - bullet lists, 1. numbered lists (with nesting via indentation)
    - > blockquotes
    - **Pseudo Header:** lines (bold text ending with colon on its own) -> h3
    - | table lines -> normal text passthrough
    - Accumulates adjacent non-special lines into single paragraphs
    """
    if not markdown_str or not markdown_str.strip():
        return []

    lines = markdown_str.split("\n")
    blocks = []
    paragraph_buffer = []
    table_buffer = []

    def flush_paragraph():
        """Flush accumulated paragraph lines into a single normal block."""
        if paragraph_buffer:
            text = " ".join(paragraph_buffer).strip()
            if text:
                blocks.append(_make_block("normal", text))
            paragraph_buffer.clear()

    def flush_table():
        """Flush accumulated table lines into a single block for frontend rendering."""
        if table_buffer:
            table_text = "\n".join(table_buffer)
            blocks.append(_make_block("normal", table_text))
            table_buffer.clear()

    for line in lines:
        stripped = line.rstrip()

        # Empty line -> flush paragraph and table
        if not stripped.strip():
            flush_table()
            flush_paragraph()
            continue

        # Headings: ## h2, ### h3, #### h4
        heading_match = re.match(r'^(#{1,4})\s+(.+)$', stripped.strip())
        if heading_match:
            flush_paragraph()
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            # Strip trailing # if present (e.g., ## Heading ##)
            heading_text = re.sub(r'\s*#+\s*$', '', heading_text)
            style = f"h{level}" if level >= 2 else "h2"
            blocks.append(_make_block(style, heading_text))
            continue

        # Blockquote: > text
        bq_match = re.match(r'^>\s*(.*)$', stripped.strip())
        if bq_match:
            flush_paragraph()
            blocks.append(_make_block("blockquote", bq_match.group(1).strip()))
            continue

        # Bullet list: - text or * text (check indentation for nesting)
        bullet_match = re.match(r'^(\s*)([-*])\s+(.+)$', stripped)
        if bullet_match:
            flush_paragraph()
            indent = len(bullet_match.group(1))
            level = 1 + (indent // 2)  # 0 indent = level 1, 2+ indent = level 2, etc.
            blocks.append(_make_block("normal", bullet_match.group(3).strip(), list_item="bullet", level=level))
            continue

        # Numbered list: 1. text, 2. text, etc.
        num_match = re.match(r'^(\s*)\d+\.\s+(.+)$', stripped)
        if num_match:
            flush_paragraph()
            indent = len(num_match.group(1))
            level = 1 + (indent // 2)
            blocks.append(_make_block("normal", num_match.group(2).strip(), list_item="number", level=level))
            continue

        # Table lines: accumulate consecutive rows into table_buffer,
        # then flush as a single block so the frontend renders an HTML table.
        if stripped.strip().startswith("|"):
            flush_paragraph()
            table_buffer.append(stripped.strip())
            continue

        # If we were accumulating table lines and hit a non-table line, flush the table
        if table_buffer:
            flush_table()

        # Horizontal rule: --- or *** or ___
        if re.match(r'^[\s]*[-*_]{3,}\s*$', stripped):
            flush_paragraph()
            continue

        # Pseudo-header: a line that is ONLY bold text ending with colon, e.g. **Something:**
        pseudo_match = re.match(r'^\*\*([^*]+)\*\*:?\s*$', stripped.strip())
        if pseudo_match:
            flush_paragraph()
            blocks.append(_make_block("h3", pseudo_match.group(1).strip()))
            continue

        # Regular text -> accumulate into paragraph
        paragraph_buffer.append(stripped.strip())

    # Flush any remaining buffers
    flush_table()
    flush_paragraph()

    return blocks
