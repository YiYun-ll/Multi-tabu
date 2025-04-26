import random
import math
import json
from tqdm import tqdm

def get_loop_by_solution(solution, positions):
    #根据当前解返回起点集合
    set = []  
    for idx in solution:
        set.append(positions[idx])  # 将每个索引对应的坐标加入集合
    return set

def tabu(loop_positions, layer_class, loop_class):
    # 实现禁忌搜索算法寻找最优封闭环路径
    loop_count = len(loop_positions)          # 封闭环的总数
    layer_count = len(set(layer_class))       # 切片层的数量
    distance_matrix = calculate_distance_matrix(loop_positions)  # 计算距离矩阵

    max_iterations = 1500     # 最大迭代次数
    tabu_list = []            # 禁忌表
    tabu_time = []            # 禁忌时间表
    tabu_duration = 50        # 禁忌期限

    # 初始化解
    current_solution = generate_initial_solution(loop_positions, loop_class)  # 生成初始解
    current_value = [calculate_cost(distance_matrix, current_solution, layer_count)]  # 计算解的成本

    best_solution = current_solution.copy()  # 初始化最优解
    best_value = current_value[-1]  # 初始化最优值
    best_values = [best_value]  # 存储迭代中的最优值

    # 开始迭代
    for iteration in range(max_iterations):
        # 生成候选解集
        candidate_solutions, candidate_values = generate_candidates(
            current_solution, loop_positions, layer_class, loop_class, distance_matrix, layer_count)
        
        # 找到候选解中的最优解
        candidate_best_value, best_index = min((val, idx) for (idx, val) in enumerate(candidate_values))
        
        current_value.append(candidate_best_value)  
        current_solution = candidate_solutions[best_index].copy()  
        
        # 更新最优解
        if current_value[-1] < best_value:
            best_value = current_value[-1]  
            best_solution = current_solution.copy()  
        best_values.append(best_value)  
        
        # 更新禁忌表
        update_tabu_list(tabu_list, tabu_time, candidate_solutions[best_index], tabu_duration)

    return best_solution, loop_positions, loop_class, best_value

def generate_initial_solution(loop_positions, loop_class):
    # 生成随机初始解
    current_solution = []  
    positions = []  
    for layer_loops in loop_class:
        while True:
            choice = random.choice(layer_loops)  
            this_position = loop_positions[choice]
            if this_position not in positions:  # 如果位置未被选择
                positions.append(this_position)  # 将位置加入已选择集合
                current_solution.append(choice)  # 将选择加入解
                break
    random.shuffle(current_solution)  
    return current_solution

def generate_candidates(current_solution, loop_positions, layer_class, loop_class, distance_matrix, layer_count):
    # 生成候选解集
    candidate_solutions = []  
    candidate_values = []  
    positions = get_loop_by_solution(current_solution, loop_positions)  # 获取解对应位置
    candidate_count = len(current_solution)  # 候选解数量为当前解数量
    
    for _ in range(candidate_count):
        new_solution = current_solution.copy()  # 复制当前解
        if random.random() > 0.5:
            swap_within_layer(new_solution, positions, loop_positions, loop_class, layer_class)  # 在同层内交换
        else:
            random_swap(new_solution, layer_count)  

        if new_solution not in candidate_solutions:  # 如果新解不在候选集中
            candidate_solutions.append(new_solution)  
            candidate_values.append(calculate_cost(distance_matrix, new_solution, layer_count))  # 计算并记录新解的值

    return candidate_solutions, candidate_values

def swap_within_layer(solution, positions, loop_positions, loop_class, layer_class):
    # 在同一切片层中交换两个封闭环的起点
    layer = random.randrange(len(loop_class))  
    alternatives = [loop for loop in loop_class[layer] if loop_positions[loop] not in positions] 
    if not alternatives:
        return

    loc = solution.index(random.choice([loop for loop in loop_class[layer] if loop in solution]))
    solution[loc] = random.choice(alternatives)

def random_swap(solution, layer_count):
    # 随机交换两个封闭环起点
    swap_indices = random.sample(range(layer_count), 2)  
    solution[swap_indices[0]], solution[swap_indices[1]] = solution[swap_indices[1]], solution[swap_indices[0]]

def update_tabu_list(tabu_list, tabu_time, best_candidate, tabu_duration):
    # 更新禁忌表及期限
    tabu_list.append(best_candidate)  
    tabu_time.append(tabu_duration)

    # 更新禁忌时间，并移除过期项
    tabu_time[:] = [x-1 for x in tabu_time]  
    while 0 in tabu_time:  
        index = tabu_time.index(0)  
        tabu_list.pop(index)
        tabu_time.pop(index)

def calculate_distance_matrix(loop_positions):
    # 计算封闭环之间的距离矩阵
    count = len(loop_positions)
    distance_matrix = [[0] * count for _ in range(count)]
    for i in range(count):
        for j in range(i, count):
            dist = math.sqrt(
                (loop_positions[i][0] - loop_positions[j][0]) ** 2 +
                (loop_positions[i][1] - loop_positions[j][1]) ** 2
            )  # 计算两点之间的距离
            distance_matrix[i][j] = distance_matrix[j][i] = dist  # 填入对称的距离矩阵
    return distance_matrix

def calculate_cost(distance_matrix, solution, layer_count):
    # 计算路径的总长度，包括首尾连接
    total_cost = sum(
        distance_matrix[solution[j]][solution[j + 1]] for j in range(layer_count - 1)
    ) + distance_matrix[solution[0]][solution[layer_count - 1]]
    return total_cost

def convert_input_data(input_data):
    # 将输入数据转换为封闭环坐标、切片层分类和封闭环分类
    loop_positions, layer_class, loop_class = [], [], []
    polygons = [eval(x) for x in input_data.split("@")]  
    for i, polygon in enumerate(polygons):
        loop_count = len(loop_positions) 
        loop_positions += polygon  
        layer_class += [i] * len(polygon)  # 记录每个封闭环的层信息
        loop_class.append([i + loop_count for i in range(len(polygon))])  # 记录每个层的封闭环索引
    return loop_positions, layer_class, loop_class

if __name__ == '__main__':
    time_limit = 5
    iteration = 0
    test_file = 'overlap_inputs.json'
    points = 0
    with open(test_file, 'r') as file:
        test_cases = json.load(file)
    idx = 0
    total_dist = 0
    for dic in tqdm(test_cases[:10]):
        idx += 1
        input_data = dic['input']
        loop_positions, layer_class, loop_class = convert_input_data(input_data)
        best_global_solution, loop_positions, loop_class, best_global_value = tabu(loop_positions, layer_class, loop_class)
        result = [loop_positions[i] for i in best_global_solution] + [loop_positions[best_global_solution[0]]]
        x_result = [x[0] for x in result]
        y_result = [y[1] for y in result]
        prediction = result[:-1]
        assert len(prediction) == len(set(prediction))
        prediction = str(prediction).replace(' ', '')
        distance = best_global_value
        print(prediction, distance)
        total_dist += distance
    print(f"测试完成，总距离为{total_dist}")