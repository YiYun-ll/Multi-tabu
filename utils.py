import math
import matplotlib.pyplot as plt

colors=['black', 'blue', 'green', 'red', 'yellow', 'orange','purple', 'darkblue','lightblue','gold', 'lime', 'maroon',
            'olive', 'silver', 'orchid', 'salmon', 'tomato', 'yellowgreen', 'rosybrown', 'plum', 'peru', 'tan', 'sienna', 'saddlebrown',
            'palevioletred']

def record_distance(city_position):
    num = len(city_position)  # 城市数量
    distance = [[0] * num for _ in range(num)]  # 初始化二维列表
    for i in range(num):
        for j in range(i, num):
            dist = math.sqrt(
                (city_position[i][0] - city_position[j][0]) ** 2 +
                (city_position[i][1] - city_position[j][1]) ** 2
            )
            distance[i][j] = distance[j][i] = dist  # 对称赋值
    return distance

def cal_cost(distance, solution, goods_num):
    cost = 0
    for j in range(goods_num-1):
        cost += distance[solution[j]][solution[j+1]]
    cost += distance[solution[0]][solution[goods_num - 1]]
    return cost

##### 获取绘图散点信息 #####
def get_plot_points(city_class, city_position):
    x = [] # 横坐标
    y = [] # 纵坐标
    c = [] # 颜色
    for index, item in enumerate(city_class): # 根据商品种类划分点
        x.append([city_position[i][0] for i in item])
        y.append([city_position[i][1] for i in item])
        c.append(colors[index])
    return x,y,c

##### 绘图 #####
def show_result(best_solution, city_position, city_class, save_path, vis=True):
    # 所有点 - 根据商品种类划分颜色
    # x = [x[0] for x in city_position]
    # y = [y[1] for y in city_position]
    x,y,c = get_plot_points(city_class, city_position)

    # 结果上的点
    result = []
    for i in best_solution:
        result.append(city_position[i])
    result.append(city_position[best_solution[0]])
    x_result = [x[0] for x in result]
    y_result = [y[1] for y in result]
    output_result = result[:-1]
    print(str(output_result).replace(' ',''))
    if vis:
        for index, x_item in enumerate(x):
            plt.scatter(x_item, y[index], label='Location', color = c[index]) # 散点 edgecolors = 'coral'
        plt.plot(x_result, y_result, label = 'result', color = 'black', alpha = 0.2, marker = '*', markersize=10) # 路径
        plt.ylabel("y")
        plt.xlabel("x")
        plt.title("best result")
        # plt.legend()
        # plt.show()
        plt.savefig(save_path)
        plt.close()
    return output_result
    
def convert_input_data(input_data):
    city_position = []
    goods_class = []
    city_class = []
    polygons = input_data.split("@")
    polygons = [eval(x) for x in polygons]
    for (i, polygon) in enumerate(polygons):
        city_count = len(city_position)
        city_position = city_position + polygon
        goods_class = goods_class + [i] * len(polygon)
        city_class.append([i+city_count for i in range(len(polygon))])           
    return city_position, goods_class, city_class

def is_same_cycle(predicted_path, expected_path):
    """
    判断两个路径是否为首尾相接的等价循环路径，包括正序和反序，且忽略起点
    """
    if len(predicted_path) != len(expected_path):
        return False

    # 将路径标准化为元组的列表
    predicted_path = list(map(tuple, predicted_path))
    expected_path = list(map(tuple, expected_path))

    # 正序循环判断
    for i in range(len(expected_path)):
        rotated_path = expected_path[i:] + expected_path[:i]
        if predicted_path == rotated_path:
            return True

    # 反序循环判断
    reversed_expected = list(reversed(expected_path))
    for i in range(len(reversed_expected)):
        rotated_reversed = reversed_expected[i:] + reversed_expected[:i]
        if predicted_path == rotated_reversed:
            return True

    return False