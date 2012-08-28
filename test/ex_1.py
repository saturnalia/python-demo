import os
import sys
import Tkinter
import threading
from Tkconstants import *

class GUI(threading.Thread):
	def __init__(self,state):
		global st, q, smsdb
		st = state
		


		tk = Tkinter.Tk()
		frame = Tkinter.Frame(tk, relief=RIDGE, borderwidth=2)
		frame.pack(fill=BOTH,expand=10)
		label = Tkinter.Label(frame, text="Hello, World..................................................................................")
		label.pack(fill=X, expand=1)
		button = Tkinter.Button(frame,text="Exit",command=tk.destroy)
		button.pack(side=TOP)
		tk.mainloop()


if __name__ == "__main__":
	gui = GUI(0)