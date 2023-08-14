import tkinter as tk
from PIL import ImageTk, Image
from tkinter import filedialog, messagebox, ttk
import numpy as np
import cv2

'''
1. resize
2. Grey
3. Gaussian filter
4. Roberts
5. Threshold(> 20)
'''

class Hair():
	def __init__(self, parent):
		self.parent = parent
		self.new_window = tk.Toplevel(self.parent)
		self.new_window.title("Hair")
		self.new_window.geometry("1300x800")
		menubar = tk.Menu(self.new_window)
		# File Menu
		self.filemenu = tk.Menu(menubar, tearoff = 0)
		menubar.add_command(label = "Open File", command = self.Open)
		self.new_window.config(menu=menubar)

	def Open(self):
		file = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpg","*.jpg"),("all files","*.*")))
		if(file != ''):
			try:
				self.img_canvas.grid_forget()
				self.img1_canvas.grid_forget()
			except:
				pass
			img_open = Image.open(file)
			img = np.array(img_open)
			'''
			new_img = np.zeros((int(img.shape[0] / 2), int(img.shape[1] / 2), 3), dtype=np.uint8)
			for i in range(new_img.shape[0]):
				for l in range(new_img.shape[1]):
					r = round((int(img[i*2,l*2,0]) + int(img[i*2+1,l*2,0]) + int(img[i*2,l*2+1,0]) + int(img[i*2+1,l*2+1,0])) / 4)
					g = round((int(img[i*2,l*2,1]) + int(img[i*2+1,l*2,1]) + int(img[i*2,l*2+1,1]) + int(img[i*2+1,l*2+1,1])) / 4)
					b = round((int(img[i*2,l*2,2]) + int(img[i*2+1,l*2,2]) + int(img[i*2,l*2+1,2]) + int(img[i*2+1,l*2+1,2])) / 4)
					new_img[i, l] = (r, g, b)
			img = new_img
			'''

			img = cv2.resize(img, (int(img.shape[1] / 2), int(img.shape[0] / 2)), interpolation = cv2.INTER_LINEAR)

			img_grey = np.zeros((img.shape[0], img.shape[1]), dtype = np.uint8)
			for i in range(img_grey.shape[0]):
				for l in range(img_grey.shape[1]):
					img_grey[i, l] = 0.2989 * img[i, l, 0] + 0.5870 * img[i, l, 1] + 0.1140 * img[i, l, 2]

			
			img2 = img_grey.copy()
			cv2.GaussianBlur(img2, (5, 5), 0)
			
			img3 = np.zeros((img2.shape[0], img2.shape[1]), dtype = np.uint8)
			for i in range(img3.shape[0] - 1):
				for l in range(img3.shape[1] - 1):
					img3[i, l] = abs(int(img2[i, l]) - int(img2[i + 1, l + 1])) + abs(int(img2[i + 1, l]) - int(img2[i, l + 1]))

			img_result = img.copy()
			for i in range(img_result.shape[0]):
				for l in range(img_result.shape[1]):
					if(img3[i, l] > 25):
						img_result[i, l] = (255, 0, 0)
			
			img_PIL = Image.fromarray(img)
			img_PIL = ImageTk.PhotoImage(img_PIL)
			self.img_canvas = tk.Canvas(self.new_window, width = img.shape[1], height = img.shape[0])
			self.img_canvas.create_image(0, 0, image = img_PIL, anchor = tk.N + tk.W)
			self.img_canvas.image = img_PIL
			self.img_canvas.grid(column = 0, row = 0, padx = 50, pady = 20)

			img_PIL = Image.fromarray(img_result)
			img_PIL = ImageTk.PhotoImage(img_PIL)
			self.img1_canvas = tk.Canvas(self.new_window, width = img_result.shape[1], height = img_result.shape[0])
			self.img1_canvas.create_image(0, 0, image = img_PIL, anchor = tk.N + tk.W)
			self.img1_canvas.image = img_PIL
			self.img1_canvas.grid(column = 1, row = 0, padx = 50, pady = 20)
