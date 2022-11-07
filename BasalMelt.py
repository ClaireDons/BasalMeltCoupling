class BasalMelt:
    # Parameters to compute basal ice shelf melt (Favier 2019)
    rho_i = 917. #ice density kg m-3
    rho_sw = 1028. # sea water density
    c_po = 3974. # specific heat capacity of ocean mixed layer J kg-1 K-1
    L_i = 3.34*10**5 # latent heat of fusion of ice
    Tf = -1.6
    baseline = 1

    def __init__(self,gamma,thetao):
        self.gamma = gamma
        self.thetao = thetao
        

    def calc_cquad(self):
        c_lin = (self.rho_sw*self.c_po)/(self.rho_i*self.L_i)
        c_quad = (c_lin)**2
        return c_quad


    def quadBasalMeltAnomalies(self):
        ## Compute quadratic basal melt anomalies with gamma
        c_quad = self.calc_cquad()
        ms = self.gamma * 10**5 * c_quad # Quadratic constant
        # Quadratic melt baseline (negative if To < Tf)
        BM_base = (self.baseline - self.Tf)*(abs(self.baseline) - self.Tf) * ms
        # Compute basal melt
        BM = (self.thetao - self.Tf) * (abs(self.thetao) - self.Tf) * ms  
        # Compute basal melt anomalies
        dBM = BM - BM_base
        return dBM
    pass