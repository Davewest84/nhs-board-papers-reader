# NHS Board Papers Analyser

Searches for, downloads, and analyses NHS trust board papers using the Claude AI API. Returns story leads structured for NHS specialist journalism.

---

## Quick start — Google Colab (recommended)

1. Open `Board_Papers_Analyser.ipynb` in [Google Colab](https://colab.research.google.com)
2. Get an Anthropic API key from [console.anthropic.com](https://console.anthropic.com)
3. Edit the configuration cell (Cell 2) with your API key and trust name
4. Run all cells in order

No installation required.

---

## What it does

1. **Searches** DuckDuckGo for the trust's board papers page
2. **Fetches** the index page and identifies PDF/ZIP download links
3. **Downloads** the most recent board pack using browser-mimicking headers and session cookies
4. **Extracts** text from the PDF using targeted passes (agenda first, then key sections)
5. **Analyses** the text with Claude, returning structured story leads with page references

---

## If the download fails

Some NHS trust websites block automated downloads even with browser headers. If this happens, the tool will say so clearly and ask you to upload the PDF manually. You can download it yourself from the trust's website and either:
- **In Colab**: upload via the file panel (left sidebar → Files icon)
- **CLI**: use the `--pdf` flag pointing to your downloaded file

---

## Approximate costs per run

| Pack size | Pages read | Approx. cost (Opus 4.6) | Approx. cost (Sonnet 4.6) |
|---|---|---|---|
| Small (50pp) | ~40pp | ~£0.50 | ~£0.10 |
| Medium (150pp) | ~80pp | ~£1.00 | ~£0.20 |
| Large (250pp) | ~120pp | ~£1.50 | ~£0.30 |

To use Sonnet instead of Opus, change `MODEL` in the configuration cell. Sonnet is faster and much cheaper; quality is slightly lower for complex editorial judgements.

---

## Known limitations

- **JS-rendered sites**: trusts using JavaScript to render download buttons (e.g. some Civica/Idox CMS sites) will block automated download — use manual upload
- **Login-gated papers**: some trusts require login to access papers — not supported
- **Scanned PDFs**: papers scanned as images rather than text-layer PDFs will extract no useful text
- **Zipped packs**: handled — the tool unpacks ZIPs and processes each PDF inside
- **Multiple individual papers**: the tool will attempt to download the first/most prominent link; you can override by pasting a direct URL

---

## CLI usage (developers)

```bash
pip install -r requirements.txt

# Basic usage
python board_papers.py "Sussex Community NHS Foundation Trust" --api-key sk-ant-...

# With known URL (skips search)
python board_papers.py "UCLH" --url https://www.uclh.nhs.uk/.../board-meetings --api-key sk-ant-...

# With manually downloaded PDF
python board_papers.py "Norfolk and Waveney" --pdf ./norfolk_jan2026.pdf --api-key sk-ant-...

# Use environment variable for API key
export ANTHROPIC_API_KEY=sk-ant-...
python board_papers.py "Shrewsbury and Telford Hospital NHS Trust"
```

---

## Files

| File | Purpose |
|---|---|
| `Board_Papers_Analyser.ipynb` | Google Colab notebook — main user interface |
| `board_papers.py` | CLI Python script for developers |
| `prompt_template.txt` | Analysis prompt sent to Claude — edit to adjust output |
| `requirements.txt` | Python dependencies |

---

## Adjusting the analysis

The `prompt_template.txt` file controls what Claude looks for and how it frames the output. Edit it to:
- Adjust story strength thresholds
- Add organisation-specific context
- Change output format (e.g. longer summaries vs shorter bullets)
- Focus on specific story categories

Use `{{TRUST_NAME}}`, `{{BOARD_PAPERS_URL}}` and `{{EXTRACTED_TEXT}}` as placeholders — they are replaced at runtime.
