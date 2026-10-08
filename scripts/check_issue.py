#!/usr/bin/env python3
"""号(issues/YYYY-MM-DD.md)の書き方と、定期実行のコミットが触ってよい場所だけを触ったかを点検する。

使い方:
  python3 scripts/check_issue.py issues/2026-10-13.md   1つの号を点検する
  python3 scripts/check_issue.py --all                  issues/ の号を全部点検する
  python3 scripts/check_issue.py --commits BEFORE AFTER BEFORE..AFTER のうち、題が「号:」で始まるコミットが
                                                        書いてよい場所の外を変えていないかを点検する

中身が正しいか(書いたことが本当か)は見ない。見るのは、いつの情報か・どこから取ったか・どこまで読んだかが
書いてあるかだけ。無人の実行で、確かめていないことを確かめたように書くのを、形の上で防ぐため。
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECTIONS = [
    "## 1. 食い違い",
    "## 2. このやり方と逆向きの結果",
    "## 3. Claude Code の変更",
    "## 4. 新しい研究・発表",
    "## 5. 読み物(二次情報)",
    "## 6. あなた向けの1件",
    "## 7. 開けなかったもの",
    "## 8. 実行の記録",
]
# 項目に日付・出どころ・読んだ範囲を求める節(1〜6)と、項目の数の上限
ITEM_SECTIONS = SECTIONS[:6]
MAX_ITEMS = {SECTIONS[0]: 5, SECTIONS[4]: 3, SECTIONS[5]: 1}
# 新しい順に並んでいるかを見る節
ORDERED = {SECTIONS[2], SECTIONS[3], SECTIONS[4]}

DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
SOURCE = re.compile(r"出どころ:\s*https?://\S+")
READ = re.compile(r"読んだ範囲:\s*(本文|要旨|要約|二次情報)")
NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")

# 定期実行(題が「号:」のコミット)が変えてよい場所
ALLOWED = ("issues/", "topics/", "backlog.md", "sources.md")


def split_sections(text):
    parts, current = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line.strip()
            parts[current] = []
        elif current:
            parts[current].append(line)
    return parts


def items(lines):
    """行頭が「- 」の項目(字下げした補足は前の項目に含める)を返す"""
    out = []
    for line in lines:
        if line.startswith("- "):
            out.append(line)
        elif line.startswith("  ") and out:
            out[-1] += "\n" + line
    return out


def check_issue(path):
    errors = []
    name = os.path.basename(path)
    m = NAME.match(name)
    if not m:
        return [f"{name}: ファイル名が YYYY-MM-DD.md ではありません"]
    text = open(path, encoding="utf-8").read()
    if not text.startswith(f"# 号 {m.group(1)}"):
        errors.append(f"1行目が「# 号 {m.group(1)}」ではありません")
    if not re.search(r"^- 種類: (定期|試し)$", text, re.M):
        errors.append("「- 種類: 定期」か「- 種類: 試し」の行がありません")
    if not re.search(r"^- 期間: \d{4}-\d{2}-\d{2} 〜 \d{4}-\d{2}-\d{2}$", text, re.M):
        errors.append("「- 期間: YYYY-MM-DD 〜 YYYY-MM-DD」の行がありません")

    parts = split_sections(text)
    found = [h for h in parts if h in SECTIONS]
    if found != SECTIONS:
        errors.append("節の見出しが型(templates/issue.md)と同じ順に揃っていません")

    for head in SECTIONS:
        its = items(parts.get(head, []))
        if not its:
            errors.append(f"{head}: 項目がありません(なければ「- なし」と書く)")
            continue
        if len(its) == 1 and its[0].strip() == "- なし":
            continue
        if head in MAX_ITEMS and len(its) > MAX_ITEMS[head]:
            errors.append(f"{head}: 項目が {len(its)} 件あります(上限 {MAX_ITEMS[head]} 件)")
        if head in ITEM_SECTIONS:
            for it in its:
                first = it.splitlines()[0][:60]
                if not DATE.search(it):
                    errors.append(f"{head}: 日付(YYYY-MM-DD)がない項目: {first}")
                if not SOURCE.search(it):
                    errors.append(f"{head}: 「出どころ: URL」がない項目: {first}")
                if not READ.search(it):
                    errors.append(f"{head}: 「読んだ範囲: 本文/要旨/要約/二次情報」がない項目: {first}")
        if head == SECTIONS[6]:
            for it in its:
                if not re.search(r"https?://", it):
                    errors.append(f"{head}: URL がない項目: {it.splitlines()[0][:60]}")
        if head in ORDERED:
            dates = [DATE.search(it).group(0) for it in its if DATE.search(it)]
            if dates != sorted(dates, reverse=True):
                errors.append(f"{head}: 新しい順に並んでいません")
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
