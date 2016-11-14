#-*- coding: UTF-8 -*-
'''
Modify Log:
Nolan 05/21/2015 INIT
'''

import os
import datetime
import re
import sys
import jieba
import MySQLdb
import time
import operator

exclude_list = ['#','%','&','(',')',',','-','.','/','﹝','﹞','！','（','）', '\r', '\r\n'
			,'，','－','：','；','？', ' ', '	', '\n', '\t', '  ', '   ', '    ', '\'']

def connect_mysql_db():
	try:
		con 	= MySQLdb.connect(host = 'localhost', user = 'nolanjian', passwd = 'excellent', db = 'search', port=3306, charset='utf8')
		cur 	= con.cursor()
	except MySQLdb.Error,e:
		print "Mysql Error %d: %s" % (e.args[0], e.args[1])
		exit()
	return con, cur
	
def disconnect_mysql_db(con, cur):
	try:
		cur.close()
		con.close()
	except MySQLdb.Error,e:
		print "Mysql Error %d: %s" % (e.args[0], e.args[1])
		return False
	return True

def execute_sql(cur, sql_line):
	err_code 	= 0
	result 		= 0
	try:
		result = cur.execute(sql_line)
	except MySQLdb.Error,e:
		print "Mysql Error %d: %s" % (e.args[0], e.args[1])
		print sql_line
		#time.sleep(10)
		err_code = -1
	if err_code == -1:
		return -1
	return result

def get_words_list_from_string(input_str):
	seg_list 	= jieba.cut_for_search(input_str)
	word_list 	= set()
	for item in seg_list:
		str_tmp = '%s' % item
		if str_tmp not in exclude_list:
			word_list.add(str_tmp)
	#print 'word_list: '
	#for item in word_list:
	#	print item
	return word_list

def input_search_string():
	return raw_input('Your search input:')

def get_url_and_url_id(cur, url_url_id):
	function_start_time = time.time()

	sql_line 	= 'select * from url_list'
	rows 		= execute_sql(cur, sql_line)
	if rows > 0:
		results = cur.fetchall()
		for item in results:
			url_url_id[item[0]] = (item[1], item[2])

	function_end_time = time.time()
	return function_end_time - function_start_time

def get_words_id(word_list, word_word_id):
	function_start_time = time.time()

	word_id_list = []
	for word in word_list:
		if word in word_word_id:
			word_id_list.append(word_word_id[word])

	#for item in word_id_list:
	#	print item
	function_end_time = time.time()
	return word_id_list, function_end_time - function_start_time

def get_word_and_word_id(cur, word_word_id):
	function_start_time = time.time()

	sql_line 	= 'select * from word_list'
	rows 		= execute_sql(cur, sql_line)
	if rows > 0:
		results = cur.fetchall()
		for item in results:
			word_word_id[item[1]] = item[0]

	function_end_time = time.time()
	return function_end_time - function_start_time

def get_word_id_url_id_word_location(word_id_list):
	function_start_time = time.time()
	print 'word_id_list: '
	print word_id_list
	word_location = {}
	#word_id_list = set(word_id_list)
	for word_id in word_id_list:
		#print word_id
		#time.sleep(5)
		sql_line 	= 'select * from word_location%d where word_id = %d' % (word_id % 512, word_id)
		rows 		= execute_sql(cur, sql_line)
		print '************************** %d rows select.' % rows
		if rows > 0:
			results = cur.fetchall()
			for item in results:
				if item[0] not in word_location:
					word_location[item[0]] = []
				tub = (item[1], item[2])
				#print item[0],item[1],item[2]
				#print tub
				word_location[item[0]].append(tub)
	
	#for item in word_location:
	#	print item, word_location[item]
	'''
	result format:
	url0: word0, loca0; word1, loca1 ..........
	url1: word0, loca0; word1, loca1 ..........
	...............
	...............
	'''
	function_end_time = time.time()
	return word_location, function_end_time - function_start_time

def get_search_result(word_location):
	function_start_time = time.time()
	
	result_analyse = {}
	for url_id in word_location:
		result_analyse[url_id] = len(word_location[url_id])
		#print 'url_id: %d ---> len: %d' % (url_id, result_analyse[url_id])
	
	#time.sleep(10)
	result_analyse = sorted(result_analyse.iteritems(), key = operator.itemgetter(1), reverse=True)
	#for item in result_analyse:
	#	print item
	url_result = []
	for item in result_analyse:
		#print item[0], item[1]
		tmp_url_id = int(item[0])
		#print url_url_id[tmp_url_id]
		#print 'url_id: %d' % tmp_url_id
		url_result.append(url_url_id[item[0]])
	
	function_end_time = time.time()
	return url_result, function_end_time - function_start_time

def initialization_words_urls(cur, word_word_id, url_url_id):
	function_start_time = time.time()

	time_1 = get_word_and_word_id(cur, word_word_id)
	time_2 = get_url_and_url_id(cur, url_url_id)

	function_end_time = time.time()
	deta = function_end_time - function_start_time
	print 'initialization: %.2fs (%.2fs + %.2fs)' % (deta, time_1, time_2)

# ****************************************************************

con, cur = connect_mysql_db()
word_word_id = {}
url_url_id = {}
initialization_words_urls(cur, word_word_id, url_url_id)

while True:
	input_str 		= input_search_string()
	print input_str
	word_list 		= get_words_list_from_string(input_str)
	word_id_list, word_id_list_time = get_words_id(word_list, word_word_id)
	print 'word_id_list: %.2fs' % word_id_list_time
	word_location, word_location_time = get_word_id_url_id_word_location(word_id_list)
	print 'word_location_time: %.2fs' % word_location_time
	search_result, search_result_time = get_search_result(word_location)
	print 'search_result_time: %.2fs' % search_result_time
	for item in search_result:
		print item
	#send_result_to_client(search_result)
	
disconnect_mysql_db(con, cur)