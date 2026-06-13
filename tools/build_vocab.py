#!/usr/bin/env python3
"""Build vocab.js from Hansol's two Chinese worksheets (data/*.docx).

Each worksheet entry looks like:
    亲戚 – qīn qi韩语句子：<Korean>中文翻译：<Chinese>拼音：<pinyin>

We parse those four parts, drop the explicit duplicate notes the worksheets
contain, dedupe by hanzi, tag each word with a theme, and emit a single
`window.VOCAB = [...]` file the offline/online app loads. Run from repo root:

    python3 tools/build_vocab.py
"""
import re
import sys
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = [ROOT / "data" / "worksheet1.docx", ROOT / "data" / "worksheet2.docx"]
# Extra words Claude transcribes from photos / new documents Stanley sends.
# One tab-separated row per word: hanzi <TAB> pinyin <TAB> kr <TAB> cn_sentence
# <TAB> cn_pinyin <TAB> theme. Trailing columns may be left blank. Lines
# starting with "#" are ignored. See data/extra/template.tsv.
EXTRA_DIR = ROOT / "data" / "extra"
COLS = ["hanzi", "pinyin", "kr", "cn_sentence", "cn_pinyin", "theme"]
OUT = ROOT / "vocab.js"

# Pull the plain text out of a .docx (paragraphs separated by newlines).
def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    xml = xml.replace("</w:p>", "\n")
    return re.sub(r"<[^>]+>", "", xml)


# hanzi may contain the ellipsis used in grammar patterns (又…又…, 是…的).
HANZI = r"[一-鿿…]"
# pinyin / romanization: anything that is not CJK, a newline, or a full-width
# paren/colon. This makes orphan "duplicate" headers (which lack 韩语句子...)
# fail to match, so they are skipped automatically.
NOT_CJK = r"[^一-鿿\n（：]"

ENTRY = re.compile(
    rf"({HANZI}+)\s*–\s*({NOT_CJK}+?)"      # hanzi – pinyin
    r"韩语句子：(.+?)"        # 韩语句子：Korean
    r"中文翻译：(.+?)"        # 中文翻译：Chinese
    r"拼音：([^一-鿿（]+)", # 拼音：sentence pinyin
    re.S,
)

# trailing list-numbering that leaks into a captured field, e.g. "...bān.11. "
TRAIL_NUM = re.compile(r"\s*\d+\.?\s*$")


def clean(s: str) -> str:
    return TRAIL_NUM.sub("", s.strip()).strip()


# --- theme tagging --------------------------------------------------------
# Display labels (English + Korean) live in the app; here we just emit the key.
THEME = {
    "family": "亲戚 外公 外婆 阿姨 姨妈 舅舅 孩子 爷爷 女儿 儿子 奶奶 大伯 叔叔 姑姑",
    "clothing": "领带 皮带 皮鞋 连衣裙 套装 袜子 戴 鞋 凉鞋 围巾 帽子 手套 雨伞 西装 皮靴 双 件 顶 副 耳环 项链 游泳衣 试 合适",
    "body": "腰 背 脖子 肩膀 手指头 脚指头 眉毛 屁股 个子 直 瓜子脸 圆 瘦 帅 胖 漂亮",
    "weather": "暖和 雾 雷 雷雨 凉快 干燥 潮湿 冰雹 发大水 龙卷风 沙尘暴 太阳",
    "health": "流鼻涕 肚子 拉肚子 量体温 开药 发烧 咳嗽 嗓子疼 耳朵疼 眼睛疼 受 受伤 病假 请假 请病假 给",
    "subjects": "物理 生物 化学 地理 科目 功课 测验 考试 学期 教 难 容易 有用 意思 有意思 写 介绍 为什么 觉得 教学",
    "facilities": "校长 办公室 教师 校医室 图书馆 礼堂 操场 体育馆 篮球场 足球场 游泳池 停车场 教室 三层 实验 实验室 隔壁 厕所 男 幢 公司 律师行",
    "stationery": "铅笔 钢笔 尺子 橡皮 白板 卷笔刀 练习本 计算器",
    "sports": "踢 足球 滑冰 滑雪 羽毛 羽毛球 排球 乒乓球 钓鱼",
    "directions": "中间 上面 下面 前面 后面 对面 楼上 楼下 旁边 左边 右边 左面 右面",
    "places": "洛杉矶 纽约 加拿大",
    "time": "圣诞节 春节 前年 暑假 寒假 小时候 已经 去世 过",
    "grammar": "又…又… 是…的 …的时候 的时候 别 因为 所以 如果 不用 最好 能 不能 需要 太…了 对…好 对…感兴趣 有点儿 几 万 千 当然 祝 亲爱 不见",
}
WORD2THEME = {}
for theme, words in THEME.items():
    for w in words.split():
        WORD2THEME.setdefault(w.rstrip("?"), theme)
# words that fall through (忙 出差 见面 找 帮 着急 报纸 量 ...) → "other"


def main() -> int:
    records = []
    seen = set()
    for src in SOURCES:
        if not src.exists():
            print(f"missing source: {src}", file=sys.stderr)
            return 1
        text = docx_text(src)
        for m in ENTRY.finditer(text):
            hanzi = clean(m.group(1))
            if hanzi in seen:
                continue
            seen.add(hanzi)
            records.append({
                "id": len(records) + 1,
                "hanzi": hanzi,
                "pinyin": clean(m.group(2)),
                "kr": m.group(3).strip(),
                "cn_sentence": m.group(4).strip(),
                "cn_pinyin": clean(m.group(5)),
                "theme": WORD2THEME.get(hanzi, "other"),
            })

    # supplementary words (photos / new docs transcribed into data/extra/*.tsv)
    for tsv in sorted(EXTRA_DIR.glob("*.tsv")) if EXTRA_DIR.exists() else []:
        for ln, raw in enumerate(tsv.read_text(encoding="utf-8").splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            cells = [c.strip() for c in raw.split("\t")]
            row = dict(zip(COLS, cells + [""] * (len(COLS) - len(cells))))
            hanzi = row["hanzi"]
            if not hanzi or not row["kr"]:
                print(f"skip {tsv.name}:{ln} (need hanzi + kr): {line[:40]}", file=sys.stderr)
                continue
            if hanzi in seen:
                continue
            seen.add(hanzi)
            records.append({
                "id": len(records) + 1,
                "hanzi": hanzi,
                "pinyin": row["pinyin"],
                "kr": row["kr"],
                "cn_sentence": row["cn_sentence"],
                "cn_pinyin": row["cn_pinyin"],
                "theme": row["theme"] or WORD2THEME.get(hanzi, "other"),
            })

    # sanity: core fields populated (example sentence is optional for extras)
    bad = [r for r in records if not all(r[k] for k in ("hanzi", "kr"))]
    if bad:
        print(f"WARNING: {len(bad)} records with empty fields", file=sys.stderr)
        for r in bad[:5]:
            print("  ", r, file=sys.stderr)

    body = json.dumps(records, ensure_ascii=False, indent=2)
    OUT.write_text(
        "// Auto-generated by tools/build_vocab.py from data/worksheet{1,2}.docx\n"
        "// plus any data/extra/*.tsv. Hansol's Chinese vocabulary. Do not edit by hand.\n"
        f"window.VOCAB = {body};\n",
        encoding="utf-8",
    )

    counts = {}
    for r in records:
        counts[r["theme"]] = counts.get(r["theme"], 0) + 1
    print(f"wrote {len(records)} unique words -> {OUT.relative_to(ROOT)}")
    for t, c in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {t:12} {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
