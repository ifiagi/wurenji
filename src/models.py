import numpy as np

class Drone:
    """无人机物理属性 [cite: 590]"""
    def __init__(self):
        self.self_weight = 6.0          # 自重 W0 (kg) [cite: 590]
        self.battery_capacity = 504.0   # 电池容量 E (Wh) [cite: 590]
        self.output_power = 1008.0      # 输出功率 P (W) [cite: 590]
        self.energy_coeff = 3.5         # 能耗系数 alpha (Wh/(km*kg)) [cite: 590]
        self.service_time = 0.05        # 每个客户点的服务时间 t0 (h) [cite: 590]
        self.max_payload = 3.0          # 最大载重量 (kg) [cite: 582]

    def get_travel_time(self, distance, current_payload):
        """
        实现论文公式 (25): 计算受载荷影响的飞行时间 [cite: 268, 1300]
        t = (d * (W0 + W_payload) * alpha) / P
        """
        # 注意：这里计算出的时间单位是小时 (h)
        travel_time = (distance * (self.self_weight + current_payload) * self.energy_coeff) / self.output_power
        return travel_time

class Customer:
    """客户节点定义，包含异构任务属性与时间窗 [cite: 211, 580]"""
    def __init__(self, id, x, y, demand_type, weight, w_a, w_b, w_e, w_l):
        self.id = id
        self.x = x
        self.y = y
        self.demand_type = demand_type  # 'D' (送货), 'P' (取货), 'PD' (市内即时) [cite: 182, 1268]
        self.weight = weight            # 包裹重量 [cite: 582]
        # 时间窗定义 [cite: 211, 583, 1276]
        self.w_a = w_a  # 期望开始时间
        self.w_b = w_b  # 期望结束时间
        self.w_e = w_e  # 容忍最早时间
        self.w_l = w_l  # 容忍最晚时间

    def calculate_satisfaction(self, arrival_time):
        """
        实现论文公式 (2): 软时间窗满意度计算 [cite: 256, 1297]
        """
        if self.w_a <= arrival_time <= self.w_b:
            return 1.0  # 在期望时间内到达，满意度为1 [cite: 237, 1297]
        elif self.w_e <= arrival_time < self.w_a:
            # 早于期望但晚于容忍限值，满意度线性下降 [cite: 237, 1297]
            return (arrival_time - self.w_e) / (self.w_a - self.w_e)
        elif self.w_b < arrival_time <= self.w_l:
            # 迟于期望但早于容忍限值，满意度线性下降 [cite: 237, 1297]
            return (self.w_l - arrival_time) / (self.w_l - self.w_b)
        else:
            return 0.0  # 超出容忍范围，满意度为0 [cite: 238, 1297]

class Depot:
    """配送站/仓库定义 [cite: 177, 1272]"""
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

# src/models.py 文件的末尾添加

class Individual:
    """对应论文中的染色体/解个体 """
    def __init__(self, routes):
        self.routes = routes  # 二维列表：[[node1, node2], [node3]]
        self.obj = [0.0, 0.0] # [f1, f2]
        self.rank = 0
        self.crowding_distance = 0
        self.domination_count = 0
        self.dominated_solutions = []