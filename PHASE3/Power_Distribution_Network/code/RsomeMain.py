from ParamsGeneration import initialize_approx_pipeline_length, initialize_plant_levels, generate_city_populations, generate_costs, generate_pipeline_loss_rate, generate_plant_cost_cut_rate_table, generate_plant_production_ceil_table, generate_random_spot_coordinate
from PowerVolumeEstimation import estimate_power_consumption, estimate_power_production, estimate_required_power_surplus
from DevDepLevelEstimation import estimate_city_development_level, estimate_city_power_dependency
from PyomoMain import min_cost_power_flow_optimization_pyomo_main
from CrossValidation import solution_consistency_two_models
from rsome import ro, grb_solver as grb
import numpy as np


def min_cost_power_flow_optimization_rsome_main(n, m, k, pops=None, dev_levels=None, dep_levels=None, coords=None, 
                                                lambda_matrix=None, length_matrix=None, 
                                        cmaint_matrix=None, cflow_matrix=None, 
                                        p_array=None, d_array=None, s_array=None, 
                                        plant_levels=None, plant_cost_cut_rate_table=None, plant_production_ceil_table=None,
                                        realcase=0, test=0, doublecheck=0, random_seed=666, epsilon=1):

    N = n + m
    M = 100000000
    
    #Simulated case, no need to put in all parameters
    if realcase == 0:

        omega = 0.1
        c_city = 200
        c_plant = 1000
        
        if pops is None:
            pops = generate_city_populations(n)
        if coords is None:
            coords, map_r = generate_random_spot_coordinate(n, m)
        if dev_levels is None:
            dev_levels = estimate_city_development_level(pops)
        if dep_levels is None:
            dep_levels = estimate_city_power_dependency(dev_levels)
        if lambda_matrix is None:
            lambda_matrix = generate_pipeline_loss_rate(n, m)
        if length_matrix is None:
            length_matrix = initialize_approx_pipeline_length(n, m, coords)
        if cmaint_matrix is None:
            cmaint_matrix = generate_costs(n, m)[0]
        if cflow_matrix is None:
            cflow_matrix = generate_costs(n, m)[1]
        if p_array is None:
            p_array = estimate_power_production(pops, dep_levels)
        if d_array is None:
            d_array = estimate_power_consumption(pops, dev_levels)
        if s_array is None:
            s_array = estimate_required_power_surplus(pops, n, m, dev_levels)
        if plant_levels is None:
            plant_levels = initialize_plant_levels(m, k)
        if plant_cost_cut_rate_table is None:
            plant_cost_cut_rate_table = generate_plant_cost_cut_rate_table(k)
        if plant_production_ceil_table is None:
            plant_production_ceil_table = generate_plant_production_ceil_table(k, big_improvement=0)
            
    #Real case, must self-input all measurable parameters
    if realcase == 1:
        
        omega = input('omega-->')
        c_city = input('c_city-->')
        c_plant = input('c_plant-->')
        map_r = input('map_r-->')
        
        if any(param is None for param in [pops, coords, lambda_matrix, cmaint_matrix, cflow_matrix, plant_levels, plant_cost_cut_rate_table, plant_production_ceil_table]):
            raise ValueError("Please input all relevant params that can be directly measured or evaluated!")
        if dev_levels is None:
            dev_levels = estimate_city_development_level(pops)
        if dep_levels is None:
            dep_levels = estimate_city_power_dependency(dev_levels)
        if length_matrix is None:
            length_matrix = initialize_approx_pipeline_length(n, m, coords)
        if p_array is None:
            p_array = estimate_power_production(pops, dep_levels)
        if d_array is None:
            d_array = estimate_power_consumption(pops, dev_levels)
        if s_array is None:
            s_array = estimate_required_power_surplus(pops, n, m, dev_levels)
        if plant_levels is None:
            plant_levels = initialize_plant_levels(m, k)
        if plant_cost_cut_rate_table is None:
            plant_cost_cut_rate_table = generate_plant_cost_cut_rate_table(k)
        if plant_production_ceil_table is None:
            plant_production_ceil_table = generate_plant_production_ceil_table(k, big_improvement=0)

    

    #Check the dimension of self-input parametres
    if not (isinstance(pops, np.ndarray) and pops.shape == (n,)):
        raise ValueError("pops should be a np.1darray with a dimension of (n,).")
    for matrix_name, matrix in zip(["lambda_matrix", "length_matrix", "cmaint_matrix", "cflow_matrix"], 
                               [lambda_matrix, length_matrix, cmaint_matrix, cflow_matrix]):
        if not (isinstance(matrix, np.ndarray) and matrix.shape == (N, N)):
            raise ValueError(f"{matrix_name} should be a bp.2darray with a dimension of (N, N).")
    for arr_name, arr in zip(["p_array", "d_array"], [p_array, d_array]):
        if not (isinstance(arr, np.ndarray) and arr.shape == (n,)):
            raise ValueError(f"{arr_name} should be a np.1darray with a dimension of (n,).")
    if not (isinstance(s_array, np.ndarray) and s_array.shape == (N,)):
        raise ValueError("s_array should be a np.1darray with a dimension of (N,)")
    if not (isinstance(coords, list) and all(isinstance(item, tuple) and len(item) == 2 for item in coords)):
        raise ValueError("coords must be a list of length N with each element being a 2-tuple.")
    for param in [dev_levels, dep_levels]:
        if not ((isinstance(param, list) or isinstance(param, np.ndarray)) and len(param) == n):
            raise ValueError("dev_levels and dep_levels must be lists or np.ndarrays of length n.")
    if not ((isinstance(plant_levels, list) or isinstance(plant_levels, np.ndarray)) and len(plant_levels) == m):
        raise ValueError("plant_levels must be a list or np.ndarray of length m.")
    for param in [plant_cost_cut_rate_table, plant_production_ceil_table]:
        if not ((isinstance(param, list) or isinstance(param, np.ndarray)) and len(param) == k):
            raise ValueError("plant_cost_cut_rate_table and plant_production_ceil_table must be lists or np.ndarrays of length k.")
            
    
    # Model 
    model = ro.Model('Minimum Cost Power Flow Optimization Model')
    
    # Decision variables
    x_ins = model.dvar((N, N), vtype='C')
    x_out = model.dvar((N, N), vtype='C')
    y = model.dvar((N, N), vtype='B')
    p = model.dvar(m, vtype='C')

    # Objective function
    objective = sum(p[i-n] * (1 - plant_cost_cut_rate_table[plant_levels[i-n]]) * c_plant for i in range(n, N))
    objective += sum(y[i, j] * length_matrix[i, j] * cmaint_matrix[i, j] for i in range(N) for j in range(i+1, N))
    objective += sum(0.5 * length_matrix[i, j] * cflow_matrix[i, j] * (x_out[i, j] + x_ins[j, i] + x_out[j, i] + x_ins[i, j]) for i in range(N) for j in range(i+1, N))
    objective += sum([ep * (1 - omega * dv) * c_city for ep, dv in zip(p_array.tolist(), dev_levels)])
    
    model.min(objective)

    # Constraints
    for i in range(N):
        for j in range(N):
            if i != j:
                model.st(x_ins[i, j] == x_out[i, j] * (1 - lambda_matrix[i, j]))
                model.st(x_ins[i, j] <= M * y[i, j])
                model.st(x_out[i, j] <= M * y[i, j])
                model.st(x_ins[i, j] >= 0)
                model.st(x_out[i, j] >= 0)
                model.st(y[i, j] == y[j, i])
            if i == j:
                model.st(x_ins[i, j] == 0)
                model.st(x_out[i, j] == 0)
                model.st(y[i, j] == 0)

    for j in range(0, n):
        model.st(sum(x_ins[i, j] for i in range(N)) + p_array[j] >= s_array[j] + d_array[j] + sum(x_out[j, i] for i in range(N)))
    for j in range(n, N):
        model.st(sum(x_ins[i, j] for i in range(N)) + p[j-n] >= s_array[j] + sum(x_out[j, i] for i in range(N)))
        model.st(p[j-n] >= 0)
        model.st(p[j-n] <= plant_production_ceil_table[plant_levels[j-n]])
    
        
    # Solving
    model.solve(grb)

    # Extract the solution
    x_ins_sol = x_ins.get()
    x_out_sol = x_out.get()
    y_sol = y.get()
    p_sol = p.get()
    minimum_total_cost_per_unit_time = model.get()

    
    if doublecheck:
        #If cross-validation is needed, then extract the solution from a different approach
        (x_ins_sol_pyomo, x_out_sol_pyomo, y_sol_pyomo, p_sol_pyomo, minimum_total_cost_per_unit_time_pyomo) = min_cost_power_flow_optimization_pyomo_main(n, m, k, c_city, c_plant, omega, 
                                                                                                            pops, dev_levels, dep_levels,
                                                                                                            lambda_matrix, length_matrix, 
                                                                                                            cmaint_matrix, cflow_matrix,
                                                                                                            p_array, d_array, s_array, 
                                                                                                            plant_levels, plant_cost_cut_rate_table, plant_production_ceil_table, 
                                                                                                            random_seed)

        #check if the solutions are identical
        (is_consistent, x_ins_ptf, x_out_ptf, y_ptf, p_ptf, min_cost_ptf) = solution_consistency_two_models(x_ins_sol, x_ins_sol_pyomo, 
                                                                                               x_out_sol, x_out_sol_pyomo, 
                                                                                               y_sol, y_sol_pyomo, 
                                                                                               p_sol, p_sol_pyomo, 
                                                                                               minimum_total_cost_per_unit_time, minimum_total_cost_per_unit_time_pyomo, 
                                                                                               epsilon)
        if realcase == 0:
        
            if is_consistent:
            
                # Print the initial parameters to verify their validity
                if test == 1:
                    print()
                    print(f'populations of {n} cities:', pops,
              'coordinates of {N} spots:', coords,
              'power attrition rate:', lambda_matrix, 
              'pipe total length between 2 spots:', length_matrix, 
              'pipe maintenance cost per unit time:', cmaint_matrix, 
              'power flow cost per power unit per unit time:', cflow_matrix, 
              'city total power production per unit time:', p_array, 
              'city total power demand per unit time:', d_array, 
              'total required power surplus per unit time:', s_array, 
              sep='\n\n', end='\n')

                # Print the solution (for demonstration purposes)
                print('-'*100, end='\n')
                print("x_ins:", x_ins_sol.astype(int), sep='\n', end='\n')
                print("x_out:", x_out_sol.astype(int), sep='\n', end='\n')
                print("y:", y_sol.astype(int), sep='\n', end='\n')
                print("p:", p_sol.astype(int), sep='\n', end='\n')
                print("min_total_cost_per_unit_time:\n$", minimum_total_cost_per_unit_time, sep='')

            else:
                flags = [x_ins_ptf, x_out_ptf, y_ptf, p_ptf, min_cost_ptf]
                ptf_l = [x_ins_sol, x_ins_sol_pyomo, x_out_sol, x_out_sol_pyomo, y_sol, y_sol_pyomo, p_sol, p_sol_pyomo, minimum_total_cost_per_unit_time, minimum_total_cost_per_unit_time_pyomo]
                for i in range(len(flags)):
                    if flags[i]:
                        print(ptf_l[2*i], ptf_l[2*i+1], sep='\n', end='\n')

        else:
        
            if is_consistent:
            
                flags = [x_ins_ptf, x_out_ptf, y_ptf, p_ptf, min_cost_ptf]
                ptf_l = [x_ins_sol, x_ins_sol_pyomo, x_out_sol, x_out_sol_pyomo, y_sol, y_sol_pyomo, p_sol, p_sol_pyomo, minimum_total_cost_per_unit_time, minimum_total_cost_per_unit_time_pyomo]
                for i in range(len(flags)):
                    if flags[i]:
                        print(ptf_l[2*i], ptf_l[2*i+1], sep='\n', end='\n')
        
    else:
        # If there's no need to cross validate, then just print the solution (for demonstration purposes)
            print('-'*100, end='\n')
            print("x_ins:", x_ins_sol.astype(int), sep='\n', end='\n')
            print("x_out:", x_out_sol.astype(int), sep='\n', end='\n')
            print("y:", y_sol.astype(int), sep='\n', end='\n')
            print("p:", p_sol.astype(int), sep='\n', end='\n')
            print("min_total_cost_per_unit_time:\n$", minimum_total_cost_per_unit_time, sep='')

    return x_ins_sol, x_out_sol, y_sol, p_sol, minimum_total_cost_per_unit_time, (pops, coords, p_array, map_r)