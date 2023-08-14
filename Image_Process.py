from tkinter import filedialog, messagebox, ttk
from PIL import ImageTk, Image
import numpy as np
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from itertools import combinations
import ctypes, math, time, random

from Header import Header
from Bouncing_Ball import B_Ball
from Canny import canny
from Splash import Splash
from Huffman import Huffman
from Video import Video_Compression
from Hair import Hair

class watermark():
	def __init__(self, parent, img):
		self.parent = parent
		self.img = img
		self.new_window = tk.Toplevel(self.parent)
		self.new_window.title("Watermark")
		self.new_window.geometry("1250x900")
		menubar = tk.Menu(self.new_window)
		menubar.add_cascade(label = "Open Watermark", command = self.read_file)
		self.new_window.config(menu=menubar)

		self.label = tk.Label(self.new_window,  text = " 請先開啟浮水印圖片", font = ('Arial', 12))
		self.label.grid(column = 3, row = 0, sticky = tk.N + tk.W)
		self.snr_label = tk.Label(self.new_window)

		#SNR
		self.p = 0
		self.p_w = 0
		if(len(self.img.shape) == 3):
			new_img = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					new_img[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
					self.p += int(new_img[i, j]) * int(new_img[i, j])
		else:
			new_img = self.img.copy()
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					self.p += int(new_img[i, j]) * int(new_img[i, j])
		self.img = new_img
		img_PIL = Image.fromarray(self.img, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		img_Canvas = tk.Canvas(self.new_window, width=new_img.shape[1], height=new_img.shape[0])
		img_Canvas.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		img_Canvas.image = img_PIL
		img_Canvas.grid(column = 0, row = 0, padx = 10, pady = 10)

		#Bit plane
		i = 128
		row, col = 1, 0
		while(i >= 1):
			new_img_B = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			new_img_B = self.img & int(i)
			new_img_B[new_img_B != 0] = new_img_B[new_img_B != 0] * (256 / i) - 1
			img_PIL = Image.fromarray(new_img_B, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			img_Canvas = tk.Canvas(self.new_window, width=new_img_B.shape[1], height=new_img_B.shape[0])
			img_Canvas.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
			img_Canvas.image = img_PIL
			img_Canvas.grid(column = col, row = row, padx = 10, pady = 10)
			i /= 2
			if(col < 3):
				col += 1
			else:
				col = 0
				row += 1

	def read_file(self):
		filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("PCX","*.PCX, *.pcx"),("all files","*.*")))
		if filename != '':
			f = open(filename, 'rb') #rb = read bytes
			h = f.read(128)
			if h[0] != 10:
				messagebox.showerror("Error", "File Type Not PCX") #Error not pcx file
			header = Header(h)
			XSize = header.XEnd - header.XStart + 1
			YSize = header.YEnd - header.YStart + 1

			if (header.BitsPerPixel == 1) and (header.NumBitPlanes == 1): #Monochrome
				data = f.read()
				image = UI.BW_image(self, header, data)
			elif (header.Version == 5) and (header.BitsPerPixel == 8) and (header.NumBitPlanes == 3):
				data = f.read()
				image = UI._24b_image(self, header, data)
			elif (header.Version == 5) and (header.BitsPerPixel == 8) and (header.NumBitPlanes == 1): #version 5 palette is at back
				data = f.read()
				data = data[0:len(data) - 769]
				f.seek(-768, 2) #2 = back
				s = f.read(768)
				self.Extend_Palette = UI._Extend_Palette(self, s)
				image = UI._256_image(self, header, data)
			
			#watermark RGB -> B/W
			self.water_image = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
			for i in range(image.shape[0]):
				for j in range(image.shape[1]):
					self.water_image[i, j] = 0.3 * int(image[i, j, 0]) + 0.3 * int(image[i, j, 1]) + 0.4 * int(image[i, j, 2])
					if(self.water_image[i, j] < 128) :
						self.water_image[i, j] = 0
					else:
						self.water_image[i, j] = 255

			img_PIL = Image.fromarray(self.water_image, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			img_Canvas = tk.Canvas(self.new_window, width = self.water_image.shape[1], height = self.water_image.shape[0])
			img_Canvas.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
			img_Canvas.image = img_PIL
			img_Canvas.grid(column = 1, row = 0, padx = 10, pady = 10)

			self.label.grid_forget()
			self.label = tk.Label(self.new_window,  text = "Bit-Plane : ", font = ('Arial', 12))
			self.label.grid(column = 3, row = 0, sticky = tk.N + tk.W)
			self.combobox = ttk.Combobox(self.new_window, value = ['0','1', '2', '3', '4', '5', '6', '7',])
			self.combobox.bind("<<ComboboxSelected>>", self.Add_watermark)
			self.combobox.grid(column = 3, row = 0, sticky = tk.N + tk.E)
			

	def Add_watermark(self, event):
		plane = 2 ** int(self.combobox.get())
		self.p_w = 0
		#Add watermark
		new_water_img = self.img.copy()
		for i in range(new_water_img.shape[0]):
			for j in range(new_water_img.shape[1]):
				if(self.img[i, j] & plane):
					new_water_img[i, j] -= plane

				if(self.water_image[i, j] == 255):
					new_water_img[i, j] += plane
				self.p_w += int(int(self.img[i, j]) - int(new_water_img[i, j])) * int(int(self.img[i, j]) - int(new_water_img[i, j]))
		img_PIL = Image.fromarray(new_water_img, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		img_Canvas = tk.Canvas(self.new_window, width=new_water_img.shape[1], height=new_water_img.shape[0])
		img_Canvas.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		img_Canvas.image = img_PIL
		img_Canvas.grid(column = 2, row = 0, padx = 10, pady = 10)
		snr = round(10 * math.log10(self.p / self.p_w), 3)
		self.snr_label.grid_forget()
		self.snr_label = tk.Label(self.new_window,  text = "Single-to-Noise Ratio : " + str(snr), font = ('Arial', 12))
		self.snr_label.grid(column = 3, row = 0)

		#Bit plane
		i = 128
		row, col = 1, 0
		while(i >= 1):
			new_img_B = np.zeros((new_water_img.shape[0], new_water_img.shape[1]), dtype=np.uint8)
			new_img_B = new_water_img & int(i)
			new_img_B[new_img_B != 0] = new_img_B[new_img_B != 0] * (256 / i) - 1
			img_PIL = Image.fromarray(new_img_B, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			img_Canvas = tk.Canvas(self.new_window, width=new_img_B.shape[1], height=new_img_B.shape[0])
			img_Canvas.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
			img_Canvas.image = img_PIL
			img_Canvas.grid(column = col, row = row, padx = 10, pady = 10)
			i /= 2
			if(col < 3):
				col += 1
			else:
				col = 0
				row += 1

#Main UI Function & Design
class UI():#tk.Frame):
	def __init__(self, parent):
		#tk.Frame.__init__(self, parent)
		self.img = None
		self.parent = parent
		
		self.parent.withdraw() #隱藏main window

		#splah window
		splash = Splash(self.parent)	
		splash.destroy() #delete splash

		#Cut Setting
		self.drawn  = None
		self.parent.deiconify() #顯示main window
		self.initUI()

	def initUI(self):
		screen_width = self.parent.winfo_screenwidth()
		screen_height = self.parent.winfo_screenheight()
		
		x = int(screen_width/2 - 1400/2)
		y = int(screen_height/2 - 900/2)
		#print(screen_width, screen_height, x, y)
		self.parent.title("Image Process M093040040")
		self.parent.geometry("%dx%d+%d+%d" % (1400, 920, x, y))
		
		menubar = tk.Menu(self.parent)
		# File Menu
		self.filemenu = tk.Menu(menubar, tearoff = 0)
		menubar.add_cascade(label = "File", menu = self.filemenu)
		icon_open = ImageTk.PhotoImage(Image.open("menu_icon/open.png"))
		self.filemenu.add_command(label = "Open", image = icon_open, compound = "left", command = self.Open_File, accelerator = "Ctrl + O")
		
		icon_save = ImageTk.PhotoImage(Image.open("menu_icon/save.png"))
		self.filemenu.add_command(label = "Save (Huffman)", image = icon_save, compound = "left", command = self.Save_File_Huffman, accelerator = "Ctrl + S")
		

		#Edit Menu
		#放大
		self.editmenu = tk.Menu(menubar, tearoff = 0)
		menubar.add_cascade(label = "Edit", menu = self.editmenu)
		magnifymenu = tk.Menu(self.editmenu, tearoff = 0)
		icon_magnify = ImageTk.PhotoImage(Image.open("menu_icon/magnify.png"))
		magnifymenu.add_command(label = "複製", command = self.Magnify_Duplicate_Image, accelerator = "Ctrl + B + 1")
		magnifymenu.add_command(label = "內插", command = self.Magnify_Interpolation_Image, accelerator = "Ctrl + B + 1")
		self.editmenu.add_cascade(label = "放大", menu = magnifymenu, image = icon_magnify, compound = "left")

		#縮小
		minifymenu = tk.Menu(self.editmenu, tearoff = 0)
		icon_minify = ImageTk.PhotoImage(Image.open("menu_icon/minify.png"))
		minifymenu.add_command(label = "刪除", command = self.Minify_Delete_Image, accelerator = "Ctrl + S + 1")
		minifymenu.add_command(label = "平均", command = self.Minify_Mean_Image, accelerator = "Ctrl + S + 1")
		self.editmenu.add_cascade(label = "縮小", menu = minifymenu, image = icon_minify, compound = "left")
		
		#Rotation
		rotationmenu = tk.Menu(self.editmenu, tearoff = 0)
		icon_rotation = ImageTk.PhotoImage(Image.open("menu_icon/rotation.png"))
		rotationmenu.add_command(label = "旋轉(有洞版)", command = self.Rotation_Version_1, accelerator = "Ctrl + R + 1")
		rotationmenu.add_command(label = "旋轉(無洞版)", command = self.Rotation_Version_2, accelerator = "Ctrl + R + 1")
		self.editmenu.add_cascade(label = "旋轉", menu = rotationmenu, image = icon_rotation, compound = "left")
		
		#Cut
		cutmenu = tk.Menu(self.editmenu, tearoff = 0)
		icon_circle = ImageTk.PhotoImage(Image.open("menu_icon/circle.png"))
		cutmenu.add_command(label = "圓形", command = self.Cut_Oval_Image, image = icon_circle, compound = "left", accelerator = "Ctrl + C + 1")
		icon_square = ImageTk.PhotoImage(Image.open("menu_icon/square.png"))
		cutmenu.add_command(label = "方形", command = self.Cut_Rectangle_Image, image = icon_square, compound = "left", accelerator = "Ctrl + C + 2")
		icon_cut = ImageTk.PhotoImage(Image.open("menu_icon/cut.png"))
		self.editmenu.add_cascade(label = "Cut", menu = cutmenu, image = icon_cut, compound = "left")
		
		#Magic wand
		icon_magic = ImageTk.PhotoImage(Image.open("menu_icon/magic.png"))
		self.editmenu.add_command(label = "魔術棒", command = self.Magic_Wand, image = icon_magic, compound = "left", accelerator = "Ctrl + M + W")
		
		#Color Menu
		self.colormenu = tk.Menu(menubar, tearoff = 0)
		#RGB
		icon_rgb = ImageTk.PhotoImage(Image.open("menu_icon/rgb.png"))
		self.colormenu.add_command(label = "RGB", command = self.RGB_image, image = icon_rgb, compound = "left", accelerator = "Ctrl + R")
		
		#Histogram
		icon_histogram = ImageTk.PhotoImage(Image.open("menu_icon/histogram.png"))
		self.colormenu.add_command(label = "Histogram", command = self.Histogram_Image, image = icon_histogram, compound = "left", accelerator = "Ctrl + H")
		
		#Gray
		icon_gray = ImageTk.PhotoImage(Image.open("menu_icon/gray.png"))
		self.colormenu.add_command(label = "灰階", command = self.Color_To_Gray, image = icon_gray, compound = "left", accelerator = "Ctrl + G")
		
		#B/W
		icon_BW = ImageTk.PhotoImage(Image.open("menu_icon/BW.png"))
		self.colormenu.add_command(label = "黑白(level)", command = self.Gray_To_BW, image = icon_BW, compound = "left", accelerator = "Ctrl + B")
		
		#Transparent
		icon_transparent = ImageTk.PhotoImage(Image.open("menu_icon/transparent.png"))
		self.colormenu.add_command(label = "透明", command = self.Transparent_Image, image = icon_transparent, compound = "left", accelerator = "Ctrl + T")
		
		#Invert
		icon_invert = ImageTk.PhotoImage(Image.open("menu_icon/invert.png"))
		self.colormenu.add_command(label = "負片", command = self.Invert_Image, image = icon_invert, compound = "left", accelerator = "Ctrl + I")
		
		#Threshold
		icon_threshold = ImageTk.PhotoImage(Image.open("menu_icon/threshold.png"))
		self.colormenu.add_command(label = "Threshold", command = self.Threshold, image = icon_threshold, compound = "left", accelerator = "Ctrl + T + H")
		
		#Gamma Correction
		icon_gamma = ImageTk.PhotoImage(Image.open("menu_icon/gamma.png"))
		self.colormenu.add_command(label = "Gamma Correction", command = self.Gamma_Correction, image = icon_gamma, compound = "left", accelerator = "Ctrl + G + M")
		
		#Otsu's Threshold
		icon_otsu = ImageTk.PhotoImage(Image.open("menu_icon/otsu.png"))
		self.colormenu.add_command(label = "Otsu's Threshold", command = self.Otsus_Threshold, image = icon_otsu, compound = "left", accelerator = "Ctrl + O + S")
		
		#Kullback
		self.colormenu.add_command(label = "Kullback", command = self.Kullback, image = icon_otsu, compound = "left", accelerator = "Ctrl + K")
		
		#Contrast stretching
		icon_stretching = ImageTk.PhotoImage(Image.open("menu_icon/stretching.png"))
		self.colormenu.add_command(label = "Contrast stretching", command = self.Contrast_Stretching, image = icon_stretching, compound = "left", accelerator = "Ctrl + C + S")
		
		#Bit-plane slicing
		BPSlicingnmenu = tk.Menu(self.colormenu, tearoff = 0)
		icon_bit = ImageTk.PhotoImage(Image.open("menu_icon/bit.png"))
		BPSlicingnmenu.add_command(label = "Binary Code", command = self.Bit_plane_Slicing_Binary, accelerator = "Ctrl + B + C")
		BPSlicingnmenu.add_command(label = "Gray Code", command = self.Bit_plane_Slicing_Gray, accelerator = "Ctrl + G + C")
		BPSlicingnmenu.add_command(label = "Watermark", command = self.Watermark, accelerator = "Ctrl + W")
		self.colormenu.add_cascade(label = "Bit-plane Slicing", menu = BPSlicingnmenu, image = icon_bit, compound = "left")
		
		#Histogram Equalization
		icon_equalization = ImageTk.PhotoImage(Image.open("menu_icon/equalization.png"))
		self.colormenu.add_command(label = "Histogram Equalization", command = self.Histogram_Equalization, image = icon_equalization, compound = "left", accelerator = "Ctrl + H + E")
		
		#Histogram Specification
		icon_match = ImageTk.PhotoImage(Image.open("menu_icon/match.png"))
		self.colormenu.add_command(label = "Histogram Specification", command = self.Histogram_Specification, image = icon_match, compound = "left", accelerator = "Ctrl + H + S")
		
		#Connected Components
		icon_connect = ImageTk.PhotoImage(Image.open("menu_icon/connect.png"))
		self.colormenu.add_command(label = "Connected Components", command = self.Connected_Components, image = icon_connect, compound = "left", accelerator = "Ctrl + C")
		menubar.add_cascade(label = "顏色", menu = self.colormenu)

		self.filtermenu = tk.Menu(menubar, tearoff = 0)
		#Mean & Median Filtering
		icon_filter = ImageTk.PhotoImage(Image.open("menu_icon/filter.png"))
		self.filtermenu.add_command(label = "Outlier", command = self.Outlier, image = icon_filter, compound = "left", accelerator = "Ctrl + F + O")
		self.filtermenu.add_command(label = "Mean & Median", command = self.Mean_Median, image = icon_filter, compound = "left", accelerator = "Ctrl + F + M")
		self.filtermenu.add_command(label = "Pseudo Median", command = self.Pseudo_Median, image = icon_filter, compound = "left", accelerator = "Ctrl + F + P")
		self.filtermenu.add_command(label = "Highpass", command = self.Highpass, image = icon_filter, compound = "left", accelerator = "Ctrl + F + H")
		self.filtermenu.add_command(label = "Edge Crispening", command = self.Edge_Crispening, image = icon_filter, compound = "left", accelerator = "Ctrl + F + E")
		self.filtermenu.add_command(label = "High-boost", command = self.High_Boost, image = icon_filter, compound = "left", accelerator = "Ctrl + F + B")
		icon_edge = ImageTk.PhotoImage(Image.open("menu_icon/edge.png"))
		self.filtermenu.add_command(label = "Roberts & Sobel & Prewitt", command = self.Roberts_Sobel_Prewitt, image = icon_edge, compound = "left", accelerator = "Ctrl + F + R")
		self.filtermenu.add_command(label = "Canny", command = self.Canny_Algorithm, image = icon_edge, compound = "left", accelerator = "Ctrl + F + C")

		menubar.add_cascade(label = "Filtering", menu = self.filtermenu)


		othermenu = tk.Menu(menubar, tearoff = 0)
		#彈跳球
		icon_ball = ImageTk.PhotoImage(Image.open("menu_icon/ball.png"))
		othermenu.add_command(label = "Bouncing ball", command = self.Bouncing_ball, image = icon_ball, compound = "left", accelerator = "Ctrl + B + 2")

		#影片壓縮
		icon_video = ImageTk.PhotoImage(Image.open("menu_icon/video.png"))
		othermenu.add_command(label = "Video", command = self.Video, image = icon_video, compound = "left", accelerator = "Ctrl + V")

		#Hair detect
		icon_hair = ImageTk.PhotoImage(Image.open("menu_icon/hair.png"))
		othermenu.add_command(label = "Hiar", command = self.Hair, image = icon_hair, compound = "left", accelerator = "Ctrl + H + D")

		menubar.add_cascade(label = "Other", menu = othermenu)

		self.parent.config(menu=menubar)

		#Disable menu
		self.filemenu.entryconfig("Save (Huffman)", state="disabled")
		self.editmenu.entryconfig("放大", state="disabled")
		self.editmenu.entryconfig("縮小", state="disabled")
		self.editmenu.entryconfig("旋轉", state="disabled")
		self.editmenu.entryconfig("Cut", state="disabled")
		self.editmenu.entryconfig("魔術棒", state="disabled")
		self.colormenu.entryconfig("RGB", state="disabled")
		self.colormenu.entryconfig("Histogram", state="disabled")
		self.colormenu.entryconfig("灰階", state="disabled")
		self.colormenu.entryconfig("黑白(level)", state="disabled")
		self.colormenu.entryconfig("透明", state="disabled")
		self.colormenu.entryconfig("負片", state="disabled")
		self.colormenu.entryconfig("Threshold", state="disabled")
		self.colormenu.entryconfig("Gamma Correction", state="disabled")
		self.colormenu.entryconfig("Otsu's Threshold", state="disabled")
		self.colormenu.entryconfig("Kullback", state="disabled")
		self.colormenu.entryconfig("Contrast stretching", state="disabled")
		self.colormenu.entryconfig("Bit-plane Slicing", state="disabled")
		self.colormenu.entryconfig("Histogram Equalization", state="disabled")
		self.colormenu.entryconfig("Histogram Specification", state="disabled")
		self.colormenu.entryconfig("Connected Components", state="disabled")
		self.filtermenu.entryconfig("Outlier", state="disabled")
		self.filtermenu.entryconfig("Mean & Median", state="disabled")
		self.filtermenu.entryconfig("Pseudo Median", state="disabled")
		self.filtermenu.entryconfig("Highpass", state="disabled")
		self.filtermenu.entryconfig("Edge Crispening", state="disabled")
		self.filtermenu.entryconfig("High-boost", state="disabled")
		self.filtermenu.entryconfig("Roberts & Sobel & Prewitt", state="disabled")
		self.filtermenu.entryconfig("Canny", state="disabled")

		#bind shortcut keys
		self.parent.bind_all("<Control-o>", self.Open_File)
		self.parent.bind_all("<Control-b> <Key-2>", self.Bouncing_ball)
		self.parent.bind_all("<Control-v>", self.Video)
		self.parent.bind_all("<Control-h> <Key-d>", self.Hair)
		
		
		#Frame
		#self.canvas = tk.Canvas(width = 1000, height = 920)
		
		self.frmL = tk.Frame(width = 1000, height = 870)
		self.frmB = tk.Frame(width = 1000, height = 30)
		self.frmR = tk.Frame(width = 400, height = 900, highlightbackground = "black", highlightthickness = 1)
		self.frmL.grid_propagate(0) #fix frame
		self.frmB.grid_propagate(0)
		self.frmR.grid_propagate(0)

		#Raw Image
		self.raw_label_img = tk.Canvas(self.frmL)
		self.raw_label_img.grid(column = 0, row = 0, ipadx = 5, pady = 5)
		#Red Image
		self.red_label_img = tk.Canvas(self.frmL)
		#Green Image
		self.green_label_img = tk.Canvas(self.frmL)
		#Blue Image
		self.blue_label_img = tk.Canvas(self.frmL)
		#header field
		self.header_tree = ttk.Treeview(self.frmR, show="tree", columns=('content'), height = 16)
		self.header_tree.column("content", width = 100, anchor = 'center', stretch = False)
		#palette image
		self.palette_label_img = tk.Canvas(self.frmL)
		#Filename Label
		self.filename_label = tk.Label(self.frmL)
		#Height x Width Label
		self.h_w_label = tk.Label(self.frmL)
		#Bottom image pixel and color
		self.p_i_label = tk.Label(self.frmB)
		

		self.frmL.grid(column = 0, row = 0)
		self.frmB.grid(column = 0, row = 1)
		self.frmR.grid(column = 1, row = 0,  rowspan = 2)

		self.parent.mainloop()

	#Read PCX File
	def Open_File(self, event = None):
		self.filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("PCX","*.PCX, *.pcx"),("all files","*.*")))
		if self.filename != '':
			#Clear Image, Palette
			self.palette_label_img.grid_forget()
			self.Clear_Image()
			self.img = self.Read_File(self.filename)
			self.original_img = self.img.copy()
			self.show_image()
			
			self.show_image_information()
			try:
				self.show_palette()
			except:
				pass
			self.Bind_Image()

			self.filemenu.entryconfig("Save (Huffman)", state="normal")
			self.editmenu.entryconfig("放大", state="normal")
			self.editmenu.entryconfig("縮小", state="normal")
			self.editmenu.entryconfig("旋轉", state="normal")
			self.editmenu.entryconfig("Cut", state="normal")
			self.editmenu.entryconfig("魔術棒", state="normal")
			self.colormenu.entryconfig("RGB", state="normal")
			self.colormenu.entryconfig("Histogram", state="normal")
			self.colormenu.entryconfig("灰階", state="normal")
			self.colormenu.entryconfig("黑白(level)", state="normal")
			self.colormenu.entryconfig("透明", state="normal")
			self.colormenu.entryconfig("負片", state="normal")
			self.colormenu.entryconfig("Threshold", state="normal")
			self.colormenu.entryconfig("Gamma Correction", state="normal")
			self.colormenu.entryconfig("Otsu's Threshold", state="normal")
			self.colormenu.entryconfig("Kullback", state="normal")
			self.colormenu.entryconfig("Contrast stretching", state="normal")
			self.colormenu.entryconfig("Bit-plane Slicing", state="normal")
			self.colormenu.entryconfig("Histogram Equalization", state="normal")
			self.colormenu.entryconfig("Histogram Specification", state="normal")
			self.colormenu.entryconfig("Connected Components", state="normal")
			self.filtermenu.entryconfig("Outlier", state="normal")
			self.filtermenu.entryconfig("Mean & Median", state="normal")
			self.filtermenu.entryconfig("Pseudo Median", state="normal")
			self.filtermenu.entryconfig("Highpass", state="normal")
			self.filtermenu.entryconfig("Edge Crispening", state="normal")
			self.filtermenu.entryconfig("High-boost", state="normal")
			self.filtermenu.entryconfig("Roberts & Sobel & Prewitt", state="normal")
			self.filtermenu.entryconfig("Canny", state="normal")
			
			self.Bind_Shortcut_key()


	def Read_File(self, filename):
		f = open(filename, 'rb') #rb = read bytes
		h = f.read(128)
		if h[0] != 10:
			messagebox.showerror("Error", "File Type Not PCX") #Error not pcx file
		header = Header(h)
		XSize = header.XEnd - header.XStart + 1
		YSize = header.YEnd - header.YStart + 1

		if (header.BitsPerPixel == 1) and (header.NumBitPlanes == 1): #Monochrome
			data = f.read()
			img = UI.BW_image(self, header, data)
		elif (header.Version == 5) and (header.BitsPerPixel == 8) and (header.NumBitPlanes == 3):
			data = f.read()
			img = UI._24b_image(self, header, data)
		elif (header.Version == 5) and (header.BitsPerPixel == 8) and (header.NumBitPlanes == 1): #version 5 palette is at back
			data = f.read()
			data = data[0:len(data) - 769]
			f.seek(-768, 2) #2 = back
			s = f.read(768)
			self.Extend_Palette = UI._Extend_Palette(self, s)
			img = UI._256_image(self, header, data)

		if(filename == self.filename):
			self.show_header(header)
		return img

	#放大 複製版
	def Magnify_Duplicate_Image(self, event = None):
		new_h = self.img.shape[0] * 2
		new_w = self.img.shape[1] * 2

		progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
		progressbar.grid(column = 2, row = 0, sticky = tk.E)
		progressbar["value"] = 0
		progressbar["maximum"] = self.img.shape[0]
		if(len(self.img.shape) == 3):
			new_img = np.zeros((new_h, new_w, 3), dtype=np.uint8)
		else:
			new_img = np.zeros((new_h, new_w), dtype=np.uint8)
		for i in range(new_h):
			for j in range(new_w):
				if(i % 2 == 0):
					if(j % 2 == 0):
						new_img[i, j] = self.img[int(i/2), int(j/2)]
					else:
						new_img[i, j] = self.img[int(i/2), int(j/2-1)]
				else:
					if(j % 2 == 0):
						new_img[i, j] = self.img[int(i/2-1), int(j/2)]
					else:
						new_img[i, j] = self.img[int(i/2-1), int(j/2-1)]
			progressbar["value"] += 0.5
			progressbar.update()
		progressbar["value"] = self.img.shape[0]
		progressbar.update()
		try:
			progressbar.grid_forget()
		except:
			pass

		#Clear the image
		self.Clear_Image()
		self.img = new_img
		self.show_image_information()
		self.show_image()
		self.Bind_Image()

	#放大 雙線性插值
	def Magnify_Interpolation_Image(self, event = None):
		new_h = self.img.shape[0] * 2
		new_w = self.img.shape[1] * 2
		if(len(self.img.shape) == 3):
			new_img = np.zeros((new_h, new_w, 3), dtype=np.uint8)
		else:
			new_img = np.zeros((new_h, new_w), dtype=np.uint8)
		scale_x = float(self.img.shape[1]) / new_w
		scale_y = float(self.img.shape[0]) / new_h

		progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
		progressbar.grid(column = 2, row = 0, sticky = tk.E)
		progressbar["value"] = 0
		progressbar["maximum"] = self.img.shape[0]
		
		for i in range(new_h):
			for j in range(new_w):
				raw_x = (j + 0.5) * scale_x - 0.5
				raw_y = (i + 0.5) * scale_y - 0.5
				raw_x_0 = int(np.floor(raw_x))
				raw_y_0 = int(np.floor(raw_y))
				raw_x_1 = min(raw_x_0 + 1, self.img.shape[1] - 1)
				raw_y_1 = min(raw_y_0 + 1, self.img.shape[0] - 1)
				value_0 = (raw_x_1 - raw_x) * self.img[raw_y_0, raw_x_0] + (raw_x - raw_x_0) * self.img[raw_y_0, raw_x_1]
				value_1 = (raw_x_1 - raw_x) * self.img[raw_y_1, raw_x_0] + (raw_x - raw_x_0) * self.img[raw_y_1, raw_x_1]
				new_img[i, j] = (raw_y_1 - raw_y) * value_0 + (raw_y - raw_y_0) * value_1
			progressbar["value"] += 0.5
			progressbar.update()
		progressbar["value"] = self.img.shape[0]
		progressbar.update()
		try:
			progressbar.grid_forget()
		except:
			pass
		self.img = new_img
		
		#Clear the image
		self.Clear_Image()
		self.show_image_information()
		
		self.show_image()
		self.Bind_Image()

	#縮小 刪除法
	def Minify_Delete_Image(self, event = None):
		if(self.img.shape[0] / 2 < 1 or self.img.shape[1] / 2 < 1):
			messagebox.showerror("Error", "無法再縮小")
		else:
			#Clear the image
			self.Clear_Image()
			
			new_h = int(self.img.shape[0] / 2)
			new_w = int(self.img.shape[1] / 2)
			if(len(self.img.shape) == 3):
				new_img = np.zeros((new_h, new_w, 3), dtype=np.uint8)
			else:
				new_img = np.zeros((new_h, new_w), dtype=np.uint8)
			for i in range(new_w):
				for j in range(new_h):
					new_img[j, i] = self.img[int(j*2), int(i*2)]
							
			self.img = new_img
			self.show_image_information()
			self.show_image()
			self.Bind_Image()

	#縮小 平均法
	def Minify_Mean_Image(self, event = None):
		if(self.img.shape[0] / 2 < 0 or self.img.shape[1] / 2 < 0):
			messagebox.showerror("Error", "無法再縮小")
		else:
			#Clear the image
			self.Clear_Image()
			
			new_h = int(self.img.shape[0] / 2)
			new_w = int(self.img.shape[1] / 2)
			if(len(self.img.shape) == 3):
				new_img = np.zeros((new_h, new_w, 3), dtype=np.uint8)
				for i in range(new_w):
					for j in range(new_h):
						r = round((int(self.img[j*2,i*2,0]) + int(self.img[j*2+1,i*2,0]) + int(self.img[j*2,i*2+1,0]) + int(self.img[j*2+1,i*2+1,0]))/4)
						g = round((int(self.img[j*2,i*2,1]) + int(self.img[j*2+1,i*2,1]) + int(self.img[j*2,i*2+1,1]) + int(self.img[j*2+1,i*2+1,1]))/4)
						b = round((int(self.img[j*2,i*2,2]) + int(self.img[j*2+1,i*2,2]) + int(self.img[j*2,i*2+1,2]) + int(self.img[j*2+1,i*2+1,2]))/4)
						new_img[j, i] = (r, g, b)
			else:
				new_img = np.zeros((new_h, new_w), dtype=np.uint8)
				for i in range(new_w):
					for j in range(new_h):
						value = round((int(self.img[j*2,i*2]) + int(self.img[j*2+1,i*2]) + int(self.img[j*2,i*2+1]) + int(self.img[j*2+1,i*2+1])) / 4)
						new_img[j, i] = value
							
			self.img = new_img
			self.show_image_information()
			self.show_image()
			self.Bind_Image()

	#彩色 -> 灰階
	def Color_To_Gray(self, event = None):
		if(len(self.img.shape) == 3):
			#Clear the image
			self.Clear_Image()

			new_img = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					new_img[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
			self.img = new_img
			self.show_image_information()
			self.show_image()
			self.Bind_Image()
			self.colormenu.entryconfig("RGB", state="disabled")
			self.colormenu.entryconfig("灰階", state="disabled")

	#不同灰階 1~7
	def Gray_To_BW(self, event = None):
		#Clear the image
		self.Clear_Image()
		self.show_image_information()
		self.show_image()
		self.trans_label = tk.Label(self.frmL, text = "灰階程度(1~7)，1 = 黑白")
		self.trans_box = tk.Spinbox(self.frmL, from_ = 1, to = 7, command = self.Grey_Level)
		self.trans_box.bind("<Return>", self.Grey_Level)
		self.trans_button = tk.Button(self.frmL, text="修改", command = self.Close_window)
		if(len(self.img.shape) == 3):
			self.red_image = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[1]):
				for j in range(self.img.shape[0]):
					self.red_image[j, i] = 0.3 * int(self.img[j, i, 0]) + 0.3 * int(self.img[j, i, 1]) + 0.4 * int(self.img[j, i, 2])
		else:
			self.red_image = self.img.copy()
		img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.trans_label.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.W)
		self.trans_box.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.E)
		self.trans_button.grid(row = 2, column = 2, padx = 10, pady = 10)
		self.Bind_Image()

	def Grey_Level(self, event = None):
		gray_level = self.trans_box.get()
		if(int(gray_level) >= 1 and int(gray_level) <= 7):
			
			try:
				self.red_label_img.delete('all')
			except:
				pass
			try:
				self.red_label_img.grid_forget() 
			except:
				pass
			if(len(self.img.shape) == 3):
				self.red_image = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
				for i in range(self.img.shape[1]):
					for j in range(self.img.shape[0]):
						self.red_image[j, i] = 0.3 * int(self.img[j, i, 0]) + 0.3 * int(self.img[j, i, 1]) + 0.4 * int(self.img[j, i, 2])
			else:
				self.red_image = self.img.copy()
			p2 = pow(2, int(gray_level))
			threshold = 256 / p2
			value = 255 / (p2 - 1)
			for n in range(p2):
				min_img = self.red_image >= (n * threshold)
				max_img = self.red_image < ((n + 1) * threshold)
				com = min_img & max_img
				self.red_image[np.where(com == True)] = n * value

			img_PIL = Image.fromarray(self.red_image, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
			self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
			self.red_label_img.image = img_PIL
			self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)

		else:
			messagebox.showerror("Error", "請輸入1 ~ 7的數值")
		self.Bind_Image()

	def Close_window(self):
		self.img = self.red_image
		self.colormenu.entryconfig("RGB", state="disabled")
		self.colormenu.entryconfig("灰階", state="disabled")
		self.colormenu.entryconfig("Otsu's Threshold", state="disabled")
		self.colormenu.entryconfig("Kullback", state="disabled")
		self.colormenu.entryconfig("Contrast stretching", state="disabled")
		self.colormenu.entryconfig("Bit-plane Slicing", state="disabled")
		self.colormenu.entryconfig("Histogram Equalization", state="disabled")
		self.colormenu.entryconfig("Histogram Specification", state="disabled")
		self.Clear_Image()
		self.show_image()
		self.show_image_information()
		self.Bind_Image()

	#Rotation with hole
	def Rotation_Version_1(self, event = None):
		self.Clear_Image()
		self.show_image()
		self.show_image_information()
		self.trans_label = tk.Label(self.frmL, text = "旋轉角度，-180~180")
		self.trans_box = tk.Spinbox(self.frmL, from_ = -180, to = 180, command = self.Rotation_1)
		self.trans_box.bind("<Return>", self.Rotation_1)
		self.trans_button = tk.Button(self.frmL, text="修改", command = self.Rotation_Version_Close_1)
		self.trans_label.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.W)
		self.trans_box.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.E)
		self.trans_button.grid(row = 2, column = 2, padx = 10, pady = 10)
		self.red_image = self.img.copy()
		if(len(self.red_image.shape) == 3):
			img_PIL = Image.fromarray(self.red_image, 'RGB')
		else:
			img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.red_label_img = tk.Canvas(self.frmL, width=self.img.shape[1], height=self.img.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
	
	def Rotation_1(self, event = None):
		r = int(self.trans_box.get())
		try:	
			self.red_label_img.delete('all')
		except:
			pass
		try:	
			self.red_label_img.grid_forget() 
		except:
			pass
		if(r >= -180 and r <= 180):
			height = int(self.img.shape[0] / 2)
			width = int(self.img.shape[1] / 2)
			r_x_1, r_y_1 = self.rotation_x_y(-height, -width, r, 1)
			r_x_2, r_y_2 = self.rotation_x_y(-height, width, r, 1)
			r_x_3, r_y_3 = self.rotation_x_y(height, -width, r, 1)
			r_x_4, r_y_4 = self.rotation_x_y(height, width, r, 1)
			new_height = max(r_x_1, r_x_2, r_x_3, r_x_4) - min(r_x_1, r_x_2, r_x_3, r_x_4)
			new_width = max(r_y_1, r_y_2, r_y_3, r_y_4) - min(r_y_1, r_y_2, r_y_3, r_y_4)
			if(len(self.img.shape) == 3):
				self.red_image = np.zeros((new_height, new_width, 3), dtype=np.uint8)
			else:
				self.red_image = np.zeros((new_height, new_width), dtype=np.uint8)
			for i in range(0, int(self.img.shape[0])):
				for l in range(0, int(self.img.shape[1])):
					r_x, r_y = self.rotation_x_y(i - int(self.img.shape[0] / 2), l - int(self.img.shape[1] / 2), r, 1)
					self.red_image[r_x + int(new_height / 2) - 1, r_y + int(new_width / 2) - 1] = self.img[i, l]
			if(len(self.red_image.shape) == 3):
				img_PIL = Image.fromarray(self.red_image, 'RGB')
			else:
				img_PIL = Image.fromarray(self.red_image, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
			self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
			self.red_label_img.image = img_PIL
			self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
			self.Bind_Image()
		else:
			messagebox.showerror("Error", "請輸入-180 ~ 180的數值")

	def Rotation_Version_Close_1(self):
		self.img = self.red_image
		self.Clear_Image()
		self.show_image()
		self.show_image_information()
		self.Bind_Image()

	#Rotation without hole
	def Rotation_Version_2(self, event = None):
		self.Clear_Image()
		self.show_image()
		self.show_image_information()
		self.trans_label = tk.Label(self.frmL, text = "旋轉角度，-180~180")
		self.trans_box = tk.Spinbox(self.frmL, from_ = -180, to = 180, command = self.Rotation_2)
		self.trans_box.bind("<Return>", self.Rotation_2)
		self.trans_button = tk.Button(self.frmL, text="修改", command = self.Rotation_Version_Close_2)
		self.trans_label.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.W)
		self.trans_box.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.E)
		self.trans_button.grid(row = 2, column = 2, padx = 10, pady = 10)
		self.red_image = self.img.copy()
		if(len(self.red_image.shape) == 3):
			img_PIL = Image.fromarray(self.red_image, 'RGB')
		else:
			img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.red_label_img = tk.Canvas(self.frmL, width=self.img.shape[1], height=self.img.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
	
	def Rotation_2(self, event = None):
		r = int(self.trans_box.get())
		try:	
			self.red_label_img.delete('all')
		except:
			pass
		try:	
			self.red_label_img.grid_forget() 
		except:
			pass
		if(r >= -180 and r <= 180):
			height = int(self.img.shape[0] / 2)
			width = int(self.img.shape[1] / 2)
			r_x_1, r_y_1 = self.rotation_x_y(-height, -width, r, 1)
			r_x_2, r_y_2 = self.rotation_x_y(-height, width, r, 1)
			r_x_3, r_y_3 = self.rotation_x_y(height, -width, r, 1)
			r_x_4, r_y_4 = self.rotation_x_y(height, width, r, 1)
			new_height = max(r_x_1, r_x_2, r_x_3, r_x_4) - min(r_x_1, r_x_2, r_x_3, r_x_4)
			new_width = max(r_y_1, r_y_2, r_y_3, r_y_4) - min(r_y_1, r_y_2, r_y_3, r_y_4)
			if(len(self.img.shape) == 3):
				self.red_image = np.zeros((new_height, new_width, 3), dtype=np.uint8)
			else:
				self.red_image = np.zeros((new_height, new_width), dtype=np.uint8)
			for i in range(0, new_height):
				for l in range(0, new_width):
					r_x, r_y = self.rotation_x_y(i - int(new_height / 2), l - int(new_width / 2), r, 2)
					r_x += height - 1
					r_y += width - 1
					if((r_x >= 0 and r_x < self.img.shape[0]) and (r_y >= 0 and r_y < self.img.shape[1])):
						self.red_image[i, l] = self.img[r_x, r_y]
			if(len(self.red_image.shape) == 3):
				img_PIL = Image.fromarray(self.red_image, 'RGB')
			else:
				img_PIL = Image.fromarray(self.red_image, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
			self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
			self.red_label_img.image = img_PIL
			self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
			self.Bind_Image()
		else:
			messagebox.showerror("Error", "請輸入-180 ~ 180的數值")

	def Rotation_Version_Close_2(self):
		self.img = self.red_image
		self.Clear_Image()
		self.show_image()
		self.show_image_information()
		self.Bind_Image()

	#Rotation X, Y
	def rotation_x_y(self, x, y, r, version):
		r = math.radians(r)
		if(version == 1):
			r_x = round(x * math.cos(r) - y * math.sin(r))
			r_y = round(x * math.sin(r) + y * math.cos(r))
		elif(version == 2):
			r_x = round(x * math.cos(r) + y * math.sin(r))
			r_y = round(x * -(math.sin(r)) + y * math.cos(r))
		return (r_x, r_y)

	#負片
	def Invert_Image(self, event = None):
		#Clear the image
		self.Clear_Image()

		self.img = 255 - self.img
		self.show_image_information()
		self.show_image()
		self.Bind_Image()

	#User defined Threshold
	def Threshold(self, event = None):
		#Clear the image
		self.Clear_Image()

		self.trans_label = tk.Label(self.frmL, text = "Threshold : ")
		self.trans_box = tk.Spinbox(self.frmL, from_ = 0, to = 256, command = self.Show_threshold)
		self.trans_box.bind("<Return>", self.Show_threshold)
		if(len(self.img.shape) == 3):
			self.red_image = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[1]):
				for j in range(self.img.shape[0]):
					self.red_image[j, i] = 0.3 * int(self.img[j, i, 0]) + 0.3 * int(self.img[j, i, 1]) + 0.4 * int(self.img[j, i, 2])
			self.img = self.red_image
		else:
			self.red_image = self.img.copy()
		img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.trans_label.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.W)
		self.trans_box.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.E)
		self.show_image_information()
		self.show_image()
		self.Bind_Image()
		self.colormenu.entryconfig("RGB", state="disabled")
		self.colormenu.entryconfig("灰階", state="disabled")

	def Show_threshold(self, event = None):
		threshold = int(self.trans_box.get())
		try:	
			self.red_label_img.delete('all')
		except:
			pass
		try:	
			self.red_label_img.grid_forget() 
		except:
			pass
		if(0 <= threshold < 256):
			self.red_image = self.img.copy()
			self.red_image[self.img >= threshold] = 255
			self.red_image[self.img < threshold] = 0
			img_PIL = Image.fromarray(self.red_image, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
			self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
			self.red_label_img.image = img_PIL
			self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
			self.trans_label.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.W)
			self.trans_box.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.E)
			self.Bind_Image()
		else:
			self.red_image = self.img.copy()
			img_PIL = Image.fromarray(self.red_image, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
			self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
			self.red_label_img.image = img_PIL
			self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
			self.trans_label.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.W)
			self.trans_box.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.E)
			self.Bind_Image()
			messagebox.showerror("Error", "請輸入0 ~ 255的數值")

	#顯示 Histogram
	def Histogram_Image(self, event = None):
		#Clear the image
		self.Clear_Image()
		self.show_image()
		self.show_image_information()
		if(len(self.img.shape) == 3):
			self.trans_box = ttk.Combobox(self.frmL, value = ['R', 'G', 'B', 'RGB', "Grey"])
		else:
			self.trans_box = ttk.Combobox(self.frmL, value = ["Grey"])
		self.trans_box.bind("<<ComboboxSelected>>", self.Show_Histrogram)
		self.trans_box.grid(row = 2, column = 1, padx = 10, pady = 10)
		self.Bind_Image()

	def Show_Histrogram(self, event):
		color = event.widget.get()
		if(len(self.img.shape) == 3):
			new_img = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[1]):
				for j in range(self.img.shape[0]):
					new_img[j, i] = 0.3 * int(self.img[j, i, 0]) + 0.3 * int(self.img[j, i, 1]) + 0.4 * int(self.img[j, i, 2])
			red_h = [0] * 256
			green_h = [0] * 256
			blue_h = [0] * 256
			for i in range(int(self.img.shape[0])):
				for l in range(int(self.img.shape[1])):
					red_h[self.img[i, l, 0]] += 1
					green_h[self.img[i, l, 1]] += 1
					blue_h[self.img[i, l, 2]] += 1
		else:
			new_img = self.img.copy()
		
		grey_h = [0] * 256
		for i in range(int(new_img.shape[0])):
			for l in range(int(new_img.shape[1])):
				grey_h[new_img[i, l]] += 1

		f = Figure(figsize=(5,3), dpi=70)
		a = f.add_subplot(111)
		if(color == 'R'):
			a.bar(list(range(0, 256)), red_h, color = 'r', align='center')
		elif(color == 'G'):
			a.bar(list(range(0, 256)), green_h, color = 'g', align='center')
		elif(color == 'B'):
			a.bar(list(range(0, 256)), blue_h, color = 'blue', align='center')
		elif(color == "RGB"):
			a.bar(list(range(0, 256)), red_h, color = 'r', align='center')
			a.bar(list(range(0, 256)), green_h, color = 'g', align='center')
			a.bar(list(range(0, 256)), blue_h, color = 'blue', align='center')
		elif(color == 'Grey'):
			a.bar(list(range(0, 256)), grey_h, color = 'black', align='center')
		try:	
			self.canvas_1.get_tk_widget().grid_forget()
		except:
			pass
		self.canvas_1 = FigureCanvasTkAgg(f, self.frmL)
		self.canvas_1.draw()
		self.canvas_1.get_tk_widget().grid(column = 1, row = 1)

	#切割
	def Cut_Oval_Image(self, event = None):
		#Clear the image
		self.Clear_Image()
		#self.show_image()
		if(len(self.img.shape) == 3):
			img_PIL = Image.fromarray(self.img, 'RGB')
		else:
			img_PIL = Image.fromarray(self.img, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.raw_label_img = tk.Canvas(self.frmL, width=self.img.shape[1], height=self.img.shape[0], cursor = 'tcross')
		self.raw_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.raw_label_img.image = img_PIL
		self.raw_label_img.grid(column = 0, row = 1, padx = 50, pady = 20)
		self.show_image_information()
		self.shape = self.raw_label_img.create_oval
		self.raw_label_img.bind("<Button-1>", self.OnStart)
		self.raw_label_img.bind("<B1-Motion>", self.OnGrow)
		self.raw_label_img.bind("<ButtonRelease-1>", self.Add_Graph)

	def Cut_Rectangle_Image(self, event = None):
		#Clear the image
		self.Clear_Image()
		#self.show_image()
		if(len(self.img.shape) == 3):
			img_PIL = Image.fromarray(self.img, 'RGB')
		else:
			img_PIL = Image.fromarray(self.img, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.raw_label_img = tk.Canvas(self.frmL, width=self.img.shape[1], height=self.img.shape[0], cursor = 'tcross')
		self.raw_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.raw_label_img.image = img_PIL
		self.raw_label_img.grid(column = 0, row = 1, padx = 50, pady = 20)
		self.show_image_information()
		self.shape = self.raw_label_img.create_rectangle
		self.raw_label_img.bind("<Button-1>", self.OnStart)
		self.raw_label_img.bind("<B1-Motion>", self.OnGrow)
		self.raw_label_img.bind("<ButtonRelease-1>", self.Add_Graph)

	def OnStart(self, event):
		self.start = event

	def OnGrow(self, event):
		canvas = event.widget
		if self.drawn:
			canvas.delete(self.drawn)
		if(self.shape == self.raw_label_img.create_oval):
			if(abs(event.x - self.start.x) > abs(event.y - self.start.y)):
				if(event.y > self.start.y):
					event.y = self.start.y + abs(event.x - self.start.x)
				else:
					event.y = self.start.y - abs(event.x - self.start.x)
			else:
				if(event.x > self.start.x):
					event.x = self.start.x + abs(event.y - self.start.y)
				else:
					event.x = self.start.x - abs(event.y - self.start.y)
		objectId = self.shape(self.start.x, self.start.y, event.x, event.y, dash = (5, 1), outline = "red")
		self.drawn = objectId
	
	def Add_Graph(self, event):
		canvas = event.widget
		if self.drawn:
			canvas.delete(self.drawn)
		if(self.shape == self.raw_label_img.create_oval):
			if(abs(event.x - self.start.x) > abs(event.y - self.start.y)):
				if(event.y > self.start.y):
					event.y = self.start.y + abs(event.x - self.start.x)
				else:
					event.y = self.start.y - abs(event.x - self.start.x)
			else:
				if(event.x > self.start.x):
					event.x = self.start.x + abs(event.y - self.start.y)
				else:
					event.x = self.start.x - abs(event.y - self.start.y)
		objectId = self.shape(self.start.x, self.start.y, event.x, event.y, outline = "red")
		self.drawn = objectId

		if(self.start.x > event.x):
			s_x = event.x
			e_x = self.start.x
		else:
			s_x = self.start.x
			e_x = event.x
		if(self.start.y > event.y):
			s_y = event.y
			e_y = self.start.y
		else:
			s_y = self.start.y
			e_y = event.y
		if(e_x > self.img.shape[1]): e_x = self.img.shape[1]
		if(e_y > self.img.shape[0]): e_y = self.img.shape[0]
		if(s_x < 0): s_x = 0
		if(s_y < 0): s_y = 0
		if(len(self.img.shape) == 3):
			self.red_image = np.full((self.img.shape[0], self.img.shape[1], 3), 255, dtype=np.uint8)
		else:
			self.red_image = np.full((self.img.shape[0], self.img.shape[1]), 255, dtype=np.uint8)
		if(self.shape == self.raw_label_img.create_oval):
			center = (int((e_x + s_x) / 2), int((e_y + s_y) / 2))
			circle_size = int((e_y - s_y) / 2)

			for i in range(s_x, e_x):
				for l in range(s_y, e_y):
					x_y_long = pow(pow(center[0] - i, 2) + pow(center[1] - l, 2), 0.5)
					if(x_y_long <= circle_size):
						self.red_image[l,i] = self.img[l,i]
		else:
			for i in range(s_x, e_x):
				for l in range(s_y, e_y):
					self.red_image[l, i] = self.img[l,i]
		if(len(self.img.shape) == 3):
			img_PIL = Image.fromarray(self.red_image, 'RGB')
		else:
			img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)

		try:	
			self.red_label_img.delete('all')
		except:
			pass
		try:	
			self.red_label_img.grid_forget() 
		except:
			pass
		self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.Bind_Image()

	#魔術棒
	def Magic_Wand(self, event = None):
		#Clear the image
		self.Clear_Image()
		#self.show_image()
		if(len(self.img.shape) == 3):
			img_PIL = Image.fromarray(self.img, 'RGB')
		else:
			img_PIL = Image.fromarray(self.img, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.raw_label_img = tk.Canvas(self.frmL, width=self.img.shape[1], height=self.img.shape[0], cursor = 'tcross')
		self.raw_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.raw_label_img.image = img_PIL
		self.raw_label_img.grid(column = 0, row = 1, padx = 50, pady = 20)
		self.show_image_information()

		self.red_image = self.img.copy()
		if(len(self.red_image.shape) == 3):
			img_PIL = Image.fromarray(self.red_image, 'RGB')
		else:
			img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.show_image()
		self.red_label_img = tk.Canvas(self.frmL, width=self.img.shape[1], height=self.img.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.red_label_img.bind("<Button-1>", self.MagicStart_Point)
		self.trans_button = tk.Button(self.frmL, text="清空", command = self.Clear_Magic)
		self.trans_button.grid(row = 2, column = 1, padx = 10, pady = 10)
	
	def MagicStart_Point(self, event):
		self.start = event
		self.red_label_img.create_line(self.start.x - 3, self.start.y - 3, self.start.x + 4, self.start.y + 4, fill = "red")
		self.red_label_img.create_line(self.start.x - 3, self.start.y + 4, self.start.x + 4, self.start.y - 4, fill = "red")
		self.red_label_img.unbind("<Button-1>")
		self.red_label_img.bind("<Button-1>", self.MagicStart)

	def MagicStart(self, event):
		self.magic_start = event
		self.red_label_img.create_line(self.start.x - 3, self.start.y - 3, self.start.x + 4, self.start.y + 4, fill = "red")
		self.red_label_img.create_line(self.start.x - 3, self.start.y + 4, self.start.x + 4, self.start.y - 4, fill = "red")
		self.red_label_img.bind("<B1-Motion>", self.MagicMove)
		

	def MagicMove(self, event):
		self.red_label_img.bind("<ButtonRelease-1>", self.MagicEnd)
		
		try:	
			self.red_label_img.delete('all')
		except:
			pass
		try:	
			self.red_label_img.grid_forget() 
		except:
			pass
		
		if(self.magic_start.x > event.x):
			s_x = self.start.x - (self.magic_start.x - event.x)
		else:
			s_x = self.start.x + (event.x - self.magic_start.x)
		if(self.magic_start.y > event.y):
			s_y = self.start.y - (self.magic_start.y - event.y)
		else:
			s_y = self.start.y + (event.y - self.magic_start.y)
		e_x = s_x + 5
		e_y = s_y + 5
		s_x -= 5
		s_y -= 5
		if(s_x > self.img.shape[1]): s_x = self.img.shape[1] - 1
		if(s_y > self.img.shape[0]): s_y = self.img.shape[0] - 1
		if(s_x < 0): s_x = 0
		if(s_y < 0): s_y = 0
		if(e_x > self.img.shape[1]): e_x = self.img.shape[1] - 1
		if(e_y > self.img.shape[0]): e_y = self.img.shape[0] - 1
		if(e_x < 0): e_x = 0
		if(e_y < 0): e_y = 0
		if(len(self.img.shape) == 3):
			for i in range(s_x, e_x):
				for l in range(s_y, e_y):
					c_x = event.x + i - s_x
					c_y = event.y + l - s_y
					if(c_x >= self.img.shape[1]):
						c_x = self.img.shape[1] - 1
					elif(c_x < 0):
						c_x = 0
					if(c_y >= self.img.shape[0]):
						c_y = self.img.shape[0] - 1
					elif(c_y < 0):
						c_y = 0
					self.red_image[c_y, c_x] = self.img[l, i]
			img_PIL = Image.fromarray(self.red_image, 'RGB')
		else:
			for i in range(s_x, e_x):
				for l in range(s_y, e_y):
					c_x = event.x + i - s_x
					c_y = event.y + l - s_y
					if(c_x >= self.img.shape[1]):
						c_x = self.img.shape[1] - 1
					elif(c_x < 0):
						c_x = 0
					if(c_y >= self.img.shape[0]):
						c_y = self.img.shape[0] - 1
					elif(c_y < 0):
						c_y = 0
					self.red_image[c_y, c_x] = self.img[l, i]
			img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.show_image()
		self.red_label_img = tk.Canvas(self.frmL, width=self.img.shape[1], height=self.img.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.red_label_img.create_line(self.start.x - 4, self.start.y - 4, self.start.x + 4, self.start.y + 4, fill = "red")
		self.red_label_img.create_line(self.start.x - 4, self.start.y + 4, self.start.x + 4, self.start.y - 4, fill = "red")

	def MagicEnd(self, event):
		#self.show_image()
		self.red_label_img.create_line(self.start.x - 4, self.start.y - 4, self.start.x + 4, self.start.y + 4, fill = "red")
		self.red_label_img.create_line(self.start.x - 4, self.start.y + 4, self.start.x + 4, self.start.y - 4, fill = "red")
		self.Bind_Image()
		self.red_label_img.bind("<Button-1>", self.MagicStart)

	def Clear_Magic(self):
		try:	
			self.red_label_img.delete('all')
		except:
			pass
		try:	
			self.red_label_img.grid_forget() 
		except:
			pass
		self.red_image = self.img.copy()
		if(len(self.red_image.shape) == 3):
			img_PIL = Image.fromarray(self.red_image, 'RGB')
		else:
			img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.show_image()
		self.red_label_img = tk.Canvas(self.frmL, width=self.img.shape[1], height=self.img.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.red_label_img.bind("<Button-1>", self.MagicStart_Point)
		

	#透明度 兩張照片
	def Transparent_Image(self, event = None):
		filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("PCX","*.PCX, *.pcx"),("all files","*.*")))
		if filename != '':
			#Clear the image
			self.Clear_Image()
			self.show_image()
			self.show_image_information()
			
			self.red_image = self.Read_File(filename)
			img_PIL = Image.fromarray(self.red_image, 'RGB')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			self.red_label_img = tk.Canvas(self.frmL, width = self.red_image.shape[1], height = self.red_image.shape[0])
			self.red_label_img.create_image(0, 0, image = img_PIL, anchor = tk.N + tk.W)
			self.red_label_img.image = img_PIL
			self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
			self.trans_label = tk.Label(self.frmL, text = "透明值，0~1")
			self.trans_box = tk.Spinbox(self.frmL, from_ = 0, to = 1, increment = 0.1)
			self.trans_button = tk.Button(self.frmL, text="確定", command = self.Show_Transparent_Image)
			self.trans_label.grid(row = 2, column = 1, padx=10, pady=10, sticky = tk.W)
			self.trans_box.grid(row = 2, column = 1, padx=10, pady=10, sticky = tk.E)
			self.trans_button.grid(row = 2, column = 2, padx=10, pady=10)
			self.Bind_Image()

	def Show_Transparent_Image(self):
		try:	
			self.green_label_img.delete('all')
		except:
			pass
		try:	
			self.green_label_img.grid_forget()
		except:
			pass
		value = float(self.trans_box.get())
		if(value >= 0 and value <= 1):
			height = int(max(self.img.shape[0], self.red_image.shape[0]))
			width = int(max(self.img.shape[1], self.red_image.shape[1]))
			self.green_image = np.zeros((height, width, 3), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for l in range(self.img.shape[1]):
					self.green_image[i, l] = value * self.img[i, l]
			for i in range(self.red_image.shape[0]):
				for l in range(self.red_image.shape[1]):
					self.green_image[i, l] = self.green_image[i, l] + (1 - value) * self.red_image[i, l]		
			img_PIL = Image.fromarray(self.green_image, 'RGB')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			self.green_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
			self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
			self.green_label_img.image = img_PIL
			self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)
		else:	
			messagebox.showerror("Error", "請輸入0 ~ 1的數值")
		self.Bind_Image()
	#Gamma Correction
	def Gamma_Correction(self, event = None):
		#Clear the image
		self.Clear_Image()
		self.show_image()
		self.show_image_information()
		self.Bind_Image()

		self.red_label_img = tk.Canvas(self.frmL, bg = "white", width = 256, height = 256, highlightbackground = "black", highlightthickness = 1)
		self.red_label_img.bind("<ButtonPress-1>", self.Gamma_Image)
		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.point = []
		self.point.append((0,255))
		self.point.append((255, 0))
		self.red_label_img.create_line(0,255,255,0, width=1,fill="red")

	def Gamma_Image(self, event):
		try:	
			self.red_label_img.delete('all')
		except:
			pass
		try:	
			self.green_label_img.grid_forget()
		except:
			pass
		event.x = min(event.x, 255)
		event.y = min(event.y, 255)
		gamma_value = [0] * 256
		p_save = True
		for i in range(len(self.point)):
			x, y = self.point[i]
			if(x == event.x):
				self.point[i] = (event.x, event.y)
				p_save = False
				break
		if(p_save):
			self.point.append((event.x, event.y))
			self.point.sort()
		
		for i in range(0, len(self.point) - 1):
			x0, y0 = self.point[i]
			x1, y1 = self.point[i + 1]
			self.red_label_img.create_line(x0,y0,x1,y1, width=1,fill="red")

			gamma_value[x0] = 255 - y0
			gamma_value[x1] = 255 - y1
			value = (y0 - y1) / (x1 - x0)
			for l in range(x0 + 1, x1 + 1):
				gamma_value[l] = gamma_value[l - 1] + value
		if(len(self.img.shape) == 3):
			self.green_image = np.zeros((self.img.shape[0], self.img.shape[1], 3), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for l in range(self.img.shape[1]):
					for j in range(3):
						pixel = gamma_value[self.img[i, l, j]]
						
						self.green_image[i, l, j] = pixel
			img_PIL = Image.fromarray(self.green_image, 'RGB')
		else:
			self.green_image = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for l in range(self.img.shape[1]):
					pixel = gamma_value[self.img[i, l]]
					self.green_image[i, l] = pixel
			img_PIL = Image.fromarray(self.green_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.green_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
		self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.green_label_img.image = img_PIL
		self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)
		self.Bind_Image()

	#Otsu's Threshold
	def Otsus_Threshold(self, event = None):
		self.Clear_Image()
		#Turn image to grey
		if(len(self.img.shape) == 3):
			new_img = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					new_img[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
			self.img = new_img
		grey_h = [0] * 256
		for i in range(int(self.img.shape[0])):
			for l in range(int(self.img.shape[1])):
				grey_h[self.img[i, l]] += 1
		threshold_t = 0
		max_g = 0
		for t in range(255):
			n0 = self.img[np.where(self.img < t)]
			n1 = self.img[np.where(self.img >= t)]
			w0 = len(n0) / (self.img.shape[0] * self.img.shape[1])
			w1 = len(n1) / (self.img.shape[0] * self.img.shape[1])
			u0 = np.mean(n0) if len(n0) > 0 else 0.
			u1 = np.mean(n1) if len(n0) > 0 else 0.
			g = w0 * w1 * (u0 - u1) ** 2
			if g > max_g:
				max_g = g
				threshold_t = t
		self.green_image = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
		self.green_image[self.img < threshold_t] = 0
		self.green_image[self.img >= threshold_t] = 255
		img_PIL = Image.fromarray(self.green_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)

		threshold_grey_h = [0] * 256
		for i in range(int(self.green_image.shape[0])):
			for l in range(int(self.green_image.shape[1])):
				threshold_grey_h[self.green_image[i, l]] += 1
		f = Figure(figsize=(5,3), dpi=70)
		a = f.add_subplot(111)
		a.bar(list(range(0, 256)), grey_h, color = 'black', align='center')
		a.plot(np.full((max(grey_h)), threshold_t), np.arange(0,max(grey_h)), 'r')
		self.canvas_1 = FigureCanvasTkAgg(f, self.frmL)
		self.canvas_1.draw()
		self.canvas_1.get_tk_widget().grid(column = 1, row = 1)
		self.show_image_information()
		self.show_image()
		self.Bind_Image()
		self.colormenu.entryconfig("RGB", state="disabled")
		self.colormenu.entryconfig("灰階", state="disabled")

		self.trans_label = tk.Label(self.frmL, text = "Threshold = " + str(threshold_t), font = ('Arial', 16))
		self.trans_label.grid(column = 1, row = 2, padx=10, pady=10)
		self.green_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
		self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.green_label_img.image = img_PIL
		self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)

		f = Figure(figsize=(5,3), dpi=70)
		a = f.add_subplot(111)
		a.bar(list(range(0, 256)), threshold_grey_h, color = 'black', align='center')
		a.plot(np.full((max(threshold_grey_h)), threshold_t), np.arange(0,max(threshold_grey_h)), 'r')
		self.canvas_2 = FigureCanvasTkAgg(f, self.frmL)
		self.canvas_2.draw()
		self.canvas_2.get_tk_widget().grid(column = 1, row = 3)
		self.Bind_Image()

	#Kullback
	def Kullback(self, event = None):
		self.Clear_Image()
		#Turn image to grey
		if(len(self.img.shape) == 3):
			new_img = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					new_img[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
			self.img = new_img

		grey_h = [0] * 256
		for i in range(int(self.img.shape[0])):
			for l in range(int(self.img.shape[1])):
				grey_h[self.img[i, l]] += 1
		MinValue, MaxValue = 0, 255
		for i in range(256):
			if(grey_h[i] == 0):
				MinValue += 1
			else:
				break
		for i in range(255, 0, -1):
			if(grey_h[i] == 0):
				MaxValue -= 1
			else:
				break

		threshold_t = -1
		MinSigma = 1e+20
		for i in range(MinValue, MaxValue):
			PixelBack, PixelFore = 0, 0
			OmegaBack, OmegaFore = 0, 0
			for l in range(MinValue, i + 1):
				PixelBack += grey_h[l]
				OmegaBack = OmegaBack + l * grey_h[l]
			for l in range(i + 1, MaxValue + 1):
				PixelFore += grey_h[l]
				OmegaFore = OmegaFore + l * grey_h[l]
			OmegaBack = OmegaBack / PixelBack
			OmegaFore = OmegaFore / PixelFore
			sigmaBack, sigmaFore = 0, 0
			for l in range(MinValue, i + 1):
				sigmaBack = sigmaBack + (l - OmegaBack) * (l - OmegaBack) * grey_h[l]
			for l in range(i + 1, MaxValue + 1):
				sigmaFore = sigmaFore + (l - OmegaFore) * (l - OmegaFore) * grey_h[l]
			if(sigmaBack == 0 or sigmaFore == 0):
				if(threshold_t == - 1): 
					threshold_t = i
			else:
				sigmaBack = math.sqrt((sigmaBack / PixelBack))
				sigmaFore = math.sqrt((sigmaFore / PixelFore))
				#Sigma = 1 + 2 * (PixelBack * math.log(sigmaBack / PixelBack) + PixelFore * math.log(sigmaFore / PixelFore))
				Sigma = PixelBack * math.log(sigmaBack / PixelBack) + PixelFore * math.log(sigmaFore / PixelFore) - PixelBack * math.log(PixelBack) - PixelFore * math.log(PixelFore)
				if(Sigma < MinSigma):
					MinSigma = Sigma
					threshold_t = i
		self.green_image = self.img.copy()#np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
		self.green_image[self.img < threshold_t] = 0
		self.green_image[self.img >= threshold_t] = 255
		img_PIL = Image.fromarray(self.green_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)

		threshold_grey_h = [0] * 256
		for i in range(int(self.green_image.shape[0])):
			for l in range(int(self.green_image.shape[1])):
				threshold_grey_h[self.green_image[i, l]] += 1

		f = Figure(figsize=(5,3), dpi=70)
		a = f.add_subplot(111)
		a.bar(list(range(0, 256)), grey_h, color = 'black', align='center')
		a.plot(np.full((max(grey_h)), threshold_t), np.arange(0,max(grey_h)), 'r')
		self.canvas_1 = FigureCanvasTkAgg(f, self.frmL)
		self.canvas_1.draw()
		self.canvas_1.get_tk_widget().grid(column = 1, row = 1)
		self.show_image_information()
		self.show_image()
		self.Bind_Image()
		self.colormenu.entryconfig("RGB", state="disabled")
		self.colormenu.entryconfig("灰階", state="disabled")

		self.trans_label = tk.Label(self.frmL, text = "Threshold = " + str(threshold_t), font = ('Arial', 16))
		self.trans_label.grid(column = 1, row = 2, padx=10, pady=10)
		self.green_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
		self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.green_label_img.image = img_PIL
		self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)

		f = Figure(figsize=(5,3), dpi=70)
		a = f.add_subplot(111)
		a.bar(list(range(0, 256)), threshold_grey_h, color = 'black', align='center')
		a.plot(np.full((max(threshold_grey_h)), threshold_t), np.arange(0,max(threshold_grey_h)), 'r')
		self.canvas_2 = FigureCanvasTkAgg(f, self.frmL)
		self.canvas_2.draw()
		self.canvas_2.get_tk_widget().grid(column = 1, row = 3)
		self.Bind_Image()

	#Contrast Stretching
	def Contrast_Stretching(self, event = None):
		self.Clear_Image()
		#Turn image to grey
		if(len(self.img.shape) == 3):
			new_img = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					new_img[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
			self.img = new_img

		grey_h = [0] * 256
		for i in range(int(self.img.shape[0])):
			for l in range(int(self.img.shape[1])):
				grey_h[self.img[i, l]] += 1

		self.green_image = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
		for i in range(7, 255):
			if grey_h[i] != 0:
				old_L = i
				break
		for i in range(248, 0, -1):
			if grey_h[i] != 0:
				old_R = i
				break
		print(old_L, old_R)
		for i in range(self.img.shape[0]):
			for l in range(self.img.shape[1]):
				value = ((self.img[i, l] - old_L) / (old_R - old_L)) * 255
				if(value > 255): value = 255
				if(value < 0): value = 0
				self.green_image[i, l] = value
		img_PIL = Image.fromarray(self.green_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)

		Contrast_grey_h = [0] * 256
		for i in range(int(self.green_image.shape[0])):
			for l in range(int(self.green_image.shape[1])):
				Contrast_grey_h[self.green_image[i, l]] += 1

		f = Figure(figsize=(5,3), dpi=70)
		a = f.add_subplot(111)
		a.bar(list(range(0, 256)), grey_h, color = 'black', align='center')
		self.canvas_1 = FigureCanvasTkAgg(f, self.frmL)
		self.canvas_1.draw()
		self.canvas_1.get_tk_widget().grid(column = 1, row = 1)
		self.show_image_information()
		self.show_image()
		self.Bind_Image()
		self.colormenu.entryconfig("RGB", state="disabled")
		self.colormenu.entryconfig("灰階", state="disabled")

		self.green_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
		self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.green_label_img.image = img_PIL
		self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)
		f = Figure(figsize=(5,3), dpi=70)
		a = f.add_subplot(111)
		a.bar(list(range(0, 256)), Contrast_grey_h, color = 'black', align='center')
		self.canvas_2 = FigureCanvasTkAgg(f, self.frmL)
		self.canvas_2.draw()
		self.canvas_2.get_tk_widget().grid(column = 1, row = 3)
		self.Bind_Image()

	#Bit-plane Slicing with binary code
	def Bit_plane_Slicing_Binary(self, event = None):
		new_window = tk.Toplevel(self.parent)
		new_window.title("Bit-plane Slicing(Binary Code)")
		new_window.geometry("1250x600")
		if(len(self.img.shape) == 3):
			new_img = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					new_img[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
		else:
			new_img = self.img.copy()
		i = 128
		row, col = 0, 0
		while(i >= 1):
			new_img_B = np.zeros((new_img.shape[0], new_img.shape[1]), dtype=np.uint8)
			new_img_B = new_img & int(i)
			new_img_B[new_img_B != 0] = new_img_B[new_img_B != 0] * (256 / i) - 1
			img_PIL = Image.fromarray(new_img_B, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			img_Canvas = tk.Canvas(new_window, width=new_img_B.shape[1], height=new_img_B.shape[0])
			img_Canvas.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
			img_Canvas.image = img_PIL
			img_Canvas.grid(column = col, row = row, padx = 10, pady = 10)
			i /= 2
			if(col < 3):
				col += 1
			else:
				col = 0
				row += 1

	#Bit-plane Slicing with gray code
	def Bit_plane_Slicing_Gray(self, event = None):
		new_window = tk.Toplevel(self.parent)
		new_window.title("Bit-plane Slicing(Gray Code)")
		new_window.geometry("1250x600")
		if(len(self.img.shape) == 3):
			new_img = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					value = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
					new_img[i, j] = self.Gray_Code(int(value))
		else:
			new_img = self.img.copy()
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					new_img[i, j] = self.Gray_Code(int(new_img[i, j]))
		i = 128
		row, col = 0, 0
		while(i >= 1):
			new_img_B = np.zeros((new_img.shape[0], new_img.shape[1]), dtype=np.uint8)
			new_img_B = new_img & int(i)
			new_img_B[new_img_B != 0] = new_img_B[new_img_B != 0] * (256 / i) - 1
			img_PIL = Image.fromarray(new_img_B, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			img_Canvas = tk.Canvas(new_window, width=new_img_B.shape[1], height=new_img_B.shape[0])
			img_Canvas.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
			img_Canvas.image = img_PIL
			img_Canvas.grid(column = col, row = row, padx = 10, pady = 10)
			i /= 2
			if(col < 3):
				col += 1
			else:
				col = 0
				row += 1

	def Gray_Code(self, val):
		result = (val & 128 == 128) * 128
		last_b = val & 128 == 128
		i = 64
		while(i >= 1):
			b = (val & i) == i
			result += (last_b ^ b) * i
			i = int(i / 2)
			last_b = b
		return result

	#Watermark
	def Watermark(self, event = None):
		watermark(self.parent, self.img)
		
	#Histogram Equalization
	def Histogram_Equalization(self, event = None):
		self.Clear_Image()
		if(len(self.img.shape) == 3):
			new_img = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					new_img[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
			self.img = new_img

		grey_h = [0] * 256
		for i in range(int(self.img.shape[0])):
			for l in range(int(self.img.shape[1])):
				grey_h[self.img[i, l]] += 1
		p = [0] * 256
		cdf = [0] * 256
		cdf_min = 1000
		cdf_max = 0
		size = self.img.shape[0] * self.img.shape[1]
		p[0] = grey_h[0] / (size)
		for i in range(1, 256):
			p[i] = grey_h[i] / (size)
			cdf[i] = p[i] + cdf[i - 1]
			if(cdf[i] < cdf_min): cdf_min = cdf[i]
			if(cdf[i] > cdf_max): cdf_max = cdf[i]
		c_h = [0] * 256
		for i in range(1, 256):
			c_h[i] = cdf[i] * max(grey_h)
		h = [None] * 256
		for i in range(256):
			#h[i] = (cdf[i] - cdf_min) * (size) / (size - (cdf_min * size)) * 255
			h[i] = ((cdf[i] - cdf_min)  / (cdf_max - cdf_min)) * 255
		self.green_image = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
		for i in range(self.green_image.shape[0]):
			for l in range(self.green_image.shape[1]):
				self.green_image[i, l] = h[self.img[i, l]]
		img_PIL = Image.fromarray(self.green_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)

		grey_h_e = [0] * 256
		for i in range(int(self.green_image.shape[0])):
			for l in range(int(self.green_image.shape[1])):
				grey_h_e[self.green_image[i, l]] += 1
		cdf_e = [0] * 256
		for i in range(1, 256):
			cdf_e[i] = (grey_h_e[i] / size) + cdf_e[i - 1]
		c_h_e = [0] * 256
		for i in range(256):
			c_h_e[i] = cdf_e[i] * max(grey_h_e)

		f = Figure(figsize=(5,3), dpi=70)
		a = f.add_subplot(111)
		a.bar(list(range(0, 256)), grey_h, color = 'black', align='center')
		a.plot(list(range(0, 256)), c_h, 'r')
		self.canvas_1 = FigureCanvasTkAgg(f, self.frmL)
		self.canvas_1.draw()
		self.canvas_1.get_tk_widget().grid(column = 1, row = 1)
		self.show_image_information()
		self.show_image()
		
		self.colormenu.entryconfig("RGB", state="disabled")
		self.colormenu.entryconfig("灰階", state="disabled")

		self.green_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
		self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.green_label_img.image = img_PIL
		self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)
		f = Figure(figsize=(5,3), dpi=70)
		a = f.add_subplot(111)
		a.bar(list(range(0, 256)), grey_h_e, color = 'black', align='center')
		a.plot(list(range(0, 256)), c_h_e, 'r')
		self.canvas_2 = FigureCanvasTkAgg(f, self.frmL)
		self.canvas_2.draw()
		self.canvas_2.get_tk_widget().grid(column = 1, row = 3)
		self.Bind_Image()

	#Histogram Specification
	def Histogram_Specification(self, event = None):
		new_window = tk.Toplevel(self.parent)
		new_window.title("Histogram Specification")
		new_window.geometry("950x850")
		filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("PCX","*.PCX, *.pcx"),("all files","*.*")))
		if filename != '':
			self.Clear_Image()
			self.show_image_information()
			self.show_image()
			self.Bind_Image()
			if(len(self.img.shape) == 3):
				new_img = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
				for i in range(self.img.shape[0]):
					for j in range(self.img.shape[1]):
						new_img[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
			else:
				new_img = self.img.copy()

			grey_h = [0] * 256
			for i in range(int(new_img.shape[0])):
				for l in range(int(new_img.shape[1])):
					grey_h[new_img[i, l]] += 1

			size = new_img.shape[0] * new_img.shape[1]
			mNum1 = [0] * 256
			mNum1[0] = grey_h[0] / (size)
			for i in range(1, 256):
				mNum1[i] = mNum1[i - 1] + grey_h[i] / size
			c_h = [0] * 256 
			for i in range(256):
				c_h[i] = mNum1[i] * max(grey_h)
			inhist1 = [0] * 256 
			for i in range(256):
				inhist1[i] = round(mNum1[i] * 255)

			#target image to grey
			trans_image = self.Read_File(filename)
			if(len(trans_image.shape) == 3):
				img = np.zeros((trans_image.shape[0], trans_image.shape[1]), dtype=np.uint8)
				for i in range(trans_image.shape[0]):
					for j in range(trans_image.shape[1]):
						img[i, j] = 0.3 * int(trans_image[i, j, 0]) + 0.3 * int(trans_image[i, j, 1]) + 0.4 * int(trans_image[i, j, 2])
				trans_image = img

			trans_grey_h = [0] * 256
			for i in range(trans_image.shape[0]):
				for l in range(trans_image.shape[1]):
					trans_grey_h[trans_image[i, l]] += 1

			size1 = trans_image.shape[0] * trans_image.shape[1]
			mNum2 = [0] * 256
			mNum2[0] = trans_grey_h[0] / (size1)
			for i in range(1, 256):
				mNum2[i] = mNum2[i - 1] + trans_grey_h[i] / size1
			
			trans_c_h = [0] * 256
			for i in range(256):
				trans_c_h[i] = mNum2[i] * max(trans_grey_h)

			inhist2 = [0] * 256 
			for i in range(256):
				inhist2[i] = round(mNum2[i] * 255)

			g = []
			for i in range(256):
				a = inhist1[i]
				flag = True
				for j in range(256):
					if(inhist2[j] == a):
						g.append(j)
						flag = False
						break
				if(flag == True):
					minp = 255
					for j in range(256):
						b = abs(inhist2[j] - a)
						if(b < minp):
							minp = b
							jmin = j
					g.append(jmin)

			result_img = np.zeros((new_img.shape[0], new_img.shape[1]), dtype=np.uint8)
			for i in range(result_img.shape[0]):
				for l in range(result_img.shape[1]):
					result_img[i, l] = g[new_img[i, l]]
			
			result_grey_h = [0] * 256
			for i in range(int(result_img.shape[0])):
				for l in range(int(result_img.shape[1])):
					result_grey_h[result_img[i, l]] += 1
			result_cdf = [0] * 256
			result_cdf[0] = result_grey_h[0] / size
			for i in range(1, 256):
				result_cdf[i] = (result_grey_h[i] / size) + result_cdf[i - 1]
			result_c_h = [0] * 256
			for i in range(256):
				result_c_h[i] = result_cdf[i] * max(result_grey_h)

			img_PIL = Image.fromarray(new_img, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			new_img_label = tk.Canvas(new_window, width=new_img.shape[1], height=new_img.shape[0])
			new_img_label.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
			new_img_label.image = img_PIL
			new_img_label.grid(column = 0, row = 0, padx = 10, pady = 10)

			f = Figure(figsize=(5,3), dpi=70)
			a = f.add_subplot(111)
			a.bar(list(range(0, 256)), grey_h, color = 'black', align='center')
			a.plot(list(range(0, 256)), c_h, 'r')
			canvas_1 = FigureCanvasTkAgg(f, new_window)
			canvas_1.draw()
			canvas_1.get_tk_widget().grid(column = 1, row = 0)

			img_PIL = Image.fromarray(trans_image, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			trans_img_label = tk.Canvas(new_window, width=trans_image.shape[1], height=trans_image.shape[0])
			trans_img_label.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
			trans_img_label.image = img_PIL
			trans_img_label.grid(column = 0, row = 1, padx = 10, pady = 10)
			
			f = Figure(figsize=(5,3), dpi=70)
			a = f.add_subplot(111)
			a.bar(list(range(0, 256)), trans_grey_h, color = 'black', align='center')
			a.plot(list(range(0, 256)), trans_c_h, 'r')
			canvas_1 = FigureCanvasTkAgg(f, new_window)
			canvas_1.draw()
			canvas_1.get_tk_widget().grid(column = 1, row = 1)

			img_PIL = Image.fromarray(result_img, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			result_img_label = tk.Canvas(new_window, width=result_img.shape[1], height=result_img.shape[0])
			result_img_label.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
			result_img_label.image = img_PIL
			result_img_label.grid(column = 0, row = 2, padx = 10, pady = 10)
			
			f = Figure(figsize=(5,3), dpi=70)
			a = f.add_subplot(111)
			a.bar(list(range(0, 256)), result_grey_h, color = 'black', align='center')
			a.plot(list(range(0, 256)), result_c_h, 'r')
			canvas_1 = FigureCanvasTkAgg(f, new_window)
			canvas_1.draw()
			canvas_1.get_tk_widget().grid(column = 1, row = 2)
	

	#Connected Components
	def Connected_Components(self, event = None):
		self.Clear_Image()

		if(len(self.img.shape) == 3):
			self.red_image = np.zeros((self.img.shape[0], self.img.shape[1]), dtype = np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					self.red_image[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
		else:
			self.red_image = self.img.copy()
		self.red_image[self.red_image < 128] = 0
		self.red_image[self.red_image >= 128] = 255

		self.trans_label = tk.Button(self.frmL, text="4-connected", command = self.Four_Connected)
		self.trans_box = tk.Button(self.frmL, text="8-connected", command = self.Eight_Connected)

		img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.show_image_information()
		self.show_image()
		self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL

		self.trans_label.grid(row = 2, column = 1, padx=10, pady=10, sticky = tk.W)
		self.trans_box.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.E)
		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.Bind_Image()

	'''
	  O
	O X O
	  O
	'''
	def Four_Connected(self):
		try:	
			self.green_label_img.delete('all')
		except:
			pass
		try:	
			self.green_label_img.grid_forget()
		except:
			pass
		new_img = np.zeros((self.red_image.shape[0], self.img.shape[1]), dtype=np.int64)
		index = 1
		same_index = []
		for i in range(self.red_image.shape[0]):
			for l in range(self.red_image.shape[1]):
				if(self.red_image[i, l] == 255):
					if(i - 1 >= 0 and l - 1 >= 0):
						if(new_img[i - 1, l] == 0 and new_img[i, l - 1] == 0):
							new_img[i, l] = index
							same_index.append([index])
							index += 1
						elif(new_img[i - 1, l] != 0 and new_img[i, l - 1] != 0):
							if(new_img[i - 1, l] != new_img[i, l - 1]):
								value = min(new_img[i - 1, l], new_img[i, l - 1])
								new_img[i, l] = value
								same_index[int(new_img[i - 1, l]) - 1] = same_index[int(new_img[i - 1, l]) - 1] + [new_img[i, l - 1]]
								same_index[int(new_img[i, l - 1]) - 1] = same_index[int(new_img[i, l - 1]) - 1] + [new_img[i - 1, l]]
							else:
								new_img[i, l] = new_img[i, l - 1]

						elif(new_img[i - 1, l] == 0):
							new_img[i, l] = new_img[i, l - 1]
						elif(new_img[i, l - 1] == 0):
							new_img[i, l] = new_img[i - 1, l]
					elif(i - 1 < 0):
						if(new_img[i, l - 1] != 0):
							new_img[i, l] = new_img[i, l - 1]
						else:
							new_img[i, l] = index
							same_index.append([index])
							index += 1
					elif(l - 1 < 0):
						if(new_img[i - 1, l] != 0):
							new_img[i, l] = new_img[i - 1, l]
						else:
							new_img[i, l] = index
							same_index.append([index])
							index += 1
					else:
						new_img[i, l] = index
						same_index.append([index])
						index += 1
				else:
					new_img[i, l] = 0

		replace_index = [0] * len(same_index)
		replace_index[0] = int(round(min(same_index[0])))
		for i in range(1, len(same_index)):
			value = int(round(min(same_index[i]))) - 1
			if(value < i):
				value1 = i
				while(value != value1):
					value = int(value1)
					value1 = int(round(min(same_index[value]))) - 1
				replace_index[i] = int(round(min(same_index[value])))
			else:
				replace_index[i] = int(round(min(same_index[value])))

		color_number = list(set(replace_index))
		
		for i in range(new_img.shape[0]):
			for l in range(new_img.shape[1]):
				if(new_img[i, l] != 0):
					new_img[i, l] = replace_index[int(new_img[i, l]) - 1]

		mask = [[-1, 0], [0, -1], [1, 0], [0, 1]]
		for i in range(new_img.shape[0]):
			for l in range(new_img.shape[1]):
				index = new_img[i, l]
				if(new_img[i, l] != 0):
					index = new_img[i, l]
					for x, y in mask:
						x_ = i + x
						y_ = l + y
						if(x_ < 0 or x_ >= new_img.shape[0]):
							pass
						elif(y_ < 0 or y_ >= new_img.shape[1]):
							pass
						else:
							if(new_img[x_, y_] != 0 and (x_ != i or y_ != l)):
								if(new_img[x_, y_] not in same_index[index - 1]):
									same_index[index - 1] = same_index[index - 1] + [new_img[x_, y_]]

		replace_index = [0] * len(same_index)
		replace_index[0] = int(round(min(same_index[0])))
		for i in range(1, len(same_index)):
			value = int(round(min(same_index[i]))) - 1
			if(value < i):
				value1 = i
				while(value != value1):
					value = int(value1)
					value1 = int(round(min(same_index[value]))) - 1
				replace_index[i] = int(round(min(same_index[value])))
			else:
				replace_index[i] = int(round(min(same_index[value])))

		for i in range(new_img.shape[0]):
			for l in range(new_img.shape[1]):
				if(new_img[i, l] != 0):
					new_img[i, l] = replace_index[int(new_img[i, l]) - 1]

		color = np.zeros((len(color_number), 3), dtype=np.uint8)
		for i in range(len(color_number)):
			c = [random.random() * 255, random.random() * 255, random.random() * 255]
			while(c != 0):
				if(c not in color):
					color[i] = c
					c = 0
				else:
					c = [random.random() * 255, random.random() * 255, random.random() * 255]
		self.green_image = np.zeros((self.red_image.shape[0], self.img.shape[1], 3), dtype=np.uint8)
		for i in range(self.green_image.shape[0]):
			for l in range(self.green_image.shape[1]):
				if(new_img[i, l] != 0):
					self.green_image[i, l] = color[color_number.index(int(new_img[i, l]))]
				else:
					self.green_image[i, l] = [0, 0, 0]

		img_PIL = Image.fromarray(self.green_image, 'RGB')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.green_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
		self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.green_label_img.image = img_PIL
		self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)
		self.Bind_Image()
	
	'''
	O O O
	O X O
	O O O
	'''
	def Eight_Connected(self):
		try:	
			self.blue_label_img.delete('all')
		except:
			pass
		try:	
			self.blue_label_img.grid_forget()
		except:
			pass
		new_img = np.zeros((self.red_image.shape[0], self.img.shape[1]), dtype=np.int64)
		index = 1
		same_index = []
		mask = [[0, -1], [-1, -1], [-1, 0], [-1, 1]]
		for i in range(self.red_image.shape[0]):
			for l in range(self.red_image.shape[1]):
				if(self.red_image[i, l] == 255):
					start_ = 0
					end_ = 4
					value = 0
					if(i - 1 < 0):
						end_ = 2
					if(l - 1 < 0):
						start_ = 2
					elif(l + 1 >= self.red_image.shape[1]):
						end_ = 3

					for n in range(start_, end_):
						x, y = mask[n][0], mask[n][1]
						pixel = new_img[i + x, l + y]
						if(pixel != 0):
							if(value != 0):
								if(value not in same_index[pixel - 1]):
									same_index[pixel - 1] = same_index[pixel - 1] + [value]
								if(pixel not in same_index[value - 1]):
									same_index[value - 1] = same_index[value - 1] + [pixel]
								value = min(value, pixel)
							else:
								value = pixel

							
					if(value == 0):
						new_img[i, l] = index
						same_index.append([index])
						index += 1
					else:
						new_img[i, l] = value
					
				else:
					new_img[i, l] = 0

		replace_index = [0] * len(same_index)
		replace_index[0] = int(round(min(same_index[0])))
		for i in range(1, len(same_index)):
			value = int(round(min(same_index[i]))) - 1
			if(value < i):
				value1 = i
				while(value != value1):
					value = int(value1)
					value1 = int(round(min(same_index[value]))) - 1
				replace_index[i] = int(round(min(same_index[value])))
			else:
				replace_index[i] = int(round(min(same_index[value])))

		for i in range(new_img.shape[0]):
			for l in range(new_img.shape[1]):
				if(new_img[i, l] != 0):
					new_img[i, l] = replace_index[int(new_img[i, l]) - 1]

		for i in range(new_img.shape[0]):
			for l in range(new_img.shape[1]):
				if(new_img[i, l] != 0):
					index = new_img[i, l]
					for x in range(i - 1, i + 2):
						for y in range(l - 1, l + 2):
							if(0 <= x < new_img.shape[0] and 0 <= y < new_img.shape[1]):
								if(new_img[x, y] != 0 and (x != i or y != l)):
									if(new_img[x, y] not in same_index[index - 1]):
										same_index[index - 1] = same_index[index - 1] + [new_img[x, y]]
		replace_index = [0] * len(same_index)
		replace_index[0] = int(round(min(same_index[0])))
		for i in range(1, len(same_index)):
			value = int(round(min(same_index[i]))) - 1
			if(value < i):
				value1 = i
				while(value != value1):
					value = int(value1)
					value1 = int(round(min(same_index[value]))) - 1
				replace_index[i] = int(round(min(same_index[value])))
			else:
				replace_index[i] = int(round(min(same_index[value])))

		for i in range(new_img.shape[0]):
			for l in range(new_img.shape[1]):
				if(new_img[i, l] != 0):
					new_img[i, l] = replace_index[int(new_img[i, l]) - 1]

		color_number = list(set(replace_index))
		color = np.zeros((len(color_number), 3), dtype=np.uint8)
		for i in range(len(color_number)):
			c = [random.random() * 255, random.random() * 255, random.random() * 255]
			while(c != 0):
				if(c not in color):
					color[i] = c
					c = 0
				else:
					c = [random.random() * 255, random.random() * 255, random.random() * 255]
		self.blue_image = np.zeros((self.red_image.shape[0], self.img.shape[1], 3), dtype=np.uint8)
		for i in range(self.blue_image.shape[0]):
			for l in range(self.blue_image.shape[1]):
				if(new_img[i, l] != 0):
					self.blue_image[i, l] = color[color_number.index(int(new_img[i, l]))]
				else:
					self.blue_image[i, l] = [0, 0, 0]

		img_PIL = Image.fromarray(self.blue_image, 'RGB')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.blue_label_img = tk.Canvas(self.frmL, width=self.blue_image.shape[1], height=self.blue_image.shape[0])
		self.blue_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.blue_label_img.image = img_PIL
		self.blue_label_img.grid(column = 1, row = 3, padx = 50, pady = 20)
		self.Bind_Image()


	'''
	O1 O2 O3
	O4  X O5
	O6 O7 O8

	if((x - 1/8 * sum(Oi)) > threshold):
		x = 1/8 * sum(Oi)

	'''
	#Outlier Filtering
	def Outlier(self, event = None):
		self.Clear_Image()
		if(len(self.img.shape) == 3):
			self.red_image = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					self.red_image[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
		else:
			self.red_image = self.img.copy()
		'''
		#Add Salt and Pepper noise
		p = 0.005
		for i in range(self.red_image.shape[0]):
			for l in range(self.red_image.shape[1]):
				rdn = random.random()
				if(rdn < p):
					self.red_image[i, l] = 255 #salt
				elif(rdn > 1 - p):
					self.red_image[i, l] = 0 #peper
		'''

		img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.show_image_information()
		self.show_image()
		self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		self.trans_label = tk.Label(self.frmL, text = "Filter Size : \n\nThreshold : ")
		self.trans_box = ttk.Combobox(self.frmL, value = ['3', '5', '7', '9', "11", "13", "15"])
		self.trans_box.bind("<<ComboboxSelected>>", self.Outlier_Filtering_Image)

		var = tk.DoubleVar(value=128)
		self.trans_button = tk.Spinbox(self.frmL, from_ = 0, to = 255, increment = 1, textvariable = var)
		self.trans_button.bind("<Return>", self.Outlier_Filtering_Image)

		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.trans_label.grid(row = 2, column = 1, padx=10, pady=10, sticky = tk.W)
		self.trans_box.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.E + tk.N)
		self.trans_button.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.E + tk.S)
		self.Bind_Image()

	def Outlier_Filtering_Image(self, event):
		try:	
			self.green_label_img.delete('all')
		except:
			pass
		try:	
			self.green_label_img.grid_forget()
		except:
			pass

		progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
		progressbar.grid(column = 2, row = 0, sticky = tk.E)
		progressbar["value"] = 0
		progressbar["maximum"] = self.red_image.shape[0]

		size = int(int(self.trans_box.get()) / 2)
		threshold = int(self.trans_button.get())
		#print(size, threshold)

		self.green_image = np.zeros((self.red_image.shape[0], self.red_image.shape[1]), dtype=np.uint8)
		for i in range(self.red_image.shape[0]):
			progressbar["value"] += 1
			progressbar.update()
			for l in range(self.red_image.shape[1]):
				mean = 0 
				for x in range(i - size, i + size + 1):
					for y in range(l - size, l + size + 1):
						if(x < 0):
							pick_x = self.red_image.shape[0] + x
						elif(x > self.red_image.shape[0] - 1):
							pick_x = x - self.red_image.shape[0]
						else:
							pick_x = x
						if(y < 0):
							pick_y = self.red_image.shape[1] + y
						elif(y > self.red_image.shape[1] - 1):
							pick_y = y - self.red_image.shape[1]
						else:
							pick_y = y
						#print(pick_x, pick_y)
						if(pick_x != i or pick_y != l):
							mean += self.red_image[pick_x, pick_y]

				mean /= 8
				value = int(self.red_image[i, l]) - mean
				if(value > threshold):
					self.green_image[i, l] = int(mean)
				else:
					self.green_image[i, l] = self.red_image[i, l]
		try:
			progressbar.grid_forget()
		except:
			pass
		img_PIL = Image.fromarray(self.green_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.green_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
		self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.green_label_img.image = img_PIL
		self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)
		self.Bind_Image()

	#Mean Median Filtering
	def Mean_Median(self, event = None):
		self.Clear_Image()
		if(len(self.img.shape) == 3):
			self.red_image = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					self.red_image[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
		else:
			self.red_image = self.img.copy()

		#Add Salt and Pepper noise
		p = 0.005
		for i in range(self.red_image.shape[0]):
			for l in range(self.red_image.shape[1]):
				rdn = random.random()
				if(rdn < p):
					self.red_image[i, l] = 255 #salt
				elif(rdn > 1 - p):
					self.red_image[i, l] = 0 #peper
		img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.show_image_information()
		self.show_image()
		self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		self.trans_label = tk.Label(self.frmL, text = "Mean Filter Size : \n\nMedian Filter Size : ")
		self.trans_box = ttk.Combobox(self.frmL, value = ['3', '5', '7', '9'])
		self.trans_box.bind("<<ComboboxSelected>>", self.Mean_Filtering_Image)

		self.trans_button = ttk.Combobox(self.frmL, value = ['square 3', 'cross 3', 'square 5', 'cross 5', 'square 7', 'cross 7', 'square 9', 'cross 9'])
		self.trans_button.bind("<<ComboboxSelected>>", self.Median_Filtering_Image)

		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.trans_label.grid(row = 2, column = 1, padx=10, pady=10, sticky = tk.W)
		self.trans_box.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.E + tk.N)
		self.trans_button.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.E + tk.S)
		self.Bind_Image()

	#Mean Filtering
	def Mean_Filtering_Image(self, event):
		try:	
			self.green_label_img.delete('all')
		except:
			pass
		try:	
			self.green_label_img.grid_forget()
		except:
			pass

		progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
		progressbar.grid(column = 2, row = 0, sticky = tk.E)
		progressbar["value"] = 0
		progressbar["maximum"] = self.red_image.shape[0]

		size = int(int(event.widget.get()) / 2)
		
		self.green_image = np.zeros((self.red_image.shape[0], self.red_image.shape[1]), dtype=np.uint8)
		for i in range(0, self.red_image.shape[0]):
			progressbar["value"] += 1
			progressbar.update()
			for l in range(0, self.red_image.shape[1]):
				mean = 0
				count = 0
				for x in range(i - size, i + size + 1):
					for y in range(l - size, l + size + 1):
						if(x < 0):
							pick_x = self.red_image.shape[0] + x
						elif(x > self.red_image.shape[0] - 1):
							pick_x = x - self.red_image.shape[0]
						else:
							pick_x = x
						if(y < 0):
							pick_y = self.red_image.shape[1] + y
						elif(y > self.red_image.shape[1] - 1):
							pick_y = y - self.red_image.shape[1]
						else:
							pick_y = y
						#print(pick_x, pick_y)
						mean += self.red_image[pick_x, pick_y]
						count += 1
				mean /= count
				self.green_image[i, l] = int(mean)
		try:
			progressbar.grid_forget()
		except:
			pass
		img_PIL = Image.fromarray(self.green_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.green_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
		self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.green_label_img.image = img_PIL
		self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)
		self.Bind_Image()
		
	#Median Filtering
	def Median_Filtering_Image(self, event):
		try:	
			self.blue_label_img.delete('all')
		except:
			pass
		try:	
			self.blue_label_img.grid_forget()
		except:
			pass

		progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
		progressbar.grid(column = 2, row = 0, sticky = tk.E)
		progressbar["value"] = 0
		progressbar["maximum"] = self.red_image.shape[0]

		mode = (event.widget.get()).split(' ')[0]
		size = int((event.widget.get())[-1])
		s = int(size / 2)
		self.blue_image = np.zeros((self.red_image.shape[0], self.red_image.shape[1]), dtype=np.uint8)

		if(mode == "square"):
			for i in range(0, self.red_image.shape[0]):
				progressbar["value"] += 1
				progressbar.update()
				for l in range(0, self.red_image.shape[1]):
					m_array = [0] * (size * size)
					count = 0
					for x in range(i - s, i + s + 1):
						for y in range(l - s, l + s + 1):
							if(x < 0 ):
								pick_x = self.red_image.shape[0] + x
							elif(x > self.red_image.shape[0] - 1):
								pick_x = x - self.red_image.shape[0]
							else:
								pick_x = x
							if(y < 0 ):
								pick_y = self.red_image.shape[1] + y
							elif(y > self.red_image.shape[1] - 1):
								pick_y = y - self.red_image.shape[1]
							else:
								pick_y = y
							m_array[count] = self.red_image[pick_x, pick_y]
							count += 1
					m_array.sort()
					if(count % 2 != 0):
						median = m_array[int(count / 2) + 1]
					else:
						median = m_array[int(count / 2)]
					self.blue_image[i, l] = median
		else:
			for i in range(0, self.red_image.shape[0]):
				progressbar["value"] += 1
				progressbar.update()
				for l in range(0, self.red_image.shape[1]):
					m_array = [self.red_image[i, l]]
					count = 1
					for x in range(i - s, i + s + 1):
						if(x < 0):
							pick_x = self.red_image.shape[0] + x
						elif(x > self.red_image.shape[0] - 1):
							pick_x = x - self.red_image.shape[0]
						else:
							pick_x = x
						if(pick_x != i):
							m_array.append(self.red_image[pick_x, l])
							count += 1

					for y in range(l - s, l + s + 1):
						if(y < 0):
							pick_y = self.red_image.shape[1] + y
						elif(y > self.red_image.shape[1] - 1):
							pick_y = y - self.red_image.shape[1]
						else:
							pick_y = y
						if(pick_y != l):
							m_array.append(self.red_image[i, pick_y])
							count += 1
					m_array.sort()
					if(count % 2 != 0):
						median = m_array[int(count / 2) + 1]
					else:
						median = m_array[int(count / 2)]
					self.blue_image[i, l] = median

		try:
			progressbar.grid_forget()
		except:
			pass
		img_PIL = Image.fromarray(self.blue_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.blue_label_img = tk.Canvas(self.frmL, width=self.blue_image.shape[1], height=self.blue_image.shape[0])
		self.blue_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.blue_label_img.image = img_PIL
		self.blue_label_img.grid(column = 1, row = 3, padx = 50, pady = 20)
		self.Bind_Image()

	#Pseudo Median Filtering
	'''
	1/2(max(min)) + 1/2(min(max))

	'''
	def Pseudo_Median(self, event = None):
		self.Clear_Image()
		if(len(self.img.shape) == 3):
			self.red_image = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					self.red_image[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
		else:
			self.red_image = self.img.copy()
		#Add Salt and Pepper noise
		p = 0.005
		for i in range(self.red_image.shape[0]):
			for l in range(self.red_image.shape[1]):
				rdn = random.random()
				if(rdn < p):
					self.red_image[i, l] = 255 #salt
				elif(rdn > 1 - p):
					self.red_image[i, l] = 0 #peper

		img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.show_image_information()
		self.show_image()
		self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		
		self.trans_box = tk.Button(self.frmL, text="Pseudo", command = self.Pseudo_Filtering_Image)

		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.trans_box.grid(row = 2, column = 1, padx = 10, pady = 10)
		self.Bind_Image()

	def Pseudo_Filtering_Image(self):
		try:	
			self.green_label_img.delete('all')
		except:
			pass
		try:	
			self.green_label_img.grid_forget()
		except:
			pass

		progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
		progressbar.grid(column = 2, row = 0, sticky = tk.E)
		progressbar["value"] = 0
		progressbar["maximum"] = self.red_image.shape[0]

		size = 5
		s = int(size / 2)
		self.green_image = np.zeros((self.red_image.shape[0], self.red_image.shape[1]), dtype=np.uint8)
		for i in range(self.red_image.shape[0]):
			progressbar["value"] += 1
			progressbar.update()
			for l in range(self.red_image.shape[1]):
				arr = []
				arr1 = []
				
				for x in range(i - s, i + s + 1):
					if(x < 0):
						pick_x = self.red_image.shape[0] + x
					elif(x > self.red_image.shape[0] - 1):
						pick_x = x - self.red_image.shape[0]
					else:
						pick_x = x
					arr.append(self.red_image[pick_x, l])
				
				for y in range(l - s, l + s + 1):
					if(y < 0):
						pick_y = self.red_image.shape[1] + y
					elif(y > self.red_image.shape[1] - 1):
						pick_y = y - self.red_image.shape[1]
					else:
						pick_y = y
					arr1.append(self.red_image[i, pick_y])

				min_arr = [min(c) for c in combinations(arr, 3)]
				max_arr = [max(c) for c in combinations(arr, 3)]
				min_arr1 = [min(c) for c in combinations(arr1, 3)]
				max_arr1 = [max(c) for c in combinations(arr1, 3)]

				self.green_image[i, l] = max(max(min_arr), max(min_arr1	)) / 2 + min(min(max_arr), min(max_arr1)) / 2
				
		try:
			progressbar.grid_forget()
		except:
			pass
		img_PIL = Image.fromarray(self.green_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.green_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
		self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.green_label_img.image = img_PIL
		self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)
		self.Bind_Image()

	'''
		   -1 -1 -1
	1/9 *  -1  8 -1 
		   -1 -1 -1 
	'''
	#Highpass Filtering
	def Highpass(self, event = None):
		self.Clear_Image()
		if(len(self.img.shape) == 3):
			self.red_image = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					self.red_image[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
		else:
			self.red_image = self.img.copy()

		img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.show_image_information()
		self.show_image()
		self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		self.trans_label = tk.Label(self.frmL, text = "Highpass Filter Size : ")
		self.trans_box = ttk.Combobox(self.frmL, value = ['3', '5', '7', '9'])
		self.trans_box.bind("<<ComboboxSelected>>", self.Highpass_Filtering_Image)

		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.trans_label.grid(row = 2, column = 1, padx=10, pady=10, sticky = tk.W)
		self.trans_box.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.E + tk.N)
		self.Bind_Image() 

	def Highpass_Filtering_Image(self, event):
		try:	
			self.green_label_img.delete('all')
			self.blue_label_img.delete('all')
		except:
			pass
		try:	
			self.green_label_img.grid_forget()
			self.blue_label_img.delete('all')
		except:
			pass

		progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
		progressbar.grid(column = 2, row = 0, sticky = tk.E)
		progressbar["value"] = 0
		progressbar["maximum"] = self.red_image.shape[0]

		size = int(event.widget.get())
		s = int(size / 2)

		self.green_image = np.zeros((self.red_image.shape[0], self.red_image.shape[1]), dtype=np.uint8)
		for i in range(1, self.green_image.shape[0] - 1):
			progressbar["value"] += 1
			progressbar.update()
			for l in range(1, self.green_image.shape[1] - 1):
				mean = 0
				for x in range(i - s, i + s + 1):
					for y in range(l - s, l + s + 1):
						#mean = 0
						if(x < 0):
							pick_x = self.red_image.shape[0] + x
						elif(x > self.red_image.shape[0] - 1):
							pick_x = x - self.red_image.shape[0]
						else:
							pick_x = x
						if(y < 0 ):
							pick_y = self.red_image.shape[1] + y
						elif(y > self.red_image.shape[1] - 1):
							pick_y = y - self.red_image.shape[1]
						else:
							pick_y = y
						if(pick_x == i and pick_y == l):
							mean += self.red_image[pick_x][pick_y] * (size * size - 1)
						else:
							mean -= self.red_image[pick_x][pick_y]
				mean /= (size * size)
				if(mean < 0):
					self.green_image[i, l] = 0
				elif(mean > 255):
					self.green_image[i, l] = 255
				else:
					self.green_image[i, l] = mean

		self.blue_image = self.red_image.copy()
		for i in range(self.blue_image.shape[0]):
			for l in range(self.blue_image.shape[1]):
				self.blue_image[i, l] = self.blue_image[i, l] - self.green_image[i, l]
		try:
			progressbar.grid_forget()
		except:
			pass
		img_PIL = Image.fromarray(self.green_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.green_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
		self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.green_label_img.image = img_PIL
		self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)

		img_PIL = Image.fromarray(self.blue_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.blue_label_img = tk.Canvas(self.frmL, width=self.blue_image.shape[1], height=self.blue_image.shape[0])
		self.blue_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.blue_label_img.image = img_PIL
		self.blue_label_img.grid(column = 1, row = 3, padx = 50, pady = 20)
		self.Bind_Image()

	#Edge Crispening Filtering
	'''
	Mask1 =  0 -1  0
			-1  5 -1
			 0 -1  0

	Mask2 = -1 -1 -1
			-1  9 -1
			-1 -1 -1

	Mask3 =  1 -2  1
			-2  5 -2
			 1 -2  1

	'''
	def Edge_Crispening(self, event = None):
		self.Clear_Image()
		if(len(self.img.shape) == 3):
			self.red_image = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					self.red_image[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
		else:
			self.red_image = self.img.copy()

		img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.show_image_information()
		self.show_image()
		self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		self.trans_label = tk.Label(self.frmL, text = "Edge Crispening Type : ")
		self.trans_box = ttk.Combobox(self.frmL, value = ['Mask1', 'Mask2', 'Mask3'])
		self.trans_box.bind("<<ComboboxSelected>>", self.Edge_Crispening_Filtering_Image)

		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.trans_label.grid(row = 2, column = 1, padx=10, pady=10, sticky = tk.W)
		self.trans_box.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.E + tk.N)
		self.Bind_Image()

	def Edge_Crispening_Filtering_Image(self, event):
		try:	
			self.green_label_img.delete('all')
		except:
			pass
		try:	
			self.green_label_img.grid_forget()
		except:
			pass

		progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
		progressbar.grid(column = 2, row = 0, sticky = tk.E)
		progressbar["value"] = 0
		progressbar["maximum"] = self.red_image.shape[0]

		mask_type = event.widget.get()
		

		self.green_image = np.zeros((self.red_image.shape[0], self.red_image.shape[1]), dtype=np.uint8)
		for i in range(1, self.green_image.shape[0] - 1):
			progressbar["value"] += 1
			progressbar.update()
			for l in range(1, self.green_image.shape[1] - 1):
				
				if(mask_type == "Mask1"):
					value = int(self.red_image[i, l]) * 5
					value -= int(self.red_image[i - 1, l])
					value -= int(self.red_image[i + 1, l])
					value -= int(self.red_image[i, l - 1])
					value -= int(self.red_image[i, l + 1])
					value = max(0, value)
					value = min(255, value)
				elif(mask_type == "Mask2"):
					value = int(self.red_image[i, l]) * 9
					value -= int(self.red_image[i - 1, l - 1])
					value -= int(self.red_image[i - 1, l])
					value -= int(self.red_image[i - 1, l + 1])
					value -= int(self.red_image[i, l - 1])
					value -= int(self.red_image[i, l + 1])
					value -= int(self.red_image[i + 1, l - 1])
					value -= int(self.red_image[i + 1, l])
					value -= int(self.red_image[i + 1, l + 1])
					value = max(0, value)
					value = min(255, value)
				else:
					value = int(self.red_image[i, l]) * 5
					value += int(self.red_image[i - 1, l - 1])
					value += int(self.red_image[i - 1, l + 1])
					value += int(self.red_image[i + 1, l - 1])
					value += int(self.red_image[i + 1, l + 1])
					value -= int(self.red_image[i, l - 1]) * 2
					value -= int(self.red_image[i, l + 1]) * 2
					value -= int(self.red_image[i - 1, l]) * 2
					value -= int(self.red_image[i + 1, l]) * 2
					value = max(0, value)
					value = min(255, value)
				
				self.green_image[i, l] = value
				
		try:
			progressbar.grid_forget()
		except:
			pass
		img_PIL = Image.fromarray(self.green_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.green_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
		self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.green_label_img.image = img_PIL
		self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)
		self.Bind_Image()

	'''
		   -1 -1 -1
	1/9 *  -1  w -1
		   -1 -1 -1
	w = 9 * A - 1
	'''
	#High Boost Filtering
	def High_Boost(self, event = None):
		self.Clear_Image()
		if(len(self.img.shape) == 3):
			self.red_image = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					self.red_image[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
		else:
			self.red_image = self.img.copy()

		img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.show_image_information()
		self.show_image()
		self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		self.trans_label = tk.Label(self.frmL, text = "High-boost (A) : ")
		self.trans_box = tk.Spinbox(self.frmL, from_ = 1, to = 3, increment = 0.1)
		self.trans_button = tk.Button(self.frmL, text="確定", command = self.High_Boost_Image)

		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.trans_label.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = tk.W)
		self.trans_box.grid(row = 2, column = 1, padx = 10, pady = 10)
		self.trans_button.grid(row = 2, column = 2, padx = 10, pady = 10, sticky = tk.E )
		self.Bind_Image()

	def High_Boost_Image(self):
		A = float(self.trans_box.get())
		try:	
			self.green_label_img.delete('all')
		except:
			pass
		try:	
			self.green_label_img.grid_forget()
		except:
			pass
		if(A >= 1):
			progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
			progressbar.grid(column = 2, row = 0, sticky = tk.E)
			progressbar["value"] = 0
			progressbar["maximum"] = self.red_image.shape[0]
			
			self.green_image = np.zeros((self.red_image.shape[0], self.red_image.shape[1]), dtype=np.uint8)
			for i in range(0, self.red_image.shape[0]):
				progressbar["value"] += 1
				progressbar.update()
				for l in range(0, self.red_image.shape[1]):
					mean = 0
					for x in range(i - 1, i + 2):
						for y in range(l - 1, l + 2):
							if(x < 0):
								pick_x = self.red_image.shape[0] + x
							elif(x > self.red_image.shape[0] - 1):
								pick_x = x - self.red_image.shape[0]
							else:
								pick_x = x
							if(y < 0):
								pick_y = self.red_image.shape[1] + y
							elif(y > self.red_image.shape[1] - 1):
								pick_y = y - self.red_image.shape[1]
							else:
								pick_y = y
							if(x == i and y == l):
								mean += int(self.red_image[pick_x, pick_y]) * (9 * A - 1)
							else:
								mean -= self.red_image[pick_x, pick_y]
					mean /= 9
					if(mean < 0):
						self.green_image[i, l] = 0
					elif(mean > 255):
						self.green_image[i, l] = 255
					else:
						self.green_image[i, l] = int(mean)
			try:
				progressbar.grid_forget()
			except:
				pass

			img_PIL = Image.fromarray(self.green_image, 'L')
			img_PIL = ImageTk.PhotoImage(img_PIL)
			self.green_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
			self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
			self.green_label_img.image = img_PIL
			self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)
			self.Bind_Image()

		else:
			messagebox.showerror("Error", "請輸入1以上的數值")


	#Roberts & Sobel & Prewitt Filtering
	def Roberts_Sobel_Prewitt(self, event = None):
		self.Clear_Image()
		if(len(self.img.shape) == 3):
			new_img = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
			for i in range(self.img.shape[0]):
				for j in range(self.img.shape[1]):
					new_img[i, j] = 0.3 * int(self.img[i, j, 0]) + 0.3 * int(self.img[i, j, 1]) + 0.4 * int(self.img[i, j, 2])
			self.img = new_img

		
		self.show_image_information()
		self.show_image()
		self.red_image = self.img.copy()
		img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL

		self.green_image = self.img.copy()
		img_PIL = Image.fromarray(self.green_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.green_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
		self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.green_label_img.image = img_PIL

		self.blue_image = self.img.copy()
		img_PIL = Image.fromarray(self.blue_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.blue_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
		self.blue_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.blue_label_img.image = img_PIL

		self.trans_label = tk.Button(self.frmL, text="Roberts", command = self.Roberts_Filtering_Image)
		self.trans_box = tk.Button(self.frmL, text="Sobel", command = self.Sobel_Filtering_Image)
		self.trans_button = tk.Button(self.frmL, text="Prewitt", command = self.Prewitt_Filtering_Image)


		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)
		self.blue_label_img.grid(column = 1, row = 3, padx = 50, pady = 20)
		self.trans_label.grid(row = 2, column = 1, padx=10, pady=10)
		self.trans_box.grid(row = 4, column = 0, padx = 10, pady = 10)
		self.trans_button.grid(row = 4, column = 1, padx = 10, pady = 10)
		self.Bind_Image() 

	#Roberts
	'''
	-1  0
	 0  1

	 0 -1
	 1  0
	'''
	def Roberts_Filtering_Image(self):
		try:	
			self.red_label_img.delete('all')
		except:
			pass
		try:	
			self.red_label_img.grid_forget()
		except:
			pass

		progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
		progressbar.grid(column = 2, row = 0, sticky = tk.E)
		progressbar["value"] = 0
		progressbar["maximum"] = self.red_image.shape[0]

		for i in range(self.red_image.shape[0] - 1):
			progressbar["value"] += 1
			progressbar.update()
			for l in range(self.red_image.shape[1] - 1):
				self.red_image[i, l] = abs(int(self.img[i, l]) - int(self.img[i+1, l+1])) + abs(int(self.img[i+1, l]) - int(self.img[i, l+1]))
		try:
			progressbar.grid_forget()
		except:
			pass
		img_PIL = Image.fromarray(self.red_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.red_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)
		self.Bind_Image() 

	#Sobel
	'''
	Gx = -1  0  1
		 -2  0  2
		 -1  0  1
		 
	-----------------

	Gy = -1 -2 -1
		  0  0  0
		  1  2  1
	'''
	def Sobel_Filtering_Image(self):
		try:	
			self.green_label_img.delete('all')
		except:
			pass
		try:	
			self.green_label_img.grid_forget()
		except:
			pass

		progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
		progressbar.grid(column = 2, row = 0, sticky = tk.E)
		progressbar["value"] = 0
		progressbar["maximum"] = self.red_image.shape[0]

		for i in range(1, self.green_image.shape[0] - 1):
			progressbar["value"] += 1
			progressbar.update()
			for l in range(1, self.green_image.shape[1] - 1):
				Gx = (int(self.img[i - 1, l + 1]) + 2 * int(self.img[i, l + 1]) + int(self.img[i + 1, l + 1]))
				Gx = abs(Gx - (int(self.img[i - 1, l - 1]) + 2 * int(self.img[i, l - 1]) + int(self.img[i + 1, l - 1])))
				Gy = (int(self.img[i + 1, l - 1]) + 2 * int(self.img[i + 1, l]) + int(self.img[i + 1, l + 1]))
				Gy = abs(Gy - (int(self.img[i - 1, l - 1]) + 2 * int(self.img[i - 1, l]) + int(self.img[i - 1, l + 1])))
				if(Gx + Gy < 0):
					self.green_image[i, l] = 0
				elif(Gx + Gy > 255):
					self.green_image[i, l] = 255
				else:
					self.green_image[i, l] = Gx + Gy

		try:
			progressbar.grid_forget()
		except:
			pass
		img_PIL = Image.fromarray(self.green_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.green_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
		self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.green_label_img.image = img_PIL
		self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)
		self.Bind_Image() 

	#Prewitt
	'''
	Gx = -1 -1 -1
		  0  0  0
		  1  1  1

	Gy = -1  0  1
		 -1  0  1
		 -1  0  1
	'''
	def Prewitt_Filtering_Image(self):
		try:	
			self.blue_label_img.delete('all')
		except:
			pass
		try:	
			self.blue_label_img.grid_forget()
		except:
			pass

		progressbar = ttk.Progressbar(self.frmB, length = 500, mode='determinate')
		progressbar.grid(column = 2, row = 0, sticky = tk.E)
		progressbar["value"] = 0
		progressbar["maximum"] = self.red_image.shape[0]

		for i in range(1, self.blue_image.shape[0] - 1):
			progressbar["value"] += 1
			progressbar.update()
			for l in range(1, self.blue_image.shape[1] - 1):
				Gx = (int(self.img[i - 1, l + 1]) + int(self.img[i, l + 1]) + int(self.img[i + 1, l + 1]))
				Gx = abs(Gx - (int(self.img[i - 1, l - 1]) + int(self.img[i, l - 1]) + int(self.img[i + 1, l - 1])))
				Gy = (int(self.img[i + 1, l - 1]) + int(self.img[i + 1, l]) + int(self.img[i + 1, l + 1]))
				Gy = abs(Gy - (int(self.img[i - 1, l - 1]) + int(self.img[i - 1, l]) + int(self.img[i - 1, l + 1])))
				if(Gx + Gy < 0):
					self.blue_image[i, l] = 0
				elif(Gx + Gy > 255):
					self.blue_image[i, l] = 255
				else:
					self.blue_image[i, l] = Gx + Gy

		try:
			progressbar.grid_forget()
		except:
			pass
		img_PIL = Image.fromarray(self.blue_image, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.blue_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
		self.blue_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.blue_label_img.image = img_PIL
		self.blue_label_img.grid(column = 1, row = 3, padx = 50, pady = 20)
		self.Bind_Image()

	#Canny
	def Canny_Algorithm(self, event = None):
		canny(self.parent, self.img)

	#Image Compression using Huffman
	def Save_File_Huffman(self, event = None):
		#return
		Huffman(self.parent, self.img)

	#Video Compression Decompression
	def Video(self, event = None):
		Video_Compression(self.parent)

	def Hair(self, event = None):
		Hair(self.parent)

	#Show raw Image
	def show_image(self):
		if(len(self.img.shape) == 3):
			img_PIL = Image.fromarray(self.img, 'RGB')
		else:
			img_PIL = Image.fromarray(self.img, 'L')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.raw_label_img = tk.Canvas(self.frmL, width=self.img.shape[1], height=self.img.shape[0])
		self.raw_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.raw_label_img.image = img_PIL
		self.raw_label_img.grid(column = 0, row = 1, padx = 50, pady = 20)

	#Show header information on right side
	def show_header(self, header):
		items = self.header_tree.get_children()
		[self.header_tree.delete(item) for item in items]
		self.header_tree.insert('','end', text = "Manufacturer" , value = header.Manufacturer)
		self.header_tree.insert('','end', text = "Version" , value = header.Version)
		self.header_tree.insert('','end', text = "Encoding" , value = header.Encoding)
		self.header_tree.insert('','end', text = "BitsPerPixel" , value = header.BitsPerPixel)
		self.header_tree.insert('','end', text = "Xmin" , value = header.XStart)
		self.header_tree.insert('','end', text = "Ymin" , value = header.YStart)
		self.header_tree.insert('','end', text = "Xmax" , value = header.XEnd)
		self.header_tree.insert('','end', text = "Ymax" , value = header.YEnd)
		self.header_tree.insert('','end', text = "Hdpi" , value = header.HorzRes)
		self.header_tree.insert('','end', text = "Vdpi" , value = header.VertRes)
		self.header_tree.insert('','end', text = "Reserved" , value = header.Reserved)
		self.header_tree.insert('','end', text = "NPLanes" , value = header.NumBitPlanes)
		self.header_tree.insert('','end', text = "BytesPerLine" , value = header.BytesPerLine)
		self.header_tree.insert('','end', text = "PaletteInfo" , value = header.PaletteType)
		self.header_tree.insert('','end', text = "HscreenSize" , value = header.HorzScreenSize)
		self.header_tree.insert('','end', text = "VscreenSize" , value = header.VertScreenSize)
		self.header_tree.grid(column = 0, row = 0, padx = 50, pady = 20)

	#Show Image filename & Size
	def show_image_information(self):
		self.filename_label.grid_forget()
		self.h_w_label.grid_forget()
		#File name Label
		self.filename_label = tk.Label(self.frmL, text = str(self.filename.split("/")[-1]), font = ('Arial', 16))
		self.filename_label.grid(column = 0, row = 0, padx = 10, pady = 10)

		# Height X Width Label
		if(len(self.img.shape) == 3):
			show_text = str(self.img.shape[0]) + " X " + str(self.img.shape[1]) + " X " + str(self.img.shape[2])
		else:
			show_text = str(self.img.shape[0]) + " X " + str(self.img.shape[1]) + " X 1"
		self.h_w_label = tk.Label(self.frmL, text = show_text , font = ('Arial', 12))
		self.h_w_label.grid(column = 0, row = 2)

	#Show Palette information on right side
	def show_palette(self):
		palette = np.zeros((256, 256, 3), dtype=np.uint8)
		count = 0
		for i in range(0, 256, 16):
			for l in range(0, 256, 16):
				palette[i:i+16, l:l+16] = self.Extend_Palette[count]
				count += 1
		img_PIL = Image.fromarray(palette, 'RGB')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.palette_label_img = tk.Canvas(self.frmR, width=256, height=256)
		self.palette_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.palette_label_img.image = img_PIL
		self.palette_label_img.grid(column = 0, row = 1, padx = 50, pady = 20)

	#Clear Image
	def Clear_Image(self):
		try:
			self.canvas_1.get_tk_widget().grid_forget()
		except:
			pass
		try:
			self.canvas_2.get_tk_widget().grid_forget()
		except:
			pass
		try:
			self.trans_label.grid_forget()
		except:
			pass
		try:
			self.trans_box.grid_forget()
		except:
			pass
		try:
			self.trans_button.grid_forget()
		except:
			pass
		try:	
			self.raw_label_img.delete('all')
		except:
			pass
		try:	
			self.raw_label_img.grid_forget()
		except:
			pass
		try:	
			self.red_label_img.delete('all')
		except:
			pass
		try:	
			self.red_label_img.grid_forget() 
		except:
			pass
		try:	
			self.green_label_img.delete('all')
		except:
			pass
		try:	
			self.green_label_img.grid_forget()
		except:
			pass
		try:	
			self.blue_label_img.delete('all')
		except:
			pass
		try:
			self.blue_label_img.grid_forget()
		except:
			pass
		self.red_image = None
		self.green_image = None
		self.blue_image = None

	#Show only R, G, B color image
	def RGB_image(self, event = None):
		self.Clear_Image()
		self.show_image()
		self.show_image_information()
		self.red_image = self.img.copy()
		self.green_image = self.img.copy()
		self.blue_image = self.img.copy()

		#red image
		self.red_image[:,:,1] = 0
		self.red_image[:,:,2] = 0
		img_PIL = Image.fromarray(self.red_image, 'RGB')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.red_label_img = tk.Canvas(self.frmL, width=self.red_image.shape[1], height=self.red_image.shape[0])
		self.red_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.red_label_img.image = img_PIL
		self.red_label_img.grid(column = 1, row = 1, padx = 50, pady = 20)

		#green image
		self.green_image[:,:,0] = 0
		self.green_image[:,:,2] = 0
		img_PIL = Image.fromarray(self.green_image, 'RGB')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.green_label_img = tk.Canvas(self.frmL, width=self.green_image.shape[1], height=self.green_image.shape[0])
		self.green_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.green_label_img.image = img_PIL
		self.green_label_img.grid(column = 0, row = 3, padx = 50, pady = 20)

		#blue image
		self.blue_image[:,:,0] = 0
		self.blue_image[:,:,1] = 0
		img_PIL = Image.fromarray(self.blue_image, 'RGB')
		img_PIL = ImageTk.PhotoImage(img_PIL)
		self.blue_label_img = tk.Canvas(self.frmL, width=self.blue_image.shape[1], height=self.blue_image.shape[0])
		self.blue_label_img.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
		self.blue_label_img.image = img_PIL
		self.blue_label_img.grid(column = 1, row = 3, padx = 50, pady = 20)
		self.Bind_Image()
	
	#Bind image
	def Bind_Image(self):
		self.raw_label_img.bind("<Motion>", self.Mouse_Information_Raw_Img)
		if(type(self.red_image) != type(None)):
			self.red_label_img.bind("<Motion>", self.Mouse_Information_Red_Img)
		if(type(self.green_image) != type(None)):
			self.green_label_img.bind("<Motion>", self.Mouse_Information_Green_Img)
		if(type(self.blue_image) != type(None)):
			self.blue_label_img.bind("<Motion>", self.Mouse_Information_Blue_Img)

	#Show the Mouse point information
	def Mouse_Information_Raw_Img(self, event):
		self.Mouse_Information(event, self.img)

	def Mouse_Information_Red_Img(self, event):
		self.Mouse_Information(event, self.red_image)
	
	def Mouse_Information_Green_Img(self, event):
		self.Mouse_Information(event, self.green_image)

	def Mouse_Information_Blue_Img(self, event):
		self.Mouse_Information(event, self.blue_image)

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
				
				if(len(img.shape) == 3):
					self.p_i_label = tk.Label(self.frmB, text = str("X : %3d, Y : %3d" % (event.x, event.y)) + ", " + str("R : %3d, G : %3d, B : %3d" % (img[event.y, event.x,0], img[event.y, event.x,1], img[event.y, event.x,2])), font = ('Arial', 12))
					p_color = np.full((16, 16, 3), img[event.y, event.x], dtype=np.uint8)
					img_PIL = Image.fromarray(p_color, 'RGB')
				else:
					self.p_i_label = tk.Label(self.frmB, text = str("X : %3d, Y : %3d" % (event.x, event.y)) + ", " + str("[%3d]" % (img[event.y, event.x])), font = ('Arial', 12))
					p_color = np.full((16, 16), img[event.y, event.x], dtype=np.uint8)
					img_PIL = Image.fromarray(p_color, 'L')
				img_PIL = ImageTk.PhotoImage(img_PIL)
				self.p_i_color = tk.Canvas(self.frmB, width=p_color.shape[1], height=p_color.shape[0])
				self.p_i_color.create_image(0, 0, image=img_PIL, anchor=tk.N + tk.W)
				self.p_i_color.image = img_PIL
				self.p_i_label.grid(column = 0, row = 0, sticky = tk.N)
				self.p_i_color.grid(column = 1, row = 0, sticky = tk.S)

	def Bind_Shortcut_key(self):
		self.parent.bind_all("<Control-s>", self.Save_File_Huffman)
		self.parent.bind_all("<Control-b> <Key-1>", self.Magnify_Duplicate_Image)
		self.parent.bind_all("<Control-b> <Key-2>", self.Magnify_Interpolation_Image)
		self.parent.bind_all("<Control-s> <Key-1>", self.Minify_Delete_Image)
		self.parent.bind_all("<Control-s> <Key-2>", self.Minify_Mean_Image)
		self.parent.bind_all("<Control-r> <Key-1>", self.Rotation_Version_1)
		self.parent.bind_all("<Control-r> <Key-2>", self.Rotation_Version_2)
		self.parent.bind_all("<Control-c> <Key-1>", self.Cut_Oval_Image)
		self.parent.bind_all("<Control-c> <Key-2>", self.Cut_Rectangle_Image)
		self.parent.bind_all("<Control-m> <Key-m>", self.Magic_Wand)
		self.parent.bind_all("<Control-r>", self.RGB_image)
		self.parent.bind_all("<Control-h>", self.Histogram_Image)
		self.parent.bind_all("<Control-g>", self.Color_To_Gray)
		self.parent.bind_all("<Control-b>", self.Gray_To_BW)
		self.parent.bind_all("<Control-t>", self.Transparent_Image)
		self.parent.bind_all("<Control-i>", self.Invert_Image)
		self.parent.bind_all("<Control-t> <Key-h>", self.Threshold)
		self.parent.bind_all("<Control-g> <Key-m>", self.Gamma_Correction)
		self.parent.bind_all("<Control-o> <Key-s>", self.Otsus_Threshold)
		self.parent.bind_all("<Control-k>", self.Kullback)
		self.parent.bind_all("<Control-c> <Key-s>", self.Contrast_Stretching)
		self.parent.bind_all("<Control-b> <Key-c>", self.Bit_plane_Slicing_Binary)
		self.parent.bind_all("<Control-g> <Key-c>", self.Bit_plane_Slicing_Gray)
		self.parent.bind_all("<Control-w>", self.Watermark)
		self.parent.bind_all("<Control-h> <Key-e>", self.Histogram_Equalization)
		self.parent.bind_all("<Control-h> <Key-s>", self.Histogram_Specification)
		self.parent.bind_all("<Control-c>", self.Connected_Components)
		self.parent.bind_all("<Control-f> <Key-o>", self.Outlier)
		self.parent.bind_all("<Control-f> <Key-m>", self.Mean_Median)
		self.parent.bind_all("<Control-f> <Key-p>", self.Pseudo_Median)
		self.parent.bind_all("<Control-f> <Key-h>", self.Highpass)
		self.parent.bind_all("<Control-f> <Key-e>", self.Edge_Crispening)
		self.parent.bind_all("<Control-f> <Key-b>", self.High_Boost)
		self.parent.bind_all("<Control-f> <Key-r>", self.Roberts_Sobel_Prewitt)
		self.parent.bind_all("<Control-f> <Key-c>", self.Canny_Algorithm)
		

	#Read Image File
	def BW_image(self, header, data): #Process B/W image
		XSize = header.XEnd - header.XStart + 1
		YSize = header.YEnd - header.YStart + 1
		TotalBytes = header.NumBitPlanes * header.BytesPerLine
		image = np.zeros((YSize, XSize, 3), dtype=np.uint8)
		data_index = 0
		for i in range(0, YSize):
			image_index = 0
			image_byte = 0
			while(1):
				if(data[data_index] > 0xC0):
					length = data[data_index] - 192
					value = data[data_index + 1]
					data_index = data_index + 2
				else:
					length = 1
					value = data[data_index]
					data_index += 1
				while(length > 0):
					take = 128
					for t in range(0, 8):
						if(value & take == take):
							image[i, image_index] = [1,1,1]
						else:
							image[i, image_index] = [0,0,0]
						take >>= 1
						image_index += 1
						if(image_index >= XSize):
							break
					length -= 1
					image_byte += 1
				if(image_byte >= TotalBytes):
					break
		image = Image.fromarray((image * 255))
		return image

	def _24b_image(self, header, data):
		XSize = header.XEnd - header.XStart + 1
		YSize = header.YEnd - header.YStart + 1
		TotalBytes = header.NumBitPlanes * header.BytesPerLine
		image = np.zeros((YSize, XSize, 3), dtype=np.uint8)
		data_index = 0
		for i in range(0, YSize):
			image_byte = 0
			for l in range(0,3):
				image_byte = 0
				while(image_byte < TotalBytes / 3):
					if(data_index >= len(data)):
						break
					if(data[data_index] > 0xC0):
						length = data[data_index] - 192
						value = data[data_index + 1]
						data_index += 2
					else:
						length = 1
						value = data[data_index]
						data_index += 1
					if(image_byte + length <= XSize):
						image[i, image_byte:image_byte + length, l] = value
						image_byte += length
					else:
						image[i, image_byte:XSize, l] = value
						image_byte = XSize
						break
		return image

	def _256_image(self, header, data):
		XSize = header.XEnd - header.XStart + 1
		YSize = header.YEnd - header.YStart + 1
		TotalBytes = header.NumBitPlanes * header.BytesPerLine
		image = np.zeros((YSize, XSize, 3), dtype=np.uint8)
		data_index = 0
		for i in range(0, YSize):
			image_byte = 0
			while(image_byte < TotalBytes):
				if(data_index >= len(data) or data_index + 1 >= len(data)):
						break
				if(data[data_index] > 0xC0):
					length = data[data_index] - 192
					value = data[data_index + 1]
					data_index += 2
				else:
					length = 1
					value = data[data_index]
					data_index += 1
				value = self.Extend_Palette[value]
				if(image_byte + length > XSize):
					image[i, image_byte:XSize] = value
					image_byte = XSize
				else:
					image[i, image_byte:image_byte + length] = value
					image_byte += length
				if(image_byte >= XSize):
					break
		return image

	def _Extend_Palette(self, s):
		Extend_Palette = np.zeros((256, 3))
		#if (s[0] == 12) and (len(s) == 769):
			#s = s[1:]
		for i in range(0, 256):
			Extend_Palette[i] = [s[i * 3], s[i * 3 + 1], s[i * 3 + 2]]
		return Extend_Palette

	#Bouncing ball
	def Bouncing_ball(self):
		B_Ball(self.parent)


def main():
	myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
	ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
	app = tk.Tk()
	app.iconphoto(False, tk.PhotoImage(file='icon/icon.png'))
	ui = UI(app)
	#app.mainloop()

if __name__ == '__main__':
	main()