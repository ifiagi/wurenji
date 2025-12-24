# src/config.py

class GlobalConfig:
    """
    统一管理论文中的所有超参数 [cite: 148, 590, 963]
    """
    
    # 1. 算法通用参数
    ITER_MAX = 1000          # 最大迭代次数 
    POP_SIZE = 100           # 种群规模 
    R_MAX = 5               # 历史Pareto前沿记录的最大数量 
    
    # 2. ALNS 算子得分与权重更新参数 [cite: 405, 963]
    EPSILON = 0.4           # 权重调整系数 (e) 
    THETA1 = 0.8            # 算子奖励得分1 (theta1) 
    THETA2 = 0.4            # 算子奖励得分2 (theta2) 
    
    # 3. 目标函数权重系数 [cite: 233, 1294]
    SIGMA = 0.5             # 飞行距离权重
    RHO = 0.5               # 活跃无人机数量权重
    
    # 4. 无人机物理参数 (Table III) [cite: 590, 1300]
    DRONE_SELF_WEIGHT = 6.0       # kg
    BATTERY_CAPACITY = 504.0      # Wh
    OUTPUT_POWER = 1008.0         # W
    SERVICE_TIME = 0.05           # h
    ENERGY_COEFF_ALPHA = 3.5      # Wh/(km*kg)
    
    # 5. 任务分配比例参数 [cite: 582, 1268-1271]
    PROB_DELIVERY = 0.6           # 配送任务占比 (60%)
    PROB_PICKUP = 0.3             # 取件任务占比 (30%)
    PROB_INTRA_CITY = 0.1         # 同城即时配送任务占比 (10%)
    
    # 6. 时间窗参数 [cite: 583, 1277]
    ETA = 0.2                     # 柔性时间窗系数，用于计算 w_e 和 w_l
    
    # 7. 路径规则
    PD_TYPE_CODE = 'PD'           # 市内即时配送代码
    D_TYPE_CODE = 'D'             # 仅送货代码
    P_TYPE_CODE = 'P'             # 仅取件代码

# 实例化，方便其他模块直接 import
config = GlobalConfig()