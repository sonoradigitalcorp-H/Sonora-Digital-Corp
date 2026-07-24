from pathlib import Path
import re


def chunk_markdown(filepath: Path) -> list[dict]:
    text = filepath.read_text(encoding="utf-8")
    rel = str(filepath)
    title = filepath.stem

    lines = text.split("\n")
    chunks = []
    current_section = None
    current_lines = []

    def flush():
        if not current_lines:
            return
        content = "\n".join(current_lines).strip()
        if len(content) < 20:
            return
        chunks.append({
            "content": content,
            "metadata": {
                "source": rel,
                "title": title,
                "section": current_section or title,
                "type": "obsidian",
            },
        })

    for line in lines:
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            flush()
            level = len(heading.group(1))
            current_section = heading.group(2).strip()
            current_lines = [line]
        else:
            current_lines.append(line)
    flush()

    return chunks
