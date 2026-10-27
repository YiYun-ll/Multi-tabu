"""运行仓库内的小样例，验证路径约束，并按需导出路径图。"""
import argparse
import ast
import json
import math
from pathlib import Path
import platform
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from TS_pro_submission import (calculate_distance_matrix, calculate_cost,
                               generate_best_initial_solution, multitabu)


def parse_input(text):
    groups = [ast.literal_eval(part) for part in text.split('@')]
    if len(groups) < 2 or any(not g for g in groups):
        raise ValueError('需要至少两个非空分组')
    positions, labels, indices = [], [], []
    for group_id, group in enumerate(groups):
        ids = []
        for point in group:
            if len(point) != 2 or any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in point):
                raise ValueError('每个候选点必须是两个有限数值构成的坐标')
            ids.append(len(positions))
            positions.append(tuple(point))
            labels.append(group_id)
        indices.append(ids)
    # 当前初始化逻辑会排除重复坐标；演示仅接受组间互异的候选点。
    if len(set(positions)) != len(positions):
        raise ValueError('本演示要求所有候选点坐标互异')
    return positions, labels, indices


def draw(positions, groups, baseline, solution, before, after, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({'font.sans-serif': ['Microsoft YaHei', 'SimHei', 'DejaVu Sans'],
                         'axes.unicode_minus': False, 'font.size': 11})
    # 分组同时以颜色与 G 编号标识；路径使用深色线与实心节点。
    colors = ['#2563eb', '#b7791f', '#a64794', '#568035', '#db6d28', '#547d99', '#7463a6']
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 6), sharex=True, sharey=True)
    for ax, route, label, cost in zip(axes, [baseline, solution], ['初始化路径', '搜索后路径'], [before, after]):
        for i, ids in enumerate(groups):
            ax.scatter([positions[j][0] for j in ids], [positions[j][1] for j in ids],
                       color=colors[i % len(colors)], alpha=.65, s=35, zorder=3)
            x = sum(positions[j][0] for j in ids) / len(ids)
            y = max(positions[j][1] for j in ids)
            ax.annotate('G' + str(i+1), (x, y), xytext=(0, 10), textcoords='offset points',
                        ha='center', fontsize=10, color='#334155')
        closed = route + [route[0]]
        ax.plot([positions[j][0] for j in closed], [positions[j][1] for j in closed],
                color='#172b4d', linewidth=1.6, zorder=2)
        ax.scatter([positions[j][0] for j in route], [positions[j][1] for j in route],
                   s=95, facecolors='none', edgecolors='#172b4d', linewidths=1.5, zorder=4)
        ax.set_title(f'{label}  |  闭环长度 {cost:.3f}', fontsize=14, pad=15)
        ax.set_xlabel('X 坐标（输入单位）')
        ax.set_aspect('equal', adjustable='box')
        ax.margins(.15)
        ax.grid(alpha=.15)
        ax.spines[['top', 'right']].set_visible(False)
    axes[0].set_ylabel('Y 坐标（输入单位）')
    fig.suptitle('GTSP 示例：每组选择一个点，形成闭合访问路径', fontsize=17, y=.98)
    fig.legend(handles=[Line2D([0],[0],marker='o',linestyle='',color='#64748b',label='候选点（G 表示分组）'),
                        Line2D([0],[0],marker='o',markerfacecolor='none',color='#172b4d',label='选中点与闭合路径')],
               loc='lower center',ncol=2,frameon=False,bbox_to_anchor=(.5,.015))
    fig.tight_layout(rect=[0,.08,1,.94])
    fig.savefig(output, dpi=170, facecolor='white')
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', type=int, default=1, choices=[1, 2], help='inputs_test.json 中的样例编号')
    parser.add_argument('--time-limit', type=float, default=1.0)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--plot', action='store_true', help='需要 matplotlib')
    parser.add_argument('--output-dir', type=Path, default=Path('demo-output'))
    args = parser.parse_args()
    if not math.isfinite(args.time_limit) or args.time_limit <= 0:
        parser.error('--time-limit 必须为有限正数')
    text = json.loads((ROOT/'inputs_test.json').read_text(encoding='utf-8'))[args.case-1]['input']
    positions, labels, groups = parse_input(text)
    matrix = calculate_distance_matrix(positions)
    random.seed(args.seed)
    baseline = generate_best_initial_solution(positions, groups, matrix, labels)
    initial_cost = calculate_cost(matrix, baseline, len(groups))
    random.seed(args.seed)
    started = time.perf_counter()
    solution, _, _, reported = multitabu(positions, labels, groups, args.time_limit)
    elapsed = time.perf_counter() - started
    assert solution is not None, '未返回路径'
    assert len(solution) == len(groups) == len(set(labels[i] for i in solution)), '分组覆盖检查失败'
    assert len(set(positions[i] for i in solution)) == len(groups), '存在重复坐标'
    measured = sum(math.hypot(positions[a][0] - positions[b][0], positions[a][1] - positions[b][1])
                   for a, b in zip(solution, solution[1:] + solution[:1]))
    assert math.isclose(measured, reported, rel_tol=1e-10, abs_tol=1e-8), '长度校验失败'
    assert measured <= initial_cost + 1e-8, '结果劣于本次初始化路径'
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = {'source': 'inputs_test.json', 'case': args.case, 'seed': args.seed,
              'python': platform.python_version(), 'solver': 'TS_pro_submission.multitabu',
              'time_limit_seconds': args.time_limit, 'elapsed_seconds': elapsed,
              'groups': len(groups), 'candidates': len(positions),
              'initial_distance': initial_cost, 'result_distance': measured,
              'improvement_percent': (initial_cost-measured)/initial_cost*100,
              'initial_indices': baseline, 'result_indices': solution,
              'result_coordinates': [positions[i] for i in solution], 'constraints_valid': True}
    (args.output_dir/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Source: inputs_test.json / case {args.case}')
    print(f'Solver: TS_pro_submission.multitabu | Python {platform.python_version()}')
    print(f'Seed: {args.seed} | budget: {args.time_limit:.1f} s | elapsed: {elapsed:.3f} s')
    print(f'Groups: {len(groups)} | candidate points: {len(positions)}')
    print(f'Initial closed-tour distance: {initial_cost:.6f}')
    print(f'Result  closed-tour distance: {measured:.6f}')
    print(f'Improvement over this initialization: {result["improvement_percent"]:.2f}%')
    print('PASS: one point per group; unique coordinates; closed-tour distance verified')
    print(f'Route: {result["result_coordinates"]}')
    if args.plot:
        draw(positions, groups, baseline, solution, initial_cost, measured, args.output_dir/'route-comparison.png')
        print('Saved: route-comparison.png')
    print('Saved: result.json')


if __name__ == '__main__':
    main()
