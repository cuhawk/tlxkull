"""Insert 'blog bodies ingested' marker into the people pages whose blogs
were ingested 2026-05-19."""
import re
from pathlib import Path

PEOPLE = Path("/Users/soural/Documents/TLX/wiki/people")

LINKS = {
    "james-kettle": [
        "wiki/sources/blogs/personal/portswigger-research/",
        "wiki/sources/blogs/personal/skeletonscribe-kettle/",
    ],
    "gareth-heyes": [
        "wiki/sources/blogs/personal/portswigger-research/",
        "wiki/sources/blogs/personal/thespanner-heyes/",
    ],
    "johann-rehberger": ["wiki/sources/blogs/personal/embracethered/"],
    "shubham-shah": ["wiki/sources/blogs/personal/assetnote/"],
    "sean-yeoh": ["wiki/sources/blogs/personal/assetnote/"],
    "zlz": ["wiki/sources/blogs/personal/zlz-buerhaus/"],
    "sam-curry": ["wiki/sources/blogs/personal/sam-curry/"],
    "kevin-mizu": ["wiki/sources/blogs/personal/kevin-mizu/"],
    "michal-bentkowski": ["wiki/sources/blogs/personal/securitum-research/"],
    "spaceraccoon": [
        "wiki/sources/blogs/personal/spaceraccoon/",
        "wiki/sources/blogs/personal/spaceraccoon-book/",
    ],
    "sergey-toshin": ["wiki/sources/blogs/personal/oversecured/"],
    "mathias-karlsson": ["wiki/sources/blogs/detectify/"],  # cofounder, posts under Detectify Labs
    # Second-pass cross-links from fallback-crawler + firecrawl-resume runs:
    "daniel-thatcher": ["wiki/sources/blogs/personal/daniel-thatcher/"],
    "jack-cable": ["wiki/sources/blogs/personal/jack-cable/"],
    "gal-nagli": ["wiki/sources/blogs/personal/naglinagli-gh/"],
    "douglas-day": ["wiki/sources/blogs/personal/douglas-day/"],
    "matanber": ["wiki/sources/blogs/personal/matanber/"],
    "corben-leo": ["wiki/sources/blogs/personal/corben-leo/"],
    "daniel-miessler": ["wiki/sources/blogs/personal/daniel-miessler/"],
    "matt-brown": ["wiki/sources/blogs/personal/matt-brown/"],
    "inti-de-ceukelaire": ["wiki/sources/blogs/personal/inti/"],
    "alex-chapman": ["wiki/sources/blogs/personal/alex-chapman/"],
    "sam-erb": ["wiki/sources/blogs/personal/sam-erb/"],
    "slonser": ["wiki/sources/blogs/personal/slonser/"],
    "rez0": ["wiki/sources/blogs/personal/rez0-thacker/"],
}


def marker(paths: list[str]) -> str:
    bullet = "\n  ".join(f"`{p}`" for p in paths)
    return (
        "\n## Wiki RAG ingestion\n\n"
        "Blog bodies ingested 2026-05-19 into the `wiki` Chroma collection.\n"
        "Source files:\n\n"
        f"- {bullet}\n\n"
        'Query via `docs_query(collection="wiki", query="...")` instead of WebFetch.\n'
    )


def update_one(slug: str, paths: list[str]) -> bool:
    p = PEOPLE / f"{slug}.md"
    if not p.exists():
        print(f"MISSING: {p}")
        return False
    text = p.read_text()
    if "## Wiki RAG ingestion" in text:
        return False
    # Update updated_utc if frontmatter has it
    text = re.sub(r"updated_utc:\s*\S+", "updated_utc: 2026-05-19T14:42:00Z", text, count=1)
    text = text.rstrip() + "\n" + marker(paths) + "\n"
    p.write_text(text)
    return True


def main():
    changed = 0
    for slug, paths in LINKS.items():
        if update_one(slug, paths):
            changed += 1
            print(f"  updated: {slug}")
    print(f"Updated {changed}/{len(LINKS)} people pages.")


if __name__ == "__main__":
    main()
