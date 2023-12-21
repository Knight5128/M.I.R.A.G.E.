import math
from Enumeration import get_feasible_actions_for_stage_t

def calculate_current_costs(t, x_t, y_t, params_all_stages):
    #simplify cost calculation
    
    launch_cost = params_all_stages[t-1]['c_launch'] * x_t
    manufacturing_cost = params_all_stages[t-1]['c_manu'] * y_t
    tech_investment_cost = params_all_stages[t-1]['c_tech']
    total_current_cost = launch_cost + manufacturing_cost + tech_investment_cost
    
    return total_current_cost

def get_V_for_each_state_at_stage_t(t, state_t, big_dict, params_all_stages, M=66666666666):
    #Backward Recursion
    
    feasible_actions_t, fl = get_feasible_actions_for_stage_t(t, state_t, params_all_stages)

    #if there's no plausible future state, proceed with next state at this stage
    if fl:
        big_dict[f'optimal_cost_actions_{t}'][f'{state_t}'] = (M, M, M)
        return big_dict
        
    min_cost = M
    x_t_optimal = M
    y_t_optimal = M
    for action in feasible_actions_t:
        x_t, y_t = action
        state_next = state_t - x_t + y_t
        str_state_next = str(state_next)
        if not ((state_next >= 0) and (str_state_next in big_dict[f'optimal_cost_actions_{t+1}'])):
            continue
        current_cost = calculate_current_costs(t, x_t, y_t, params_all_stages)
        future_cost = big_dict[f'optimal_cost_actions_{t+1}'][str_state_next][2]    
        total_cost = current_cost + future_cost
        if total_cost < min_cost:
            min_cost = total_cost
            x_t_optimal = x_t
            y_t_optimal = y_t

    if min_cost < M:

        big_dict[f'optimal_cost_actions_{t}'][f'{state_t}'] = (x_t_optimal, y_t_optimal, min_cost)

    else:

        big_dict[f'optimal_cost_actions_{t}'][f'{state_t}'] = (M, M, M)
    
    return big_dict

def get_V_for_each_state_at_final_stage(T, state_T, params_T, big_dict, M=66666666666):
    #Boundary Condition

    flag = 0
    g_T = params_T['g']
    theta_T = params_T['theta']
    p_T = params_T['p']
    d_T = params_T['d']
    c_manu_T = params_T['c_manu']
    c_launch_T = params_T['c_launch']
    min_launches_required = math.ceil(d_T / (p_T * g_T * theta_T))
    if state_T >= min_launches_required:
        big_dict[f'optimal_cost_actions_{T}'][f'{state_T}'] = (min_launches_required, 0, c_launch_T * min_launches_required)
        return big_dict

    else:
        if min_launches_required - state_T > params_T['m']:
            big_dict[f'optimal_cost_actions_{T}'][f'{state_T}'] = (M,M,M)
            return big_dict
            
        big_dict[f'optimal_cost_actions_{T}'][f'{state_T}'] = (min_launches_required, (min_launches_required - state_T), c_launch_T * min_launches_required + c_manu_T * (min_launches_required - state_T))
        return big_dict
    

def main_for_each_inv_ops_given(T, params_all_stages, init_params):
    #Obtain a look-up dictionary for each investment choice sequence
    
    bg_dict = {'id': 'dict_contains_all_Vs', 'investment_options': init_params['inv_all_stages']}
    for i in range(1,T+1):
        name = 'optimal_cost_actions_' + str(i)
        value_name = name
        bg_dict[name] = {}
        bg_dict[name].update({'id': value_name})  

    id_T = 'optimal_cost_actions_' + str(T)
    for i in range(init_params['max_state'] + 1):
        bg_dict = get_V_for_each_state_at_final_stage(T, i, params_all_stages[T-1], bg_dict)

    for i in range(T-1, 1, -1):
        for j in range(init_params['max_state']+1):
            bg_dict = get_V_for_each_state_at_stage_t(i, j, bg_dict, params_all_stages)

    bg_dict = get_V_for_each_state_at_stage_t(1, init_params['s0'], bg_dict, params_all_stages)

    return bg_dict