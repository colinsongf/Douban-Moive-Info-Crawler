#-*- coding: UTF-8 -*-
'''
Modify Log
Nolan 05/07/2015 ADD_USER_AGENT
Nolan 05/07/2015 CODE_AND_LOGIC_MODIFY
Nolan 05/07/2015 MODIFY_SLEEP_TIME
Nolan 05/07/2015 SET_USER_AGENT
Nolan 05/07/2015 ADD_PROXY
Nolan 05/07/2015 MODIFY_WAITING_TIME_WITH_USING_PROXY
Nolan 05/07/2015 BEAUTIFY_PROGRAM_STRUCTURE
Nolan 05/07/2015 CLEAN_COMMENT_AND_CODE_MARK
Nolan 05/07/2015 ADD_GLOBAL_VARIBLES
Nolan 05/08/2015 SAVE_HTML_FILE_AND_SET_WAITTING_TIME
Nolan 05/08/2015 CLEAN_CODE_MARK
Nolan 05/08/2015 CHANGE_PAGE_SIZE
Nolan 05/08/2015 SAVE_HTML_FILE
	---------------------------->> achieve a breakthrough that in downloading html file, not 403 occurs
Nolan 05/08/2015 REDUCE_IO_CALLED_TIMES
Nolan 05/08/2015 ADD_INFORMATION
Nolan 05/08/2015 CLEAN_CODE_MARK
Nolan 05/09/2015 CHECK_EMPTY_PAGE
Nolan 05/09/2015 SAVE_MOVIE_PAGE
Nolan 05/10/2015 START_FROM_END
Nolan 05/10/2015 CHANGE_PAGE_SIZE
Nolan 05/10/2015 SUPPORT_TRY_SESSION_ON_URL_OPEN
Nolan 05/10/2015 DISABLE_CHECK_REPEAT_AND_ENLARGE_SCAN_PAGE_LIMIT
Nolan 05/10/2015 MORE_FRIENDLY_HITS
Nolan 05/10/2015 MORE_HUMMAN_AT_PAGE_SELECT
Nolan 05/11/2015 HANDLER_ERROR_STATUS_IS_EMPTY
Nolan 05/11/2015 CUT_UNNEED_FEATURE
	---------------------------->> in the coming few days, multi process and regular should be supported, and comment should be collected.
Nolan 05/13/2015 NEW_WAY_TO_GET_MOVIE_TAG_LIST
Nolan 05/14/2015 RESTRUCTURE
Nolan 05/15/2015 SUPPORT_TAGS_INDEX_RANGE
'''

import urllib2
import re
import time
import urllib
import os
import datetime

target_url 	= 'http://movie.douban.com/tag/?view=cloud'
tag_url 	= 'http://movie.douban.com/tag/'
agent_ip 	= '218.207.195.217'
agent_port 	= '80'

class Movie_list:
	def __init__(self):
		self.url1 			= tag_url
	def request_open(self, tag_index, page_index):
		self.url2 			= '?start=' + str(page_index * 20) + '&type=T'
		full_url 			= self.url1 + movie_tags[tag_index] + self.url2
		save_as_file_name 	= "%d_%d.html" % (tag_index + 0, page_index + 1)
		print save_as_file_name
		# if the html file has ever been visited, just read it in the hard disk.
		#if os.path.exists(save_as_file_name) == True:
		#	print "%s exists" % save_as_file_name
		#	file 		= open(save_as_file_name,  'r')
		#	self.page1 	= file.read()
		#	file.close()
		#else:
		#	# Nolan 05/10/2015 SUPPORT_TRY_SESSION_ON_URL_OPEN
		#	#self.page1 	= urllib2.urlopen(full_url).read()
		#	self.page1 	= open_url(full_url)
		#	# End SUPPORT_TRY_SESSION_ON_URL_OPEN
		#	# Nolan 05/09/2015 CHECK_EMPTY_PAGE
		#	result 		= re.findall('没有找到符合条件的电影',self.page1)
		#	#print 'Here is result'
		#	err_string 	= ''
		#	for item in result:
		#		err_string += item
		#	#print err_string
		#	#print 'End'
		#	if err_string == '':
		#		save_html(self.page1, save_as_file_name)
		#	else:
		#		self.page1 = ''
		#	# End CHECK_EMPTY_PAGE
		self.page1 	= open_url(full_url)
		result 		= re.findall('没有找到符合条件的电影',self.page1)
		err_string 	= ''
		for item in result:
			err_string += item
		if err_string == '':
			save_html(self.page1, save_as_file_name)
		else:
			self.page1 = ''
		return self.page1

class Next_page:
	def __init__(self):
		self.url1 	= tag_url
	def np(self, tag_index):
		full_url 	= self.url1 + movie_tags[tag_index]
		self.page1 	= open_url(full_url)
		self.url2 		= re.findall('amp.*\d{1,2}',self.page1)
		if self.url2:
			self.num2 	= self.url2[-1][14:]
			num_page = int(self.num2)
			if num_page <= 58:
				return num_page
			else:
				return 58
		else:
			return 1

class Movie_info:
	def __init__(self):
		pass

	def get_moives_name(self, tag_index, page_index):
		target_page 		= movie_list.request_open(tag_index, page_index)
		if target_page == '':
			return False
		self.movie_name2 	= []
		self.movie_name1 	= re.findall('title="\S{1,}?"', target_page)
		for x in range(len(self.movie_name1)-1):
			self.movie_name2.append(self.movie_name1[x][7:-1]) 

		self.movie_url2 = []
		self.n 			= 0
		self.movie_url1 = re.findall('http://movie.douban.com/subject/\d{1,10}', target_page)
		for i in range(len(self.movie_url1)/2):
			self.movie_url2.append(self.movie_url1[2*self.n])
			movie_url 	= self.movie_url1[2*self.n]
			movie_id 	= movie_url[32:]
			save_as_file_name = movie_id + '.html'
			if os.path.exists(save_as_file_name) == False:
				tmp_page = open_url(movie_url)
				save_html(tmp_page, save_as_file_name)
				time.sleep(1)
				print '++++ %s' % save_as_file_name
			else:
				print "%s exists" % save_as_file_name
			self.n+=1
		return True

def save_html(page, save_as_file_name):
	target_file = file(save_as_file_name,'w')
	target_file.write(page)
	target_file.close()

def open_url(url, try_times = 3):
	times = 1
	return_page = ''
	while times <= try_times:
		times = times + 1
		try:
			return_page = urllib2.urlopen(url).read()
		except urllib2.HTTPError, e:
			print e.code
			time.sleep(30)
		except urllib2.URLError, e:
			print e.reason
			# Nolan 05/10/2015 HANDLER_ERROR_STATUS_IS_EMPTY
			if e.reason == '':
				print '**************** %s. Error status is empty, we will have a 1.5 mins wait.' % get_current_time()
				time.sleep(60)
			time.sleep(30)
		else:
			return return_page
	
	if return_page == '':
		exit()

def get_current_time():
	now = datetime.datetime.now()
	otherStyleTime = now.strftime("%Y-%m-%d %H:%M:%S")
	return otherStyleTime

def set_user_agent(url, agent_ip, agent_port):
	agent_ip_port 	= agent_ip + ':' + agent_port
	protocol 		= 'http'
	proxy 			= {protocol:agent_ip_port}
	proxy_support 	= urllib2.ProxyHandler(proxy)
	opener 			= urllib2.build_opener(proxy_support)
	urllib2.install_opener(opener)
	i_headers 		= {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.48'}
	req 			= urllib2.Request(url,headers=i_headers)
	html 			= urllib2.urlopen(req)
	if url == html.geturl():
		doc = html.read()
		return doc
	return

start_page 	= set_user_agent(target_url, agent_ip, agent_port)
movie_tags  = []   #movie_tags为电影标签
if start_page == '':
	print "\n***************************************"
	print "Get Nothing."
	exit()

first_tag 	= start_page.find('1990s')
last_tag 	= start_page.find('宗教')
tmp_page 	= start_page[(first_tag - 4):(last_tag + 50)]

tags_list 	= re.findall('\>\S{1,}?\<', tmp_page)
movie_tags  = []

for tag in tags_list:
    tag = tag[1:-1]
    movie_tags.append(tag)
movie_tags_len = len(movie_tags)
print "Total %d tag(s)" % movie_tags_len

movie_list 	= Movie_list()
movie 		= []

next_page 	= Next_page()
movie_info 	= Movie_info() 


print movie_tags_len
# Nolan 05/15/2015 SUPPORT_TAGS_INDEX_RANGE
#tag_index = 200 #for testing
tag_index_range_left 	= 0
tag_index_range_right 	= movie_tags_len - 1
tag_index 				= tag_index_range_left
# End SUPPORT_TAGS_INDEX_RANGE
#while tag_index < movie_tags_len:
while tag_index <= tag_index_range_right:
	print "********************************* 正在抓取标签 %s 中的电影 %d/%d" %(movie_tags[tag_index], tag_index + 1, movie_tags_len)
	starttime1 = time.time()
	num_page = next_page.np(tag_index)
	for page_index in range(num_page):
		print "开始抓取 %s 第%d页 (%d/%d)，抓取进度：" % (movie_tags[tag_index], page_index + 1, page_index + 1, num_page)
		starttime2 	= time.time()
		result 		= movie_info.get_moives_name(tag_index, page_index)
		endtime2 	= time.time()
		print "抓取第%d页完毕 (%d/%d)，用时%.2fs" % (page_index + 1, page_index + 1, num_page, endtime2 - starttime2)
		time.sleep(1)
		if result == False:
			break
	endtime1 	= time.time()
	print "********************************* 抓取 %s 标签完毕，用时%.2fs\n" % (movie_tags[tag_index], endtime1 - starttime1)
	time.sleep(10)
	tag_index = tag_index + 1
	
#删除超过3000部的电影
if len(movie)>3000:
	for i in range(len(movie)-3000):
		del movie[-i]

#排序
def comment(s):
    return int(s[1])

def sort_movies_list(movie):
	starttime4 = time.time()
	print '开始排序……'
	movie.sort(key = comment, reverse=True)
	endtime4 = time.time()
	print '排序完毕，共耗时%.2f'%(endtime4-starttime4)

sort_movies_list(movie)

#写到html文件里面
def write_to_html_file(movie):
	f = file('Douban_movies.html','w')
	f.write('<!DOCTYPE html>\n<html>\n<head>\n')
	f.write('<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">\n')
	f.write('</head>\n\n<body>\n')
	f.write('<h1>豆瓣电影榜单</h1>'+' '+'<h3>按评价人数排名，共3000部</h3>')  #标题
	s = 1     #s是电影序号
	for i in movie:
		f.write('<p>'+str(s)+'. '+'<a href=\"'+i[3]+'\">'+i[0]+'</a>'+'，共'+i[1]+'人评价，'+'得分：'+i[2]+'分；'+'\n')
		s+=1
	f.write('</body>')
	f.close()
	print '完成！请查看html文件，获取豆瓣电影榜单。'

write_to_html_file(movie)