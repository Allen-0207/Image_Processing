import tkinter as tk
from PIL import ImageTk, Image
import numpy as np
from tkinter import filedialog, messagebox, ttk
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cv2 as cv
import time, threading, math


class Video_Compression():
	def __init__(self, parent):
		self.parent = parent
		self.new_window = tk.Toplevel(self.parent)
		self.new_window.title("Video")
		self.new_window.geometry("1200x800")

		menubar = tk.Menu(self.new_window)
		# File Menu
		self.filemenu = tk.Menu(menubar, tearoff = 0)
		self.filemenu.add_command(label = "Optimal Compression", command = self.Compression)
		#self.filemenu.add_command(label = "Coarse Compression", command = self.Compression)
		self.filemenu.add_command(label = "TDL Compression", command = self.TDL)
		#self.filemenu.add_command(label = "TSS Compression", command = self.Compression)
		#self.filemenu.add_command(label = "OSA Compression", command = self.Compression)
		#self.filemenu.add_command(label = "OTS Compression", command = self.Compression)
		#self.filemenu.add_command(label = "CSA Compression", command = self.Compression)
		self.filemenu.add_command(label = "Decompression", command = self.Decompression)
		menubar.add_cascade(label = "File", menu = self.filemenu)

		self.new_window.config(menu=menubar)
		self.filename_label = tk.Label(self.new_window)

	def Compression(self):
		self.mode = "Optimal"
		files = filedialog.askopenfilenames(initialdir = "/",title = "Select file",filetypes = (("tiff","*.tiff"),("all files","*.*")))
		self.filename = list(files)
		self.filename.sort()
		print(str((self.filename[0].split("/")[-1])[:3]))
		self.total_file = len(self.filename)
		self.PSNR = []
		for n in range(self.total_file - 1):
			self.n = n
			self.loop = None
			self.Compression_Start()
			self.Show_PSNR()
			self.Save()
	
	def TDL(self):
		self.mode = "TDL"
		files = filedialog.askopenfilenames(initialdir = "/",title = "Select file",filetypes = (("tiff","*.tiff"),("all files","*.*")))
		self.filename = list(files)
		self.filename.sort()
		print(str((self.filename[0].split("/")[-1])[:3]))
		self.total_file = len(self.filename)
		self.PSNR = []
		for n in range(self.total_file - 1):
			self.n = n
			self.loop = None
			self.Compression_Start()
			self.Show_PSNR()
			self.Save()

	def Compression_Start(self, done = None):
		im1 = Image.open(self.filename[self.n])
		im2 = Image.open(self.filename[self.n + 1])
		self.img1 = np.array(im1)
		self.img2 = np.array(im2)
		self.Compression_Show(self.n)
		self.first = True
		size1 = int(self.img1.shape[0] / 8)
		size2 = int(self.img1.shape[1] / 8)
		self.Motion_Vector = [[None] * size1 for i in range(size2)]
		self.Compression_Find()

	def Compression_Find(self):
		for i in range(0, self.img2.shape[0], 8):
			for l in range(0, self.img2.shape[1], 8):
				try:
					self.sequence1.delete(self.draw2)
				except:
					pass
				self.target_block = self.img2[i : i + 8, l : l + 8]
				
				show_target = np.zeros((64, 64), dtype=np.uint8)
				for x in range(self.target_block.shape[0]):
					for y in range(self.target_block.shape[1]):
						show_target[x * 8: (x + 1) * 8, y * 8 : (y + 1) * 8] = self.target_block[x, y]
				
				img_PIL = Image.fromarray(show_target, 'L')
				img_PIL = ImageTk.PhotoImage(img_PIL)
				self.compare1.image = img_PIL
				self.compare1.configure(image = img_PIL)
				

				self.draw2 = self.sequence1.create_rectangle(l, i ,l + 8, i + 8, outline = "red")
				self.parent.update()
				self.m_x = 0
				self.m_y = 0
				if(self.mode == "Optimal"):
					self.Optimal_Find_Matching()
				elif(self.mode == "TDL"):
					self.TDL_Find_Matching(i, l)
				self.Motion_Vector[int(i / 8)][int(l / 8)] = (self.m_x, self.m_y)
				if(i + 4 == self.m_x and l + 4 == self.m_y):
					self.Show_Motion_Vector.create_oval(self.m_y, self.m_x, self.m_y + 1, self.m_x + 1, fill = "black")
				else:
					self.Show_Motion_Vector.create_line(l + 4, i + 4, self.m_y, self.m_x, fill = "black")
				self.parent.update()

	def Optimal_Find_Matching(self):
		self.match_block = np.zeros((8, 8), dtype=np.uint8)
		min_MAD = 8 * 8 * 255
		for i in range(0, self.img1.shape[0] - 7):
			for l in range(0, self.img2.shape[1] - 7):
				try:
					self.sequence.delete(self.draw1)
				except:
					pass
				candidate_block = self.img1[i : i + 8, l : l + 8]
				#show_candidate = np.zeros((64, 64), dtype=np.uint8)
				MAD = 0
				
				for x in range(8):
					for y in range(8):
						MAD += abs(int(self.target_block[x, y]) - int(candidate_block[x, y]))
						
				'''
						show_candidate[x * 8: (x + 1) * 8, y * 8 : (y + 1) * 8] = candidate_block[x, y]
				
				img_PIL = Image.fromarray(show_candidate, 'L')
				img_PIL = ImageTk.PhotoImage(img_PIL)
				self.compare.image = img_PIL
				self.compare.configure(image = img_PIL)
				self.draw1 = self.sequence.create_rectangle(l, i, l + 8, i + 8, outline = "red")
				'''
				if(MAD < min_MAD):
					min_MAD = MAD
					self.match_block = candidate_block
					self.m_x = i + 4
					self.m_y = l + 4
				self.parent.update()

	def TDL_Find_Matching(self, start_i, start_l):
		'''
		point1 = up
		point2 = down
		point3 = left
		point4 = right
		point5 = center
		'''
		s = 32
		cx = start_i
		cy = start_l
		while(1):
			#print(cx, cy, s)
			if(s != 1):
				find = [[-s, 0], [s, 0], [0, -s], [0, s], [0, 0]]
				best_match = -1
				min_MAD = 8 * 8 * 256
				for i in range(len(find)):
					try:
						self.sequence.delete(self.draw1)
					except:
						pass
					x, y = find[i]
					x = cx + x
					y = cy + y
					#print(x, y)
					if(0 <= x < self.img1.shape[0] and 0 <= (x + 8) <= self.img1.shape[0] and 0 <= y < self.img1.shape[1] and 0 <= (y + 8) <= self.img1.shape[1]):
						MAD = 0
						candidate_block = self.img1[x : x + 8, y : y + 8]
						show_candidate = np.zeros((64, 64), dtype=np.uint8)
						for m in range(8):
							for n in range(8):
								MAD += abs(int(self.target_block[m, n]) - int(candidate_block[m ,n]))
								show_candidate[m * 8: (m + 1) * 8, n * 8 : (n + 1) * 8] = candidate_block[m, n]
						if(MAD <= min_MAD):
							min_MAD = MAD
							best_match = i
						#print("best_match : " + str(best_match))
						img_PIL = Image.fromarray(show_candidate, 'L')
						img_PIL = ImageTk.PhotoImage(img_PIL)
						self.compare.image = img_PIL
						self.compare.configure(image = img_PIL)
						self.draw1 = self.sequence.create_rectangle(y, x, y + 8, x + 8, outline = "red")
						self.parent.update()
				
				if(best_match == 4):
					s = int(s / 2)
				else:
					for i in range(len(find)):
						if(i == best_match):
							x, y = find[i]
							cx += x 
							cy += y
							break
			else:
				min_MAD = 8 * 8 * 256
				
				for i in range(-1, 2, 1):
					for l in range(-1, 2, 1):
						try:
							self.sequence.delete(self.draw1)
						except:
							pass
						x = cx + i
						y = cy + l
						#print(x, y)
						if(0 <= x < self.img1.shape[0] and 0 <= (x + 8) <= self.img1.shape[0] and 0 <= y < self.img1.shape[1] and 0 <= (y + 8) <= self.img1.shape[1]):
							MAD = 0
							candidate_block = self.img1[x : x + 8, y : y + 8]
							show_candidate = np.zeros((64, 64), dtype=np.uint8)
							for m in range(8):
								for n in range(8):
									MAD += abs(int(self.target_block[m, n]) - int(candidate_block[m ,n]))
									show_candidate[m * 8: (m + 1) * 8, n * 8 : (n + 1) * 8] = candidate_block[m, n]
							
							if(MAD < min_MAD):
								min_MAD = MAD
								self.m_x = x + 4
								self.m_y = y + 4
							img_PIL = Image.fromarray(show_candidate, 'L')
							img_PIL = ImageTk.PhotoImage(img_PIL)
							self.compare.image = img_PIL
							self.compare.configure(image = img_PIL)
							self.draw1 = self.sequence.create_rectangle(y, x, y + 8, x + 8, outline = "red")
							self.parent.update()
				break


				

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
			self.Show_Motion_Vector.grid_forget()
		except:
			pass
		try:
			self.button1.grid_forget()
			self.button2.grid_forget()
			self.button3.grid_forget()
			self.button4.grid_forget()
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
		
		self.compare = tk.Label(self.new_window, width = 64, height = 64, highlightbackground = "black", highlightthickness = 1)
		self.compare.grid(column = 1, row = 1, padx = 50, pady = 20)
		
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
		

	def Save(self):
		#print(self.Motion_Vector)
		with open(str((self.filename[self.n].split("/")[-1])[:3]) + ".txt", 'a') as f:
			f.write(str(self.Motion_Vector) + "\n")

	def Show_PSNR(self):
		img_C = np.zeros((self.img2.shape[0], self.img2.shape[1]), dtype=np.uint8)
		for i in range(len(self.Motion_Vector)):
			for l in range(len(self.Motion_Vector[0])):
				(x, y) = self.Motion_Vector[i][l]
				img_C[i * 8 : (i + 1) * 8, l * 8 : (l + 1) * 8] = self.img1[x - 4 : x + 4, y - 4 : y + 4]

		psnr = 0
		for i in range(self.img2.shape[0]):
			for l in range(self.img2.shape[1]):
				psnr += pow((int(self.img2[i, l]) - int(img_C[i, l])), 2)
		psnr /= (self.img2.shape[0] * self.img2.shape[1])
		psnr = round(10 * math.log10((255 ** 2) / psnr), 2)
		self.PSNR.append(psnr)
		print("PSNR : ")
		print(self.PSNR)
		print()
		f = Figure(figsize=(5,3), dpi=70)
		a = f.add_subplot(111)
		a.plot(np.arange(0, len(self.PSNR), 1), self.PSNR, color = 'black', marker = "o")
		

		try:	
			self.PSNR_Canvas.get_tk_widget().grid_forget()
		except:
			pass
		self.PSNR_Canvas = FigureCanvasTkAgg(f, self.new_window)
		self.PSNR_Canvas.draw()
		self.PSNR_Canvas.get_tk_widget().grid(column = 2, row = 2)


	#解壓縮
	def Decompression(self):
		self.tiff_file = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("tiff","*.tiff"),("all files","*.*")))
		M_V_file = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("txt","*.txt"),("all files","*.*")))
		
		im1 = Image.open(self.tiff_file)
		img = np.array(im1)

		self.total_file = 0
		self.All_img = [img]
		self.All_Moction_Vector = []

		with open(M_V_file, 'r') as fp:
			txt = fp.readline()
			self.PSNR = eval(txt)
			while(1):
				txt = fp.readline()
				self.total_file += 1
				if(len(txt) == 0):
					break
				else:
					motion_vector = eval(txt)
					self.All_Moction_Vector.append(motion_vector)
					img = self.Next_Image(self.All_img[self.total_file - 1], motion_vector)
					self.All_img.append(img)
		self.i = 0
		self.loop = None
		self.Show_Decomprssion()
		

	def Show_Decomprssion(self):
		try:
			self.filename_label.grid_forget()
		except:
			pass
		try:
			self.filename_label.grid_forget()
		except:
			pass
		try:
			self.sequence.grid_forget()
		except:
			pass
		try:
			self.sequence1.grid_forget()
		except:
			pass
		try:
			self.Show_Motion_Vector.grid_forget()
		except:
			pass
		try:
			self.compare.grid_forget()
		except:
			pass
		try:
			self.compare1.grid_forget()
		except:
			pass
		try:
			self.button1.grid_forget()
			self.button2.grid_forget()
			self.button3.grid_forget()
			self.button4.grid_forget()
		except:
			pass
		try:	
			self.PSNR_Canvas.get_tk_widget().grid_forget()
		except:
			pass

		self.filename_label = tk.Label(self.new_window, text = str(self.tiff_file.split("/")[-1]) + ", " + str((self.i + 1)) + "/" + str(self.total_file) + " frame", font = ('Arial', 12))
		self.filename_label.grid(column = 0, row = 0, padx = 10, pady = 10, columnspan = 4)

		photo = tk.PhotoImage(file = "icon/play.png")
		self.button1 = tk.Button(self.new_window, image = photo, command = self.Play)
		self.button1.image = photo
		self.button1.grid(column = 0, row = 2)

		photo = tk.PhotoImage(file = "icon/back.png")
		self.button2 = tk.Button(self.new_window, image = photo, command = self.Back)
		self.button2.image = photo
		self.button2.grid(column = 1, row = 2)

		photo = tk.PhotoImage(file = "icon/pause.png")
		self.button3 = tk.Button(self.new_window, image = photo, command = self.Pause)
		self.button3.image = photo
		self.button3.grid(column = 2, row = 2)

		photo = tk.PhotoImage(file = "icon/next.png")
		self.button4 = tk.Button(self.new_window, image = photo, command = self.Next)
		self.button4.image = photo
		self.button4.grid(column = 3, row = 2)

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
					self.Show_Motion_Vector.create_oval(y, x, y + 1, x + 1, fill = "black")
				else:
					self.Show_Motion_Vector.create_line(y, x, n, m, fill = "black")
				n += 8
			n = 4
			m += 8

		img2 = self.All_img[self.i + 1]
		img_PIL = Image.fromarray(img2, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.sequence1 = tk.Label(self.new_window, width = img2.shape[1], height = img2.shape[0], image = img_PIL)
		self.sequence1.image = img_PIL
		self.sequence1.grid(column = 4, row = 1, padx = 50, pady = 20, columnspan = 4)

		f = Figure(figsize=(5,3), dpi=70)
		a = f.add_subplot(111)
		a.plot(np.arange(0, len(self.PSNR), 1), self.PSNR, color = 'black', marker = "o")
		self.PSNR_Canvas = FigureCanvasTkAgg(f, self.new_window)
		self.PSNR_Canvas.draw()
		self.PSNR_Canvas.get_tk_widget().grid(column = 4, row = 3)
		

	def Next_Image(self, img, motion_vector):
		img1 = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
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
						self.Show_Motion_Vector.create_oval(y, x, y + 1, x + 1, fill = "black")
					else:
						self.Show_Motion_Vector.create_line(y, x, n, m, fill = "black")
					n += 8
				n = 4
				m += 8
			
			self.loop = self.Show_Motion_Vector.after(2, self.Play)
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
						self.Show_Motion_Vector.create_oval(y, x, y + 1, x + 1, fill = "black")
					else:
						self.Show_Motion_Vector.create_line(y, x, n, m, fill = "black")
					n += 8
				n = 4
				m += 8
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
						self.Show_Motion_Vector.create_oval(y, x, y + 1, x + 1, fill = "black")
					else:
						self.Show_Motion_Vector.create_line(y, x, n, m, fill = "black")
					n += 8
				n = 4
				m += 8

