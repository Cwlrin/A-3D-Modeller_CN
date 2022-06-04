import numpy
import sys

from node import Sphere, SnowFigure, Cube


class Scene(object):
    # 放置节点的深度，放置的节点距离摄像机 15 个单位
    PLACE_DEPTH = 15.0

    def __init__(self):
        # 场景下的节点队列
        self.node_list = list()
        # 跟踪当前选定的节点
        # 操作可能取决于是否选择了某些内容
        self.selected_node = None

    def add_node(self, node):
        """ 在场景中加入一个新节点 """
        self.node_list.append(node)

    def render(self):
        """ 遍历场景下所有节点并渲染 """
        for node in self.node_list:
            node.render()

    def pick(self, start, direction, mat):
        """
        参数中的 mat 为当前 ModelView 的逆矩阵，作用是计算激光在局部（对象）坐标系中的坐标
        参数中的 start 描述光线的方向
        """
        if self.selected_node is not None:
            self.selected_node.select(False)
            self.selected_node = None

        # 找出激光击中的最近的节点。
        mindist = sys.maxsize
        closest_node = None
        for node in self.node_list:
            hit, distance = node.pick(start, direction, mat)
            if hit and distance < mindist:
                mindist, closest_node = distance, node

        # 如果找到了，选中它
        if closest_node is not None:
            closest_node.select()
            closest_node.depth = mindist
            closest_node.selected_loc = start + direction * mindist
            self.selected_node = closest_node

    def move_selected(self, start, direction, inv_modelview):
        """
        移动选定节点（如果有）
        参数:
            start, direction  描述要移动到的光线
            inv_modelview     场景的反向 modelview 矩阵
        """
        if self.selected_node is None:
            return

        # 找到选中节点的坐标与深度（距离）
        node = self.selected_node
        depth = node.depth
        oldloc = node.selected_loc

        # 新坐标的深度保持不变
        newloc = (start + direction * depth)

        # 得到世界坐标系中的移动坐标差
        translation = newloc - oldloc
        pre_tran = numpy.array([translation[0], translation[1], translation[2], 0])
        translation = inv_modelview.dot(pre_tran)

        # 节点做平移变换
        node.translate(translation[0], translation[1], translation[2])
        node.selected_loc = newloc

    def place(self, shape, start, direction, inv_modelview):
        """
        放置新节点
        参数：
            shape             要添加的形状
            start, direction  描述要移动到的光线
            inv_modelview     场景的反向 modelview 矩阵
        """
        new_node = None
        if shape == 'sphere':
            new_node = Sphere()
        elif shape == 'cube':
            new_node = Cube()
        elif shape == 'figure':
            new_node = SnowFigure()

        self.add_node(new_node)

        # 得到在摄像机坐标系中的坐标
        translation = (start + direction * self.PLACE_DEPTH)

        # 转换到世界坐标系
        pre_tran = numpy.array([translation[0], translation[1], translation[2], 1])
        translation = inv_modelview.dot(pre_tran)

        new_node.translate(translation[0], translation[1], translation[2])

    def rotate_selected_color(self, forwards):
        """ 旋转当前选定节点的颜色 """
        if self.selected_node is None:
            return
        self.selected_node.rotate_color(forwards)

    def scale_selected(self, up):
        """ 缩放当前选择节点 """
        if self.selected_node is None:
            return
        self.selected_node.scale(up)
