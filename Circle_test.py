import tkinter as tk

class main():

	def __init__(self, parent=None):
		app = tk.Tk()
		self.canvas = tk.Canvas(app, width=1200, height=800)
		self.canvas.grid(column=0, row=0)
		self.canvas.bind("<Button-1>", self.OnStart)
		self.canvas.bind("<B1-Motion>", self.onGrow)
		self.canvas.bind("<ButtonRelease-1>", self.add_circle)
		#self.canvas = self.canvas
		self.drawn  = None
		app.mainloop()

	def OnStart(self, event):
		self.shape = self.canvas.create_rectangle
		self.start = event

	def onGrow(self, event):                         
		canvas = event.widget
		if self.drawn:
			canvas.delete(self.drawn)
		objectId = self.shape(self.start.x, self.start.y, event.x, event.y, dash = (5, 1))
		self.drawn = objectId
	
	def add_circle(self, event):
		canvas = event.widget
		if self.drawn:
			canvas.delete(self.drawn)
		objectId = self.shape(self.start.x, self.start.y, event.x, event.y)
		self.drawn = objectId
		print(self.shape == self.canvas.create_oval)
		print(self.drawn)
		print(self.start.x, self.start.y, event.x, event.y)
	
	

if __name__ == '__main__':
	main()