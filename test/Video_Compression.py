import tkinter as tk
from PIL import ImageTk, Image
import numpy as np
from tkinter import filedialog, messagebox, ttk
import cv2 as cv
import time, threading


class Video_Compression():
	def __init__(self, parent):
		self.parent = parent
		self.new_window = tk.Toplevel(self.parent)
		self.new_window.title("Video Compression")
		self.new_window.geometry("1200x800")

		menubar = tk.Menu(self.new_window)
		# File Menu
		self.filemenu = tk.Menu(menubar, tearoff = 0)
		self.filemenu.add_command(label = "Compression", command = self.Compression)
		self.filemenu.add_command(label = "Decompression", command = self.Decompression)
		menubar.add_cascade(label = "File", menu = self.filemenu)

		self.new_window.config(menu=menubar)
		self.filename_label = tk.Label(self.new_window)


	def Compression(self):
		files = filedialog.askopenfilenames(initialdir = "/",title = "Select file",filetypes = (("tiff","*.tiff"),("all files","*.*")))
		self.filename = list(files)
		self.filename.sort()
		print(self.filename)
		self.total_file = len(self.filename)
		self.n = 0
		self.loop = None
		self.i1 = 0
		self.l1 = 0
		self.m_x = 0
		self.m_y = 0
		self.min_MAD = 8 * 8 * 255
		
		self.Compression_Start()
			
	def Compression_Start(self, done = None):
		im1 = Image.open(self.filename[self.n])
		im2 = Image.open(self.filename[self.n + 1])
		self.img1 = np.array(im1)
		self.img2 = np.array(im2)
		self.i = 0
		self.l = 0
		self.first = True
		size1 = int(self.img1.shape[0] / 8)
		size2 = int(self.img1.shape[1] / 8)
		self.Motion_Vector = [[None] * size1 for i in range(size2)]
		if(self.n != self.total_file - 1):
			self.Compression_Find()
		if(done == True):
			print(done)
			print(self.Motion_Vector)
			with open("motion_vector.txt", 'w') as f:
				f.write(str(self.Motion_Vector) + "\n")
		self.n += 1

	def Compression_Find(self, done = None):
		if(self.first):
			self.first = False
			self.Compression_Show(self.n)
		if(self.loop != None):
			self.compare.after_cancel(self.loop)
		#clear
		try:
			self.sequence1.delete(self.draw2)
		except:
			pass

		self.target_block = self.img2[self.i : self.i + 8, self.l : self.l + 8]
		show_target = np.zeros((64, 64), dtype=np.uint8)
		for x in range(self.target_block.shape[0]):
			for y in range(self.target_block.shape[1]):
				show_target[x * 8: (x + 1) * 8, y * 8 : (y + 1) * 8] = self.target_block[x, y]
		if(done == True):
			print(self.i, self.l)
			print(self.m_x, self.m_y)
			print()
			self.Motion_Vector[int(self.i / 8)][int(self.l / 8)] = (self.m_x, self.m_y)
			if(self.i + 4 == self.m_x and self.l + 4 == self.m_y):
				self.Show_Motion_Vector.create_oval(self.m_x, self.m_y, self.m_x + 1, self.m_y + 1, fill = "black")
			else:
				self.Show_Motion_Vector.create_line(self.i + 4, self.l + 4, self.m_x, self.m_y, fill = "black")
			
			if((self.i + 8) == self.img2.shape[0] and (self.l + 8) == self.img2.shape[1]):
				self.Compression_Start(True)
			if(self.i + 8 == self.img2.shape[0]):
				self.i = 0
				self.l += 8
			else:
				self.i += 8
			self.i1 = 0
			self.l1 = 0
			self.m_x = 0
			self.m_y = 0
			self.min_MAD = 8 * 8 * 255

		img_PIL = Image.fromarray(show_target, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.compare1.image = img_PIL
		self.compare1.configure(image = img_PIL)
		
		self.draw2 = self.sequence1.create_rectangle(self.i, self.l, self.i + 8, self.l + 8, outline = "red")

		self.Find_Matching()

	def Find_Matching(self):
		self.match_block = np.zeros((8, 8), dtype=np.uint8)
		
		try:
			self.sequence.delete(self.draw1)
		except:
			pass
		
		candidate_block = self.img1[self.i1 : self.i1 + 8, self.l1 : self.l1 + 8]
		show_candidate = np.zeros((64, 64), dtype=np.uint8)
		MAD = 0
		for x in range(8):
			for y in range(8):
				show_candidate[x * 8: (x + 1) * 8, y * 8 : (y + 1) * 8] = candidate_block[x, y]
				MAD += abs(int(self.target_block[x, y]) - int(candidate_block[x, y]))

		if(MAD < self.min_MAD):
			self.min_MAD = MAD
			self.match_block = candidate_block
			self.m_x = self.i1 + 4
			self.m_y = self.l1 + 4
		
		img_PIL = Image.fromarray(show_candidate, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.compare.image = img_PIL
		self.compare.configure(image = img_PIL)
		self.draw1 = self.sequence.create_rectangle(self.i1, self.l1, self.i1 + 8, self.l1 + 8, outline = "red")
		
		if((self.i1 + 8) == self.img1.shape[0] and (self.l1 + 8) == self.img1.shape[1]):
			self.Compression_Find(True)

		if(self.i1 + 8 == self.img1.shape[0]):
			self.i1 = 0
			self.l1 += 1
		else:
			self.i1 += 1

		self.loop = self.compare.after(1, self.Find_Matching)

	def Compression_Show(self, i):
		try:
			self.filename_label.grid_forget()
		except:
			pass
		
		try:
			self.sequence.delete('all')
		except:
			pass
		try:
			self.sequence.grid_forget()
		except:
			pass

		try:
			self.sequence1.delete('all')
		except:
			pass
		try:
			self.sequence1.grid_forget()
		except:
			pass

		try:
			self.Show_Motion_Vector.delete('all')
		except:
			pass
		
		self.filename_label = tk.Label(self.new_window, text = str(self.filename[i].split("/")[-1]) + ", " + str(i + 1) + "/" + str(self.total_file) + " frame", font = ('Arial', 16))
		self.filename_label.grid(column = 0, row = 0, padx = 10, pady = 10)

		img_PIL = Image.fromarray(self.img1, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.sequence = tk.Canvas(self.new_window, width = self.img1.shape[1], height = self.img1.shape[0])
		self.sequence.create_image(0, 0, image = img_PIL, anchor = tk.N + tk.W)
		self.sequence.image = img_PIL
		self.sequence.grid(column = 0, row = 1, padx = 50, pady = 20)
		'''
		self.compare = tk.Label(self.new_window, width = 64, height = 64, highlightbackground = "black", highlightthickness = 1)
		self.compare.grid(column = 1, row = 1, padx = 50, pady = 20)
		'''
		img_PIL = Image.fromarray(self.img2, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.sequence1 = tk.Canvas(self.new_window, width = self.img2.shape[1], height = self.img2.shape[0])
		self.sequence1.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.sequence1.image = img_PIL
		self.sequence1.grid(column = 2, row = 1, padx = 50, pady = 20)
		
		self.compare1 = tk.Label(self.new_window, width = 64, height = 64, highlightbackground = "black", highlightthickness = 1)
		self.compare1.grid(column = 3, row = 1, padx = 50, pady = 20)

		self.Show_Motion_Vector = tk.Canvas(self.new_window, width = self.img1.shape[1], height = self.img1.shape[0], bg = "white", highlightbackground = "black", highlightthickness = 1)
		self.Show_Motion_Vector.grid(column = 0, row = 2, padx = 50, pady = 20)
		for i in range(4, self.img1.shape[0], 4):
			for l in range(4, self.img1.shape[1], 4):
				self.Show_Motion_Vector.create_oval(i, l, i + 1, l + 1, fill = "black")


	def Decompression(self):
		self.tiff_file = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("tiff","*.tiff"),("all files","*.*")))
		M_V_file = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("txt","*.txt"),("all files","*.*")))
		
		im1 = Image.open(self.tiff_file)
		img = np.array(im1)

		self.total_file = 0
		self.All_img = [img]
		self.All_Moction_Vector = []
		with open(M_V_file, 'r') as fp:
			while(1):
				txt = fp.readline()
				self.total_file += 1
				if(len(txt) == 0):
					break
				else:
					motion_vector = eval(txt)
					self.All_Moction_Vector.append(motion_vector)
					img = self.Next_Image(img, motion_vector)
					self.All_img.append(img)
		print(self.total_file)
		self.i = 0
		self.loop = None
		self.Show_Decomprssion()
		

	def Show_Decomprssion(self):
		try:
			self.filename_label.grid_forget()
		except:
			pass
		self.filename_label = tk.Label(self.new_window, text = str(self.tiff_file.split("/")[-1]) + ", " + str((self.i + 1)) + "/" + str(self.total_file) + " frame", font = ('Arial', 12))
		self.filename_label.grid(column = 0, row = 0, padx = 10, pady = 10, columnspan = 4)

		photo = tk.PhotoImage(file = "icon/play.png")
		button = tk.Button(self.new_window, image = photo, command = self.Play)
		button.image = photo
		button.grid(column = 0, row = 2)

		photo = tk.PhotoImage(file = "icon/back.png")
		button = tk.Button(self.new_window, image = photo, command = self.Back)
		button.image = photo
		button.grid(column = 1, row = 2)

		photo = tk.PhotoImage(file = "icon/pause.png")
		button = tk.Button(self.new_window, image = photo, command = self.Pause)
		button.image = photo
		button.grid(column = 2, row = 2)

		photo = tk.PhotoImage(file = "icon/next.png")
		button = tk.Button(self.new_window, image = photo, command = self.Next)
		button.image = photo
		button.grid(column = 3, row = 2)

		img1 = self.All_img[self.i]
		img_PIL = Image.fromarray(img1, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.sequence = tk.Label(self.new_window, width = img1.shape[1], height = img1.shape[0], image = img_PIL)
		self.sequence.image = img_PIL
		self.sequence.grid(column = 0, row = 1, padx = 50, pady = 20, columnspan = 4)

		self.Show_Motion_Vector = tk.Canvas(self.new_window, width = img1.shape[1], height = img1.shape[0], bg = "white", highlightbackground = "black", highlightthickness = 1)
		self.Show_Motion_Vector.grid(column = 0, row = 3, padx = 50, pady = 20, columnspan = 4)

		m = 4
		n = 4
		for i in range(len(self.All_Moction_Vector[self.i])):
			for l in range(len(self.All_Moction_Vector[self.i][0])):
				(x, y) = self.All_Moction_Vector[self.i][i][l]
				if(m == x and n == y):
					self.Show_Motion_Vector.create_oval(x, y, x + 1, y + 1, fill = "black")
				else:
					self.Show_Motion_Vector.create_line(m, n, x, y, fill = "black")
				m += 8
			m = 0
			n += 8

		img2 = self.All_img[self.i + 1]
		img_PIL = Image.fromarray(img2, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.sequence1 = tk.Label(self.new_window, width = img2.shape[1], height = img2.shape[0], image = img_PIL)
		self.sequence1.image = img_PIL
		self.sequence1.grid(column = 4, row = 1, padx = 50, pady = 20, columnspan = 4)
		

	def Next_Image(self, img, motion_vector):
		img1 = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
		m = 0
		n = 0
		for i in range(len(motion_vector)):
			for l in range(len(motion_vector[0])):
				(x, y) = motion_vector[i][l]
				img1[i * 8 : (i + 1) * 8, l * 8 : (l + 1) * 8] = img[x - 4 : x + 4, y - 4 : y + 4]
		return img1

	def Play(self):
		if(self.i + 1 != self.total_file - 1):
			self.i += 1
			try:
				self.Show_Motion_Vector.delete('all')
			except:
				pass
			
			self.filename_label['text'] = str(self.tiff_file.split("/")[-1]) + ", " + str((self.i + 1)) + "/" + str(self.total_file) + " frame"

			img1 = self.All_img[self.i]
			img_PIL = Image.fromarray(img1, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)

			self.sequence.image = img_PIL
			self.sequence.configure(image = img_PIL)

			img2 = self.All_img[self.i + 1]
			img_PIL = Image.fromarray(img2, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)

			self.sequence1.image = img_PIL
			self.sequence1.configure(image = img_PIL)
			m = 4
			n = 4
			for i in range(len(self.All_Moction_Vector[self.i])):
				for l in range(len(self.All_Moction_Vector[self.i][0])):
					(x, y) = self.All_Moction_Vector[self.i][i][l]
					if(m == x and n == y):
						self.Show_Motion_Vector.create_oval(x, y, x + 1, y + 1, fill = "black")
					else:
						self.Show_Motion_Vector.create_line(m, n, x, y, fill = "black")
					m += 8
				m = 0
				n += 8
			self.loop = self.Show_Motion_Vector.after(1, self.Play)
		else:
			if(self.loop != None):
				self.Show_Motion_Vector.after_cancel(self.loop)
			self.loop = None

	def Back(self):
		if(self.i != 0):
			self.i -= 1
			try:
				self.Show_Motion_Vector.delete('all')
			except:
				pass
			self.filename_label['text'] = str(self.tiff_file.split("/")[-1]) + ", " + str((self.i + 1)) + "/" + str(self.total_file) + " frame"

			img1 = self.All_img[self.i]
			img_PIL = Image.fromarray(img1, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)

			self.sequence.image = img_PIL
			self.sequence.configure(image = img_PIL)

			img2 = self.All_img[self.i + 1]
			img_PIL = Image.fromarray(img2, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)

			self.sequence1.image = img_PIL
			self.sequence1.configure(image = img_PIL)
			m = 4
			n = 4
			for i in range(len(self.All_Moction_Vector[self.i])):
				for l in range(len(self.All_Moction_Vector[self.i][0])):
					(x, y) = self.All_Moction_Vector[self.i][i][l]
					if(m == x and n == y):
						self.Show_Motion_Vector.create_oval(x, y, x + 1, y + 1, fill = "black")
					else:
						self.Show_Motion_Vector.create_line(m, n, x, y, fill = "black")
					m += 8
				m = 0
				n += 8
			self.loop = self.Show_Motion_Vector.after(1, self.Back)
		else:
			if(self.loop != None):
				self.Show_Motion_Vector.after_cancel(self.loop)
			self.loop = None

	def Pause(self):
		if(self.loop != None):
			self.Show_Motion_Vector.after_cancel(self.loop)

	def Next(self):
		if(self.i + 1 != self.total_file - 1):
			self.i += 1
			try:
				self.Show_Motion_Vector.delete('all')
			except:
				pass
			
			self.filename_label['text'] = str(self.tiff_file.split("/")[-1]) + ", " + str((self.i + 1)) + "/" + str(self.total_file) + " frame"

			img1 = self.All_img[self.i]
			img_PIL = Image.fromarray(img1, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)

			self.sequence.image = img_PIL
			self.sequence.configure(image = img_PIL)

			img2 = self.All_img[self.i + 1]
			img_PIL = Image.fromarray(img2, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)

			self.sequence1.image = img_PIL
			self.sequence1.configure(image = img_PIL)
			m = 4
			n = 4
			for i in range(len(self.All_Moction_Vector[self.i])):
				for l in range(len(self.All_Moction_Vector[self.i][0])):
					(x, y) = self.All_Moction_Vector[self.i][i][l]
					if(m == x and n == y):
						self.Show_Motion_Vector.create_oval(x, y, x + 1, y + 1, fill = "black")
					else:
						self.Show_Motion_Vector.create_line(m, n, x, y, fill = "black")
					m += 8
				m = 0
				n += 8

