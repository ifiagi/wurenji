import sys
import os
import argparse

# 确保项目根目录在系统路径中，以便正确导入 src 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import DataLoader
from src.solver.alnsmo import ALNSMO
from experiments.benchmark_run import run_benchmarks
from experiments.real_world_run import run_real_world

def main():
    parser = argparse.ArgumentParser(description="MDRP-DPOD 多无人机协作路径规划复现工程")
    parser.add_argument('--mode', type=str, default='real', choices=['benchmark', 'real', 'single'],
                        help='运行模式: benchmark(基准测试), real(长沙实景), single(单次运行演示)')
    
    args = parser.parse_args()

    print("="*50)
    print("具有异构取送服务的多目标多无人机协作路径规划复现")
    print("论文来源: Hong 等, IEEE T-ITS 2025")
    print("="*50)

    if args.mode == 'benchmark':
        print("\n[状态] 启动 29 个基准实例测试 (对应论文 Table IV)...")
        run_benchmarks()

    elif args.mode == 'real':
        print("\n[状态] 启动长沙市 40 任务点实景模拟 (对应论文 Fig. 7)...")
        run_real_world()

    elif args.mode == 'single':
        print("\n[状态] 执行单次演示运行 (n20m2d2 实例)...")
        loader = DataLoader()
        # 加载基础数据 [cite: 581-583]
        customers, depot = loader.load_instance("n20m2d2")
        solver = ALNSMO(customers, depot)
        # 运行 ALNSMO 算法 [cite: 333, 404]
        pareto_front = solver.solve()
        
        print(f"演示运行完成！找到 {len(pareto_front)} 个帕累托最优解。")
        for i, sol in enumerate(pareto_front[:3]): # 展示前3个解
            print(f"方案 {i+1}: 成本 f1={sol.obj[0]:.2f}, 满意度 f2={sol.obj[1]:.2f}")

    print("\n" + "="*50)
    print("实验已结束，结果存放在 experiments/results/ 目录下。")

if __name__ == "__main__":
    main()