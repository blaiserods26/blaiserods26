#!/usr/bin/env python3
import json
import re
import urllib.request
from pathlib import Path

NAMESPACE = "BlaiseRodrigues"
README_PATH = Path(__file__).resolve().parent.parent.parent / "README.md"

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "GitHub-Actions-OpenVSX-Updater"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    print(f"Fetching Open VSX extensions for namespace: {NAMESPACE}...")
    namespace_data = fetch_json(f"https://open-vsx.org/api/{NAMESPACE}")
    extensions_dict = namespace_data.get("extensions", {})

    items = []
    total_downloads = 0

    for slug, url in extensions_dict.items():
        try:
            info = fetch_json(url)
            downloads = info.get("downloadCount", 0)
            total_downloads += downloads
            repo_url = info.get("repository", f"https://github.com/blaiserods26/{slug}")
            if repo_url:
                repo_url = repo_url.rstrip("/").removesuffix(".git")
            items.append({
                "slug": slug,
                "name": info.get("displayName", slug),
                "version": info.get("version", "latest"),
                "downloads": downloads,
                "rating": info.get("averageRating", 5.0),
                "reviews": info.get("reviewCount", 0),
                "description": info.get("description", ""),
                "repo": repo_url,
                "openvsx_url": f"https://open-vsx.org/extension/{NAMESPACE}/{slug}"
            })
        except Exception as e:
            print(f"Error fetching {slug}: {e}")

    # Sort descending by downloads
    items.sort(key=lambda x: x["downloads"], reverse=True)

    print(f"Found {len(items)} extensions. Total downloads: {total_downloads}")

    # Build markdown snippet
    table_lines = [
        "<!-- OPENVSX_STATS_START -->",
        f"<p align=\"center\">",
        f"  <a href=\"https://open-vsx.org/extension/{NAMESPACE}\">",
        f"    <img src=\"https://img.shields.io/badge/Verified_Publisher-{NAMESPACE}-6933FF?style=for-the-badge&logo=visualstudiocode&logoColor=white\" alt=\"Open VSX Publisher\" />",
        f"  </a>",
        f"  &nbsp;",
        f"  <img src=\"https://img.shields.io/badge/Total_Downloads-{total_downloads:,}+-238636?style=for-the-badge&logo=openvsx&logoColor=white\" alt=\"Total Downloads\" />",
        f"  &nbsp;",
        f"  <img src=\"https://img.shields.io/badge/Published_Extensions-{len(items)}-blue?style=for-the-badge&logo=visualstudiocode&logoColor=white\" alt=\"Published Extensions\" />",
        f"</p>",
        "",
        "| Extension | Target IDEs | Live Downloads | Latest Version | Rating | Repository |",
        "| :--- | :--- | :---: | :---: | :---: | :---: |"
    ]

    for item in items:
        slug = item["slug"]
        name = item["name"]
        openvsx_url = item["openvsx_url"]
        repo = item["repo"]
        target = "Google Antigravity IDE & VS Code" if slug == "Quotoo" else "VS Code, VSCodium & Cursor"
        
        # Live shields badges fetch real-time numbers directly from Open VSX API
        dl_badge = f'<a href="{openvsx_url}"><img src="https://img.shields.io/open-vsx/dt/{NAMESPACE}/{slug}?style=flat-square&logo=openvsx&logoColor=white&label=Downloads&color=2ea44f" alt="{name} Downloads" /></a>'
        ver_badge = f'<a href="{openvsx_url}"><img src="https://img.shields.io/open-vsx/v/{NAMESPACE}/{slug}?style=flat-square&color=0969da" alt="{name} Version" /></a>'
        rating_badge = f'<a href="{openvsx_url}"><img src="https://img.shields.io/open-vsx/rating/{NAMESPACE}/{slug}?style=flat-square&color=ea7233" alt="{name} Rating" /></a>'
        repo_link = f'[Code]({repo})'

        table_lines.append(
            f'| [**{name}**]({openvsx_url}) | `{target}` | {dl_badge} | {ver_badge} | {rating_badge} | {repo_link} |'
        )

    table_lines.append("<!-- OPENVSX_STATS_END -->")
    replacement = "\n".join(table_lines)

    if not README_PATH.exists():
        print(f"README not found at {README_PATH}")
        return

    content = README_PATH.read_text(encoding="utf-8")
    pattern = r"<!-- OPENVSX_STATS_START -->[\s\S]*?<!-- OPENVSX_STATS_END -->"
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, replacement, content)
        print("Updated existing OPENVSX_STATS block in README.md")
    else:
        print("OPENVSX_STATS markers not found. Please insert markers into README.md")
        return

    README_PATH.write_text(new_content, encoding="utf-8")
    print("README.md successfully updated!")

if __name__ == "__main__":
    main()
