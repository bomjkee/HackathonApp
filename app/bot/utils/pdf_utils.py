import os
from typing import List
from loguru import logger

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.db.models import User


def create_hackathon_report_pdf(users: List[User], hackathon_name: str, start_date: str, end_date: str, pdf_dir: str = "reports_pdf"):

    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    safe_name = "".join(c for c in hackathon_name if c.isalnum() or c in (' ', '-', '_')).strip()
    file_path = os.path.join(pdf_dir, f"{safe_name}.pdf")

    pdfmetrics.registerFont(TTFont('ArialUnicode', 'arial.ttf'))


    c = canvas.Canvas(file_path, pagesize=letter)

    styles = getSampleStyleSheet()
    title_style = styles['h1']
    title_style.fontName = 'ArialUnicode'
    title_style.textColor = colors.blue
    title_style.alignment = 1

    heading_style = styles['h2']
    heading_style.fontName = 'ArialUnicode'
    heading_style.textColor = colors.black

    normal_style = styles['Normal']
    normal_style.fontName = 'ArialUnicode'
    normal_style.fontSize = 12
    normal_style.leading = 14
    normal_style.textColor = colors.black

    title = Paragraph(f"Отчет по хакатону: {hackathon_name}", title_style)
    title.wrapOn(c, letter[0] - 2 * inch, letter[1])
    title.drawOn(c, inch, letter[1] - inch)

    c.setFont('ArialUnicode', 14)
    c.drawCentredString(letter[0]/2.0,letter[1] - 1.5 * inch,f"Дата проведения: {start_date} - {end_date}")

    students = [user for user in users if user.is_mirea_student]
    non_students = [user for user in users if not user.is_mirea_student]

    students.sort(key=lambda user: user.group or "")

    y_position = letter[1] - 2 * inch

    def add_section_header(text, y_pos):
        p = Paragraph(text, heading_style)
        p.wrapOn(c, letter[0] - 2 * inch, letter[1])
        p.drawOn(c, inch, y_pos)
        return y_pos - 0.5 * inch

    def add_user_info(user, y_pos):
        user_info = f"ФИО: {user.full_name or 'Не указано'}, Telegram: @{user.username}"
        if user.is_mirea_student:
            user_info += f", Группа: {user.group or 'Не указана'}"

        p = Paragraph(user_info, normal_style)
        p.wrapOn(c, letter[0] - 2 * inch, letter[1])
        p.drawOn(c, inch, y_pos)
        return y_pos - 0.3 * inch



    y_position = add_section_header("Студенты МИРЭА", y_position)

    if students:
        for student in students:
            y_position = add_user_info(student, y_position)
            if y_position < inch:
                c.showPage()
                y_position = letter[1] - inch


    else:
        p = Paragraph("Нет студентов МИРЭА.", normal_style)
        p.wrapOn(c, letter[0] - 2 * inch, letter[1])
        p.drawOn(c, inch, y_position)
        y_position -= 0.3 * inch

    y_position = add_section_header("Не студенты", y_position)

    if non_students:
        for non_student in non_students:
            y_position = add_user_info(non_student, y_position)
            if y_position < inch:
                c.showPage()
                y_position = letter[1] - inch

    else:
        p = Paragraph("Нет участников не из МИРЭА.", normal_style)
        p.wrapOn(c, letter[0] - 2 * inch, letter[1])
        p.drawOn(c, inch, y_position)
        y_position -= 0.3 * inch

    c.save()
    logger.info(f"PDF отчет создан: {file_path}")
    return file_path