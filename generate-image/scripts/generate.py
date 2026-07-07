#!/usr/bin/env python3
"""
Standalone image generation — 万相 (DashScope) & Google Gemini.
不依赖 Ada Core generate_image 工具，Agent 通过 shell 直接调用。

参考实现：apps/core/src/domain/agent/tools/image/engines/wanxiang.ts
          apps/core/src/domain/agent/tools/image/engines/google.ts
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_LOG_PATH = SKILL_DIR / "logs" / "generations.jsonl"

WANXIANG_DEFAULT_URL = (
    "https://token-plan.cn-beijing.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
)
WANXIANG_DEFAULT_MODEL = "wan2.7-image-pro"

GEMINI_DEFAULT_MODEL = "gemini-3.1-flash-image-preview"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

ASPECT_TO_SIZE = {
    "1:1": "1024*1024",
    "16:9": "1280*720",
    "9:16": "720*1280",
}

GEMINI_ASPECT_MAP = {
    "16:9": "ASPECT_RATIO_SIXTEEN_BY_NINE",
    "9:16": "ASPECT_RATIO_NINE_BY_SIXTEEN",
    "1:1": "ASPECT_RATIO_ONE_BY_ONE",
    "4:3": "ASPECT_RATIO_FOUR_BY_THREE",
    "3:4": "ASPECT_RATIO_THREE_BY_FOUR",
    "3:2": "ASPECT_RATIO_THREE_BY_TWO",
    "2:3": "ASPECT_RATIO_TWO_BY_THREE",
}


def resolve_log_path() -> Path:
    custom = os.environ.get("IMAGE_GEN_LOG", "").strip()
    return Path(custom).expanduser() if custom else DEFAULT_LOG_PATH


def append_generation_log(entry: dict[str, Any], *, enabled: bool) -> Path | None:
    if not enabled:
        return None
    log_path = resolve_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return log_path


def build_log_entry(
    *,
    ok: bool,
    prompt: str,
    provider: str,
    model: str,
    aspect_ratio: str,
    output_path: str | None,
    ref_paths: list[str],
    error: str | None = None,
) -> dict[str, Any]:
    return {
        "id": uuid4().hex[:12],
        "ok": ok,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt,
        "provider": provider,
        "model": model,
        "aspect_ratio": aspect_ratio,
        "output_path": output_path,
        "refs": ref_paths,
        "error": error,
    }


def load_env_file() -> None:
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[1] / ".env",
        Path.home() / ".image_gen_env",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
        break


def http_json(
    url: str,
    *,
    method: str = "POST",
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
    timeout: int = 180,
) -> tuple[int, Any]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw) if raw else {"error": str(e)}
        except json.JSONDecodeError:
            payload = {"error": raw or str(e)}
        return e.code, payload


def download_file(url: str, dest: Path, timeout: int = 180) -> None:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        dest.write_bytes(resp.read())


def resolve_output_path(output: str | None, suffix: str = "png") -> Path:
    if output:
        path = Path(output).expanduser()
    else:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = Path.cwd() / f"generated-{ts}.{suffix}"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


MIME_BY_EXT = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def load_reference_image(path_str: str) -> dict[str, str]:
    """读取本地参考图，返回 base64 / mime / dataUri（对齐 Ada readImageAsBase64）。"""
    path = Path(path_str).expanduser()
    if not path.is_file():
        print(f"错误：参考图不存在: {path}", file=sys.stderr)
        raise FileNotFoundError(f"参考图不存在: {path}")
    ext = path.suffix.lower()
    mime = MIME_BY_EXT.get(ext, "image/png")
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return {
        "base64": b64,
        "mimeType": mime,
        "dataUri": f"data:{mime};base64,{b64}",
        "path": str(path.resolve()),
    }


def get_dashscope_key() -> str:
    key = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("WANXIANG_API_KEY")
    if not key:
        print("错误：请设置 DASHSCOPE_API_KEY 或 WANXIANG_API_KEY", file=sys.stderr)
        sys.exit(1)
    return key


def get_gemini_key() -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("错误：请设置 GEMINI_API_KEY", file=sys.stderr)
        sys.exit(1)
    return key


def generate_wanxiang(
    prompt: str,
    *,
    model: str,
    aspect_ratio: str,
    output: str | None,
    base_url: str | None,
    ref_images: list[dict[str, str]],
) -> Path:
    api_key = get_dashscope_key()
    url = base_url or os.environ.get("DASHSCOPE_BASE_URL") or WANXIANG_DEFAULT_URL
    size = ASPECT_TO_SIZE.get(aspect_ratio, ASPECT_TO_SIZE["1:1"])
    is_compatible = "compatible-mode" in url

    if ref_images and is_compatible:
        print("警告：compatible-mode 万相接口不支持 --ref，已忽略参考图", file=sys.stderr)

    if is_compatible:
        status, data = http_json(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            body={"model": model, "prompt": prompt, "n": 1, "size": size},
        )
        if status != 200:
            raise RuntimeError(f"万相 API 失败 ({status}): {json.dumps(data, ensure_ascii=False)}")
        image_url = (data.get("data") or [{}])[0].get("url")
    else:
        content: list[dict[str, str]] = [{"text": prompt}]
        for ref in ref_images:
            content.append({"image": ref["dataUri"]})
        status, data = http_json(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "X-DashScope-Async": "disable",
            },
            body={
                "model": model,
                "input": {"messages": [{"role": "user", "content": content}]},
                "parameters": {
                    "n": 1,
                    "size": size,
                    "aspect_ratio": aspect_ratio,
                    "watermark": False,
                },
            },
        )
        if status != 200:
            raise RuntimeError(f"万相 API 失败 ({status}): {json.dumps(data, ensure_ascii=False)}")
        image_url = None
        choices = (data.get("output") or {}).get("choices") or []
        if choices:
            content = (choices[0].get("message") or {}).get("content") or []
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("image"):
                        image_url = item["image"]
                        break

    if not image_url:
        raise RuntimeError(f"万相未返回图片 URL: {json.dumps(data, ensure_ascii=False)}")

    out_path = resolve_output_path(output)
    download_file(image_url, out_path)
    return out_path


def generate_gemini(
    prompt: str,
    *,
    model: str,
    aspect_ratio: str,
    output: str | None,
    ref_images: list[dict[str, str]],
) -> Path:
    api_key = get_gemini_key()
    url = f"{GEMINI_API_BASE}/models/{model}:generateContent?key={api_key}"

    generation_config: dict[str, Any] = {"responseModalities": ["IMAGE"]}
    google_ratio = GEMINI_ASPECT_MAP.get(aspect_ratio)
    if google_ratio:
        generation_config["responseFormat"] = {"image": {"aspectRatio": google_ratio}}

    parts: list[dict[str, Any]] = [{"text": prompt}]
    for ref in ref_images:
        parts.append({"inlineData": {"mimeType": ref["mimeType"], "data": ref["base64"]}})

    status, data = http_json(
        url,
        body={
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": generation_config,
        },
    )
    if status != 200:
        raise RuntimeError(f"Gemini API 失败 ({status}): {json.dumps(data, ensure_ascii=False)}")

    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"Gemini 无 candidates: {json.dumps(data, ensure_ascii=False)}")

    parts = (candidates[0].get("content") or {}).get("parts") or []
    image_b64 = None
    for part in parts:
        inline = part.get("inlineData")
        if inline and str(inline.get("mimeType", "")).startswith("image/"):
            image_b64 = inline.get("data")
            break
        if part.get("text"):
            raise RuntimeError(f"Gemini 返回文本而非图片: {part['text']}")

    if not image_b64:
        raise RuntimeError(f"Gemini 响应中无图片: {json.dumps(data, ensure_ascii=False)}")

    out_path = resolve_output_path(output)
    out_path.write_bytes(base64.b64decode(image_b64))
    return out_path


def main() -> None:
    load_env_file()

    parser = argparse.ArgumentParser(description="Standalone image generation (Wanxiang / Gemini)")
    parser.add_argument("prompt", help="绘图提示词（建议英文，中文也可）")
    parser.add_argument(
        "--provider",
        "-p",
        choices=["wanxiang", "gemini"],
        default="wanxiang",
        help="生图提供商（默认 wanxiang）",
    )
    parser.add_argument("--model", "-m", help="模型 ID（省略则用各提供商默认值）")
    parser.add_argument(
        "--aspect-ratio",
        "-a",
        choices=["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"],
        default="16:9",
        help="宽高比（默认 16:9）",
    )
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--base-url", help="万相 API 地址（仅 wanxiang）")
    parser.add_argument(
        "--ref",
        "-r",
        action="append",
        default=[],
        metavar="IMAGE",
        help="参考图/垫图路径，可多次指定（万相 DashScope 原生 + Gemini 均支持）",
    )
    parser.add_argument("--json", action="store_true", help="以 JSON 打印结果路径")
    parser.add_argument(
        "--no-log",
        action="store_true",
        help="不写入本地生图记录（默认每次成功/失败都会追加到 logs/generations.jsonl）",
    )

    args = parser.parse_args()
    ref_images = [load_reference_image(p) for p in args.ref]
    ref_paths = [r["path"] for r in ref_images]
    log_enabled = not args.no_log

    try:
        if args.provider == "wanxiang":
            model = args.model or WANXIANG_DEFAULT_MODEL
            out = generate_wanxiang(
                args.prompt,
                model=model,
                aspect_ratio=args.aspect_ratio,
                output=args.output,
                base_url=args.base_url,
                ref_images=ref_images,
            )
            provider_label = f"wanxiang/{model}"
        else:
            model = args.model or GEMINI_DEFAULT_MODEL
            out = generate_gemini(
                args.prompt,
                model=model,
                aspect_ratio=args.aspect_ratio,
                output=args.output,
                ref_images=ref_images,
            )
            provider_label = f"gemini/{model}"

        out_str = str(out.resolve())
        log_entry = build_log_entry(
            ok=True,
            prompt=args.prompt,
            provider=args.provider,
            model=model,
            aspect_ratio=args.aspect_ratio,
            output_path=out_str,
            ref_paths=ref_paths,
        )
        log_path = append_generation_log(log_entry, enabled=log_enabled)

        result = {
            "ok": True,
            "provider": provider_label,
            "path": out_str,
            "refs": ref_paths,
            "log_id": log_entry["id"],
            "log_path": str(log_path.resolve()) if log_path else None,
        }
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(f"已生成 ({provider_label}): {out_str}")
            if log_path:
                print(f"已记录: {log_path.resolve()} (#{log_entry['id']})")
    except (Exception, FileNotFoundError) as exc:
        model = args.model or (
            WANXIANG_DEFAULT_MODEL if args.provider == "wanxiang" else GEMINI_DEFAULT_MODEL
        )
        log_entry = build_log_entry(
            ok=False,
            prompt=args.prompt,
            provider=args.provider,
            model=model,
            aspect_ratio=args.aspect_ratio,
            output_path=args.output,
            ref_paths=ref_paths,
            error=str(exc),
        )
        log_path = append_generation_log(log_entry, enabled=log_enabled)
        print(str(exc), file=sys.stderr)
        if log_path:
            print(f"失败已记录: {log_path.resolve()} (#{log_entry['id']})", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
