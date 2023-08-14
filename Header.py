from struct import unpack_from

#Header Information
class Header():
	def __init__(self, h):
		self.h = h
		self.save_header()
	def save_header(self):
		self.Manufacturer = self.h[0]
		self.Version = self.h[1]										# 5->palette=-768, start with 0x0C
		self.Encoding = self.h[2]										# 1->RLE
		self.BitsPerPixel = self.h[3]									#color: 1->B/W 2, 4, 8
		self.XStart = unpack_from("<H", self.h, 4)[0]					#Left of image
		self.YStart = unpack_from("<H", self.h, 6)[0]					#Top of Image
		self.XEnd = unpack_from("<H", self.h, 8)[0]						#Right of Image
		self.YEnd = unpack_from("<H", self.h, 10)[0]					#Bottom of image
		self.HorzRes = unpack_from("<H", self.h, 12)[0]					
		self.VertRes = unpack_from("<H", self.h, 14)[0]
		self.Palette = list(self.h[16:64])
		self.Reserved = self.h[64]
		self.NumBitPlanes = self.h[65]									
		self.BytesPerLine = unpack_from("<H", self.h, 66)[0]
		self.PaletteType = unpack_from("<H", self.h, 68)[0]				#1->color, 2->gray
		self.HorzScreenSize = unpack_from("<H", self.h, 70)[0]
		self.VertScreenSize = unpack_from("<H", self.h, 72)[0]