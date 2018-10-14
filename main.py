import sqlite3
from tkinter import *
import tkinter.messagebox as mbox
import random

class MainWindow(Frame):
	"""docstring for MainWindow"""
	def __init__(self, parent):
		super().__init__(parent, background = 'white')
		self.parent = parent
		self.initUI()
		self.centerWindow()
		self.conn = sqlite3.connect('datebase/dates')
		self.curs = self.conn.cursor()
		self.curs.execute('select * from history')
		self.spisok = []
		for x in self.curs.fetchall():
			self.spisok.append([item for item in x])

		self.spisok = sorted(self.spisok, key = self.by_number)
		self.idx = 0

	def centerWindow(self):
		w = 620
		h = 400
		sw = self.parent.winfo_screenwidth()
		sh = self.parent.winfo_screenheight()
		x = (sw - w)/2
		y = (sh - h)/2
		self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

	def by_number(self, key):
			return int(key[0])

	def initUI(self):
		self.parent.title('Nota Bene!')

		menubar = Menu(self.parent)
		self.parent.config(menu = menubar)

		fileMenu = Menu(menubar)
		fileMenu.add_command(label="Watch Dates", command = self.watchDates, accelerator ="F2")
		self.parent.bind('<Key-F2>', self.watchDates)
		fileMenu.add_command(label="Exit", command = self.onExit)
		menubar.add_cascade(label="File", menu = fileMenu)

		watchMenu = Menu(menubar)
		watchMenu.add_command(label="Reference", command = self.reference)
		menubar.add_cascade(label="Info", menu = watchMenu)
		self.parent.bind("<Escape>", self.onExit)

		tex = "\tЭта программа создана для изучения и повторения исторических дат. Добавьте даты, которые вы хотите \
				выучить и нажмите \"Составить тест\". После того, как вы ответите на все вопросы, вам покажет количество \
				 правильных ответов и вопросы, при ответе на котоые вы ошиблись. Приятного использования!"

		mainFrame = Frame(self.parent)
		mainFrame.pack()
		title = Label(mainFrame, text = "Вас приветствует программа Nota Bene!", font = "Verdana 16")
		title.pack( pady = 5)
		text = Text(mainFrame, height = 18, font = "Consolas 10", wrap = WORD)
		text.insert(END, tex)
		text.pack(fill = BOTH)
		text.configure(state='disabled')
		button_start = Button(mainFrame, text = "Start", command = lambda *args: self.createTest())
		button_start.pack(pady = 10)
		self.parent.bind("<Return>", lambda *args: self.createTest())


	def watchDates(self, *args):
		sub = Toplevel(self)
		sub.title("Watch dates")
		sub.transient(self)
		sub.title('All dates')
		sub.minsize(320, 240)
		sub.maxsize(480, 320)

		listFrame = Frame(sub)
		listFrame.pack()
		scrollbar = Scrollbar(listFrame)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.lb = Listbox(listFrame, width = 300, yscrollcommand=scrollbar.set, exportselection = 0)
		for i in self.spisok:
			self.lb.insert(END, (' - '.join(i)))
		scrollbar.config(command=self.lb.yview)        
		self.lb.bind("<<ListboxSelect>>", self.onSelect)


		self.lb.pack(pady=15)
 
		addButton = Button(sub, text = "Add", command = lambda: self.addDate(sub))
		addButton.pack(side=LEFT, padx=5, pady=5)
		editButton = Button(sub, text = "Edit", command = lambda: self.editDate(sub))
		editButton.pack(side=LEFT, pady=5)
		delButton = Button(sub, text = "Delete", command = lambda: self.deleteDate())
		delButton.pack(side=LEFT, padx=5, pady=5)
		closeButton = Button(sub, text = "Close", command = lambda: self.closeSub(sub))
		closeButton.pack(side=RIGHT, padx=5, pady=5)

		sub.bind("<Key-F1>", lambda *args: self.addDate(sub))
		sub.bind("<Escape>", lambda *args: self.closeSub(sub))
		sub.bind("<Return>", lambda *args: self.editDate(sub))
		sub.bind("<Delete>", lambda *args: self.deleteDate())
		self.lb.select_set(0)
		self.lb.event_generate("<<ListboxSelect>>")
		sub.grab_set()
		sub.wait_window()
		sub.mainloop()


	def addDate(self, sub):
		def add():
			if ( not entryDate.get().isdigit() ):
				mbox.showerror("Error", "You date isn't number!")
			else:
				date = entryDate.get()
				event = entryEvent.get().strip();
				self.curs.execute('insert into history values (?,?)', (date, event))
				self.conn.commit()
				self.spisok.append([date, event])
				self.spisok = sorted(self.spisok, key = self.by_number)
				self.lb.insert(self.spisok.index([date, event]),' - '.join([date, event]))
				self.lb.select_clear(0, END)
				self.lb.select_set(self.spisok.index([date, event]))
				self.lb.event_generate("<<ListboxSelect>>")
				self.lb.see(self.spisok.index([date, event]))
				entryDate.delete(0, END)
				entryEvent.delete(0, END)
				entryDate.focus_set()


		subOver = Toplevel(sub)
		subOver.title("Edit date")
		subOver.transient(sub)
		subOver.minsize(320, 150)
		subOver.maxsize(320, 150)
		newDate = Label(subOver, text = "Enter date")
		newDate.place(x = 5, y = 10)
		newEvent = Label(subOver, text = "Enter event")
		newEvent.place(x = 5, y = 40)

		entryDate = Entry(subOver, width = 27)
		entryDate.place(x = 90, y = 10)
		entryDate.focus_set()
		entryEvent = Entry(subOver, width = 27)
		entryEvent.place(x = 90, y = 40)

		enter = Button(subOver, text = "Enter", command = add)
		enter.place( x = 130, y = 80)

		close = Button(subOver, text = "Close", command = lambda: self.closeSub(subOver))
		close.place(x = 250, y = 115)
		close.bind("<Return>", lambda *args: self.closeSub(subOver))

		subOver.bind("<Escape>", lambda *args: self.closeSub(subOver))
		subOver.bind("<Return>", lambda *args: add())

		subOver.grab_set()
		subOver.wait_window()
		subOver.mainloop()

	def editDate(self, sub, *args):
		def edit():
			if ( not entryDate.get().isdigit() ):
				mbox.showerror("Error", "You date isn't number!")
			else:
				date = entryDate.get()
				event = entryEvent.get().strip();
				self.lb.delete(self.idx)
				toDel = self.spisok[self.idx][0]
				self.spisok.pop(self.idx)
				self.curs.execute('delete from history where date = ?', [toDel])
				self.conn.commit()
				self.curs.execute('insert into history values (?,?)', (date, event))
				self.conn.commit()
				self.spisok.append([date, event])
				self.spisok = sorted(self.spisok, key = self.by_number)
				self.lb.insert(self.spisok.index([date, event]),' - '.join([date, event]))
				self.lb.select_set(self.spisok.index([date, event]))
				self.lb.event_generate("<<ListboxSelect>>") 
				subOver.destroy()

		try:
			subOver = Toplevel(sub)
			subOver.transient(sub)
			subOver.minsize(320, 150)
			subOver.maxsize(320, 150)
			newDate = Label(subOver, text = "Enter date")
			newDate.place(x = 5, y = 10)
			newEvent = Label(subOver, text = "Enter event")
			newEvent.place(x = 5, y = 40)

			oldDate = self.spisok[int(self.idx)][0]
			oldEvent = self.spisok[int(self.idx)][1]

			entryDate = Entry(subOver, width = 27)
			entryDate.place(x = 90, y = 10)
			entryDate.insert(0, oldDate)
			entryDate.focus_set()
			entryEvent = Entry(subOver, width = 27)
			entryEvent.place(x = 90, y = 40)
			entryEvent.insert(0, oldEvent)

			enter = Button(subOver, text = "Enter", command = edit)
			enter.place( x = 130, y = 80)

			close = Button(subOver, text = "Close", command = lambda: self.closeSub(subOver))
			close.place(x = 250, y = 115)
			close.bind("<Return>", lambda *args: self.closeSub(subOver))

			subOver.bind("<Escape>", lambda *args: self.closeSub(subOver))
			subOver.bind("<Return>", lambda *args: edit())

			subOver.grab_set()
			subOver.wait_window()
			subOver.mainloop()
		except IndexError:
			pass


	def deleteDate(self, *args):
		try:
			self.lb.delete(self.idx)
			toDel = self.spisok[self.idx][0]
			self.spisok.pop(self.idx)
			self.curs.execute('delete from history where date = ?', [toDel])
			self.conn.commit()
			self.lb.select_set(self.idx)
			self.lb.event_generate("<<ListboxSelect>>")
		except IndexError:
			pass
	
	def createTest(self):
		class TestError():
			def __init__(self, window, uncorrect):
				self.parent = window
				self.uncorrect = uncorrect
				self.addLabel()

			def addLabel(self):
				text = StringVar()
				text.set("{}. {}. Ваш ответ: {} Правильный ответ: {}".format(self.uncorrect[0], self.uncorrect[1], self.uncorrect[2], self.uncorrect[3]))
				label = Label(self.parent, textvariable = text)
				label.pack(fill = X, pady = 5)

		def startTest(ask_window):
			def testWindowCallback(test_window):
				answer = entry_question.get()
				if ( not answer.isdigit() ):
					mbox.showerror("Error", "You date isn't number!")
				else:
					if test_dict.get(answer) == self.event:
						self.points += 1
					else:
						uncorrect.append([(int(self.iterator)), question.get()[:-1], answer, iter_dict[self.event]]) # номер вопроса,вопрос, ответ, правильный ответ
					self.iterator+=1
					if self.iterator > number:
						self.closeSub(test_window)
						return showResult()
					test_window.title("{} question of {}".format(self.iterator, number))
					self.event = random.choice(events)
					events.remove(self.event)
					question.set("{}?".format(self.event))
					entry_question.delete(0, END)
					entry_question.focus_set()

			def showResult():
				result_window = Toplevel(self)
				result_window.transient(self)
				result_window.minsize(320, 140)
				result_window.title("Test is over!")
				result = StringVar()
				result.set("{} of {} correct".format(self.points, number))
				label_result = Label(result_window, textvariable = result)
				label_result.pack(pady=10)
				if len(uncorrect) > 0:
					temp_dict = {}
					for x in uncorrect:
						temp_dict[x[1]] = TestError(result_window, x)
				result_window.bind("<Escape>", lambda *args: self.closeSub(result_window))

			number = int(self.scale.get())
			if number == 0:
				self.closeSub(ask_window)
				return
			self.closeSub(ask_window)
			test_window = Toplevel(self)
			test_window.transient(self)
			test_window.minsize(320, 140)
			test_window.maxsize(320, 220)
			question = StringVar()
			label_question = Label(test_window, textvariable = question)
			label_question.pack(pady = 10)
			entry_question = Entry(test_window)
			entry_question.pack(pady = 10)
			test_dict = {}
			for x in self.spisok:
				test_dict.update({x[0]:x[1]}) #создание словаря из таблицы dates
			iter_dict = {v:k for k,v in test_dict.items()} #создание обратного словаря "событие:дата"
			events = [x for x in test_dict.values()] #создание списка событий
			self.points = 0
			uncorrect = []
			self.iterator = 1

			test_window.title("{} question of {}".format(self.iterator, number))
			self.event = random.choice(events)
			events.remove(self.event)
			question.set("{}?".format(self.event))
			entry_question.delete(0, END)
			entry_question.focus_set()
			button_enter = Button(test_window, text = "Enter", command = lambda *args: testWindowCallback(test_window))
			button_enter.pack(pady = 10)
			test_window.bind("<Escape>", lambda *args: self.closeSub(test_window))
			test_window.bind("<Return>", lambda *args: testWindowCallback(test_window))

			test_window.grab_set()
			test_window.wait_window()

			#test_window.protocol("WM_DELETE_WINDOW", self.onClosing(test_window))
			test_window.mainloop()

		ask_window = Toplevel(self)
		ask_window.transient(self)
		ask_window.minsize(320, 200)
		ask_window.maxsize(320, 220)
		ask_window.title("Creating test")
		label_1 = Label(ask_window, text = "Choose number of questions:")
		label_1.pack(pady = 10)
		self.scale = Scale(ask_window, orient=HORIZONTAL,length=300, from_=0, to=len(self.spisok), 
            command=self.onScale)
		self.scale.pack()
		self.var = StringVar()
		self.entry = Entry(ask_window, text = self.var)
		self.entry.pack(pady = 10)
		self.entry.focus_set()
		try:
			#python 3.6
			self.var.trace_add('write', lambda *args: self.onScale_callback(self.var, self.scale))
		except AttributeError:
			#python <3.6
			self.var.trace('write', lambda *args: self.onScale_callback(self.var, self.scale))
		button_start = Button(ask_window, text = "Start", command = lambda *args: startTest(ask_window))
		button_start.pack(pady = 10)
		ask_window.bind("<Return>", lambda *args: startTest(ask_window))
		ask_window.bind("<Escape>", lambda *args: self.closeSub(ask_window))
		ask_window.grab_set()
		ask_window.wait_window()
		ask_window.mainloop()
	
	def reference(self):
		ref_window = Toplevel(self)
		ref_window.transient(self)
		ref_window.minsize(320, 80)
		ref_window.maxsize(320, 220)
		ref_window.title("Creating test")
		label_1 = Label(ref_window, text = "Nota Bene! Created by Mehnar 2018 v0.0.1")
		label_1.pack(pady = 20)
		ref_window.bind("<Escape>", lambda *args: self.closeSub(ref_window))

	def onSelect(self, val):
		sender = val.widget
		try:
			self.idx = sender.curselection()[0]
		except IndexError:
			pass
		value = sender.get(self.idx)

	def closeSub(self, sub):
		sub.destroy()

	def onExit(self, args):
		self.quit()	

	def onScale_callback(self, var, scale):
		i = self.var.get()
		if ( not i.isdigit()):
			return
		i = int(i)
		if ( i > len(self.spisok)):
			i = len(self.spisok)
		elif ( i == ''):
			i = 0
		self.scale.set(i)

	def onScale(self, val):
		self.entry.delete(0, END)
		self.entry.insert(0, val)

	#def onClosing(self, sub):
	#	if mbox.askokcancel("Quit", "Do you really want to quit?"):
	#		sub.destroy()

def main():
	root = Tk()
	global app
	app = MainWindow(root)


	root.mainloop()
	
if __name__ == '__main__':
    main()