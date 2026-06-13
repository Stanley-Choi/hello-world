# 한솔이의 중국어 📚 · Hansol's Chinese study app

A small, friendly web app to help **Hansol** study the Chinese vocabulary from
her two June worksheets — **196 words** with pinyin, Korean prompt sentences,
and Chinese example sentences, grouped into themes (family, clothing, body,
weather, health, school subjects, sports, directions, and more).

It runs in any browser, on a phone or computer, and works **online or offline**.

## 🌏 Use it online (anywhere)

Once GitHub Pages is enabled, the app is live at:

**https://stanley-choi.github.io/hello-world/**

One-time setup (repo owner, ~10 seconds): **Settings → Pages → Build and
deployment → Source: _GitHub Actions_**. After the PR is merged to `master`,
it deploys automatically and updates on every push.

## 💻 Use it offline

Download `index.html` and `vocab.js` into the same folder and open
`index.html` — no internet, no install needed.

## How to use it

- **플래시카드 (Flashcards)** — see a prompt, tap to flip, then tap **✓ 맞았어**
  or **✗ 틀렸어**. The back shows the word, pinyin, and the full example
  sentence so she sees it in context.
- **퀴즈 (Quiz)** — 4 multiple-choice options (wrong choices come from the same
  theme, so they're a real test). Score is tracked.
- **복습 (Mistakes)** — every word she gets wrong is collected here to redo
  until it sticks.
- **단어추가 (Add)** — add her own new words anytime; they join the decks.

**Direction toggle** lets her practice both ways: 한국어 → 中 (produce the
Chinese) and 中 → 한국어 (recognize the meaning). **병음** hides/shows pinyin so
she can test real recall. **틀린 단어 섞기** mixes previously-missed words back
into new study sessions automatically.

Progress and added words are saved in the browser. Use **내보내기 / 불러오기**
(export / import) at the bottom to move them between devices.

## For maintainers

The word list lives in `vocab.js`, generated from the original worksheets:

```bash
python3 tools/build_vocab.py   # reads data/worksheet{1,2}.docx → writes vocab.js
```

- `index.html` — the whole app (HTML + CSS + JS, no dependencies, no build step)
- `vocab.js` — `window.VOCAB`, the cleaned/deduplicated/theme-tagged word list
- `data/` — the original worksheet `.docx` source files
- `tools/build_vocab.py` — regenerates `vocab.js` if the worksheets change
