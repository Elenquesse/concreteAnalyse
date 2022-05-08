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
        # 这里应该按b、h、b1、h1、b2、h2顺序传入 单位mm
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
        """
        返回截面总面积

        :return: 截面面积，单位mm^2
        """
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
        """
        获取当前配筋钢筋面积

        :return: 钢筋总面积，单位mm^2
        """
        return self.area

    def get_force(self, strain: float):
        """
        获取钢筋当前内力

        :param strain: 钢筋应变值
        :return: 钢筋当前内力，单位N
        """
        return self.area * self.steel.get_stress(strain)


class CrossSection:
    # 20220427，突然意识到自己似乎没有办法在设计类的时候把混凝土和钢筋设计成两个同质化的类了，这是在设计材料包的时候没有的问题，就还挺有趣
    height_in_compression = None  # 压区高度，自截面顶部开始计算
    ec = None
    kappa = None

    def __init__(self, shape: Shape, concrete: material.Concrete, reinforce: SteelDistribution):
        self.shape = shape
        self.concrete = concrete
        self.steel_distribution = reinforce
        self.h0 = shape.h - reinforce.a0  # 截面有效高度，单位mm

    def set_section_state(self, kappa: float, max_strain_of_concrete: float):
        """
        设定截面状态，包括曲率和压区最大应变，相应更新压区高度

        :param kappa: 截面曲率，单位mm^-1
        :param max_strain_of_concrete: 压区混凝土最大应变
        :return: None
        """
        self.kappa = kappa
        self.ec = max_strain_of_concrete
        if kappa > 0:
            self.height_in_compression = max_strain_of_concrete / kappa

    def get_strain_at_height(self, h: float) -> float:
        """
        高度为 h 处应变，压正拉负

        :param h: 计算高度h，自截面最底部开始计算
        :return: h处应变，压应变为正，拉应变为负
        """
        height_of_zero_stress = self.shape.h - self.height_in_compression  # 自截面底部开始计算的中和轴位置
        return self.kappa * (h - height_of_zero_stress)

    def get_compression_force(self) -> tuple:
        """
        返回当前曲率和最大压应变下混凝土压力及作用位置（到中和轴）

        :return: (compression_force, compression_position)分别为混凝土压力合力与压力作用点（到中和轴距离）
        """
        split_num = 100
        dx = self.height_in_compression / split_num
        height_of_zero_stress = self.shape.h - self.height_in_compression  # 自截面底部开始计算的中和轴位置
        compression_force = 0
        compression_moment = 0
        for i in range(split_num):
            now_height = i * dx
            now_height_to_bottom = now_height + height_of_zero_stress
            now_strain = i * dx * self.kappa
            dc = self.shape.get_width_at_height(now_height_to_bottom) * dx * self.concrete.get_stress(now_strain)
            compression_force += dc
            compression_moment += dc * i * dx
        compression_position = compression_moment / compression_force
        return compression_force, compression_position

    def get_tension_force(self) -> tuple:
        # 当前曲率和最大压应变下混凝土截面拉力T及高度（到中和轴）
        # 简化编码，拉区按ft均布处理了
        if self.height_in_compression is not None:
            height_of_tension = self.concrete.et / self.kappa  # 使用曲率计算的开裂区长度
            max_tension_height = self.shape.h - self.height_in_compression  # 使用曲率最大压应变计算的拉区最大高度
            height_of_tension = height_of_tension if height_of_tension <= max_tension_height else max_tension_height
            position_of_crack = max_tension_height - height_of_tension
            area_in_tension = \
                self.shape.get_area_below(max_tension_height) - self.shape.get_area_below(position_of_crack)
            return area_in_tension * self.concrete.ft, height_of_tension

    def get_tension_force_of_steel(self) -> tuple:
        # 钢筋力及位置，位置到中和轴
        height_of_zero_stress = self.shape.h - self.height_in_compression
        strain_of_steel = self.kappa * (height_of_zero_stress - self.steel_distribution.a0)
        return self.steel_distribution.get_force(strain_of_steel), height_of_zero_stress - self.steel_distribution.a0


if __name__ == "__main__":
    default_shape = Shape(TypeOfShape.Rectangle, [250, 500])  # 宽 250 高 500 的矩形截面
    sd = SteelDistribution(material.Steel(material.SteelGrade.HPB300), 4, 20, 35)  # 4根 HPB300 钢筋，直径20，距离下边缘35
    cs_concrete = material.Concrete(material.ConcreteGrade.C30)  # C30混凝土
    cross_section = CrossSection(default_shape, cs_concrete, sd)  # 生成截面

    cross_section.set_section_state(2.475*(10**-5), 0.0033)
    print(cross_section.height_in_compression)
    print(cross_section.get_tension_force_of_steel())
    print(cross_section.get_tension_force())
    print(cross_section.get_compression_force())
