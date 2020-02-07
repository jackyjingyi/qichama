from tkinter import ttk, Text
from tkinter import *
from collections import defaultdict
from queue import Queue
import logging

class Table(ttk.Treeview):

	def add_columns(self, cols):
		self['columns'] = cols
		for col in cols:  # 绑定函数，使表头可排序
			self.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(_col, False))

	def treeview_sort_column(self, col, reverse):  # Treeview、列名、排列方式
		l = [(self.set(k, col), k) for k in self.get_children('')]
		l.sort(reverse=reverse)  # 排序方式
		# rearrange items in sorted positions
		for index, (val, k) in enumerate(l):  # 根据排序后索引移动
			self.move(k, '', index)
		self.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))  # 重写标题，使之成为再点倒序的标题


class TreeList(ttk.Treeview):
	"""
	generate a tree from a root instance
	 root root_info
	  |__child1
	  |	|___grandchild1
	  |___child2
	DFS
	"""

	tags = ('shareholder', 'investment')

	def __init__(self, master):
		super().__init__(master, height=18, selectmode="browse")

	def show(self):
		self.config(columns=("level"))
		self.column('level', width=600)
		self.column('#0', width=350)
		self.heading('level', text="level")

	def generate_tree(self, root_node):
		nodes = Queue()
		nodes.put(root_node)
		while not nodes.empty():
			item = nodes.get()
			info = item.get_tree_node()

			if item.is_root():
				self.insert_item(info)
			else:
				parent = item.parent.key + info[4]

				self.insert_item(info=info, parent=parent)
			try:
				if item.has_child:
					for child in item.children:
						nodes.put(child)
			except:
				continue

	def insert_item(self, info, parent=None, end=True, idx=None):
		"""
		:param parent: str=>
				idx =>'0','1'
		:param info: tuple (id, level, name, url, status)
		:return:
		"""
		try:
			if not end:
				idx = idx
				assert not idx
			else:
				idx = 'end'
			if parent:
				try:
					self.insert(parent, idx, info[0], text="第" + str(info[1]) + "层 " + str(info[2]), values=(info[5], ""))
					if len(info[0]) < 60:
						self.insert(info[0], 'end', info[0] + 'shareholder', text="股东")
						self.insert(info[0], 'end', info[0] + 'investment', text="投资")
				except:
					self.insert(parent, idx, text="第" + str(info[1]) + "层 " + str(info[2]), values=(info[5], ""))

			else:
				self.insert('', '0', info[0], text="第" + str(info[1]) + "层 " + info[2], values=(info[5], ""))
				self.insert(info[0], 'end', info[0] + 'shareholder', text="股东")
				self.insert(info[0], 'end', info[0] + 'investment', text="投资")

			if info[4]:
				self.item(info[0], tags=(info[4]))
		except Exception as e:
			logging.warning(e)


class Shareholders(Table):
	cols = ("股东", "认缴", "持股比例", "实缴")

	def __init__(self, master):
		super().__init__(master, height=18, show="headings")
		self.add_columns(cols=self.__class__.cols)
		self.grid(column=0, row=0, sticky="news")

	def insert_data(self, data):
		self.delete(*self.get_children())
		for i in range(len(data)):
			k = list(data[i].keys())[0]

			v = data[i][k]
			_temp = tuple([k.name] + [vs for vs in v.values()])
			self.insert('', i, values=_temp)


class Investment(Table):
	cols = ("被投资企业名称", "被投资法定代表人", "注册资本", "出资比例", "注册时间", "状态")

	def __init__(self, master):
		super().__init__(master, height=18, show="headings")
		self.add_columns(cols=self.__class__.cols)
		self.grid(column=0, row=0, sticky="news")

	def insert_data(self, data):
		self.delete(*self.get_children())
		logging.info("inserting data {} of investment ".format(data))
		for i in range(len(data)):
			k = list(data[i].keys())[0]

			v = data[i][k]
			_temp = []
			for item in self.__class__.cols:
				_temp.append(v[item])

			self.insert('', i, values=tuple(_temp))


class BasicInfo(ttk.Frame):
	title = '工商基本信息'
	span_title = ('法定代表人', '纳税人识别号', '名称', '机构代码', '注册号', '注册资本', '统一社会信用代码', '登记机关', '经营状态',
				  '成立日期', '企业类型', '经营期限', '所属地区', '核准日期')
	long_span_title = ('企业地址')
	text_span_title = ('经营范围')

	def __init__(self, master):
		super().__init__(master, relief="raised")
		self.spans = defaultdict()
		# self.grid_columnconfigure(0,weight=1)
		# self.grid_rowconfigure(0,weight=1)
		self.columnconfigure(0, weight=1)
		# self.rowconfigure(0,weight=1)
		self.set_spans()

	def set_spans(self):
		span_titles = self.__class__.span_title
		self.span_frame = ttk.Frame(self)
		self.span_frame.grid(column=0, row=0, columnspan=4, sticky="news")
		max_row = 0
		for idx, name in enumerate(span_titles):
			_string = StringVar(self)
			_lable = ttk.Label(self.span_frame, text=name + ":")
			_entry = ttk.Entry(self.span_frame, textvariable=_string)
			_geo = divmod(idx, 3)
			max_row = max(max_row, _geo[0])

			# _geo[0] row, _geo[1] col
			_lable.grid(row=_geo[0], column=_geo[1] * 2, padx=0.5, pady=0.5, sticky="w")
			_entry.grid(row=_geo[0], column=_geo[1] * 2 + 1, padx=0.5, pady=0.5, sticky="ew")
			self.spans[name] = _string
		for i in range(6, 1, 2):
			self.span_frame.columnconfigure(i, weight=1)
			self.span_frame.grid_columnconfigure(i, weight=1)

		long_span_name = self.__class__.long_span_title
		long_span_string = StringVar(self.span_frame)
		lable = ttk.Label(self.span_frame, text=long_span_name + ":")
		entry = ttk.Entry(self.span_frame, textvariable=long_span_string)
		lable.grid(row=7, column=0, padx=0.5, pady=0.5, sticky="w")
		entry.grid(row=7, column=1, padx=0.5, columnspan=5, pady=0.5, sticky="ew")

		text_span_name = self.__class__.text_span_title
		# string1 = StringVar(self)
		lable1 = ttk.Label(self.span_frame, text=text_span_name + ":")
		entry1 = Text(self.span_frame)
		lable1.grid(row=8, column=0, padx=0.5, pady=0.5, sticky="nw")
		entry1.grid(row=8, column=1, columnspan=5, padx=0.5, pady=0.5, sticky="news")
		self.spans[long_span_name] = long_span_string
		self.spans[text_span_name] = entry1

	def set_info(self, d):

		for k, v in d.items():
			try:
				_k = self.spans[k]
				if isinstance(_k, StringVar):
					_k.set(v)
				elif isinstance(_k, Text):
					_k.delete(1.0, END)
					_k.insert("insert", v)
			except KeyError as e:
				logging.warning(e)



if __name__ == '__main__':
	root = Tk()
	share = Investment(root)
	test_info = [{
		"3 四川新荷花川贝母生态药材有限公司 https://www.qichamao.com/orgcompany/searchitemdtl/ab5cc412b926f685c45f3c5713124a84.html 27dd1969-f27a-4fa8-8fc0-f9a34f447799":
			{'被投资企业名称': '四川新荷花川贝母生态药材有限公司',
			 'url': 'https://www.qichamao.comhttps://www.qichamao.com/orgcompany/searchitemdtl/ab5cc412b926f685c45f3c5713124a84.html',
			 '被投资法定代表人': '吕强', '注册资本': '1,500.0000(万人民币)', '出资比例': '--', '注册时间': '2008-10-16',
			 '状态': '存续'}},
		{
			"3 四川古蔺肝苏药业有限公司 https://www.qichamao.com/orgcompany/searchitemdtl/458da261cc80bfbbed54af9edfe38b72.html 7f0bbd81-d219-4363-915e-4f9485118b55":
				{'被投资企业名称': '四川古蔺肝苏药业有限公司',
				 'url': 'https://www.qichamao.comhttps://www.qichamao.com/orgcompany/searchitemdtl/458da261cc80bfbbed54af9edfe38b72.html',
				 '被投资法定代表人': '吴学丹', '注册资本': '2,180.0000(万人民币)', '出资比例': '100%', '注册时间': '1999-04-29',
				 '状态': '存续'}},
		{
			"1 四川新荷花中药饮片股份有限公司 https://www.qichamao.com/orgcompany/searchitemdtl/5c39c6a3a47ab0b3e6e0416acb7944fe.html cda445e3-3572-4f79-a9a7-6c115d3019f7":
				{'被投资企业名称': '四川新荷花中药饮片股份有限公司',
				 'url': 'https://www.qichamao.comhttps://www.qichamao.com/orgcompany/searchitemdtl/5c39c6a3a47ab0b3e6e0416acb7944fe.html',
				 '被投资法定代表人': '江云', '注册资本': '6,038(万人民币)', '出资比例': '54.44%', '注册时间': '2001-12-30', '状态': '存续'}},
		{
			"2 四川省新荷花中药炮制工程研究有限公司 https://www.qichamao.com/orgcompany/searchitemdtl/839a2086d44cee8a9f9e34df58704a14.html abbd6b57-d72c-4824-8ba7-91d86692178d":
				{'被投资企业名称': '四川省新荷花中药炮制工程研究有限公司',
				 'url': 'https://www.qichamao.comhttps://www.qichamao.com/orgcompany/searchitemdtl/839a2086d44cee8a9f9e34df58704a14.html',
				 '被投资法定代表人': '江云', '注册资本': '1,000.0000(万人民币)', '出资比例': '15%', '注册时间': '2009-08-03',
				 '状态': '存续'}}]
	share.insert_data(test_info)
	root.mainloop()
