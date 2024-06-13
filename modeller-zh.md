标题： 3D 建模师
作者：Erick Dransch

**Erick 是一位软件开发者，也是 2D 和 3D 计算机图形学的爱好者。他曾参与过视频游戏、3D
特效软件和计算机辅助设计工具的开发。如果某项工作涉及到现实模拟，他很可能愿意进一步了解。你可以在 [erickdransch.com](http://erickdransch.com)
上找到他。**

## 引言

人类天生具有创造力。我们不断地设计和构建新颖、有用和有趣的事物。在现代，我们编写软件来协助设计和创造过程。

计算机辅助设计（CAD）软件允许创造者在构建设计的物理版本之前，设计建筑物、桥梁、视频游戏艺术、电影怪物、3D 可打印对象以及许多其他事物。

在它们的核心，CAD 工具是将三维设计抽象成可以在二维屏幕上查看和编辑的东西的一种方法。

为了满足这个定义，CAD 工具必须提供三个基本功能。

首先，它们必须有一个数据结构来表示正在设计的对象：这是计算机对用户正在构建的三维世界的理解。

其次，CAD 工具必须提供一种在用户屏幕上显示设计的方法。用户正在设计一个具有三个维度的物理对象，但计算机屏幕仅有两个维度。CAD 工具必须模拟我们如何感知对象，并将它们绘制到屏幕上，以便用户能够理解对象的所有三个维度。

第三，CAD 工具必须提供一种与正在设计的对象交互的方式。用户必须能够添加和修改设计，以产生所需的结果。

此外，所有工具都需要一种从磁盘保存和加载设计的方法，以便用户可以协作、共享和保存他们的工作。

特定领域的 CAD 工具为该领域的特定需求提供了许多额外的功能。例如，建筑 CAD 工具将提供物理模拟来测试建筑物上的气候压力，一个 3D 打印工具将具有检查对象是否确实有效打印的功能，电气 CAD 工具将模拟电流通过铜的物理过程，电影特效套件将包括准确模拟热力学特性的功能。

然而，所有 CAD 工具至少必须包括上述三个特征：表示设计的数据结构、将其显示到屏幕上的能力，以及与设计交互的方法。

考虑到这一点，让我们探索如何在 500 行 Python 中表示 3D 设计、将其显示到屏幕上以及与之交互。

## 渲染作为指导

3D 建模中许多设计决策背后的驱动力是渲染过程。我们希望能够存储和渲染设计中的复杂对象，但同时我们希望保持渲染代码的复杂度低。让我们审视渲染过程，并探索设计的数据结构，它允许我们用简单的渲染逻辑存储和绘制任意复杂的对象。

### 管理接口和主循环

在我们开始渲染之前，有一些事情需要设置。首先，我们需要创建一个窗口来展示我们的设计。其次，我们希望与图形驱动程序通信以渲染到屏幕上。

我们不想直接与图形驱动程序通信，因此我们使用一个名为 OpenGL 的跨平台抽象层，以及一个名为 GLUT（OpenGL 实用工具包）的库来管理我们的窗口。

#### 关于 OpenGL 的说明

OpenGL 是一个用于跨平台开发的图形应用程序编程接口。它是跨平台开发图形应用程序的标准 API。

OpenGL 有两个主要的变体：传统 OpenGL（Legacy OpenGL）和现代 OpenGL（Modern OpenGL）。

OpenGL 中的渲染基于由顶点和法线定义的多边形。例如，要渲染一个立方体的一面，我们需要指定这四个顶点和该面的法线。

传统 OpenGL 提供了一个“固定功能管线”。通过设置全局变量，程序员可以启用和禁用诸如照明、着色、面剔除等功能的自动化实现。然后 OpenGL 自动使用启用的功能渲染场景。这项功能已被弃用。

另一方面，现代 OpenGL 具有一个可编程的渲染管线，程序员编写小型程序，称为“着色器”（shaders），它们在专用图形硬件（GPU）上运行。现代 OpenGL 的可编程管线已经取代了传统 OpenGL。

在这个项目中，尽管它已被弃用，我们还是使用了传统 OpenGL。传统 OpenGL 提供的固定功能非常有用，有助于保持代码体积小。它减少了所需的线性代数知识量，并简化了我们将要编写的代码。

#### 关于 GLUT

与 OpenGL 捆绑在一起的 GLUT（OpenGL 工具箱）允许我们创建操作系统窗口并注册用户界面回调。这些基本功能对我们来说是足够的。如果我们想要一个更全面功能的窗口管理和用户交互库，我们会考虑使用像 GTK 或 Qt 这样的完整窗口工具包。

#### 视图管理器

为了管理 GLUT 和 OpenGL 的设置，以及驱动模型编辑器的其余部分，我们创建了一个名为 `Viewer` 的类。
我们使用单个 `Viewer` 实例，它管理窗口的创建和渲染，并包含我们程序的主循环。

在 `Viewer` 的初始化过程中，我们创建了 GUI 窗口并初始化了 OpenGL。

`init_interface` 函数创建模型编辑器将被渲染到的窗口，并指定了当设计需要被渲染时调用的函数。`init_opengl` 函数设置了项目所需的 OpenGL 状态。它设置了矩阵，启用了背面剔除，注册了一个照亮场景的光源，并告诉 OpenGL 我们希望对象被着色。`init_scene` 函数创建了 `Scene` 对象并在场景中放置了一些初始节点以便用户开始使用。我们很快就会看到更多关于 `Scene`数据结构的内容。

最后，`init_interaction` 注册了用户交互的回调，我们将在后面讨论。

初始化 `Viewer` 后，我们调用 `glutMainLoop` 将程序执行转移到 GLUT。这个函数永不返回。我们注册在 GLUT 事件上的回调将在那些事件发生时被调用。

```python
class Viewer(object):
    def __init__(self):
        """ Initialize the viewer. """
        self.init_interface()
        self.init_opengl()
        self.init_scene()
        self.init_interaction()
        init_primitives()

    def init_interface(self):
        """ initialize the window and register the render function """
        glutInit()
        glutInitWindowSize(640, 480)
        glutCreateWindow("3D Modeller")
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutDisplayFunc(self.render)

    def init_opengl(self):
        """ initialize the opengl settings to render the scene """
        self.inverseModelView = numpy.identity(4)
        self.modelView = numpy.identity(4)

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_4(0, 0, 1, 0))
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, GLfloat_3(0, 0, -1))

        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
        glClearColor(0.4, 0.4, 0.4, 0.0)

    def init_scene(self):
        """ initialize the scene object and initial scene """
        self.scene = Scene()
        self.create_sample_scene()

    def create_sample_scene(self):
        cube_node = Cube()
        cube_node.translate(2, 0, 2)
        cube_node.color_index = 2
        self.scene.add_node(cube_node)

        sphere_node = Sphere()
        sphere_node.translate(-2, 0, 2)
        sphere_node.color_index = 3
        self.scene.add_node(sphere_node)

        hierarchical_node = SnowFigure()
        hierarchical_node.translate(-2, 0, -2)
        self.scene.add_node(hierarchical_node)

    def init_interaction(self):
        """ init user interaction and callbacks """
        self.interaction = Interaction()
        self.interaction.register_callback('pick', self.pick)
        self.interaction.register_callback('move', self.move)
        self.interaction.register_callback('place', self.place)
        self.interaction.register_callback('rotate_color', self.rotate_color)
        self.interaction.register_callback('scale', self.scale)

    def main_loop(self):
        glutMainLoop()


if __name__ == "__main__":
    viewer = Viewer()
    viewer.main_loop()
```

在我们深入 `render` 函数之前，我们应该讨论一些线性代数的基础知识。

### 坐标空间

对于我们的目的来说，坐标空间是一个原点和一组 3 个基向量，通常是 $x$、$y$ 和 $z$ 轴。

### 点

任何三维空间中的点都可以表示为相对于原点在 $x$、$y$ 和 $z$ 方向上的偏移量。点的表示是相对于它所在的坐标空间的。同一个点在不同的坐标空间中有不同的表示。任何三维空间中的点都可以在任何三维坐标空间中表示。

### 向量

一个向量是一个 $x$、$y$ 和 $z$ 值，分别表示两个点在 $x$、$y$ 和 $z$ 轴之间的差异。

### 变换矩阵

在计算机图形学中，为了方便起见，不同类型的点使用多个不同的坐标空间。变换矩阵将点从一个坐标空间转换到另一个坐标空间。要将向量 $v$ 从一个坐标空间转换到另一个坐标空间，我们通过乘以变换矩阵 $M$ 来实现：$v' = Mv$。一些常见的变换矩阵包括平移、缩放和旋转。

### 模型、世界、视图和投影坐标空间

![](https://aosabook.org/en/500L/modeller-images/newtranspipe.png)

要在屏幕上绘制一个项目，我们需要在几种不同的坐标空间之间进行转换。

该图 [^1] 的右侧，包括从眼睛空间到视口空间的所有变换都将由 OpenGL 为我们处理。

从眼睛空间到齐次裁剪空间的转换由 `gluPerspective` 处理，而到标准化设备空间和视口空间的转换由 `glViewport` 处理。
这两个矩阵相乘后存储为 GL_PROJECTION 矩阵。我们不需要知道这些矩阵的术语或它们如何工作的详细信息来进行此项目。

然而，我们确实需要自己管理图表的左侧。我们定义了一个矩阵，它将模型（也称为网格）中的点从模型空间转换到世界空间，称为模型矩阵。我们还定义了视图矩阵，它将从世界空间转换到眼睛空间。
在这个项目中，我们将这两个矩阵结合起来得到模型视图矩阵。

要了解更多关于完整的图形渲染管线以及所涉及的坐标空间，请参阅 [ 实时渲染 ](http://www.realtimerendering.com/) 的第 2 章，或另一本计算机图形学入门书籍。

### 使用视图渲染器进行渲染

`render` 函数首先设置在渲染时需要的任何 OpenGL 状态。它通过 `init_view` 初始化投影矩阵，并使用交互成员的数据来使用将场景空间转换为世界空间的变换矩阵初始化 ModelView 矩阵。我们将在下面看到更多关于 Interaction 类的内容。它使用 `glClear` 清除屏幕，并让场景自行渲染，然后渲染单位网格。

我们在渲染网格之前禁用 OpenGL 的照明。照明被禁用后，OpenGL 以纯色渲染项目，而不是模拟光源。这样，网格与场景在视觉上有所区分。

最后，`glFlush` 向图形驱动程序发出信号，表示我们已准备好缓冲区被刷新并显示在屏幕上。

```python
# class Viewer
def render(self):
    """ The render pass for the scene """
    self.init_view()

    glEnable(GL_LIGHTING)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Load the modelview matrix from the current state of the trackball
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    loc = self.interaction.translation
    glTranslated(loc[0], loc[1], loc[2])
    glMultMatrixf(self.interaction.trackball.matrix)

    # store the inverse of the current modelview.
    currentModelView = numpy.array(glGetFloatv(GL_MODELVIEW_MATRIX))
    self.modelView = numpy.transpose(currentModelView)
    self.inverseModelView = inv(numpy.transpose(currentModelView))

    # render the scene. This will call the render function for each object
    # in the scene
    self.scene.render()

    # draw the grid
    glDisable(GL_LIGHTING)
    glCallList(G_OBJ_PLANE)
    glPopMatrix()

    # flush the buffers so that the scene can be drawn
    glFlush()


def init_view(self):
    """ initialize the projection matrix """
    xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
    aspect_ratio = float(xSize) / float(ySize)

    # load the projection matrix. Always the same
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    glViewport(0, 0, xSize, ySize)
    gluPerspective(70, aspect_ratio, 0.1, 1000.0)
    glTranslated(0, 0, -15)

```

### 渲染内容：场景

现在我们已经初始化了渲染管线来处理世界坐标空间中的绘图，我们将要渲染什么？回想一下，我们的目标是拥有一个由 3D 模型组成的设计。我们需要一个数据结构来包含这个设计，并且我们需要使用这个数据结构来渲染设计。
注意在上面我们从视图的渲染循环中调用了 `self.scene.render()`。什么是场景？

`Scene` 类是我们用来表示设计的的数据结构的接口。它抽象了数据结构的细节，并提供了与设计交互所需的必要接口函数，包括渲染、添加项目和操作项目的函数。有一个 `Scene` 对象，由视图拥有。`Scene` 实例维护了一个包含场景中所有项目列表 `node_list`。它还跟踪所选项目。

场景上的 `render` 函数简单地对 `node_list` 的每个成员调用 `render`。

```python
class Scene(object):
    # the default depth from the camera to place an object at
    PLACE_DEPTH = 15.0

    def __init__(self):
        # The scene keeps a list of nodes that are displayed
        self.node_list = list()
        # Keep track of the currently selected node.
        # Actions may depend on whether or not something is selected
        self.selected_node = None

    def add_node(self, node):
        """ Add a new node to the scene """
        self.node_list.append(node)

    def render(self):
        """ Render the scene. """
        for node in self.node_list:
            node.render()
```

### 节点

在场景的 `render` 函数中，我们调用场景的 `node_list` 中每个项目的 `render`。但这个列表的元素是什么？我们称它们为*节点*。
从概念上讲，节点是任何可以放置在场景中的东西。在面向对象的软件中，我们将 `Node` 编写为一个抽象基类。任何表示要放置在 `Scene` 中的对象的类都将从 `Node` 继承。这个基类允许我们抽象地推理场景。

代码库的其余部分不需要知道它显示的对象的细节；它只需要知道它们是 `Node` 类。

每种类型的 `Node` 定义了自己渲染自己以及任何其他交互的行为。`Node` 跟踪有关自己的一些重要数据：平移矩阵、缩放矩阵、颜色等。将节点的平移矩阵乘以其缩放矩阵，可以得到从节点的模型坐标空间到世界坐标空间的变换矩阵。

节点还存储了一个轴对齐的边界框（AABB）。我们将在下面讨论选择时更多地了解 AABB。

`Node` 最简单的具体实现是 *原始体*。原始体是可以在场景中添加的单一实体形状。在这个项目中，原始体是 `Cube` 和 `Sphere`。

```python
class Node(object):
    """ Base class for scene elements """

    def __init__(self):
        self.color_index = random.randint(color.MIN_COLOR, color.MAX_COLOR)
        self.aabb = AABB([0.0, 0.0, 0.0], [0.5, 0.5, 0.5])
        self.translation_matrix = numpy.identity(4)
        self.scaling_matrix = numpy.identity(4)
        self.selected = False

    def render(self):
        """ renders the item to the screen """
        glPushMatrix()
        glMultMatrixf(numpy.transpose(self.translation_matrix))
        glMultMatrixf(self.scaling_matrix)
        cur_color = color.COLORS[self.color_index]
        glColor3f(cur_color[0], cur_color[1], cur_color[2])
        if self.selected:  # emit light if the node is selected
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.3, 0.3, 0.3])

        self.render_self()

        if self.selected:
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0])
        glPopMatrix()

    def render_self(self):
        raise NotImplementedError(
            "The Abstract Node Class doesn't define 'render_self'")


class Primitive(Node):
    def __init__(self):
        super(Primitive, self).__init__()
        self.call_list = None

    def render_self(self):
        glCallList(self.call_list)


class Sphere(Primitive):
    """ Sphere primitive """

    def __init__(self):
        super(Sphere, self).__init__()
        self.call_list = G_OBJ_SPHERE


class Cube(Primitive):
    """ Cube primitive """

    def __init__(self):
        super(Cube, self).__init__()
        self.call_list = G_OBJ_CUBE
```

渲染节点基于每个节点存储的变换矩阵。一个节点的变换矩阵是其缩放矩阵和平移矩阵的组合。无论节点的类型如何，渲染的第一步是将 OpenGL 模型视图矩阵设置为变换矩阵，以从模型坐标空间转换到视图坐标空间。

一旦 OpenGL 矩阵更新完毕，我们调用 `render_self` 来指示节点进行必要的 OpenGL 调用以绘制自身。最后，我们撤销对 OpenGL 状态针对此特定节点所做的任何更改。我们使用 OpenGL 中的 `glPushMatrix` 和 `glPopMatrix` 函数来保存和恢复在渲染节点之前和之后的模型视图矩阵的状态。

请注意，节点存储其颜色、位置和缩放，并在渲染之前将这些应用到 OpenGL 状态。

如果节点当前被选中，我们让它发出光。这样，用户就有视觉提示，知道他们选择了哪个节点。

为了渲染原始体，我们使用了 OpenGL 的调用列表功能。OpenGL 调用列表是一系列定义一次并以单一名称捆绑在一起的 OpenGL 调用。调用可以通过 `glCallList(LIST_NAME)` 进行分派。每个原始体（`Sphere` 和 `Cube`）定义了渲染它所需的调用列表（未显示）。

例如，一个立方体的调用列表绘制了立方体的 6 个面，其中心位于原点，边长恰好为 1 单位长度。

```python
# Pseudocode Cube definition
# Left face
((-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5)),
# Back face
((-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5)),
# Right face
((0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5)),
# Front face
((-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)),
# Bottom face
((-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5)),
# Top face
((-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5))
```

仅使用原始体对于建模应用来说将非常受限。3D 模型通常由多个原始体（或三角形网格组成，这不在本项目范围内）构成。

幸运的是，我们设计的 `Node` 类便于由多个原始体构成的 `Scene` 节点。实际上，我们可以支持任意节点组合，而无需增加复杂性。

为了激发兴趣，让我们考虑一个非常基本的图形：一个典型的雪人或由三个球体组成的雪雕。尽管这个图形由三个独立的原始体组成，我们希望能够将其视为一个单一的对象。

我们创建了一个名为 `HierarchicalNode` 的类，一个包含其他节点的 `Node`。它管理一个“子节点”列表。
对于层次结构节点，`render_self` 函数简单地对每个子节点调用 `render_self`。有了 `HierarchicalNode` 类，向场景中添加图形变得非常容易。

现在，定义雪人就像指定组成它的图形及其相对位置和大小一样简单。

![](https://aosabook.org/en/500L/modeller-images/nodes.jpg)

```python
class HierarchicalNode(Node):
    def __init__(self):
        super(HierarchicalNode, self).__init__()
        self.child_nodes = []

    def render_self(self):
        for child in self.child_nodes:
            child.render()
```

```python
class SnowFigure(HierarchicalNode):
    def __init__(self):
        super(SnowFigure, self).__init__()
        self.child_nodes = [Sphere(), Sphere(), Sphere()]
        self.child_nodes[0].translate(0, -0.6, 0)  # scale 1.0
        self.child_nodes[1].translate(0, 0.1, 0)
        self.child_nodes[1].scaling_matrix = numpy.dot(
            self.scaling_matrix, scaling([0.8, 0.8, 0.8]))
        self.child_nodes[2].translate(0, 0.75, 0)
        self.child_nodes[2].scaling_matrix = numpy.dot(
            self.scaling_matrix, scaling([0.7, 0.7, 0.7]))
        for child_node in self.child_nodes:
            child_node.color_index = color.MIN_COLOR
        self.aabb = AABB([0.0, 0.0, 0.0], [0.5, 1.1, 0.5])
```

你可能已经注意到 `Node` 对象形成了一个树状数据结构。`render` 函数通过层次结构节点，对树进行深度优先遍历。在遍历过程中，它保持一个 `ModelView` 矩阵的栈，这些矩阵用于转换到世界空间。

在每一步，它将当前的 `ModelView` 矩阵压入栈中，当它完成所有子节点的渲染时，它会从栈中弹出矩阵，留下父节点的 `ModelView` 矩阵在栈顶。

通过这种方式使 `Node` 类可扩展，我们可以在不改变任何其他场景操作和渲染代码的情况下，向场景中添加新类型的形状。使用节点概念来抽象一个 `Scene` 对象可能有多个子节点的事实被称为组合设计模式。

### 用户交互

现在我们的建模器能够存储和显示场景，我们需要一种与之交互的方式。

我们需要促进两种类型的交互。首先，我们需要能够改变场景的观察视角。我们希望能够在场景中移动视点或相机。其次，我们需要能够添加新的节点以及修改场景中的节点。

为了使用户能够与之交互，我们需要知道用户何时按下键盘或移动鼠标。幸运的是，操作系统已经知道这些事件发生的时间。GLUT 允许我们在特定事件发生时注册一个被调用的函数。我们编写函数来解释按键和鼠标移动，并告诉 GLUT 在相应的键被按下时调用这些函数。一旦我们知道用户按下了哪些键，我们需要解释输入并将预期的操作应用到场景中。

监听操作系统事件并解释其含义的逻辑位于 `Interaction` 类中。我们之前编写的 `Viewer` 类拥有 `Interaction` 的单一实例。我们将使用 GLUT 回调机制来注册在鼠标按钮被按下时调用的函数（`glutMouseFunc`）、鼠标移动时（`glutMotionFunc`）、键盘按钮被按下时（`glutKeyboardFunc`）以及箭头键被按下时（`glutSpecialFunc`）。我们很快会看到处理输入事件的函数。

```python
class Interaction(object):
    def __init__(self):
        """ Handles user interaction """
        # currently pressed mouse button
        self.pressed = None
        # the current location of the camera
        self.translation = [0, 0, 0, 0]
        # the trackball to calculate rotation
        self.trackball = trackball.Trackball(theta=-25, distance=15)
        # the current mouse location
        self.mouse_loc = None
        # Unsophisticated callback mechanism
        self.callbacks = defaultdict(list)

        self.register()

    def register(self):
        """ register callbacks with glut """
        glutMouseFunc(self.handle_mouse_button)
        glutMotionFunc(self.handle_mouse_move)
        glutKeyboardFunc(self.handle_keystroke)
        glutSpecialFunc(self.handle_keystroke)
```

#### 操作系统回调

为了有意义地解释用户输入，我们需要结合鼠标位置、鼠标按钮和键盘的知识。由于将用户输入解释为有意义的操作需要多行代码，我们将其封装在一个单独的类中，远离主代码路径。

`Interaction` 类从代码库的其余部分隐藏了不相关的复杂性，并将操作系统事件转换为应用程序级事件。

```python
# class Interaction 
def translate(self, x, y, z):
    """ translate the camera """
    self.translation[0] += x
    self.translation[1] += y
    self.translation[2] += z


def handle_mouse_button(self, button, mode, x, y):
    """ Called when the mouse button is pressed or released """
    xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
    y = ySize - y  # invert the y coordinate because OpenGL is inverted
    self.mouse_loc = (x, y)

    if mode == GLUT_DOWN:
        self.pressed = button
        if button == GLUT_RIGHT_BUTTON:
            pass
        elif button == GLUT_LEFT_BUTTON:  # pick
            self.trigger('pick', x, y)
        elif button == 3:  # scroll up
            self.translate(0, 0, 1.0)
        elif button == 4:  # scroll up
            self.translate(0, 0, -1.0)
    else:  # mouse button release
        self.pressed = None
    glutPostRedisplay()


def handle_mouse_move(self, x, screen_y):
    """ Called when the mouse is moved """
    xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
    y = ySize - screen_y  # invert the y coordinate because OpenGL is inverted
    if self.pressed is not None:
        dx = x - self.mouse_loc[0]
        dy = y - self.mouse_loc[1]
        if self.pressed == GLUT_RIGHT_BUTTON and self.trackball is not None:
            # ignore the updated camera loc because we want to always
            # rotate around the origin
            self.trackball.drag_to(self.mouse_loc[0], self.mouse_loc[1], dx, dy)
        elif self.pressed == GLUT_LEFT_BUTTON:
            self.trigger('move', x, y)
        elif self.pressed == GLUT_MIDDLE_BUTTON:
            self.translate(dx / 60.0, dy / 60.0, 0)
        else:
            pass
        glutPostRedisplay()
    self.mouse_loc = (x, y)


def handle_keystroke(self, key, x, screen_y):
    """ Called on keyboard input from the user """
    xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
    y = ySize - screen_y
    if key == 's':
        self.trigger('place', 'sphere', x, y)
    elif key == 'c':
        self.trigger('place', 'cube', x, y)
    elif key == GLUT_KEY_UP:
        self.trigger('scale', up=True)
    elif key == GLUT_KEY_DOWN:
        self.trigger('scale', up=False)
    elif key == GLUT_KEY_LEFT:
        self.trigger('rotate_color', forward=True)
    elif key == GLUT_KEY_RIGHT:
        self.trigger('rotate_color', forward=False)
    glutPostRedisplay()
```

#### 内部回调

在上述代码片段中，你会注意到当 `Interaction` 实例解释用户操作时，它会使用一个描述动作类型的字符串调用 `self.trigger`。`Interaction` 类上的 `trigger` 函数是我们将要用于处理应用程序级事件的简单回调系统的一部分。

回想一下，`Viewer` 类上的 `init_interaction` 函数通过调用 `register_callback` 在 `Interaction` 实例上注册回调。

```python
# class Interaction
def register_callback(self, name, func):
    self.callbacks[name].append(func)
```

当用户界面代码需要在场景上触发一个事件时，`Interaction` 类会调用它为该特定事件保存的所有回调：

```python
# class Interaction
def trigger(self, name, *args, **kwargs):
    for func in self.callbacks[name]:
        func(*args, **kwargs)
```

这个应用程序级的回调系统抽象了系统其他部分对操作系统输入的需要。每个应用程序级的回调都代表了应用程序内的一个有意义的请求。`Interaction` 类充当操作系统事件和应用程序级事件之间的翻译器。

这意味着，如果我们决定将建模器移植到除了 GLUT 之外的另一个工具包，我们只需要用一个将新工具包的输入转换为相同一组有意义的应用程序级回调的类来替换 `Interaction` 类。我们在下表中使用回调和参数。

| 回调             | 参数                       | 用途                    |
|:---------------|:-------------------------|:----------------------|
| `pick`         | x: 数字, y: 数字             | 选择鼠标指针位置处的节点。         |
| `move`         | x: 数字, y: 数字             | 将当前选中的节点移动到鼠标指针位置。    |
| `place`        | shape: 字符串, x: 数字, y: 数字 | 在鼠标指针位置放置指定类型的图形。     |
| `rotate_color` | forward: 布尔值             | 根据参数向前或向后旋转当前选中节点的颜色。 |
| `scale`        | up: 布尔值                  | 根据参数放大或缩小当前选中的节点。     |

这个简单的回调系统为我们的项目提供了所需的所有功能。然而，在一个生产级的 3D 建模器中，用户界面对象通常是动态创建和销毁的。在那种情况下，我们需要一个更复杂的事件监听系统，其中对象可以注册和注销事件的回调。

### 与场景交互

利用我们的回调机制，我们可以从 `Interaction` 类接收有关用户输入事件的有意义的信息。我们准备将这些操作应用到 `Scene`。

#### 移动场景

在这个项目中，我们通过变换场景来实现摄像机的移动。换句话说，摄像机位于一个固定位置，用户输入移动的是场景而不是摄像机。摄像机被放置在 `[0, 0, -15]`并面向世界空间的原点。（另外，我们可以通过改变透视矩阵来移动摄像机，而不是场景。这个设计决策对项目的其余部分影响很小。）

重新审视 `Viewer` 中的 `render` 函数，我们看到在渲染 `Scene` 之前使用 `Interaction` 状态来变换 OpenGL 矩阵状态。

与场景的交互有两种类型：旋转和翻译。

#### 使用轨迹球旋转场景

我们使用 *轨迹球* 算法来实现场景的旋转。轨迹球是操作三维场景的直观界面。
从概念上讲，轨迹球界面的工作原理就像场景位于一个透明的地球仪内部。将手放在地球仪表面并推动它会旋转地球仪。类似地，点击鼠标右键并在屏幕上移动它就会旋转场景。
你可以在 [OpenGL Wiki](http://www.opengl.org/wiki/Object_Mouse_Trackball) 上找到更多关于轨迹球理论的信息。
在这个项目中，我们使用了 [Glumpy](https://code.google.com/p/glumpy/source/browse/glumpy/trackball.py) 提供的轨迹球实现。

我们使用 `drag_to` 函数与轨迹球交云，将鼠标的当前位置作为起始位置，鼠标位置的变化作为参数。

```python
self.trackball.drag_to(self.mouse_loc[0], self.mouse_loc[1], dx, dy)
```

#### 场景旋转结果

旋转操作的结果矩阵是 `trackball.matrix`，在渲染场景时由视图使用。

#### 旁注：四元数

旋转传统上用两种方式之一表示。第一种是每个轴的旋转值；你可以将其存储为一个浮点数的三元组。

旋转的另一种常见表示是四元数，由一个向量组成，该向量具有 $x$、$y$ 和 $z$ 坐标，以及一个 $w$ 旋转。使用四元数比按轴旋转有许多好处；特别是，它们在数值上更稳定。使用四元数避免了像陀螺仪锁这样的问题。

四元数的缺点是它们不那么直观，更难以理解。如果你勇敢并且想更多地了解四元数，你可以查阅 [这个解释](http://3dgep.com/?p=1815)。

轨迹球实现通过在内部使用四元数来存储场景的旋转，从而避免了陀螺仪锁。幸运的是，我们不需要直接使用四元数，因为轨迹球上的矩阵成员将旋转转换为矩阵。

#### 平移场景

平移场景（即滑动它）比旋转它要简单得多。场景平移通过鼠标滚轮和左鼠标按钮提供。左鼠标按钮在 $x$ 和 $y$ 坐标中平移场景。滚动鼠标滚轮在 $z$ 坐标中平移场景（朝向或远离相机）。`Interaction` 类存储当前场景的平移，并使用 `translate` 函数进行修改。

在渲染期间，视图检索 `Interaction` 摄像机位置，以在 `glTranslated` 调用中使用。

#### 选择场景对象

现在用户可以移动和旋转整个场景以获得他们想要的视角，下一步是允许用户修改和操纵构成场景的对象。

为了让用户能够操纵场景中的对象，他们需要能够选择项目。

为了选择一个项目，我们使用当前的投影矩阵生成一个代表鼠标点击的射线，就好像鼠标指针向场景中发射了一个射线。被选择的节点是与射线相交且离相机最近的节点。

因此，选择问题归结为寻找射线与场景中节点相交的问题。那么问题来了：我们如何知道射线是否击中了一个节点？

精确计算射线是否与节点相交在代码复杂性和性能方面都是一个挑战。我们将需要为每种类型的原始体编写射线 - 对象交点检查。

对于具有复杂网格几何形状和许多面的节点，计算精确的射线 - 对象交点将需要测试射线与每个面的交点，这在计算上是昂贵的。

为了保持代码紧凑和合理的性能，我们使用一个简单、快速的射线 - 对象交点测试的近似方法。

在我们的实现中，每个节点存储一个轴对齐的边界框（AABB），这是它所占空间的近似。

为了测试射线是否与节点相交，我们测试射线是否与节点的 AABB 相交。这种实现意味着所有节点共享相同的交点测试代码，这意味着对于所有节点类型，性能成本是恒定且小的。

```python
# class Viewer
def get_ray(self, x, y):
    """ 
    Generate a ray beginning at the near plane, in the direction that
    the x, y coordinates are facing 

    Consumes: x, y coordinates of mouse on screen 
    Return: start, direction of the ray 
    """
    self.init_view()

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # get two points on the line.
    start = numpy.array(gluUnProject(x, y, 0.001))
    end = numpy.array(gluUnProject(x, y, 0.999))

    # convert those points into a ray
    direction = end - start
    direction = direction / norm(direction)

    return (start, direction)


def pick(self, x, y):
    """ Execute pick of an object. Selects an object in the scene. """
    start, direction = self.get_ray(x, y)
    self.scene.pick(start, direction, self.modelView)
```

为了确定哪个节点被点击，我们遍历场景以测试射线是否击中任何节点。我们取消选择当前选中的节点，然后选择与射线起点相交最近的节点。

```python
# class Scene
def pick(self, start, direction, mat):
    """ 
    Execute selection.
        
    start, direction describe a Ray. 
    mat is the inverse of the current modelview matrix for the scene.
    """
    if self.selected_node is not None:
        self.selected_node.select(False)
        self.selected_node = None

    # Keep track of the closest hit.
    mindist = sys.maxint
    closest_node = None
    for node in self.node_list:
        hit, distance = node.pick(start, direction, mat)
        if hit and distance < mindist:
            mindist, closest_node = distance, node

    # If we hit something, keep track of it.
    if closest_node is not None:
        closest_node.select()
        closest_node.depth = mindist
        closest_node.selected_loc = start + direction * mindist
        self.selected_node = closest_node
```

在 `Node` 类中，`pick` 函数测试射线是否与节点的轴对齐边界框（AABB）相交。

如果一个节点被选中，`select` 函数会切换节点的选中状态。

请注意，AABB 的 `ray_hit` 函数接受第三个参数，即盒子坐标空间和射线坐标空间之间的变换矩阵。每个节点在调用 `ray_hit` 函数之前都会将自己的变换应用到矩阵上。

```python
# class Node
def pick(self, start, direction, mat):
    """ 
    Return whether or not the ray hits the object

    Consume:  
    start, direction form the ray to check
    mat is the modelview matrix to transform the ray by 
    """

    # transform the modelview matrix by the current translation
    newmat = numpy.dot(
        numpy.dot(mat, self.translation_matrix),
        numpy.linalg.inv(self.scaling_matrix)
    )
    results = self.aabb.ray_hit(start, direction, newmat)
    return results


def select(self, select=None):
    """ Toggles or sets selected state """
    if select is not None:
        self.selected = select
    else:
        self.selected = not self.selected
```

在 `Node` 类中，`pick` 函数测试射线是否与节点的轴对齐边界框（AABB）相交。如果一个节点被选中，`select` 函数会切换节点的选中状态。

请注意，AABB 的 `ray_hit` 函数接受第三个参数，即盒子坐标空间和射线坐标空间之间的变换矩阵。每个节点在调用 `ray_hit` 函数之前都会将自己的变换应用到矩阵上。

#### 修改场景对象

接下来，我们希望允许用户操纵选中的节点。他们可能想要移动、调整大小或更改选中节点的颜色。当用户输入一个操作节点的命令时，`Interaction` 类将输入转换为用户意图的动作，并调用相应的回调。

当 `Viewer` 接收到这些事件之一的回调时，它会在 `Scene` 上调用适当的函数，该函数进而将变换应用于当前选中的 `Node`。

```python
# class Viewer
def move(self, x, y):
    """ Execute a move command on the scene. """
    start, direction = self.get_ray(x, y)
    self.scene.move_selected(start, direction, self.inverseModelView)


def rotate_color(self, forward):
    """ 
    Rotate the color of the selected Node. 
    Boolean 'forward' indicates direction of rotation. 
    """
    self.scene.rotate_selected_color(forward)


def scale(self, up):
    """ Scale the selected Node. Boolean up indicates scaling larger."""
    self.scene.scale_selected(up)
```

#### 更改颜色

通过一系列可能的颜色列表来实现颜色的操作。用户可以使用箭头键在列表中循环切换。场景会将颜色更改命令分派给当前选中的节点。

```python
# class Scene
def rotate_selected_color(self, forwards):
    """ Rotate the color of the currently selected node """
    if self.selected_node is None: return
    self.selected_node.rotate_color(forwards)
```

每个节点都存储着它当前的颜色。`rotate_color` 函数简单地修改节点的当前颜色。当节点被渲染时，颜色会通过 `glColor` 传递给 OpenGL。

```python
# class Node
def rotate_color(self, forwards):
    self.color_index += 1 if forwards else -1
    if self.color_index > color.MAX_COLOR:
        self.color_index = color.MIN_COLOR
    if self.color_index < color.MIN_COLOR:
        self.color_index = color.MAX_COLOR
```

#### 缩放节点

与更改颜色类似，如果存在选中的节点，场景会将所有缩放修改分派给该节点。

```python
# class Scene
def scale_selected(self, up):
    """ Scale the current selection """
    if self.selected_node is None: return
    self.selected_node.scale(up)
```

每个节点都存储着一个当前矩阵，该矩阵记录了它的缩放比例。一个按照参数 $x$、$y$ 和 $z$ 在各自方向上进行缩放的矩阵是：
$$
\begin{bmatrix}
x & 0 & 0 & 0 \\
0 & y & 0 & 0 \\
0 & 0 & z & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$
当用户修改节点的缩放比例时，得到的缩放矩阵会乘以节点的当前缩放矩阵。

```python
# class Node
def scale(self, up):
    s = 1.1 if up else 0.9
    self.scaling_matrix = numpy.dot(self.scaling_matrix, scaling([s, s, s]))
    self.aabb.scale(s)
```

函数 `scaling` 在给定 $x$、$y$ 和 $z$ 缩放因子的列表时，返回这样一个矩阵。

```python
def scaling(scale):
    s = numpy.identity(4)
    s[0, 0] = scale[0]
    s[1, 1] = scale[1]
    s[2, 2] = scale[2]
    s[3, 3] = 1
    return s
```

#### 移动节点

为了平移一个节点，我们使用与选择时相同的射线计算方法。我们将代表当前鼠标位置的射线传递给场景的 `move` 函数。节点的新位置应该在这条射线上。

为了确定在射线上的哪个位置放置节点，我们需要知道节点与相机的距离。由于我们在选择节点时（在 `pick`函数中）存储了节点的位置和与相机的距离，我们可以在这里使用这些数据。我们找到沿着目标射线与相机距离相同的点，并计算新旧位置之间的向量差。然后，我们根据得到的向量平移节点。

```python
# class Scene
def move_selected(self, start, direction, inv_modelview):
    """ 
    Move the selected node, if there is one.
        
    Consume: 
    start, direction describes the Ray to move to
    mat is the modelview matrix for the scene 
    """
    if self.selected_node is None: return

    # Find the current depth and location of the selected node
    node = self.selected_node
    depth = node.depth
    oldloc = node.selected_loc

    # The new location of the node is the same depth along the new ray
    newloc = (start + direction * depth)

    # transform the translation with the modelview matrix
    translation = newloc - oldloc
    pre_tran = numpy.array([translation[0], translation[1], translation[2], 0])
    translation = inv_modelview.dot(pre_tran)

    # translate the node and track its location
    node.translate(translation[0], translation[1], translation[2])
    node.selected_loc = newloc
```

请注意，新旧位置都是在相机坐标空间中定义的。我们需要将平移定义在世界坐标空间中。因此，我们通过乘以模型视图矩阵的逆矩阵，将相机空间的平移转换为世界空间的平移。

与缩放类似，每个节点都存储一个表示其平移的矩阵。平移矩阵看起来像这样：

$$
\begin{bmatrix}
1 & 0 & 0 & x \\
0 & 1 & 0 & y \\
0 & 0 & 1 & z \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

当节点被平移时，我们为当前的平移构造一个新的平移矩阵，并将其乘以节点的平移矩阵，以便在渲染期间使用。

```python
# class Node
def translate(self, x, y, z):
    self.translation_matrix = numpy.dot(
        self.translation_matrix,
        translation([x, y, z]))
```

当节点被平移时，我们为当前的平移构造一个新的平移矩阵，并将其乘以节点的平移矩阵，以便在渲染期间使用。

```python
def translation(displacement):
    t = numpy.identity(4)
    t[0, 3] = displacement[0]
    t[1, 3] = displacement[1]
    t[2, 3] = displacement[2]
    return t
```

#### 放置节点

节点放置结合了拾取和平移的技术。我们使用当前鼠标位置的相同射线计算来确定放置节点的位置。

```python
    # class Viewer
def place(self, shape, x, y):
    """ Execute a placement of a new primitive into the scene. """
    start, direction = self.get_ray(x, y)
    self.scene.place(shape, start, direction, self.inverseModelView)
```

为了放置一个新节点，我们首先创建相应类型节点的新实例，并将其添加到场景中。

我们希望将节点放置在用户光标的下方，因此我们在射线上找到一个点，该点距离相机是固定的。同样，射线在相机空间中表示，所以我们通过将其乘以模型视图矩阵的逆矩阵，将得到的平移向量转换为世界坐标空间。最后，我们根据计算出的向量平移新节点。

```python
    # class Scene
def place(self, shape, start, direction, inv_modelview):
    """ 
    Place a new node.
        
    Consume:  
    shape the shape to add
    start, direction describes the Ray to move to
    inv_modelview is the inverse modelview matrix for the scene 
    """
    new_node = None
    if shape == 'sphere':
        new_node = Sphere()
    elif shape == 'cube':
        new_node = Cube()
    elif shape == 'figure':
        new_node = SnowFigure()

    self.add_node(new_node)

    # place the node at the cursor in camera-space
    translation = (start + direction * self.PLACE_DEPTH)

    # convert the translation to world-space
    pre_tran = numpy.array([translation[0], translation[1], translation[2], 1])
    translation = inv_modelview.dot(pre_tran)

    new_node.translate(translation[0], translation[1], translation[2])
```

## 概述

恭喜！我们已经成功实现了一个小型 3D 建模器！

![](https://aosabook.org/en/500L/modeller-images/StartScene.png)

我们看到了如何开发一个可扩展的数据结构来表示场景中的对象。我们注意到，使用组合设计模式和基于树的数据结构，可以轻松地遍历场景以进行渲染，并允许我们添加新类型的节点而无需增加复杂性。我们利用这个数据结构将设计渲染到屏幕上，并在场景图的遍历中操作 OpenGL 矩阵。我们构建了一个非常简单的回调系统用于应用程序级事件，并用它来封装操作系统事件的处理。我们讨论了射线 -对象碰撞检测的可能实现方法，以及正确性、复杂性和性能之间的权衡。最后，我们实现了操作方法用于操纵场景的内容。

你可以在生产级的 3D 软件中找到这些相同的基本构建块。场景图结构和相对坐标空间在许多类型的 3D 图形应用程序中都有发现，从 CAD 工具到游戏引擎。这个项目的一个主要简化是在用户界面上。一个生产级的 3D 建模器预计将有一个完整的用户界面，这将需要一个比我们的简单回调系统更复杂的事件系统。

我们可以进行进一步的实验，为这个项目添加新功能。尝试以下之一：

* 添加一个 `Node` 类型来支持任意形状的三角形网格。
* 添加一个撤销栈，允许对建模操作进行撤销 / 重做。
* 使用如 DXF 这样的 3D 文件格式保存 / 加载设计。
* 集成渲染引擎：导出设计以用于真实感渲染器。
* 改进碰撞检测，实现准确的射线 - 对象交点。

## 进一步探索

为了更深入地了解现实世界的 3D 建模软件，一些开源项目很有趣。

[Blender](http://www.blender.org/) 是一个开源的全功能 3D 动画套件。它为视频特效制作或游戏创建提供了完整的 3D
管线。建模器只是这个项目中的一小部分，它是将建模器集成到大型软件套件中的一个很好的例子。

[OpenSCAD](http://www.openscad.org/) 是一个开源 3D 建模工具。它不是交互式的；相反，它读取一个脚本文件，指定如何生成场景。这给设计师提供了“对建模过程的完全控制”。

有关计算机图形学中算法和技术的更多信息，[Graphics Gems](http://tog.acm.org/resources/GraphicsGems/) 是一个很好的资源。


[^1]: 图片由 Dr. Anton Gerdelan 提供。他的 OpenGL 教程书籍可以在 [这里](http://antongerdelan.net/opengl/) 找到。