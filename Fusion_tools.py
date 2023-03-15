from io import BytesIO
import os
import cv2  # pip install opencv-python
import numpy as np  # pip install numpy
import open3d as o3d  # pip install open3d
import pandas as pd  # pip install pandas
from matplotlib import pyplot as plt  # pip install matplotlib
import PIL


class Fusion_tools:
    def __init__(self, camera_matrix_camera, extrinsic_matrix):
        self.camera_matrix_camera = camera_matrix_camera
        self.extrinsic_matrix = extrinsic_matrix

    def show_fusion(self, lidar_file_path, camera_file_path):
        pcd = o3d.t.io.read_point_cloud(lidar_file_path)
        lidar_pcd_DF = pd.DataFrame(pcd.point.positions.numpy(), columns=['x', 'y', 'z'])
        # lidar_pcd_DF['y'] = -lidar_pcd_DF['y']
        lidar_pcd_DF['zero'] = 1

        # 外参
        xyz0 = lidar_pcd_DF[['x', 'y', 'z', 'zero']].values @ self.extrinsic_matrix.T
        lidar_pcd_DF[['u', 'v', 'w']] = xyz0 @ self.camera_matrix_camera.T
        lidar_pcd_DF['u'] = lidar_pcd_DF['u'] / lidar_pcd_DF['w']
        lidar_pcd_DF['v'] = lidar_pcd_DF['v'] / lidar_pcd_DF['w']
        lidar_pcd_DF['w'] = lidar_pcd_DF['w'] / lidar_pcd_DF['w']

        lidar_pcd_DF = lidar_pcd_DF[
            (lidar_pcd_DF['u'] > 0) & (lidar_pcd_DF['u'] < 1920) & (lidar_pcd_DF['v'] > 0) & (lidar_pcd_DF['v'] < 1080)]

        frame = cv2.imdecode(np.fromfile(camera_file_path, dtype=np.int8), -1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        fig, ax = plt.subplots(figsize=(19.2, 10.8), layout='constrained')
        plt.axis('off')
        ax.scatter(x=lidar_pcd_DF['u'], y=lidar_pcd_DF['v'], c=lidar_pcd_DF['y'], s=0.5, cmap='rainbow')
        ax.matshow(frame)

        # ax.text(40, 60, 'camera file: %s' % (os.path.split(camera_file_path)[1]), fontsize=10, color='white')
        # ax.text(40, 40, 'lidar file: %s' % (os.path.split(lidar1_file_path)[1]), fontsize=10, color='white')
        # 申请缓冲地址
        buffer_ = BytesIO()  # using buffer,great way!
        # 保存在内存中，而不是在本地磁盘，注意这个默认认为你要保存的就是plt中的内容
        plt.savefig(buffer_, format='png')
        buffer_.seek(0)
        # 用PIL或CV2从内存中读取
        dataPIL = PIL.Image.open(buffer_)
        # 转换为nparrary，PIL转换就非常快了,data即为所需
        data = np.asarray(dataPIL)
        cv2.imshow('image', data)
        cv2.waitKey(0)
        # 释放缓存
        buffer_.close()
        return data
        # plt.show()


if __name__ == '__main__':
    lidar1_file_path = r'./Test_data\DataSet\00001.pcd'
    camera_file_path = r'./Test_data\DataSet\00001.jpg'

    # camera2 内参
    camera_matrix_camera2 = np.array([
        [3992.8730702442631, 0.0, 68.03105595291413, 0],
        [0.0, 3.9938781972371780e+03, 5.7696760488326117e+02, 0],
        [0, 0, 1, 0],
    ]
    )
    # camera3 内参
    camera_matrix_camera3 = np.array([
        [2086.1597172498164, 0.0, 950.57223449235289, 0],
        [0.0, 2.0878898342380035e+03, 5.2959928591229880e+02, 0],
        [0, 0, 1, 0],
    ]
    )
    # lidar2camera 转换矩阵\外参
    extrinsic_matrix = np.array([
        [-0.00152138, -0.999984, 0.00530767, -0.31778],
        [0.061145, -0.00539078, -0.998114, 0.370984],
        [0.998127, -0.00119398, 0.0611522, 2.41304],
        [0, 0, 0, 1],
    ]
    )
    fusion_tools = Fusion_tools(camera_matrix_camera3, extrinsic_matrix)
    fusion_tools.show_fusion(lidar1_file_path, camera_file_path)
    # show_fusion(lidar1_file_path, camera_file_path, camera_matrix_camera2, extrinsic_matrix)
