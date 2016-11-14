#-*- coding: UTF-8 -*-
'''
Modify Log:
Nolan 05/18/2015 INIT
			--------->> now, we can build key words list, may be the some key word should be excluded, 
			--------->>		but that not the most significant thing.
Nolan 05/19/2015 SUPPORT_MULIT_FILE
Nolan 05/19/2015 SUPPORT_MYSQL
Nolan 05/20/2015 MAKE_RELATION_BETWEEN_URL_AND_WORDS
Nolan 05/20/2015 CLEAN_CODE_MARK
Nolan 05/20/2015 LOAD_WORD_AND_WORD_ID
Nolan 05/20/2015 SQL_TIME_ANALYSE
Nolan 05/20/2015 CLEAN_CODE_MARK
Nolan 05/21/2015 WORD_LOCATION_TABLE_ANALYSE
			--------->> now, have a search of WORD_LOCATION_TABLE takes about 54s in about 6080911 rows.
Nolan 05/21/2015 RESTRUCT
Nolan 05/21/2015 USE_INSERT_ID
			--------->> achieve a great breakthrough on get_words_list_unique_id_and_add_word_to_word_list function cost, last then 0.5s cost.
Nolan 05/21/2015 CLEAN_CODE_MARK
Nolan 05/22/2015 SUPPORT_MULIT_WORD_LOCATION_TABLES
'''


import os
import datetime
import re
import sys
import jieba
import MySQLdb
import time
from bs4 import *

exclude_list = ['#','%','&','(',')',',','-','.','/','﹝','﹞','！','（','）', '\r', '\r\n'
			,'，','－','：','；','？', ' ', '	', '\n', '\t', '  ', '   ', '    ', '\'']
html_file_local_path = 'E:\\\\DouBanMovies\\\\'
movie_url 	= 'http://movie.douban.com/subject/'
# Nolan 05/22/2015 SUPPORT_MULIT_WORD_LOCATION_TABLES
word_location_table_num = 512
# End SUPPORT_MULIT_WORD_LOCATION_TABLES

def get_page_from_hard_disk(file_name):
	file_object = open(file_name, 'r')
	soup 		= BeautifulSoup(file_object)
	file_object.close()
	return clear_js_script(soup)

def clear_js_script(soup):
	find_result = soup.find_all('script')
	if len(find_result) > 0:
		for js_script_item in find_result:
			js_script_item.clear()
	return soup

def get_date():
	now 		= datetime.datetime.now()
	new_format 	= now.strftime("%Y-%m-%d")
	time_str 	= '%s' % new_format
	return time_str

def get_text_only_without_empty_line(soup):
	page_text = get_text_only(soup)
	page_text = re.sub(r"\n[\s| ]*\n", '', page_text)
	return page_text

def get_text_only(soup):
	node_string = soup.string
	if node_string == None:
		contents 	= soup.contents
		result_text = ''
		for content in contents:
			sub_text 	= get_text_only(content)
			result_text += sub_text + '\n'
		return result_text
	else:
		return node_string.strip()

def get_words_list_from_page(page):
	seg_list 	= jieba.cut_for_search(page)
	word_list 	= []
	for item in seg_list:
		str_tmp = '%s' % item
		if str_tmp not in exclude_list:
			word_list.append(str_tmp)
	word_list_unique = list(set(word_list))
	word_list_unique.sort()
	return word_list, word_list_unique

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
	
def get_entry_id(cur, table, field, value, create_new = True):
	cur.execute("select %s from %s where %s = '%s'" % (field, table, field, value))
	res = cur.fetchone()
	if res == None:
		cur.execute("insert into %s(%s) value('%s')" % (table, field, value))
	cur.execute("select %s from %s where %s = '%s'" % (field, table, field, value))
	res = cur.fetchone()
	return res[0]

def get_words_list_unique_id_and_add_word_to_word_list(cur, word_list_unique, unique_word_word_id):
	function_start_time = time.time()

	for i in range(len(word_list_unique)):
		bool_re = word_list_unique[i] in unique_word_word_id
		if bool_re == True:
			continue
		cmd = "insert into %s(%s) value('%s')" % ('word_list', 'word', word_list_unique[i])
		result_count = execute_sql(cur, cmd)
		if result_count != -1:
			word_tmp 		= '%s' % word_list_unique[i]
			last_insert_id 	= cur.lastrowid
			unique_word_word_id[word_tmp] = last_insert_id

	cur.execute('commit')
	function_end_time = time.time()
	return function_end_time - function_start_time
	
def add_url_to_url_list_and_return_url_id(cur, internal_url, external_url):
	function_start_time = time.time()
	cmd 	= "select url_id from url_list where external_url = '%s'" % external_url
	result 	= execute_sql(cur, cmd)
	if result == 0:
		cmd = "insert into url_list(external_url, internal_url) value('%s', '%s')" % (external_url, internal_url)
		result = execute_sql(cur, cmd)
	cur.execute('commit')
	cmd 	= "select url_id from url_list where external_url = '%s'" % external_url
	result 	= execute_sql(cur, cmd)
	res 	= cur.fetchone()
	url_id 	= res[0]
	function_end_time = time.time()
	return url_id, function_end_time - function_start_time
	
def make_relation_between_page_word(cur, unique_word_word_id, word_list, url_id):
	function_start_time = time.time()
	pair_count = 0
	word_list_length = len(word_list)
	#time.sleep(10)
	for word_location in range(word_list_length):
		try:
			word = word_list[word_location]
			word_id 	= unique_word_word_id[word]
		except KeyError, k_e:
			continue
		table_id = word_id % word_location_table_num
		cmd 		= "insert into word_location%d(url_id, word_id, location) value(%d, %d, %d)" % (table_id, url_id, word_id, word_location)
		result 		= execute_sql(cur, cmd)
		if result != -1:
			pair_count += 1
	cur.execute('commit')
	function_end_time = time.time()
	return pair_count, function_end_time - function_start_time

def load_word_in_word_list_table(cur):
	build_word_list_start_time = time.time()
	tmp_dic = {}
	cmd 	= 'select * from word_list'
	rows 	= execute_sql(cur, cmd)
	if rows > 0:
		results = cur.fetchall()
		for item in results:
			tmp_dic[item[1]] = item[0]
	build_word_list_end_time = time.time()
	deta_time = build_word_list_end_time - build_word_list_start_time
	return tmp_dic, deta_time

def SQL_operation(unique_word_word_id, word_list, word_list_unique, file_id, cur):
	function_start_time = time.time()
	internal_url 		= '%s%s.html' % (html_file_local_path, file_id)
	external_url 		= "%s%d" % (movie_url, file_id)
	time_1 				= get_words_list_unique_id_and_add_word_to_word_list(cur, word_list_unique, unique_word_word_id)	# word_list table
	url_id, time_2 		= add_url_to_url_list_and_return_url_id(cur, internal_url, external_url)	# url_list table
	pair_count, time_3 	= make_relation_between_page_word(cur, unique_word_word_id, word_list, url_id)	# word_location_table
	
	print 'state informations:'
	print 'unique_word_word_id length:	%d' % len(unique_word_word_id)
	print 'word_list_unique length:	%d' % len(word_list_unique)
	print 'word_list length:		%d' % len(word_list)
	print 'pairs_count:			%d' % pair_count
	print '%.2fs + %.2fs + %.2fs' % (time_1, time_2, time_3)
	print 'file : %d.html, sql operation end.' % file_id
	#time.sleep(10)
	function_end_time = time.time()
	return function_end_time - function_start_time

def build_word_list_and_url_list_and_wordlocation(start_file_id, end_file_id):
	function_start_time = time.time()
	external_url 	= ''
	internal_url 	= ''
	con, cur 		= connect_mysql_db()
	file_id 		= start_file_id
	task_count 		= 0
	
	unique_word_word_id, deta_time = load_word_in_word_list_table(cur)
	print 'It takes %.2fs to bulid unique_word_word_id, length: %d' % (deta_time, len(unique_word_word_id))

	while file_id <= end_file_id:
		file_name 	= '%d.html' % file_id
		if os.path.exists(file_name) == True:
			start_time 	= time.time()
			print '------------------------------->> Now in File: %s' % file_name
			soup 		= get_page_from_hard_disk(file_name)
			page_text 	= get_text_only_without_empty_line(soup)
			page 		= '%s' % page_text.encode('utf-8')
			end_time_tmp1 = time.time()
			word_list, word_list_unique = get_words_list_from_page(page)
			end_time_tmp2 = time.time()
			sql_operation_time = SQL_operation(unique_word_word_id, word_list, word_list_unique, file_id, cur)
			task_count 	+= 1
			end_time 	= time.time()
			time_cost_1 	= end_time_tmp1 - start_time
			time_cost_2 	= end_time_tmp2 - end_time_tmp1
			time_cost_total = end_time 		- start_time
			print '------------------------------->> %.2fs cost. (%.2fs + %.2fs + %.2fs) \n' % (time_cost_total, time_cost_1, time_cost_2, sql_operation_time)
		file_id 	+= 1;
	# end while
	disconnect_mysql_db(con, cur)
	function_end_time = time.time()
	return task_count, function_end_time - function_start_time
# ************************************* *************** ************************

# last_id: 4221475
#start_file_id 	= 1291543 
start_file_id 	= 4221475
#end_file_id 	= 26387746
end_file_id 	= 26387746

# process start
result, function_time = build_word_list_and_url_list_and_wordlocation(start_file_id, end_file_id)
print '********************	%d task(s) finish, cost %.2fs' % (result, function_time)