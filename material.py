from enum import IntEnum, Enum
from math import fabs


ELASTIC_MODULES_OF_STEEL = 20000


class SteelGrade(IntEnum):
    HPB300 = 300
    HRB335 = 335
    HRB400 = 400
    HRBF400 = 400
    RRB400 = 400
    HRB500 = 500
    HRBF500 = 500


class ConcreteGrade(Enum):
    C30 = {"fck": 30, "n": 2, "e0": 0.002, "eu": 0.0033, "ft": 1, "ec": 1}
    C40 = {"fck": 40, "n": 2, "e0": 0.002, "eu": 0.0033, "ft": 1, "ec": 1}
    C50 = {"fck": 50, "n": 2, "e0": 0.002, "eu": 0.0033, "ft": 1, "ec": 1}
    C60 = {"fck": 60, "n": 1.83, "e0": 0.00205, "eu": 0.0032, "ft": 1, "ec": 1}
    C70 = {"fck": 70, "n": 1.67, "e0": 0.00210, "eu": 0.0031, "ft": 1, "ec": 1}
    C80 = {"fck": 80, "n": 1.50, "e0": 0.00215, "eu": 0.0030, "ft": 1, "ec": 1}


class Steel:
    def __init__(self, grade: SteelGrade):
        self.__yield_stress = grade
        self.__yield_strain = grade / ELASTIC_MODULES_OF_STEEL

    def get_stress(self, strain: float) -> float:
        strain = fabs(strain)
        return self.__yield_stress if strain >= self.__yield_strain else ELASTIC_MODULES_OF_STEEL * strain


class Concrete:
    def __init__(self, grade: ConcreteGrade):
        self.__fck = grade.value["fck"]
        self.__fc = self.__fck
        self.__n = grade.value["n"]
        self.__e0 = grade.value["e0"]
        self.__eu = grade.value["eu"]
        self.ec = grade.value["ec"]
        self.ft = grade.value["ft"]
        self.et = 2 * grade.value["ft"] / self.ec

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
