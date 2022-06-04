import numpy
from OpenGL.GL import glClearColor, glColorMaterial, glCullFace, glDepthFunc, glEnable, glLightfv, \
    GL_AMBIENT_AND_DIFFUSE, GL_BACK, GL_CULL_FACE, GL_COLOR_MATERIAL, GL_DEPTH_TEST, GL_FRONT_AND_BACK, GL_LESS, \
    GL_LIGHT0, GL_POSITION, GL_SPOT_DIRECTION
from OpenGL.GLUT import glutCreateWindow, glutDisplayFunc, glutInit, glutInitDisplayMode, glutInitWindowSize, \
    glutMainLoop, GLUT_SINGLE, GLUT_RGB
from OpenGL.constants import GLfloat_3, GLfloat_4


class Viewer(object):
    def __init__(self):
        """ 初始化 viewer. """
        # 初始化接口，创建窗口并注册渲染函数
        self.init_interface()
        # 初始化opengl的配置
        self.init_opengl()
        # 初始化3d场景
        self.init_scene()
        # 初始化交互操作相关的代码
        self.init_interaction()

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
        # 初始化场景，之后实现
        pass

    def init_interaction(self):
        # 初始化交互操作相关的代码，之后实现
        pass

    def main_loop(self):
        # 程序主循环开始
        glutMainLoop()

    def render(self):
        # 程序进入主循环后每一次循环调用的渲染函数
        pass


if __name__ == "__main__":
    viewer = Viewer()
    viewer.main_loop()
