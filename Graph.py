import heapq
import itertools


class EdgeNode:
    def __init__(self, vertex, weight, next=None, scenic=None):
        """
        :param vertex: 边所指向的顶点
        :param weight: 边的权重（旅行时间）
        :param next: 下一个节点（用于链表结构）
        :param scenic: 边上沿途的小景点信息，可选
        """
        self.vertex = vertex
        self.weight = weight
        self.next = next
        self.scenic = scenic  # 边上沿路小景点


class Graph:
    def __init__(self):
        """
        构造函数，初始化图的邻接表和每个顶点的参考游玩时长字典
        """
        self.adj_list = {}
        self.vertex_time = {}

    def create_graph(self):
        """
        创建图并添加顶点、边以及各顶点的参考游玩时长。
        :return: None
        """
        vertices = ['南门入口',
            '怡红院',
            '曲径通幽',
            '沁芳桥亭',
            '秋爽斋',
            '潇湘馆',
            '滴翠亭',
            '晓翠堂',
            '缀锦阁',
            '稻香村',
            '暖香坞',
            '汀花溆',
            '蘅芜院',
            '嘉荫堂/正殿/省亲别墅',
            '栊翠庵',
            '凸碧山庄',
            '葬花冢',
            '凹晶溪馆',
            '林中道观',
            '沁芳闸',
            '芦雪庵',
            '藕香榭']
        for v in vertices:
            self.add_vertex(v)
        # 设置每个景点的参考游玩时长（单位：分钟）
        self.vertex_time = {
            '南门入口': 1,
            '怡红院': 8,
            '曲径通幽': 4,
            '沁芳桥亭': 3,
            '秋爽斋': 6,
            '潇湘馆': 7,
            '滴翠亭':5,
            '晓翠堂':6,
            '缀锦阁':10,
            '稻香村': 10,
            '暖香坞': 9,
            '汀花溆': 4,
            '蘅芜院': 8,
            '嘉荫堂/正殿/省亲别墅': 25,
            '栊翠庵': 5,
            '凸碧山庄':9,
            '葬花冢':5,
            '凹晶溪馆':6,
            '林中道观':7,
            '沁芳闸':2,
            '芦雪庵':5,
            '藕香榭':3,
        }
        self.edge_info = {
            ('南门入口', '怡红院'):   {'weight': 10},
            ('南门入口', '曲径通幽'): {'weight': 5},
            ('南门入口', '潇湘馆'): {'weight': 10},
            ('曲径通幽', '沁芳桥亭'): {'weight': 3},
            ('曲径通幽', '怡红院'):   {'weight': 5},
            ('曲径通幽', '潇湘馆'):   {'weight': 7},
            ('沁芳桥亭', '潇湘馆'):   {'weight': 5},
            ('沁芳桥亭', '晓翠堂'):   {'weight': 4},
            ('沁芳桥亭', '怡红院'):   {'weight': 10},
            ('滴翠亭', '缀锦阁'):   {'weight': 1},
            ('滴翠亭', '秋爽斋'):   {'weight': 2},
            ('秋爽斋', '晓翠堂'):     {'weight': 1},
            ('秋爽斋', '芦雪庵'):     {'weight': 10},
            ('秋爽斋', '藕香榭'):     {'weight': 10},
            ('稻香村', '芦雪庵'):     {'weight': 3},
            ('稻香村', '藕香榭'):     {'weight': 10},
            ('稻香村', '汀花溆'):      {'weight': 10},
            ('稻香村', '暖香坞'):      {'weight': 5},
            ('藕香榭', '暖香坞'):      {'weight': 2},
            ('汀花淑', '暖香坞'):      {'weight': 10},
            ('芦雪庵', '藕香榭'):      {'weight': 15},
            ('汀花溆', '蘅芜院'):      {'weight': 5},
            ('凸碧山庄', '蘅芜院'):      {'weight': 5},
            ('凸碧山庄', '嘉荫堂/正殿/省亲别墅'):      {'weight': 3},
            ('凸碧山庄', '凹晶溪馆'):      {'weight': 13},
            ('凸碧山庄', '葬花冢'):      {'weight': 15},
            ('凹晶溪馆', '葬花冢'):      {'weight': 3},
            ('林中道观', '葬花冢'):      {'weight': 10},
            ('林中道观', '凹晶溪馆'):      {'weight': 15},
            ('嘉荫堂/正殿/省亲别墅', '沁芳桥亭'):      {'weight': 3},
            ('嘉荫堂/正殿/省亲别墅', '怡红院'):      {'weight': 12},
            ('嘉荫堂/正殿/省亲别墅', '沁芳闸'):      {'weight': 2},
            ('沁芳闸', '怡红院'):     {'weight': 13},
            ('沁芳闸', '栊翠庵'):     {'weight': 3},

            ('栊翠庵', '怡红院'):      {'weight': 8},
            ('栊翠庵', '林中道观'):      {'weight': 3},
        }

        # 通过迭代edge_info添加所有边
        for (src, dest), info in self.edge_info.items():
            scenic = info.get('scenic')  # 如果没有scenic信息将返回None
            self.add_edge(src, dest, info['weight'], scenic=scenic)


    def add_vertex(self, vertex):
        """
        添加顶点。
        """
        if vertex not in self.adj_list:
            self.adj_list[vertex] = None

    def add_edge(self, src, dest, weight, bidirectional=True, scenic=None):
        """
        添加有权边，支持双向（无向图）添加边。
        """
        if src not in self.adj_list:
            self.add_vertex(src)
        if dest not in self.adj_list:
            self.add_vertex(dest)
        node = EdgeNode(dest, weight, self.adj_list[src], scenic)
        self.adj_list[src] = node
        if bidirectional:
            node = EdgeNode(src, weight, self.adj_list[dest], scenic)
            self.adj_list[dest] = node

    def display(self):
        """
        打印图的邻接表表示，包括每条边的权重和沿途小景点信息。
        """
        for vertex in self.adj_list:
            print(f"{vertex}: ", end="")
            current = self.adj_list[vertex]
            while current:
                scenic_info = f", scenic: {current.scenic}" if current.scenic else ""
                print(f"{current.vertex}({current.weight}{scenic_info}) -> ", end="")
                current = current.next
            print("End")

    def get_shortest_route(self, start, target):
        """
        使用 Dijkstra 算法求最短路径。
        """
        distance = {vertex: float('inf') for vertex in self.adj_list}
        parent = {vertex: None for vertex in self.adj_list}
        distance[start] = 0
        heap = [(0, start)]
        while heap:
            current_dist, u = heapq.heappop(heap)
            if current_dist > distance[u]:
                continue
            if u == target:
                break
            current = self.adj_list[u]
            while current:
                v = current.vertex
                weight = current.weight
                if distance[u] + weight < distance[v]:
                    distance[v] = distance[u] + weight
                    parent[v] = u
                    heapq.heappush(heap, (distance[v], v))
                current = current.next
        if distance[target] == float('inf'):
            return None, None
        path = []
        v = target
        while v is not None:
            path.append(v)
            v = parent[v]
        path.reverse()
        return path, distance[target]

    # 修改后的规划必经景点的路径方法
    def get_visit_path(self, required, start=None, end=None):
        """
        在全图中寻找一条从 start 到 end 的路径，该路径必须经过所有必经景点（required）。
        这里采用枚举必经景点中除起点和终点外的排列组合，再利用已有的最短路径方法连接各个必经景点。

        :param required: 用户选择的必经景点列表
        :param start: 起点（必须在 required 中）
        :param end: 终点（必须在 required 中）
        :return: (路径列表, [旅行时间, 游玩时长, 总时间])，若无解则返回 (None, None)
        """
        if not required or start not in required or end not in required:
            return None, None

        # 取得除起点和终点之外的必经景点
        intermediate = [v for v in required if v != start and v != end]

        best_path = None
        best_travel_time = float('inf')

        # 枚举所有中间必经景点的排列
        for perm in itertools.permutations(intermediate):
            sequence = [start] + list(perm) + [end]
            total_travel_time = 0
            candidate_path = []
            valid = True
            for i in range(len(sequence) - 1):
                subpath, subtime = self.get_shortest_route(sequence[i], sequence[i + 1])
                if subpath is None:
                    valid = False
                    break
                if i == 0:
                    candidate_path.extend(subpath)
                else:
                    # 避免重复加入上一个子路径的终点
                    candidate_path.extend(subpath[1:])
                total_travel_time += subtime
            if valid and total_travel_time < best_travel_time:
                best_travel_time = total_travel_time
                best_path = candidate_path

        if best_path is None:
            return None, None

        # 计算各景点的游玩时长（按路径中每个景点的参考时长求和）
        visit_time = sum(self.vertex_time.get(v, 0) for v in best_path)
        total_time = best_travel_time + visit_time
        return best_path, [best_travel_time, visit_time, total_time]

    def find_wc(self, start):
        """
        在图中查找最近的厕所。
        """
        path1, time1 = self.get_shortest_route(start, '厕所1')
        path2, time2 = self.get_shortest_route(start, '厕所2')
        if time1 <= time2:
            return path1, time1
        else:
            return path2, time2


if __name__ == "__main__":
    graph = Graph()
    graph.create_graph()

    # 示例：求最短路径
    vertices = ['南门入口', '怡红院', '曲径通幽处', '沁芳桥亭', '秋爽斋',
                '潇湘馆', '稻香村', '缀锦楼', '花溆', '蘅芜苑', '省亲牌坊/别墅', '栊翠庵']
    print("求最短路径（从南门入口出发）：")
    for v in vertices:
        path, time_val = graph.get_shortest_route('南门入口', v)
        print(f"路径: {path}")
        print(f"总旅行时间: {time_val} 分钟")

    # 示例：构造必经景点路径（原“哈密顿路径”）
    hamilton_start = '南门入口'
    hamilton_end = '潇湘馆'
    required_points = ['南门入口', '曲径通幽处', '秋爽斋', '潇湘馆', '沁芳桥亭']
    print(f"\n构造必经景点路径 (起点: {hamilton_start}, 终点: {hamilton_end}) ：")
    path, times = graph.get_visit_path(required_points, start=hamilton_start, end=hamilton_end)
    print(f"路径: {path}")
    if times:
        print(f"旅行时间: {times[0]} 分钟，游玩时长: {times[1]} 分钟，总计: {times[2]} 分钟")
    else:
        print("无法规划出满足条件的游览路线。")

    # 示例：查找最近的厕所
    wc_start = '潇湘馆'
    print(f"\n查找最近的厕所 (起点: {wc_start}) ：")
    path, time_val = graph.find_wc(wc_start)
    print(f"路径: {path}")
    print(f"总时间: {time_val} 分钟")
