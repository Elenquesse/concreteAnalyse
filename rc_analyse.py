import cross_section
from cross_section import TypeOfShape as tos
import material
from material import SteelGrade as sd
from material import  ConcreteGrade as cd
import pandas as pd

# 截面形状、钢筋牌号、混凝土强度等级由数字向类的映射
SHAPE_DICT = (tos.Rectangle, tos.T_shape, tos.I_shape)
STEEL_DICT = (sd.HPB300, sd.HRB335, sd.HRB400, sd.HRBF400, sd.RRB400, sd.HRB500, sd.HRBF500)
CONCRETE_DICT = {
    30: cd.C30,
    40: cd.C40,
    50: cd.C50,
    60: cd.C60,
    70: cd.C70,
    80: cd.C80
}


def analyse_strain(cs: cross_section.CrossSection, given_kappa: float) -> tuple:
    l = 0
    r = cs.concrete.eu
    while l < r:
        mid = (l + r) / 2
        cs.set_section_state(given_kappa, mid)
        concrete_tension, tension_position = cs.get_tension_force()
        compression, compression_position = cs.get_compression_force()
        steel_force, steel_position = cs.get_tension_force_of_steel()
        tension = concrete_tension + steel_force
        e = tension - compression
        if 0 <= e <= 1:
            moment = concrete_tension * tension_position + compression * compression_position + \
                     steel_force * steel_position
            # print(cs.get_tension_force_of_steel())
            # print(cs.kappa * (cs.height_in_compression - cs.steel_distribution.a0))
            return mid, moment
        if e > 1:
            l = mid
        else:
            r = mid
    return -1, -1


def analyse_section(shape_type: int, shape_para: list, steel_type: int, steel_para: list, concrete_grade: int) -> tuple:
    """
    根据给定的截面和钢筋情况分析弯矩-曲率曲线

    :param shape_type: 截面形状类型，0为矩形，1为T形，2为I形，后两种TODO
    :param shape_para: 相应界面参数，根据截面类型应有不同数量
    :param steel_type: 钢筋类型
    :param steel_para: 钢筋分布参数：数量、直径（mm）、距离截面底部距离（mm）
    :param concrete_grade: 混凝土强度等级
    :return: tuple，其中为两个list，第一个为曲率（1/mm），第二个为对应弯矩（N·mm）
    """
    shape = cross_section.Shape(SHAPE_DICT[shape_type], shape_para)

    steel_grade = material.Steel(STEEL_DICT[steel_type])
    _sd = cross_section.SteelDistribution(steel_grade, steel_para[0], steel_para[1], steel_para[2])

    _cs_concrete = material.Concrete(CONCRETE_DICT[concrete_grade])
    cs = cross_section.CrossSection(shape, _cs_concrete, _sd)

    _mo = []
    _ka = []
    ec = 0
    i = 1
    while True:
        ec, m = analyse_strain(cs, i * (10 ** -8))
        if ec != -1:
            _mo.append(m)
            _ka.append(i)
            i += 1
            # debug
            # if i%10==0:
            #     print(i)
        else:
            break
    return _ka, _mo


if __name__ == "__main__":
    # default_shape = cross_section.Shape(cross_section.TypeOfShape.Rectangle, [250, 500])  # 宽 250 高 500 的矩形截面
    # # 4根 HPB300 钢筋，直径20，距离下边缘35
    # sd = cross_section.SteelDistribution(material.Steel(material.SteelGrade.HPB300), 4, 20, 35)
    # cs_concrete = material.Concrete(material.ConcreteGrade.C30)  # C30混凝土
    # cross_section = cross_section.CrossSection(default_shape, cs_concrete, sd)  # 生成截面
    #
    # # print(analyse_strain(cross_section, 5.8*(10**-6)))
    #
    # mo = []
    # ka = []
    # for i in range(1, 24000):
    #     t = analyse_strain(cross_section, i*(10**-9))
    #     if t is not None:
    #         _, m = t
    #         mo.append(m)
    #         ka.append(i)
    #     if i % 100 == 0:
    #         print(i)
    # df = pd.DataFrame({
    #     "mo": mo,
    #     "ka": ka
    # })
    # df.to_csv("1.csv")

    ka, mo = analyse_section(0, [250, 500], 0, [4, 20, 35], 30)
    df = pd.DataFrame({
        "mo": mo,
        "ka": ka
    })
    df.to_csv("1.csv")
