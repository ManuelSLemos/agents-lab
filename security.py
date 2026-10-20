"""Security helpers shared by the *_secure agents."""


def wrap_untrusted(tag: str, text: str) -> str:
    """Mark text as DATA. Escapes < and > so the text cannot close the tag itself."""
    safe = text.replace("<", "&lt;").replace(">", "&gt;")
    return f"<{tag}>\n{safe}\n</{tag}>"
