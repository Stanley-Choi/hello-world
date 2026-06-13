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
COLS = ["hanzi", "pinyin", "kr", "cn_sentence", "cn_pinyin", "theme", "meaning"]
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

# Concise Korean word glosses (the worksheets only had example sentences).
# Shown as the "word" on the Korean side of flashcards and quiz. Easy to tweak.
MEANING = {
    "亲戚": "친척", "圣诞节": "크리스마스", "领带": "넥타이", "皮带": "벨트",
    "皮鞋": "구두", "连衣裙": "원피스", "套装": "정장 세트", "袜子": "양말",
    "经理": "경리·매니저", "公司": "회사", "戴": "(안경·모자를) 쓰다", "过": "(명절을) 지내다",
    "忙": "바쁘다", "出差": "출장", "律师行": "변호사 사무실", "外公": "외할아버지",
    "外婆": "외할머니", "前年": "재작년", "去世": "돌아가시다", "阿姨": "이모·아주머니",
    "姨妈": "이모", "舅舅": "외삼촌", "孩子": "아이", "校长": "교장",
    "办公室": "사무실", "教师": "교사", "校医室": "보건실", "中间": "가운데",
    "上面": "위쪽", "下面": "아래쪽", "爷爷": "할아버지", "女儿": "딸",
    "前面": "앞쪽", "后面": "뒤쪽", "对面": "맞은편", "楼上": "위층", "楼下": "아래층",
    "儿子": "아들", "见面": "만나다", "春节": "설날·춘절", "漂亮": "예쁘다",
    "瓜子脸": "갸름한 얼굴", "圆": "둥글다", "瘦": "마르다", "又…又…": "~하기도 ~하기도",
    "帅": "잘생기다", "奶奶": "할머니", "有点儿": "조금", "胖": "뚱뚱하다",
    "腰": "허리", "背": "등", "脖子": "목", "肩膀": "어깨", "手指头": "손가락",
    "脚指头": "발가락", "眉毛": "눈썹", "屁股": "엉덩이", "洛杉矶": "로스앤젤레스",
    "个子": "키", "直": "곧다·직모", "是…的": "~한 것이다(강조)", "不见": "안 보이다",
    "报纸": "신문", "的时候": "~할 때", "别": "~하지 마라", "着急": "조급하다",
    "帮": "돕다", "找": "찾다", "大伯": "큰아버지", "流鼻涕": "콧물이 나다",
    "肚子": "배", "拉肚子": "설사하다", "给": "주다", "量体温": "체온을 재다",
    "开药": "약을 처방하다", "一些": "조금·약간", "发烧": "열이 나다", "咳嗽": "기침하다",
    "嗓子疼": "목이 아프다", "叔叔": "삼촌", "耳朵疼": "귀가 아프다", "眼睛疼": "눈이 아프다",
    "踢": "(발로) 차다", "足球": "축구", "受": "받다·입다", "受伤": "다치다",
    "需要": "필요하다", "所以": "그래서", "能": "~할 수 있다", "不能": "~할 수 없다",
    "姑姑": "고모", "病假": "병가", "请假": "휴가를 내다", "请病假": "병가를 내다",
    "暖和": "따뜻하다", "雾": "안개", "雷": "천둥", "雷雨": "뇌우", "凉快": "시원하다",
    "干燥": "건조하다", "纽约": "뉴욕", "潮湿": "습하다", "冰雹": "우박",
    "发大水": "홍수가 나다", "龙卷风": "토네이도", "沙尘暴": "황사", "亲爱": "친애하는",
    "如果": "만약", "暑假": "여름방학", "鞋": "신발", "凉鞋": "샌들", "因为": "~때문에",
    "寒假": "겨울방학", "不用": "~할 필요 없다", "围巾": "목도리·스카프", "帽子": "모자",
    "手套": "장갑", "最好": "~하는 게 좋다", "雨伞": "우산", "祝": "(축하를) 빌다",
    "西装": "양복", "双": "켤레(양사)", "皮靴": "가죽 부츠", "试": "입어보다·해보다",
    "当然": "당연히·물론", "合适": "알맞다", "千": "천(1,000)", "太…了": "너무 ~하다",
    "小时候": "어렸을 때", "加拿大": "캐나다", "滑冰": "스케이트 타다", "滑雪": "스키 타다",
    "太阳": "태양", "羽毛": "깃털", "羽毛球": "배드민턴", "排球": "배구",
    "乒乓球": "탁구", "钓鱼": "낚시하다", "件": "벌·개(양사)", "游泳衣": "수영복",
    "几": "몇", "顶": "개(모자 양사)", "副": "벌(장갑 양사)", "耳环": "귀걸이",
    "已经": "이미·벌써", "项链": "목걸이", "万": "만(10,000)", "物理": "물리",
    "生物": "생물", "化学": "화학", "地理": "지리", "对…好": "~에게 잘하다·좋다",
    "对…感兴趣": "~에 관심이 있다", "觉得": "~라고 생각하다", "有用": "유용하다",
    "难": "어렵다", "容易": "쉽다", "写": "쓰다", "科目": "과목", "为什么": "왜",
    "意思": "뜻·의미", "有意思": "재미있다", "教": "가르치다", "功课": "숙제",
    "测验": "시험·테스트", "考试": "시험", "学期": "학기", "介绍": "소개하다",
    "幢": "채(건물 양사)", "教学": "교학·수업", "图书馆": "도서관", "礼堂": "강당",
    "操场": "운동장", "体育馆": "체육관", "篮球场": "농구장", "足球场": "축구장",
    "游泳池": "수영장", "停车场": "주차장", "铅笔": "연필", "钢笔": "만년필",
    "尺子": "자", "橡皮": "지우개", "白板": "화이트보드", "卷笔刀": "연필깎이",
    "练习本": "공책·연습장", "计算器": "계산기", "教室": "교실", "三层": "3층",
    "旁边": "옆·옆쪽", "实验": "실험", "实验室": "실험실", "隔壁": "옆집·이웃",
    "男": "남자", "厕所": "화장실", "左边": "왼쪽", "右边": "오른쪽",
}


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
            kr = m.group(3).strip()
            records.append({
                "id": len(records) + 1,
                "hanzi": hanzi,
                "pinyin": clean(m.group(2)),
                "meaning": MEANING.get(hanzi) or kr,
                "kr": kr,
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
                "meaning": row["meaning"] or MEANING.get(hanzi) or row["kr"],
                "kr": row["kr"],
                "cn_sentence": row["cn_sentence"],
                "cn_pinyin": row["cn_pinyin"],
                "theme": row["theme"] or WORD2THEME.get(hanzi, "other"),
            })

    # sanity: core fields populated (example sentence is optional for extras)
    bad = [r for r in records if not all(r[k] for k in ("hanzi", "kr", "meaning"))]
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
