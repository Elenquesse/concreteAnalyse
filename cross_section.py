from enum import IntEnum, Enum
import material

PI = 3.14159


class TypeOfShape(Enum):
    Rectangle = 2
    T_shape = 4
    I_shape = 6


def _get_area_of_rectangle(b, h):
    return b * h


def _get_area_of_t_shape(b, h, b1, h1):
    return b * (h - h1) + b1 * h1


def _get_area_of_i_shape(b, h, b1, h1, b2, h2):
    return b * (h - h1 - h2) + b1 * h1 + b2 * h2


class Shape:
    def __init__(self, type_of_shape: TypeOfShape, shape_values: list):
        self.type_of_shape = type_of_shape
        # 这里应该按b、h、b1、h1、b2、h2顺序传入
        if type_of_shape is TypeOfShape.Rectangle:
            self.b, self.h = shape_values
            self._area = _get_area_of_rectangle(self.b, self.h)
        if type_of_shape is TypeOfShape.T_shape:
            self.b, self.h, self.b1, self.h1 = shape_values
            self._area = _get_area_of_t_shape(self.b, self.h, self.b1, self.h1)
        if type_of_shape is TypeOfShape.I_shape:
            self.b, self.h, self.b1, self.h1, self.b2, self.h2 = shape_values
            self._area = _get_area_of_i_shape(self.b, self.h, self.b1, self.h1, self.b2, self.h2)

    def get_area(self):
        return self._area

    # TODO: 下面俩函数都需要补完T截面和I截面的，测试暂时只用矩形截面吧
    def get_width_at_height(self, h: float) -> float:
        if self.type_of_shape is TypeOfShape.Rectangle:
            return self.b

    def get_area_below(self, x: float):
        if self.type_of_shape is TypeOfShape.Rectangle:
            return self._area if x >= self.h else x * self.b


class SteelDistribution:
    def __init__(self, steel: material.Steel, n: int, phi: float, a: float):
        self.steel = steel
        self._n = n
        self._phi = phi
        self.a0 = a
        self.area = self._n * PI * (self._phi ** 2) / 4

    def get_area(self):
        return self.area

    def get_force(self, strain: float):
        return self.area * self.steel.get_stress(strain)


class CrossSection:
    # 20220427，突然意识到自己似乎没有办法在设计类的时候把混凝土和钢筋设计成两个同质化的类了，这是在设计材料包的时候没有的问题，就还挺有趣
    height_of_zero_stress = None
    ec = None
    kappa = None

    def __init__(self, shape: Shape, concrete: material.Concrete, reinforce: SteelDistribution):
        self.shape = shape
        self.concrete = concrete
        self.steel_distribution = reinforce
        # self.rho = reinforce.area / shape.get_area()  配筋率好像不太用的到
        self.h0 = shape.h - reinforce.a0

    def set_section_state(self, kappa: float, max_strain_of_concrete: float):
        # 设定截面状态：斜率和压区混凝土最大压应变
        self.kappa = kappa
        self.ec = max_strain_of_concrete
        if kappa > 0:
            self.height_of_zero_stress = max_strain_of_concrete / kappa

    def get_strain_at_height(self, h: float) -> float:
        # 高度为h处应变，压正拉负
        height_in_compression = self.h0 - self.height_of_zero_stress
        return self.kappa * (h - height_in_compression)

    def get_compression_force(self) -> tuple:
        # 返回当前曲率和最大压应变下压力
        pass

    def get_tension_force(self) -> tuple:
        # 当前曲率和最大压应变下混凝土截面拉力T及高度（到中和轴）
        # 简化编码，拉区按ft均布处理了
        if self.height_of_zero_stress is not None:
            height_of_tension = self.concrete.et / self.kappa
            height_of_tension = height_of_tension if height_of_tension <= self.height_of_zero_stress \
                else self.height_of_zero_stress
            area_in_tension = (self.shape.get_area_below(self.height_of_zero_stress)
                               - self.shape.get_area_below(height_of_tension))
            return area_in_tension * self.concrete.ft, height_of_tension / 2

    def get_tension_force_of_steel(self) -> float:
        strain_of_steel = self.kappa * (self.height_of_zero_stress - self.steel_distribution.a0)
        return self.steel_distribution.get_force(strain_of_steel)
