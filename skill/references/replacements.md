# 詞彙替換規則

`apply_vocab.py` 讀本檔做機械式替換。**只動 SRT 的文字行，時間碼與段號絕不更動。**

## 怎麼改這份檔案

- 表格由上到下依序執行，**順序有意義**（見各節註解）
- 詞彙前後的空白會被去掉；用 `` ` `` 包起來可以保留原樣
- 詞彙裡若有 `|`，寫成 `\|`
- 加規則前先讀下面〈中文規則的陷阱〉

**不想動到技能本體**（升級會被覆蓋）的話，把自己的規則放 `~/.audio-to-srt/replacements.md`，
格式相同，會**先於**本檔執行，可覆蓋內建行為。要暫時停用加 `--no-user-rules`。

## 中文規則的陷阱

英文規則有**詞邊界**自動保護：規則頭尾是英數字時，會要求前後不是英數字，
所以 `Cloud` → `Claude` 不會把 `iCloud` 改成 `iClaude`。

**中文沒有詞邊界可言**，所以中文規則沒有這層保護。凡是可能出現在正常語句裡的中文字串
一律不要寫進來——寫「三十八 → 某個名字」會把「第三十八頁」「三十八度」一起改掉。
那類需要看語境才知道對錯的修正，交給清字階段由 Claude 判斷，這本來就是流程分兩階段的用意。

## 保護詞

替換開始前先遮蔽、全部跑完再還原。用來保住「含有待替換字串、但本身是正確詞」的詞——
詞邊界救得了 `iCloud`，救不了 `Google Cloud`（前後都是空白，邊界檢查會放行）。

比對區分大小寫，長的優先遮蔽。

- `Google Cloud`
- `Cloud Functions`
- `Cloud Storage`
- `cloud storage`
- `Cloud Native`
- `cloud native`
- `Cloud Shell`
- `Cloud Run`
- `iCloud`
- `SoundCloud`
- `Cloudflare`
- `CloudFlare`
- `CloudKit`
- `Netflix`

## 替換規則

「邊界」欄留空 = 自動加詞邊界（預設）；填「否」= 關掉，用來匹配詞中片段。

### GPT-Codex 變體

必須**最先**處理，否則 `Cloud` → `Claude` 跑完就分不出哪些原本是 Codex。

| 聽成 | 正確 | 邊界 |
|------|------|------|
| `GPT-ClaudeX` | `GPT-Codex` | |
| `GPT ClaudeX` | `GPT Codex` | |
| `GPT-CloudX` | `GPT-Codex` | |
| `GPT CloudX` | `GPT Codex` | |
| `GPT-Cloud X` | `GPT-Codex` | |
| `GPT Cloud X` | `GPT Codex` | |
| `ClaudeX` | `Codex` | |
| `CloudX` | `Codex` | |
| `Cloud X` | `Codex` | |
| `Claude X` | `Codex` | |
| `CodeX` | `Codex` | |
| `Code X` | `Codex` | |
| `DexDex` | `Codex` | |
| `Dex Dex` | `Codex` | |
| `dex dex` | `Codex` | |
| `Code x` | `Codex` | |
| `code x` | `Codex` | |
| `克勞德X` | `Codex` | |
| `克勞X` | `Codex` | |

### Antigravity（Google 的 AI IDE）

| 聽成 | 正確 | 邊界 |
|------|------|------|
| `Anti-Gravity` | `Antigravity` | |
| `Anti Gravity` | `Antigravity` | |
| `AntiGravity` | `Antigravity` | |
| `Antiquity` | `Antigravity` | |
| `Antiguity` | `Antigravity` | |
| `Antiqueity` | `Antigravity` | |
| `anti-gravity` | `Antigravity` | |
| `Antigrate ID` | `Antigravity IDE` | |
| `AntiGraphy2` | `Antigravity 2` | |
| `AntiGraphy 2` | `Antigravity 2` | |
| `AntiGraphy` | `Antigravity` | |
| `Antigrate` | `Antigravity` | |
| `Antigrity` | `Antigravity` | |
| `Antigua提` | `Antigravity 提` | |
| `安定iquity` | `Antigravity` | |

### 部署與開發工具

| 聽成 | 正確 | 邊界 |
|------|------|------|
| `Netify` | `Netlify` | |
| `Netfly` | `Netlify` | |
| `Netfile` | `Netlify` | |
| `NetFi` | `Netlify` | |
| `Pellet` | `Padlet` | |
| `Pell et` | `Padlet` | |
| `Paylet` | `Padlet` | |
| `Google She et` | `Google Sheet` | |
| `Google Shirt` | `Google Sheet` | |
| `Google size` | `Google Sites` | |
| `Cla.S.P` | `clasp` | |
| `Cla.S` | `clasp` | |
| `DLSP` | `clasp` | |
| `CLSP` | `clasp` | |
| `Clasp` | `clasp` | |
| `App ScriptAppSquid` | `Apps Script` | |
| `AppSquid` | `Apps Script` | |
| `Appsquiz` | `Apps Script` | |
| `Assess Token` | `Access Token` | |
| `aging setting` | `Agent Settings` | |
| `Aging Settings` | `Agent Settings` | |
| `Agin Setting` | `Agent Settings` | |
| `Agen setting` | `Agent Settings` | |
| `bookLM的MCP` | `bookLM 的 MCP` | 否 |

最後一條關掉邊界，是為了匹配 `notebookLM的MCP` 這種詞中片段；
補完空格後由下面的 `notebookLM` → `NotebookLM` 接手。

### OpenCode

| 聽成 | 正確 | 邊界 |
|------|------|------|
| `OpenGo` | `OpenCode Go` | |
| `Open Go` | `OpenCode Go` | |
| `Sense4AI` | `生成式AI` | |
| `Sense 4 AI` | `生成式AI` | |

### Claude 生態

`Cloud` → `Claude` 放**最後**，否則會先把 `Cloud Code` 改掉，上面的複合詞規則就沒機會跑。

| 聽成 | 正確 | 邊界 |
|------|------|------|
| `ClockCode` | `Claude Code` | |
| `Clock Code` | `Claude Code` | |
| `Cloud Code` | `Claude Code` | |
| `cloud code` | `Claude Code` | |
| `CloudCode` | `Claude Code` | |
| `ClawCode` | `Claude Code` | |
| `claw code` | `Claude Code` | |
| `Claw code` | `Claude Code` | |
| `Cloud design` | `Claude Design` | |
| `cloud design` | `Claude Design` | |
| `Cloud Design` | `Claude Design` | |
| `克勞德` | `Claude` | |
| `克勞` | `Claude` | |
| `Cloud` | `Claude` | |
| `cloud` | `Claude` | |

### 其他 AI 工具

| 聽成 | 正確 | 邊界 |
|------|------|------|
| `Notebook AM` | `NotebookLM` | |
| `notebook AM` | `NotebookLM` | |
| `Notebook LM` | `NotebookLM` | |
| `notebook LM` | `NotebookLM` | |
| `NotebookAM` | `NotebookLM` | |
| `notebookLM` | `NotebookLM` | |
| `ImageR` | `Image 2` | |
| `Image R` | `Image 2` | |
| `GPT Image 2` | `GPT-Image 2` | |
| `GPT-Image2` | `GPT-Image 2` | |

### 常見錯字

只放**確定性**的一對一映射。需要看語境的（同音字、可能是正常語句的字串）不要寫這裡。

| 聽成 | 正確 | 邊界 |
|------|------|------|
| `斷考` | `段考` | |
| `Signard型` | `三角形` | |
| `Signard 型` | `三角形` | |
| `翻例` | `範例` | |
| `原始黑體` | `思源黑體` | |
| `烤卷` | `考卷` | |
| `用字按鈕` | `用一個按鈕` | |
| `五文字` | `無文字` | |
| `全然登地` | `飛天遁地` | |
| `飛天遁地啊` | `飛天遁地` | |
| `生成師` | `生成式` | |
| `進乎無限` | `近乎無限` | |
| `進乎` | `近乎` | |
| `生徒技能` | `生圖技能` | |
| `生徒` | `生圖` | |
| `第二大堂` | `第二大腦` | |
| `詹音` | `噪音` | |
| `栏位` | `欄位` | |
| `四傳表` | `試算表` | |
| `路板` | `陸版` | |
