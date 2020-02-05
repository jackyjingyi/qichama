#!/usr/bin/python
# -*- coding: utf-8 -*-

def isFind(shareholder, index):
    # print(arg0,filename)
    with open('.\output\shareholder' + str(index) + '.txt',encoding="utf-8") as fobj:
        for line in fobj:
            if (shareholder[0] in line):
                print("在第" + str(index) + "层找到了：", line)
                return True
    return False


def judge(shareholder):
    if isFind(shareholder, 7):
        find(shareholder, 7)
    elif isFind(shareholder, 6):
        find(shareholder, 6)
    elif isFind(shareholder, 5):
        find(shareholder, 5)
    elif isFind(shareholder, 4):
        find(shareholder, 4)
    elif isFind(shareholder, 3):
        find(shareholder, 3)
    elif isFind(shareholder, 2):
        find(shareholder, 2)
    elif isFind(shareholder, 1):
        find(shareholder, 1)
    else:
        print("未找到对应的")


'''
def reverse(shareholder,index):
	s5 = find(list(set(shareholder)),index)
	print("第5层 ",list(set(s5)))
	s4 = find(list(set(s5)),4)
	print("第4层 ",list(set(s4)))
	s3 = find(list(set(s4)),3)
	print("第3层 ",list(set(s3)))
	s2 = find(list(set(s3)),2)
	print("第2层 ",list(set(s2)))
	s1 = find(list(set(s2)),1)
'''


def find(shareholder, index):
    global company
    company = []
    gudong = []
    result = []
    # 获取input的股东的公司名
    if index > 0:
        with open('.\output\shareholder' + str(index) + '.txt', encoding="utf-8") as fobj:
            for line in fobj:
                for x in shareholder:
                    if (x in line):
                        company.append(line.split(",")[1])
        print("company: ", list(set(company)))
        # print("company123: ",company5)

        if index > 1:
            # 通过公司名获取本公司的所有股东
            with open('.\output\shareholder' + str(index) + '.txt', encoding="utf-8") as fobj1:
                for line in fobj1:
                    for x in company:
                        if (x in line):
                            gudong.append(line.split(",")[2])
            # 本层与上一层的股东名字进行比较
            with open('.\output\shareholder' + str(index - 1) + '.txt', "r",encoding="utf-8") as fobj2:
                for line in fobj2:
                    for x in gudong:
                        if x == line.split(",")[2]:
                            result.append(x)
        if index > 1:
            print("第" + str(index) + "层 ", list(set(result)))
        index -= 1
        find(list(set(result)), index)


if __name__ == '__main__':
    shareholder = input("input shareholder name：")
    L = [shareholder]
    judge(L)
