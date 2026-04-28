---
name: md-to-docx
description: >
  Convert Markdown files to Word (.docx) format using pandoc. Use when the user
  asks to convert a markdown file to Word, docx, or document format, or wants to
  export markdown as a Word document.
allowed-tools:
  - Bash
  - Read
---

# md-to-docx — Markdown to Word Converter

Converts `.md` files to `.docx` using **pandoc**, which is available in the
environment at `/usr/bin/pandoc`.

---

## Quick Decision Tree

| Situation | Action |
|-----------|--------|
| Single file, default style | Basic conversion |
| Single file, custom style | Conversion with `--reference-doc` |
| Multiple files / batch | Loop conversion |
| File uploaded by user | Copy from `/mnt/user-data/uploads/` first |

---

## Step-by-step workflow

### 1. Locate the input file

- If the user uploaded a file, it's at `/mnt/user-data/uploads/<filename>.md`
- If the user specified a path, use it directly
- If unclear, ask the user for the file path or to upload the file

### 2. Set output path

- Default: same directory as the input, same name but `.docx` extension
- If the result should be available to the user, write to `/mnt/user-data/outputs/`

### 3. Run the conversion

**Basic (no custom style):**
```bash
pandoc input.md -o output.docx
```

**With a reference style template:**
```bash
pandoc input.md --reference-doc=template.docx -o output.docx
```

**Batch (convert all .md in a directory):**
```bash
for f in *.md; do
  pandoc "$f" -o "${f%.md}.docx"
done
```

### 4. Verify output

After conversion, confirm the file exists and is non-empty:
```bash
ls -lh output.docx
```

### 5. Present the file to the user

Use the `present_files` tool pointing to the output path so the user can
download the `.docx` file.

---

## Common options

| Option | Purpose |
|--------|---------|
| `--reference-doc=template.docx` | Apply custom styles from a Word template |
| `--toc` | Add a table of contents |
| `--toc-depth=N` | Depth of TOC headings (default: 3) |
| `-V geometry:margin=1in` | Set page margins |
| `--highlight-style=tango` | Syntax highlighting for code blocks |

---

## Edge cases

- **File not found**: Check the path carefully; uploads live at `/mnt/user-data/uploads/`
- **pandoc not found**: It's at `/usr/bin/pandoc`; use full path if needed
- **Images in markdown**: Relative image paths must be resolvable from the working directory — `cd` to the file's directory before running pandoc
- **Multiple files into one docx**: Concatenate with space-separated inputs:
  ```bash
  pandoc file1.md file2.md -o combined.docx
  ```

---

## Notes

- pandoc preserves headings, bold, italic, lists, tables, code blocks, and links
- The output style follows Word's default theme unless `--reference-doc` is provided
- For heavy formatting needs, consider the `docx` skill after conversion
