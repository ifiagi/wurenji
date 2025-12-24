# src/__init__.py

# 1. 从 models 导入核心类
from .models import Drone, Customer, Depot

# 2. 从 utils 导入计算函数
from .utils import (
    calculate_distance, 
    calculate_total_costs, 
    calculate_total_satisfaction,
    normalize_objective
)

# 定义导出的公开接口
__all__ = [
    'Drone',
    'Customer',
    'Depot',
    'calculate_distance',
    'calculate_total_costs',
    'calculate_total_satisfaction',
    'normalize_objective'
]