import numpy as np
import random
import math


def estimate_power_consumption(population_list, development_list, beta=1.023, max_error_ratio=0.04):
    '''
    Estimate the total energy consumption of a city per unit time based on the city's total population & level of development.

    This function is a General-Purpose | Estimation function.
    In real cases, an estimation of the city's total energy consumption per unit time can be made by 
    conducting regression analysis on the city's total population and the total energy consumption per unit time,
    and then estimating it directly through the regression model.
    If a strong correlation is hard to find, this function can also be used to 
    estimate the city's total energy consumption per unit time based on the city's total population & level of development.
    '''
    magni_1 = 75
    
    if len(population_list) != len(development_list):
        raise ValueError("Population and development level lists must be of the same length.")

    basic_energy_consumption = [magni_1 * (pop**beta) * dev for pop, dev in zip(population_list, development_list)]
    energy_consumption_with_error = [int(consumption * (1 + random.uniform(-max_error_ratio, max_error_ratio))) for consumption in basic_energy_consumption]

    return np.array(energy_consumption_with_error)


def estimate_power_production(population_list, energy_dependency_list, theta=0.94, max_error_ratio=0.04):
    '''
    Estimate the total energy output of a city per unit time based on the city's total population & the city's dependence on external energy inputs.

    This function is a General-Purpose | Estimation function.
    In real cases, an estimation of the city's total energy output per unit time can be made by 
    conducting regression analysis on the city's total population and the total energy output per unit time,
    and then estimating it directly through the regression model.
    If a strong correlation is hard to find, this function can also be used to 
    estimate the city's total energy output per unit time based on the city's total population & its external energy dependence.
    '''
    magni_2 = 110
    
    if len(population_list) != len(energy_dependency_list):
        raise ValueError("Population and energy dependency lists must be of the same length.")

    basic_energy_production = [magni_2 * (pop**theta) * (1 - dep) for pop, dep in zip(population_list, energy_dependency_list)]
    energy_production_with_error = [int(production * (1 + random.uniform(-max_error_ratio, max_error_ratio))) for production in basic_energy_production]

    return np.array(energy_production_with_error)
    
    
def estimate_required_power_surplus(population_list, n, m, development_list, delta=0.4, max_error_ratio=0.04, plant_energy_discount_ratio=0.5):
    '''
    Estimate the total required energy surplus of a city per unit time based on the city's total population & level of development.

    This function is a General-Purpose | Estimation function.
    In real cases, an estimation of the total required energy surplus of a city per unit time can be made by 
    conducting regression analysis on the city's total population and the total required energy surplus per unit time, 
    and then estimating it directly through the regression model.
    If a strong correlation is hard to find, this function can also be used to 
    estimate the city's total required energy surplus per unit time based on the city's total population & level of development.
    '''
    magni_3 = 200
    magni_4 = 80

    required_energy_surplus_basic = [(magni_3 * math.log(pop) * dev + magni_4 * delta * dev * pop) for pop, dev in zip(population_list, development_list)]
    required_energy_surplus_with_error = [int(sp * (1 + random.uniform(-max_error_ratio, max_error_ratio))) for sp in required_energy_surplus_basic]

    basic_required_plant_surplus = plant_energy_discount_ratio * sum(required_energy_surplus_with_error) / m
    for i in range(m):
        required_energy_surplus_with_error.append(basic_required_plant_surplus * (1 + random.uniform(-max_error_ratio, max_error_ratio)))
    
    return np.array(required_energy_surplus_with_error)