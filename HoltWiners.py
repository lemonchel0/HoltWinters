class HoltWinters:
    def __init__(self, series, slen, alpha, beta, gamma, n_preds, scaling_factor=1.96):
        self.series = series
        self.slen = slen
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.n_preds = n_preds
        self.scaling_factor = scaling_factor

    def initial_trend(self):
        summ = 0.0
        for i in range(self.slen):
            summ += float(self.series[i+self.slen] - self.series[i]) / self.slen
        return summ / self.slen  

    def initial_seasonal_components(self):
        seasonals = {}
        season_averages = []
        n_seasons = int(len(self.series)/self.slen)
        for j in range(n_seasons):
            season_averages.append(sum(self.series[self.slen*j:self.slen*j+self.slen])/float(self.slen))
        for i in range(self.slen):
            sum_of_vals_over_avg = 0.0
            for j in range(n_seasons):
                sum_of_vals_over_avg += self.series[self.slen*j+i]-season_averages[j]
            seasonals[i] = sum_of_vals_over_avg/n_seasons
        return seasonals   

    def triple_exponential_smoothing(self):
        self.result = []
        self.Smooth = []
        self.Season = []
        self.Trend = []
        self.PredictedDeviation = []
        self.UpperBond = []
        self.LowerBond = []

        self.seasonals = self.initial_seasonal_components()

        for i in range(len(self.series)+self.n_preds):
            if i == 0:
                smooth = self.series[0]
                trend = self.initial_trend()
                self.result.append(self.series[0])
                self.Smooth.append(smooth)
                self.Trend.append(trend)
                self.Season.append(self.seasonals[i%self.slen])

                self.PredictedDeviation.append(0)

                self.UpperBond.append(self.result[0] + 
                                      self.scaling_factor * 
                                      self.PredictedDeviation[0])

                self.LowerBond.append(self.result[0] - 
                                      self.scaling_factor * 
                                      self.PredictedDeviation[0])

                continue
            if i >= len(self.series):
                m = i - len(self.series) + 1
                self.result.append((smooth + m*trend) + self.seasonals[i%self.slen])

                self.PredictedDeviation.append(self.PredictedDeviation[-1]*1.01) 

            else:
                val = self.series[i]
                last_smooth, smooth = smooth, self.alpha*(val-self.seasonals[i%self.slen]) + (1-self.alpha)*(smooth+trend)
                trend = self.beta * (smooth-last_smooth) + (1-self.beta)*trend
                self.seasonals[i%self.slen] = self.gamma*(val-smooth) + (1-self.gamma)*self.seasonals[i%self.slen]
                self.result.append(smooth+trend+self.seasonals[i%self.slen])

                self.PredictedDeviation.append(self.gamma * abs(self.series[i] - self.result[i]) 
                                               + (1-self.gamma)*self.PredictedDeviation[-1])

            self.UpperBond.append(self.result[-1] + 
                                  self.scaling_factor * 
                                  self.PredictedDeviation[-1])

            self.LowerBond.append(self.result[-1] - 
                                  self.scaling_factor * 
                                  self.PredictedDeviation[-1])

            self.Smooth.append(smooth)
            self.Trend.append(trend)
            self.Season.append(self.seasonals[i % self.slen])
            
    def train_new_value(self,value):
        val = value
        self.series.append(val)
        smooth = self.Smooth[-1]
        trend = self.Trend[-1]
        
        last_smooth, smooth = smooth, self.alpha*(val-self.seasonals[len(self.series)%self.slen]) + (1-self.alpha)*(smooth+trend)
        trend = self.beta * (smooth-last_smooth) + (1-self.beta)*trend
        self.seasonals[len(self.series)%self.slen] = self.gamma*(val-smooth) + (1-self.gamma)*self.seasonals[len(self.series)%self.slen]
        
        self.PredictedDeviation.append(self.gamma * abs(self.series[-1] - self.result[-1]) 
                                               + (1-self.gamma)*self.PredictedDeviation[-1])

        self.UpperBond.append(self.result[-1] + 
                              self.scaling_factor * 
                              self.PredictedDeviation[-1])

        self.LowerBond.append(self.result[-1] - 
                              self.scaling_factor * 
                              self.PredictedDeviation[-1])

        self.Smooth.append(smooth)
        self.Trend.append(trend)
        self.Season.append(self.seasonals[len(self.series) % self.slen])
        
    def forcast(self):
        m = 1
        smooth = self.Smooth[-1]
        trend = self.Trend[-1]
        self.result.append((smooth + m*trend) + self.seasonals[len(self.series)%self.slen])
        self.PredictedDeviation.append(self.PredictedDeviation[-1]*1.01) 
        return self.result[-1]