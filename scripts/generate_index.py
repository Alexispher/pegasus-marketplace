```python
import json
from pathlib import Path


CATEGORIES = {
    "mods": "Mods",
    "plugins": "Plugins",
    "themes": "Themes"
}


def prettify_name(name):
    return name.replace("-", " ").replace("_", " ").title()


def read_marketplace_json(item_path):
    metadata_file = item_path / "marketplace.json"

    if not metadata_file.exists():
        return {}

    try:
        with metadata_file.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def normalize_cover(cover, folder_name, item_name):
    if not cover:
        return ""

    if cover.startswith("http://") or cover.startswith("https://") or cover.startswith("/"):
        return cover

    return f"{folder_name}/{item_name}/{cover}"


def generate_index():
    data = {
        "mods": [],
        "plugins": [],
        "themes": []
    }

    for key, folder_name in CATEGORIES.items():
        folder_path = Path(folder_name)

        if not folder_path.exists():
            continue

        for item_path in sorted(folder_path.iterdir()):
            if not item_path.is_dir():
                continue

            if item_path.name.startswith("."):
                continue

            metadata = read_marketplace_json(item_path)

            name = metadata.get("name") or prettify_name(item_path.name)

            item_data = {
                "id": item_path.name,
                "name": name,
                "category": key,
                "path": f"{folder_name}/{item_path.name}",
                "description": metadata.get("description", ""),
                "version": metadata.get("version", ""),
                "author": metadata.get("author", ""),
                "cover": normalize_cover(
                    metadata.get("cover", ""),
                    folder_name,
                    item_path.name
                ),
                "tags": metadata.get("tags", [])
            }

            data[key].append(item_data)

    with open("index.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    generate_index()
```
