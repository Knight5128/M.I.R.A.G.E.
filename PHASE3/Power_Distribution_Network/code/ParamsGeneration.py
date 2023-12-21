import random
import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt


def generate_random_spot_coordinate(n, m, r=750, d_min=230):
    '''
    Randomly generate coordinates for cities and potential energy supply station locations.

    - The origin coordinate represents the central city location, and subsequently, 
    several polar coordinates are randomly generated and then converted back to Cartesian coordinates.
    - The generation process uses a while loop, ensuring that the minimum distance from the newly added coordinate to the existing coordinates 
    is not less than d_min, until a sufficient number of locations are generated.

    Return a list of N two-dimensional coordinates.

    This function is a Testing | Random Generation function.
    In real cases, the list of coordinates for each location must be directly input into the model, 
    with the first location's coordinates being the origin (0,0).
    '''
    def is_valid_point(point, points, min_distance):
        return all(math.hypot(point[0] - p[0], point[1] - p[1]) >= min_distance for p in points)

    spots = [(0, 0)]

    while len(spots) < n + m:
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, r)
        new_spot = (int(distance * math.cos(angle)), int(distance * math.sin(angle)))

        if is_valid_point(new_spot, spots, d_min):
            spots.append(new_spot)

    return spots, r

def initialize_approx_pipeline_length(n, m, points):
    """
    Initialize the pipeline lengths between points based on their coordinates (assuming straight-line pipeline installation).

    - Calculate the distance between two nodes using their input coordinates as a linear distance, 
    which serves as an approximation for the pipeline length.

    Return the pipeline length 2d array: (N, N)
    
    This function is a General-Purpose | Approximate Initialization function.
    In real cases, the total length of pipelines between each point can be planned based on satellite data and input into the model. 
    If the total pipeline length is difficult to measure practically, 
    this function can be used to initialize the pipeline length between two points based on the straight-line distance between their coordinates.
    """
    N = n + m

    if len(points) != N or not all(isinstance(p, (tuple, list)) and len(p) == 2 for p in points):
        raise ValueError("Wrong Spot Coordinate Format!")

    length_matrix = np.zeros((N, N))

    for i in range(N):
        for j in range(N):
            length_matrix[i, j] = round(math.hypot(points[i][0] - points[j][0], points[i][1] - points[j][1]))

    return length_matrix

def generate_pipeline_loss_rate(n, m, lambda_max=0.25):
    """
    Initialize the pipeline loss rates.

    - Randomly generate the pipeline loss rates between two nodes. 
    - Notably, the pipeline loss rate is bidirectional and equal, meaning the loss rate is the same for both directions in a single pipeline.

    Return the pipeline loss rate 2d array: (N, N)

    This function is a Testing | Random Generation function.
    In real cases, the pipeline energy loss rate 2d array between each point must be directly input into the model.
    """
    total = m + n
    matrix = [[0 for _ in range(total)] for _ in range(total)]

    for i in range(total):
        for j in range(i+1, total):  # Only fill the upper triangle
            val = round(random.uniform(0, lambda_max), 3)
            matrix[i][j] = matrix[j][i] = val

    return np.array(matrix)

def generate_city_populations(n, mean=50000, std_dev=3500, pop_min=25000, pop_max=100000, min_n=3):
    """
    Initialize the total population numbers for each city.

    - Generate the total population for n cities randomly using a normal distribution, 
    controlling the mean and standard deviation, and appropriately increasing the variation in population numbers.
    - Limit the population numbers within the range of [pop_min, pop_max].

    Return a 1d array of population numbers: (n,)

    This function is a Testing | Random Generation function.
    In real cases, the total population 1d array for each city must be directly input into the model.
    """
    if n < min_n:
        raise ValueError(f"Number of cities must be at least {min_n} to create a meaningful distribution.")
    
    # Use a normal distribution to generate populations
    pops = np.random.normal(mean, std_dev, n)
    
    # Sort the populations and modify the extremes
    pops.sort()
    
    # Increase the population of 1-2 cities
    pops[-1] = min(pops[-1] * 1.5, pop_max)
    if n > 4:
        pops[-2] = min(pops[-2] * 1.3, pop_max)
    
    # Decrease the population of 2-3 cities
    pops[0] = max(pops[0] * 0.5, pop_min)
    pops[1] = max(pops[1] * 0.6, pop_min)
    if n > 5:
        pops[2] = max(pops[2] * 0.7, pop_min)
    
    # Ensure populations are positive and do not exceed 200,000
    pops = np.clip(pops, pop_min, pop_max)

    # Convert to integers
    pops = [int(pop) for pop in pops]

    # Place the largest population at the beginning for subsequent visualizing
    max_pop = max(pops)
    pops.remove(max_pop)
    random.shuffle(pops)
    pops.insert(0, max_pop)

    return np.array(pops)


def generate_costs(n, m, c_min=150, c_max=250, alpha=0.05):
    """
    Randomly initialize the maintenance cost per unit time for pipelines and the transportation cost per unit time per unit of energy.

    - Generate maintenance costs using a normal distribution within the range of [c_min, c_max] and 
    fill the non-diagonal elements of the maintenance cost 2d array.
    - Generate transportation costs using a normal distribution within the range of [alpha * c_min, alpha * c_max] and 
    fill the non-diagonal elements of the transportation cost 2d array.

    Return Value 1: Maintenance cost 2d array: (N, N)
    Return Value 2: Transportation cost per unit of energy 2d array: (N, N)

    This function is a Testing | Random Generation function.
    In real cases, the maintenance cost per unit time for pipelines between each point and 
    the transportation cost per unit time per unit of energy for pipelines must be directly input into the model.
    """
    size = m + n
    
    #Initialize
    maintenance_cost_matrix = np.zeros((size, size))
    flow_cost_matrix = np.zeros((size, size))
    
    #Fill Non-diagonal Elements
    for i in range(size):
        for j in range(i + 1, size):
            maintenance_cost_matrix[i, j] = maintenance_cost_matrix[j, i] = round(np.random.uniform(c_min, c_max), 1)
            flow_cost_matrix[i, j] = flow_cost_matrix[j, i] = round(np.random.uniform(c_min, c_max) * alpha, 1)
    return maintenance_cost_matrix, flow_cost_matrix


def generate_plant_cost_cut_rate_table(k, min_cost_cut=0.05, max_cost_cut=0.75):
    '''
    Randomly initialize the cost optimization indices for k different levels of energy supply stations.

    Generate k increasing values within the range of [min_cost_cut, max_cost_cut], 
    representing the cost optimization indices for supply stations from level 0 to level k-1. 
    Introduce some random fluctuations when generating each optimization index to 
    ensure the production capacity growth of supply stations at different levels is non-uniform.

    Return a 1d array representing the cost optimization indices corresponding to each level of energy supply station: (k,)

    This function is a Testing | Random Generation function.
    In real cases, the cost optimization indices corresponding to each level of energy supply station should be directly input into the model.
    '''
    if not (k >= 0 and isinstance(k, int)):
        raise ValueError("k must be a positive integer.")

    step = (max_cost_cut - min_cost_cut) / (k - 1)
    
    return np.array([(1 + random.uniform(-0.05, 0.05)) * (min_cost_cut + i * step) for i in range(k)])


def generate_plant_production_ceil_table(k, basic_ceil=2250000, growth_step_linear=0.2, growth_step_exponential=0.08, big_improvement=0):
    '''
    Randomly initialize the maximum energy production limits (per unit time) for k different levels of energy supply stations.

    Assume that the production capacity limit for a level 0 supply station is basic_ceil, 
    and successively increase to generate the maximum energy production limits corresponding to each level of energy supply station. 
        - If big_improvement = 0, the main difference between different levels of supply stations is scale, 
        hence the production capacity limit grows *linearly*.
        - If big_improvement = 1, the main difference between different levels of supply stations is technology, 
        hence the production capacity limit grows *exponentially*.

    Return a 1d array representing the production capacity limits corresponding to each level of energy supply station: (k,)

    This function is a Testing | Random Generation function.
    In real cases, the maximum energy production limits for each level of energy supply station should be directly input into the model.
    '''
    if not (k >= 0 and isinstance(k, int)):
        raise ValueError("k must be a positive integer.")

    p_ceil_table = [basic_ceil]
    for i in range(1, k):
        if big_improvement == 0:
            # Linear ceil growth
            p_ceil_table.append(p_ceil_table[i - 1] + basic_ceil * growth_step_linear)
        else:
            # Exponential ceil growth
            p_ceil_table.append(p_ceil_table[i - 1] * (1 + growth_step_exponential))

    return np.array(p_ceil_table)

    
def initialize_plant_levels(m, k):
    '''
    Randomly initialize the most suitable energy supply station levels (from 0 to k-1) for m potential energy supply station locations.

    Ensure the total level count is a positive integer and then directly generate the most suitable energy station level for each location.

    Return a 1d array indicating the most suitable energy supply station levels for each location: (m,)

    This function is a Testing | Random Generation function.
    In real cases, the appropriate levels of energy supply stations for each location should be directly input into the model.
    '''
    if not (k >= 0 and isinstance(k, int)):
        raise ValueError("k must be a positive integer.")

    return np.array([random.randint(0, k - 1) for _ in range(m)])