import yaml
from pathlib import Path
from httpx import get
from json import dump

json_path = Path(__file__).parent / "achievement.json"


def main():
    yml_data = get(
        "https://cdn.staticaly.com/gh/misskey-dev/misskey/develop/locales/zh-CN.yml"
    )
    json_raw_data = yaml.safe_load(yml_data.text)
    json_data = {}

    for key, value in json_raw_data["_achievements"]["_types"].items():
        json_data[key[1:]] = (
            value.get("title", ""),
            value.get("description", ""),
            value.get("flavor", ""),
        )

    with open(json_path, "w", encoding="utf-8") as f:
        dump(json_data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
