import random
import numpy as np
import copy
from ..config import config
from .multi_objective import fast_non_dominated_sort, calculate_crowding_distance
from ..models import Individual
from ..utils import calculate_hv, calculate_total_costs, calculate_total_satisfaction
from ..operators import (
    reorder_task_o1, transfer_task_o2, migrate_task_o3,
    reduce_drones_o4, time_window_greedy_o5, optimize_position_o6
)

class ALNSMO:
    def __init__(self, customers, depots):
        self.customers = customers
        self.depots = depots if isinstance(depots, list) else [depots]
        self.operators = [
            reorder_task_o1, transfer_task_o2, migrate_task_o3,
            reduce_drones_o4, time_window_greedy_o5, optimize_position_o6
        ]
        self.weights = np.ones(len(self.operators))
        self.scores = np.zeros(len(self.operators))
        self.usage_count = np.zeros(len(self.operators))
        self.archive = []

    def initialize_population(self):
        population = []
        for _ in range(config.POP_SIZE):
            shuffled_tasks = copy.copy(self.customers)
            random.shuffle(shuffled_tasks)
            num_drones = len(self.depots) * 2 
            routes = [[] for _ in range(num_drones)]
            for idx, task in enumerate(shuffled_tasks):
                routes[idx % num_drones].append(task)
            ind = Individual(routes)
            self.evaluate(ind)
            population.append(ind)
        return population

    def evaluate(self, ind):
        """
        【关键修复 1】目标函数缩放
        f1 (成本) 通常在 100-500 之间，f2 (满意度) 在 0-1 之间。
        必须将 f1 除以一个缩放因子（如 100），使其量级与 f2 匹配。
        """
        raw_cost = calculate_total_costs(ind.routes)
        ind.obj[0] = raw_cost / 100.0  # 缩放到 1-5 左右
        ind.obj[1] = -calculate_total_satisfaction(ind.routes) # 范围约 -1 到 0

    def update_archive(self, population):
        combined = self.archive + population
        fronts = fast_non_dominated_sort(combined)
        if fronts:
            new_archive = []
            seen_objs = set()
            for ind in fronts[0]:
                # 稍微降低去重的精度，有助于在图上形成连贯的曲线
                obj_tuple = (round(ind.obj[0], 2), round(ind.obj[1], 2))
                if obj_tuple not in seen_objs:
                    new_archive.append(ind)
                    seen_objs.add(obj_tuple)
            # 增加档案容量，确保有足够的点画出曲线
            self.archive = new_archive[:500]

    def select_operator(self):
        prob = self.weights / sum(self.weights)
        return np.random.choice(len(self.operators), p=prob)

    def solve(self):
        population = self.initialize_population()
        self.archive = [] 
        hv_trajectory = []

        for i in range(config.ITER_MAX):
            offspring = []
            for ind in population:
                op_idx = self.select_operator()
                self.usage_count[op_idx] += 1
                
                new_routes = copy.deepcopy(ind.routes)
                d_idx = random.randrange(len(new_routes))
                
                if op_idx in [1, 2, 3] and len(new_routes) > 1:
                    idx_j = random.choice([j for j in range(len(new_routes)) if j != d_idx])
                    new_routes[d_idx], new_routes[idx_j] = self.operators[op_idx](new_routes[d_idx], new_routes[idx_j])
                else:
                    new_routes[d_idx] = self.operators[op_idx](new_routes[d_idx])
                
                new_ind = Individual(new_routes)
                self.evaluate(new_ind)
                
                # 【关键修复 2】多目标接受准则
                # 不能只比较 obj[0]。如果新解在任一维度变好，或者满足概率阈值，就接受。
                # 这样可以强迫算法去探索“成本虽高但满意度更好”的区域。
                if new_ind.obj[0] < ind.obj[0] or new_ind.obj[1] < ind.obj[1] or random.random() < 0.2:
                    offspring.append(new_ind)
                    self.scores[op_idx] += config.THETA1
                else:
                    offspring.append(ind)
            
            population = self.elitism_selection(population + offspring)
            self.update_archive(population)
            
            # 使用档案计算 HV
            hv_trajectory.append(calculate_hv(self.archive))
            
            if i % 10 == 0:
                self.update_weights()
                
        return self.archive, hv_trajectory

    def update_weights(self):
        for j in range(len(self.operators)):
            if self.usage_count[j] > 0:
                self.weights[j] = (1 - config.EPSILON) * self.weights[j] + \
                                  config.EPSILON * (self.scores[j] / self.usage_count[j])
        self.scores.fill(0)
        self.usage_count.fill(0)

    def elitism_selection(self, combined_pop):
        new_pop = []
        fronts = fast_non_dominated_sort(combined_pop)
        for front in fronts:
            if not front: continue
            calculate_crowding_distance(front)
            # 排序：拥挤度降序（让稀疏区域的点优先保留）
            front.sort(key=lambda x: x.crowding_distance, reverse=True)
        
            if len(new_pop) + len(front) <= config.POP_SIZE:
                new_pop.extend(front)
            else:
                needed = config.POP_SIZE - len(new_pop)
                new_pop.extend(front[:needed])
                break
        return new_pop