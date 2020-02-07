from tkinter import *
from tkinter import ttk, filedialog, messagebox, Text
from datetime import datetime, date
import re
import logging
import openpyxl
from queue import Queue
from collections import defaultdict
from store_ref import BasicInfo, Shareholders, Investment, TreeList
from qcm_info import Company, NaturalPerson, get_cookies, worker, write_to_excel
import threading
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

pipe = Queue()


class MainScreen:

	def __init__(self):
		self.root = Tk()
		self.root.title("企查猫信息搜索器")
		self.root.geometry("400x500+50+20")

		self.input_panel = ttk.Frame(self.root, borderwidth=2, relief="raised")
		self.display_panel = ttk.Frame(self.root, borderwidth=2, relief="raised")
		self.tree = TreeList(self.display_panel)
		self.log_panel = ttk.Frame(self.root, borderwidth=2, relief="raised")
		self.url_string = StringVar(self.root,
									value="https://www.qichamao.com/orgcompany/searchitemdtl/5c39c6a3a47ab0b3e6e0416acb7944fe.html")
		self.url_input_lable = ttk.Label(self.input_panel, text="请输入网址: ")
		self.url_input_entry = ttk.Entry(self.input_panel, textvariable=self.url_string)
		self.start_search_button = ttk.Button(self.input_panel, text="开始搜索!", command=self.search)
		self.level_string = StringVar(self.root, value=6)
		self.level_label = ttk.Label(self.input_panel, text="请输入层数： ")
		self.level_entry = ttk.Entry(self.input_panel, textvariable=self.level_string)
		self.log_pane_main = ttk.Notebook(self.log_panel)
		self.log_pane1_1 = ttk.Frame(self.log_pane_main)
		self.log_text_note = Text(self.log_pane1_1)

		self.log_pane1_2 = ttk.Frame(self.log_pane_main)
		self.company_basic_info = BasicInfo(self.log_pane1_2)

		self.log_text_note.grid(column=0, row=0, sticky="news")
		self.company_basic_info.grid(column=0, row=0, sticky="news")

		self.log_panel_3 = ttk.Frame(self.log_pane_main)
		self.shareholders = Shareholders(self.log_panel_3)

		self.log_pane1_4 = ttk.Frame(self.log_pane_main)
		self.investment = Investment(self.log_pane1_4)

		self.log_pane1_1.grid(column=0, row=0, sticky="news")
		self.log_pane1_2.grid(column=0, row=0, sticky="news")
		self.log_panel_3.grid(column=0, row=0, sticky="news")
		self.log_pane1_4.grid(column=0, row=0, sticky="news")
		self.log_pane1_1.name = self.log_pane_main
		self.log_pane1_2.name = self.log_pane_main
		self.log_panel_3.name = self.log_pane_main
		self.log_pane1_4.name = self.log_pane_main
		self.log_pane_main.add(self.log_pane1_1, text="运行数据", compound=TOP)
		self.log_pane_main.add(self.log_pane1_2, text="工商基本信息")
		self.log_pane_main.add(self.log_panel_3, text="股东信息")
		self.log_pane_main.add(self.log_pane1_4, text="对外投资")
		self.input_panel.grid(column=0, row=0, padx=0.5, pady=0.5, sticky="news")
		self.display_panel.grid(column=0, row=1, padx=0.5, pady=0.5, sticky="news")
		self.tree.grid(column=0, row=0, padx=0.5, pady=0.5, sticky="news")
		self.log_panel.grid(column=0, row=2, padx=0.5, pady=0.5, sticky="news")
		self.url_input_lable.grid(column=0, row=0, padx=0.5, pady=0.5, sticky="w")
		self.url_input_entry.grid(column=1, row=0, padx=0.5, pady=0.5, sticky="ew")
		self.level_label.grid(column=2, row=0, padx=0.5, pady=0.5, sticky="w")
		self.level_entry.grid(column=3, row=0, padx=0.5, pady=0.5, sticky="ew")
		self.start_search_button.grid(column=4, row=0, padx=0.5, pady=0.5, sticky="w")
		self.log_pane_main.grid(column=0, row=0, padx=0.5, pady=0.5, sticky="news")
		self.root.grid_columnconfigure(0, weight=1)
		self.input_panel.columnconfigure(1, weight=1)
		self.input_panel.columnconfigure(3, weight=1)
		self.input_panel.rowconfigure(0, weight=1)
		self.input_panel.grid_columnconfigure(1, weight=1)
		self.input_panel.grid_columnconfigure(3, weight=1)
		self.input_panel.grid_rowconfigure(0, weight=1)
		self.display_panel.grid_rowconfigure(0, weight=1)
		self.display_panel.grid_columnconfigure(0, weight=1)
		self.log_panel.grid_columnconfigure(0, weight=1)
		self.log_panel.grid_rowconfigure(0, weight=1)
		self.log_panel.columnconfigure(0, weight=1)
		self.log_panel.rowconfigure(0, weight=1)
		self.log_pane1_1.grid_rowconfigure(0, weight=1)
		self.log_pane1_1.grid_columnconfigure(0, weight=1)
		self.log_pane1_1.rowconfigure(0, weight=1)
		self.log_pane1_1.columnconfigure(0, weight=1)
		self.log_pane1_2.grid_rowconfigure(0, weight=1)
		self.log_pane1_2.grid_columnconfigure(0, weight=1)
		self.log_panel_3.rowconfigure(0, weight=1)
		self.log_panel_3.columnconfigure(0, weight=1)
		self.log_panel_3.grid_rowconfigure(0, weight=1)
		self.log_panel_3.grid_columnconfigure(0, weight=1)
		self.log_panel_3.rowconfigure(0, weight=1)
		self.log_panel_3.columnconfigure(0, weight=1)
		self.log_pane1_4.rowconfigure(0, weight=1)
		self.log_pane1_4.columnconfigure(0, weight=1)
		self.log_pane1_4.grid_rowconfigure(0, weight=1)
		self.log_pane1_4.grid_columnconfigure(0, weight=1)
		self.log_pane1_4.rowconfigure(0, weight=1)
		self.log_pane1_4.columnconfigure(0, weight=1)

		self.tree.bind("<<TreeviewSelect>>", self.get_item)
		self.current_company = StringVar(self.root)
		self.root.mainloop()

	def search(self):

		self.tree.delete(*self.tree.get_children())
		Company.flush()
		NaturalPerson.flush()

		def process_work(queue, url, level, workers):
			# event = threading.Event()
			root_company = Company(level=1, url=url, name=None)
			queue.put(root_company)
			for i in range(8):
				queue.put('1')

			with ThreadPoolExecutor(max_workers=workers) as executor:
				for i in range(workers):
					executor.submit(worker, queue, level)
			return root_company

		root_company = process_work(pipe, self.url_string.get(), int(self.level_string.get()), 8)
		write_to_excel(int(self.level_string.get()))
		self.tree.generate_tree(root_node=root_company)
		self.tree.show()
		self.current_company.set(root_company.key)
		self.display_basic_info(key=self.current_company.get())
		return

	def get_item(self, event):
		_current_company = event.widget.selection()
		if _current_company[0] == self.current_company.get():
			return
		else:
			self.current_company.set(_current_company[0])
			self.display_basic_info(key=self.current_company.get())
		return

	def display_basic_info(self, key):
		company_instance = Company.get_company(uid=key)
		logging.info("currently displaying {}".format(company_instance))
		basic = company_instance.basic_info
		invest = company_instance.investment
		shareholders = company_instance.shareholders

		self.company_basic_info.set_info(basic)
		try:
			self.investment.insert_data(invest)
		except:
			logging.warning("investment issue {}".format(invest))
		try:
			self.shareholders.insert_data(shareholders)
		except:
			logging.warning("shareholder issue {}".format(shareholders))


if __name__ == '__main__':
	format1 = "%(asctime)s: %(message)s"
	logging.basicConfig(format=format1, level=logging.WARN, datefmt="%H:%M:%S")
	app = MainScreen()
