from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app_paths import get_app_paths


@dataclass(frozen=True)
class CompanyProfile:
    name: str
    tagline: str
    address_lines: list[str]
    phone: str
    email: str
    conditions: list[str]
    acceptance_text: str
    legal_notice: str


DEFAULT_COMPANY_PROFILE = CompanyProfile(
    name="Krystal Elec",
    tagline="Energie & protection - tous types de travaux electriques",
    address_lines=[
        "Route de Leodate Zami Fond Bambou",
        "97139 Les Abymes",
    ],
    phone="+590 6912 66773",
    email="krystal.elec@gmail.com",
    conditions=[
        "Delais : 2 jours",
        "Materiels a la charge du client",
        "Paiement : acompte 30 %, solde fin de travaux",
        "Validite : 30 jours",
    ],
    acceptance_text=(
        "Je soussigne(e), {client_name}, accepte le devis {quote_number} "
        "pour un montant total de {total_amount} TTC."
    ),
    legal_notice="TVA non applicable - art. 293 B du CGI",
)


class QuotePdfService:
    def __init__(
        self,
        project_root: Path | None = None,
        company_profile: CompanyProfile | None = None,
    ) -> None:
        app_paths = get_app_paths()
        self.project_root = Path(project_root or app_paths.project_root)
        resources_root = Path(project_root) if project_root else app_paths.bundle_root
        self.assets_dir = resources_root / "assets" / "quotes"
        self.exports_dir = app_paths.exports_dir
        self.company_profile = company_profile or DEFAULT_COMPANY_PROFILE
        self.left_panel_ratio = 0.50

    def export_quote_pdf(self, quote: dict[str, Any], client: dict[str, Any]) -> Path:
        output_path = self._build_output_path(quote["numero"])
        self._write_pdf(quote, client, output_path)
        return output_path

    def _build_output_path(self, quote_number: str) -> Path:
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        safe_number = "".join(character for character in quote_number if character.isalnum() or character in ("-", "_"))
        return self.exports_dir / f"devis_{safe_number}.pdf"

    def _write_pdf(self, quote: dict[str, Any], client: dict[str, Any], output_path: Path) -> None:
        try:
            from reportlab.graphics import renderPDF
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.utils import ImageReader
            from reportlab.pdfbase.pdfmetrics import stringWidth
            from reportlab.pdfgen import canvas
            from reportlab.platypus import Paragraph
            from svglib.svglib import svg2rlg
        except ImportError as error:
            raise RuntimeError("ReportLab est requis pour generer le devis PDF.") from error

        pdf = canvas.Canvas(str(output_path), pagesize=A4)
        page_width, page_height = A4

        palette = {
            "blue": colors.HexColor("#386FB5"),
            "yellow": colors.HexColor("#F1E033"),
            "dark": colors.HexColor("#111111"),
            "text": colors.HexColor("#1A1A1A"),
            "muted_blue": colors.HexColor("#3D72B2"),
            "white": colors.white,
        }

        margin = 12
        left = margin
        bottom = margin
        top = page_height - margin
        content_width = page_width - (margin * 2)

        pdf.setStrokeColor(palette["dark"])
        pdf.setLineWidth(1.8)
        pdf.rect(left, bottom, content_width, page_height - (margin * 2))

        y = top
        y = self._draw_header(
            pdf,
            quote,
            left,
            y,
            content_width,
            palette,
            ImageReader,
            renderPDF,
            svg2rlg,
            stringWidth,
        )
        y = self._draw_band(pdf, left, y, content_width, palette)
        y = self._draw_parties(pdf, quote, client, left, y, content_width, palette)
        y = self._draw_band(pdf, left, y, content_width, palette)
        y = self._draw_lines_table(pdf, quote, left, y, content_width, palette, Paragraph, ParagraphStyle)
        y = self._draw_band(pdf, left, y, content_width, palette)
        y = self._draw_conditions(pdf, left, y, content_width, palette, quote)
        self._draw_acceptance(pdf, quote, client, left, y, content_width, palette, Paragraph, ParagraphStyle)

        pdf.showPage()
        pdf.save()

    def _draw_header(self, pdf, quote, x, y_top, width, palette, image_reader_cls, render_pdf_module, svg_loader, string_width) -> float:
        header_height = 92
        left_width = width * self.left_panel_ratio
        right_width = width - left_width
        y = y_top - header_height

        pdf.setStrokeColor(palette["dark"])
        pdf.setLineWidth(1.4)
        pdf.rect(x, y, left_width, header_height)
        pdf.setFillColor(palette["blue"])
        pdf.rect(x + left_width, y, right_width, header_height, fill=1, stroke=1)

        self._draw_logo(
            pdf,
            x + 2,
            y + 4,
            left_width - 4,
            header_height - 8,
            palette,
            image_reader_cls,
            render_pdf_module,
            svg_loader,
        )

        quote_number = f"DEVIS N° : {quote['numero']}"
        quote_date = f"Date : {self._format_date(quote.get('created_at'))}"

        pdf.setFillColor(palette["white"])
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(x + left_width + (right_width - string_width(quote_number, "Helvetica-Bold", 16)) / 2, y + 56, quote_number)

        pdf.setFont("Helvetica", 11.5)
        pdf.drawString(x + left_width + (right_width - string_width(quote_date, "Helvetica", 11.5)) / 2, y + 22, quote_date)
        return y

    def _draw_band(self, pdf, x, y_top, width, palette) -> float:
        band_height = 10
        y = y_top - band_height
        pdf.setFillColor(palette["yellow"])
        pdf.rect(x, y, width, band_height, fill=1, stroke=1)
        return y

    def _draw_parties(self, pdf, quote, client, x, y_top, width, palette) -> float:
        block_height = 106
        y = y_top - block_height
        left_width = width * self.left_panel_ratio
        right_width = width - left_width

        pdf.setStrokeColor(palette["dark"])
        pdf.setLineWidth(1.3)
        pdf.rect(x, y, left_width, block_height)
        pdf.rect(x + left_width, y, right_width, block_height)

        pdf.setFillColor(palette["muted_blue"])
        pdf.setFont("Helvetica", 12.5)
        pdf.drawString(x + left_width + 16, y + block_height - 24, "Client")

        company_y = y + block_height - 26
        pdf.setFont("Helvetica", 10.2)
        for line in self.company_profile.address_lines + [
            f"Tel : {self.company_profile.phone}",
            f"Mail : {self.company_profile.email}",
        ]:
            for wrapped_line in self._wrap_text(line, 34):
                pdf.drawString(x + 16, company_y, wrapped_line)
                company_y -= 18

        current_y = y + block_height - 46
        client_rows = [
            ("Nom :", client.get("nom") or quote.get("client_nom") or ""),
            ("Adresse :", client.get("adresse") or ""),
            ("Tel :", client.get("telephone") or ""),
        ]
        pdf.setFont("Helvetica", 10.2)
        for label, value in client_rows:
            pdf.setFillColor(palette["muted_blue"])
            pdf.drawString(x + left_width + 16, current_y, label)
            pdf.setFillColor(palette["text"])
            wrapped_lines = self._split_lines(value, 24) or [""]
            pdf.drawString(x + left_width + 78, current_y, wrapped_lines[0])
            next_y = current_y - 14
            for extra_line in wrapped_lines[1:]:
                pdf.drawString(x + left_width + 78, next_y, extra_line)
                next_y -= 14
            current_y = next_y - 4

        return y

    def _draw_lines_table(self, pdf, quote, x, y_top, width, palette, Paragraph, ParagraphStyle) -> float:
        header_height = 28
        total_height = 38
        body_target_height = 286
        current_y = y_top - header_height
        col_widths = [width * 0.57, width * 0.10, width * 0.12, width * 0.21]
        col_x = [x]
        for value in col_widths[:-1]:
            col_x.append(col_x[-1] + value)

        pdf.setStrokeColor(palette["dark"])
        pdf.setLineWidth(1.4)
        pdf.setFillColor(palette["blue"])
        headers = ["Designation", "Qte", "U", "TOTAL HT"]
        for index, header in enumerate(headers):
            pdf.rect(col_x[index], current_y, col_widths[index], header_height, fill=1, stroke=1)
            pdf.setFillColor(palette["white"])
            pdf.setFont("Helvetica-Bold", 11.5)
            self._draw_centered_text(pdf, header, col_x[index], current_y, col_widths[index], header_height)
            pdf.setFillColor(palette["blue"])

        row_style = ParagraphStyle(
            "quote-row",
            fontName="Helvetica",
            fontSize=9.2,
            leading=11,
            textColor=palette["text"],
        )

        used_height = 0
        current_y -= 1
        for line in quote.get("lignes", []):
            paragraph = Paragraph((line.get("description") or "").replace("\n", "<br/>"), row_style)
            _, paragraph_height = paragraph.wrap(col_widths[0] - 10, 200)
            row_height = max(24, paragraph_height + 8)
            row_y = current_y - row_height
            self._draw_row(pdf, col_x, col_widths, row_y, row_height, palette)
            paragraph.drawOn(pdf, col_x[0] + 4, row_y + 4)

            pdf.setFont("Helvetica", 9.5)
            self._draw_centered_text(pdf, self._format_number(line.get("quantite", 0)), col_x[1], row_y, col_widths[1], row_height)
            self._draw_right_text(pdf, self._format_currency(line.get("prix_unitaire", 0)), col_x[2], row_y, col_widths[2], row_height, padding=4)
            self._draw_right_text(pdf, self._format_currency(line.get("total_ligne", 0)), col_x[3], row_y, col_widths[3], row_height, padding=6)

            current_y = row_y
            used_height += row_height

        while used_height < body_target_height:
            row_height = min(24, body_target_height - used_height)
            row_y = current_y - row_height
            self._draw_row(pdf, col_x, col_widths, row_y, row_height, palette)
            current_y = row_y
            used_height += row_height

        total_y = current_y - total_height
        blank_width = col_widths[0] + col_widths[1]
        pdf.rect(x, total_y, blank_width, total_height, stroke=1, fill=0)
        pdf.setFillColor(palette["blue"])
        pdf.rect(col_x[2], total_y, col_widths[2], total_height, stroke=1, fill=1)
        pdf.setFillColor(palette["white"])
        pdf.setFont("Helvetica-Bold", 12.5)
        self._draw_centered_text(pdf, "TOTAL", col_x[2], total_y, col_widths[2], total_height)

        pdf.setFillColor(palette["white"])
        pdf.setStrokeColor(palette["dark"])
        pdf.rect(col_x[3], total_y, col_widths[3], total_height, stroke=1, fill=0)
        pdf.setFillColor(palette["text"])
        pdf.setFont("Helvetica-Bold", 11.2)
        self._draw_right_text(pdf, self._format_currency(quote.get("total", 0)), col_x[3], total_y, col_widths[3], total_height, padding=6)
        return total_y

    def _draw_conditions(self, pdf, x, y_top, width, palette, quote) -> float:
        y = y_top - 8
        pdf.setFillColor(palette["text"])
        pdf.setFont("Helvetica-Bold", 12.5)
        pdf.drawString(x + 4, y - 8, "CONDITIONS")
        text_y = y - 26

        pdf.setFont("Helvetica", 9.8)
        for condition in self._get_quote_conditions(quote):
            for wrapped_line in self._wrap_text(condition, 82):
                pdf.drawString(x + 4, text_y, wrapped_line)
                text_y -= 14
            text_y -= 3

        for wrapped_line in self._wrap_text(f"Mentions legales : {self.company_profile.legal_notice}", 90):
            pdf.drawString(x + 4, text_y, wrapped_line)
            text_y -= 13
        return text_y - 18

    def _draw_acceptance(self, pdf, quote, client, x, y_top, width, palette, Paragraph, ParagraphStyle) -> None:
        client_name = client.get("nom") or quote.get("client_nom") or "Client"
        total_amount = self._format_currency(quote.get("total", 0))
        acceptance_text = self.company_profile.acceptance_text.format(
            client_name=client_name,
            quote_number=quote["numero"],
            total_amount=total_amount,
        )

        pdf.setFillColor(palette["text"])
        pdf.setFont("Helvetica-Bold", 12.5)
        pdf.drawString(x + 4, y_top, "ACCEPTATION DU DEVIS")

        top_spacing = 28
        style = ParagraphStyle(
            "acceptance",
            fontName="Helvetica",
            fontSize=9.8,
            leading=13,
            textColor=palette["text"],
        )
        paragraph = Paragraph(acceptance_text.replace("\n", "<br/>"), style)
        _, paragraph_height = paragraph.wrap(width - 8, 72)
        paragraph.drawOn(pdf, x + 4, y_top - top_spacing - paragraph_height)

        signature_y = y_top - (top_spacing * 2) - paragraph_height
        pdf.drawString(x + 4, signature_y, "Signature du client :")
        pdf.drawString(x + (width / 2) + 12, signature_y, "Signature de l'electricien :")
        pdf.line(x + 4, signature_y - 32, x + width / 2 - 20, signature_y - 32)
        pdf.line(x + width / 2 + 12, signature_y - 32, x + width - 6, signature_y - 32)

    def _draw_logo(self, pdf, x, y, width, height, palette, image_reader_cls, render_pdf_module, svg_loader) -> None:
        logo_path = self._get_logo_path()
        if logo_path is None:
            self._draw_logo_fallback(pdf, x, y, width, height, palette)
            return

        if logo_path.suffix.lower() == ".svg":
            drawing = svg_loader(str(logo_path))
            if drawing is None:
                self._draw_logo_fallback(pdf, x, y, width, height, palette)
                return

            scale = min(width / drawing.width, height / drawing.height) * 1.5
            scaled_width = drawing.width * scale
            scaled_height = drawing.height * scale
            pdf.saveState()
            pdf.translate(x + (width - scaled_width) / 2, y + (height - scaled_height) / 2)
            pdf.scale(scale, scale)
            render_pdf_module.draw(drawing, pdf, 0, 0)
            pdf.restoreState()
            return

        image = image_reader_cls(str(logo_path))
        image_width, image_height = image.getSize()
        scale = min(width / image_width, height / image_height) * 1.5
        draw_width = image_width * scale
        draw_height = image_height * scale
        offset_x = x + (width - draw_width) / 2
        offset_y = y + (height - draw_height) / 2
        pdf.drawImage(image, offset_x, offset_y, draw_width, draw_height, preserveAspectRatio=True, mask="auto")

    def _draw_logo_fallback(self, pdf, x, y, width, height, palette) -> None:
        initials = "".join(word[0] for word in self.company_profile.name.split()[:2]).upper() or "KE"
        pdf.setFillColorRGB(0.93, 0.96, 1)
        pdf.setStrokeColorRGB(0.54, 0.68, 0.88)
        pdf.rect(x + 6, y + 4, width - 12, height - 8, fill=1, stroke=1)
        pdf.setFillColor(palette["blue"])
        pdf.setFont("Helvetica-Bold", 26)
        self._draw_centered_text(pdf, initials, x + 6, y + 4, width - 12, height - 8)

    def _get_logo_path(self) -> Path | None:
        candidates = [
            self.assets_dir / "logo.png",
            self.assets_dir / "logo2.png",
            self.assets_dir / "logo.jpg",
            self.assets_dir / "logo.jpeg",
            self.assets_dir / "logo.webp",
            self.assets_dir / "logo.svg",
        ]
        for path in candidates:
            if path.exists():
                return path
        return None

    def _draw_row(self, pdf, col_x, col_widths, row_y, row_height, palette) -> None:
        pdf.setStrokeColor(palette["dark"])
        pdf.setLineWidth(1.15)
        for index in range(4):
            pdf.rect(col_x[index], row_y, col_widths[index], row_height, stroke=1, fill=0)

    def _draw_centered_text(self, pdf, text: str, x: float, y: float, width: float, height: float) -> None:
        text = str(text)
        text_width = pdf.stringWidth(text, pdf._fontname, pdf._fontsize)
        text_x = x + (width - text_width) / 2
        text_y = y + (height - pdf._fontsize) / 2 + 4
        pdf.drawString(text_x, text_y, text)

    def _draw_right_text(self, pdf, text: str, x: float, y: float, width: float, height: float, padding: float = 0) -> None:
        text = str(text)
        text_width = pdf.stringWidth(text, pdf._fontname, pdf._fontsize)
        text_x = x + width - text_width - padding
        text_y = y + (height - pdf._fontsize) / 2 + 4
        pdf.drawString(text_x, text_y, text)

    def _wrap_text(self, text: str, max_chars: int) -> list[str]:
        words = str(text).split()
        if not words:
            return [""]

        lines: list[str] = []
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if len(candidate) <= max_chars:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    def _split_lines(self, value: str | None, max_chars: int) -> list[str]:
        if not value:
            return []
        lines: list[str] = []
        for raw_line in str(value).splitlines():
            stripped = raw_line.strip()
            if not stripped:
                continue
            lines.extend(self._wrap_text(stripped, max_chars))
        return lines

    def _format_currency(self, value: Any) -> str:
        amount = float(value or 0)
        formatted = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", " ")
        return f"{formatted} EUR"

    def _format_number(self, value: Any) -> str:
        amount = float(value or 0)
        if amount.is_integer():
            return str(int(amount))
        return f"{amount:.2f}".replace(".", ",")

    def _format_date(self, value: Any) -> str:
        if not value:
            return datetime.now().astimezone().strftime("%d/%m/%Y")

        try:
            parsed = datetime.fromisoformat(str(value))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone().strftime("%d/%m/%Y")
        except ValueError:
            return str(value)

    def _get_quote_conditions(self, quote: dict[str, Any]) -> list[str]:
        materiel_charge = quote.get("materiel_charge") or "client"
        materiel_label = "Materiel a la charge du client"
        if materiel_charge == "electricien":
            materiel_label = "Materiel a la charge de l'electricien"

        conditions = [
            f"Delais : {quote.get('delai') or '2 jours'}",
            materiel_label,
            f"Paiement : acompte {quote.get('acompte_percent', 30)} %, solde fin de travaux",
            f"Validite : {quote.get('validite') or '30 jours'}",
        ]

        exceptional = (quote.get("conditions_exceptionnelles") or "").strip()
        if exceptional:
            conditions.append(f"Condition(s) exceptionnelle(s) : {exceptional}")

        return conditions
