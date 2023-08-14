import tkinter as tk


class B_Ball():
	def __init__(self, parent):
		self.parent = parent
		new_window = tk.Toplevel(self.parent)
		new_window.title("Bouncing ball")
		new_window.geometry("1200x650")
		
		self.bouncing_canvas = tk.Canvas(new_window, width = 1200, height = 600, highlightbackground = "black", highlightthickness = 1)
		self.bouncing_canvas.grid(column = 0, row = 0, columnspan = 4)
		self.ball = self.bouncing_canvas.create_oval(580, 300, 620, 340, width = 0, fill = 'blue')

		self.x_box = tk.Spinbox(new_window, from_ = -5, to = 5)
		self.y_box = tk.Spinbox(new_window, from_ = -5, to = 5)
		go_Btn = tk.Button(new_window, text="Go", command = self.go)
		stop_Btn = tk.Button(new_window, text="Stop", command = self.stop)
		self.x_box.grid(column = 0, row = 1, padx = 10, pady = 10)
		self.y_box.grid(column = 1, row = 1, padx = 10, pady = 10)
		go_Btn.grid(column = 2, row = 1, padx = 10, pady = 10)
		stop_Btn.grid(column = 3, row = 1, padx = 10, pady = 10)
		self.job = None
		self.x = 0
		self.y = 0

	def go(self):
		self.x = int(self.x_box.get())
		self.y = int(self.y_box.get())
		n = max(abs(self.x), (self.y))
		for i in range(2, n):
			while(self.x % i == 0 and self.y % i == 0):
				self.x = self.x / i
				self.y = self.y / i
		self.run()

	def run(self):
		x1, y1, x2, y2 = self.bouncing_canvas.coords(self.ball)
		if x1 <= 0 or x2 >= 1200:
			# hit wall, reverse x speed
			self.x = -self.x
		if y1 <= 0 or y2 >= 600:
			# hit top wall
			self.y = -self.y
		self.bouncing_canvas.move(self.ball, self.x, self.y)
		self.job = self.bouncing_canvas.after(40, self.run)

	def stop(self):
		if(self.run is not None):
			self.bouncing_canvas.after_cancel(self.job)