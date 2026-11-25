#!/usr/bin/env python3
"""
Gabungkan lyric JSON word-level + lyric-blocks menjadi format:
[
  {"words": [{"text": "WORD", "delay": 0.5}, ...]},
  ...
]

Delay = waktu dari awal kata saat ini ke awal kata berikutnya.
Untuk kata terakhir pada satu baris, delay tetap dihitung sampai awal kata
pertama pada baris berikutnya, sehingga jeda antarbaris ikut tersimpan.
"""

import argparse
import json
from pathlib import Path


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_word_records(data):
    # Mendukung JSON berupa list langsung atau {"words": [...]}
    if isinstance(data, dict):
        data = data.get("words", [])

    if not isinstance(data, list):
        raise ValueError("File word-level harus berupa list atau object dengan key 'words'.")

    records = []
    for item in data:
        word = item.get("word", item.get("text"))
        start = item.get("start")
        end = item.get("end")
        line_index = item.get("line_index", item.get("line", 0))

        if word is None or start is None or end is None:
            continue

        records.append({
            "text": str(word),
            "start": float(start),
            "end": float(end),
            "line_index": int(line_index),
        })

    records.sort(key=lambda item: item["start"])
    if not records:
        raise ValueError("Tidak ada data kata valid (butuh word/text, start, end).")
    return records


def validate_blocks(data):
    # File blocks dipakai untuk validasi dan sebagai referensi susunan baris.
    if not isinstance(data, dict) or not isinstance(data.get("blocks"), list):
        raise ValueError("File blocks harus memiliki key 'blocks' berupa list.")

    block_lines = []
    for block in data["blocks"]:
        lines = block.get("lines", [])
        block_lines.extend(lines)
    return block_lines


def convert(words, block_lines, intro_text="...", include_intro=True):
    # Kelompokkan kata berdasarkan line_index, mempertahankan urutan waktu.
    grouped = {}
    for item in words:
        grouped.setdefault(item["line_index"], []).append(item)

    line_ids = sorted(grouped)
    output = []

    if include_intro and words[0]["start"] > 0:
        output.append({
            "words": [{
                "text": intro_text,
                "delay": round(words[0]["start"], 3)
            }]
        })

    # Cocokkan indeks baris word-level dengan baris pada file blocks.
    # Teks dari word-level tetap dipakai agar ejaan/pemisahan kata akurat.
    for pos, line_id in enumerate(line_ids):
        current_words = grouped[line_id]
        converted_words = []

        for word_pos, word in enumerate(current_words):
            if word_pos + 1 < len(current_words):
                next_start = current_words[word_pos + 1]["start"]
            elif pos + 1 < len(line_ids):
                next_start = grouped[line_ids[pos + 1]][0]["start"]
            else:
                next_start = word["end"]

            delay = max(0.0, next_start - word["start"])
            converted_words.append({
                "text": word["text"].upper(),
                "delay": round(delay, 3)
            })

        output.append({"words": converted_words})

    # Pemeriksaan ringan: jumlah baris dari word-level vs referensi blocks.
    if block_lines and len(block_lines) != len(line_ids):
        print(
            f"Catatan: blocks berisi {len(block_lines)} baris, "
            f"sedangkan word-level berisi {len(line_ids)} line_index. "
            "Output mengikuti line_index dari word-level."
        )

    return output


def main():
    parser = argparse.ArgumentParser(
        description="Konversi JSON word-level + blocks ke format lyric JSON."
    )
    parser.add_argument("blocks_json", help="File JSON lyric-blocks")
    parser.add_argument("words_json", help="File JSON word-level")
    parser.add_argument("-o", "--output", default="converted_lyrics.json",
                        help="Nama file output (default: converted_lyrics.json)")
    parser.add_argument("--intro-text", default="...",
                        help="Teks placeholder sebelum lirik dimulai (default: ...)")
    parser.add_argument("--no-intro", action="store_true",
                        help="Jangan tambahkan placeholder intro")
    args = parser.parse_args()

    blocks_data = load_json(args.blocks_json)
    words_data = load_json(args.words_json)

    block_lines = validate_blocks(blocks_data)
    words = get_word_records(words_data)
    result = convert(
        words,
        block_lines,
        intro_text=args.intro_text,
        include_intro=not args.no_intro
    )

    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    print(f"Berhasil: {len(result)} grup ditulis ke {args.output}")


if __name__ == "__main__":
    main()
