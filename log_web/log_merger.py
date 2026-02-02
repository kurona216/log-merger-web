import re
from datetime import datetime

def merge_logs(file_contents):
    all_entries = []

    for content in file_contents:
        entries = parse_file(content)
        all_entries.extend(entries)

    merged = merge_all_entries(all_entries)
    merged.sort(key=lambda x: x["timestamp"] or datetime.max)

    output_lines = []
    for e in merged:
        output_lines.append(normalize_date(e["raw"]))
        output_lines.append("")

    return "\n".join(output_lines)

# ================= 解析日志（支持多行） =================

def parse_file(content):
    lines = content.split("\n")
    entries = []

    header_pattern = re.compile(
        r'^(.*?)\(\d+\)\s+\d{4}[-/]\d{2}[-/]\d{2} \d{2}:\d{2}:\d{2}$'
    )

    current_header = None
    current_body = []

    for line in lines:
        if header_pattern.match(line.strip()):
            if current_header:
                entries.append(build_entry(
                    current_header,
                    "\n".join(current_body).rstrip()
                ))
            current_header = line.strip()
            current_body = []
        else:
            if current_header:
                current_body.append(line)

    if current_header:
        entries.append(build_entry(
            current_header,
            "\n".join(current_body).rstrip()
        ))

    return entries

def build_entry(header, body):
    return {
        "raw": header + "\n" + body,
        "timestamp": extract_timestamp(header),
        "speaker": extract_speaker(header),
        "content": body,
        "is_cq": "CQ:image" in body,
        "is_plain_img": "[图片]" in body
    }

# ================= 工具函数 =================

def extract_timestamp(line):
    m = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2} \d{2}:\d{2}:\d{2})', line)
    if not m:
        return None
    return datetime.strptime(m.group(1).replace("-", "/"), "%Y/%m/%d %H:%M:%S")

def extract_speaker(line):
    m = re.search(r'^(.*?)(?=\s*\d{4})', line)
    return m.group(1).strip() if m else ""

def normalize_date(text):
    return re.sub(r'(\d{4})-(\d{2})-(\d{2})', r'\1/\2/\3', text)

# ================= 合并 & CQ 精准替换 =================

def merge_all_entries(entries):
    groups = {}
    for e in entries:
        key = (e["timestamp"], e["speaker"])
        groups.setdefault(key, []).append(e)

    result = []

    for group in groups.values():
        plain_imgs = [e for e in group if e["is_plain_img"]]
        cq_imgs = [e for e in group if e["is_cq"]]
        others = [e for e in group if not e["is_plain_img"] and not e["is_cq"]]

        result.extend(unique_by_content(others))

        if plain_imgs and cq_imgs:
            for i in range(min(len(plain_imgs), len(cq_imgs))):
                result.append(cq_imgs[i])
            if len(cq_imgs) > len(plain_imgs):
                result.extend(cq_imgs[len(plain_imgs):])
        else:
            result.extend(plain_imgs)
            result.extend(cq_imgs)

    return result

def unique_by_content(entries):
    seen = set()
    out = []
    for e in entries:
        if e["content"] not in seen:
            seen.add(e["content"])
            out.append(e)
    return out
