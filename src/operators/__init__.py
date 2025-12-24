# src/operators/__init__.py

# 导入全局搜索算子 (ALNS 核心算子 o1-o6)
from .destroy_repair import (
    reorder_task_o1,
    transfer_task_o2,
    migrate_task_o3,
    reduce_drones_o4,
    time_window_greedy_o5,
    optimize_position_o6
)

# 导入局部搜索算子 (APLS 核心策略)
from .local_search import (
    ls_vnd,
    ls_wait_adjustment
)

# 定义导出列表，方便 solver 模块调用
__all__ = [
    # ALNS 算子 [cite: 512, 1332]
    'reorder_task_o1',
    'transfer_task_o2',
    'migrate_task_o3',
    'reduce_drones_o4',
    'time_window_greedy_o5',
    'optimize_position_o6',
    
    # 局部搜索策略 [cite: 541, 1360]
    'ls_vnd',
    'ls_wait_adjustment'
]