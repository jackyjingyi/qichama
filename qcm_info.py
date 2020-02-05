#!/usr/bin/python
# -*- coding: utf-8 -*- 
import time
import requests
import logging
from lxml import etree
from urllib import request
from fake_useragent import UserAgent
from uuid import uuid4
from queue import Queue
from collections import defaultdict
import openpyxl

from store_ref import TreeList

url_front = "https://www.qichamao.com"
pipe = Queue()
# url_sets = set()
natrual_person_key = "自然人股东"
legal_person_key = "企业法人"


class NaturalPerson:
	instances = set()

	@classmethod
	def flush(cls):
		cls.instances = set()

	@classmethod
	def is_new_person(cls, person_id):
		return not person_id in [i.person_id for i in cls.instances]

	@classmethod
	def get_person(cls, person_id):
		for p in cls.instances:
			if p.person_id == person_id:
				yield p

	def __init__(self, name, level, parent, person_id):
		self.name = name
		self.person_id = person_id
		self.__class__.instances.add(self)
		self.investment = defaultdict(dict)
		self.parent = parent
		self.level = level

	def is_root(self):
		return

	def add_investment_company(self, key, val):
		self.investment[key] = val

	def __repr__(self):
		return "{} {}".format(self.name, self.person_id)

	@classmethod
	def __iter__(cls):
		for i in cls.instances:
			yield i.person_id, i.name, len(i.investment.keys())

	@classmethod
	def write_to_ws(cls, ws):
		row_generator = cls.__iter__()
		cols = ["姓名ID", "姓名", "投资公司总数"]
		for row in ws.iter_rows(min_row=1, max_col=3, max_row=len(cls.instances) + 1):

			if row[0].row == 1:
				for i in range(len(row)):
					row[i].value = cols[i]
			else:
				k = next(row_generator)
				for i in range(len(row)):
					row[i].value = str(k[i])

	def get_tree_node(self):
		_values = ""
		for k, v in self.investment[self.parent].items():
			_values += k + ": " + v + "\t"
		return self.person_id, self.level, self.name, '', 'shareholder', _values


class Company:
	instances = set()
	url = set()

	@classmethod
	def flush(cls):
		cls.instances = set()
		cls.url = set()

	@classmethod
	def is_new_company(cls, url):
		return url not in cls.url

	@classmethod
	def get_company(cls, uid=None, url=None):
		try:
			if uid:
				for instance in cls.instances:
					if instance.key == uid:
						return instance
			elif url:
				for instance in cls.instances:
					if instance.url == url:
						return instance
			else:
				logging.warning("At least one key element need to provid")
		except StopIteration:
			logging.warning("No matched item")

	def __init__(self, level, url, name=None, parent=None, basic_info=None):
		key = uuid4()
		self.url = url
		self.name = name
		self.level = level
		self.key = str(key)
		if basic_info:
			if isinstance(basic_info, (defaultdict, dict)):
				self.basic_info = basic_info
		else:
			self.basic_info = defaultdict(str)
		self.parent = parent
		self.status = None
		self.children = set()
		self._shareholders = []
		self._investment = []
		self.child_number = 0
		self.html = None
		# add current obj into class instances
		self.__class__.instances.add(self)
		self.__class__.url.add(self.url)

	# url_sets.add(self.url)

	def get_tree_node(self):
		"""
		get a dict for ttk.treeview
		:return: (id, level, name, url, status)
		"""
		return self.key, self.level, self.name, self.url, self.status, self.status

	@property
	def shareholders(self):
		return self._shareholders

	@shareholders.setter
	def shareholders(self, shareholder):
		self._shareholders.append(shareholder)

	@property
	def investment(self):
		return self._investment

	@investment.setter
	def investment(self, invest):
		self._investment.append(invest)

	def __repr__(self):
		return "{} {} {} {}".format(self.level, self.name, self.url, self.key)

	def generate_html(self):
		headers2 = {
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
			'Accept-Encoding': 'gzip, deflate, br, utf-8',
			'Accept-Language': 'zh-CN,zh;q=0.9',
			'Cache-Control': 'max-age=0',
			'Connection': 'keep-alive',
			'Cookie': get_cookies(),
			'Host': 'www.qichamao.com',
			'Upgrade-Insecure-Requests': '1',
			'User-Agent': UserAgent().random
		}
		if not self.html:
			r1 = requests.get(self.url, headers=headers2)

			assert r1.url == self.url

			self.html = etree.HTML(r1.text)
		return self.html

	def add_basic_info(self, key, value):
		self.basic_info[key] = value

	def is_root(self):
		# true if parent is None
		return not self.parent

	def has_child(self):
		return len(self.children) > 0

	def add_child(self, child):
		self.children.add(child)
		self.child_number += 1

	def get_children_number(self):
		return len(self.children)

	def get_basic_info(self, html=None):
		if not html:
			html = self.html
		if self.level > 6:
			return
		basic_info = html.xpath('//div[@class="qd-table-body li-half f14"]')[0].findall('.//li')
		agent = basic_info[0].find('./div/a')
		self.add_basic_info(key='法定代表人', value=agent.text)
		k = basic_info[2].xpath('./div/text()')
		m = basic_info[2].find('./div/a')
		company_title = k[0].strip() + str(m.text) + k[1].strip()
		if not self.name:
			self.name = company_title
		self.add_basic_info(key='名称', value=company_title)
		for i in [1, 3, 4]:
			k, v = basic_info[i].find('./span').text.strip()[:-1], basic_info[i].find('./div').text
			self.add_basic_info(key=k, value=v)
		for i in basic_info[5:]:
			k, v = i.find('./span').text.strip()[:-1], i.find('./div').text
			self.add_basic_info(key=k, value=v)

		return self.basic_info

	def get_shareholders(self, queue, html=None):
		if not html:
			html = self.html
		if self.level > 6:
			return
		data_shareholders = html.xpath('//div[@id="M_gdxx"]/div[2]')[0]
		# get all <ul> tags
		data_shareholders_uls = data_shareholders.xpath('.//div[@class="data-list"]')[0].findall('ul')
		_shareholders = {}
		for ele in data_shareholders_uls:
			boss = ele[1].xpath('./span[@class="info"]')
			boss_title, boss_name, boss_url = boss[0].find('em').text, boss[0].find('a').text, url_front + boss[0].find(
				'a').get('href')
			_inv_temp = {}
			for i in ele[2:]:
				_inv_temp[i.xpath('./span[1]/text()')[0].strip()[:-1]] = i.xpath('./span[2]/text()')[0].strip()
			if boss_title == natrual_person_key:
				person_id = boss_url.split('/')[-1]
				if NaturalPerson.is_new_person(person_id):
					new_nartrual_person = NaturalPerson(parent=self, level=self.level + 1, name=boss_name,
														person_id=person_id)
				else:
					new_nartrual_person = next(NaturalPerson.get_person(person_id))
				new_nartrual_person.add_investment_company(key=self, val=_inv_temp)
				self.shareholders = {new_nartrual_person: _inv_temp}
				self.add_child(new_nartrual_person)

			elif boss_title == legal_person_key:
				if boss_url not in self.__class__.url:
					# not in queue
					if Company.is_new_company(boss_url):
						# a brand new company
						_new_company = Company(level=self.level + 1, url=boss_url, name=boss_name)
						_new_company.status = "shareholder"
						# put into pipe
						queue.put(_new_company)
					else:
						logging.warning("company url not in queue but created before")
						return
				else:
					# url in queue, which means a company has been inited
					continue
				_new_company.parent = self
				self.add_child(_new_company)
				self.shareholders = {_new_company: _inv_temp}
			else:
				# other investors ignore them
				continue

	def get_investments(self, queue, html=None):
		if not html:
			html = self.html
		if self.level > 6:
			return
		# investment
		data_list = html.xpath('//div[@id="M_dwtz"]')[0]
		all_investments = data_list.findall('.//ul')

		for s in all_investments[1:]:
			lis = s.findall('.//li')
			temp = {}

			# shareholder_name = lis[1].findtext('.//a')
			investment_url = lis[1].findall('span/a')[0]
			investment_name, investment_url = investment_url.text, url_front + investment_url.get('href')
			temp['被投资企业名称'] = investment_name
			temp['url'] = url_front + investment_url
			temp[lis[2].xpath('./span[1]/text()')[0].strip()[:-1]] = lis[2].find('.//a').text
			for l in lis[3:]:
				temp[l.xpath('./span[1]/text()')[0].strip()[:-1]] = l.xpath('./span[2]/text()')[0]
			if investment_url not in self.__class__.url:
				# not in queue
				if Company.is_new_company(url=investment_url):
					_new_company = Company(level=self.level + 1, url=investment_url, name=investment_name)
					_new_company.status = "investment"
					queue.put(_new_company)
				else:
					logging.warning("company url not in queue but created before")
					return
			else:
				continue
			_new_company.parent = self
			self.add_child(_new_company)
			self.investment = {_new_company: temp}

		return self.investment


def get_cookies():
	cookies = (open(".\input\cookies.txt", 'r').read()).strip()
	if len(cookies) < 50:
		# self.logger.info('请先在cookies.txt中填写cookies信息')
		return
	else:
		cookies = cookies[0:-10] + str(int(time.time() * 1000))
		return cookies


def worker(queue, level):

	while not queue.empty():
		try:
			current_company = queue.get()
			logging.info("currently checking {}, queue size {}".format(current_company, queue.qsize()))

			if isinstance(current_company, Company):
				assert isinstance(current_company, Company)
				if current_company.level <= level:
					current_company.generate_html()
					current_company.get_basic_info()
					current_company.get_shareholders(queue)
					current_company.get_investments(queue)

				else:
					continue
			elif isinstance(current_company, str):
				time.sleep(1)
				logging.info("waiting 1 secs")
		except:
			continue


if __name__ == "__main__":
	try:

		url_base = (open(r".\input\input.txt", 'r', encoding="utf-8").read()).strip()
		headers1 = {
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept-Language': 'zh-CN,zh;q=0.9',
			'Cache-Control': 'max-age=0',
			'Connection': 'keep-alive',
			'Cookie': get_cookies(),
			'Host': 'www.qichamao.com',
			'Upgrade-Insecure-Requests': '1',
			'User-Agent': UserAgent().random
		}
		root_company = Company(level=1, url=url_base, name=None)
		pipe.put(root_company)
		worker(pipe)
		wb = openpyxl.Workbook()
		ws = wb.active
		NaturalPerson.write_to_ws(ws)
		wb.save("test.xlsx")
		assert root_company.is_root()
		from tkinter import ttk
		from tkinter import *

		root = Tk()
		tree = TreeList(root)
		tree.generate_tree(root_node=root_company)
		tree.show()
		tree.grid(column=0, row=0)
		tree.grid_columnconfigure(1, weight=1)
		tree.columnconfigure(1, weight=1)
		root.grid_rowconfigure(0, weight=1)
		root.grid_columnconfigure(0, weight=1)
		root.columnconfigure(0, weight=1)
		root.mainloop()

	except IOError as err:
		print('File error: ' + str(err))
