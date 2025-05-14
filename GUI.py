import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from Graph import Graph
from Sorting import Sorter, InsertionSortStrategy, chinese_to_pinyin_initials
from openai import OpenAI
import threading
import ast


# 更新文件信息
def update_scenery_visit_count(scenery_name, file_path):
    """
    遍历 txt 文件中的每一行，找到匹配景点名称的记录，
    将该记录中浏览人数（第5个字段）加 1，并写回文件。
    """
    updated_lines = []
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                # 跳过空行
                if not line_str:
                    continue
                try:
                    # 注意原文件每行格式如:
                    # "大观园正门", "金陵十二钗影壁所在地", ["入口","标志性建筑","影视取景"], 120,0
                    record = list(ast.literal_eval('(' + line_str + ')'))
                except Exception as e:
                    print("解析记录失败，跳过该行:", line_str, e)
                    updated_lines.append(line)
                    continue

                if record[0] == scenery_name:
                    # record[4] 为浏览人数，更新 +1
                    record[4] = record[4] + 1
                    # 重新构造一行内容，利用 repr 保持数据格式（数字不带引号，字符串带引号）
                    new_line = ", ".join(repr(x) for x in record)
                    updated_lines.append(new_line + "\n")
                else:
                    updated_lines.append(line)
        # 将更新后的所有行写回文件
        with open(file_path, 'w', encoding="utf-8") as f:
            f.writelines(updated_lines)
    except Exception as e:
        print("更新浏览人数失败:", e)


# 读取文件信息
def load_scenery_info(file_path):
    """
    从txt文件中读取详细景点信息，并返回以景点名称为键的字典。
    每行格式示例：
    "大观园正门", "金陵十二钗影壁所在地", ["入口","标志性建筑","影视取景"], 120,0
    或带有可选花签词的情况。
    """
    scenery_dict = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    # 用括号包裹后解析成元组
                    record = ast.literal_eval('(' + line + ')')
                    # 按顺序解析：名称, 简介, 标签列表, 热度, 浏览人次, [花签词]
                    name = record[0]
                    description = record[1]
                    tags = record[2]
                    popularity = record[3]
                    visit_count = record[4]
                    flower = record[5] if len(record) > 5 else ""
                    scenery_dict[name] = {
                        "name": name,
                        "description": description,
                        "tags": tags,
                        "popularity": popularity,
                        "visit_count": visit_count,
                        "flower": flower,
                    }
                except Exception as e:
                    print("解析景点记录失败:", line, e)
        return scenery_dict
    except Exception as e:
        print("读取景点文件失败:", e)
        return {}


# 地图显示部件
class Map(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.resize(2494, 1402)
        self.bg_image = QtGui.QImage("MAP.png")
        self.original_bg_size = self.bg_image.size()
        self.zoom_factor = 1.0
        self.pan_offset = QtCore.QPoint(0, 0)
        self.last_mouse_pos = None
        self.buttons = []
        self.current_path = []  # 存储当前要绘制的点序列
        self.loadbuttons("SceneryPosition.txt")

    def loadbuttons(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(" ")
                    if len(parts) < 3:
                        print(f"跳过无效的行: {line}")
                        continue
                    name = parts[0]
                    try:
                        x = int(parts[1])
                        y = int(parts[2])
                    except ValueError:
                        print(f"坐标转换错误: {line}")
                        continue
                    # 固定设置热度和浏览次数为默认值0，不读取后续数据
                    popularity = 0
                    visits = 0
                    button = CircularPushButton(name, 60, self)
                    button.original_pos = QtCore.QPoint(x, y)
                    button.info = {
                        "name": name,
                        "x": x,
                        "y": y,
                        "popularity": popularity,
                        "visits": visits
                    }
                    self.buttons.append(button)
        except Exception as e:
            print("读取文件错误:", e)

    def updateview(self):
        fit_scale = min(self.width() / self.original_bg_size.width(),
                        self.height() / self.original_bg_size.height())
        actual_scale = fit_scale * self.zoom_factor
        target_width = int(self.original_bg_size.width() * actual_scale)
        target_height = int(self.original_bg_size.height() * actual_scale)
        offset_x = (self.width() - target_width) // 2 + self.pan_offset.x()
        offset_y = (self.height() - target_height) // 2 + self.pan_offset.y()

        for button in self.buttons:
            new_x = int(button.original_pos.x() * actual_scale) + offset_x
            new_y = int(button.original_pos.y() * actual_scale) + offset_y
            button.move(new_x, new_y)
            if self.zoom_factor == 1.0:
                button.show()
            else:
                button.hide()
        self.update()

    def paintEvent(self, event):
   #     super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        fit_scale = min(self.width() / self.original_bg_size.width(),
                        self.height() / self.original_bg_size.height())
        actual_scale = fit_scale * self.zoom_factor
        target_width = int(self.original_bg_size.width() * actual_scale)
        target_height = int(self.original_bg_size.height() * actual_scale)
        offset_x = (self.width() - target_width) // 2 + self.pan_offset.x()
        offset_y = (self.height() - target_height) // 2 + self.pan_offset.y()

        scaled_image = self.bg_image.scaled(target_width, target_height,
                                            QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
                                            QtCore.Qt.TransformationMode.SmoothTransformation)

        painter.drawImage(offset_x, offset_y, scaled_image)

        if self.current_path:
            pen = QtGui.QPen(QtGui.QColor(255,215,0), 4
                             , QtCore.Qt.PenStyle.SolidLine)
            pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
            pen.setDashPattern([8, 4])

            painter.setPen(pen)

            # 找到每个节点的中心，转换成 QPointF
            pts = []
            for name in self.current_path:
                btn = next((b for b in self.buttons if b.info.get("name") == name), None)
                if btn:
                    c = btn.geometry().center()
                    pts.append(QtCore.QPointF(c.x(), c.y()))
            if len(pts) >= 2:
                path = QtGui.QPainterPath(pts[0])
                for p in pts[1:]:
                    path.lineTo(p)
                painter.drawPath(path)


    def resizeEvent(self, event):
        self.updateview()
        super().resizeEvent(event)
    def clear_path(self):
        self.current_path = []
        self.update()
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is not None:
            delta = event.pos() - self.last_mouse_pos
            self.pan_offset += delta
            self.last_mouse_pos = event.pos()
            self.updateview()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.last_mouse_pos = None
        super().mouseReleaseEvent(event)

    def zoom_in(self):
        self.zoom_factor += 0.2
        self.updateview()

    def zoom_out(self):
        self.zoom_factor -= 0.2
        self.updateview()

    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.pan_offset = QtCore.QPoint(0, 0)
        self.updateview()


# 圆形景点按钮
class CircularPushButton(QtWidgets.QPushButton):
    def __init__(self, text, diameter=60, parent=None):
        super().__init__("", parent)
        self._button_text = text
        self._diameter = diameter
        self.setFixedSize(QtCore.QSize(diameter, diameter))
        self.setStyleSheet("QPushButton { border: none; background-color: transparent;}")
        self.setMask(QtGui.QRegion(self.rect(), QtGui.QRegion.RegionType.Ellipse))
        self.clicked.connect(self.handle_click)
        self.info = {}

    def handle_click(self):
        dialog = SceneryInfoDialog(self.info, self)
        dialog.exec()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setMask(QtGui.QRegion(self.rect(), QtGui.QRegion.RegionType.Ellipse))


# 景点信息对话框
class SceneryInfoDialog(QtWidgets.QDialog):
    def __init__(self, info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("景点信息")
        self.setFixedSize(350, 300)
        layout = QtWidgets.QVBoxLayout(self)

        # 获取景点名称
        name = info.get("name", "")
        # 更新文件中对应景点的浏览人数（每次显示时+1）
        update_scenery_visit_count(name, "Scenerydetail.txt")

        # 重新加载详细景点信息（假设文件格式参考 :contentReference[oaicite:1]{index=1}）
        scenery_details = load_scenery_info("SceneryDetail.txt")
        details = scenery_details.get(name, {
            "name": name,
            "description": "暂无详细信息",
            "tags": [],
            "popularity": 0,
            "visit_count": 0,
            "flower": ""
        })

        name_label = QtWidgets.QLabel(f"名称: {details.get('name', '')}")
        desc_label = QtWidgets.QLabel(f"简介: {details.get('description', '')}")
        tags_label = QtWidgets.QLabel(f"标签: {', '.join(details.get('tags', []))}")
        popularity_label = QtWidgets.QLabel(f"热度: {details.get('popularity', 0)}")
        visits_label = QtWidgets.QLabel(f"浏览人数: {details.get('visit_count', 0)}")
        flower_label = QtWidgets.QLabel(
            f"花签词: {details.get('flower', '无')}" if details.get('flower') else "花签词: 无")

        layout.addWidget(name_label)
        layout.addWidget(desc_label)
        layout.addWidget(tags_label)
        layout.addWidget(popularity_label)
        layout.addWidget(visits_label)
        layout.addWidget(flower_label)

        btn = QtWidgets.QPushButton("确定")
        btn.setFixedSize(60, 30)
        btn.setStyleSheet("QPushButton { border: 1px solid gray; }")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)


# 搜索对话框
class SearchDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("搜索景点")
        self.resize(400, 300)
        self.attractions = []
        # 读取详细景点信息，文件为“SceneryDetail.txt”
        self.loadattractions("SceneryDetail.txt")
        self.initUI()

    def loadattractions(self, filename):
        try:
            # 调用上面定义的 load_scenery_info 解析详细信息
            scenery_details = load_scenery_info(filename)
            # 将字典的值转为列表存入 attractions 中
            self.attractions = list(scenery_details.values())
        except Exception as e:
            print("读取文件错误:", e)

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.search_line = QtWidgets.QLineEdit(self)
        self.search_line.setPlaceholderText("请输入搜索内容")
        layout.addWidget(self.search_line)

        self.sort_combo = QtWidgets.QComboBox(self)
        self.sort_combo.addItems([
            "名称升序", "名称降序",
            "热度升序", "热度降序",
            "游览人数升序", "游览人数降序"
        ])
        layout.addWidget(self.sort_combo)

        self.list_widget = QtWidgets.QListWidget(self)
        layout.addWidget(self.list_widget)

        btn_layout = QtWidgets.QHBoxLayout()
        self.ok_button = QtWidgets.QPushButton("确定", self)
        self.cancel_button = QtWidgets.QPushButton("取消", self)
        btn_layout.addWidget(self.ok_button)
        btn_layout.addWidget(self.cancel_button)
        layout.addLayout(btn_layout)

        self.search_line.textChanged.connect(self.updateList)
        self.sort_combo.currentIndexChanged.connect(self.updateList)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.updateList()

    def updateList(self):
        search_text = self.search_line.text().strip()
        sort_option = self.sort_combo.currentText()
        if sort_option == "名称升序":
            key_func = lambda a: chinese_to_pinyin_initials(a["name"])
            reverse = False
        elif sort_option == "名称降序":
            key_func = lambda a: chinese_to_pinyin_initials(a["name"])
            reverse = True
        elif sort_option == "热度升序":
            key_func = lambda a: a["popularity"]
            reverse = False
        elif sort_option == "热度降序":
            key_func = lambda a: a["popularity"]
            reverse = True
        elif sort_option == "游览人数升序":
            key_func = lambda a: a["visit_count"]
            reverse = False
        elif sort_option == "游览人数降序":
            key_func = lambda a: a["visit_count"]
            reverse = True
        else:
            key_func = lambda a: chinese_to_pinyin_initials(a["name"])
            reverse = False

        filtered = [a for a in self.attractions if
                    search_text.lower() in a["name"].lower()] if search_text else self.attractions[:]
        sorter = Sorter(strategy=InsertionSortStrategy(), key=key_func, reverse=reverse)
        filtered = sorter.sort(filtered)
        self.list_widget.clear()
        for a in filtered:
            # 此处显示名称、热度和浏览人数（visit_count）
            item_text = f"{a['name']} (热度: {a['popularity']}  游览: {a['visit_count']})"
            self.list_widget.addItem(item_text)


# 选景点对话框：用于规划游览路线，用户从所有景点中选择必经景点，同时确定起点和终点
class SightseeingRouteDialog(QtWidgets.QDialog):
    def __init__(self, attractions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("规划游览路线")
        self.resize(400, 400)
        self.attractions = attractions
        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel("请选择必经景点 (至少1个):")
        layout.addWidget(label)

        self.list_widget = QtWidgets.QListWidget(self)
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        for a in attractions:
            self.list_widget.addItem(a)
        layout.addWidget(self.list_widget)

        form_layout = QtWidgets.QFormLayout()
        self.start_combo = QtWidgets.QComboBox()
        self.end_combo = QtWidgets.QComboBox()
        form_layout.addRow("起点:", self.start_combo)
        form_layout.addRow("终点:", self.end_combo)
        layout.addLayout(form_layout)

        # 初始时组合框显示全体景点
        self.update_combos()
        self.list_widget.itemSelectionChanged.connect(self.update_combos)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def update_combos(self):
        selected_items = self.list_widget.selectedItems()
        selected_names = [item.text() for item in selected_items]
        # 若未选择，则组合框显示所有景点
        if not selected_names:
            selected_names = self.attractions
        self.start_combo.clear()
        self.end_combo.clear()
        self.start_combo.addItems(selected_names)
        self.end_combo.addItems(selected_names)

    def get_selection(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            required = [item.text() for item in selected_items]
        else:
            required = []
        start = self.start_combo.currentText()
        end = self.end_combo.currentText()
        return required, start, end


# 最短路线
class ShortestRoutePlanDialog(QtWidgets.QDialog):
    def __init__(self, attractions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("最短路线")
        self.setFixedSize(300, 150)
        layout = QtWidgets.QVBoxLayout(self)

        form_layout = QtWidgets.QFormLayout()
        self.start_combo = QtWidgets.QComboBox()
        self.start_combo.addItems(attractions)
        self.end_combo = QtWidgets.QComboBox()
        self.end_combo.addItems(attractions)
        form_layout.addRow("起点:", self.start_combo)
        form_layout.addRow("终点:", self.end_combo)
        layout.addLayout(form_layout)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


# 主窗口
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("地图程序")
        self.resize(1200, 715)
        self.createToolBar()
        self.map_widget = Map()
        self.setCentralWidget(self.map_widget)

    def createToolBar(self):
        toolbar = QtWidgets.QToolBar("工具栏")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setFixedHeight(40)
        font = QtGui.QFont()
        font.setPointSize(14)
        toolbar.setFont(font)
        self.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, toolbar)

        zoom_in_action = QtGui.QAction("放大", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)

        zoom_out_action = QtGui.QAction("缩小", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)

        reset_action = QtGui.QAction("重置", self)
        reset_action.triggered.connect(self.reset_view)
        toolbar.addAction(reset_action)

        search_action = QtGui.QAction("搜索", self)
        search_action.triggered.connect(self.show_search_dialog)
        toolbar.addAction(search_action)

        shortest_route_action = QtGui.QAction("最短路线", self)
        shortest_route_action.triggered.connect(self.plan_shortest_route)
        toolbar.addAction(shortest_route_action)

        visit_route_action = QtGui.QAction("路线规划", self)
        visit_route_action.triggered.connect(self.plan_visit_route)
        toolbar.addAction(visit_route_action)

        ai_action = QtGui.QAction("AI问答", self)
        ai_action.triggered.connect(self.show_ai_dialog)
        toolbar.addAction(ai_action)

    # AI 问答对话框
    def show_ai_dialog(self):
        dialog = AIDialog(self)
        dialog.exec()

    # 放大
    def zoom_in(self):
        self.map_widget.zoom_in()

    # 缩小
    def zoom_out(self):
        self.map_widget.zoom_out()

    # 重置
    def reset_view(self):
        self.map_widget.reset_zoom()

    # 搜索
    def show_search_dialog(self):
        dialog = SearchDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            selected_items = dialog.list_widget.selectedItems()
            if selected_items:
                name = selected_items[0].text().split(" ")[0]
                info = {"name": name}
                detail_dialog = SceneryInfoDialog(info, self)
                detail_dialog.exec()
            else:
                print("未选择景点")
        else:
            print("搜索取消")

    # 最短路径规划
    def plan_shortest_route(self):
        from PyQt6.QtWidgets import QMessageBox
        graph = Graph()
        graph.create_graph()
        attractions = list(graph.vertex_time.keys())
        dialog = ShortestRoutePlanDialog(attractions, self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            start = dialog.start_combo.currentText()
            target = dialog.end_combo.currentText()
            if start == target:
                QMessageBox.warning(self, "输入错误", "起点与终点不能相同！")
                return
            path, time_val = graph.get_shortest_route(start, target)
            if path is None:
                QMessageBox.information(self, "结果", f"从 {start} 到 {target} 无法找到路径。")
            else:
                QMessageBox.information(self, "路线规划结果",
                                        f"最短路径：{' -> '.join(path)}\n总旅行时间：{time_val} 分钟")
                # 在地图上绘制
                self.map_widget.current_path = path
                self.map_widget.update()
                # 5秒后清除
                QtCore.QTimer.singleShot(6480, lambda: self.map_widget.clear_path())
        else:
            print("最短路线规划取消")

    # 游览路径规划
    def plan_visit_route(self):
        from PyQt6.QtWidgets import QMessageBox
        graph = Graph()
        graph.create_graph()
        all_attractions = list(graph.vertex_time.keys())
        dialog = SightseeingRouteDialog(all_attractions, self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            required, start, end = dialog.get_selection()
            if not required:
                QMessageBox.warning(self, "输入错误", "请至少选择一个必经景点。")
                return
            if start not in required or end not in required:
                QMessageBox.warning(self, "输入错误", "起点和终点必须在必经景点中。")
                return
            path, times = graph.get_visit_path(required, start=start, end=end)
            if not path:
                QMessageBox.information(self, "结果", "无法规划出满足条件的游览路线。")
            else:
                travel_time, visit_time, total_time = times
                QMessageBox.information(self, "路径规划结果",
                                        f"游览路线：{' -> '.join(path)}\n旅行时间：{travel_time} 分钟\n游玩时长：{visit_time} 分钟\n总计：{total_time} 分钟")
                # 在地图上绘制
                self.map_widget.current_path = path
                self.map_widget.update()
                # 5秒后清除
                QtCore.QTimer.singleShot(6480, lambda: self.map_widget.clear_path())

        else:
            print("游览规划取消")


# 设置 OpenAI API 密钥（请替换成你自己的密钥，或从环境变量中读取）
client = OpenAI(
    api_key="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")


# AI 问答对话框
class AIDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI问答")
        self.resize(500, 400)

        layout = QtWidgets.QVBoxLayout(self)

        # 用户输入问题的多行文本框
        self.question_edit = QtWidgets.QTextEdit(self)
        self.question_edit.setPlaceholderText("请输入你的问题...")
        layout.addWidget(self.question_edit)

        # 展示 AI 回答的只读多行文本框
        self.answer_edit = QtWidgets.QTextEdit(self)
        self.answer_edit.setReadOnly(True)
        layout.addWidget(self.answer_edit)

        # 按钮布局
        btn_layout = QtWidgets.QHBoxLayout()
        self.ask_button = QtWidgets.QPushButton("提交", self)
        self.cancel_button = QtWidgets.QPushButton("取消", self)
        btn_layout.addWidget(self.ask_button)
        btn_layout.addWidget(self.cancel_button)
        layout.addLayout(btn_layout)

        self.ask_button.clicked.connect(self.submit_question)
        self.cancel_button.clicked.connect(self.reject)

    def submit_question(self):
        question = self.question_edit.toPlainText().strip()
        if not question:
            QtWidgets.QMessageBox.warning(self, "错误", "请输入问题后再提交。")
            return

        self.answer_edit.setPlainText("正在查询，请稍后...")
        self.ask_button.setEnabled(False)

        # 使用新线程调用 API，以免阻塞 GUI 主线程
        thread = threading.Thread(target=self.get_ai_answer, args=(question,))
        thread.start()

    def get_ai_answer(self, question):
        try:
            # 将系统角色和用户问题合并为一个输入提示
            system_msg = "假设你是一个大观园景区的导游，用户向你提问，请你解答。"
            prompt = f"{system_msg}\n以下为用户的提问：{question}\n"
            # 调用 API 接口，传入输入字符串
            response = client.responses.create(
                model="gpt-4o",
                input=prompt
            )
            answer = response.output_text.strip()
        except Exception as e:
            answer = f"调用 OpenAI API 时出错：{e}"

        # 使用 QMetaObject.invokeMethod 安全地在主线程中更新界面
        QtCore.QMetaObject.invokeMethod(
            self,
            "update_answer",
            QtCore.Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, answer)
        )

    @QtCore.pyqtSlot(str)
    def update_answer(self, answer):
        self.answer_edit.setPlainText(answer)
        self.ask_button.setEnabled(True)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
