from typing import List, Callable, Any
from pypinyin import lazy_pinyin # 需要安装pypinyin 这里用的是0.53.0

# 排序策略基类
class SortStrategy:
    """
    定义了排序策略的接口，子类需要实现sort方法。
    """

    def sort(self, data: List[Any], key: Callable[[Any], Any], reverse: bool) -> List[Any]:
        """
        排序方法，需要子类实现。

        :param data: 要排序的数据列表。
        :param key: 一个函数，用于从每个元素中提取一个用于比较的关键字。
        :param reverse: 如果为True，则排序结果将按降序排列；否则按升序排列。
        :return: 排序后的数据列表。
        """
        raise NotImplementedError("Subclasses must implement this method")


# 插入排序策略类
class InsertionSortStrategy(SortStrategy):
    """
    实现了插入排序算法的策略类，适合部分有序的数据。
    """

    def sort(self, data: List[Any], key: Callable[[Any], Any], reverse: bool) -> List[Any]:
        sorted_data = list(data)
        for i in range(1, len(sorted_data)):
            current = sorted_data[i]
            j = i - 1
            # 将当前元素插入到已排序部分的正确位置
            while j >= 0 and (
                    (key(sorted_data[j]) > key(current)) if not reverse else (key(sorted_data[j]) < key(current))
            ):
                sorted_data[j + 1] = sorted_data[j]
                j -= 1
            sorted_data[j + 1] = current
        return sorted_data


# 冒泡排序策略类
class BubbleSortStrategy(SortStrategy):
    """
    实现了冒泡排序算法的策略类，适合小数据集。
    """

    def sort(self, data: List[Any], key: Callable[[Any], Any], reverse: bool) -> List[Any]:
        sorted_data = list(data)
        n = len(sorted_data)
        for i in range(n):
            swapped = False
            for j in range(n - i - 1):
                # 比较相邻元素并根据reverse参数决定排序顺序
                condition = (key(sorted_data[j]) > key(sorted_data[j + 1])) if not reverse else (
                            key(sorted_data[j]) < key(sorted_data[j + 1]))
                if condition:
                    sorted_data[j], sorted_data[j + 1] = sorted_data[j + 1], sorted_data[j]
                    swapped = True
            # 如果没有发生交换，说明列表已经有序，可以提前退出循环
            if not swapped:
                break
        return sorted_data


# 选择排序策略类
class SelectionSortStrategy(SortStrategy):
    """
    实现了选择排序算法的策略类，适合简单场景。
    """

    def sort(self, data: List[Any], key: Callable[[Any], Any], reverse: bool) -> List[Any]:
        sorted_data = list(data)
        n = len(sorted_data)
        for i in range(n):
            extrema = i
            for j in range(i + 1, n):
                # 找到最小（或最大）元素的位置
                if (key(sorted_data[j]) < key(sorted_data[extrema])) if not reverse else (
                        key(sorted_data[j]) > key(sorted_data[extrema])):
                    extrema = j
            # 将找到的最小（或最大）元素与当前位置交换
            sorted_data[i], sorted_data[extrema] = sorted_data[extrema], sorted_data[i]
        return sorted_data


# 快速排序策略类
class QuickSortStrategy(SortStrategy):
    """快速排序策略（适合大数据量）"""

    def sort(self, data: List[Any], key: Callable[[Any], Any], reverse: bool) -> List[Any]:
        if len(data) <= 1:
            return list(data)

        pivot = data[len(data) // 2]
        pivot_key = key(pivot)
        left, middle, right = [], [], []

        for x in data:
            x_key = key(x)
            if x_key == pivot_key:
                middle.append(x)
            elif (x_key < pivot_key and not reverse) or (x_key > pivot_key and reverse):
                left.append(x)
            else:
                right.append(x)

        return self.sort(left, key, reverse) + middle + self.sort(right, key, reverse)


# 排序器类，支持策略模式
class Sorter:
    """
    排序器类，通过策略模式支持不同的排序算法。
    """

    def __init__(
            self,
            strategy: SortStrategy = InsertionSortStrategy(),  # 默认排序策略为插入排序
            key: Callable[[Any], Any] = lambda x: x,  # 默认键函数为身份函数
            reverse: bool = False  # 默认排序顺序为升序
    ):
        self.strategy = strategy  # 排序策略
        self.key = key  # 键函数
        self.reverse = reverse  # 排序顺序

    def sort(self, data: List[Any]) -> List[Any]:
        """
        使用当前策略对数据进行排序。

        :param data: 要排序的数据列表。
        :return: 排序后的数据列表。
        """
        return self.strategy.sort(data, self.key, self.reverse)


class GrandViewGardenSpot:
    """大观园景点类（包含中文名称、热度、游览人数）"""

    def __init__(self, name: str, popularity: int, visits: int):
        self.name = name  # 中文地名
        self.popularity = popularity  # 热度评分
        self.visits = visits  # 游览人次

    def __repr__(self):
        return f"{self.name}（热度{self.popularity}★ 游览{self.visits}次）"


def chinese_to_pinyin_initials(name: str) -> str:
    """将中文转换为拼音首字母组合（如'怡红院'->'YHY'）"""
    return ''.join([p[0].upper() for p in lazy_pinyin(name)])


if __name__ == "__main__":
    # 测试数据
    spots = [
        GrandViewGardenSpot("怡红院", 5, 1500),
        GrandViewGardenSpot("潇湘馆", 4, 3200),
        GrandViewGardenSpot("蘅芜苑", 3, 4500),
        GrandViewGardenSpot("稻香村", 4, 1800),
        GrandViewGardenSpot("栊翠庵", 5, 2750),
        GrandViewGardenSpot("凹晶溪馆", 3, 2100)
    ]

# 场景1：按拼音首字母排序（插入排序）
    print("-- 按拼音首字母排序 --")
    sorter = Sorter(
        strategy=InsertionSortStrategy(),
        key=lambda x: chinese_to_pinyin_initials(x.name),
        reverse=False
    )
    for item in sorter.sort(spots):
        pinyin = chinese_to_pinyin_initials(item.name)
        # print(f"{pinyin} - {item}")
        print(item)

# 场景2：按热度降序（冒泡排序，带提前终止优化）
    print("-- 按热度排行 --")
    sorter = Sorter(
        strategy=BubbleSortStrategy(),
        key=lambda x: x.popularity,
        reverse=True
    )
    for item in sorter.sort(spots):
        print(item)

# 场景3：按游览人次降序（选择排序找极值）
    print("-- 按游览量排行 --")
    sorter = Sorter(
        strategy=SelectionSortStrategy(),
        key=lambda x: x.visits,
        reverse=True
    )
    for item in sorter.sort(spots):
        print(item)

# 场景4：快速排序示例
    print("\n-- 快速排序按游览人次升序 --")
    sorter = Sorter(
        strategy=QuickSortStrategy(),
        key=lambda x: x.visits,
        reverse=False
    )
    for item in sorter.sort(spots):
        print(item)