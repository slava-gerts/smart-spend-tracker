from django.conf import settings

from groq import Groq


class STTService:
	def __init__(self):
		self.client = Groq(api_key=settings.GROQ_API_KEY)

	def transcribe(self, file_path: str) -> str:
		with open(file_path, "rb") as file:
			transcription = self.client.audio.transcriptions.create(
				file=file,
				model="whisper-large-v3",
				response_format="text",
				language="en"
			)

			return transcription
