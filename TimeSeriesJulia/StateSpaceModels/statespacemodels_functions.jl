# # Use the packages
# using StateSpaceModels, DataFrames, CSV, Plots

"""
    plot_time_series(time_series, x_axis, y_axis, title, x_label, y_label; test_length=0)

Plot a time series with a specified test length.

# Parameters
- `time_series`: DataFrame containing the time series data
- `x_axis`: String representing the column name for the x-axis
- `y_axis`: String representing the column name for the y-axis
- `title`: String representing the title of the plot
- `x_label`: String representing the label for the x-axis
- `y_label`: String representing the label for the y-axis
- `test_length`: Int64 representing the length of the test period (default=0)

# Returns
- A plot of the time series with the specified test length
"""
function plot_time_series(time_series::DataFrame, x_axis::String, y_axis::String,
                        title::String, x_label::String, y_label::String;
                        test_length::Int64 = 0)

    # Split the time series into training and testing sets
    time_series_train = time_series[1:end - test_length, :]
    time_series_test = time_series[end - test_length + 1:end, :]
    
    # Plot the time series
    plot(time_series[:, x_axis], time_series[:, y_axis], title = title, label = "", xlabel = x_label, ylabel = y_label)
    plot!(time_series_test[:, x_axis], time_series_test[:, y_axis], title = title, label = "Test", xlabel = x_label, ylabel = y_label)
end

"""
    time_series_split(time_series, test_length)

Split a time series into training and testing sets.

# Parameters
- `time_series`: DataFrame containing the time series data
- `test_length`: Int64 representing the length of the test period

# Returns
- A tuple containing the training and testing sets
"""
function time_series_split(time_series::DataFrame, test_length::Int64)
    # Split the time series into training and testing sets
    train_series = time_series[1:end - test_length, :]
    test_series = time_series[end - test_length + 1:end, :]
    
    return train_series, test_series
end


# Get the predictive, filtered and smoothed states
"""
    get_components_from_states(states::Matrix{Fl}) where {Fl}

Get the level, slope and seasonality components from a matrix of states.

# Parameters
- `states`: Matrix of states

# Returns
- The level, slope and seasonality components
"""
function get_components_from_states(states::Matrix{Fl}) where {Fl}
    level       = states[:, 1];
    slope       = states[:, 2];
    seasonality = sum(states[:, i] for i in collect(3:13));

    return level, slope, seasonality
end

"""
    plot_component(dates, mean_component, type, component)

Plot a single component of a time series.

# Parameters
- `dates`: Array of dates corresponding to the components
- `mean_component`: Array representing the mean values of the component
- `type`: String indicating the type of the plot
- `component`: String representing the name of the component

# Returns
- A plot of the specified component
"""
function plot_component(dates, mean_component, type, component)
    p = plot(dates, mean_component, title = "$(type) $(component)", label = "", formatter = :plain)
    return p
end

"""
    plot_components(dates, level, slope, seasonality, type)

Plot all the components of a time series decomposition.

# Parameters
- `dates`: Array of dates corresponding to the components
- `level`: Array representing the level component
- `slope`: Array representing the slope component
- `seasonality`: Array representing the seasonality component
- `type`: String indicating the type of the plot

# Returns
- A plot of all the components
"""
function plot_components(dates, level, slope, seasonality, type)

    T = length(dates)
    p_level       = plot_component(dates[end-T+13:end], level[end-T+13:end], type, "Level")
    p_slope       = plot_component(dates[end-T+13:end], slope[end-T+13:end], type, "Slope")
    p_seasonality = plot_component(dates[end-T+13:end], seasonality[end-T+13:end], type, "Seasonality")

    p_compontens = plot(p_level, p_slope, p_seasonality, layout = (3, 1), size = (900, 600))
    return p_compontens
end


"""
    plot_forecast(time_series_train::DataFrame, time_series_test::DataFrame, 
                    expected_value::Vector{Fl}, scenarios::Matrix{Fl}, 
                    title::String, x_axis::String, y_axis::String,
                    x_label::String, y_label::String)

Plot the forecast of a time series with a specified test length.

# Parameters
- `time_series_train`: DataFrame containing the time series data used for training
- `time_series_test`: DataFrame containing the time series data used for testing
- `expected_value`: Vector representing the expected values of the time series
- `scenarios`: Matrix representing the different scenarios of the time series
- `title`: String representing the title of the plot
- `x_axis`: String representing the column name for the x-axis
- `y_axis`: String representing the column name for the y-axis
- `x_label`: String representing the label for the x-axis
- `y_label`: String representing the label for the y-axis

# Returns
- A plot of the forecasted time series with a specified test length
"""
function plot_forecast(time_series_train::DataFrame, time_series_test::DataFrame, 
                        expected_value::Vector{Fl}, scenarios::Matrix{Fl}, 
                        title::String, x_axis::String, y_axis::String,
                        x_label::String, y_label::String) where Fl
    p = plot(time_series_train[:, x_axis], time_series_train[:, y_axis], title = title, label = "Passengers", xlabel = x_label, ylabel = y_label, color = :black, size = (1000, 600))
    p = plot!(time_series_test[:, x_axis], scenarios, color = :lightgray, label = "")
    p = plot!(time_series_test[:, x_axis], time_series_test[:, y_axis], label = "", color = :black)
    p = plot!(time_series_test[:, x_axis], expected_value, label = "Expected Value", color = :red)
    return p
end
