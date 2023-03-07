import math
import fitz
from tkinter import PhotoImage

class PDFMiner:
	def __init__(self, filepath):
		self.filepath = filepath
		self.pdf = fitz.open(self.filepath)
		self.first_page = self.pdf.load_page(0)
		self.width, self.height = self.first_page.rect.width, self.first_page.rect.height
		print(self.width, self.height)

		zoomdict = {800:0.8, 700:0.6, 600:0.7, 500:0.8}
		width = int(math.floor(self.width / 100.0)) * 100
		print(width)
		self.zoom = zoomdict.get(width,0)


	def get_metadata(self):
		metadata = self.pdf.metadata
		numPages = self.pdf.page_count

		return metadata, numPages

	def get_page(self, page_num):
		page = self.pdf.load_page(page_num)
		if self.zoom:
			mat = fitz.Matrix(self.zoom, self.zoom)
			pix = page.get_pixmap(matrix=mat)
		else:
			pix = page.getpixmap()
		px1 = fitz.Pixmap(pix, 0) if pix.alpha else pix
		imgdata = px1.tobytes('ppm')
		return PhotoImage(data=imgdata)

	def getText(self, page_num):
		page = self.pdf.load_page(page_num)
		text = page.get_text('text')
		return text 