import tkinter as tk
from PIL import ImageTk, Image
from tkinter import ttk



#Splash Design
class Splash(tk.Toplevel):
	def __init__(self, parent):
		tk.Toplevel.__init__(self, parent)
		self.title("Splash")
		width = parent.winfo_screenwidth()
		height = parent.winfo_screenheight()
		self.iconphoto(False, tk.PhotoImage(file='icon/icon.png'))

		image_file = "icon/Lena_splash.jpg"
		image = ImageTk.PhotoImage(file = image_file)
		x = int((width / 2) - (image.width() / 2))
		y = int((height / 2) - (image.height() / 2))
		geometry = '{}x{}+{}+{}'.format(image.width(), image.height() + 30, x, y)
		self.geometry(geometry)
		l = ttk.Label(self, image = image)
		l.image = image
		l.grid(column = 0, row = 0)

		progressbar = ttk.Progressbar(self, orient=tk.HORIZONTAL, length = image.width(), mode='determinate')
		progressbar.grid(column = 0, row = 1)
		progressbar["value"] = 0
		progressbar["maximum"] = 100
		for i in range(10):
			progressbar["value"] += 10
			progressbar.after(100)
			progressbar.update()
		
		# required to make window show before the program gets to the mainloop
		self.update()