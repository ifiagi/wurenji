import random
import numpy as np
from .models import Customer, Depot
from .config import config

class DataLoader:
    def __init__(self):
        self.config = config

    def load_instance(self, instance_name):
        """加载 Homberger 算例并按 6:3:1 比例生成异构任务 [cite: 581-582]"""
        # 复现逻辑：模拟读取文本数据并缩放坐标
        customers = []
        # 假设读取了 n 个点
        n = int(instance_name.split('n')[1].split('m')[0])
        for i in range(1, n + 1):
            # 缩放坐标与时间窗 [cite: 581]
            x, y = random.uniform(0, 20), random.uniform(0, 20)
            w_a, w_b = random.uniform(0, 10), random.uniform(10, 20)
            
            # 按照比例分配任务类型 
            rand = random.random()
            if rand < self.config.PROB_DELIVERY:
                d_type = self.config.D_TYPE_CODE
            elif rand < self.config.PROB_DELIVERY + self.config.PROB_PICKUP:
                d_type = self.config.P_TYPE_CODE
            else:
                d_type = self.config.PD_TYPE_CODE
            
            # 计算柔性时间窗容忍边界 [cite: 583]
            w_e = w_a - self.config.ETA * (w_b - w_a)
            w_l = w_b + self.config.ETA * (w_b - w_a)
            
            customers.append(Customer(i, x, y, d_type, random.uniform(0, 3), w_a, w_b, w_e, w_l))
        
        depot = Depot(0, 10, 10) # 中心配送站
        return customers, depot

    def load_real_world_data(self, nodes=40):
        """模拟长沙市 40 个任务点的数据 [cite: 737-739, 1107-1108]"""
        customers = []
        # 长沙实景：8:00 am - 11:00 am (换算为 0-3h) [cite: 739]
        for i in range(nodes):
            x, y = random.uniform(112.90, 113.02), random.uniform(28.14, 28.22)
            w_a = random.uniform(0, 2.5) # 8:00 开始
            w_b = w_a + random.uniform(0.33, 0.67) # 20-40分钟宽度 [cite: 739]
            
            w_e = w_a - self.config.ETA * (w_b - w_a)
            w_l = w_b + self.config.ETA * (w_b - w_a)
            
            customers.append(Customer(i, x, y, 'D', random.uniform(0, 3), w_a, w_b, w_e, w_l))
        
        depots = [Depot(0, 112.94, 28.17), Depot(1, 112.98, 28.17)] # 2个配送中心 [cite: 740]
        return customers, depots