import numpy as np

def fast_non_dominated_sort(population):
    """
    快速非支配排序：将种群划分为不同的层级 (Rank)
    """
    if not population: return [[]]
    
    for p in population:
        p.domination_count = 0  
        p.dominated_solutions = []  
        p.rank = 0

    fronts = [[]]
    for i, p in enumerate(population):
        for j, q in enumerate(population):
            if i == j: continue
            # 这里的 obj[0] 和 obj[1] 必须都是“越小越好”
            # 注意：在 ALNSMO.evaluate 中我们已经把满意度取了负值
            if (p.obj[0] <= q.obj[0] and p.obj[1] <= q.obj[1]) and \
               (p.obj[0] < q.obj[0] or p.obj[1] < q.obj[1]):
                p.dominated_solutions.append(q)
            elif (q.obj[0] <= p.obj[0] and q.obj[1] <= p.obj[1]) and \
                 (q.obj[0] < p.obj[0] or q.obj[1] < p.obj[1]):
                p.domination_count += 1
        
        if p.domination_count == 0:
            p.rank = 1
            fronts[0].append(p)

    curr_idx = 0
    while len(fronts[curr_idx]) > 0:
        next_front = []
        for p in fronts[curr_idx]:
            for q in p.dominated_solutions:
                q.domination_count -= 1
                if q.domination_count == 0:
                    q.rank = curr_idx + 2
                    next_front.append(q)
        curr_idx += 1
        if not next_front: break
        fronts.append(next_front)
    return [f for f in fronts if f]

def calculate_crowding_distance(front):
    """
    【核心修复】归一化拥挤距离计算
    修复点坍缩的关键：确保不同量级的目标函数对多样性的贡献平等。
    """
    l = len(front)
    if l <= 2:
        for p in front: p.crowding_distance = 1e10 # 赋予极大值
        return

    for p in front: p.crowding_distance = 0

    num_objectives = len(front[0].obj)
    for m in range(num_objectives):
        # 1. 按当前维度目标排序
        front.sort(key=lambda x: x.obj[m])
        
        # 2. 边界点必须保留，赋予极大值
        front[0].crowding_distance = 1e10
        front[-1].crowding_distance = 1e10
        
        # 3. 计算极差进行归一化
        obj_min = front[0].obj[m]
        obj_max = front[-1].obj[m]
        obj_range = obj_max - obj_min
        
        # 如果该维度所有解都一样，跳过，否则会导致除以零
        if obj_range < 1e-6: continue
        
        # 4. 累加归一化后的曼哈顿距离
        for i in range(1, l - 1):
            distance = (front[i+1].obj[m] - front[i-1].obj[m]) / obj_range
            front[i].crowding_distance += distance

def get_pareto_front(population):
    """提取当前的帕累托前沿"""
    return [p for p in population if getattr(p, 'rank', 999) == 1]