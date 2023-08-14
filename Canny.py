import tkinter as tk
from PIL import ImageTk, Image
import numpy as np
from tkinter import filedialog, messagebox, ttk


'''
Step 1 : Gaussian filter 5 * 5
			 2  4  5  4  2
			 4  9 12  9  4
	1/159 *	 5 12 15 12  5
			 4  9 12  9  4
			 2  4  5  4  2

Step 2 : Sobel filter 3 * 3
		Gx = -1 -2 -1
		  	  0  0  0
		  	  1  2  1
		-----------------

		Gy = -1  0  1
			 -2  0  2
		 	 -1  0  1

Step 3 : Non-maximum suppression (0, 45, 90, 135 度)

Step 4 : Connect weak Edge [0.2, 0.8]([51, 204])
'''
class canny():
	def __init__(self, parent, img):
		self.parent = parent
		self.img = img
		self.new_window = tk.Toplevel(self.parent)
		self.new_window.title("Canny")
		self.new_window.geometry("1200x700")
		self.frmU = tk.Frame(self.new_window, width = 1200, height = 670)
		self.frmB = tk.Frame(self.new_window, width = 1200, height = 30)
		self.frmU.grid_propagate(0)
		self.frmB.grid_propagate(0)
		self.frmU.grid(column = 0, row = 0)
		self.frmB.grid(column = 0, row = 1)
		label = tk.Label(self.frmU, text = "原圖", font = ('Arial', 16))
		label.grid(column = 0, row = 0, padx = 10, pady = 10)
		if(len(self.img.shape) == 3):
			new_img = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					new_img[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
			self.img = new_img
		img_PIL = Image.fromarray(self.img, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.img1_Canvas = tk.Canvas(self.frmU, width=self.img.shape[1], height=self.img.shape[0])
		self.img1_Canvas.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.img1_Canvas.image = img_PIL
		self.img1_Canvas.grid(column = 0, row = 1, padx = 10, pady = 10)
		self.img1_Canvas.bind("<Motion>", self.Mouse1)
		self.photo = tk.PhotoImage(file = "icon/right-arrow.png")
		button = tk.Button(self.frmU, image = self.photo, command = self.Gaussian_Filter)
		button.image = self.photo
		button.grid(column = 1, row = 1)

	def Gaussian_Filter(self):
		G_filter = np.array([[2, 4, 5, 4, 2], [4, 9, 12 , 9, 4], [5, 12, 15, 12, 5], [4, 9, 12, 9, 4], [2, 4, 5, 4, 2]], dtype = np.uint8)
		self.img2 = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)

		progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
		progressbar.grid(column = 2, row = 0, sticky = tk.E)
		progressbar["value"] = 0
		progressbar["maximum"] = self.img2.shape[0]

		for i in range(self.img2.shape[0]):
			progressbar["value"] += 1
			progressbar.update()
			for l in range(self.img2.shape[1]):
				value = 0
				for x in range(-2, 3):
					for y in range(-2, 3):
						if(i + x < 0):
							pick_x = i + x + self.img2.shape[0]
						elif(i + x >= self.img2.shape[0]):
							pick_x = i + x - self.img2.shape[0]
						else:
							pick_x = i + x

						if(l + y < 0):
							pick_y = l + y + self.img2.shape[1]
						elif(l + y >= self.img2.shape[1]):
							pick_y = l + y - self.img2.shape[1]
						else:
							pick_y = l + y
						value += (int(G_filter[2 + x, 2 + y]) * int(self.img[pick_x, pick_y]))
				
				value /= 159
				if(value < 0):
					self.img2[i, l] = 0
				elif(value > 255):
					self.img2[i, l] = 255
				else:
					self.img2[i, l] = value
		try:
			progressbar.grid_forget()
		except:
			pass

		label = tk.Label(self.frmU, text = "Gaussian Filter", font = ('Arial', 16))
		label.grid(column = 2, row = 0, padx = 10, pady = 10)
		img_PIL = Image.fromarray(self.img2, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.img2_Canvas = tk.Canvas(self.frmU, width=self.img2.shape[1], height=self.img2.shape[0])
		self.img2_Canvas.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.img2_Canvas.image = img_PIL
		self.img2_Canvas.grid(column = 2, row = 1, padx = 10, pady = 10)
		self.img2_Canvas.bind("<Motion>", self.Mouse2)

		button = tk.Button(self.frmU, image = self.photo, command = self.Sobel_Filter)
		button.image = self.photo
		button.grid(column = 3, row = 1)

	def Sobel_Filter(self):
		self.img3 = np.zeros((self.img2.shape[0], self.img2.shape[1]), dtype=np.uint8)
		self.angle = np.zeros((self.img2.shape[0], self.img2.shape[1]), dtype=np.uint8)

		progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
		progressbar.grid(column = 2, row = 0, sticky = tk.E)
		progressbar["value"] = 0
		progressbar["maximum"] = self.img2.shape[0]

		for i in range(1, self.img3.shape[0] - 1):
			progressbar["value"] += 1
			progressbar.update()
			for l in range(1, self.img3.shape[1] - 1):
				Gx = (int(self.img2[i - 1, l + 1]) + 2 * int(self.img2[i, l + 1]) + int(self.img2[i + 1, l + 1]))
				Gx = abs(Gx - (int(self.img2[i - 1, l - 1]) + 2 * int(self.img2[i, l - 1]) + int(self.img2[i + 1, l - 1])))
				Gy = (int(self.img2[i + 1, l - 1]) + 2 * int(self.img2[i + 1, l]) + int(self.img2[i + 1, l + 1]))
				Gy = abs(Gy - (int(self.img2[i - 1, l - 1]) + 2 * int(self.img2[i - 1, l]) + int(self.img2[i - 1, l + 1])))
				if(Gx + Gy < 0):
					self.img3[i, l] = 0
				elif(Gx + Gy > 255):
					self.img3[i, l] = 255
				else:
					self.img3[i, l] = Gx + Gy

				ang = np.arctan2(Gy, Gx)
				ang = ang * 180. / np.pi
				if(ang < 0): ang += 180
				self.angle[i, l] = ang

		try:
			progressbar.grid_forget()
		except:
			pass

		label = tk.Label(self.frmU, text = "Sobel Filter", font = ('Arial', 16))
		label.grid(column = 4, row = 0, padx = 10, pady = 10)
		img_PIL = Image.fromarray(self.img3, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.img3_Canvas = tk.Canvas(self.frmU, width=self.img3.shape[1], height=self.img3.shape[0])
		self.img3_Canvas.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.img3_Canvas.image = img_PIL
		self.img3_Canvas.grid(column = 4, row = 1, padx = 10, pady = 10)
		self.img3_Canvas.bind("<Motion>", self.Mouse3)

		button = tk.Button(self.frmU, image = self.photo, command = self.Non_maximum_suppression)
		button.image = self.photo
		button.grid(column = 5, row = 1)

	def Non_maximum_suppression(self):
		self.img4 = np.zeros((self.img3.shape[0], self.img3.shape[1]), dtype=np.uint8)

		progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
		progressbar.grid(column = 2, row = 0, sticky = tk.E)
		progressbar["value"] = 0
		progressbar["maximum"] = self.img2.shape[0]

		for i in range(1, self.img4.shape[0] - 1):
			progressbar["value"] += 1
			progressbar.update()
			for l in range(1, self.img4.shape[1] - 1):
				pixel_1 = 255
				pixel_2 = 255

				#angle 0
				if(0 <= self.angle[i, l] < 22.5 or 157.5 <= self.angle[i, l] <= 180):
					pixel_1 = self.img3[i, l + 1]
					pixel_2 = self.img3[i, l - 1]
				#angle 45
				elif(22.5 <= self.angle[i, l] < 67.5):
					pixel_1 = self.img3[i - 1, l + 1]
					pixel_2 = self.img3[i + 1, l - 1]
				#angle 90
				elif(67.5 <= self.angle[i, l] < 112.5):
					pixel_1 = self.img3[i - 1, l]
					pixel_2 = self.img3[i + 1, l]
				#angle 135
				elif(112.5 <= self.angle[i, l] < 157.5):
					pixel_1 = self.img3[i - 1, l - 1]
					pixel_2 = self.img3[i + 1, l + 1]

				if(self.img3[i, l] >= pixel_1 and self.img3[i, l] >= pixel_2):
					self.img4[i, l] = self.img3[i, l]
				else:
					self.img4[i, l] = 0

		try:
			progressbar.grid_forget()
		except:
			pass

		label = tk.Label(self.frmU, text = "Non-maximum suppression", font = ('Arial', 16))
		label.grid(column = 0, row = 2, padx = 10, pady = 10)
		img_PIL = Image.fromarray(self.img4, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.img4_Canvas = tk.Canvas(self.frmU, width=self.img4.shape[1], height=self.img4.shape[0])
		self.img4_Canvas.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.img4_Canvas.image = img_PIL
		self.img4_Canvas.grid(column = 0, row = 3, padx = 10, pady = 10)
		self.img4_Canvas.bind("<Motion>", self.Mouse4)

		button = tk.Button(self.frmU, image = self.photo, command = self.Connect_weak_Edge)
		button.image = self.photo
		button.grid(column = 1, row = 3)

	def Connect_weak_Edge(self):
		upper_bound = 255 * 0.8	#204
		lower_bound = 255 * 0.2 #51
		self.img5 = np.zeros((self.img4.shape[0], self.img4.shape[1]), dtype=np.uint8)

		progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
		progressbar.grid(column = 2, row = 0, sticky = tk.E)
		progressbar["value"] = 0
		progressbar["maximum"] = self.img2.shape[0]

		for i in range(1, self.img5.shape[0] - 1):
			progressbar["value"] += 1
			progressbar.update()
			for l in range(1, self.img5.shape[1] - 1):
				if(self.img4[i, l] > upper_bound):
					self.img5[i, l] = self.img4[i, l]
				elif(self.img4[i, l] < lower_bound):
					self.img4[i, l] = 0
				else:
					count = 0
					for x in range(-1, 2):
						for y in range(-1, 2):
							if(self.img4[i + x, l + y] > upper_bound):
								count += 1
					if(count >= 2):
						self.img5[i, l] = self.img4[i, l]
					else:
						self.img5[i, l] = 0

		try:
			progressbar.grid_forget()
		except:
			pass

		label = tk.Label(self.frmU, text = "Connect Weak Edge", font = ('Arial', 16))
		label.grid(column = 2, row = 2, padx = 10, pady = 10)
		img_PIL = Image.fromarray(self.img5, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.img5_Canvas = tk.Canvas(self.frmU, width=self.img4.shape[1], height=self.img4.shape[0])
		self.img5_Canvas.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.img5_Canvas.image = img_PIL
		self.img5_Canvas.grid(column = 2, row = 3, padx = 10, pady = 10)
		self.img5_Canvas.bind("<Motion>", self.Mouse5)

	def Mouse1(self, event):
		self.Mouse_Information(event, self.img)

	def Mouse2(self, event):
		self.Mouse_Information(event, self.img2)

	def Mouse3(self, event):
		self.Mouse_Information(event, self.img3)

	def Mouse4(self, event):
		self.Mouse_Information(event, self.img4)

	def Mouse5(self, event):
		self.Mouse_Information(event, self.img5)

	def Mouse_Information(self, event, img):
		if(type(img) != type(None)):
			if(event.x < img.shape[1] and event.y < img.shape[0]):
				try:
					self.p_i_label.grid_forget()
				except:
					pass
				try:
					self.p_i_color.grid_forget()
				except:
					pass
				
				self.p_i_label = tk.Label(self.frmB, text = str("X : %3d, Y : %3d" % (event.x, event.y)) + ", " + str("[%3d]" % (img[event.y, event.x])), font = ('Arial', 12))
				p_color = np.full((16, 16), img[event.y, event.x], dtype=np.uint8)
				img_PIL = Image.fromarray(p_color, 'L')
				img_PIL = ImageTk.PhotoImage(img_PIL)
				self.p_i_color = tk.Canvas(self.frmB, width=p_color.shape[1], height=p_color.shape[0])
				self.p_i_color.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
				self.p_i_color.image = img_PIL
				self.p_i_label.grid(column = 0, row = 0, sticky = tk.N)
				self.p_i_color.grid(column = 1, row = 0, sticky = tk.S)
