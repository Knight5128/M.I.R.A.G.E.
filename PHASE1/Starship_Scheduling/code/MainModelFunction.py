from time import perf_counter
from Enumeration import generate_inv_sequences
from ParamsInitialization import g_whole_period, initialize_initial_parameters, get_params_for_all_stages
from Recursion import main_for_each_inv_ops_given

def main(T, tech_investments_table, tech_growth_table, s_0, n_0, 
         alpha, beta, c_launch_0, c_manu_0, p_0, theta_0,
        Pad_available_agenda, manu_limit_table, demand_table):

    """
    Parameter that can be directly derived from initial problem：
    tech_investments_table:   K tech investment options in each window period
    tech_growth_table:        K (g_t+1 - g_t) corresponding to investment in each window period
    T:                        required total n of window periods
    Pad_available_agenda:     launch pad available in each window period
    s_0:                      n of Starships available at the beginning of the project
    n_0:                      maximum n of launches a launch pad can accommmodate
    c_launch_0:               initial cost of launch a rocket
    c_manu_0:                 initial cost of build a new rocket
    p_0:                      initial payload of a rocket (≈200)
    theta_0:                  initial resource retention rate (<1)
    manu_limit_table:         maximum n of new Starships that can be built in each window period
    demand_table:             minimum resources demands in each window period
    
    Estimated Parameters:
    alpha:                    The coefficient of positive correlation between c_launch_cut_rate_t & g_t
    beta:                     The coefficient of positive correlation between c_manu_cut_rate_t & g_t
    """
    
    K = min(len(tech_investments_table), len(tech_growth_table))

    global_min_cost = float('inf') 
    optimal_investment_sequence = [] # Length should be T in the end, last element always 0
    optimal_actions_sequence_with_state = [(0, 0, 0, 0) for i in range(T)] # Length should be T in the end, each element is a (4,) tuple
    
    for inv_sequence in generate_inv_sequences(T, K):
        g_lst, inv_lst = g_whole_period(T, inv_sequence, tech_investments_table, tech_growth_table)
        ini_params = initialize_initial_parameters(
                        T=T, 
                        Pad_available_agda=Pad_available_agenda, 
                        s0=s_0, 
                        n0=n_0, 
                        g_all_stages=g_lst,
                        inv_all_stages=inv_lst,
                        c_launch0=c_launch_0, 
                        c_manu0=c_manu_0, 
                        p0=p_0,
                        theta0=theta_0,
                        alpha=alpha, 
                        beta=beta, 
                        manu_limit_table=manu_limit_table,
                        demand_table=demand_table)
        all_params = get_params_for_all_stages(T, ini_params)
        big_dic = main_for_each_inv_ops_given(T, all_params, ini_params)
        min_cost = big_dic['optimal_cost_actions_1'][f'{s_0}'][2]
        if min_cost < global_min_cost:
            # Get new optimal_action_sequence
            global_min_cost = min_cost
            optimal_investment_sequence = big_dic['investment_options']

            # (x_1, y_1, V_1(s_1)) s_1 == s_0
            opt_act_stage_1_with_V = big_dic['optimal_cost_actions_1'][f'{s_0}'] 
            
            # (s_1, x_1, y_1, c_tech_1)
            opt_act_stage_1_with_state = (s_0, opt_act_stage_1_with_V[0], opt_act_stage_1_with_V[1], optimal_investment_sequence[0])
            optimal_actions_sequence_with_state[0] = opt_act_stage_1_with_state

            s_t = s_0 # t: 1 ~ t-1

            # (x_t, y_t, V_t(s_t))
            opt_act_stage_t_with_V = (0, 0, 0)
            # (s_t, x_t, y_t, c_tech_t)
            opt_act_stage_t_with_state = (0, 0, 0, 0)

            for i in range(2, T+1):
                s_t -= optimal_actions_sequence_with_state[i-2][1] 
                s_t += optimal_actions_sequence_with_state[i-2][2]
                opt_act_stage_t_with_V = big_dic[f'optimal_cost_actions_{i}'][f'{s_t}']
                opt_act_stage_t_with_state = (s_t, opt_act_stage_t_with_V[0], opt_act_stage_t_with_V[1], optimal_investment_sequence[i-1])
                optimal_actions_sequence_with_state[i-1] = opt_act_stage_t_with_state
            
    optimal_actions_sequence = [i[1:] for i in optimal_actions_sequence_with_state]
            
    return global_min_cost, optimal_actions_sequence_with_state, optimal_actions_sequence


def main_with_timer(T, tech_investments_table, tech_growth_table, s_0, n_0, 
         alpha, beta, c_launch_0, c_manu_0, p_0, theta_0,
        Pad_available_agenda, manu_limit_table, demand_table):
    
    #main() that shows total running time
    
    start_time = perf_counter()
    
    global_min_cost, optimal_actions_sequence_with_state, optimal_actions_sequence = main(T, tech_investments_table, tech_growth_table, s_0, n_0, 
         alpha, beta, c_launch_0, c_manu_0, p_0, theta_0,
        Pad_available_agenda, manu_limit_table, demand_table)

    end_time = perf_counter()
    total_time = end_time - start_time
    print(f"\nTotal runtime of the main function: {total_time:.2f} seconds.\n")

    return global_min_cost, optimal_actions_sequence_with_state, optimal_actions_sequence