import numpy
from OpenGL.GL import glClearColor, glColorMaterial, glCullFace, glDepthFunc, glEnable, glLightfv, \
    GL_AMBIENT_AND_DIFFUSE, GL_BACK, GL_CULL_FACE, GL_COLOR_MATERIAL, GL_DEPTH_TEST, GL_FRONT_AND_BACK, GL_LESS, \
    GL_LIGHT0, GL_POSITION, GL_SPOT_DIRECTION
from OpenGL.GLUT import glutCreateWindow, glutDisplayFunc, glutInit, glutInitDisplayMode, glutInitWindowSize, \
    glutMainLoop, GLUT_SINGLE, GLUT_RGB
from OpenGL.constants import GLfloat_3, GLfloat_4
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_LIGHTING, glClear, GL_DEPTH_BUFFER_BIT, GL_MODELVIEW, glMatrixMode, \
    GL_COLOR_BUFFER_BIT, glPushMatrix, glLoadIdentity, glDisable, glPopMatrix, glFlush, GL_PROJECTION, glViewport, \
    glTranslated, glCallList
from OpenGL.raw.GLU import gluPerspective
from OpenGL.raw.GLUT import glutGet, GLUT_WINDOW_WIDTH, GLUT_WINDOW_HEIGHT

from node import Sphere, SnowFigure, Cube
from primitive import init_primitives, G_OBJ_PLANE
from scene import Scene


class Viewer(object):
    def __init__(self):
        """ 初始化 viewer. """
        # 初始化接口，创建窗口并注册渲染函数
        self.init_interface()
        # 初始化 OpenGL 的配置
        self.init_opengl()
        # 初始化 3D 场景
        self.init_scene()
        # 初始化交互操作相关的代码
        self.init_interaction()
        init_primitives()

    def init_interface(self):
        """ 初始化窗口并注册渲染函数 """
        glutInit()
        glutInitWindowSize(1280, 720)
        glutCreateWindow(b"3D Modeller")
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        # 注册窗口渲染函数
        glutDisplayFunc(self.render)

    def init_opengl(self):
        """ 初始化 OpenGL 的配置 """
        # 模型视图矩阵
        self.inverseModelView = numpy.identity(4)
        # 模型视图矩阵的逆矩阵
        self.modelView = numpy.identity(4)

        # 开启剔除操作效果
        glEnable(GL_CULL_FACE)
        # 取消对多边形背面进行渲染的计算（看不到的部分不渲染）
        glCullFace(GL_BACK)
        # 开启深度测试
        glEnable(GL_DEPTH_TEST)
        # 测试是否被遮挡，被遮挡的物体不予渲染
        glDepthFunc(GL_LESS)
        # 启用0号光源
        glEnable(GL_LIGHT0)
        # 设置光源的位置
        glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_4(0, 0, 1, 0))
        # 设置光源的照射方向
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, GLfloat_3(0, 0, -1))
        # 设置材质颜色
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
        # 设置清屏的颜色
        glClearColor(0.4, 0.4, 0.4, 0.0)

    def init_scene(self):
        """ 初始化场景 """
        # 创建一个场景实例
        self.scene = Scene()
        # 初始化场景内的对象
        self.create_sample_scene()

    def create_sample_scene(self):
        # 创建方体
        cube_node = Cube()
        cube_node.translate(2, 0, 2)
        cube_node.color_index = 1
        self.scene.add_node(cube_node)

        # 创建一个球体
        sphere_node = Sphere()
        # 设置球体的颜色
        sphere_node.color_index = 3
        sphere_node.translate(-2, 0, 2)
        # 将球体放进场景中，默认在正中央
        self.scene.add_node(sphere_node)

        # 添加小雪人
        hierarchical_node = SnowFigure()
        hierarchical_node.translate(-2, 0, -2)
        self.scene.add_node(hierarchical_node)

    def init_interaction(self):
        # 初始化交互操作相关的代码
        pass

    def main_loop(self):
        # 程序主循环开始
        glutMainLoop()

    def render(self):
        """ 程序进入主循环后每一次循环调用的渲染函数 """
        # 初始化投影矩阵
        self.init_view()

        # 启动光照
        glEnable(GL_LIGHTING)
        # 清空颜色缓存与深度缓存
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 设置模型视图矩阵，目前为止用单位矩阵就行了。
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # 渲染场景
        self.scene.render()

        # 每次渲染后复位光照状态
        glDisable(GL_LIGHTING)
        glCallList(G_OBJ_PLANE)
        glPopMatrix()
        # 把数据刷新到显存上
        glFlush()

    def init_view(self):
        """ 初始化投影矩阵 """
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        # 得到屏幕宽高比
        aspect_ratio = float(xSize) / float(ySize)

        # 设置投影矩阵
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # 设置视口，应与窗口重合
        glViewport(0, 0, xSize, ySize)
        # 设置透视，摄像机上下视野幅度70度
        # 视野范围到距离摄像机1000个单位为止。
        gluPerspective(70, aspect_ratio, 0.1, 1000.0)
        # 摄像机镜头从原点后退15个单位
        glTranslated(0, 0, -15)


if __name__ == "__main__":
    viewer = Viewer()
    viewer.main_loop()
