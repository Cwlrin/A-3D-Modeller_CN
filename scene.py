class Scene(object):
    # 放置节点的深度，放置的节点距离摄像机15个单位
    PLACE_DEPTH = 15.0

    def __init__(self):
        # 场景下的节点队列
        self.node_list = list()
        self.selected_node = None

    def add_node(self, node):
        """ 在场景中加入一个新节点 """
        self.node_list.append(node)

    def render(self):
        """ 遍历场景下所有节点并渲染 """
        for node in self.node_list:
            node.render()

    # Scene 下实现
    def pick(self, start, direction, mat):
        """ 参数中的 mat 为当前 ModelView 的逆矩阵，作用是计算激光在局部（对象）坐标系中的坐标 """
        import sys

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