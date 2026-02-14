import io
import asyncio

from aiogram import Bot
from aiogram.types import BufferedInputFile
from celery import shared_task

from django.conf import settings
from django.db.models import Sum
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

from apps.transactions.models import Transaction
from apps.users.models import Profile


@shared_task(name='apps.transactions.tasks.generate_monthly_report')
def generate_monthly_report(telegram_id: int):
	profile = Profile.objects.get(telegram_id=telegram_id)
	now = timezone.now()

	transactions = Transaction.objects.filter(
		profile=profile,
		date__month=now.month,
		date__year=now.year
	).order_by('date')

	buffer = io.BytesIO()
	doc = SimpleDocTemplate(buffer, pagesize=letter)
	elements = []
	pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
	styles = getSampleStyleSheet()
	styles['Normal'].fontName = 'DejaVu'
	styles['Title'].fontName = 'DejaVu'

	elements.append(Paragraph(f"Monthly Report: {now.strftime('%B %Y')}", styles['Title']))

	data = [["Date", "Category", "Amount", "Ccy", "Description"]]

	for tx in transactions:
		data.append([
			tx.date.strftime("%Y-%m-%d"),
			tx.category.name,
			str(tx.amount),
			tx.currency,
			(tx.description[:20] + '...') if tx.description and len(tx.description) > 20 else (tx.description or "")
		])

	table = Table(data)
	table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, 0), colors.grey),
		('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
		('ALIGN', (0, 0), (-1, -1), 'CENTER'),
		('GRID', (0, 0), (-1, -1), 1, colors.black),
		('FONTNAME', (0, 0), (-1, -1), 'DejaVu')
	]))
	elements.append(table)

	total = transactions.aggregate(total=Sum('base_amount'))['total'] or 0

	elements.append(Paragraph(f"<br/><br/>Total Spent (Base): {total:.2f} {profile.base_currency}", styles['Normal']))

	doc.build(elements)
	buffer.seek(0)

	async def send_file():
		bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
		input_file = BufferedInputFile(buffer.read(), filename=f"report_{now.strftime('%Y_%m')}.pdf")

		await bot.send_document(chat_id=telegram_id, document=input_file, caption="Here is your report! 📊")
		await bot.session.close()

	asyncio.run(send_file())
	return f"Report sent to {telegram_id}"
