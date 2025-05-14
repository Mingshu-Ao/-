排序模块

项目结构

SortStrategy：排序策略基类
InsertionSortStrategy：插入排序实现
BubbleSortStrategy：冒泡排序实现
SelectionSortStrategy：选择排序实现
QuickSortStrategy：快速排序实现
Sorter：排序器类，封装排序逻辑
GrandViewGardenSpot：大观园景点数据类
chinese_to_pinyin_initials：中文转拼音首字母工具函数

功能特性

多种排序算法：
插入排序（适合部分有序数据）
冒泡排序（适合小数据集，带提前终止优化）
选择排序（适合简单场景）
快速排序（适合大数据量）

灵活排序规则：
支持按拼音首字母排序
支持按景点热度排序
支持按游览人次排序
支持自定义升降序

策略模式：
通过策略模式实现排序算法的灵活切换
易于扩展新的排序算法