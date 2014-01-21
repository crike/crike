crike
=====

English online teaching and testing system.

Todo
-----
* refine urls to RESTful -- WIP
* 支持方向键翻页
* page 导航颜色，风格改进（箭头），放在显眼的位置（单词下方）
* pad上支持滑动翻页
* h1灰色背景改为活泼的图片或颜色，网页背景改变
* 自测环节改为渐进式的，不需要按钮，不能跳跃阶段
* 加入中间休息环节，播放轻松音乐和休息提示
* 时间控制：单词展示和考试
* 单词学习和自测环节加入换页前的短暂反馈，笑脸，对号
* 单词错误3次以上进入常错词
* 每次登陆提示先学习常错的单词，每个常错词只重新学习两次，但不从错词单中删除
* 加入积分系统，主要针对考试，教师可以消除积分，积分换奖品提示等
* 考试和学习结束时根据成绩播放掌声或成功画面
* exam
* statistics
* redis
* rewrite a registration module for django-registration doens't support custom user.
* naming, ICON in browser tab.
* word answered recording for users and lessons.
* user history, how many lessons have been done and show the next step users should do.
* use canvas / jquery flot to draw statistic pictures
* use bookblock to flip the words
* release

需求
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
