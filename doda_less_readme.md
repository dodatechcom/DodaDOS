# Doda Less (Markdown Pager)

Doda Less is a text-mode pager utility optimized for reading documentation. Rather than just dumping raw text to the screen, it acts as a lightweight Markdown parser, applying color-coding and bold attributes to headers, lists, bold tags (`**`), and inline code segments (` ` `).

## How to Use

Pass the filename you wish to read as an argument:
```bash
python doda_less.py README.md
```

## Shortcut Keys

| Key             | Action                  |
| --------------- | ----------------------- |
| **Arrow Keys**  | Scroll up and down line by line. |
| **PgUp / PgDn** | Scroll by full pages.   |
| **Q, ESC**      | Exit the pager.         |
