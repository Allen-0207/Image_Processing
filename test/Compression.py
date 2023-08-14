import tkinter as tk
from PIL import ImageTk, Image
import numpy as np
from tkinter import filedialog, messagebox, ttk
import cv2 as cv
import time, threading

class Video_Compression():
	def __init__(self):
		self.Compression()

	def Compression(self):
		'''
		self.filename = ['C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.01.tiff', \
		'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.02.tiff', \
		'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.03.tiff', \
		'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.04.tiff', \
		'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.05.tiff', \
		'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.06.tiff', \
		'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.07.tiff', \
		'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.08.tiff', \
		'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.09.tiff', \
		'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.10.tiff', \
		'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.11.tiff', \
		'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.12.tiff', \
		'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.13.tiff', \
		'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.14.tiff', \
		'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.15.tiff', \
		'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.16.tiff']
		
		self.filename = ['C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion01.512.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion02.512.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion03.512.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion04.512.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion05.512.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion06.512.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion07.512.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion08.512.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion09.512.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion10.512.tiff']
		
		self.filename = ['C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.01.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.02.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.03.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.04.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.05.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.06.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.07.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.08.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.09.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.10.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.11.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.12.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.13.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.14.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.15.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.16.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.17.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.18.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.19.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.20.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.21.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.22.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.23.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.24.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.25.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.26.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.27.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.28.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.29.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.30.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.31.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.32.tiff']
		'''

		self.filename = ['C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences4/6.3.01.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences4/6.3.02.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences4/6.3.03.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences4/6.3.04.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences4/6.3.05.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences4/6.3.06.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences4/6.3.07.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences4/6.3.08.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences4/6.3.09.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences4/6.3.10.tiff', \
							'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences4/6.3.11.tiff']

							
		self.total_file = len(self.filename)
		self.Compression_Start()
			
	def Compression_Start(self, done = None):
		for n in range(self.total_file - 1):
			im1 = Image.open(self.filename[n])
			im2 = Image.open(self.filename[n + 1])
			print(self.filename[n], self.filename[n + 1])
			self.img1 = np.array(im1)
			self.img2 = np.array(im2)
			size1 = int(self.img1.shape[0] / 8)
			size2 = int(self.img1.shape[1] / 8)
			self.Motion_Vector = [[None] * size1 for i in range(size2)]
			self.Compression_Find()	
			self.Save()			

	def Compression_Find(self):
		for i in range(0, self.img2.shape[0], 8):
			for l in range(0, self.img2.shape[1], 8):
				self.target_block = self.img2[i : i + 8, l : l + 8]
				
				self.m_x = 0
				self.m_y = 0

				print(i, l)
				t = threading.Thread(target = self.Find_Matching)
				t.start()
				t.join()
				#print("Done")
				#print(i, l)
				#print(self.m_x, self.m_y)
				self.Motion_Vector[int(i / 8)][int(l / 8)] = (self.m_x, self.m_y)
		print(self.Motion_Vector)
		

	def Find_Matching(self):
		self.match_block = np.zeros((8, 8), dtype=np.uint8)
		min_MAD = 8 * 8 * 255
		
		for i in range(self.img1.shape[0] - 7):
			for l in range(self.img1.shape[0] - 7):
				#print((i, l))
				candidate_block = self.img1[i : i + 8, l : l + 8]
				MAD = 0
				for x in range(8):
					for y in range(8):
						MAD += abs(int(self.target_block[x, y]) - int(candidate_block[x, y]))

				if(MAD < min_MAD):
					min_MAD = MAD
					self.match_block = candidate_block
					self.m_x = i + 4
					self.m_y = l + 4
	def Save(self):
		with open("6.3.txt", 'a') as f:
			f.write(str(self.Motion_Vector) + "\n")

def main():
	Video_Compression()

if __name__ == '__main__':
	main()