"""
模拟器图标种子数据脚本 - 使用 SQLite 直接访问
"""

import sqlite3
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'hercu.db')

ICONS_DATA = [
    # 基础形状
    ("circle", "圆形", "Circle", "basic", "#3B82F6"),
    ("rect", "矩形", "Rectangle", "basic", "#10B981"),
    ("star", "五角星", "Star", "basic", "#F59E0B"),
    ("diamond", "菱形", "Diamond", "basic", "#8B5CF6"),
    ("hexagon", "六边形", "Hexagon", "basic", "#EC4899"),
    ("triangle", "三角形", "Triangle", "basic", "#EF4444"),
    ("arrow", "箭头", "Arrow", "basic", "#6366F1"),
    # 教育学习
    ("book", "书本", "Book", "education", "#3B82F6"),
    ("pencil", "铅笔", "Pencil", "education", "#F59E0B"),
    ("graduation", "学士帽", "Graduation Cap", "education", "#1F2937"),
    ("certificate", "证书", "Certificate", "education", "#F59E0B"),
    ("blackboard", "黑板", "Blackboard", "education", "#1F2937"),
    ("notebook", "笔记本", "Notebook", "education", "#3B82F6"),
    ("ruler", "直尺", "Ruler", "education", "#F59E0B"),
    ("eraser", "橡皮", "Eraser", "education", "#EC4899"),
    ("schoolBag", "书包", "School Bag", "education", "#3B82F6"),
    ("globe", "地球仪", "Globe", "education", "#3B82F6"),
    # 科学实验
    ("flask", "烧瓶", "Flask", "science", "#10B981"),
    ("testTube", "试管", "Test Tube", "science", "#3B82F6"),
    ("microscope", "显微镜", "Microscope", "science", "#6B7280"),
    ("atom", "原子", "Atom", "science", "#3B82F6"),
    ("dna", "DNA", "DNA", "science", "#8B5CF6"),
    ("molecule", "分子", "Molecule", "science", "#10B981"),
    ("beaker", "烧杯", "Beaker", "science", "#3B82F6"),
    ("magnet", "磁铁", "Magnet", "science", "#EF4444"),
    ("telescope", "望远镜", "Telescope", "science", "#6B7280"),
    ("prism", "棱镜", "Prism", "science", "#8B5CF6"),
    # 思维认知
    ("brain", "大脑", "Brain", "cognition", "#EC4899"),
    ("lightbulb", "灯泡", "Lightbulb", "cognition", "#F59E0B"),
    ("puzzle", "拼图", "Puzzle", "cognition", "#3B82F6"),
    ("target", "靶心", "Target", "cognition", "#EF4444"),
    ("questionMark", "问号", "Question Mark", "cognition", "#8B5CF6"),
    ("checkMark", "对勾", "Check Mark", "cognition", "#10B981"),
    ("crossMark", "叉号", "Cross Mark", "cognition", "#EF4444"),
    ("idea", "创意", "Idea", "cognition", "#F59E0B"),
    # 自然生物
    ("tree", "树木", "Tree", "nature", "#10B981"),
    ("flower", "花朵", "Flower", "nature", "#EC4899"),
    ("leaf", "树叶", "Leaf", "nature", "#10B981"),
    ("sun", "太阳", "Sun", "nature", "#F59E0B"),
    ("moon", "月亮", "Moon", "nature", "#F59E0B"),
    ("cloud", "云朵", "Cloud", "nature", "#94A3B8"),
    ("water", "水滴", "Water Drop", "nature", "#3B82F6"),
    ("fire", "火焰", "Fire", "nature", "#EF4444"),
    ("mountain", "山峰", "Mountain", "nature", "#6B7280"),
    ("wave", "波浪", "Wave", "nature", "#3B82F6"),
    # 人体解剖
    ("heart", "心脏", "Heart", "anatomy", "#EF4444"),
    ("lung", "肺部", "Lung", "anatomy", "#EC4899"),
    ("skeleton", "骨骼", "Skeleton", "anatomy", "#F5F5F4"),
    ("muscle", "肌肉", "Muscle", "anatomy", "#EF4444"),
    ("eye", "眼睛", "Eye", "anatomy", "#3B82F6"),
    ("hand", "手掌", "Hand", "anatomy", "#F5D0C5"),
    ("joint", "关节", "Joint", "anatomy", "#F5F5F4"),
    # 体育运动
    ("basketball", "篮球", "Basketball", "sports", "#F97316"),
    ("football", "足球", "Football", "sports", "#1F2937"),
    ("tennis", "网球", "Tennis", "sports", "#84CC16"),
    ("swimming", "游泳", "Swimming", "sports", "#3B82F6"),
    ("running", "跑步", "Running", "sports", "#F97316"),
    ("cycling", "骑行", "Cycling", "sports", "#3B82F6"),
    ("yoga", "瑜伽", "Yoga", "sports", "#8B5CF6"),
    # 体育器材
    ("dumbbell", "哑铃", "Dumbbell", "sports_equipment", "#6B7280"),
    ("racket", "球拍", "Racket", "sports_equipment", "#F59E0B"),
    ("stopwatch", "秒表", "Stopwatch", "sports_equipment", "#6B7280"),
    # 运动动作
    ("runningPose", "跑步姿势", "Running Pose", "sports_action", "#F97316"),
    ("jumpingPose", "跳跃姿势", "Jumping Pose", "sports_action", "#3B82F6"),
    ("squatPose", "深蹲姿势", "Squat Pose", "sports_action", "#8B5CF6"),
    # 机械工程
    ("gear", "齿轮", "Gear", "mechanical", "#6B7280"),
    ("wrench", "扳手", "Wrench", "mechanical", "#6B7280"),
    ("hammer", "锤子", "Hammer", "mechanical", "#92400E"),
    ("pulley", "滑轮", "Pulley", "mechanical", "#6B7280"),
    ("lever", "杠杆", "Lever", "mechanical", "#92400E"),
    # 电子电气
    ("battery", "电池", "Battery", "electronic", "#10B981"),
    ("circuit", "电路", "Circuit", "electronic", "#10B981"),
    ("led", "LED灯", "LED", "electronic", "#EF4444"),
    ("chip", "芯片", "Chip", "electronic", "#1F2937"),
    # 交通运输
    ("car", "汽车", "Car", "transport", "#3B82F6"),
    ("airplane", "飞机", "Airplane", "transport", "#3B82F6"),
    ("bicycle", "自行车", "Bicycle", "transport", "#10B981"),
    ("rocket", "火箭", "Rocket", "transport", "#EF4444"),
    # 医疗健康
    ("stethoscope", "听诊器", "Stethoscope", "medical", "#6B7280"),
    ("syringe", "注射器", "Syringe", "medical", "#3B82F6"),
    ("pill", "药丸", "Pill", "medical", "#EF4444"),
    # 音乐艺术
    ("musicNote", "音符", "Music Note", "art", "#1F2937"),
    ("guitar", "吉他", "Guitar", "art", "#92400E"),
    ("palette", "调色板", "Palette", "art", "#F59E0B"),
    ("camera", "相机", "Camera", "art", "#1F2937"),
    # 商业金融
    ("coin", "硬币", "Coin", "business", "#F59E0B"),
    ("chart", "图表", "Chart", "business", "#3B82F6"),
    ("calculator", "计算器", "Calculator", "business", "#6B7280"),
    # 食物饮品
    ("apple", "苹果", "Apple", "food", "#EF4444"),
    ("bread", "面包", "Bread", "food", "#F59E0B"),
    ("coffee", "咖啡", "Coffee", "food", "#92400E"),
    # 动物
    ("dog", "狗", "Dog", "animal", "#92400E"),
    ("cat", "猫", "Cat", "animal", "#F97316"),
    ("bird", "鸟", "Bird", "animal", "#3B82F6"),
    ("fish", "鱼", "Fish", "animal", "#3B82F6"),
    ("butterfly", "蝴蝶", "Butterfly", "animal", "#EC4899"),
    ("elephant", "大象", "Elephant", "animal", "#6B7280"),
    ("panda", "熊猫", "Panda", "animal", "#1F2937"),
    # 天文地理
    ("earth", "地球", "Earth", "geography", "#3B82F6"),
    ("volcano", "火山", "Volcano", "geography", "#EF4444"),
    ("compass", "指南针", "Compass", "geography", "#EF4444"),
    # 家具家电
    ("sofa", "沙发", "Sofa", "furniture", "#92400E"),
    ("table", "桌子", "Table", "furniture", "#92400E"),
    ("lamp", "台灯", "Lamp", "furniture", "#F59E0B"),
    ("tv", "电视", "TV", "furniture", "#1F2937"),
    # 日常用品
    ("clock", "时钟", "Clock", "daily", "#1F2937"),
    ("phone", "手机", "Phone", "daily", "#1F2937"),
    ("umbrella", "雨伞", "Umbrella", "daily", "#3B82F6"),
    # 厨房用品
    ("pot", "锅", "Pot", "kitchen", "#6B7280"),
    ("bowl", "碗", "Bowl", "kitchen", "#F5F5F4"),
    ("chopsticks", "筷子", "Chopsticks", "kitchen", "#92400E"),
    # 教室用品
    ("projector", "投影仪", "Projector", "classroom", "#1F2937"),
    ("whiteboard", "白板", "Whiteboard", "classroom", "#F5F5F4"),
    ("podium", "讲台", "Podium", "classroom", "#92400E"),
    # 数学工具
    ("protractor", "量角器", "Protractor", "math", "#3B82F6"),
    ("abacus", "算盘", "Abacus", "math", "#92400E"),
    ("pi", "圆周率", "Pi", "math", "#8B5CF6"),
    # 户外场景
    ("park", "公园", "Park", "outdoor", "#10B981"),
    ("tent", "帐篷", "Tent", "outdoor", "#10B981"),
    ("campfire", "篝火", "Campfire", "outdoor", "#F97316"),
    # 天气场景
    ("sunny", "晴天", "Sunny", "weather", "#F59E0B"),
    ("rainy", "下雨", "Rainy", "weather", "#3B82F6"),
    ("snowy", "下雪", "Snowy", "weather", "#F5F5F4"),
    ("rainbow", "彩虹", "Rainbow", "weather", "#EF4444"),
    # 时间场景
    ("morning", "早晨", "Morning", "time", "#F59E0B"),
    ("night", "夜晚", "Night", "time", "#1F2937"),
    ("calendar", "日历", "Calendar", "time", "#EF4444"),
    # 情绪表情
    ("happy", "开心", "Happy", "emotion", "#F59E0B"),
    ("sad", "伤心", "Sad", "emotion", "#3B82F6"),
    ("angry", "生气", "Angry", "emotion", "#EF4444"),
    ("love", "喜爱", "Love", "emotion", "#EC4899"),
    # 社交场景
    ("family", "家庭", "Family", "social", "#EC4899"),
    ("teacher", "老师", "Teacher", "social", "#10B981"),
    ("doctor", "医生", "Doctor", "social", "#F5F5F4"),
    # 工作场景
    ("computer", "电脑", "Computer", "office", "#1F2937"),
    ("folder", "文件夹", "Folder", "office", "#F59E0B"),
    # 安全场景
    ("fireExtinguisher", "灭火器", "Fire Extinguisher", "safety", "#EF4444"),
    ("warning", "警告", "Warning", "safety", "#F59E0B"),
    ("shield", "盾牌", "Shield", "safety", "#3B82F6"),
    ("exitSign", "安全出口", "Exit Sign", "safety", "#10B981"),
    ("firstAid", "急救箱", "First Aid", "safety", "#EF4444"),
    ("safetyVest", "安全背心", "Safety Vest", "safety", "#F59E0B"),
    ("safetyGoggles", "护目镜", "Safety Goggles", "safety", "#3B82F6"),
    ("gloves", "手套", "Gloves", "safety", "#F59E0B"),
    ("mask", "口罩", "Mask", "safety", "#F5F5F4"),
    ("danger", "危险", "Danger", "safety", "#EF4444"),
    ("lock", "锁", "Lock", "safety", "#F59E0B"),
    # 补充 - 人体解剖
    ("ear", "耳朵", "Ear", "anatomy", "#F5D0C5"),
    ("foot", "脚掌", "Foot", "anatomy", "#F5D0C5"),
    ("spine", "脊柱", "Spine", "anatomy", "#F5F5F4"),
    ("stomach", "胃", "Stomach", "anatomy", "#EC4899"),
    ("liver", "肝脏", "Liver", "anatomy", "#92400E"),
    ("kidney", "肾脏", "Kidney", "anatomy", "#92400E"),
    ("tooth", "牙齿", "Tooth", "anatomy", "#F5F5F4"),
    ("bloodCell", "血细胞", "Blood Cell", "anatomy", "#EF4444"),
    ("neuron", "神经元", "Neuron", "anatomy", "#8B5CF6"),
    # 补充 - 体育运动
    ("baseball", "棒球", "Baseball", "sports", "#F5F5F4"),
    ("volleyball", "排球", "Volleyball", "sports", "#F5F5F4"),
    ("badminton", "羽毛球", "Badminton", "sports", "#F5F5F4"),
    ("tableTennis", "乒乓球", "Table Tennis", "sports", "#F97316"),
    ("golf", "高尔夫", "Golf", "sports", "#F5F5F4"),
    ("skiing", "滑雪", "Skiing", "sports", "#3B82F6"),
    ("boxing", "拳击", "Boxing", "sports", "#EF4444"),
    ("weightlifting", "举重", "Weightlifting", "sports", "#6B7280"),
    ("gymnastics", "体操", "Gymnastics", "sports", "#EC4899"),
    # 补充 - 体育器材
    ("treadmill", "跑步机", "Treadmill", "sports_equipment", "#6B7280"),
    ("helmet", "头盔", "Helmet", "sports_equipment", "#1F2937"),
    ("skates", "溜冰鞋", "Skates", "sports_equipment", "#3B82F6"),
    ("skateboard", "滑板", "Skateboard", "sports_equipment", "#F59E0B"),
    ("jumpRope", "跳绳", "Jump Rope", "sports_equipment", "#EF4444"),
    ("mat", "瑜伽垫", "Yoga Mat", "sports_equipment", "#8B5CF6"),
    ("whistle", "哨子", "Whistle", "sports_equipment", "#F59E0B"),
    # 补充 - 运动动作
    ("stretchingPose", "拉伸姿势", "Stretching Pose", "sports_action", "#10B981"),
    ("pushupPose", "俯卧撑姿势", "Pushup Pose", "sports_action", "#EF4444"),
    ("situpPose", "仰卧起坐姿势", "Situp Pose", "sports_action", "#F59E0B"),
    ("plankPose", "平板支撑姿势", "Plank Pose", "sports_action", "#6366F1"),
    ("kickPose", "踢腿姿势", "Kick Pose", "sports_action", "#EC4899"),
    # 田径跳高专用
    ("startPoint", "起跑点", "Start Point", "track_field", "#22C55E"),
    ("curvePoint", "弧线转弯点", "Curve Point", "track_field", "#F59E0B"),
    ("takeoffPoint", "起跳点", "Takeoff Point", "track_field", "#EF4444"),
    ("highJumpBar", "跳高横杆", "High Jump Bar", "track_field", "#6B7280"),
    ("landingMat", "落地垫", "Landing Mat", "track_field", "#3B82F6"),
    ("runningPath", "直线助跑", "Running Path", "track_field", "#22C55E"),
    ("arcPath", "弧线助跑", "Arc Path", "track_field", "#F59E0B"),
    ("jumperTakeoff", "起跳姿势", "Jumper Takeoff", "track_field", "#3B82F6"),
    ("jumperArch", "背弓过杆", "Jumper Arch", "track_field", "#8B5CF6"),
    ("jumperLanding", "落地姿势", "Jumper Landing", "track_field", "#3B82F6"),
    # 补充 - 机械工程
    ("screwdriver", "螺丝刀", "Screwdriver", "mechanical", "#F59E0B"),
    ("bolt", "螺栓", "Bolt", "mechanical", "#6B7280"),
    ("nut", "螺母", "Nut", "mechanical", "#6B7280"),
    ("spring", "弹簧", "Spring", "mechanical", "#6B7280"),
    ("piston", "活塞", "Piston", "mechanical", "#6B7280"),
    ("bearing", "轴承", "Bearing", "mechanical", "#6B7280"),
    ("chain", "链条", "Chain", "mechanical", "#6B7280"),
    # 补充 - 电子电气
    ("resistor", "电阻", "Resistor", "electronic", "#F59E0B"),
    ("capacitor", "电容", "Capacitor", "electronic", "#3B82F6"),
    ("transistor", "晶体管", "Transistor", "electronic", "#1F2937"),
    ("switch", "开关", "Switch", "electronic", "#6B7280"),
    ("wire", "电线", "Wire", "electronic", "#EF4444"),
    ("motor", "电机", "Motor", "electronic", "#6B7280"),
    # 补充 - 建筑工程
    ("building", "建筑", "Building", "construction", "#6B7280"),
    ("crane", "起重机", "Crane", "construction", "#F59E0B"),
    ("brick", "砖块", "Brick", "construction", "#92400E"),
    ("cement", "水泥", "Cement", "construction", "#6B7280"),
    ("blueprint", "蓝图", "Blueprint", "construction", "#3B82F6"),
    ("hardhat", "安全帽", "Hard Hat", "construction", "#F59E0B"),
    # 补充 - 交通运输
    ("bus", "公交车", "Bus", "transport", "#F59E0B"),
    ("train", "火车", "Train", "transport", "#6B7280"),
    ("ship", "轮船", "Ship", "transport", "#6B7280"),
    ("motorcycle", "摩托车", "Motorcycle", "transport", "#EF4444"),
    ("helicopter", "直升机", "Helicopter", "transport", "#6B7280"),
    ("submarine", "潜艇", "Submarine", "transport", "#1F2937"),
    # 补充 - 医疗健康
    ("bandage", "绷带", "Bandage", "medical", "#F5F5F4"),
    ("thermometer", "体温计", "Thermometer", "medical", "#EF4444"),
    ("wheelchair", "轮椅", "Wheelchair", "medical", "#6B7280"),
    ("ambulance", "救护车", "Ambulance", "medical", "#F5F5F4"),
    ("hospital", "医院", "Hospital", "medical", "#EF4444"),
    # 补充 - 音乐艺术
    ("piano", "钢琴", "Piano", "art", "#1F2937"),
    ("violin", "小提琴", "Violin", "art", "#92400E"),
    ("drum", "鼓", "Drum", "art", "#EF4444"),
    ("microphone", "麦克风", "Microphone", "art", "#6B7280"),
    ("brush", "画笔", "Brush", "art", "#92400E"),
    ("film", "胶片", "Film", "art", "#1F2937"),
    # 补充 - 商业金融
    ("banknote", "钞票", "Banknote", "business", "#10B981"),
    ("creditCard", "信用卡", "Credit Card", "business", "#3B82F6"),
    ("briefcase", "公文包", "Briefcase", "business", "#92400E"),
    ("handshake", "握手", "Handshake", "business", "#F5D0C5"),
    ("piggyBank", "存钱罐", "Piggy Bank", "business", "#EC4899"),
    # 补充 - 食物饮品
    ("banana", "香蕉", "Banana", "food", "#F59E0B"),
    ("orange", "橙子", "Orange", "food", "#F97316"),
    ("grape", "葡萄", "Grape", "food", "#8B5CF6"),
    ("watermelon", "西瓜", "Watermelon", "food", "#10B981"),
    ("pizza", "披萨", "Pizza", "food", "#F59E0B"),
    ("hamburger", "汉堡", "Hamburger", "food", "#F59E0B"),
    ("tea", "茶", "Tea", "food", "#10B981"),
    ("iceCream", "冰淇淋", "Ice Cream", "food", "#EC4899"),
    ("cake", "蛋糕", "Cake", "food", "#EC4899"),
    # 补充 - 动物
    ("bee", "蜜蜂", "Bee", "animal", "#F59E0B"),
    ("ant", "蚂蚁", "Ant", "animal", "#1F2937"),
    ("spider", "蜘蛛", "Spider", "animal", "#1F2937"),
    ("rabbit", "兔子", "Rabbit", "animal", "#F5F5F4"),
    ("horse", "马", "Horse", "animal", "#92400E"),
    ("cow", "牛", "Cow", "animal", "#1F2937"),
    ("pig", "猪", "Pig", "animal", "#EC4899"),
    ("sheep", "羊", "Sheep", "animal", "#F5F5F4"),
    ("chicken", "鸡", "Chicken", "animal", "#F59E0B"),
    ("duck", "鸭", "Duck", "animal", "#F59E0B"),
    ("lion", "狮子", "Lion", "animal", "#F59E0B"),
    ("tiger", "老虎", "Tiger", "animal", "#F97316"),
    ("bear", "熊", "Bear", "animal", "#92400E"),
    ("monkey", "猴子", "Monkey", "animal", "#92400E"),
    ("snake", "蛇", "Snake", "animal", "#10B981"),
    ("turtle", "乌龟", "Turtle", "animal", "#10B981"),
    ("frog", "青蛙", "Frog", "animal", "#10B981"),
    ("dolphin", "海豚", "Dolphin", "animal", "#3B82F6"),
    ("whale", "鲸鱼", "Whale", "animal", "#3B82F6"),
    ("shark", "鲨鱼", "Shark", "animal", "#6B7280"),
    ("crab", "螃蟹", "Crab", "animal", "#EF4444"),
    ("octopus", "章鱼", "Octopus", "animal", "#8B5CF6"),
    ("snail", "蜗牛", "Snail", "animal", "#92400E"),
    # 补充 - 天文地理
    ("mars", "火星", "Mars", "geography", "#EF4444"),
    ("saturn", "土星", "Saturn", "geography", "#F59E0B"),
    ("starSky", "星空", "Star Sky", "geography", "#1F2937"),
    ("constellation", "星座", "Constellation", "geography", "#F59E0B"),
    ("island", "岛屿", "Island", "geography", "#10B981"),
    ("desert", "沙漠", "Desert", "geography", "#F59E0B"),
    ("forest", "森林", "Forest", "geography", "#10B981"),
    ("river", "河流", "River", "geography", "#3B82F6"),
    ("lake", "湖泊", "Lake", "geography", "#3B82F6"),
    ("ocean", "海洋", "Ocean", "geography", "#3B82F6"),
    ("glacier", "冰川", "Glacier", "geography", "#94A3B8"),
    ("cave", "洞穴", "Cave", "geography", "#6B7280"),
    ("map", "地图", "Map", "geography", "#F59E0B"),
    # 补充 - 家具家电
    ("bed", "床", "Bed", "furniture", "#F5F5F4"),
    ("chair", "椅子", "Chair", "furniture", "#92400E"),
    ("fridge", "冰箱", "Fridge", "furniture", "#F5F5F4"),
    ("washingMachine", "洗衣机", "Washing Machine", "furniture", "#F5F5F4"),
    ("airConditioner", "空调", "Air Conditioner", "furniture", "#F5F5F4"),
    ("fan", "风扇", "Fan", "furniture", "#3B82F6"),
    ("wardrobe", "衣柜", "Wardrobe", "furniture", "#92400E"),
    ("bookshelf", "书架", "Bookshelf", "furniture", "#92400E"),
    ("desk", "书桌", "Desk", "furniture", "#92400E"),
    ("mirror", "镜子", "Mirror", "furniture", "#94A3B8"),
    ("curtain", "窗帘", "Curtain", "furniture", "#8B5CF6"),
    # 补充 - 日常用品
    ("laptop", "笔记本电脑", "Laptop", "daily", "#6B7280"),
    ("key", "钥匙", "Key", "daily", "#F59E0B"),
    ("bag", "包", "Bag", "daily", "#92400E"),
    ("glasses", "眼镜", "Glasses", "daily", "#1F2937"),
    ("watch", "手表", "Watch", "daily", "#6B7280"),
    ("wallet", "钱包", "Wallet", "daily", "#92400E"),
    ("toothbrush", "牙刷", "Toothbrush", "daily", "#3B82F6"),
    ("towel", "毛巾", "Towel", "daily", "#F5F5F4"),
    ("soap", "肥皂", "Soap", "daily", "#EC4899"),
    ("scissors", "剪刀", "Scissors", "daily", "#6B7280"),
    # 补充 - 厨房用品
    ("pan", "平底锅", "Pan", "kitchen", "#1F2937"),
    ("knife", "菜刀", "Knife", "kitchen", "#6B7280"),
    ("cuttingBoard", "砧板", "Cutting Board", "kitchen", "#92400E"),
    ("plate", "盘子", "Plate", "kitchen", "#F5F5F4"),
    ("cup", "杯子", "Cup", "kitchen", "#F5F5F4"),
    ("spoon", "勺子", "Spoon", "kitchen", "#6B7280"),
    ("fork", "叉子", "Fork", "kitchen", "#6B7280"),
    ("kettle", "水壶", "Kettle", "kitchen", "#6B7280"),
    ("microwave", "微波炉", "Microwave", "kitchen", "#1F2937"),
    ("oven", "烤箱", "Oven", "kitchen", "#1F2937"),
    ("blender", "搅拌机", "Blender", "kitchen", "#6B7280"),
    ("riceCooker", "电饭煲", "Rice Cooker", "kitchen", "#F5F5F4"),
    # 补充 - 教室用品
    ("desk2", "课桌", "School Desk", "classroom", "#92400E"),
    ("chair2", "课椅", "School Chair", "classroom", "#3B82F6"),
    ("screen", "投影幕", "Screen", "classroom", "#F5F5F4"),
    ("chalk", "粉笔", "Chalk", "classroom", "#F5F5F4"),
    ("marker", "马克笔", "Marker", "classroom", "#EF4444"),
    ("bell", "铃铛", "Bell", "classroom", "#F59E0B"),
    ("flag", "旗帜", "Flag", "classroom", "#EF4444"),
    # 补充 - 数学工具
    ("compass2", "圆规", "Compass", "math", "#6B7280"),
    ("setSquare", "三角尺", "Set Square", "math", "#3B82F6"),
    ("fraction", "分数", "Fraction", "math", "#3B82F6"),
    ("plusMinus", "加减号", "Plus Minus", "math", "#1F2937"),
    ("multiply", "乘号", "Multiply", "math", "#1F2937"),
    ("divide", "除号", "Divide", "math", "#1F2937"),
    ("equals", "等号", "Equals", "math", "#1F2937"),
    ("infinity", "无穷", "Infinity", "math", "#8B5CF6"),
    ("graph", "函数图", "Graph", "math", "#3B82F6"),
    ("coordinate", "坐标系", "Coordinate", "math", "#1F2937"),
    # 补充 - 户外场景
    ("playground", "操场", "Playground", "outdoor", "#F59E0B"),
    ("bench", "长椅", "Bench", "outdoor", "#92400E"),
    ("fountain", "喷泉", "Fountain", "outdoor", "#3B82F6"),
    ("streetLight", "路灯", "Street Light", "outdoor", "#F59E0B"),
    ("bridge", "桥", "Bridge", "outdoor", "#6B7280"),
    ("road", "道路", "Road", "outdoor", "#6B7280"),
    ("trafficLight", "红绿灯", "Traffic Light", "outdoor", "#EF4444"),
    ("signpost", "路标", "Signpost", "outdoor", "#3B82F6"),
    ("mailbox", "邮箱", "Mailbox", "outdoor", "#EF4444"),
    # 补充 - 天气场景
    ("cloudy", "多云", "Cloudy", "weather", "#94A3B8"),
    ("windy", "刮风", "Windy", "weather", "#94A3B8"),
    ("foggy", "雾天", "Foggy", "weather", "#94A3B8"),
    ("thunder", "雷电", "Thunder", "weather", "#F59E0B"),
    ("tornado", "龙卷风", "Tornado", "weather", "#6B7280"),
    ("thermometer2", "温度计", "Thermometer", "weather", "#EF4444"),
    # 补充 - 时间场景
    ("noon", "中午", "Noon", "time", "#F59E0B"),
    ("evening", "傍晚", "Evening", "time", "#F97316"),
    ("hourglass", "沙漏", "Hourglass", "time", "#F59E0B"),
    ("alarm", "闹钟", "Alarm", "time", "#EF4444"),
    ("timer", "计时器", "Timer", "time", "#3B82F6"),
    # 补充 - 情绪表情
    ("surprised", "惊讶", "Surprised", "emotion", "#F59E0B"),
    ("scared", "害怕", "Scared", "emotion", "#8B5CF6"),
    ("confused", "困惑", "Confused", "emotion", "#F59E0B"),
    ("sleepy", "困倦", "Sleepy", "emotion", "#94A3B8"),
    ("cool", "酷", "Cool", "emotion", "#1F2937"),
    ("thinking", "思考", "Thinking", "emotion", "#F59E0B"),
    # 补充 - 社交场景
    ("friends", "朋友", "Friends", "social", "#3B82F6"),
    ("student", "学生", "Student", "social", "#3B82F6"),
    ("police", "警察", "Police", "social", "#3B82F6"),
    ("firefighter", "消防员", "Firefighter", "social", "#EF4444"),
    ("chef", "厨师", "Chef", "social", "#F5F5F4"),
    ("athlete", "运动员", "Athlete", "social", "#F97316"),
    ("scientist", "科学家", "Scientist", "social", "#F5F5F4"),
    # 补充 - 工作场景
    ("printer", "打印机", "Printer", "office", "#6B7280"),
    ("scanner", "扫描仪", "Scanner", "office", "#6B7280"),
    ("document", "文档", "Document", "office", "#F5F5F4"),
    ("stapler", "订书机", "Stapler", "office", "#1F2937"),
    ("paperClip", "回形针", "Paper Clip", "office", "#6B7280"),
    ("tape", "胶带", "Tape", "office", "#F59E0B"),
    ("pen", "钢笔", "Pen", "office", "#1F2937"),
    ("highlighter", "荧光笔", "Highlighter", "office", "#F59E0B"),
    ("postIt", "便利贴", "Post-it", "office", "#F59E0B"),
    ("meeting", "会议", "Meeting", "office", "#3B82F6"),
]

def seed_icons():
    print(f"数据库路径: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 先创建表（如果不存在）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulator_icons (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            name_en TEXT,
            category TEXT NOT NULL,
            description TEXT,
            keywords TEXT,
            default_color TEXT DEFAULT '#3B82F6',
            default_scale REAL DEFAULT 1.0,
            recommended_scenes TEXT,
            is_active INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0,
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)

    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_simulator_icons_category ON simulator_icons(category)")

    created = 0
    skipped = 0

    for icon_id, name, name_en, category, default_color in ICONS_DATA:
        cursor.execute("SELECT id FROM simulator_icons WHERE id = ?", (icon_id,))
        if cursor.fetchone():
            skipped += 1
            continue

        cursor.execute("""
            INSERT INTO simulator_icons (id, name, name_en, category, default_color, default_scale, is_active, sort_order, usage_count)
            VALUES (?, ?, ?, ?, ?, 1.0, 1, 0, 0)
        """, (icon_id, name, name_en, category, default_color))
        created += 1

    conn.commit()
    conn.close()
    print(f"导入完成: 创建 {created} 个, 跳过 {skipped} 个")

if __name__ == "__main__":
    print("开始导入图标数据...")
    seed_icons()
