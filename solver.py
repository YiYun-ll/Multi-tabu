import os
import json
from tqdm import tqdm
# from tabu import tabu
# from submission import tabu
# from submission_gai import tabu
# from SA import SA
#from old import tabu
# from TS import multitabu
# from TS_submission import multitabu
# from TS_pro import multitabu
from TS_pro_submission import multitabu
from utils import convert_input_data, show_result, is_same_cycle

if __name__ == '__main__':
    vis_dir = 'visualization_random'
    if not os.path.exists(vis_dir):
        os.makedirs(vis_dir)   
    test_file = 'loop_random.json'
    points = 0
    with open(test_file, 'r') as file:
        test_cases = json.load(file)
    idx = 0
    for dic in tqdm(test_cases):
        idx += 1
        input_data = dic['input']
        output_data = dic['output']
        distance = dic['distance']
        city_position, goods_class, city_class = convert_input_data(input_data)
        best_solution, city_position, city_class, predicted_distance = multitabu(city_position, goods_class, city_class,5)
        save_path = os.path.join(vis_dir, str(idx) + '.png')
        prediction = show_result(best_solution, city_position, city_class, save_path, vis=False)
        if is_same_cycle(prediction, output_data) or distance == predicted_distance:
            points += 1
        else:
            print(f"测试失败：输入数据为{input_data}，期望输出为{output_data}，实际输出为{prediction}")
            save_path = os.path.join(vis_dir, f"{idx:04d}.png")
            print(f"期望距离为{distance}，实际距离为{predicted_distance}")
            show_result(best_solution, city_position, city_class, save_path, vis=True)
            
    print(f"测试完成，得分为{points}/{len(test_cases)}, {points/len(test_cases)}")