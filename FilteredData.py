import json
import numpy as np
import cv2
import os
from Analysis_annotation_by_json import HuoShanAnalysisAnnotationJson


class Filtered:

    @staticmethod
    def filtered_3Dbox_by_dimension(comprehensive_json_data, filtered_size=[3, 3, 3]) -> list:
        '''
        通过3D框筛选目标s
        :param comprehensive_json_data:混合后的json数据
        :param filtered_size:【长，宽，高】
        :return:【超尺寸目标_1，超尺寸目标_2，...】
        '''
        targets = comprehensive_json_data['targets']
        filtered_l, filtered_h, filtered_w = filtered_size
        alarm_list = []
        for target in targets:
            target = dict(target)
            Box_3D = target.get('3DBox')
            if Box_3D != None:
                l = Box_3D['l']
                h = Box_3D['h']
                w = Box_3D['w']
                if l > filtered_l or h > filtered_h or w > filtered_w:
                    alarm_list.append(target)  # 应追加 尺寸及 警告信息
        return alarm_list

    @staticmethod
    def cut_img(alarm_list: list, img_path, save_path):
        img = cv2.imread(img_path)
        # cv2.imshow('img', img)
        # cv2.waitKey(0)
        image_name = str(os.path.split(img_path)[-1]).split('.')[0]
        img_save_path = os.path.join(save_path, image_name)
        if not os.path.exists(img_save_path):
            os.makedirs(img_save_path)
        for index, alarm_target in enumerate(alarm_list):
            type_targe = alarm_target['type']
            if '12mm' in img_path:
                box_info = alarm_target['camera_12mm_2DBox']
            else:
                box_info = alarm_target['camera_6mm_2DBox']

            xmin = int(box_info['xmin'])
            xmax = int(box_info['xmax'])
            ymin = int(box_info['ymin'])
            ymax = int(box_info['ymax'])
            cut_save = os.path.join(img_save_path, str(index) + '_' + str(type_targe) + '.png')  # 应追加 尺寸及 警告信息
            cut_img = img[ymin:ymax, xmin:xmax]
            cv2.imwrite(cut_save, cut_img)


def filtere_test():
    json_base_path = r'C:\Users\NailinLiao\Desktop\Acceptance_tools\Test_data\DW-V2.0试标Json结果交付'
    img_base_path = r'C:\Users\NailinLiao\Desktop\20230228_count5154_camera_2_on\camera_6mm'
    img_name = '02461'
    save_path = r'./ret'
    img_path = os.path.join(img_base_path, img_name + '.jpg')
    analysis = HuoShanAnalysisAnnotationJson(json_base_path)
    comprehensive_json_data = analysis.analysis(img_name + '.json')

    alarm_list = Filtered.filtered_3Dbox_by_dimension(comprehensive_json_data)
    Filtered.cut_img(alarm_list, img_path, save_path)


if __name__ == '__main__':
    filtere_test()
