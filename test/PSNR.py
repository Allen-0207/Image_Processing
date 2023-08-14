import numpy as np
from PIL import ImageTk, Image
import math

def PSNR():
	'''
	filename = ['C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences1/6.1.01.tiff', \
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
	'''
	'''
	filename = ['C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences2/6.2.01.tiff', \
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
	'''
	filename = ['C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences4/6.3.01.tiff', \
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
	'''

	filename = ['C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion01.512.tiff', \
				'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion02.512.tiff', \
				'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion03.512.tiff', \
				'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion04.512.tiff', \
				'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion05.512.tiff', \
				'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion06.512.tiff', \
				'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion07.512.tiff', \
				'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion08.512.tiff', \
				'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion09.512.tiff', \
				'C:/Users/allen/Desktop/碩士課程/影像處理/image-processing/sequences/sequences3/motion10.512.tiff']


	im = Image.open(filename[0])
	img = np.array(im)

	total_file = 0
	All_img = [img]
	All_Moction_Vector = []
	Total_PSNR = []
	with open(r"C:\Users\allen\Desktop\碩士課程\影像處理\homework\mot.txt", 'r') as fp:
		while(1):
			txt = fp.readline()
			total_file += 1
			if(len(txt) == 0):
				break
			else:
				motion_vector = eval(txt)
				All_Moction_Vector.append(motion_vector)
				img = Next_Image(All_img[total_file - 1], motion_vector)
				All_img.append(img)
				im1 = Image.open(filename[total_file])
				img1 = np.array(im1)
				Total_PSNR.append(Cal_PSNR(img1, img))
	print(Total_PSNR)

def Next_Image(img, motion_vector):
	img1 = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
	for i in range(len(motion_vector)):
		for l in range(len(motion_vector[0])):
			(x, y) = motion_vector[i][l]
			img1[i * 8 : (i + 1) * 8, l * 8 : (l + 1) * 8] = img[x - 4 : x + 4, y - 4 : y + 4]
	return img1

def Cal_PSNR(img1, img2):
	psnr = 0
	for i in range(img1.shape[0]):
		for l in range(img1.shape[1]):
			psnr += pow((int(img1[i, l]) - int(img2[i, l])), 2)
	psnr /= (img1.shape[0] * img1.shape[1])
	psnr = round(10 * math.log10((255 ** 2) / psnr), 2)
	return psnr

def main():
	PSNR()

if __name__ == '__main__':
	main()