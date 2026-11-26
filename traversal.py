from pathlib import Path

songs_path = Path("Songs")

for item in songs_path.iterdir():
    if item.is_dir():
        print(item.name)