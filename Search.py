class ScenicSpot:
    def __init__(self, id, name, description, tags, heat=0, flower="", visit_count=0):
        self.id = id          # 景点唯一标识
        self.name = name      # 景点名称（如"潇湘馆"）
        self.description = description  # 简介
        self.tags = tags      # 标签列表（如["园林","黛玉居所"]）
        self.heat = heat      # 热度值（根据访问量动态更新）
        self.flower = flower  # 花签词
        self.visit_count = visit_count  # 新增浏览人次属性

# 修正景点初始化参数（特别注意第6、11号景点的参数修正）
all_spots = [
    ScenicSpot(1, "大观园正门", "金陵十二钗影壁所在地", ["入口","标志性建筑","影视取景"], 120),
    ScenicSpot(2, "怡红院", "贾宝玉住所，金丝楠木雕花床与绛云轩匾额", ["贾宝玉居所","核心场景","富丽堂皇"], 155),
    ScenicSpot(3, "潇湘馆", "林黛玉住所，千竿翠竹环绕的幽静院落", ["林黛玉居所","诗词文化","竹林景观"], 148, "芙蓉花 - \"莫怨东风当自嗟\""),
    ScenicSpot(4, "蘅芜苑", "薛宝钗住所，奇石异草与雪洞般简朴陈设", ["薛宝钗居所","植物景观","蘅芷清芬"], 135, "牡丹花 - \"任是无情也动人\""),
    ScenicSpot(5, "大观楼", "元妃省亲主殿，顶层观景台可俯瞰全园", ["核心建筑","全景俯瞰","省亲仪式"], 142),
    ScenicSpot(6, "稻香村", "李纨居所，田园风光与纺车展示区", ["李纨居所","田园景观","亲子体验"], 110, "老梅 - \"竹篱茅舍自甘心\""),
    ScenicSpot(7, "藕香榭", "水岸亭台，中秋联诗与荷塘景观", ["水景建筑","中秋活动","夏日赏荷"], 128),
    ScenicSpot(8, "凹晶溪馆", "黛玉湘云联诗处，夜景投影展示", ["诗词场景","水岸夜景","中秋特展"], 118),
    ScenicSpot(9, "栊翠庵", "妙玉修行地，冬季红梅与茶道体验", ["宗教建筑","梅花观赏","茶文化"], 125),
    ScenicSpot(10, "紫菱洲", "贾迎春居所，临水棋枰与残荷景观", ["贾迎春居所","水榭","秋日景观"], 105),
    ScenicSpot(11, "秋爽斋", "探春居所，大案书画与梧桐庭院", ["贾探春居所","书法展示","秋景"], 112, "杏花 - \"日边红杏倚云栽\""),
    ScenicSpot(12, "暖香坞", "贾惜春居所，画室与佛教艺术展", ["贾惜春居所","绘画艺术","佛教文化"], 98),
    ScenicSpot(13, "滴翠亭", "宝钗扑蝶经典场景再现", ["经典场景","亭台","春日活动"], 138),
    ScenicSpot(14, "曲径通幽", "入口假山秘境，题刻贾政试才处", ["园林景观","题刻","入园第一景"], 132),
    ScenicSpot(15, "凸碧山庄", "中秋赏月主场地，与凹晶溪馆对景", ["山顶景观","中秋赏月","对景建筑"], 115),
    ScenicSpot(16, "红香圃", "芍药栏畔史湘云醉眠石凳", ["经典场景","花卉观赏","春日打卡"], 127, "海棠花 - \"只恐夜深花睡去\""),
    ScenicSpot(17, "芦雪庵", "琉璃世界联诗烤鹿肉场景还原", ["冬日景观","诗词活动","美食体验"], 122),
    ScenicSpot(18, "嘉荫堂", "贾母八旬寿宴举办地", ["宴饮场所","寿文化","建筑彩绘"], 108),
    ScenicSpot(19, "顾恩思义殿", "省亲别墅主殿，皇家气派展示", ["皇家礼仪","省亲仪式","主殿"], 95),
    ScenicSpot(20, "沁芳闸", "宝黛读西厢与葬花路线起点", ["经典场景","水系枢纽","爱情路线"], 145)
]

def find_spots(query):
    """支持名称精确查找和标签模糊查找的景点检索"""
    results = []
    
    # 名称精确查找（二分查找优化）
    sorted_spots = sorted(all_spots, key=lambda x: x.name)
    left, right = 0, len(sorted_spots)-1
    
    while left <= right:
        mid = (left + right) // 2
        if sorted_spots[mid].name == query:
            # 找到后向两边扩展收集所有同名景点
            i = mid
            while i >= 0 and sorted_spots[i].name == query:
                results.append(sorted_spots[i])
                i -= 1
            i = mid + 1
            while i < len(sorted_spots) and sorted_spots[i].name == query:
                results.append(sorted_spots[i])
                i += 1
            break
        elif sorted_spots[mid].name < query:
            left = mid + 1
        else:
            right = mid - 1
    
    if not results:
        for spot in all_spots:
            if query in spot.tags:
                results.append(spot)
    
    # 去重处理（防止同名或重复标签）
    seen_ids = set()
    unique_results = []
    for spot in results:
        if spot.id not in seen_ids:
            seen_ids.add(spot.id)
            unique_results.append(spot)
    
    return unique_results

def display_spots(spots):
    """格式化输出景点详细信息"""
    print(f"{'名称':<8} | {'简介':<20} | {'热度':<6} | {'花签词':<18} | {'浏览人次':<8}")
    print("-" * 70)
    for spot in spots:
        print(f"{spot.name:<8} | {spot.description[:16]:<20} | {spot.heat:<6} | {str(spot.flower)[:14]:<18} | {spot.visit_count:<8}")

if __name__ == "__main__":
    # 查找示例
    query = input("请输入要查找的景点名称或关键词：")
    found_spots = find_spots(query)
    
    if found_spots:
        print(f"\n找到 {len(found_spots)} 个相关景点：")
        display_spots(found_spots)
    else:
        print("未找到相关景点")

    # 更新浏览人次示例（演示如何操作visit_count）
    for spot in all_spots:
        if spot.name == "潇湘馆":
            spot.visit_count += 1  # 每次查询后增加浏览量
            print(f"\n{spot.name} 的最新浏览人次已更新为：{spot.visit_count}")