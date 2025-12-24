import numpy as np
from .models import Customer, Depot 

def calculate_distance(node1, node2):
    """计算两点之间的欧几里得距离"""
    return np.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

def calculate_total_costs(solution, sigma=0.5, rho=0.5):
    """计算目标函数 f1: 运输成本"""
    total_distance = 0
    active_drones = 0
    for drone_route in solution:
        if len(drone_route) > 0:
            active_drones += 1
            # 路径：仓库 -> 客户1 -> ... -> 客户n -> 仓库 (需闭环计算距离)
            # 假设 solution 里的 drone_route 仅包含 Customer 对象
            # 实际计算需包含仓库到首尾客户的距离
            # 这里简化处理，仅计算客户间的连接
            for i in range(len(drone_route) - 1):
                total_distance += calculate_distance(drone_route[i], drone_route[i+1])
    return sigma * total_distance + rho * active_drones

def calculate_total_satisfaction(solution):
    """计算目标函数 f2: 总客户满意度"""
    total_s = 0
    for drone_route in solution:
        for node in drone_route:
            if isinstance(node, Customer):
                # 假设节点已带有经过算子更新后的 arrival_time
                total_s += node.calculate_satisfaction(getattr(node, 'arrival_time', 0))
    return total_s

def normalize_objective(value, min_val, max_val):
    """实现公式 (38): 目标值标准化 """
    if max_val == min_val: return 0.0
    return (value - min_val) / (max_val - min_val)

def calculate_hv(pareto_front, ref_point=[1.1, 1.1]):
    """
    实现非占位符的真实超体积 (Hypervolume) 计算
    1. 提取 f1, f2 
    2. 归一化并转化为最小化问题
    3. 计算方案集与参考点之间的矩形并集面积
    """
    if not pareto_front:
        return 0.0
    
    # 提取目标值
    costs = [sol.obj[0] for sol in pareto_front]
    # 注意：solver 里存的是 -satisfaction，这里转回正数
    satisfactions = [abs(sol.obj[1]) for sol in pareto_front] 

    # 1. 归一化 (使用论文算例的估计边界：成本500, 40个点最大满意度40)
    # 使两个目标都变成越小越好，且范围在 [0, 1]
    norm_f1 = [c / 500.0 for c in costs]
    norm_f2 = [1.0 - (s / 40.0) for s in satisfactions]
    
    # 2. 排序并过滤掉超过参考点的解
    points = sorted(list(set(zip(norm_f1, norm_f2))))
    
    # 3. 阶梯求和法计算面积
    hv = 0.0
    last_f1 = ref_point[0]
    
    # 按 f1 从大到小遍历
    for f1, f2 in reversed(points):
        if f1 < ref_point[0] and f2 < ref_point[1]:
            # 计算当前矩形块的面积：宽度(delta f1) * 高度(ref_f2 - f2)
            hv += (last_f1 - f1) * (ref_point[1] - f2)
            last_f1 = f1
            
    return round(hv, 4)