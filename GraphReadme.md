图模块

使用
graph = Graph()
graph.create_graph()
语句定义图并载入所有需要的点和边，点和边信息的修改可以在create_graph中进行

使用
graph.get_shortest_route(start,end)
求最短路径，传入起始和结束结点的中文名字符串；返回路径（字符串列表）和时间（int）

使用
graph.get_eulerian_tour(points, start,end)
求欧拉路径，传入需要经过的所有点集（字符串列表）、起点和终点；返回路径和时间（一个三元列表，元素分别为路上的时间、景点中游玩时长、总消耗时间）

使用
graph.get_hamiltonian_path(points, start，end)
求哈密顿路径，与欧拉路径使用方法一致

使用
graph.find_wc(start)
求到最近的厕所的路径的距离和时间，传入起点；返回返回路径（字符串列表）和时间（int）