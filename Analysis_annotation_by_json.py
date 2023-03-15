import os
import json


class HuoShanAnalysisAnnotationJson:
    def __init__(self, json_base_path):
        '''
        :param json_base_path: 标注文件的根路径
        '''
        # 初始化确认json工程结构
        self.camera_6mm_json_path = os.path.join(json_base_path, 'camera_6mm')
        self.camera_12mm_json_path = os.path.join(json_base_path, 'camera_12mm')
        self.car_attribute_json_path = os.path.join(json_base_path, 'car_attribute')
        self.lidar_json_path = os.path.join(json_base_path, 'lidar')
        self.pedestrian_attribute_json_path = os.path.join(json_base_path, 'pedestrian_attribute')
        self.type_attribute_json_path = os.path.join(json_base_path, 'type_attribute')
        self.with_person_attribute_json_path = os.path.join(json_base_path, 'with_person_attribute')

    def check_file_exists(self, json_name):
        '''
        检验文件存在完整与否
        '''
        ret_dict = {
            'camera_6mm_json': os.path.join(self.camera_6mm_json_path, json_name),
            'camera_12mm_json': os.path.join(self.camera_12mm_json_path, json_name),
            'lidar_json': os.path.join(self.lidar_json_path, json_name),
            'type_attribute_json': os.path.join(self.type_attribute_json_path, json_name),
            'car_attribute_json': os.path.join(self.car_attribute_json_path, json_name),
            'pedestrian_attribute_json': os.path.join(self.pedestrian_attribute_json_path, json_name),
            'with_person_attribute_json': os.path.join(self.with_person_attribute_json_path, json_name),
        }
        for key in ret_dict:
            if not os.path.exists(ret_dict[key]):
                print('文件缺失:', ret_dict[key])
        return ret_dict

    def analysis(self, json_name, save_path=None):
        '''
        该函数通过类初始化定义的文件结构
            解析生成一个合并的json文件
        :param json_name: 需要解析的json文件名
        :param save_path: 默认为None，当需要保存混合的json是设置该参数即可
        :return: 合并的json文件
        '''
        # 定义融合后的json
        comprehensive = {
            'targets': []
        }
        path_dict = self.check_file_exists(json_name)
        # 根据init初始化定义的文件结构构建响应json路径
        camera_6mm_json = path_dict['camera_6mm_json']
        camera_12mm_json = path_dict['camera_12mm_json']
        lidar_json = path_dict['lidar_json']
        type_attribute_json = path_dict['type_attribute_json']
        car_attribute_json = path_dict['car_attribute_json']
        pedestrian_attribute_json = path_dict['pedestrian_attribute_json']
        with_person_attribute_json = path_dict['with_person_attribute_json']

        # type_attribute_json 为目标必须存在属性，所以优先检索该json
        with open(type_attribute_json, "r", encoding="utf-8") as type_attribute:
            type_attribute = json.load(type_attribute)

            # load json black
            # ----------------------------------------------------------------------------------------
            camera_6mm = open(camera_6mm_json, "r", encoding="utf-8")
            camera_12mm = open(camera_12mm_json, "r", encoding="utf-8")
            lidar = open(lidar_json, "r", encoding="utf-8")
            car_attribute = open(car_attribute_json, "r", encoding="utf-8")
            pedestrian_attribute = open(pedestrian_attribute_json, "r", encoding="utf-8")
            with_person_attribute = open(with_person_attribute_json, "r", encoding="utf-8")

            camera_6mm = json.load(camera_6mm)
            camera_12mm = json.load(camera_12mm)
            lidar = json.load(lidar)
            car_attribute = json.load(car_attribute)
            pedestrian_attribute = json.load(pedestrian_attribute)
            with_person_attribute = json.load(with_person_attribute)
            # ----------------------------------------------------------------------------------------

            # json合并模块
            # json输出结构不一致，导致需要反复重写，可能标注商提供的 json结构有问题
            # ----------------------------------------------------------------------------------------
            for target in type_attribute['type_attribute']:
                new_target = dict()
                new_target['obj_id'] = target['obj_id']
                new_target['type'] = target['type']
                # 检查6mm目标

                for target_6mm in camera_6mm['camera_6mm']:
                    obj_id = target_6mm['obj_id']
                    pop_dicet = dict(target_6mm)
                    if obj_id == new_target['obj_id']:
                        pop_dicet.pop('obj_id', None)
                        new_target['camera_6mm_2DBox'] = pop_dicet
                        break

                # 检查12mm目标
                for target_12mm in camera_12mm['camera_12mm']:
                    obj_id = target_12mm['obj_id']
                    pop_dicet = dict(target_12mm)
                    if obj_id == new_target['obj_id']:
                        pop_dicet.pop('obj_id', None)
                        new_target['camera_12mm_2DBox'] = pop_dicet
                        break

                # 检查点云目标
                for target_lidar in lidar['lidar']:
                    obj_id = target_lidar['obj_id']
                    pop_dicet = dict(target_lidar)
                    if obj_id == new_target['obj_id']:
                        pop_dicet.pop('obj_id', None)
                        new_target['3DBox'] = pop_dicet
                        break

                # 检查车辆附加属性
                for attribute in car_attribute['car_attribute']:
                    obj_id = attribute['obj_id']
                    pop_dicet = dict(attribute)
                    if obj_id == new_target['obj_id']:
                        pop_dicet.pop('obj_id', None)
                        new_target['car_attribute'] = pop_dicet
                        break

                # 检查pedestrian_attribute
                for tartget in pedestrian_attribute['pedestrian_attribute']:
                    obj_id = tartget['obj_id']
                    pop_dicet = dict(tartget)
                    if obj_id == new_target['obj_id']:
                        pop_dicet.pop('obj_id', None)
                        new_target['car_attribute'] = pop_dicet
                        break

                # 检查with_person_attribute
                for tartget in with_person_attribute['with_person_flag']:
                    obj_id = tartget['obj_id']
                    pop_dicet = dict(tartget)
                    if obj_id == new_target['obj_id']:
                        pop_dicet.pop('obj_id', None)
                        new_target['car_attribute'] = pop_dicet
                        break
                comprehensive['targets'].append(new_target)
                # ----------------------------------------------------------------------------------------

        # 保存合并后的json
        if save_path != None:
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            comprehensive_path = os.path.join(save_path, json_name)
            with open(comprehensive_path, 'w') as f:
                json.dump(comprehensive, f)
                # json.dumps(new_target)  # 编码为json
                print('json save to ---->>>>', comprehensive_path)

        return comprehensive


if __name__ == '__main__':
    analysis = HuoShanAnalysisAnnotationJson(
        r'./Test_data/DW-V2.0试标Json结果交付-0313-V5')
    analysis.analysis('00276.json', './ret')
