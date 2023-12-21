import numpy as np


def estimate_city_development_level(population_array, min_dev=0.60, max_dev=0.87):
    '''
    Estimate each city's "level of development" based on "the total population of the city".

    The "level of development" is valued between [min_dev, max_dev] and represents a combination of 
    the completeness of city technology and the maturity of development, positively correlated with the total population of the city. 
    It is assumed here that each city has reached a certain level of development, 
    but due to technological limitations and future prospects, none have achieved "full development".
    Furthermore, considering that in reality, a higher population in a region does not necessarily indicate a higher level of development, 
    a fluctuation term is added. The absolute size of this fluctuation does not exceed half the difference between 
    the city's level of development and the limit level (0/1).

    This function is a General-Purpose | Estimation function.
    In real cases, the city's level of development can be assessed and directly input into the model; 
    if it is difficult to assess the level of development, this function can also be used to estimate the city's level of development based on its population size.
    '''
    
    if len(population_array) == 0:
        return []

    if isinstance(population_array, list):
        population_array = np.array(population_array)

    lower_quantile = np.percentile(population_array, 25)
    upper_quantile = np.percentile(population_array, 75)

    scaled_population = (population_array - lower_quantile) / (upper_quantile - lower_quantile) * 0.5 + 0.25
    adjusted_population = scaled_population * (max_dev - min_dev) + min_dev

    adj_dev = 0.5 * min(min_dev, (1-max_dev))
    random_adjustments = np.random.uniform(-adj_dev, adj_dev, len(population_array))
    final_population = np.clip(adjusted_population + random_adjustments, min_dev, max_dev)

    city_development_levels = np.round(final_population, 2).tolist()

    return city_development_levels


def estimate_city_power_dependency(development_list, min_dep_dev=0.7, min_dep=0.1, max_dep=0.3, gamma=0.6):
    '''
    Estimate the city's "dependence on external energy inputs" based on "the level of urban development".

    Here, the following assumption is made: once a city develops to a certain stage, 
    it will rely on external energy stations for a part of its energy needs. 
    That is, the city does not need to build too many facilities for energy self-sufficiency but rather 
    focuses on the development of other aspects (such as technology). 
    The "dependence" value ranges from [min_dep, max_dep] and represents the proportion of 
    the city's own production allocated to external cities or energy supply stations. 
    The "dependence" reaches its minimum value when the city's development level is at min_dep_dev and 
    gradually increases as the deviation from min_dep_dev increases. 
    The increase in "dependence" is positively correlated with the absolute deviation between 
    the city's development level and min_dep_dev, with a correlation coefficient of gamma, which is exogenously given here.

    This function is a General-Purpose | Estimation function.
    In real cases, the city's dependence on external energy can be assessed and directly input into the model; 
    if it is difficult to assess the dependence, this function can also be used to estimate the city's energy dependence based on its level of development.
    '''
    if len(development_list) == 0:
        return []
        
    energy_dependency_list = []

    for dev in development_list:
        deviation = abs(dev - min_dep_dev)

        # Calculate the energy dependency based on the deviation, ensuring it stays within the range [min_dep,max_dep]
        dependency = round(min(((min_dep + gamma * deviation), max_dep)), 2)
        energy_dependency_list.append(dependency)

    return energy_dependency_list