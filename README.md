crike
=====

English online teaching and testing system.

Todo
-----
* refine urls to RESTful
* learning process: pick
* learning process: fill blanks
* learning process: dictation
* exam
* statistics
* add word management view with delete media files checkbox
* enable word info manual modification and single word info download
* images (youdao has pics or optimize result from search engine), enable single image download and upload
* redis
* Rewrite a registration module for django-registration doens't support custom user.
* naming
* release

Requirements
-----

1 教学

*  单词学习：展示单词，图片，发音，音标，释义  
*  英译汉：出单词，选释义  
*  汉译英：出释义，填写完整单词  
*  听写：听发音选词（听发音直接写出单词）  
*过程中，出现错误的单词计入生词本，并标记错误次数，直至正确后才能进入下一单词*

2 测试 
 
*  测试在完成每个单元学习流程后，进入测试  
*  提供链接，直接进入测试  
*  测试内容包含本单元单词的英译汉，汉翻英，听写，最后给出成绩统计

3 统计和管理
  
* 将为每个学生建立专属账户
	* 统计生词
	* 学习进度
	* 测试成绩
	* 可删除和添加生词
* 为教师建立专属账户
	* 可添加删除课本和课程，添加删除修改单词信息
	* 可查看该教师所属学生的所有统计数据
	* 对该教师所属所有学生建立图表，包括直方图，排名表等信息
