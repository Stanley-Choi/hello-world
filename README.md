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

## 🦎 Science: Animal Parts and Their Functions

A second, separate study app for Hansol's **Grade 4 Science, Unit 1** project
("Create a New Animal for Its Habitat"). Built for a phone, in English only:

**https://stanley-choi.github.io/hello-world/science/**

Five tabs along the bottom:

- **Words** — 67 words from the unit, each with IPA pronunciation, a plain
  definition, an example sentence, and a tap-to-hear button. 42 of them carry a
  memory hook built from a familiar word (*adaptation* ← adapter, *humid* ←
  humidifier). Filter by group; tick off the ones she knows.
- **Quiz** — read the definition, see the example sentence with the word blanked
  out, and type it. A wrong answer reveals the shape of the word (`_ _ _ _`) for
  a second try; missed words come back at the end.
- **Ideas** — the two ideas the unit is built on, plus the teeth and beak shapes.
- **Habitat** — the five habitats from the project sheet. Each one lists the
  problems of living there next to body parts that solve them.
- **Project** — the reading order through the textbook, fill-in-the-blank
  sentence frames for the report, and a checklist drawn from the marking rubric.

Read-aloud uses the browser's built-in speech engine, so there is nothing to
install and no network call. On iOS, **Share → Add to Home Screen** makes it
open like an app.

## 📢 한성대 신문사 50주년 기념식 일정 공지

A one-page schedule notice for the Hansung University newspaper's 50th
anniversary ceremony (2026-10-31, university gymnasium):

**https://stanley-choi.github.io/hello-world/hansung/**

- `hansung/index.html` — the notice page (D-day counter, progress timeline,
  copy-to-clipboard button for KakaoTalk, add-to-calendar `.ics`)
- `hansung/notice.md` — the same notice as plain text, ready to paste

## 💻 Use it offline

Download `index.html` and `vocab.js` into the same folder and open
`index.html` — no internet, no install needed.

## How to use it

- **플래시카드 (Flashcards)** — see a prompt, tap to flip, then tap **✓ 맞았어**
  or **✗ 틀렸어**. The back shows the word, pinyin, and the full example
  sentence so she sees it in context.
- **퀴즈 (Quiz)** — 4 multiple-choice options on the **word** (wrong choices
  come from the same theme, so they're a real test). Score is tracked.
- **문장연습 (Sentence)** — see a sentence, pick the matching sentence in the
  other language (follows the 한↔中 direction toggle).
- **문장채우기 (Fill-in)** — the example sentence with the target word blanked;
  pick the right word from options (cloze, by meaning unit not characters).
- **복습 (Mistakes)** — every word she gets wrong (in any mode) is collected here
  to redo until it sticks.
- **단어추가 (Add)** — add her own new words anytime; they join the decks.

**Direction toggle** lets her practice both ways: 한국어 → 中 (produce the
Chinese) and 中 → 한국어 (recognize the meaning). **병음** hides/shows pinyin so
she can test real recall. **틀린 단어 섞기** mixes previously-missed words back
into new study sessions automatically.

Progress and added words are saved in the browser. Use **내보내기 / 불러오기**
(export / import) at the bottom to move them between devices.

## Adding new words (the usual way) 📸

When Hansol has a new worksheet, **send the photo or document to Claude** (in a
Claude Code session on this repo). Claude transcribes the words — hanzi, pinyin,
Korean meaning/sentence, Chinese example — into `data/extra/<name>.tsv`,
regenerates `vocab.js`, and pushes. The app picks them up automatically on its
next deploy. This is more accurate than in-browser OCR, especially for tones,
handwriting, and the Korean lines.

The in-app **단어추가 (Add)** tab is still there for the occasional one-off word.

### `data/extra/*.tsv` format

One tab-separated word per line (see `data/extra/template.tsv`). Only **hanzi**
and **kr** are required; the example sentence is optional, and `theme` is
auto-guessed if left blank:

```
hanzi <TAB> pinyin <TAB> kr <TAB> cn_sentence <TAB> cn_pinyin <TAB> theme
```

## For maintainers

The word list lives in `vocab.js`, generated from the worksheets plus any extras:

```bash
python3 tools/build_vocab.py   # data/worksheet{1,2}.docx + data/extra/*.tsv → vocab.js
```

- `index.html` — the whole app (HTML + CSS + JS, no dependencies, no build step)
- `vocab.js` — `window.VOCAB`, the cleaned/deduplicated/theme-tagged word list
- `data/` — the original worksheet `.docx` source files
- `data/extra/` — supplementary words transcribed from photos / new documents
- `tools/build_vocab.py` — regenerates `vocab.js` (deduplicates by hanzi)
