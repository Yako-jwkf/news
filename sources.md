# 見に行く先

要約: 定期実行が毎回見に行くサイトと、何を取るか。「前回届いたか」の欄だけは定期実行が書き換える。それ以外を変えるときは、会話の中で一緒に直す。

決まり:
- 一次情報(公式の文書・変更履歴・論文の本文や要旨)を先に読む。二次情報(記事・論評・議論)は「読み物」と道案内にだけ使う。
- 届かなかったら、その号の「7. 開けなかったもの」に書き、下の表の「前回届いたか」を更新する。
- ページや PDF を丸ごと写さない。短い引用と URL と取得日だけ。

## 1. Claude Code の変更 → 号の3、topics/claude-code-changes.md、照合

| サイト | URL | 取るもの | 前回届いたか |
|---|---|---|---|
| 変更履歴 | https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md | 期間内の版の変更点。下の分野に関わる行だけ | 2026-10-08 届いた |
| npm の登録情報 | https://registry.npmjs.org/@anthropic-ai/claude-code | `time` の欄の各版の公開日。変更履歴には日付がないので、期間をここで区切る | 2026-10-08 届いた |
| 公式ドキュメント | https://code.claude.com/docs/llms.txt(一覧)、各ページは `https://code.claude.com/docs/en/<名前>.md` | 変更履歴に出た分野のページの本文。test の `docs/knowledge/claude-code-config-spec.md` と照らす | 2026-10-08 届いた |

分野: フック(hooks)、権限(permissions)、設定(settings)、スキル(skills)、サブエージェント(sub-agents)、サンドボックス(sandboxing)、クラウド(cloud-environments・claude-code-on-the-web)、定期実行(routines)、CLAUDE.md(memory)。

## 2. Anthropic の発表・モデル → 号の4、topics/intelligence.md

| サイト | URL | 取るもの | 前回届いたか |
|---|---|---|---|
| 発表 | https://www.anthropic.com/news | 期間内の記事の題と日付。関係するものは本文 | 2026-10-08 届いた |
| 研究 | https://www.anthropic.com/research | 同上 | 2026-10-08 届いた |
| 技術記事 | https://www.anthropic.com/engineering | 同上 | 2026-10-08 届いた |
| Claude の記事 | https://claude.com/blog(https://claude.com/resources/articles に移る) | 使い方・設計の方針の記事 | 2026-10-08 届いた |
| API のリリースノート | https://platform.claude.com/docs/en/release-notes/overview | 新しいモデル・機能が出た日 | 2026-10-08 届いた |
| システムカード | 発表の記事からリンクされる PDF(www-cdn.anthropic.com) | 新しいモデルが出たときに、弱点・問題の行動の節 | 2026-10-08 届いた(Sonnet 5.5・Haiku 5.5・Opus 5.5) |

## 3. 研究 → 号の2・4、topics/agent-config-research.md・topics/intelligence.md、照合

| サイト | URL | 取るもの | 前回届いたか |
|---|---|---|---|
| arXiv の検索 | https://export.arxiv.org/api/query | 期間内の論文の要旨(下の3つの主題)。要旨は合わせて100件まで、本文を読むのは5本まで | 2026-10-08 届いた |
| arXiv の番号指定 | https://export.arxiv.org/api/query?id_list=<番号,番号> | topics と test が引いている論文の版と更新日。新しい版が出ていれば要旨を読み直す | 2026-10-08 届いた |
| METR | https://metr.org/blog/ | 新しいモデルの評価 | 2026-10-08 届いた |

arXiv の主題(検索は `submittedDate:[開始 TO 終了]` で期間を区切る。広い語だけだと関係のない分野が混ざる。2026-10-08 に4語で2週間207件):
1. エージェントの指示ファイル・スキル・フック・権限: `abs:"AGENTS.md"`、`abs:"CLAUDE.md"`、`abs:"agent skills"`、`abs:"coding agent"` と `instruction`・`guardrail`・`permission`・`hook` の組み合わせ
2. AI の弱点: `sycophancy`(相手に合わせすぎる)、`calibration`(自信の見積もり)、`hallucination`(作り話)、`introspection`(自分の内側を報告する力)、`self-verification`(自分の点検)。今の世代のモデルで試したものを先に
3. AI の評価の仕方: `agent evaluation`、`benchmark`、`time horizon`

## 4. 読み物(二次情報) → 号の5・6

| サイト | URL | 取るもの | 前回届いたか |
|---|---|---|---|
| Hacker News | https://hn.algolia.com/api/v1/search_by_date?query=<語>&tags=story&numericFilters=points>=100,created_at_i><開始の秒> | Claude Code・CLAUDE.md・AI エージェントの話で票の多いもの。作り手のやり方(照合の B)の手がかり | 2026-10-08 届いた |
| Latent Space | https://www.latent.space/feed | AI を使ったものづくりの記事・対談 | 2026-10-08 届いた |
| MIT Technology Review | https://www.technologyreview.com/feed/ | AI のニュース | 2026-10-08 届いた |
| Ars Technica | https://arstechnica.com/ai/feed/ | AI の欄の記事(トップのページはサイト側が 403 を返した) | 2026-10-08 届いた(配信のみ) |
| Gwern.net | https://gwern.net/changelog | 月ごとの更新。AI・知能の論考 | 2026-10-08 届いた |
| Astral Codex Ten | https://www.astralcodexten.com/feed | 合理性・心理・AI の予測の論考 | 2026-10-08 届いた |
| Aeon | https://aeon.co/ | 哲学・心理・科学の随筆 | 2026-10-08 届いた |

## 5. 道案内だけ(号には「二次情報」と書き、根拠にしない)

| サイト | URL | 前回届いたか |
|---|---|---|
| Zvi Mowshowitz | https://thezvi.substack.com/ | 2026-10-08 届いた |
| LessWrong | https://www.lesswrong.com/ | 2026-10-08 届いた |

## 使わないもの(理由)
- The Information: 有料の記事が中心で題しか読めない見込み(記憶。未確認)。
- 公式の週ごとのまとめ(code.claude.com の whats-new): 第37週(2026-09-07〜11)が最後で、第38〜41週は 404(2026-10-08)。
- ARC Prize の順位表: 届くが、文面にモデル名がほぼ出ない(画面で組み立てる作りと推測)。
- Hugging Face の論文の人気一覧: arXiv と重なり、人気は関係の深さと別。
- deepmind.google・openai.com・simonwillison.net: 2026-10-08 に届かなかった(ネットワーク設定)。
- GitHub のリリースのページ: 403(2026-10-08)。変更履歴のファイルで足りる。
