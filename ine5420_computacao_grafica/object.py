from abc import abstractmethod
from ine5420_computacao_grafica.matrixTransform import MatrixTransform2D
import numpy as np
import math


# classe que define um objeto basico do universo de representacao
class Object:

    # int id;
    # string name_, type_;

    def __init__(self, obj_id, name, obj_type):
        self.id = obj_id
        self.name = name
        self.type = obj_type
        self.visible = True

    # metodo abstrato que define a maneira como o objeto eh desenhado na tela
    @abstractmethod
    def draw(self, transform, da_width, da_height, cairo):
        pass

    @abstractmethod
    def update_scn(self, transform):
        pass

    @abstractmethod
    def translate(self, vec):
        pass

    @abstractmethod
    def rotate(self, vec):
        pass

    @abstractmethod
    def scale(self, amount):
        pass

    @abstractmethod
    def clip(self):
        pass

# end of class Object


# classe que define um ponto basico no universo de representacao
class Point2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
# end of class Point

class Point3D:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

# classe que define uma linha basica dentro do universo de representacao
class Line:
    def __init__(self, start: Point2D, end: Point2D):
        self.start = start
        self.end = end
# end of class Line


# classe que representa um poligono generico
class Polygon:

    # list points_;

    def __init__(self, points):
        self.points = points
# end of class Polygon


class DrawablePoint2D(Point2D, Object):
    def __init__(self, obj_id, name, x, y):
        # Object constructor
        Object.__init__(self, obj_id, name, "Point")
        # Constructor of Point
        Point2D.__init__(self, x, y)
        self.nx = x
        self.ny = y

    # implementacao do metodo abstrato definido em Object
    def update_scn(self, transform):
        [self.nx, self.ny, _] = np.array(
                ([self.x, self.y, 1]), dtype=float).dot(transform)

    # implementacao do metodo abstrato definido em Object
    def draw(self, transform: np.array, cairo):
        [vx, vy, _] = np.array(
                ([self.nx, self.ny, 1]), dtype=float).dot(transform)
        cairo.arc(vx, vy, 2, 0, 2*math.pi)
        cairo.fill()

    def translate(self, vec):
        self.x += vec.x
        self.y += vec.y

    def rotate(self, angle):
        pass

    def scale(self, amount):
        pass
# end of class DrawablePoint


class DrawableLine(Line, Object):

    # Point firstP_, lastP_;

    # construtor
    def __init__(self, obj_id, name, start, end):
        # constructor of Object
        Object.__init__(self, obj_id, name, "Line")
        # constructor of Line
        Line.__init__(self, start, end)
        self.scn = Line(Point2D(0, 0), Point2D(0, 0))

    # implementacao do metodo abstrato definido em Object
    def update_scn(self, transform):
        [self.scn.start.x, self.scn.start.y, _] = np.array(
                ([self.start.x, self.start.y, 1]),
                dtype=float).dot(transform)
        [self.scn.end.x, self.scn.end.y, _] = np.array(
                ([self.end.x, self.end.y, 1]),
                dtype=float).dot(transform)

    # implementacao do metodo abstrato definido em Object
    def draw(self, transform: np.array, cairo):
        # print(transform)
        [v_start_x, v_start_y, _] = np.array(
                ([self.scn.start.x, self.scn.start.y, 1]),
                dtype=float).dot(transform)
        [v_end_x, v_end_y, _] = np.array(
                ([self.scn.end.x, self.scn.end.y, 1]),
                dtype=float).dot(transform)
        cairo.save()
        cairo.move_to(v_start_x, v_start_y)
        cairo.line_to(v_end_x, v_end_y)
        cairo.stroke()
        cairo.restore()

    def translate(self, vec):
        self.start.x += vec.x
        self.start.y += vec.y
        self.end.x += vec.x
        self.end.y += vec.y

    def rotate(self, angle):
        def get_center():
            cx = (self.start.x + self.end.x) / 2
            cy = (self.start.y + self.end.y) / 2
            return Point2D(cx, cy)
        
        center = get_center()
        mtr = MatrixTransform2D()
        mtr.translate(-center.x, -center.y)
        mtr.rotate(angle)
        mtr.translate(center.x, center.y)
        [self.start.x, self.start.y, _] = np.array(
            [self.start.x, self.start.y, 1], dtype=float
        ) @ mtr.tr
        [self.end.x, self.end.y, _] = np.array(
            [self.end.x, self.end.y, 1], dtype=float
        ) @ mtr.tr

    def scale(self, amount):
        def get_center():
            cx = (self.start.x + self.end.x) / 2
            cy = (self.start.y + self.end.y) / 2
            return Point2D(cx, cy)
        
        center = get_center()
        mtr = MatrixTransform2D()
        mtr.translate(-center.x, -center.y)
        mtr.scale(amount, amount)
        mtr.translate(center.x, center.y)
        [self.start.x, self.start.y, _] = np.array(
            [self.start.x, self.start.y, 1], dtype=float
        ) @ mtr.tr
        [self.end.x, self.end.y, _] = np.array(
            [self.end.x, self.end.y, 1], dtype=float
        ) @ mtr.tr

# end of class DrawableLine


class DrawablePolygon(Polygon, Object):
    def __init__(self, obj_id, name, points):
        Object.__init__(self, obj_id, name, "Polygon")
        Polygon.__init__(self, points)
        self.scn = []

    # implementacao do metodo abstrato definido em Object
    def update_scn(self, transform):
        for index, point in enumerate(self.scn):
            [point.start.x, point.start.y, _] = np.array(
                    ([self.points[index].start.x, self.points[index].start.y, 1]),
                    dtype=float).dot(transform)

    # implementacao do metodo abstrato definido em Object
    def draw(self, transform_x, transform_y, cairo):
        cairo.save()
        cairo.move_to(
            transform_x(self.points[0].x),
            transform_y(self.points[0].y)
        )
        for i in range(1, len(self.points)):
            cairo.line_to(
                transform_x(self.points[i].x),
                transform_y(self.points[i].y)
            )

        cairo.line_to(
            transform_x(self.points[0].x),
            transform_y(self.points[0].y)
        )
        cairo.stroke_preserve()
        # cairo.restore()

    def translate(self, vec):
        for i in range(self.points):
            self.points[i].x += vec.x
            self.points[i].y += vec.y

    def rotate(self, angle):
        def get_center():
            cx = 0
            cy = 0
            for point in self.points:
                cx += point.x
                cy += point.y
            cx /= len(self.points)
            cy /= len(self.points)
            return Point2D(cx, cy)
        
        center = get_center()
        mtr = MatrixTransform2D()
        mtr.translate(-center.x, -center.y)
        mtr.rotate(angle)
        mtr.translate(center.x, center.y)

        for point in self.points:
            [point.x, point.y, _] = np.array(
                [point.x, point.y, 1], dtype=float
            ) @ mtr.tr
    
    def scale(self, amount):
        def get_center():
            cx = 0
            cy = 0
            for point in self.points:
                cx += point.x
                cy += point.y
            cx /= len(self.points)
            cy /= len(self.points)
            return Point2D(cx, cy)

        center = get_center()
        mtr = MatrixTransform2D()
        mtr.translate(-center.x, -center.y)
        mtr.scale(amount, amount)
        mtr.translate(center.x, center.y)

        for point in self.points:
            [point.x, point.y, _] = np.array(
                [point.x, point.y, 1], dtype=float
            ) @ mtr.tr