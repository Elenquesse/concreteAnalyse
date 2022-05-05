from enum import IntEnum, Enum
from math import fabs


# 钢材弹性模量，都按定值 200000MPa 取了
ELASTIC_MODULES_OF_STEEL = 200000


class SteelGrade(IntEnum):
    HPB300 = 300
    HRB335 = 335
    HRB400 = 400
    HRBF400 = 400
    RRB400 = 400
    HRB500 = 500
    HRBF500 = 500


class ConcreteGrade(Enum):
    C30 = {"fc": 14.3, "n": 2, "e0": 0.002, "eu": 0.0033, "ft": 1.43, "ec": 30000}
    C40 = {"fc": 19.1, "n": 2, "e0": 0.002, "eu": 0.0033, "ft": 1.71, "ec": 32500}
    C50 = {"fc": 23.1, "n": 2, "e0": 0.002, "eu": 0.0033, "ft": 1.89, "ec": 34500}
    C60 = {"fc": 27.5, "n": 1.83, "e0": 0.00205, "eu": 0.0032, "ft": 2.04, "ec": 36000}
    C70 = {"fc": 31.8, "n": 1.67, "e0": 0.00210, "eu": 0.0031, "ft": 2.14, "ec": 37000}
    C80 = {"fc": 35.9, "n": 1.50, "e0": 0.00215, "eu": 0.0030, "ft": 2.22, "ec": 38000}


class Steel:
    def __init__(self, grade: SteelGrade):
        self.__yield_stress = grade
        self.__yield_strain = grade / ELASTIC_MODULES_OF_STEEL

    def get_stress(self, strain: float) -> float:
        strain = fabs(strain)
        return self.__yield_stress if strain >= self.__yield_strain else ELASTIC_MODULES_OF_STEEL * strain


class Concrete:
    def __init__(self, grade: ConcreteGrade):
        self.__fc = grade.value["fc"]  # 轴心抗压强度 MPa
        self.__n = grade.value["n"]  # 应力应变关系参数
        self.__e0 = grade.value["e0"]  # 应力应变关系参数
        self.__eu = grade.value["eu"]  # 极限应变
        self.ec = grade.value["ec"]  # 弹性模量 MPa
        self.ft = grade.value["ft"]  # 抗拉强度 MPa
        self.et = 2 * grade.value["ft"] / self.ec  # 开裂应变

    def get_stress(self, strain: float) -> float:
        # 压区正应变
        if strain >= 0:
            if strain <= self.__e0:
                return self.__fc * (1 - (1 - strain / self.__e0) ** self.__n)
            else:
                if strain <= self.__eu:
                    return self.__fc
                else:
                    return 0
