from tkinter import filedialog, messagebox, ttk
import tkinter as tk
import json


class Node(object):
	def __init__(self, left = None, right = None):
		self.left = left
		self.right = right

	def children(self):
		return (self.left, self.right)

class Huffman():
	def __init__(self, parent, img):
		self.parent = parent
		self.img = img
		self.color = len(self.img.shape)

		self.new_window = tk.Toplevel(self.parent)
		self.new_window.title("Huffman")
		if(self.color == 3):
			self.new_window.geometry("1100x400")
		else:
			self.new_window.geometry("400x400")

		self.Huffman_Cost = 0
		self.Fix_Cost = 0
		self.Histogram()
		self.Coding()
		self.Show()
		self.Save()

	def Histogram(self):
		if(self.color == 3):
			self.red_h = {}
			self.green_h = {}
			self.blue_h = {}
			for i in range(self.img.shape[0]):
				for l in range(self.img.shape[1]):
					if(str(self.img[i, l, 0]) in self.red_h):
						self.red_h[str(self.img[i, l, 0])] += 1
					else:
						self.red_h[str(self.img[i, l, 0])] = 1
					if(str(self.img[i, l, 1]) in self.green_h):
						self.green_h[str(self.img[i, l, 1])] += 1
					else:
						self.green_h[str(self.img[i, l, 1])] = 1
					if(str(self.img[i, l, 2]) in self.blue_h):
						self.blue_h[str(self.img[i, l, 2])] += 1
					else:
						self.blue_h[str(self.img[i, l, 2])] = 1
		else:
			self.grey_h = {}
			for i in range(self.img.shape[0]):
				for l in range(self.img.shape[1]):
					if(str(self.img[i, l]) in self.grey_h):
						self.grey_h[str(self.img[i, l])] += 1
					else:
						self.grey_h[str(self.img[i, l])] = 1

	def Coding(self):
		if(self.color == 3):
			self.red_h = sorted(self.red_h.items(), key = lambda x: x[1], reverse = True)
			self.green_h = sorted(self.green_h.items(), key = lambda x: x[1], reverse = True)
			self.blue_h = sorted(self.blue_h.items(), key = lambda x: x[1], reverse = True)

			N = self.red_h
			while(len(N) > 1):
				#freq最小的兩個
				(key1, n1) = N[-1]
				(key2, n2) = N[-2]
				N = N[:-2]
				node = Node(key1, key2)
				N.append((node, n1 + n2))
				N = sorted(N, key = lambda x: x[1], reverse = True)

			self.r_huffmanCode = self.huffman_code_tree(N[0][0])
			for f, code in self.r_huffmanCode.items():
				self.Huffman_Cost += int(f) * len(code)
				self.Fix_Cost += int(f) * 8
			
			N = self.green_h
			while(len(N) > 1):
				#freq最小的兩個
				(key1, n1) = N[-1]
				(key2, n2) = N[-2]
				N = N[:-2]
				node = Node(key1, key2)
				N.append((node, n1 + n2))
				N = sorted(N, key = lambda x: x[1], reverse = True)

			self.g_huffmanCode = self.huffman_code_tree(N[0][0])
			for f, code in self.g_huffmanCode.items():
				self.Huffman_Cost += int(f) * len(code)
				self.Fix_Cost += int(f) * 8

			N = self.blue_h
			while(len(N) > 1):
				#freq最小的兩個
				(key1, n1) = N[-1]
				(key2, n2) = N[-2]
				N = N[:-2]
				node = Node(key1, key2)
				N.append((node, n1 + n2))
				N = sorted(N, key = lambda x: x[1], reverse = True)

			self.b_huffmanCode = self.huffman_code_tree(N[0][0])
			for f, code in self.b_huffmanCode.items():
				self.Huffman_Cost += int(f) * len(code)
				self.Fix_Cost += int(f) * 8

		else:
			self.grey_h = sorted(self.grey_h.items(), key = lambda x: x[1], reverse = True)
			
			N = self.grey_h
			while(len(N) > 1):
				#freq最小的兩個
				(key1, n1) = N[-1]
				(key2, n2) = N[-2]
				N = N[:-2]
				node = Node(key1, key2)
				N.append((node, n1 + n2))
				N = sorted(N, key = lambda x: x[1], reverse = True)
			self.huffmanCode = self.huffman_code_tree(N[0][0])
			for f, code in self.huffmanCode.items():
				self.Huffman_Cost += int(f) * len(code)
				self.Fix_Cost += int(f) * 8

	def huffman_code_tree(self, node, binString = ''):
		if(type(node) is str):
			return {node: str(int(binString))}
		(l, r) = node.children()
		d = dict()
		d.update(self.huffman_code_tree(l, (binString + '0')))
		d.update(self.huffman_code_tree(r, (binString + '1')))
		return d

	def Save(self):
		if(self.color == 3):
			with open("HuffmanCode.txt", "w") as f:
				f.write(str(self.img.shape))
				f.write("\n")
				f.write(json.dumps(self.r_huffmanCode))
				f.write("\n")
				f.write(json.dumps(self.g_huffmanCode))
				f.write("\n")
				f.write(json.dumps(self.b_huffmanCode))
				f.write("\n\n")
				for i in range(self.img.shape[0]):
					for l in range(self.img.shape[1]):
						f.write(self.r_huffmanCode[str(self.img[i, l, 0])] + " ")
				f.write("\n")
				for i in range(self.img.shape[0]):
					for l in range(self.img.shape[1]):
						f.write(self.g_huffmanCode[str(self.img[i, l, 1])] + " ")

				f.write("\n")
				for i in range(self.img.shape[0]):
					for l in range(self.img.shape[1]):
						f.write(self.b_huffmanCode[str(self.img[i, l, 2])] + " ")

		else:
			with open("HuffmanCode.txt", "w") as f:
				f.write(str(self.img.shape))
				f.write("\n")
				f.write(json.dumps(self.huffmanCode))
				f.write("\n\n")
				for i in range(self.img.shape[0]):
					for l in range(self.img.shape[1]):
						f.write(self.huffmanCode[str(self.img[i, l])] + " ")
		

	def Show(self):
		print(self.Fix_Cost / self.Huffman_Cost)
		label = tk.Label(self.new_window, text = "壓縮比：" + str(round(self.Fix_Cost / self.Huffman_Cost, 2)), font = ('Arial', 14))
		label.grid(column = 0, row = 0)

		if(self.color == 3):
			label = tk.Label(self.new_window, text = "Red")
			label.grid(column = 0, row = 1)

			Data_Tree = ttk.Treeview(self.new_window, show="tree", columns=("Fix", "Freq.", "Huffman"), height = 15)
			Data_Tree['show'] = "headings"
			Data_Tree.column("Fix", width = 80, anchor = 'center')
			Data_Tree.column("Freq.", width = 80, anchor = 'center')
			Data_Tree.column("Huffman", width = 150, anchor = 'center')
			Data_Tree.heading("Fix", text = "Fix")
			Data_Tree.heading("Freq.", text = "Freq.")
			Data_Tree.heading("Huffman", text = "Huffman")
			Data_Tree.grid(column = 0, row = 2, padx = 10, pady = 10)
			vsb = ttk.Scrollbar(self.new_window, orient="vertical", command=Data_Tree.yview)
			Data_Tree.configure(yscrollcommand = vsb.set)
			vsb.grid(column = 1, row = 2, sticky='ns')
			for (d, f) in self.red_h:
				Data_Tree.insert('', 'end', text = d, value = (str(d), str(f), str(self.r_huffmanCode[d])))

			label = tk.Label(self.new_window, text = "Green")
			label.grid(column = 2, row = 1)

			Data_Tree = ttk.Treeview(self.new_window, show="tree", columns=("Fix", "Freq.", "Huffman"), height = 15)
			Data_Tree['show'] = "headings"
			Data_Tree.column("Fix", width = 80, anchor = 'center')
			Data_Tree.column("Freq.", width = 80, anchor = 'center')
			Data_Tree.column("Huffman", width = 150, anchor = 'center')
			Data_Tree.heading("Fix", text = "Fix")
			Data_Tree.heading("Freq.", text = "Freq.")
			Data_Tree.heading("Huffman", text = "Huffman")
			Data_Tree.grid(column = 2, row = 2, padx = 10, pady = 10)
			vsb = ttk.Scrollbar(self.new_window, orient="vertical", command=Data_Tree.yview)
			Data_Tree.configure(yscrollcommand = vsb.set)
			vsb.grid(column = 3, row = 2, sticky='ns')
			for (d, f) in self.green_h:
				Data_Tree.insert('', 'end', text = d, value = (str(d), str(f), str(self.g_huffmanCode[d])))

			label = tk.Label(self.new_window, text = "Blue")
			label.grid(column = 4, row = 1)
			Data_Tree = ttk.Treeview(self.new_window, show="tree", columns=("Fix", "Freq.", "Huffman"), height = 15)
			Data_Tree['show'] = "headings"
			Data_Tree.column("Fix", width = 80, anchor = 'center')
			Data_Tree.column("Freq.", width = 80, anchor = 'center')
			Data_Tree.column("Huffman", width = 150, anchor = 'center')
			Data_Tree.heading("Fix", text = "Fix")
			Data_Tree.heading("Freq.", text = "Freq.")
			Data_Tree.heading("Huffman", text = "Huffman")
			Data_Tree.grid(column = 4, row = 2, padx = 10, pady = 10)
			vsb = ttk.Scrollbar(self.new_window, orient="vertical", command=Data_Tree.yview)
			Data_Tree.configure(yscrollcommand = vsb.set)
			vsb.grid(column = 5, row = 2, sticky='ns')
			for (d, f) in self.blue_h:
				Data_Tree.insert('', 'end', text = d, value = (str(d), str(f), str(self.b_huffmanCode[d])))

		else:
			label = tk.Label(self.new_window, text = "Grey")
			label.grid(column = 0, row = 1)
			Data_Tree = ttk.Treeview(self.new_window, show="tree", columns=("Fix", "Freq.", "Huffman"), height = 15)
			Data_Tree['show'] = "headings"
			Data_Tree.column("Fix", width = 80, anchor = 'center')
			Data_Tree.column("Freq.", width = 80, anchor = 'center')
			Data_Tree.column("Huffman", width = 150, anchor = 'center')
			Data_Tree.heading("Fix", text = "Fix")
			Data_Tree.heading("Freq.", text = "Freq.")
			Data_Tree.heading("Huffman", text = "Huffman")
			Data_Tree.grid(column = 0, row = 1, padx = 10, pady = 10)
			vsb = ttk.Scrollbar(self.new_window, orient="vertical", command=Data_Tree.yview)
			Data_Tree.configure(yscrollcommand = vsb.set)
			vsb.grid(column = 1, row = 1, sticky='ns')
			for (d, f) in self.grey_h:
				Data_Tree.insert('', 'end', text = d, value = (str(d), str(f), str(self.huffmanCode[d])))
