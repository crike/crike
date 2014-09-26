crike
=====

English online teaching and learning system.

![image](https://github.com/crike/crike/screenshots/crike.png)
![image](https://github.com/crike/crike/screenshots/crike_learn.png)
![image](https://github.com/crike/crike/screenshots/crike_admin.png)

Todo
-----
* 统计信息：对教师所教的所有学生建立图表，包括直方图，排名表等信息
* 直方图不再显示单词学习信息，改为得分统计，学习事件统计，横轴为日期
* 发布 1.0 版本
* 局域网DNS/DHCP，数据备份(distributed mongodb)
* 禁止通过修改browser地址栏直接进入某页面，禁止刷新清零错误次数
  * consider using "kiosk mode"
* 提供积分增加提示信息，积分增加或减少的历史记录

需求
-----

1 教学

*  单词学习：展示单词，图片，发音，音标，释义  
*  英译汉：出单词，选释义  
*  汉译英：出释义，填写完整单词  
*  听写：听发音选词（听发音直接写出单词）  
*过程中，出现错误的单词计入生词本，并标记错误次数，直至正确后才能进入下一单词*
*  阅读理解
*  屏幕取词，加入生词本

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
