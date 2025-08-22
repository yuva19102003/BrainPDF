from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem

PAGE_WIDTH, PAGE_HEIGHT = A4

class PDFGenerator:
    def __init__(self, output_file: str):
        self.output_file = output_file

    # --- Page Decoration ---
    def decorate_page(self, c, doc):
        header_height = 60
        footer_height = 60

        # Header bar - Violet
        c.setFillColorRGB(0.686, 0.478, 0.773)  # Violet
        c.rect(0, PAGE_HEIGHT - header_height, PAGE_WIDTH, header_height, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Times-Bold", 20)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 38, "My Application Name")

        # Footer bar - Violet
        c.setFillColorRGB(0.686, 0.478, 0.773)  # Violet
        c.rect(0, 0, PAGE_WIDTH, footer_height, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Times-Bold", 12)
        c.drawCentredString(PAGE_WIDTH / 2, 40, "Company Name | Service Name | Contact: +91-9876543210")

        # Watermark
        c.saveState()
        c.setFont("Times-Bold", 60)
        c.setFillColorRGB(0.9, 0.9, 0.9, alpha=0.3)
        c.translate(PAGE_WIDTH / 2, PAGE_HEIGHT / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, "CONFIDENTIAL")
        c.restoreState()

    # --- Centered Title ---
    def centered_title(self, text):
        return Paragraph(
            f'<para align="center"><font name="Times-Bold" size="18"><b>{text}</b></font></para>',
            ParagraphStyle('centeredTitle', alignment=1, spaceAfter=12)
        )

    # --- Create PDF ---
    def create_pdf(self, data: dict):
        doc = SimpleDocTemplate(self.output_file, pagesize=A4,
                                rightMargin=40, leftMargin=40,
                                topMargin=80, bottomMargin=80)
        styles = getSampleStyleSheet()

        # Styles using Times New Roman
        summary_style = ParagraphStyle('Summary', parent=styles['Normal'], fontName="Times-Roman", fontSize=12, leading=14, spaceAfter=12)
        bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontName="Times-Roman", leftIndent=15, spaceAfter=6)
        question_style = ParagraphStyle('Question', parent=styles['Heading3'], fontName="Times-Bold", textColor=colors.darkblue, spaceAfter=6)
        option_style = ParagraphStyle('Option', parent=styles['Normal'], fontName="Times-Roman", leftIndent=20, spaceAfter=4)
        answer_style = ParagraphStyle('Answer', parent=styles['Normal'], fontName="Times-Roman", textColor=colors.green, spaceAfter=4)
        explanation_style = ParagraphStyle('Explanation', parent=styles['Italic'], fontName="Times-Roman", textColor=colors.gray, fontSize=9, leftIndent=20, spaceAfter=12)

        elements = []

        # Summary
        elements.append(self.centered_title("Summary"))
        elements.append(Paragraph(data["summary"], summary_style))
        elements.append(Spacer(1, 12))

        # Key Points
        elements.append(self.centered_title("Key Points"))
        bullet_items = [ListItem(Paragraph(f"★ {point}", bullet_style)) for point in data["key_points"]]
        elements.append(ListFlowable(bullet_items, bulletType='bullet'))
        elements.append(Spacer(1, 12))

        # MCQs
        elements.append(self.centered_title("Multiple Choice Questions"))
        for i, mcq in enumerate(data["mcq"], start=1):
            elements.append(Paragraph(f"{i}. {mcq['question']}", question_style))
            for key, val in mcq["option"].items():
                elements.append(Paragraph(f"{key}) {val}", option_style))
            elements.append(Paragraph(f"Answer: {mcq['answer']}", answer_style))
            elements.append(Paragraph(f"Explanation: {mcq['explanation']}", explanation_style))

        # Build PDF
        doc.build(elements, onFirstPage=self.decorate_page, onLaterPages=self.decorate_page)
        return self.output_file
