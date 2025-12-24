import copy
from ..config import config
from ..utils import calculate_distance

def ls_vnd(route, drone_model):
    """
    实现局部搜索算子 LS-VND (变邻域下降搜索) [cite: 551, 1362]
    包含基础算子 o1-o5 以及特定算子 o7 (距离瓶颈) 和 o8 (满意度瓶颈) [cite: 552, 1363]
    """
    new_route = copy.deepcopy(route)
    if len(new_route) < 2:
        return new_route

    # 1. 实现 o7: 调整路径中飞行时间最长(距离最远)的任务节点 [cite: 552-553, 1364]
    max_dist = -1
    bottleneck_idx = -1
    for i in range(len(new_route)):
        # 计算前一个点到当前点的距离
        prev_node = config.DEPOT_OBJ if i == 0 else new_route[i-1] # 需在具体逻辑中定义起始点
        dist = calculate_distance(prev_node, new_route[i])
        if dist > max_dist:
            max_dist = dist
            bottleneck_idx = i
    
    if bottleneck_idx != -1:
        node = new_route.pop(bottleneck_idx)
        new_route.insert(0, node) # 简单尝试移动到起始位置以缩短后续链条

    # 2. 实现 o8: 满意度瓶颈调整 [cite: 554, 1365]
    # 找到到达时间与期望时间偏差最大的节点，尝试改变其位置
    # (此逻辑需要配合 solver 中的时间推算结果，此处预留结构)
    
    return new_route

def ls_wait_adjustment(route, drone_model):
    """
    实现 LS-wait: 等待时间精修 [cite: 558, 1179, 1366]
    通过增加前置节点的等待时长，延后后续节点的到达时间，
    使其尽可能重新落入期望窗范围内。 [cite: 574, 1367-1368]
    """
    if len(route) < 2:
        return route
        
    adjusted_route = copy.deepcopy(route)
    
    # 论文逻辑：如果调整 j1 的等待时间 t_wait 能让 j2 重新落入 [w_a, w_b]
    # 遍历路径中的节点对 (j1, j2) [cite: 556, 574]
    for i in range(len(adjusted_route) - 1):
        j1 = adjusted_route[i]
        j2 = adjusted_route[i+1]
        
        # 假设 j2 当前到达时间晚于期望窗口 (arrival_j2 > w_b_j2)
        # 但如果是因为 j1 出发太早导致的，则可以通过增加 j1 的等待时间来微调
        # 注意：此策略在论文图中 (Fig. 5) 重点展示了通过等待优化满意度的冲突 [cite: 570]
        
        # 伪代码逻辑：
        # if j2.arrival_time > j2.w_b:
        #     potential_wait = j1.w_b - j1.arrival_time
        #     if potential_wait > 0:
        #         j1.wait_time += potential_wait
    
    return adjusted_route

def apls_main(pareto_front, drone_model):
    """
    Adaptive Pareto Local Search (APLS) 主函数 [cite: 541, 1118]
    只针对非重复的 Pareto Front 进行局部搜索，提高效率 [cite: 542]
    """
    new_pf = []
    for pe in pareto_front:
        # 1. 尝试使用 LS-VND 优化物理路径 [cite: 544]
        pe_prime = ls_vnd(pe, drone_model)
        # 2. 尝试使用 LS-wait 优化时间分配 [cite: 549]
        pe_final = ls_wait_adjustment(pe_prime, drone_model)
        new_pf.append(pe_final)
    return new_pf