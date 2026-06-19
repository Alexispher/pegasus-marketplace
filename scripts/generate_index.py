import json
import shutil
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


def normalize_file_path(file_value, folder_name, item_name):
    if not file_value:
        return ""

    if file_value.startswith("http://") or file_value.startswith("https://") or file_value.startswith("/"):
        return file_value

    return f"{folder_name}/{item_name}/{file_value}"


def create_package(category_key, item_path):
    packages_dir = Path("packages") / category_key
    packages_dir.mkdir(parents=True, exist_ok=True)

    zip_base_path = packages_dir / item_path.name
    zip_file_path = packages_dir / f"{item_path.name}.zip"

    if zip_file_path.exists():
        zip_file_path.unlink()

    shutil.make_archive(
        base_name=str(zip_base_path),
        format="zip",
        root_dir=item_path
    )

    return str(zip_file_path).replace("\\", "/")


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

            cover = normalize_file_path(
                metadata.get("cover", ""),
                folder_name,
                item_path.name
            )

            download = metadata.get("download", "")

            if download:
                download_path = normalize_file_path(download, folder_name, item_path.name)
            else:
                download_path = create_package(key, item_path)

            item_data = {
                "id": item_path.name,
                "name": metadata.get("name") or prettify_name(item_path.name),
                "category": key,
                "path": f"{folder_name}/{item_path.name}",
                "description": metadata.get("description", ""),
                "version": metadata.get("version", ""),
                "author": metadata.get("author", ""),
                "cover": cover,
                "download": download_path,
                "added_at": metadata.get("added_at", ""),
                "tags": metadata.get("tags", [])
            }

            data[key].append(item_data)

    with open("index.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    generate_index()
