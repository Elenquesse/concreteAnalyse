import cross_section
import material
import pandas as pd


def analyse_strain(cs: cross_section.CrossSection, given_kappa: float) -> tuple:
    l = 0
    r = cs.concrete.eu
    while (r - l) > 0.000001:
        mid = (l + r) / 2
        cs.set_section_state(given_kappa, mid)
        concrete_tension, tension_position = cs.get_tension_force()
        compression, compression_position = cs.get_compression_force()
        steel_force, steel_position = cs.get_tension_force_of_steel()
        tension = concrete_tension + steel_force
        e = (tension - compression) / tension
        if 0 <= e <= 0.001:
            moment = concrete_tension * tension_position + compression * compression_position + \
                steel_force * steel_position
            return mid, moment
        if e > 0.001:
            l = mid
        else:
            r = mid


if __name__ == "__main__":
    default_shape = cross_section.Shape(cross_section.TypeOfShape.Rectangle, [250, 500])  # 宽 250 高 500 的矩形截面
    # 4根 HPB300 钢筋，直径20，距离下边缘35
    sd = cross_section.SteelDistribution(material.Steel(material.SteelGrade.HPB300), 4, 20, 35)
    cs_concrete = material.Concrete(material.ConcreteGrade.C30)  # C30混凝土
    cross_section = cross_section.CrossSection(default_shape, cs_concrete, sd)  # 生成截面

    mo = []
    ka = []
    for i in range(1, 24000):
        t = analyse_strain(cross_section, i*(10**-9))
        if t is not None:
            _, m = t
            mo.append(m)
            ka.append(i)
        if i % 100 == 0:
            print(i)
    df = pd.DataFrame({
        "mo": mo,
        "ka": ka
    })
    df.to_csv("1.csv")
