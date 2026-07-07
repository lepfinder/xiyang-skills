#!/usr/bin/env python3
"""查看 generate-image 本地生图记录（JSONL）。"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_LOG_PATH = SKILL_DIR / "logs" / "generations.jsonl"


def resolve_log_path() -> Path:
    custom = os.environ.get("IMAGE_GEN_LOG", "").strip()
    return Path(custom).expanduser() if custom else DEFAULT_LOG_PATH


def load_entries(log_path: Path) -> list[dict]:
    if not log_path.is_file():
        return []
    entries: list[dict] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description="List local image generation history")
    parser.add_argument("-n", "--limit", type=int, default=20, help="显示最近 N 条（默认 20）")
    parser.add_argument("--failed", action="store_true", help="仅显示失败记录")
    parser.add_argument("--json", action="store_true", help="JSON 数组输出")
    parser.add_argument("--log", help="指定日志文件路径")
    args = parser.parse_args()

    log_path = Path(args.log).expanduser() if args.log else resolve_log_path()
    entries = load_entries(log_path)

    if args.failed:
        entries = [e for e in entries if not e.get("ok")]

    entries = entries[-args.limit :]

    if args.json:
        print(json.dumps(entries, ensure_ascii=False, indent=2))
        return

    if not entries:
        print(f"暂无记录: {log_path}")
        sys.exit(0)

    print(f"日志: {log_path.resolve()}\n")
    for e in entries:
        status = "OK" if e.get("ok") else "FAIL"
        print(f"[{status}] {e.get('created_at', '?')}  #{e.get('id', '?')}")
        print(f"  provider: {e.get('provider')} / {e.get('model')}")
        print(f"  prompt:   {(e.get('prompt') or '')[:120]}{'…' if len(e.get('prompt') or '') > 120 else ''}")
        if e.get("output_path"):
            print(f"  output:   {e.get('output_path')}")
        if e.get("refs"):
            print(f"  refs:     {', '.join(e['refs'])}")
        if e.get("error"):
            print(f"  error:    {e.get('error')}")
        print()


if __name__ == "__main__":
    main()
