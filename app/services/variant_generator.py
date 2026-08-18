from app.models.post import Post


def _clean_markdown(markdown: str) -> str:
    lines = markdown.splitlines()

    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        line = line.lstrip("#").strip()

        if line:
            cleaned_lines.append(line)

    return " ".join(cleaned_lines)


def _source_text(post: Post) -> str:
    if post.source_markdown:
        return _clean_markdown(post.source_markdown)

    if post.source_url:
        return f"Read the full article: {post.source_url}"

    return ""


def generate_variant_content(
    post: Post,
    platform: str,
) -> str:
    source = _source_text(post)

    if platform == "telegram":
        return (
            f"🚀 {source}\n\n"
            "A quick look at the key ideas and why they matter.\n\n"
            "#AI #Technology"
        )

    if platform == "x":
        return (
            f"{source[:220]}\n\n"
            "What do you think? #AI"
        )[:280]

    if platform == "linkedin":
        return (
            f"{source}\n\n"
            "Here are the key ideas worth thinking about "
            "and how they can influence the future of technology.\n\n"
            "#AI #Technology #Innovation"
        )

    raise ValueError(f"Unsupported platform: {platform}")
