import Pkg
path = pwd()*"/TimeSeriesJulia/ScoreDrivenModels/"
Pkg.activate(path)
Pkg.instantiate()

using Dates
using Plots
using ScoreDrivenModels
using DelimitedFiles
using Distributions

plotlyjs()

dates = collect(Date(1961):Month(1):Date(2000, 12))
y = vec(readdlm(path * "data/nie_northeastern.csv"))

plot(dates, y, title="Brazil Northeastern Natural Inflow Energy", xlabel="Date", ylabel="Value")

# Define a ScoreDrivenModel
p_lags = [1, 12]
q_lags = [1, 12]
d = 1.0
gas_normal_mean_tv = ScoreDrivenModel(p_lags, q_lags, Distributions.Normal, d; time_varying_params=[1])
gas_normal_full_tv = ScoreDrivenModel(p_lags, q_lags, Distributions.Normal, d)
gas_lognormal_mean_tv = ScoreDrivenModel(p_lags, q_lags, Distributions.LogNormal, d; time_varying_params=[1])
gas_lognormal_full_tv = ScoreDrivenModel(p_lags, q_lags, Distributions.LogNormal, d)

# Fit the models
fit_gas_normal_mean_tv = fit!(gas_normal_mean_tv, y)
fit_gas_normal_full_tv = fit!(gas_normal_full_tv, y)
fit_gas_lognormal_mean_tv = fit!(gas_lognormal_mean_tv, y)
fit_gas_lognormal_full_tv = fit!(gas_lognormal_full_tv, y)

# Fitted mean
fitted_mean_normal_mean_tv = fitted_mean(gas_normal_mean_tv, y)
fitted_mean_normal_full_tv = fitted_mean(gas_normal_full_tv, y)
fitted_mean_lognormal_mean_tv = fitted_mean(gas_lognormal_mean_tv, y)
fitted_mean_lognormal_full_tv = fitted_mean(gas_lognormal_full_tv, y)

# Results
results_mean_normal_mean_tv = results(fit_gas_normal_mean_tv)

# Residuals
q_residuals_normal_mean_tv       = quantile_residuals(y, gas_normal_mean_tv);
pearson_residuals_normal_mean_tv = pearson_residuals(y, gas_normal_mean_tv);

# Forecast
forecast_normal_mean_tv = forecast(y, gas_normal_mean_tv, 60; S=1000)

# score!

cv_normal_mean_tv = cross_validation(gas_normal_mean_tv, y, 60, 400);