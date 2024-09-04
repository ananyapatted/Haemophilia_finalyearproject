from scipy.interpolate import interp1d
import numpy as np

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

from fractions import Fraction

def calculate_average(data):
    # Calculating the quotient for each index
    quotients = [data['plasma'][i] / data['reference'][i] for i in range(len(data['reference']))]

    # Calculating the average of these quotients
    average_quotient = sum(quotients) / len(quotients)
    return average_quotient

# def find_intersection_x(x_data, reference_y, test_y):
#     # Logarithm of x_data
#     log_x = np.log10(x_data)

#     # Create interpolation functions for the reference and test data
#     reference_interp = interp1d(log_x, reference_y, kind='linear', fill_value="extrapolate")
#     test_interp = interp1d(log_x, test_y, kind='linear', fill_value="extrapolate")

#     # Find the y-value of the test data at x = 1/10
#     log_x_target = np.log10(1/10)
#     y_test_at_x10 = test_interp(log_x_target)

#     # Extend the range of x-values to ensure we can find an intersection
#     extended_x_values = np.logspace(np.log10(min(x_data)), np.log10(max(x_data)), num=1000)
#     log_extended_x_values = np.log10(extended_x_values)
#     extended_y_values_reference = reference_interp(log_extended_x_values)

#     # Find the x-value where the extended reference line has the same y-value
#     x_value_intersection = extended_x_values[np.abs(extended_y_values_reference - y_test_at_x10).argmin()]
    
#     return x_value_intersection

def find_intersection_x(x_data, reference_y, test_y):
    # Convert x_data to logarithmic scale
    log_x = np.log10(x_data)

    # Interpolate the reference and test data
    reference_interp = interp1d(log_x, reference_y, kind='linear', fill_value="extrapolate")
    test_interp = interp1d(log_x, test_y, kind='linear', fill_value="extrapolate")

    # Define the maximum log x-value for the line
    log_x_max = np.max(log_x)
    
    # Extend the range of log x-values to cover more ground
    extended_log_x = np.linspace(np.min(log_x), log_x_max, 1000)
    extended_x = np.power(10, extended_log_x)

    # Interpolate on the extended range
    extended_y_reference = reference_interp(extended_log_x)
    extended_y_test = test_interp(extended_log_x)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(extended_x, extended_y_reference, label="Reference", color="blue")
    plt.plot(extended_x, extended_y_test, label="Test", color="red")
    
    # Find the x_max in original scale
    x_max = np.power(10, log_x_max)

    # Find y-values at x_max for both lines
    y_ref_at_x_max = reference_interp(log_x_max)
    y_test_at_x_max = test_interp(log_x_max)

    # Draw vertical line at x_max
    plt.axvline(x=x_max, color='gray', linestyle='--', label="Line from x_max")

    # Draw horizontal line from test line intersection at x_max to reference line
    plt.axhline(y=y_test_at_x_max, color='green', linestyle=':', label="Line from test at x_max")
    
    # Find intersection of horizontal line with reference line
    idx = np.abs(extended_y_reference - y_test_at_x_max).argmin()
    x_intersection = extended_x[idx]

    # Mark intersection points
    plt.scatter([x_max, x_intersection], [y_test_at_x_max, y_test_at_x_max], color='purple', zorder=5)
    plt.scatter(x_intersection, y_test_at_x_max, color='orange', zorder=5)

    # Plot annotations
    # plt.xlabel("x-axis (log scale)")
    # plt.ylabel("y-axis")
    # plt.xscale('log')
    # plt.title("Intersection Analysis")
    # plt.legend()
    # plt.grid(True)
    # plt.show()

    return x_intersection

def calculate_dosage(x,weight):
    f = (x * weight)
    return f*0.5, f


def check_values(data):
    threshold = len(data['reference']) // 2
    # Initialize a counter for tracking how many values meet the condition
    count_smaller = 0
    
    # Iterate through both lists using zip to get pairs of values from 'reference' and 'plasma'
    for ref, plasma in zip(data['reference'], data['plasma']):
        # Check if the 'plasma' value is smaller than the 'reference' value
        if plasma <= ref:
            count_smaller += 1
            # If at least 2 values are found to be smaller, return True immediately
            if count_smaller >=threshold:
                return True
    
    # Return False if less than 2 values are smaller
    return False


def severity_calulation(data):
    if(check_values(data)):
        return 50, 0, 0
    data['values'] = [eval(fraction) for fraction in data['values']]
    reference_y = data['reference']
    test_y = data['plasma']
    x_value_average = calculate_average(data)
    x_data = data['values']
    x_value_intersection = (find_intersection_x(x_data, reference_y, test_y)) * 100
    print(x_value_intersection)
    #x_value_intersection = (int(data['f8_constant']) * x_value_intersection)
    if(x_value_intersection > 2):
        severity = x_value_intersection
    else:
        severity = ((x_value_average + x_value_intersection)/2)
    x_value_intersection = (int(data['f8_constant']) * severity) /100
    f8, f9 = calculate_dosage(x_value_intersection,data['weight'])
    return x_value_intersection, f8, f9



