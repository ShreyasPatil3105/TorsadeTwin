#!/usr/bin/env python
#
# Generated on 2026-09-13 20:20:12
#
import math

#
# Components and variables
#

class CCamk:
    def __init__(self):
        self.CaMKa = None
        self.CaMKb = None
        self.CaMKo = None
        self.CaMKt = None
        self.d_camkt = None
        self.KmCaM = None
        self.KmCaMK = None
        self.aCaMK = None
        self.bCaMK = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.CaMKo = 0.05
        self.KmCaM = 0.0015
        self.KmCaMK = 0.15
        self.aCaMK = 0.05
        self.bCaMK = 0.00068
    def init(self):
        """
        Resets the state variables to their initial values
        """
        self.CaMKt =  1.25840446999999998e-02
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.CaMKb = self.CaMKo * (1.0 - self.CaMKt) / (1.0 + self.KmCaM / c_intracellular_ions.cass)
        self.CaMKa = self.CaMKb + self.CaMKt
        self.d_camkt = self.aCaMK * self.CaMKb * (self.CaMKb + self.CaMKt) - self.bCaMK * self.CaMKt

class CIpca:
    def __init__(self):
        self.GpCa = None
        self.IpCa_IpCa = None
        self.KmCap = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.GpCa = 0.0005
        self.KmCap = 0.0005
    def init(self):
        """
        Resets the state variables to their initial values
        """
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.IpCa_IpCa = self.GpCa * c_intracellular_ions.cai / (self.KmCap + c_intracellular_ions.cai)

class CCell_geometry:
    def __init__(self):
        self.Acap = None
        self.Ageo = None
        self.L = None
        self.rad = None
        self.vcell = None
        self.vjsr = None
        self.vmyo = None
        self.vnsr = None
        self.vss = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.L = 0.01
        self.rad = 0.0011
        self.Ageo = 2.0 * 3.14 * self.rad * self.rad + 2.0 * 3.14 * self.rad * self.L
        self.vcell = 1000.0 * 3.14 * self.rad * self.rad * self.L
        self.Acap = 2.0 * self.Ageo
        self.vjsr = 0.0048 * self.vcell
        self.vmyo = 0.68 * self.vcell
        self.vnsr = 0.0552 * self.vcell
        self.vss = 0.02 * self.vcell
    def init(self):
        """
        Resets the state variables to their initial values
        """
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        pass

class CDiff:
    def __init__(self):
        self.Jdiff = None
        self.JdiffK = None
        self.JdiffNa = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
    def init(self):
        """
        Resets the state variables to their initial values
        """
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.Jdiff = (c_intracellular_ions.cass - c_intracellular_ions.cai) / 0.2
        self.JdiffK = (c_intracellular_ions.kss - c_intracellular_ions.ki) / 2.0
        self.JdiffNa = (c_intracellular_ions.nass - c_intracellular_ions.nai) / 2.0

class CEnvironment:
    def __init__(self):
        self.celltype = None
        self.time = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.celltype = 0.0
    def init(self):
        """
        Resets the state variables to their initial values
        """
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        c_environment.time = engine.time

class CExtracellular:
    def __init__(self):
        self.cao = None
        self.ko = None
        self.nao = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.cao = 1.8
        self.ko = 5.4
        self.nao = 140.0
    def init(self):
        """
        Resets the state variables to their initial values
        """
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        pass

class CPhysical_constants:
    def __init__(self):
        self.F = None
        self.R = None
        self.T = None
        self.zca = None
        self.zk = None
        self.zna = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.F = 96485.0
        self.R = 8314.0
        self.T = 310.0
        self.zca = 2.0
        self.zk = 1.0
        self.zna = 1.0
    def init(self):
        """
        Resets the state variables to their initial values
        """
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        pass

class CTrans_flux:
    def __init__(self):
        self.Jtr = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
    def init(self):
        """
        Resets the state variables to their initial values
        """
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.Jtr = (c_intracellular_ions.cansr - c_intracellular_ions.cajsr) / 100.0

class CInaca_i:
    def __init__(self):
        self.E1_i = None
        self.E1_ss = None
        self.E2_i = None
        self.E2_ss = None
        self.E3_i = None
        self.E3_ss = None
        self.E4_i = None
        self.E4_ss = None
        self.Gncx = None
        self.Gncx_b = None
        self.INaCa_i_INaCa_i = None
        self.INaCa_ss = None
        self.JncxCa_i = None
        self.JncxCa_ss = None
        self.JncxNa_i = None
        self.JncxNa_ss = None
        self.KmCaAct = None
        self.allo_i = None
        self.allo_ss = None
        self.h10_i = None
        self.h10_ss = None
        self.h11_i = None
        self.h11_ss = None
        self.h12_i = None
        self.h12_ss = None
        self.h1_i = None
        self.h1_ss = None
        self.h2_i = None
        self.h2_ss = None
        self.h3_i = None
        self.h3_ss = None
        self.h4_i = None
        self.h4_ss = None
        self.h5_i = None
        self.h5_ss = None
        self.h6_i = None
        self.h6_ss = None
        self.h7_i = None
        self.h7_ss = None
        self.h8_i = None
        self.h8_ss = None
        self.h9_i = None
        self.h9_ss = None
        self.hca = None
        self.hna = None
        self.k1_i = None
        self.k1_ss = None
        self.k2_i = None
        self.k2_ss = None
        self.k3_i = None
        self.k3_ss = None
        self.k3p_i = None
        self.k3p_ss = None
        self.k3pp_i = None
        self.k3pp_ss = None
        self.k4_i = None
        self.k4_ss = None
        self.k4p_i = None
        self.k4p_ss = None
        self.k4pp_i = None
        self.k4pp_ss = None
        self.k5_i = None
        self.k5_ss = None
        self.k6_i = None
        self.k6_ss = None
        self.k7_i = None
        self.k7_ss = None
        self.k8_i = None
        self.k8_ss = None
        self.kasymm = None
        self.kcaoff = None
        self.kcaon = None
        self.kna1 = None
        self.kna2 = None
        self.kna3 = None
        self.qca = None
        self.qna = None
        self.wca = None
        self.wna = None
        self.wnaca = None
        self.x1_i = None
        self.x1_ss = None
        self.x2_i = None
        self.x2_ss = None
        self.x3_i = None
        self.x3_ss = None
        self.x4_i = None
        self.x4_ss = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.Gncx_b = 0.0008
        self.KmCaAct = 0.00015
        self.kasymm = 12.5
        self.kcaoff = 5000.0
        self.kcaon = 1500000.0
        self.kna1 = 15.0
        self.kna2 = 5.0
        self.kna3 = 88.12
        self.qca = 0.167
        self.qna = 0.5224
        self.wca = 60000.0
        self.wna = 60000.0
        self.wnaca = 5000.0
        self.Gncx = (self.Gncx_b * 1.1 if (c_environment.celltype == 1.0) else (self.Gncx_b * 1.4 if (c_environment.celltype == 2.0) else self.Gncx_b))
        self.h10_i = self.kasymm + 1.0 + c_extracellular.nao / self.kna1 * (1.0 + c_extracellular.nao / self.kna2)
        self.h10_ss = self.kasymm + 1.0 + c_extracellular.nao / self.kna1 * (1.0 + c_extracellular.nao / self.kna2)
        self.k2_i = self.kcaoff
        self.k2_ss = self.kcaoff
        self.k5_i = self.kcaoff
        self.k5_ss = self.kcaoff
        self.h11_i = c_extracellular.nao * c_extracellular.nao / (self.h10_i * self.kna1 * self.kna2)
        self.h11_ss = c_extracellular.nao * c_extracellular.nao / (self.h10_ss * self.kna1 * self.kna2)
        self.h12_i = 1.0 / self.h10_i
        self.h12_ss = 1.0 / self.h10_ss
        self.k1_i = self.h12_i * c_extracellular.cao * self.kcaon
        self.k1_ss = self.h12_ss * c_extracellular.cao * self.kcaon
    def init(self):
        """
        Resets the state variables to their initial values
        """
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.allo_i = 1.0 / (1.0 + (self.KmCaAct / c_intracellular_ions.cai)**2.0)
        self.allo_ss = 1.0 / (1.0 + (self.KmCaAct / c_intracellular_ions.cass)**2.0)
        self.h4_i = 1.0 + c_intracellular_ions.nai / self.kna1 * (1.0 + c_intracellular_ions.nai / self.kna2)
        self.h4_ss = 1.0 + c_intracellular_ions.nass / self.kna1 * (1.0 + c_intracellular_ions.nass / self.kna2)
        self.hca = math.exp(self.qca * c_membrane.v * c_physical_constants.F / (c_physical_constants.R * c_physical_constants.T))
        self.hna = math.exp(self.qna * c_membrane.v * c_physical_constants.F / (c_physical_constants.R * c_physical_constants.T))
        self.h1_i = 1.0 + c_intracellular_ions.nai / self.kna3 * (1.0 + self.hna)
        self.h1_ss = 1.0 + c_intracellular_ions.nass / self.kna3 * (1.0 + self.hna)
        self.h5_i = c_intracellular_ions.nai * c_intracellular_ions.nai / (self.h4_i * self.kna1 * self.kna2)
        self.h5_ss = c_intracellular_ions.nass * c_intracellular_ions.nass / (self.h4_ss * self.kna1 * self.kna2)
        self.h6_i = 1.0 / self.h4_i
        self.h6_ss = 1.0 / self.h4_ss
        self.h7_i = 1.0 + c_extracellular.nao / self.kna3 * (1.0 + 1.0 / self.hna)
        self.h7_ss = 1.0 + c_extracellular.nao / self.kna3 * (1.0 + 1.0 / self.hna)
        self.h2_i = c_intracellular_ions.nai * self.hna / (self.kna3 * self.h1_i)
        self.h2_ss = c_intracellular_ions.nass * self.hna / (self.kna3 * self.h1_ss)
        self.h3_i = 1.0 / self.h1_i
        self.h3_ss = 1.0 / self.h1_ss
        self.h8_i = c_extracellular.nao / (self.kna3 * self.hna * self.h7_i)
        self.h8_ss = c_extracellular.nao / (self.kna3 * self.hna * self.h7_ss)
        self.h9_i = 1.0 / self.h7_i
        self.h9_ss = 1.0 / self.h7_ss
        self.k6_i = self.h6_i * c_intracellular_ions.cai * self.kcaon
        self.k6_ss = self.h6_ss * c_intracellular_ions.cass * self.kcaon
        self.k3p_i = self.h9_i * self.wca
        self.k3p_ss = self.h9_ss * self.wca
        self.k3pp_i = self.h8_i * self.wnaca
        self.k3pp_ss = self.h8_ss * self.wnaca
        self.k4p_i = self.h3_i * self.wca / self.hca
        self.k4p_ss = self.h3_ss * self.wca / self.hca
        self.k4pp_i = self.h2_i * self.wnaca
        self.k4pp_ss = self.h2_ss * self.wnaca
        self.k7_i = self.h5_i * self.h2_i * self.wna
        self.k7_ss = self.h5_ss * self.h2_ss * self.wna
        self.k8_i = self.h8_i * self.h11_i * self.wna
        self.k8_ss = self.h8_ss * self.h11_ss * self.wna
        self.k3_i = self.k3p_i + self.k3pp_i
        self.k3_ss = self.k3p_ss + self.k3pp_ss
        self.k4_i = self.k4p_i + self.k4pp_i
        self.k4_ss = self.k4p_ss + self.k4pp_ss
        self.x1_i = self.k2_i * self.k4_i * (self.k7_i + self.k6_i) + self.k5_i * self.k7_i * (self.k2_i + self.k3_i)
        self.x1_ss = self.k2_ss * self.k4_ss * (self.k7_ss + self.k6_ss) + self.k5_ss * self.k7_ss * (self.k2_ss + self.k3_ss)
        self.x2_i = self.k1_i * self.k7_i * (self.k4_i + self.k5_i) + self.k4_i * self.k6_i * (self.k1_i + self.k8_i)
        self.x2_ss = self.k1_ss * self.k7_ss * (self.k4_ss + self.k5_ss) + self.k4_ss * self.k6_ss * (self.k1_ss + self.k8_ss)
        self.x3_i = self.k1_i * self.k3_i * (self.k7_i + self.k6_i) + self.k8_i * self.k6_i * (self.k2_i + self.k3_i)
        self.x3_ss = self.k1_ss * self.k3_ss * (self.k7_ss + self.k6_ss) + self.k8_ss * self.k6_ss * (self.k2_ss + self.k3_ss)
        self.x4_i = self.k2_i * self.k8_i * (self.k4_i + self.k5_i) + self.k3_i * self.k5_i * (self.k1_i + self.k8_i)
        self.x4_ss = self.k2_ss * self.k8_ss * (self.k4_ss + self.k5_ss) + self.k3_ss * self.k5_ss * (self.k1_ss + self.k8_ss)
        self.E1_i = self.x1_i / (self.x1_i + self.x2_i + self.x3_i + self.x4_i)
        self.E1_ss = self.x1_ss / (self.x1_ss + self.x2_ss + self.x3_ss + self.x4_ss)
        self.E2_i = self.x2_i / (self.x1_i + self.x2_i + self.x3_i + self.x4_i)
        self.E2_ss = self.x2_ss / (self.x1_ss + self.x2_ss + self.x3_ss + self.x4_ss)
        self.E3_i = self.x3_i / (self.x1_i + self.x2_i + self.x3_i + self.x4_i)
        self.E3_ss = self.x3_ss / (self.x1_ss + self.x2_ss + self.x3_ss + self.x4_ss)
        self.E4_i = self.x4_i / (self.x1_i + self.x2_i + self.x3_i + self.x4_i)
        self.E4_ss = self.x4_ss / (self.x1_ss + self.x2_ss + self.x3_ss + self.x4_ss)
        self.JncxCa_i = self.E2_i * self.k2_i - self.E1_i * self.k1_i
        self.JncxCa_ss = self.E2_ss * self.k2_ss - self.E1_ss * self.k1_ss
        self.JncxNa_i = 3.0 * (self.E4_i * self.k7_i - self.E1_i * self.k8_i) + self.E3_i * self.k4pp_i - self.E2_i * self.k3pp_i
        self.JncxNa_ss = 3.0 * (self.E4_ss * self.k7_ss - self.E1_ss * self.k8_ss) + self.E3_ss * self.k4pp_ss - self.E2_ss * self.k3pp_ss
        self.INaCa_i_INaCa_i = 0.8 * self.Gncx * self.allo_i * (c_physical_constants.zna * self.JncxNa_i + c_physical_constants.zca * self.JncxCa_i)
        self.INaCa_ss = 0.2 * self.Gncx * self.allo_ss * (c_physical_constants.zna * self.JncxNa_ss + c_physical_constants.zca * self.JncxCa_ss)

class CInak:
    def __init__(self):
        self.E1 = None
        self.E2 = None
        self.E3 = None
        self.E4 = None
        self.H = None
        self.INaK_INaK = None
        self.JnakK = None
        self.JnakNa = None
        self.Khp = None
        self.Kki = None
        self.Kko = None
        self.Kmgatp = None
        self.Knai = None
        self.Knai0 = None
        self.Knao = None
        self.Knao0 = None
        self.Knap = None
        self.Kxkur = None
        self.MgADP = None
        self.MgATP = None
        self.P = None
        self.Pnak = None
        self.Pnak_b = None
        self.a1 = None
        self.a2 = None
        self.a3 = None
        self.a4 = None
        self.b1 = None
        self.b2 = None
        self.b3 = None
        self.b4 = None
        self.delta = None
        self.eP = None
        self.k1m = None
        self.k1p = None
        self.k2m = None
        self.k2p = None
        self.k3m = None
        self.k3p = None
        self.k4m = None
        self.k4p = None
        self.x1 = None
        self.x2 = None
        self.x3 = None
        self.x4 = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.H = 1e-07
        self.Khp = 1.698e-07
        self.Kki = 0.5
        self.Kko = 0.3582
        self.Kmgatp = 1.698e-07
        self.Knai0 = 9.073
        self.Knao0 = 27.78
        self.Knap = 224.0
        self.Kxkur = 292.0
        self.MgADP = 0.05
        self.MgATP = 9.8
        self.Pnak_b = 30.0
        self.delta = -0.155
        self.eP = 4.2
        self.k1m = 182.4
        self.k1p = 949.5
        self.k2m = 39.4
        self.k2p = 687.2
        self.k3m = 79300.0
        self.k3p = 1899.0
        self.k4m = 40.0
        self.k4p = 639.0
        self.Pnak = (self.Pnak_b * 0.9 if (c_environment.celltype == 1.0) else (self.Pnak_b * 0.7 if (c_environment.celltype == 2.0) else self.Pnak_b))
        self.a2 = self.k2p
        self.a4 = self.k4p * self.MgATP / self.Kmgatp / (1.0 + self.MgATP / self.Kmgatp)
        self.b1 = self.k1m * self.MgADP
    def init(self):
        """
        Resets the state variables to their initial values
        """
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.Knai = self.Knai0 * math.exp(self.delta * c_membrane.v * c_physical_constants.F / (3.0 * c_physical_constants.R * c_physical_constants.T))
        self.Knao = self.Knao0 * math.exp((1.0 - self.delta) * c_membrane.v * c_physical_constants.F / (3.0 * c_physical_constants.R * c_physical_constants.T))
        self.P = self.eP / (1.0 + self.H / self.Khp + c_intracellular_ions.nai / self.Knap + c_intracellular_ions.ki / self.Kxkur)
        self.a1 = self.k1p * (c_intracellular_ions.nai / self.Knai)**3.0 / ((1.0 + c_intracellular_ions.nai / self.Knai)**3.0 + (1.0 + c_intracellular_ions.ki / self.Kki)**2.0 - 1.0)
        self.a3 = self.k3p * (c_extracellular.ko / self.Kko)**2.0 / ((1.0 + c_extracellular.nao / self.Knao)**3.0 + (1.0 + c_extracellular.ko / self.Kko)**2.0 - 1.0)
        self.b2 = self.k2m * (c_extracellular.nao / self.Knao)**3.0 / ((1.0 + c_extracellular.nao / self.Knao)**3.0 + (1.0 + c_extracellular.ko / self.Kko)**2.0 - 1.0)
        self.b3 = self.k3m * self.P * self.H / (1.0 + self.MgATP / self.Kmgatp)
        self.b4 = self.k4m * (c_intracellular_ions.ki / self.Kki)**2.0 / ((1.0 + c_intracellular_ions.nai / self.Knai)**3.0 + (1.0 + c_intracellular_ions.ki / self.Kki)**2.0 - 1.0)
        self.x1 = self.a4 * self.a1 * self.a2 + self.b2 * self.b4 * self.b3 + self.a2 * self.b4 * self.b3 + self.b3 * self.a1 * self.a2
        self.x2 = self.b2 * self.b1 * self.b4 + self.a1 * self.a2 * self.a3 + self.a3 * self.b1 * self.b4 + self.a2 * self.a3 * self.b4
        self.x3 = self.a2 * self.a3 * self.a4 + self.b3 * self.b2 * self.b1 + self.b2 * self.b1 * self.a4 + self.a3 * self.a4 * self.b1
        self.x4 = self.b4 * self.b3 * self.b2 + self.a3 * self.a4 * self.a1 + self.b2 * self.a4 * self.a1 + self.b3 * self.b2 * self.a1
        self.E1 = self.x1 / (self.x1 + self.x2 + self.x3 + self.x4)
        self.E2 = self.x2 / (self.x1 + self.x2 + self.x3 + self.x4)
        self.E3 = self.x3 / (self.x1 + self.x2 + self.x3 + self.x4)
        self.E4 = self.x4 / (self.x1 + self.x2 + self.x3 + self.x4)
        self.JnakK = 2.0 * (self.E4 * self.b1 - self.E3 * self.a1)
        self.JnakNa = 3.0 * (self.E1 * self.a3 - self.E2 * self.b3)
        self.INaK_INaK = self.Pnak * (c_physical_constants.zna * self.JnakNa + c_physical_constants.zk * self.JnakK)

class CSerca:
    def __init__(self):
        self.Jleak = None
        self.Jup = None
        self.Jup_b = None
        self.Jupnp = None
        self.Jupp = None
        self.fJupp = None
        self.upScale = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.Jup_b = 1.0
        self.upScale = (1.3 if (c_environment.celltype == 1.0) else 1.0)
    def init(self):
        """
        Resets the state variables to their initial values
        """
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.Jleak = 0.0039375 * c_intracellular_ions.cansr / 15.0
        self.fJupp = 1.0 / (1.0 + c_camk.KmCaMK / c_camk.CaMKa)
        self.Jupnp = self.upScale * 0.004375 * c_intracellular_ions.cai / (c_intracellular_ions.cai + 0.00092)
        self.Jupp = self.upScale * 2.75 * 0.004375 * c_intracellular_ions.cai / (c_intracellular_ions.cai + 0.00092 - 0.00017)
        self.Jup = self.Jup_b * ((1.0 - self.fJupp) * self.Jupnp + self.fJupp * self.Jupp - self.Jleak)

class CReversal_potentials:
    def __init__(self):
        self.EK = None
        self.EKs = None
        self.ENa = None
        self.PKNa = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.PKNa = 0.01833
    def init(self):
        """
        Resets the state variables to their initial values
        """
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.EK = c_physical_constants.R * c_physical_constants.T / c_physical_constants.F * math.log(c_extracellular.ko / c_intracellular_ions.ki)
        self.ENa = c_physical_constants.R * c_physical_constants.T / c_physical_constants.F * math.log(c_extracellular.nao / c_intracellular_ions.nai)
        self.EKs = c_physical_constants.R * c_physical_constants.T / c_physical_constants.F * math.log((c_extracellular.ko + self.PKNa * c_extracellular.nao) / (c_intracellular_ions.ki + self.PKNa * c_intracellular_ions.nai))

class CIk1:
    def __init__(self):
        self.GK1 = None
        self.GK1_b = None
        self.IK1_IK1 = None
        self.rk1 = None
        self.txk1 = None
        self.xk1 = None
        self.d_xk1 = None
        self.xk1ss = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.GK1_b = 3.23978399999999778e-01
        self.GK1 = (self.GK1_b * 1.2 if (c_environment.celltype == 1.0) else (self.GK1_b * 1.3 if (c_environment.celltype == 2.0) else self.GK1_b))
    def init(self):
        """
        Resets the state variables to their initial values
        """
        self.xk1 =  9.96759759399999945e-01
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.rk1 = 1.0 / (1.0 + math.exp((c_membrane.v + 105.8 - 2.6 * c_extracellular.ko) / 9.493))
        self.txk1 = 122.2 / (math.exp(-(c_membrane.v + 127.2) / 20.36) + math.exp((c_membrane.v + 236.8) / 69.33))
        self.xk1ss = 1.0 / (1.0 + math.exp(-(c_membrane.v + 2.5538 * c_extracellular.ko + 144.59) / (1.5692 * c_extracellular.ko + 3.8115)))
        self.d_xk1 = (self.xk1ss - self.xk1) / self.txk1
        self.IK1_IK1 = self.GK1 * math.sqrt(c_extracellular.ko) * self.rk1 * self.xk1 * (c_membrane.v - c_reversal_potentials.EK)

class CIkb:
    def __init__(self):
        self.GKb = None
        self.GKb_b = None
        self.IKb_IKb = None
        self.xkb = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.GKb_b = 0.003
        self.GKb = (self.GKb_b * 0.6 if (c_environment.celltype == 1.0) else self.GKb_b)
    def init(self):
        """
        Resets the state variables to their initial values
        """
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.xkb = 1.0 / (1.0 + math.exp(-(c_membrane.v - 14.48) / 18.34))
        self.IKb_IKb = self.GKb * self.xkb * (c_membrane.v - c_reversal_potentials.EK)

class CIkr:
    def __init__(self):
        self.A1 = None
        self.A11 = None
        self.A2 = None
        self.A21 = None
        self.A3 = None
        self.A31 = None
        self.A4 = None
        self.A41 = None
        self.A51 = None
        self.A52 = None
        self.A53 = None
        self.A61 = None
        self.A62 = None
        self.A63 = None
        self.B1 = None
        self.B11 = None
        self.B2 = None
        self.B21 = None
        self.B3 = None
        self.B31 = None
        self.B4 = None
        self.B41 = None
        self.B51 = None
        self.B52 = None
        self.B53 = None
        self.B61 = None
        self.B62 = None
        self.B63 = None
        self.C1 = None
        self.d_c1 = None
        self.C2 = None
        self.d_c2 = None
        self.Cbound = None
        self.d_cbound = None
        self.D = None
        self.d_d = None
        self.GKr = None
        self.GKr_b = None
        self.IC1 = None
        self.d_ic1 = None
        self.IC2 = None
        self.d_ic2 = None
        self.IKr_IKr = None
        self.IO = None
        self.d_io = None
        self.IObound = None
        self.d_iobound = None
        self.Kmax = None
        self.Kt = None
        self.Ku = None
        self.O = None
        self.d_o = None
        self.Obound = None
        self.d_obound = None
        self.Temp = None
        self.Vhalf = None
        self.halfmax = None
        self.n = None
        self.q1 = None
        self.q11 = None
        self.q2 = None
        self.q21 = None
        self.q3 = None
        self.q31 = None
        self.q4 = None
        self.q41 = None
        self.q51 = None
        self.q52 = None
        self.q53 = None
        self.q61 = None
        self.q62 = None
        self.q63 = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.A1 = 0.0264
        self.A11 = 0.0007868
        self.A2 = 4.986e-06
        self.A21 = 5.455e-06
        self.A3 = 0.001214
        self.A31 = 0.005509
        self.A4 = 1.854e-05
        self.A41 = 0.001416
        self.A51 = 0.4492
        self.A52 = 0.3181
        self.A53 = 0.149
        self.A61 = 0.01241
        self.A62 = 0.3226
        self.A63 = 0.008978
        self.B1 = 4.631e-05
        self.B11 = 1.535e-08
        self.B2 = -0.004226
        self.B21 = -0.1688
        self.B3 = 0.008516
        self.B31 = 7.771e-09
        self.B4 = -0.04641
        self.B41 = -0.02877
        self.B51 = 0.008595
        self.B52 = 3.613e-08
        self.B53 = 0.004668
        self.B61 = 0.1725
        self.B62 = -0.0006575
        self.B63 = -0.02215
        self.GKr_b = 4.65854545454545618e-02
        self.Kmax = 0.0
        self.Kt = 0.0
        self.Ku = 0.0
        self.Temp = 37.0
        self.Vhalf = 1.0
        self.halfmax = 1.0
        self.n = 1.0
        self.q1 = 4.843
        self.q11 = 4.942
        self.q2 = 4.23
        self.q21 = 4.156
        self.q3 = 4.962
        self.q31 = 4.22
        self.q4 = 3.769
        self.q41 = 1.459
        self.q51 = 5.0
        self.q52 = 4.663
        self.q53 = 2.412
        self.q61 = 5.568
        self.q62 = 5.0
        self.q63 = 5.682
        self.GKr = (self.GKr_b * 1.3 if (c_environment.celltype == 1.0) else (self.GKr_b * 0.8 if (c_environment.celltype == 2.0) else self.GKr_b))
    def init(self):
        """
        Resets the state variables to their initial values
        """
        self.IC1 = 0.999637
        self.IC2 =  6.83207999999999982e-05
        self.C1 =  1.80144999999999990e-08
        self.C2 =  8.26618999999999954e-05
        self.O =  1.55510000000000007e-04
        self.IO =  5.67622999999999969e-05
        self.IObound = 0.0
        self.Obound = 0.0
        self.Cbound = 0.0
        self.D = 0.0
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.d_d = 0.0
        self.d_c1 = -(self.A1 * math.exp(self.B1 * c_membrane.v) * self.C1 * math.exp((self.Temp - 20.0) * math.log(self.q1) / 10.0) - self.A2 * math.exp(self.B2 * c_membrane.v) * self.C2 * math.exp((self.Temp - 20.0) * math.log(self.q2) / 10.0)) - (self.A51 * math.exp(self.B51 * c_membrane.v) * self.C1 * math.exp((self.Temp - 20.0) * math.log(self.q51) / 10.0) - self.A61 * math.exp(self.B61 * c_membrane.v) * self.IC1 * math.exp((self.Temp - 20.0) * math.log(self.q61) / 10.0))
        self.d_c2 = self.A1 * math.exp(self.B1 * c_membrane.v) * self.C1 * math.exp((self.Temp - 20.0) * math.log(self.q1) / 10.0) - self.A2 * math.exp(self.B2 * c_membrane.v) * self.C2 * math.exp((self.Temp - 20.0) * math.log(self.q2) / 10.0) - (self.A31 * math.exp(self.B31 * c_membrane.v) * self.C2 * math.exp((self.Temp - 20.0) * math.log(self.q31) / 10.0) - self.A41 * math.exp(self.B41 * c_membrane.v) * self.O * math.exp((self.Temp - 20.0) * math.log(self.q41) / 10.0)) - (self.A52 * math.exp(self.B52 * c_membrane.v) * self.C2 * math.exp((self.Temp - 20.0) * math.log(self.q52) / 10.0) - self.A62 * math.exp(self.B62 * c_membrane.v) * self.IC2 * math.exp((self.Temp - 20.0) * math.log(self.q62) / 10.0))
        self.d_cbound = -(self.Kt / (1.0 + math.exp(-(c_membrane.v - self.Vhalf) / 6.789)) * self.Cbound - self.Kt * self.Obound) - (self.Kt / (1.0 + math.exp(-(c_membrane.v - self.Vhalf) / 6.789)) * self.Cbound - self.Kt * self.IObound)
        self.d_ic1 = -(self.A11 * math.exp(self.B11 * c_membrane.v) * self.IC1 * math.exp((self.Temp - 20.0) * math.log(self.q11) / 10.0) - self.A21 * math.exp(self.B21 * c_membrane.v) * self.IC2 * math.exp((self.Temp - 20.0) * math.log(self.q21) / 10.0)) + self.A51 * math.exp(self.B51 * c_membrane.v) * self.C1 * math.exp((self.Temp - 20.0) * math.log(self.q51) / 10.0) - self.A61 * math.exp(self.B61 * c_membrane.v) * self.IC1 * math.exp((self.Temp - 20.0) * math.log(self.q61) / 10.0)
        self.d_ic2 = self.A11 * math.exp(self.B11 * c_membrane.v) * self.IC1 * math.exp((self.Temp - 20.0) * math.log(self.q11) / 10.0) - self.A21 * math.exp(self.B21 * c_membrane.v) * self.IC2 * math.exp((self.Temp - 20.0) * math.log(self.q21) / 10.0) - (self.A3 * math.exp(self.B3 * c_membrane.v) * self.IC2 * math.exp((self.Temp - 20.0) * math.log(self.q3) / 10.0) - self.A4 * math.exp(self.B4 * c_membrane.v) * self.IO * math.exp((self.Temp - 20.0) * math.log(self.q4) / 10.0)) + self.A52 * math.exp(self.B52 * c_membrane.v) * self.C2 * math.exp((self.Temp - 20.0) * math.log(self.q52) / 10.0) - self.A62 * math.exp(self.B62 * c_membrane.v) * self.IC2 * math.exp((self.Temp - 20.0) * math.log(self.q62) / 10.0)
        self.d_io = self.A3 * math.exp(self.B3 * c_membrane.v) * self.IC2 * math.exp((self.Temp - 20.0) * math.log(self.q3) / 10.0) - self.A4 * math.exp(self.B4 * c_membrane.v) * self.IO * math.exp((self.Temp - 20.0) * math.log(self.q4) / 10.0) + self.A53 * math.exp(self.B53 * c_membrane.v) * self.O * math.exp((self.Temp - 20.0) * math.log(self.q53) / 10.0) - self.A63 * math.exp(self.B63 * c_membrane.v) * self.IO * math.exp((self.Temp - 20.0) * math.log(self.q63) / 10.0) - (self.Kmax * self.Ku * math.exp(self.n * math.log(self.D)) / (math.exp(self.n * math.log(self.D)) + self.halfmax) * self.IO - self.Ku * self.A53 * math.exp(self.B53 * c_membrane.v) * math.exp((self.Temp - 20.0) * math.log(self.q53) / 10.0) / (self.A63 * math.exp(self.B63 * c_membrane.v) * math.exp((self.Temp - 20.0) * math.log(self.q63) / 10.0)) * self.IObound)
        self.d_iobound = self.Kmax * self.Ku * math.exp(self.n * math.log(self.D)) / (math.exp(self.n * math.log(self.D)) + self.halfmax) * self.IO - self.Ku * self.A53 * math.exp(self.B53 * c_membrane.v) * math.exp((self.Temp - 20.0) * math.log(self.q53) / 10.0) / (self.A63 * math.exp(self.B63 * c_membrane.v) * math.exp((self.Temp - 20.0) * math.log(self.q63) / 10.0)) * self.IObound + self.Kt / (1.0 + math.exp(-(c_membrane.v - self.Vhalf) / 6.789)) * self.Cbound - self.Kt * self.IObound
        self.d_o = self.A31 * math.exp(self.B31 * c_membrane.v) * self.C2 * math.exp((self.Temp - 20.0) * math.log(self.q31) / 10.0) - self.A41 * math.exp(self.B41 * c_membrane.v) * self.O * math.exp((self.Temp - 20.0) * math.log(self.q41) / 10.0) - (self.A53 * math.exp(self.B53 * c_membrane.v) * self.O * math.exp((self.Temp - 20.0) * math.log(self.q53) / 10.0) - self.A63 * math.exp(self.B63 * c_membrane.v) * self.IO * math.exp((self.Temp - 20.0) * math.log(self.q63) / 10.0)) - (self.Kmax * self.Ku * math.exp(self.n * math.log(self.D)) / (math.exp(self.n * math.log(self.D)) + self.halfmax) * self.O - self.Ku * self.Obound)
        self.d_obound = self.Kmax * self.Ku * math.exp(self.n * math.log(self.D)) / (math.exp(self.n * math.log(self.D)) + self.halfmax) * self.O - self.Ku * self.Obound + self.Kt / (1.0 + math.exp(-(c_membrane.v - self.Vhalf) / 6.789)) * self.Cbound - self.Kt * self.Obound
        self.IKr_IKr = self.GKr * math.sqrt(c_extracellular.ko / 5.4) * self.O * (c_membrane.v - c_reversal_potentials.EK)

class CIks:
    def __init__(self):
        self.GKs = None
        self.GKs_b = None
        self.IKs_IKs = None
        self.KsCa = None
        self.txs1 = None
        self.txs1_max = None
        self.txs2 = None
        self.xs1 = None
        self.d_xs1 = None
        self.xs1ss = None
        self.xs2 = None
        self.d_xs2 = None
        self.xs2ss = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.GKs_b = 6.35800000000000080e-03
        self.txs1_max = 817.3
        self.GKs = (self.GKs_b * 1.4 if (c_environment.celltype == 1.0) else self.GKs_b)
    def init(self):
        """
        Resets the state variables to their initial values
        """
        self.xs1 =  2.70775802499999996e-01
        self.xs2 =  1.92850342599999990e-04
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.KsCa = 1.0 + 0.6 / (1.0 + (3.8e-05 / c_intracellular_ions.cai)**1.4)
        self.txs2 = 1.0 / (0.01 * math.exp((c_membrane.v - 50.0) / 20.0) + 0.0193 * math.exp(-(c_membrane.v + 66.54) / 31.0))
        self.xs1ss = 1.0 / (1.0 + math.exp(-(c_membrane.v + 11.6) / 8.932))
        self.txs1 = self.txs1_max + 1.0 / (0.0002326 * math.exp((c_membrane.v + 48.28) / 17.8) + 0.001292 * math.exp(-(c_membrane.v + 210.0) / 230.0))
        self.xs2ss = self.xs1ss
        self.IKs_IKs = self.GKs * self.KsCa * self.xs1 * self.xs2 * (c_membrane.v - c_reversal_potentials.EKs)
        self.d_xs1 = (self.xs1ss - self.xs1) / self.txs1
        self.d_xs2 = (self.xs2ss - self.xs2) / self.txs2

class CIna:
    def __init__(self):
        self.Ahf = None
        self.Ahs = None
        self.GNa = None
        self.INa_INa = None
        self.fINap = None
        self.h = None
        self.hf = None
        self.d_hf = None
        self.hp = None
        self.hs = None
        self.d_hs = None
        self.hsp = None
        self.d_hsp = None
        self.hss = None
        self.hssV1 = None
        self.hssV2 = None
        self.hssp = None
        self.j = None
        self.d_j = None
        self.jp = None
        self.d_jp = None
        self.jss = None
        self.m = None
        self.d_m = None
        self.mss = None
        self.mssV1 = None
        self.mssV2 = None
        self.mtD1 = None
        self.mtD2 = None
        self.mtV1 = None
        self.mtV2 = None
        self.mtV3 = None
        self.mtV4 = None
        self.shift_INa_inact = None
        self.thf = None
        self.ths = None
        self.thsp = None
        self.tj = None
        self.tjp = None
        self.tm = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.Ahf = 0.99
        self.GNa = 75.0
        self.hssV1 = 82.9
        self.hssV2 = 6.086
        self.mssV1 = 39.57
        self.mssV2 = 9.871
        self.mtD1 = 6.765
        self.mtD2 = 8.552
        self.mtV1 = 11.64
        self.mtV2 = 34.77
        self.mtV3 = 77.42
        self.mtV4 = 5.955
        self.shift_INa_inact = 0.0
        self.Ahs = 1.0 - self.Ahf
    def init(self):
        """
        Resets the state variables to their initial values
        """
        self.m =  7.34412110199999992e-03
        self.hf =  6.98107191299999985e-01
        self.hs =  6.98089580099999996e-01
        self.j =  6.97990843200000044e-01
        self.hsp =  4.54948552499999992e-01
        self.jp =  6.97924586499999999e-01
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.fINap = 1.0 / (1.0 + c_camk.KmCaMK / c_camk.CaMKa)
        self.hss = 1.0 / (1.0 + math.exp((c_membrane.v + self.hssV1 - self.shift_INa_inact) / self.hssV2))
        self.hssp = 1.0 / (1.0 + math.exp((c_membrane.v + 89.1 - self.shift_INa_inact) / 6.086))
        self.mss = 1.0 / (1.0 + math.exp(-(c_membrane.v + self.mssV1) / self.mssV2))
        self.thf = 1.0 / (1.432e-05 * math.exp(-(c_membrane.v + 1.196 - self.shift_INa_inact) / 6.285) + 6.149 * math.exp((c_membrane.v + 0.5096 - self.shift_INa_inact) / 20.27))
        self.ths = 1.0 / (0.009794 * math.exp(-(c_membrane.v + 17.95 - self.shift_INa_inact) / 28.05) + 0.3343 * math.exp((c_membrane.v + 5.73 - self.shift_INa_inact) / 56.66))
        self.tj = 2.038 + 1.0 / (0.02136 * math.exp(-(c_membrane.v + 100.6 - self.shift_INa_inact) / 8.281) + 0.3052 * math.exp((c_membrane.v + 0.9941 - self.shift_INa_inact) / 38.45))
        self.tm = 1.0 / (self.mtD1 * math.exp((c_membrane.v + self.mtV1) / self.mtV2) + self.mtD2 * math.exp(-(c_membrane.v + self.mtV3) / self.mtV4))
        self.h = self.Ahf * self.hf + self.Ahs * self.hs
        self.hp = self.Ahf * self.hf + self.Ahs * self.hsp
        self.jss = self.hss
        self.thsp = 3.0 * self.ths
        self.tjp = 1.46 * self.tj
        self.d_hf = (self.hss - self.hf) / self.thf
        self.d_hs = (self.hss - self.hs) / self.ths
        self.d_m = (self.mss - self.m) / self.tm
        self.INa_INa = self.GNa * (c_membrane.v - c_reversal_potentials.ENa) * self.m**3.0 * ((1.0 - self.fINap) * self.h * self.j + self.fINap * self.hp * self.jp)
        self.d_hsp = (self.hssp - self.hsp) / self.thsp
        self.d_j = (self.jss - self.j) / self.tj
        self.d_jp = (self.jss - self.jp) / self.tjp

class CIto:
    def __init__(self):
        self.AiF = None
        self.AiS = None
        self.Gto = None
        self.Gto_b = None
        self.Ito_Ito = None
        self.a = None
        self.d_a = None
        self.ap = None
        self.d_ap = None
        self.ass = None
        self.assp = None
        self.delta_epi = None
        self.dti_develop = None
        self.dti_recover = None
        self.fItop = None
        self.i = None
        self.iF = None
        self.d_if = None
        self.iFp = None
        self.d_ifp = None
        self.iS = None
        self.d_is = None
        self.iSp = None
        self.d_isp = None
        self.ip = None
        self.iss = None
        self.ta = None
        self.tiF = None
        self.tiF_b = None
        self.tiFp = None
        self.tiS = None
        self.tiS_b = None
        self.tiSp = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.Gto_b = 0.02
        self.Gto = (self.Gto_b * 4.0 if (c_environment.celltype == 1.0) else (self.Gto_b * 4.0 if (c_environment.celltype == 2.0) else self.Gto_b))
    def init(self):
        """
        Resets the state variables to their initial values
        """
        self.a =  1.00109768699999991e-03
        self.iF =  9.99554174499999948e-01
        self.iS =  5.86506173600000014e-01
        self.ap =  5.10086293400000023e-04
        self.iFp =  9.99554182300000038e-01
        self.iSp =  6.39339948199999952e-01
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.AiF = 1.0 / (1.0 + math.exp((c_membrane.v - 213.6) / 151.2))
        self.ass = 1.0 / (1.0 + math.exp(-(c_membrane.v - 14.34) / 14.82))
        self.assp = 1.0 / (1.0 + math.exp(-(c_membrane.v - 24.34) / 14.82))
        self.delta_epi = (1.0 - 0.95 / (1.0 + math.exp((c_membrane.v + 70.0) / 5.0)) if (c_environment.celltype == 1.0) else 1.0)
        self.dti_develop = 1.354 + 0.0001 / (math.exp((c_membrane.v - 167.4) / 15.89) + math.exp(-(c_membrane.v - 12.23) / 0.2154))
        self.dti_recover = 1.0 - 0.5 / (1.0 + math.exp((c_membrane.v + 70.0) / 20.0))
        self.fItop = 1.0 / (1.0 + c_camk.KmCaMK / c_camk.CaMKa)
        self.iss = 1.0 / (1.0 + math.exp((c_membrane.v + 43.94) / 5.711))
        self.ta = 1.0515 / (1.0 / (1.2089 * (1.0 + math.exp(-(c_membrane.v - 18.4099) / 29.3814))) + 3.5 / (1.0 + math.exp((c_membrane.v + 100.0) / 29.3814)))
        self.tiF_b = 4.562 + 1.0 / (0.3933 * math.exp(-(c_membrane.v + 100.0) / 100.0) + 0.08004 * math.exp((c_membrane.v + 50.0) / 16.59))
        self.tiS_b = 23.62 + 1.0 / (0.001416 * math.exp(-(c_membrane.v + 96.52) / 59.05) + 1.78e-08 * math.exp((c_membrane.v + 114.1) / 8.079))
        self.AiS = 1.0 - self.AiF
        self.tiF = self.tiF_b * self.delta_epi
        self.tiS = self.tiS_b * self.delta_epi
        self.d_a = (self.ass - self.a) / self.ta
        self.d_ap = (self.assp - self.ap) / self.ta
        self.i = self.AiF * self.iF + self.AiS * self.iS
        self.ip = self.AiF * self.iFp + self.AiS * self.iSp
        self.tiFp = self.dti_develop * self.dti_recover * self.tiF
        self.tiSp = self.dti_develop * self.dti_recover * self.tiS
        self.d_if = (self.iss - self.iF) / self.tiF
        self.d_is = (self.iss - self.iS) / self.tiS
        self.Ito_Ito = self.Gto * (c_membrane.v - c_reversal_potentials.EK) * ((1.0 - self.fItop) * self.a * self.i + self.fItop * self.ap * self.ip)
        self.d_ifp = (self.iss - self.iFp) / self.tiFp
        self.d_isp = (self.iss - self.iSp) / self.tiSp

class CInal:
    def __init__(self):
        self.GNaL = None
        self.GNaL_b = None
        self.INaL_INaL = None
        self.fINaLp = None
        self.hL = None
        self.d_hl = None
        self.hLp = None
        self.d_hlp = None
        self.hLss = None
        self.hLssp = None
        self.mL = None
        self.d_ml = None
        self.mLss = None
        self.thL = None
        self.thLp = None
        self.tmL = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.GNaL_b = 1.99574999999999753e-02
        self.thL = 200.0
        self.GNaL = (self.GNaL_b * 0.6 if (c_environment.celltype == 1.0) else self.GNaL_b)
        self.thLp = 3.0 * self.thL
    def init(self):
        """
        Resets the state variables to their initial values
        """
        self.mL =  1.88261727299999989e-04
        self.hL =  5.00854885500000013e-01
        self.hLp =  2.69306535700000016e-01
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.fINaLp = 1.0 / (1.0 + c_camk.KmCaMK / c_camk.CaMKa)
        self.hLss = 1.0 / (1.0 + math.exp((c_membrane.v + 87.61) / 7.488))
        self.hLssp = 1.0 / (1.0 + math.exp((c_membrane.v + 93.81) / 7.488))
        self.mLss = 1.0 / (1.0 + math.exp(-(c_membrane.v + 42.85) / 5.264))
        self.tmL = c_ina.tm
        self.d_hl = (self.hLss - self.hL) / self.thL
        self.d_ml = (self.mLss - self.mL) / self.tmL
        self.INaL_INaL = self.GNaL * (c_membrane.v - c_reversal_potentials.ENa) * self.mL * ((1.0 - self.fINaLp) * self.hL + self.fINaLp * self.hLp)
        self.d_hlp = (self.hLssp - self.hLp) / self.thLp

class CIcal:
    def __init__(self):
        self.A_1 = None
        self.A_2 = None
        self.A_3 = None
        self.Afcaf = None
        self.Afcas = None
        self.Aff = None
        self.Afs = None
        self.B_1 = None
        self.B_2 = None
        self.B_3 = None
        self.ICaK = None
        self.ICaL_ICaL = None
        self.ICaNa = None
        self.Kmn = None
        self.PCa = None
        self.PCaK = None
        self.PCaKp = None
        self.PCaNa = None
        self.PCaNap = None
        self.PCa_b = None
        self.PCap = None
        self.PhiCaK = None
        self.PhiCaL = None
        self.PhiCaNa = None
        self.U_1 = None
        self.U_2 = None
        self.U_3 = None
        self.anca = None
        self.d = None
        self.d_d = None
        self.dss = None
        self.f = None
        self.fICaLp = None
        self.fca = None
        self.fcaf = None
        self.d_fcaf = None
        self.fcafp = None
        self.d_fcafp = None
        self.fcap = None
        self.fcas = None
        self.d_fcas = None
        self.fcass = None
        self.ff = None
        self.d_ff = None
        self.ffp = None
        self.d_ffp = None
        self.fp = None
        self.fs = None
        self.d_fs = None
        self.fss = None
        self.jca = None
        self.d_jca = None
        self.k2n = None
        self.km2n = None
        self.nca = None
        self.d_nca = None
        self.td = None
        self.tfcaf = None
        self.tfcafp = None
        self.tfcas = None
        self.tff = None
        self.tffp = None
        self.tfs = None
        self.tjca = None
        self.ICaL_v0 = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.Aff = 0.6
        self.Kmn = 0.002
        self.PCa_b = 0.0001007
        self.k2n = 1000.0
        self.tjca = 75.0
        self.ICaL_v0 = 0.0
        self.Afs = 1.0 - self.Aff
        self.PCa = (self.PCa_b * 1.2 if (c_environment.celltype == 1.0) else (self.PCa_b * 2.5 if (c_environment.celltype == 2.0) else self.PCa_b))
        self.PCaK = 0.0003574 * self.PCa
        self.PCaNa = 0.00125 * self.PCa
        self.PCap = 1.1 * self.PCa
        self.PCaKp = 0.0003574 * self.PCap
        self.PCaNap = 0.00125 * self.PCap
    def init(self):
        """
        Resets the state variables to their initial values
        """
        self.d = 2.34e-09
        self.ff =  9.99999990900000024e-01
        self.fs =  9.10241277699999962e-01
        self.fcaf =  9.99999990900000024e-01
        self.fcas =  9.99804677700000033e-01
        self.jca =  9.99973831200000052e-01
        self.ffp =  9.99999990900000024e-01
        self.fcafp =  9.99999990900000024e-01
        self.nca =  2.74941404400000020e-03
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.Afcaf = 0.3 + 0.6 / (1.0 + math.exp((c_membrane.v - 10.0) / 10.0))
        self.dss = 1.0 / (1.0 + math.exp(-(c_membrane.v + 3.94) / 4.23))
        self.fICaLp = 1.0 / (1.0 + c_camk.KmCaMK / c_camk.CaMKa)
        self.fss = 1.0 / (1.0 + math.exp((c_membrane.v + 19.58) / 3.696))
        self.km2n = self.jca * 1.0
        self.td = 0.6 + 1.0 / (math.exp(-0.05 * (c_membrane.v + 6.0)) + math.exp(0.09 * (c_membrane.v + 14.0)))
        self.tfcaf = 7.0 + 1.0 / (0.04 * math.exp(-(c_membrane.v - 4.0) / 7.0) + 0.04 * math.exp((c_membrane.v - 4.0) / 7.0))
        self.tfcas = 100.0 + 1.0 / (0.00012 * math.exp(-c_membrane.v / 3.0) + 0.00012 * math.exp(c_membrane.v / 7.0))
        self.tff = 7.0 + 1.0 / (0.0045 * math.exp(-(c_membrane.v + 20.0) / 10.0) + 0.0045 * math.exp((c_membrane.v + 20.0) / 10.0))
        self.tfs = 1000.0 + 1.0 / (3.5e-05 * math.exp(-(c_membrane.v + 5.0) / 4.0) + 3.5e-05 * math.exp((c_membrane.v + 5.0) / 6.0))
        self.Afcas = 1.0 - self.Afcaf
        self.anca = 1.0 / (self.k2n / self.km2n + (1.0 + self.Kmn / c_intracellular_ions.cass)**4.0)
        self.fcass = self.fss
        self.tfcafp = 2.5 * self.tfcaf
        self.tffp = 2.5 * self.tff
        self.d_d = (self.dss - self.d) / self.td
        self.d_ff = (self.fss - self.ff) / self.tff
        self.d_fs = (self.fss - self.fs) / self.tfs
        self.f = self.Aff * self.ff + self.Afs * self.fs
        self.fca = self.Afcaf * self.fcaf + self.Afcas * self.fcas
        self.fcap = self.Afcaf * self.fcafp + self.Afcas * self.fcas
        self.fp = self.Aff * self.ffp + self.Afs * self.fs
        self.d_fcaf = (self.fcass - self.fcaf) / self.tfcaf
        self.d_fcafp = (self.fcass - self.fcafp) / self.tfcafp
        self.d_fcas = (self.fcass - self.fcas) / self.tfcas
        self.d_ffp = (self.fss - self.ffp) / self.tffp
        self.d_jca = (self.fcass - self.jca) / self.tjca
        self.d_nca = self.anca * self.k2n - self.nca * self.km2n

class CIcab:
    def __init__(self):
        self.ICab_A = None
        self.ICab_B = None
        self.ICab_ICab = None
        self.PCab = None
        self.ICab_U = None
        self.ICab_v0 = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.PCab = 2.5e-08
        self.ICab_v0 = 0.0
    def init(self):
        """
        Resets the state variables to their initial values
        """
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        pass

class CInab:
    def __init__(self):
        self.INab_A = None
        self.INab_B = None
        self.INab_INab = None
        self.PNab = None
        self.INab_U = None
        self.INab_v0 = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.PNab = 3.75e-10
        self.INab_v0 = 0.0
    def init(self):
        """
        Resets the state variables to their initial values
        """
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        pass

class CIntracellular_ions:
    def __init__(self):
        self.BSLmax = None
        self.BSRmax = None
        self.Bcai = None
        self.Bcajsr = None
        self.Bcass = None
        self.KmBSL = None
        self.KmBSR = None
        self.cai = None
        self.d_cai = None
        self.cajsr = None
        self.d_cajsr = None
        self.cansr = None
        self.d_cansr = None
        self.cass = None
        self.d_cass = None
        self.cm = None
        self.cmdnmax = None
        self.cmdnmax_b = None
        self.csqnmax = None
        self.ki = None
        self.d_ki = None
        self.kmcmdn = None
        self.kmcsqn = None
        self.kmtrpn = None
        self.kss = None
        self.d_kss = None
        self.nai = None
        self.d_nai = None
        self.nass = None
        self.d_nass = None
        self.trpnmax = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.BSLmax = 1.124
        self.BSRmax = 0.047
        self.KmBSL = 0.0087
        self.KmBSR = 0.00087
        self.cm = 1.0
        self.cmdnmax_b = 0.05
        self.csqnmax = 10.0
        self.kmcmdn = 0.00238
        self.kmcsqn = 0.8
        self.kmtrpn = 0.0005
        self.trpnmax = 0.07
        self.cmdnmax = (self.cmdnmax_b * 1.3 if (c_environment.celltype == 1.0) else self.cmdnmax_b)
    def init(self):
        """
        Resets the state variables to their initial values
        """
        self.nai =  7.26800449799999981e+00
        self.nass =  7.26808997699999981e+00
        self.ki =  1.44655591799999996e+02
        self.kss =  1.44655565099999990e+02
        self.cass = 8.49e-05
        self.cansr =  1.61957453799999995e+00
        self.cajsr =  1.57123401400000007e+00
        self.cai = 8.6e-05
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.d_cansr = c_serca.Jup - c_trans_flux.Jtr * c_cell_geometry.vjsr / c_cell_geometry.vnsr
        self.Bcajsr = 1.0 / (1.0 + self.csqnmax * self.kmcsqn / (self.kmcsqn + self.cajsr)**2.0)
        self.Bcass = 1.0 / (1.0 + self.BSRmax * self.KmBSR / (self.KmBSR + self.cass)**2.0 + self.BSLmax * self.KmBSL / (self.KmBSL + self.cass)**2.0)
        self.Bcai = 1.0 / (1.0 + self.cmdnmax * self.kmcmdn / (self.kmcmdn + self.cai)**2.0 + self.trpnmax * self.kmtrpn / (self.kmtrpn + self.cai)**2.0)

class CMembrane:
    def __init__(self):
        self.Istim = None
        self.ffrt = None
        self.frt = None
        self.i_Stim_Amplitude = None
        self.i_Stim_End = None
        self.i_Stim_Period = None
        self.i_Stim_PulseDuration = None
        self.i_Stim_Start = None
        self.v = None
        self.d_v = None
        self.vfrt = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.frt = c_physical_constants.F / (c_physical_constants.R * c_physical_constants.T)
        self.i_Stim_Amplitude = -80.0
        self.i_Stim_End = 1e+17
        self.i_Stim_Period = 1000.0
        self.i_Stim_PulseDuration = 0.5
        self.i_Stim_Start = 10.0
        self.ffrt = c_physical_constants.F * self.frt
    def init(self):
        """
        Resets the state variables to their initial values
        """
        self.v = -8.80019046500000002e+01
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.Istim = (self.i_Stim_Amplitude if (((c_environment.time >= self.i_Stim_Start) and (c_environment.time <= self.i_Stim_End)) and (c_environment.time - self.i_Stim_Start - math.floor((c_environment.time - self.i_Stim_Start) / self.i_Stim_Period) * self.i_Stim_Period <= self.i_Stim_PulseDuration)) else 0.0)
        self.vfrt = self.v * self.frt

class CRyr:
    def __init__(self):
        self.Jrel = None
        self.Jrel_inf = None
        self.Jrel_inf_temp = None
        self.Jrel_infp = None
        self.Jrel_scaling_factor = None
        self.Jrel_temp = None
        self.Jrelnp = None
        self.d_jrelnp = None
        self.Jrelp = None
        self.d_jrelp = None
        self.a_rel = None
        self.a_relp = None
        self.bt = None
        self.btp = None
        self.fJrelp = None
        self.tau_rel = None
        self.tau_rel_temp = None
        self.tau_relp = None
        self.tau_relp_temp = None

        self._constants()
        self.init()
    def _constants(self):
        """
        Sets the constant values
        """
        self.Jrel_scaling_factor = 1.0
        self.bt = 4.75
        self.a_rel = 0.5 * self.bt
        self.btp = 1.25 * self.bt
        self.a_relp = 0.5 * self.btp
    def init(self):
        """
        Resets the state variables to their initial values
        """
        self.Jrelnp = 2.5e-07
        self.Jrelp = 3.12e-07
    def update(self):
        """
        Re-calculates all values for the current time and state
        """
        self.fJrelp = 1.0 / (1.0 + c_camk.KmCaMK / c_camk.CaMKa)
        self.Jrel = self.Jrel_scaling_factor * ((1.0 - self.fJrelp) * self.Jrelnp + self.fJrelp * self.Jrelp)
        self.tau_rel_temp = self.bt / (1.0 + 0.0123 / c_intracellular_ions.cajsr)
        self.tau_rel = (0.001 if (self.tau_rel_temp < 0.001) else self.tau_rel_temp)
        self.tau_relp_temp = self.btp / (1.0 + 0.0123 / c_intracellular_ions.cajsr)
        self.tau_relp = (0.001 if (self.tau_relp_temp < 0.001) else self.tau_relp_temp)

#
# Engine component
#
class Engine:
    """
    Calculates the derivatives in the current state
    """
    def __init__(self):
        self.pace = 0.0
        self.time = 0.0
    def update(self):
        c_camk.update()
        c_ipca.update()
        c_cell_geometry.update()
        c_diff.update()
        c_environment.update()
        c_extracellular.update()
        c_physical_constants.update()
        c_trans_flux.update()
        c_inaca_i.update()
        c_inak.update()
        c_serca.update()
        c_reversal_potentials.update()
        c_ik1.update()
        c_ikb.update()
        c_ikr.update()
        c_iks.update()
        c_ina.update()
        c_ito.update()
        c_inal.update()
        c_ical.update()
        c_icab.update()
        c_inab.update()
        c_intracellular_ions.update()
        c_membrane.update()
        c_ryr.update()
        # Remaining equations (patched: Jrel lives on c_ryr, not Engine)
        c_intracellular_ions.d_cajsr = c_intracellular_ions.Bcajsr * (c_trans_flux.Jtr - c_ryr.Jrel)
        c_intracellular_ions.d_ki = -(c_ito.Ito_Ito + c_ikr.IKr_IKr + c_iks.IKs_IKs + c_ik1.IK1_IK1 + c_ikb.IKb_IKb + c_membrane.Istim - 2.0 * c_inak.INaK_INaK) * c_intracellular_ions.cm * c_cell_geometry.Acap / (c_physical_constants.F * c_cell_geometry.vmyo) + c_diff.JdiffK * c_cell_geometry.vss / c_cell_geometry.vmyo
        c_ical.A_1 = 4.0 * c_membrane.ffrt * (c_intracellular_ions.cass * math.exp(2.0 * c_membrane.vfrt) - 0.341 * c_extracellular.cao) / c_ical.B_1
        c_ical.A_2 = 0.75 * c_membrane.ffrt * (c_intracellular_ions.nass * math.exp(c_membrane.vfrt) - c_extracellular.nao) / c_ical.B_2
        c_ical.A_3 = 0.75 * c_membrane.ffrt * (c_intracellular_ions.kss * math.exp(c_membrane.vfrt) - c_extracellular.ko) / c_ical.B_3
        c_ical.U_1 = c_ical.B_1 * (c_membrane.v - c_ical.ICaL_v0)
        c_ical.U_2 = c_ical.B_2 * (c_membrane.v - c_ical.ICaL_v0)
        c_ical.U_3 = c_ical.B_3 * (c_membrane.v - c_ical.ICaL_v0)
        c_icab.ICab_A = c_icab.PCab * 4.0 * c_membrane.ffrt * (c_intracellular_ions.cai * math.exp(2.0 * c_membrane.vfrt) - 0.341 * c_extracellular.cao) / c_icab.ICab_B
        c_icab.ICab_U = c_icab.ICab_B * (c_membrane.v - c_icab.ICab_v0)
        c_inab.INab_A = c_inab.PNab * c_membrane.ffrt * (c_intracellular_ions.nai * math.exp(c_membrane.vfrt) - c_extracellular.nao) / c_inab.INab_B
        c_inab.INab_U = c_inab.INab_B * (c_membrane.v - c_inab.INab_v0)
        c_ical.PhiCaK = (c_ical.A_3 * (1.0 - 0.5 * c_ical.U_3) if ((-1e-07 <= c_ical.U_3) and (c_ical.U_3 <= 1e-07)) else c_ical.A_3 * c_ical.U_3 / (math.exp(c_ical.U_3) - 1.0))
        c_ical.PhiCaL = (c_ical.A_1 * (1.0 - 0.5 * c_ical.U_1) if ((-1e-07 <= c_ical.U_1) and (c_ical.U_1 <= 1e-07)) else c_ical.A_1 * c_ical.U_1 / (math.exp(c_ical.U_1) - 1.0))
        c_ical.PhiCaNa = (c_ical.A_2 * (1.0 - 0.5 * c_ical.U_2) if ((-1e-07 <= c_ical.U_2) and (c_ical.U_2 <= 1e-07)) else c_ical.A_2 * c_ical.U_2 / (math.exp(c_ical.U_2) - 1.0))
        c_icab.ICab_ICab = (c_icab.ICab_A * (1.0 - 0.5 * c_icab.ICab_U) if ((-1e-07 <= c_icab.ICab_U) and (c_icab.ICab_U <= 1e-07)) else c_icab.ICab_A * c_icab.ICab_U / (math.exp(c_icab.ICab_U) - 1.0))
        c_inab.INab_INab = (c_inab.INab_A * (1.0 - 0.5 * c_inab.INab_U) if ((-1e-07 <= c_inab.INab_U) and (c_inab.INab_U <= 1e-07)) else c_inab.INab_A * c_inab.INab_U / (math.exp(c_inab.INab_U) - 1.0))
        c_ical.ICaK = (1.0 - c_ical.fICaLp) * c_ical.PCaK * c_ical.PhiCaK * c_ical.d * (c_ical.f * (1.0 - c_ical.nca) + c_ical.jca * c_ical.fca * c_ical.nca) + c_ical.fICaLp * c_ical.PCaKp * c_ical.PhiCaK * c_ical.d * (c_ical.fp * (1.0 - c_ical.nca) + c_ical.jca * c_ical.fcap * c_ical.nca)
        c_ical.ICaL_ICaL = (1.0 - c_ical.fICaLp) * c_ical.PCa * c_ical.PhiCaL * c_ical.d * (c_ical.f * (1.0 - c_ical.nca) + c_ical.jca * c_ical.fca * c_ical.nca) + c_ical.fICaLp * c_ical.PCap * c_ical.PhiCaL * c_ical.d * (c_ical.fp * (1.0 - c_ical.nca) + c_ical.jca * c_ical.fcap * c_ical.nca)
        c_ical.ICaNa = (1.0 - c_ical.fICaLp) * c_ical.PCaNa * c_ical.PhiCaNa * c_ical.d * (c_ical.f * (1.0 - c_ical.nca) + c_ical.jca * c_ical.fca * c_ical.nca) + c_ical.fICaLp * c_ical.PCaNap * c_ical.PhiCaNa * c_ical.d * (c_ical.fp * (1.0 - c_ical.nca) + c_ical.jca * c_ical.fcap * c_ical.nca)
        c_intracellular_ions.d_cai = c_intracellular_ions.Bcai * (-(c_ipca.IpCa_IpCa + c_icab.ICab_ICab - 2.0 * c_inaca_i.INaCa_i_INaCa_i) * c_intracellular_ions.cm * c_cell_geometry.Acap / (2.0 * c_physical_constants.F * c_cell_geometry.vmyo) - c_serca.Jup * c_cell_geometry.vnsr / c_cell_geometry.vmyo + c_diff.Jdiff * c_cell_geometry.vss / c_cell_geometry.vmyo)
        c_intracellular_ions.d_nai = -(c_ina.INa_INa + c_inal.INaL_INaL + 3.0 * c_inaca_i.INaCa_i_INaCa_i + 3.0 * c_inak.INaK_INaK + c_inab.INab_INab) * c_cell_geometry.Acap * c_intracellular_ions.cm / (c_physical_constants.F * c_cell_geometry.vmyo) + c_diff.JdiffNa * c_cell_geometry.vss / c_cell_geometry.vmyo
        c_intracellular_ions.d_cass = c_intracellular_ions.Bcass * (-(c_ical.ICaL_ICaL - 2.0 * c_inaca_i.INaCa_ss) * c_intracellular_ions.cm * c_cell_geometry.Acap / (2.0 * c_physical_constants.F * c_cell_geometry.vss) + c_ryr.Jrel * c_cell_geometry.vjsr / c_cell_geometry.vss - c_diff.Jdiff)
        c_intracellular_ions.d_kss = -c_ical.ICaK * c_intracellular_ions.cm * c_cell_geometry.Acap / (c_physical_constants.F * c_cell_geometry.vss) - c_diff.JdiffK
        c_intracellular_ions.d_nass = -(c_ical.ICaNa + 3.0 * c_inaca_i.INaCa_ss) * c_intracellular_ions.cm * c_cell_geometry.Acap / (c_physical_constants.F * c_cell_geometry.vss) - c_diff.JdiffNa
        c_membrane.d_v = -(c_ina.INa_INa + c_inal.INaL_INaL + c_ito.Ito_Ito + c_ical.ICaL_ICaL + c_ical.ICaNa + c_ical.ICaK + c_ikr.IKr_IKr + c_iks.IKs_IKs + c_ik1.IK1_IK1 + c_inaca_i.INaCa_i_INaCa_i + c_inaca_i.INaCa_ss + c_inak.INaK_INaK + c_inab.INab_INab + c_ikb.IKb_IKb + c_ipca.IpCa_IpCa + c_icab.ICab_ICab + c_membrane.Istim)
        c_ryr.Jrel_inf_temp = c_ryr.a_rel * -c_ical.ICaL_ICaL / (1.0 + 1.0 * (1.5 / c_intracellular_ions.cajsr)**8.0)
        c_ryr.Jrel_temp = c_ryr.a_relp * -c_ical.ICaL_ICaL / (1.0 + (1.5 / c_intracellular_ions.cajsr)**8.0)
        c_ryr.Jrel_inf = (c_ryr.Jrel_inf_temp * 1.7 if (c_environment.celltype == 2.0) else c_ryr.Jrel_inf_temp)
        c_ryr.Jrel_infp = (c_ryr.Jrel_temp * 1.7 if (c_environment.celltype == 2.0) else c_ryr.Jrel_temp)
        c_ryr.d_jrelnp = (c_ryr.Jrel_inf - c_ryr.Jrelnp) / c_ryr.tau_rel
        c_ryr.d_jrelp = (c_ryr.Jrel_infp - c_ryr.Jrelp) / c_ryr.tau_relp

#
# Create objects, set initial values
#
def init():
    """ (Re-)Initializes the model """
    global c_camk
    global c_ipca
    global c_cell_geometry
    global c_diff
    global c_environment
    global c_extracellular
    global c_physical_constants
    global c_trans_flux
    global c_inaca_i
    global c_inak
    global c_serca
    global c_reversal_potentials
    global c_ik1
    global c_ikb
    global c_ikr
    global c_iks
    global c_ina
    global c_ito
    global c_inal
    global c_ical
    global c_icab
    global c_inab
    global c_intracellular_ions
    global c_membrane
    global c_ryr
    global engine
    c_camk                = CCamk()
    c_ipca                = CIpca()
    c_cell_geometry       = CCell_geometry()
    c_diff                = CDiff()
    c_environment         = CEnvironment()
    c_extracellular       = CExtracellular()
    c_physical_constants  = CPhysical_constants()
    c_trans_flux          = CTrans_flux()
    c_inaca_i             = CInaca_i()
    c_inak                = CInak()
    c_serca               = CSerca()
    c_reversal_potentials = CReversal_potentials()
    c_ik1                 = CIk1()
    c_ikb                 = CIkb()
    c_ikr                 = CIkr()
    c_iks                 = CIks()
    c_ina                 = CIna()
    c_ito                 = CIto()
    c_inal                = CInal()
    c_ical                = CIcal()
    c_icab                = CIcab()
    c_inab                = CInab()
    c_intracellular_ions  = CIntracellular_ions()
    c_membrane            = CMembrane()
    c_ryr                 = CRyr()
    engine = Engine()
    c_ical.B_1 = 2.0 * c_membrane.frt
    c_ical.B_2 = c_membrane.frt
    c_ical.B_3 = c_membrane.frt
    c_icab.ICab_B = 2.0 * c_membrane.frt
    c_inab.INab_B = c_membrane.frt

#
# Update function (rhs function, takes a single step)
#
def update(stepSize):
    """ Calculates all derivatives, update state, advances time """
    engine.update()
    c_membrane.v               += stepSize * c_membrane.d_v
    c_camk.CaMKt               += stepSize * c_camk.d_camkt
    c_intracellular_ions.nai   += stepSize * c_intracellular_ions.d_nai
    c_intracellular_ions.nass  += stepSize * c_intracellular_ions.d_nass
    c_intracellular_ions.ki    += stepSize * c_intracellular_ions.d_ki
    c_intracellular_ions.kss   += stepSize * c_intracellular_ions.d_kss
    c_intracellular_ions.cass  += stepSize * c_intracellular_ions.d_cass
    c_intracellular_ions.cansr += stepSize * c_intracellular_ions.d_cansr
    c_intracellular_ions.cajsr += stepSize * c_intracellular_ions.d_cajsr
    c_intracellular_ions.cai   += stepSize * c_intracellular_ions.d_cai
    c_ina.m                    += stepSize * c_ina.d_m
    c_ina.hf                   += stepSize * c_ina.d_hf
    c_ina.hs                   += stepSize * c_ina.d_hs
    c_ina.j                    += stepSize * c_ina.d_j
    c_ina.hsp                  += stepSize * c_ina.d_hsp
    c_ina.jp                   += stepSize * c_ina.d_jp
    c_inal.mL                  += stepSize * c_inal.d_ml
    c_inal.hL                  += stepSize * c_inal.d_hl
    c_inal.hLp                 += stepSize * c_inal.d_hlp
    c_ito.a                    += stepSize * c_ito.d_a
    c_ito.iF                   += stepSize * c_ito.d_if
    c_ito.iS                   += stepSize * c_ito.d_is
    c_ito.ap                   += stepSize * c_ito.d_ap
    c_ito.iFp                  += stepSize * c_ito.d_ifp
    c_ito.iSp                  += stepSize * c_ito.d_isp
    c_ical.d                   += stepSize * c_ical.d_d
    c_ical.ff                  += stepSize * c_ical.d_ff
    c_ical.fs                  += stepSize * c_ical.d_fs
    c_ical.fcaf                += stepSize * c_ical.d_fcaf
    c_ical.fcas                += stepSize * c_ical.d_fcas
    c_ical.jca                 += stepSize * c_ical.d_jca
    c_ical.ffp                 += stepSize * c_ical.d_ffp
    c_ical.fcafp               += stepSize * c_ical.d_fcafp
    c_ical.nca                 += stepSize * c_ical.d_nca
    c_ikr.IC1                  += stepSize * c_ikr.d_ic1
    c_ikr.IC2                  += stepSize * c_ikr.d_ic2
    c_ikr.C1                   += stepSize * c_ikr.d_c1
    c_ikr.C2                   += stepSize * c_ikr.d_c2
    c_ikr.O                    += stepSize * c_ikr.d_o
    c_ikr.IO                   += stepSize * c_ikr.d_io
    c_ikr.IObound              += stepSize * c_ikr.d_iobound
    c_ikr.Obound               += stepSize * c_ikr.d_obound
    c_ikr.Cbound               += stepSize * c_ikr.d_cbound
    c_ikr.D                    += stepSize * c_ikr.d_d
    c_iks.xs1                  += stepSize * c_iks.d_xs1
    c_iks.xs2                  += stepSize * c_iks.d_xs2
    c_ik1.xk1                  += stepSize * c_ik1.d_xk1
    c_ryr.Jrelnp               += stepSize * c_ryr.d_jrelnp
    c_ryr.Jrelp                += stepSize * c_ryr.d_jrelp

#
# State vector returning function
#
def state():
    """ Returns the state vector """
    return [c_membrane.v,
        c_camk.CaMKt,
        c_intracellular_ions.nai,
        c_intracellular_ions.nass,
        c_intracellular_ions.ki,
        c_intracellular_ions.kss,
        c_intracellular_ions.cass,
        c_intracellular_ions.cansr,
        c_intracellular_ions.cajsr,
        c_intracellular_ions.cai,
        c_ina.m,
        c_ina.hf,
        c_ina.hs,
        c_ina.j,
        c_ina.hsp,
        c_ina.jp,
        c_inal.mL,
        c_inal.hL,
        c_inal.hLp,
        c_ito.a,
        c_ito.iF,
        c_ito.iS,
        c_ito.ap,
        c_ito.iFp,
        c_ito.iSp,
        c_ical.d,
        c_ical.ff,
        c_ical.fs,
        c_ical.fcaf,
        c_ical.fcas,
        c_ical.jca,
        c_ical.ffp,
        c_ical.fcafp,
        c_ical.nca,
        c_ikr.IC1,
        c_ikr.IC2,
        c_ikr.C1,
        c_ikr.C2,
        c_ikr.O,
        c_ikr.IO,
        c_ikr.IObound,
        c_ikr.Obound,
        c_ikr.Cbound,
        c_ikr.D,
        c_iks.xs1,
        c_iks.xs2,
        c_ik1.xk1,
        c_ryr.Jrelnp,
        c_ryr.Jrelp]

#
# State vector printing function
#
def print_state():
    """ Prints the current state to the screen """

    f = "{:<24}  {:<20}  {:<20}"
    print("-"*80)
    print(f.format("Name", "State value", "Derivative"))
    f = "{: <24}  {:< 20.13e}  {:< 20.13e}"
    print(f.format("membrane.v", c_membrane.v, c_membrane.d_v))
    print(f.format("CaMK.CaMKt", c_camk.CaMKt, c_camk.d_camkt))
    print(f.format("intracellular_ions.nai", c_intracellular_ions.nai, c_intracellular_ions.d_nai))
    print(f.format("intracellular_ions.nass", c_intracellular_ions.nass, c_intracellular_ions.d_nass))
    print(f.format("intracellular_ions.ki", c_intracellular_ions.ki, c_intracellular_ions.d_ki))
    print(f.format("intracellular_ions.kss", c_intracellular_ions.kss, c_intracellular_ions.d_kss))
    print(f.format("intracellular_ions.cass", c_intracellular_ions.cass, c_intracellular_ions.d_cass))
    print(f.format("intracellular_ions.cansr", c_intracellular_ions.cansr, c_intracellular_ions.d_cansr))
    print(f.format("intracellular_ions.cajsr", c_intracellular_ions.cajsr, c_intracellular_ions.d_cajsr))
    print(f.format("intracellular_ions.cai", c_intracellular_ions.cai, c_intracellular_ions.d_cai))
    print(f.format("INa.m", c_ina.m, c_ina.d_m))
    print(f.format("INa.hf", c_ina.hf, c_ina.d_hf))
    print(f.format("INa.hs", c_ina.hs, c_ina.d_hs))
    print(f.format("INa.j", c_ina.j, c_ina.d_j))
    print(f.format("INa.hsp", c_ina.hsp, c_ina.d_hsp))
    print(f.format("INa.jp", c_ina.jp, c_ina.d_jp))
    print(f.format("INaL.mL", c_inal.mL, c_inal.d_ml))
    print(f.format("INaL.hL", c_inal.hL, c_inal.d_hl))
    print(f.format("INaL.hLp", c_inal.hLp, c_inal.d_hlp))
    print(f.format("Ito.a", c_ito.a, c_ito.d_a))
    print(f.format("Ito.iF", c_ito.iF, c_ito.d_if))
    print(f.format("Ito.iS", c_ito.iS, c_ito.d_is))
    print(f.format("Ito.ap", c_ito.ap, c_ito.d_ap))
    print(f.format("Ito.iFp", c_ito.iFp, c_ito.d_ifp))
    print(f.format("Ito.iSp", c_ito.iSp, c_ito.d_isp))
    print(f.format("ICaL.d", c_ical.d, c_ical.d_d))
    print(f.format("ICaL.ff", c_ical.ff, c_ical.d_ff))
    print(f.format("ICaL.fs", c_ical.fs, c_ical.d_fs))
    print(f.format("ICaL.fcaf", c_ical.fcaf, c_ical.d_fcaf))
    print(f.format("ICaL.fcas", c_ical.fcas, c_ical.d_fcas))
    print(f.format("ICaL.jca", c_ical.jca, c_ical.d_jca))
    print(f.format("ICaL.ffp", c_ical.ffp, c_ical.d_ffp))
    print(f.format("ICaL.fcafp", c_ical.fcafp, c_ical.d_fcafp))
    print(f.format("ICaL.nca", c_ical.nca, c_ical.d_nca))
    print(f.format("IKr.IC1", c_ikr.IC1, c_ikr.d_ic1))
    print(f.format("IKr.IC2", c_ikr.IC2, c_ikr.d_ic2))
    print(f.format("IKr.C1", c_ikr.C1, c_ikr.d_c1))
    print(f.format("IKr.C2", c_ikr.C2, c_ikr.d_c2))
    print(f.format("IKr.O", c_ikr.O, c_ikr.d_o))
    print(f.format("IKr.IO", c_ikr.IO, c_ikr.d_io))
    print(f.format("IKr.IObound", c_ikr.IObound, c_ikr.d_iobound))
    print(f.format("IKr.Obound", c_ikr.Obound, c_ikr.d_obound))
    print(f.format("IKr.Cbound", c_ikr.Cbound, c_ikr.d_cbound))
    print(f.format("IKr.D", c_ikr.D, c_ikr.d_d))
    print(f.format("IKs.xs1", c_iks.xs1, c_iks.d_xs1))
    print(f.format("IKs.xs2", c_iks.xs2, c_iks.d_xs2))
    print(f.format("IK1.xk1", c_ik1.xk1, c_ik1.d_xk1))
    print(f.format("ryr.Jrelnp", c_ryr.Jrelnp, c_ryr.d_jrelnp))
    print(f.format("ryr.Jrelp", c_ryr.Jrelp, c_ryr.d_jrelp))

#
# Test step function
#
def test_step():
    """ Calculates and prints the initial derivatives """
    init()
    engine.update()
    print_state()

#
# Pacing
#
class Protocol:
    """ Holds an ordered set of ProtocolEvent objects """
    def __init__(self):
        super().__init__()
        self.head = None
    def add(self, e):
        """ Schedules an event """
        if self.head is None:
            self.head = e
            return
        if e.start < self.head.start:
            e.next = self.head
            self.head = e
            return
        f = self.head
        while (f.next is not None) and (e.start > f.next.start):
            f = f.next
        e.next = f.next
        f.next = e
    def pop(self):
        """ Returns the next event """
        e = self.head
        if self.head is not None:
            self.head = self.head.next
        return e


class ProtocolEvent:
    def __init__(self, level, start, duration, period=0, multiplier=0):
        super().__init__()
        self.level = float(level)
        self.start = float(start)
        self.duration = float(duration)
        if self.duration <= 0:
            raise Exception('Duration must be greater than zero')
        self.period = float(period)
        if self.period < 0:
            raise Exception('multiplier must be zero or greater')
        self.multiplier = int(multiplier)
        if self.multiplier < 0:
            raise Exception('Multiplier must be zero or greater')
        if self.period == 0 and self.multiplier > 0:
            raise Exception('Non-periodic event cannot occur more than once')
        self.next = None


def pacing_protocol():
    pacing = Protocol()
    pacing.add(ProtocolEvent(1.0, 100.0, 0.5, 1000.0, 0))
    return pacing

#
# Solver
#
def beat(stepSmall = 0.005, stepLarge = 0.01):
    """
    Simulates a single beat
    """
    tmin = 0
    tmax = 1000
    # Feedback
    outInt = int(math.ceil(tmax / 10.0))
    outPos = engine.time
    outVal = 0
    # Logging
    logInt = 1
    logPos = engine.time
    log = []
    # Stepsize
    stepSize = stepSmall
    hadPulse = False
    vInit = c_membrane.v
    # Pacing
    pacing = pacing_protocol()
    next = pacing.head
    while next and next.start < tmin:
        next = next.next
    if next.start < tmin:
        next = None
    fire = None
    fireDown = 0
    stopTime = min(next.start, tmin + stepSize)
    print('Starting integration with step sizes ' + str(stepSmall) + ' and ' + str(stepLarge) + '.')
    while engine.time < tmax:
        update(stopTime - engine.time)
        engine.time = stopTime
        # Event over
        if (fire and engine.time >= fireDown):
            engine.pace = 0
            fire = None
        # New event
        if (next and engine.time >= next.start):
            fire = next
            next = next.next
            engine.pace = fire.level
            fireDown = fire.start + fire.duration
            if fire.period > 0:
                if fire.multiplier == 1:
                    fire.period = 0
                else:
                    if fire.multiplier > 1:
                        fire.multiplier -=1
                    fire.start += fire.period
                    pacing.add(fire)
                    next = pacing.head
        # User feedback
        if engine.time >= outPos and outVal < 100:
            print(str(outVal) + "%")
            outVal += 10
            outPos += outInt
        # Logging
        if engine.time >= logPos:
            log.append((engine.time, state()))
            logPos += logInt
        # Step size update
        if fire: # or c_membrane.v > -70:
            if stepSize != stepSmall:
                print("Small steps")
                stepSize = stepSmall
        else:
            if stepSize != stepLarge:
                print("Big steps")
                stepSize = stepLarge
        # Set next time
        stopTime = engine.time + stepSize
        if fire and fireDown < stopTime:
            stopTime = fireDown
        if next and next.start < stopTime:
            stopTime = next.start
        if logPos < stopTime:
            stopTime = logPos
    print("100% done")
    print("t = " + str(engine.time))
    print_state()
    return log

#
# Run if loaded as main script
#
if __name__ == '__main__':
    small = 0.005
    large = 0.01
    go = True
    done = False
    while go:
        go = False
        try:
            init()
            data = beat(small, large)
            done = True
        except ArithmeticError as e:
            print('Arithmetic error occurred')
            y = 'Continue with smaller stepsize? (y/n): '
            y = input(y)
            if y.lower()[0:1] == 'y':
                small /= 2
                large /= 2
                go = True
    if done:
        print('Showing result...')
        x = []
        y = []
        for time, state in data:
            x.append(time)
            y.append(state[0])
        import matplotlib.pyplot as py
        plot = py.plot(x, y)
        py.show()
