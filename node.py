import random
from OpenGL.GL import glCallList, glColor3f, glMaterialfv, glMultMatrixf, glPopMatrix, glPushMatrix, GL_EMISSION, \
    GL_FRONT
import numpy

import color
from primitive import G_OBJ_SPHERE


class Node(object):
    def __init__(self):
        # 该节点的颜色序号
        self.color_index = random.randint(color.MIN_COLOR, color.MAX_COLOR)
        # 该节点的平移矩阵，决定了该节点在场景中的位置
        self.translation_matrix = numpy.identity(4)
        # 该节点的缩放矩阵，决定了该节点的大小
        self.scaling_matrix = numpy.identity(4)

    def render(self):
        """ 渲染节点 """
        glPushMatrix()
        # 实现平移
        glMultMatrixf(numpy.transpose(self.translation_matrix))
        # 实现缩放
        glMultMatrixf(self.scaling_matrix)
        cur_color = color.COLORS[self.color_index]
        # 设置颜色
        glColor3f(cur_color[0], cur_color[1], cur_color[2])
        # 渲染对象模型
        self.render_self()
        glPopMatrix()

    def render_self(self):
        raise NotImplementedError("The Abstract Node Class doesn't define 'render_self'")


class Primitive(Node):
    def __init__(self):
        super(Primitive, self).__init__()
        self.call_list = None

    def render_self(self):
        glCallList(self.call_list)


class Sphere(Primitive):
    """ 球形图元 """
    def __init__(self):
        super(Sphere, self).__init__()
        self.call_list = G_OBJ_SPHERE
