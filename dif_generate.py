import random
import math
import json
import os
from tqdm import tqdm

def generate_non_overlapping_loops(num_loops, min_points, max_points, x_range, y_range, buffer_dist=10):
    """生成不重叠的封闭环"""
    loops = []
    while len(loops) < num_loops:
        num_points = random.randint(min_points, max_points)
        center_x = random.randint(x_range[0], x_range[1])
        center_y = random.randint(y_range[0], y_range[1])
        points = set()
        
        # 创建一个封闭环，确保点之间的间隔合理
        while len(points) < num_points:
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(5, 10)
            x = int(center_x + radius * math.cos(angle))
            y = int(center_y + radius * math.sin(angle))
            if x_range[0] <= x <= x_range[1] and y_range[0] <= y <= y_range[1]:
                points.add((x, y))
        
        # 确保新生成的封闭环不与现有的封闭环重叠
        new_loop = list(points)
        overlap = False
        for loop in loops:
            for point in new_loop:
                for existing_point in loop:
                    if distance(point, existing_point) < buffer_dist:
                        overlap = True
                        break
                if overlap:
                    break
            if overlap:
                break
        
        if not overlap:
            loops.append(new_loop)
    
    return loops

def format_input_data(loops):
    """将封闭环数据格式化为 [(...)]@[(...)]@[(...)] 形式"""
    formatted_data = []
    for loop in loops:
        formatted_data.append(f"[{','.join(str(point) for point in loop)}]")
    return "@".join(formatted_data)

def distance(point1, point2):
    """计算两点之间的欧几里得距离"""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def save_inputs_to_file(file_name, formatted_input):
    """保存输入样例到文件"""
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            save_file = json.load(file)
    else:
        save_file = []
    dic = {'input': formatted_input}
    save_file.append(dic)
    with open(file_name, 'w') as file:
        json.dump(save_file, file)

if __name__ == '__main__':
    # 随机生成不重叠的测试样例
    number = 1  # 生成的样例数量
    for i in tqdm(range(1, number + 1)):
        num_loops = 7  # 环的数量
        min_points_per_loop = random.randint(3, 4)  # 每个环的最小点数
        max_points_per_loop = min_points_per_loop + random.randint(1, 2)  # 每个环的最大点数
        x_range = (0, 120)  # 坐标范围加大
        y_range = (0, 120)

        random_test_case = generate_non_overlapping_loops(num_loops, min_points_per_loop, max_points_per_loop, x_range, y_range)

        # 格式化输入数据
        formatted_input = format_input_data(random_test_case)

        # 保存输入样例到文件
        save_inputs_to_file("inputs_tset.json", formatted_input)

        # 输出结果
        print(f"Case {i} 输入数据:")
        print(formatted_input)
