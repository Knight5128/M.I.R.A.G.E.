import numpy as np


def solution_consistency_two_models(x_ins_sol, x_ins_sol_pyomo, 
                                x_out_sol, x_out_sol_pyomo, 
                                y_sol, y_sol_pyomo, 
                                p_sol, p_sol_pyomo, 
                                minimum_total_cost_per_unit_time, minimum_total_cost_per_unit_time_pyomo, 
                                epsilon):
    '''
    Verify whether the results calculated by two different optimization modeling models are consistent
    For 2d arrays, error <-- sum of squared errors of corresponding elements at each position
    For 1d arrays, error <-- sum of squared errors of corresponding elements at each position
    For numerical values, error <-- absolute error

    This function is a General-Purpose | Consistency Verification function.
    '''
    
    def calc_2d_array_error(arr1, arr2):
        print(arr1)
        print(arr2)
        return np.sqrt(np.sum((arr1 - arr2) ** 2))

    def calc_1d_array_error(arr1, arr2):
        return np.sqrt(np.sum((arr1 - arr2) ** 2))

    flag = 1
    x_ins_ptf, x_out_ptf, y_ptf, p_ptf, min_cost_ptf = 0, 0, 0, 0, 0

    if calc_2d_array_error(x_ins_sol, x_ins_sol_pyomo) > epsilon:
        flag = 0 
        x_ins_ptf = 1
        print('x_ins is inconsistent!!!')
    if calc_2d_array_error(x_out_sol, x_out_sol_pyomo) > epsilon:
        flag = 0
        x_out_ptf = 1
        print('x_out is inconsistent!!!')
    if calc_2d_array_error(y_sol, y_sol_pyomo) > epsilon:
        flag = 0
        y_ptf = 1
        print('y is inconsistent!!!')
    if calc_1d_array_error(p_sol, p_sol_pyomo) > epsilon:
        flag = 0
        p_ptf = 1
        print('p is inconsistent!!!')
    if abs(minimum_total_cost_per_unit_time - minimum_total_cost_per_unit_time_pyomo) > epsilon:
        flag = 0
        min_cost_ptf = 1
        print('min_cost is inconsistent!!!')

    return flag, x_ins_ptf, x_out_ptf, y_ptf, p_ptf, min_cost_ptf
