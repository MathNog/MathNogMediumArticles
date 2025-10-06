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

dates = collect(Date(1961):Month(1):Date(2000, 12));
y = vec(readdlm("TimeSeriesJulia/ScoreDrivenModels/data/nie_northeastern.csv"));

H  = 60
T  = 240
last_obs  = length(y) - H
first_obs = last_obs - T

y_train     = y[first_obs:last_obs];
y_test      = y[last_obs+1:end];

dates_train = dates[first_obs:last_obs];
dates_test  = dates[last_obs+1:end];

p_lags  = [1, 12]
q_lags  = [1, 12]
distrib = Distributions.LogNormal
d       = 0.0

gas = ScoreDrivenModel(p_lags, q_lags, distrib, d; time_varying_params = [1, 2]);

# Fit the models
fit_gas = fit!(gas, y_train);
forecast_gas = forecast(y_train, gas, H; S=1000);

point_forecast = forecast_gas.observation_forecast;
scenarios      = forecast_gas.observation_scenarios;
quantiles_obs  = forecast_gas.observation_quantiles;
fitted_values  = fitted_mean(gas, y_train);

# Results
results_gas = results(fit_gas)

# Residuals
q_residuals   = quantile_residuals(y_train, gas);
std_residuals = pearson_residuals(y_train, gas);

pq = plot(dates_train[25:end], q_residuals, title = "Quantile Residuals", xlabel = "Date", ylabel = "Value", label = "")
savefig(pq, "output/q_residuals.png")
pr = plot(dates_train[25:end], std_residuals, title = "Pearson Residuals", xlabel = "Date", ylabel = "Value", label = "")
savefig(pr, "output/pearson_residuals.png")

plot(fit_gas, size=(1000, 1000), title = "Residuals Diagnostics")
savefig("output/residuals_diagnostics.png")


first_index = 100
gas_cv = cross_validation(gas, y_train, H, first_index);


cv_abs_errors = gas_cv.abs_errors
cv_mean_crps  = gas_cv.mean_crps
cv_mae        =  gas_cv.mae

H, W = size(cv_abs_errors)

plot(1:H, mean(cv_abs_errors, dims=2), title = "Mean Absolute Error across all $W windows by $H steps ahead", xlabel = "Window", ylabel = "Mean Absolute Error", label = "")
plot(1:H, cv_mean_crps, dims=2, title = "Mean CRPS across all $W windows by $H steps ahead", xlabel = "Window", ylabel = "Mean CRPS", label = "")
plot(1:H, cv_mae, title = "MAE across all $W windows by $H steps ahead", xlabel = "Window", ylabel = "MAE", label = "")
