#!/usr/bin/env python3
"""
Generate a combined PDF of all dropshipping business deliverables.
Produces: Dropshipping_Business_Plan.pdf
"""

import os
import re
import textwrap
from pathlib import Path
from fpdf import FPDF

BASE = Path(__file__).parent


class BusinessPDF(FPDF):
    """Custom PDF with header/footer and markdown-aware rendering."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=20)
        self._current_section = ""

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, self._current_section, align="L")
        self.cell(0, 8, "Dropshipping E-Commerce Business Kit", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def add_cover_page(self):
        self.add_page()
        self.ln(60)
        self.set_font("Helvetica", "B", 32)
        self.set_text_color(26, 26, 46)
        self.cell(0, 16, "Dropshipping E-Commerce", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 16, "Business Plan", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(8)
        self.set_draw_color(233, 69, 96)
        self.set_line_width(0.8)
        self.line(60, self.get_y(), 150, self.get_y())
        self.ln(12)
        self.set_font("Helvetica", "", 14)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Complete Business Kit: Strategy, Tools & Store Scaffold", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(30)
        self.set_font("Helvetica", "", 12)
        self.set_text_color(60, 60, 60)
        details = [
            "Prepared: April 2026",
            "Budget: $2,000 - $5,000",
            "Platform: Shopify",
            "Model: Dropshipping via vetted suppliers",
        ]
        for d in details:
            self.cell(0, 8, d, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(20)
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, "CONFIDENTIAL", align="C", new_x="LMARGIN", new_y="NEXT")

    def add_toc(self, sections: list[tuple[str, int]]):
        self.add_page()
        self._current_section = "Table of Contents"
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(26, 26, 46)
        self.cell(0, 12, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
        self.ln(6)
        self.set_draw_color(233, 69, 96)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(8)

        for title, page in sections:
            self.set_font("Helvetica", "", 11)
            self.set_text_color(40, 40, 40)
            dots = "." * max(1, 70 - len(title))
            self.cell(0, 7, f"{title}  {dots}  {page}", new_x="LMARGIN", new_y="NEXT")

    def add_section_divider(self, title: str):
        self.add_page()
        self._current_section = title
        self.ln(40)
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(26, 26, 46)
        self.multi_cell(0, 14, title, align="C")
        self.ln(6)
        self.set_draw_color(233, 69, 96)
        self.set_line_width(0.6)
        mid = 105
        self.line(mid - 30, self.get_y(), mid + 30, self.get_y())

    def render_markdown(self, text: str, section_name: str = ""):
        if section_name:
            self._current_section = section_name
        self.add_page()

        lines = text.split("\n")
        in_code_block = False
        in_table = False
        table_rows: list[list[str]] = []
        table_col_count = 0

        i = 0
        while i < len(lines):
            line = lines[i]

            # Code blocks
            if line.strip().startswith("```"):
                if in_code_block:
                    in_code_block = False
                    self.ln(2)
                    i += 1
                    continue
                else:
                    in_code_block = True
                    i += 1
                    continue

            if in_code_block:
                self._render_code_line(line)
                i += 1
                continue

            # Table detection
            if "|" in line and line.strip().startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                # Skip separator rows
                if all(re.match(r'^[-:]+$', c) for c in cells):
                    i += 1
                    continue

                if not in_table:
                    in_table = True
                    table_rows = []
                    table_col_count = len(cells)

                table_rows.append(cells)
                # Check if next line is still a table
                if i + 1 >= len(lines) or "|" not in lines[i + 1]:
                    self._render_table(table_rows)
                    in_table = False
                    table_rows = []
                i += 1
                continue

            if in_table:
                self._render_table(table_rows)
                in_table = False
                table_rows = []

            stripped = line.strip()

            # Skip markdown metadata/frontmatter
            if stripped == "---":
                self.ln(4)
                i += 1
                continue

            # Headings
            if stripped.startswith("# "):
                self._render_h1(stripped[2:])
                i += 1
                continue
            if stripped.startswith("## "):
                self._render_h2(stripped[3:])
                i += 1
                continue
            if stripped.startswith("### "):
                self._render_h3(stripped[4:])
                i += 1
                continue

            # Empty line
            if not stripped:
                self.ln(3)
                i += 1
                continue

            # Checkbox items
            if stripped.startswith("- [ ] "):
                self._render_checkbox(stripped[6:])
                i += 1
                continue
            if stripped.startswith("- [x] "):
                self._render_checkbox(stripped[6:], checked=True)
                i += 1
                continue

            # Bullet items
            if stripped.startswith("- ") or stripped.startswith("* "):
                self._render_bullet(stripped[2:], indent=line.startswith("  "))
                i += 1
                continue

            # Numbered list
            num_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
            if num_match:
                self._render_numbered(num_match.group(1), num_match.group(2))
                i += 1
                continue

            # Regular paragraph
            self._render_paragraph(stripped)
            i += 1

        # Flush remaining table
        if in_table and table_rows:
            self._render_table(table_rows)

    def _clean_md(self, text: str) -> str:
        """Remove markdown formatting for plain text rendering."""
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # Replace unicode chars that might not be in the font
        text = text.replace("\u2014", "-").replace("\u2013", "-")
        text = text.replace("\u2018", "'").replace("\u2019", "'")
        text = text.replace("\u201c", '"').replace("\u201d", '"')
        text = text.replace("\u2026", "...")
        text = text.replace("\u2192", "->")
        text = text.replace("\u2193", "v")
        text = text.replace("\u2500", "-")
        text = text.replace("\u2550", "=")
        text = text.replace("\u2b50", "*")
        text = text.replace("\u2022", "-")
        text = text.replace("\u00a0", " ")
        # Remove emoji and other problematic unicode
        text = re.sub(r'[\U0001f300-\U0001f9ff]', '', text)
        text = re.sub(r'[\u2705\u2611\u2612\u2610]', '[v]', text)
        # Strip any remaining non-latin1 characters
        text = text.encode('latin-1', errors='replace').decode('latin-1')
        return text

    def _render_h1(self, text: str):
        self.ln(6)
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(26, 26, 46)
        self.multi_cell(0, 10, self._clean_md(text))
        self.set_draw_color(233, 69, 96)
        self.set_line_width(0.5)
        self.line(10, self.get_y() + 1, 80, self.get_y() + 1)
        self.ln(6)

    def _render_h2(self, text: str):
        if self.get_y() > 250:
            self.add_page()
        self.ln(6)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(26, 26, 46)
        self.multi_cell(0, 8, self._clean_md(text))
        self.ln(3)

    def _render_h3(self, text: str):
        if self.get_y() > 260:
            self.add_page()
        self.ln(4)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 7, self._clean_md(text))
        self.ln(2)

    def _render_paragraph(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        cleaned = self._clean_md(text)
        self.multi_cell(0, 5.5, cleaned)
        self.ln(1)

    def _render_bullet(self, text: str, indent: bool = False):
        x_offset = 18 if indent else 14
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        bullet_char = "-" if indent else "-"
        x = self.get_x()
        self.set_x(x_offset)
        cleaned = self._clean_md(text)
        # Use a simple dash if bullet char causes issues
        self.multi_cell(190 - x_offset, 5.5, f"  {bullet_char}  {cleaned}")
        self.ln(1)

    def _render_numbered(self, num: str, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        cleaned = self._clean_md(text)
        self.set_x(14)
        self.multi_cell(176, 5.5, f"  {num}.  {cleaned}")
        self.ln(1)

    def _render_checkbox(self, text: str, checked: bool = False):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        mark = "[x]" if checked else "[ ]"
        cleaned = self._clean_md(text)
        self.set_x(14)
        self.multi_cell(176, 5.5, f"  {mark}  {cleaned}")
        self.ln(1)

    def _render_code_line(self, line: str):
        self.set_font("Courier", "", 9)
        self.set_text_color(50, 50, 50)
        self.set_fill_color(245, 245, 245)
        cleaned = self._clean_md(line)
        self.cell(190, 5, f"  {cleaned}", fill=True, new_x="LMARGIN", new_y="NEXT")

    def _render_table(self, rows: list[list[str]]):
        if not rows:
            return

        if self.get_y() > 240:
            self.add_page()

        col_count = max(len(r) for r in rows)
        usable_width = 190

        # Calculate column widths based on content
        col_widths = []
        for col_idx in range(col_count):
            max_len = 0
            for row in rows:
                if col_idx < len(row):
                    max_len = max(max_len, len(self._clean_md(row[col_idx])))
            col_widths.append(max_len)

        total_chars = sum(col_widths) or 1
        col_widths_mm = [max(20, (w / total_chars) * usable_width) for w in col_widths]

        # Normalize to fit
        scale = usable_width / sum(col_widths_mm)
        col_widths_mm = [w * scale for w in col_widths_mm]

        for row_idx, row in enumerate(rows):
            if self.get_y() > 270:
                self.add_page()

            is_header = (row_idx == 0)
            if is_header:
                self.set_font("Helvetica", "B", 8.5)
                self.set_fill_color(26, 26, 46)
                self.set_text_color(255, 255, 255)
            else:
                self.set_font("Helvetica", "", 8.5)
                if row_idx % 2 == 0:
                    self.set_fill_color(245, 245, 250)
                else:
                    self.set_fill_color(255, 255, 255)
                self.set_text_color(40, 40, 40)

            max_lines = 1
            cell_texts = []
            for col_idx in range(col_count):
                cell_text = self._clean_md(row[col_idx]) if col_idx < len(row) else ""
                wrapped = textwrap.wrap(cell_text, width=int(col_widths_mm[col_idx] / 2.2)) or [""]
                cell_texts.append(wrapped)
                max_lines = max(max_lines, len(wrapped))

            row_height = max_lines * 5
            y_start = self.get_y()

            for col_idx in range(col_count):
                x = 10 + sum(col_widths_mm[:col_idx])
                self.set_xy(x, y_start)
                wrapped = cell_texts[col_idx]
                # Draw cell background
                self.rect(x, y_start, col_widths_mm[col_idx], row_height, "F")
                self.set_draw_color(200, 200, 200)
                self.rect(x, y_start, col_widths_mm[col_idx], row_height, "D")
                # Write text
                for line_idx, txt_line in enumerate(wrapped):
                    self.set_xy(x + 1.5, y_start + line_idx * 5 + 0.5)
                    self.cell(col_widths_mm[col_idx] - 3, 4.5, txt_line)

            self.set_y(y_start + row_height)

        self.ln(4)


def read_file(path: str) -> str:
    with open(BASE / path, "r") as f:
        return f.read()


def main():
    pdf = BusinessPDF()
    pdf.alias_nb_pages()

    # ---- Cover page ----
    pdf.add_cover_page()

    # We'll track page numbers for the TOC after rendering,
    # but since fpdf2 doesn't support post-insert easily,
    # we'll add the TOC as page 2 then render sections.

    sections_content = [
        ("Part 1: Business Plan", "business-plan/BUSINESS_PLAN.md"),
        ("Part 2: Financial Model", "business-plan/financial-model.md"),
        ("Part 3: App Setup Guide", "store/APP_SETUP_GUIDE.md"),
        ("Part 4: Launch Checklist", "store/LAUNCH_CHECKLIST.md"),
    ]

    # Add a TOC placeholder
    toc_page = pdf.page_no() + 1
    pdf.add_page()
    pdf._current_section = "Table of Contents"
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(0, 12, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_draw_color(233, 69, 96)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 80, pdf.get_y())
    pdf.ln(8)

    toc_items = [
        "Part 1: Business Plan",
        "    1. Executive Summary",
        "    2. Niche Selection Framework",
        "    3. Market Research",
        "    4. Supplier Strategy",
        "    5. Revenue Model & Financial Projections",
        "    6. Marketing Strategy",
        "    7. Operations Plan",
        "    8. Tech Stack",
        "    9. 90-Day Launch Timeline",
        "    10. Risk Assessment",
        "    11. Budget Allocation",
        "Part 2: Financial Model",
        "    Assumptions & Unit Economics",
        "    3-Scenario P&L (Pessimistic / Realistic / Optimistic)",
        "    Sensitivity Analysis & Cash Flow",
        "    Scaling Milestones & Tax Considerations",
        "Part 3: App Setup Guide",
        "    DSers, Judge.me, Klaviyo, Vitals, Google Shopping",
        "Part 4: Launch Checklist",
        "    Legal, Store Config, Products, Marketing, Launch Day",
        "Appendix: Tool Documentation",
        "    Niche Scorer, Product Finder, Competitor Analyzer",
        "    Pricing Calculator, Bulk Calculator",
    ]

    for item in toc_items:
        if item.startswith("    "):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 6.5, f"       {item.strip()}", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(26, 26, 46)
            pdf.ln(3)
            pdf.cell(0, 7, item, new_x="LMARGIN", new_y="NEXT")

    # ---- Render each section ----
    for title, filepath in sections_content:
        pdf.add_section_divider(title)
        content = read_file(filepath)
        # Skip the first H1 since we have a divider
        lines = content.split("\n")
        if lines and lines[0].startswith("# "):
            # Keep subtitle lines
            skip = 1
            while skip < len(lines) and lines[skip].strip().startswith("**"):
                skip += 1
            content = "\n".join(lines[skip:])
        pdf.render_markdown(content, title)

    # ---- Appendix: Tool documentation ----
    pdf.add_section_divider("Appendix: Tool Documentation")
    pdf.add_page()
    pdf._current_section = "Appendix: Tool Documentation"

    pdf._render_h1("Niche Scorer (niche_scorer.py)")
    appendix_text = """Evaluates dropshipping niches across five weighted dimensions and produces a composite 1-100 score.

Dimensions:
- Demand Trajectory (25%) - Google Trends 12-month interest slope
- Competition Density (20%) - Estimated number of competing stores
- Margin Potential (25%) - Markup ratio from supplier cost to retail price
- Shipping Feasibility (15%) - Weight, fragility, US warehouse availability
- Social Virality (15%) - Hashtag popularity on TikTok and Instagram

Usage:
  python niche_scorer.py                          # Score 5 default niches
  python niche_scorer.py -n "smart home" "pets"   # Custom niches
  python niche_scorer.py --offline                # Heuristic-only (no API)
  python niche_scorer.py --json                   # JSON output"""
    for line in appendix_text.split("\n"):
        pdf._render_paragraph(line)

    pdf.ln(4)
    pdf._render_h1("Product Finder (product_finder.py)")
    appendix_text2 = """Searches supplier catalogs and filters products by dropshipping viability criteria.

Filters applied:
- Minimum markup multiplier (default 3x)
- Maximum product cost (default $50)
- Minimum seller rating (default 4.5 stars)
- Minimum order count (default 100)
- Shipping method (rejects China Post-only)

Usage:
  python product_finder.py "massage gun"
  python product_finder.py "led lights" --min-markup 4 --max-cost 10
  python product_finder.py "pet bowl" --export results.csv"""
    for line in appendix_text2.split("\n"):
        pdf._render_paragraph(line)

    pdf.ln(4)
    pdf._render_h1("Competitor Analyzer (competitor_analyzer.py)")
    appendix_text3 = """Analyzes any Shopify store URL and extracts competitive intelligence.

Data extracted:
- Product count and price ranges
- Installed Shopify apps (via HTML signature detection)
- Theme identification
- Feature checklist (reviews, upsells, email popup, live chat, shipping bar)
- Social media presence
- Competitive assessment (strengths, weaknesses, opportunities)

Usage:
  python competitor_analyzer.py https://competitor-store.com
  python competitor_analyzer.py https://example.com --json"""
    for line in appendix_text3.split("\n"):
        pdf._render_paragraph(line)

    pdf.ln(4)
    pdf._render_h1("Pricing Calculator (calculator.py)")
    appendix_text4 = """Calculates recommended retail price, per-order economics, and models three scenarios.

Inputs: product cost, shipping cost, target CPA, target net margin, refund rate.
Outputs: recommended price, markup, ROAS, gross/net profit, break-even orders, scenario modeling.

Usage:
  python calculator.py                                    # Interactive mode
  python calculator.py --cost 8 --ship 3 --cpa 10 --margin 30
  python calculator.py --cost 8 --ship 3 --json"""
    for line in appendix_text4.split("\n"):
        pdf._render_paragraph(line)

    pdf.ln(4)
    pdf._render_h1("Bulk Calculator (bulk_calculator.py)")
    appendix_text5 = """Batch-prices a CSV of products and outputs a ranked, priced catalog.

Input CSV columns: name, cost, shipping (optional: target_cpa, target_margin)

Usage:
  python bulk_calculator.py --generate-sample             # Create sample CSV
  python bulk_calculator.py products.csv --output priced.csv
  python bulk_calculator.py products.csv --cpa 12 --margin 25"""
    for line in appendix_text5.split("\n"):
        pdf._render_paragraph(line)

    # ---- Save ----
    output_path = BASE / "Dropshipping_Business_Plan.pdf"
    pdf.output(str(output_path))
    print(f"PDF generated: {output_path}")
    print(f"Total pages: {pdf.page_no()}")


if __name__ == "__main__":
    main()
