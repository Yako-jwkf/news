#!/usr/bin/env python3
"""号(issues/YYYY-MM-DD.md)の書き方と、定期実行のコミットが触ってよい場所だけを触ったかを点検する。

使い方:
  python3 scripts/check_issue.py issues/2026-10-13.md   1つの号を点検する
  python3 scripts/check_issue.py --all                  issues/ の号を全部点検する
  python3 scripts/check_issue.py --commits BEFORE AFTER BEFORE..AFTER のうち、題が「号:」で始まるコミットが
                                                        書いてよい場所の外を変えていないかを点検する

中身が正しいか(書いたことが本当か)は見ない。見るのは、読む人の順番に並んでいるか、各項目に
「一言で」「test への影響」があるか、いつの情報か・どこから取ったか・どこまで読んだかが書いてあるか。
号の形は templates/issue.md(2026-10-08 から、読む人の順番: あなた向けの1件 → この号で分かったこと →
食い違い → 逆向きの結果 → 読み物 → 記録)。
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECTIONS = ["## この号で分かったこと", "## 食い違い", "## 逆向きの結果", "## 読み物", "## 記録"]
RECORDS = ["### Claude Code の変更", "### 研究と発表", "### 開けなかったもの", "### 実行の記録"]

DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
SOURCE = re.compile(r"出どころ:\s*(\[[^\]]*\]\()?https?://")
READ = re.compile(r"読んだ範囲:\s*(本文|要旨|要約|二次情報)")
NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")
LEFTOVER = re.compile(r"YYYY-MM-DD|\(題\)|\(名前\)|\(一言で|\(一言の題\)|N件|2\.1\.xxx")

# 定期実行(題が「号:」のコミット)が変えてよい場所
ALLOWED = ("issues/", "topics/", "backlog.md", "sources.md")


def front_matter(text):
    """先頭の --- で囲んだプロパティを、(値の辞書, tags の一覧, 本文) にして返す"""
    if not text.startswith("---\n"):
        return None, [], text
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, [], text
    props, tags, key = {}, [], None
    for line in text[4:end].splitlines():
        m = re.match(r"^([^\s:][^:]*):\s*(.*)$", line)
        if m:
            key, val = m.group(1).strip(), m.group(2).strip()
            props[key] = val
        elif key == "tags" and re.match(r"^\s+-\s+", line):
            tags.append(re.sub(r"^\s+-\s+", "", line).strip())
    return props, tags, text[end + 5:]


def unquote(lines):
    """囲み枠の印(行頭の >)を外す。枠の見出し([!...])の行は落とす"""
    out = []
    for line in lines:
        if line.startswith(">"):
            line = re.sub(r"^>\s?", "", line)
            if line.startswith("[!"):
                continue
        out.append(line)
    return out


def split_by(lines, prefix):
    """prefix で始まる行ごとに分ける。{見出しの行: その下の行}"""
    parts, current = {}, None
    for line in lines:
        if line.startswith(prefix) and not line.startswith(prefix + "#"):
            current = line.strip()
            parts[current] = []
        elif current is not None:
            parts[current].append(line)
    return parts


def find(parts, head):
    for k in parts:
        if k.startswith(head):
            return k
    return None


def bullets(lines):
    """行頭が「- **」の項目(字下げした補足は前の項目に含める)"""
    out = []
    for line in lines:
        if line.startswith("- **"):
            out.append(line)
        elif line.startswith("  ") and out:
            out[-1] += "\n" + line
    return out


def is_none(lines):
    return any(l.strip() in ("なし", "- なし") for l in lines)


def need(errors, where, text, source=True, read=True, date=True):
    first = text.strip().splitlines()[0][:50] if text.strip() else "(空)"
    if date and not DATE.search(text):
        errors.append(f"{where}: 日付(YYYY-MM-DD)がない: {first}")
    if source and not SOURCE.search(text):
        errors.append(f"{where}: 「出どころ: URL」がない: {first}")
    if read and not READ.search(text):
        errors.append(f"{where}: 「読んだ範囲: 本文/要旨/要約/二次情報」がない: {first}")


def check_issue(path):
    errors = []
    name = os.path.basename(path)
    m = NAME.match(name)
    if not m:
        return [f"{name}: ファイル名が YYYY-MM-DD.md ではありません"]
    day = m.group(1)
    text = open(path, encoding="utf-8").read()
    props, tags, body = front_matter(text)

    # プロパティ
    if props is None:
        errors.append("先頭に --- で囲んだプロパティがありません(templates/issue.md)")
        props = {}
    kind = props.get("種類", "")
    if props.get("日付") != day:
        errors.append(f"プロパティの「日付」がファイル名の日付({day})と違います")
    if kind not in ("定期", "試し"):
        errors.append("プロパティの「種類」が「定期」か「試し」ではありません")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2} 〜 \d{4}-\d{2}-\d{2}", props.get("期間", "")):
        errors.append("プロパティの「期間」が「YYYY-MM-DD 〜 YYYY-MM-DD」ではありません")
    if not re.fullmatch(r"\d+", props.get("食い違いの数", "")):
        errors.append("プロパティの「食い違いの数」が数ではありません")
    for t in ("news/号", f"news/{kind}"):
        if t not in tags:
            errors.append(f"プロパティの tags に {t} がありません")

    # 全体
    lines = body.splitlines()
    first = next((l for l in lines if l.strip()), "")
    if not first.startswith(f"# 号 {day}"):
        errors.append(f"題の行が「# 号 {day}」で始まっていません")
    if "%%" in body or "<!--" in body:
        errors.append("号に書き方の案内(%% や <!-- -->)が残っています。案内は PROMPT.md にだけ書く")
    left = LEFTOVER.search(body)
    if left:
        errors.append(f"型の書きかけが残っています: {left.group(0)}")

    # あなた向けの1件(一番上、1つだけ)
    tips = [i for i, l in enumerate(lines) if l.startswith("> [!tip] あなた向けの1件")]
    learned = next((i for i, l in enumerate(lines) if l.startswith(SECTIONS[0])), len(lines))
    if len(tips) != 1:
        errors.append(f"「> [!tip] あなた向けの1件」の枠が {len(tips)} 個あります(1つにする)")
    elif tips[0] > learned:
        errors.append("「あなた向けの1件」が「この号で分かったこと」より下にあります(一番上に置く)")
    else:
        block = []
        for l in lines[tips[0]:]:
            if not l.startswith(">"):
                break
            block.append(l)
        need(errors, "あなた向けの1件", "\n".join(block))

    # 節の順
    parts = split_by(lines, "## ")
    heads = [h for h in parts if any(h.startswith(s) for s in SECTIONS)]
    if [next(s for s in SECTIONS if h.startswith(s)) for h in heads] != SECTIONS:
        errors.append("節の見出しが型と同じ順に揃っていません(" + " → ".join(s[3:] for s in SECTIONS) + ")")
        return [f"{name}: {e}" for e in errors]

    # この号で分かったこと
    sec = parts[find(parts, SECTIONS[0])]
    nums = [i for i, l in enumerate(sec) if re.match(r"^\d+\. ", l)]
    if not nums and not is_none(sec):
        errors.append("この号で分かったこと: 項目(「1. 」で始まる行)がありません(なければ「なし」)")
    for k, i in enumerate(nums):
        chunk = "\n".join(sec[i:nums[k + 1] if k + 1 < len(nums) else len(sec)])
        if "test への影響:" not in chunk:
            errors.append(f"この号で分かったこと: 「test への影響:」がない項目: {sec[i][:50]}")

    # 食い違い
    sec = parts[find(parts, SECTIONS[1])]
    items = split_by(sec, "### ")
    ids = [h for h in items if re.match(r"^### D\d+ ", h)]
    if len(ids) != len(items):
        errors.append("食い違い: 項目の見出しは「### D1 」の形にする")
    count = props.get("食い違いの数", "")
    if count.isdigit() and int(count) != len(ids):
        errors.append(f"食い違い: プロパティの「食い違いの数」({count})と項目の数({len(ids)})が違います")
    if len(ids) > 5:
        errors.append(f"食い違い: 項目が {len(ids)} 件あります(上限 5 件)")
    if not ids and not is_none(sec):
        errors.append("食い違い: 項目がありません(なければ「なし」)")
    for h in ids:
        chunk = "\n".join(items[h])
        for key in ("- 一言で:", "- test への影響:", "> [!note]- くわしく"):
            if key not in chunk:
                errors.append(f"食い違い {h[4:30]}: 「{key.lstrip('-> ')}」がありません")
        need(errors, f"食い違い {h[4:30]}", "\n".join(unquote(items[h])))

    # 逆向きの結果
    sec = parts[find(parts, SECTIONS[2])]
    items = split_by(sec, "### ")
    if not items and not is_none(sec):
        errors.append("逆向きの結果: 項目(「### 」の見出し)がありません(なければ「なし」)")
    for h, body_lines in items.items():
        chunk = "\n".join(body_lines)
        for key in ("- 一言で:", "- test への影響:"):
            if key not in chunk:
                errors.append(f"逆向きの結果 {h[4:30]}: 「{key[2:]}」がありません")
        need(errors, f"逆向きの結果 {h[4:30]}", "\n".join(unquote(body_lines)))

    # 読み物
    sec = parts[find(parts, SECTIONS[3])]
    its = bullets(sec)
    if not its and not is_none(sec):
        errors.append("読み物: 項目(「- **」で始まる行)がありません(なければ「なし」)")
    if len(its) > 3:
        errors.append(f"読み物: 項目が {len(its)} 件あります(上限 3 件)")
    for it in its:
        need(errors, "読み物", it)
        if "読んだ範囲: 二次情報" not in it:
            errors.append(f"読み物: 「読んだ範囲: 二次情報」と書いていない: {it.splitlines()[0][:50]}")
    dates = [DATE.search(it).group(0) for it in its if DATE.search(it)]
    if dates != sorted(dates, reverse=True):
        errors.append("読み物: 新しい順に並んでいません")

    # 記録
    rec = split_by(parts[find(parts, SECTIONS[4])], "### ")
    rheads = [h for h in rec if any(h.startswith(r) for r in RECORDS)]
    if [next(r for r in RECORDS if h.startswith(r)) for h in rheads] != RECORDS:
        errors.append("記録: 小見出しが型と同じ順に揃っていません(" + " → ".join(r[4:] for r in RECORDS) + ")")
    else:
        for r in RECORDS[:2]:
            sub = unquote(rec[find(rec, r)])
            its = bullets(sub)
            if not its and not is_none(sub):
                errors.append(f"記録 {r[4:]}: 項目がありません(なければ「なし」)")
            for it in its:
                need(errors, f"記録 {r[4:]}", it)
                if r == RECORDS[1] and "試したモデル:" not in it:
                    errors.append(f"記録 {r[4:]}: 「試したモデル:」がない: {it.splitlines()[0][:50]}")
            dates = [DATE.search(it).group(0) for it in its if DATE.search(it)]
            if dates != sorted(dates, reverse=True):
                errors.append(f"記録 {r[4:]}: 新しい順に並んでいません")
        sub = unquote(rec[find(rec, RECORDS[2])])
        its = bullets(sub)
        if not its and not is_none(sub):
            errors.append("記録 開けなかったもの: 項目がありません(なければ「なし」)")
        for it in its:
            if not re.search(r"https?://", it):
                errors.append(f"記録 開けなかったもの: URL がない: {it.splitlines()[0][:50]}")
        if "推敲" not in "\n".join(rec[find(rec, RECORDS[3])]):
            errors.append("記録 実行の記録: 推敲(/proofread)で直したところの行がありません")
    return [f"{name}: {e}" for e in errors]


def all_issues():
    folder = os.path.join(ROOT, "issues")
    return sorted(os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".md"))


def check_commits(before, after):
    zero = re.fullmatch(r"0+", before or "")
    rng = after if (not before or zero) else f"{before}..{after}"
    log = subprocess.run(["git", "log", "--format=%H%x09%s", rng], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    errors = []
    for line in log.splitlines():
        sha, subject = line.split("\t", 1)
        if not subject.startswith("号:"):
            continue
        files = subprocess.run(["git", "show", "--name-only", "--format=", sha], cwd=ROOT,
                               capture_output=True, text=True, check=True).stdout.split()
        for f in files:
            if not f.startswith(ALLOWED):
                errors.append(f"{sha[:7]}「{subject}」: 定期実行が変えてはいけない場所を変えています: {f}")
    return errors


def main(argv):
    if argv[:1] == ["--commits"] and len(argv) == 3:
        errors = check_commits(argv[1], argv[2])
    elif argv == ["--all"]:
        errors = [e for p in all_issues() for e in check_issue(p)]
    elif len(argv) == 1:
        errors = check_issue(argv[0])
    else:
        print(__doc__)
        return 2
    for e in errors:
        print(e)
    print("点検: 問題なし" if not errors else f"点検: 問題 {len(errors)} 件")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
