import random
import copy
from ..config import config

def reorder_task_o1(route):
    """o1: 单架无人机任务重排 - 随机交换两个任务点"""
    if len(route) < 2: return route
    new_route = copy.copy(route)
    idx1, idx2 = random.sample(range(len(new_route)), 2)
    new_route[idx1], new_route[idx2] = new_route[idx2], new_route[idx1]
    return new_route

def transfer_task_o2(route_i, route_j):
    """o2: 同站任务转移 - 从 i 移一个任务到 j"""
    if len(route_i) == 0: return route_i, route_j
    new_i, new_j = copy.copy(route_i), copy.copy(route_j)
    
    # 随机取出一个任务
    task = new_i.pop(random.randrange(len(new_i)))
    # 随机插入到另一条路径
    new_j.insert(random.randrange(len(new_j) + 1), task)
    return new_i, new_j

def migrate_task_o3(route_i, route_j):
    """o3: 跨站任务迁移 - 逻辑同 o2，但在 solver 中会跨 Depot 选择路径"""
    return transfer_task_o2(route_i, route_j)

def reduce_drones_o4(route_i, route_j):
    """o4: 减少活跃飞机数 - 将 i 的所有任务并入 j，清空 i"""
    new_j = route_j + route_i
    new_i = []
    return new_i, new_j

def time_window_greedy_o5(route):
    """o5: 基于时间窗重排 - 按期望截止时间 w_b 排序以提升满意度 f2"""
    if len(route) < 2: return route
    # 排序可能会破坏 PD 任务的先后顺序，实际复现中需谨慎
    return sorted(route, key=lambda x: x.w_b)

def optimize_position_o6(route):
    """o6: 任务位置优化 - 针对 PD 或 P 任务寻找更近的插入点"""
    if len(route) < 2: return route
    new_route = copy.copy(route)
    idx = random.randrange(len(new_route))
    task = new_route.pop(idx)
    
    # 寻找一个随机新位置插入 (实际论文中会根据距离矩阵插入)
    new_route.insert(random.randrange(len(new_route) + 1), task)
    return new_route