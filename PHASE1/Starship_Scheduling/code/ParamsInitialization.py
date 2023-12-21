import random


def generate_investment_growth(K, min_investment, min_growth):
    """
    Generate two lists of length K. 
    The first list contains possible tech growth values, starting from min_growth.
    This measures how will the cmprehensive tech factor growth from stage {t} to {t+1}
    The second list contains corresponding tech investment values, starting from min_investment.
    This measures the investment threshold in order to achieve each correspnding growth rate
    Both lists are in ascending order. Incremental values 

    Here we use linear growth to initialize the growth table & investment table 

    Returns a tuple containing two lists, the first for growth and the second for investment.
    """

    growth_list = [min_growth]
    investment_list = [min_investment]

    # Generate the remaining values in the lists with accelerating increments
    for i in range(1, K):
        # Accelerating increment: Increase the increment itself in each step
        incremental_growth = min_growth * ((0.5* i * (1.6 + random.uniform(-0.01, 0.01)))) * (1 + random.uniform(-0.01, 0.1))
        incremental_investment = min_investment * ((0.4 * i * (1.4 + random.uniform(-0.01, 0.01)))) * (1 + random.uniform(-0.01, 0.01))
        next_growth = round(growth_list[i-1] + incremental_growth, 5) # Exponential growth rate
        next_investment = round(investment_list[i-1] + incremental_investment, 0) # Exponential growth rate

        growth_list.append(next_growth)
        investment_list.append(next_investment)

    return growth_list, investment_list


def g_whole_period(T, investment_options_chosen, tech_investments_table, tech_growth_table):
    '''
    Calculate the g_t and c_tech_t for all T launch windows in advance based on 
    the level of technological investment selected in each period, for ease of subsequent calculations.

    Return two lists of length T, where the first list is an increasing list, 
    with each element representing the comprehensive technology index level g_t of the current period; 
    the second list contains elements representing the technological investment cost c_tech_t of the current period.
    '''
    g0 = 1
    g_whole_period_list = [g0]
    whole_period_tech_investment_list = []
    for i in range(T-1):
        g0 += tech_growth_table[investment_options_chosen[i]-1]
        whole_period_tech_investment_list.append(tech_investments_table[investment_options_chosen[i]-1])
        g_whole_period_list.append(g0)
    whole_period_tech_investment_list.append(0)
    
    return g_whole_period_list, whole_period_tech_investment_list


def initialize_initial_parameters(T, Pad_available_agda, s0, n0, g_all_stages, inv_all_stages, c_launch0, c_manu0, p0, theta0, 
                                 alpha, beta, manu_limit_table, demand_table):
    """
    Internal logic transition params:
    g_all_stages:       A list of comprehensive technology indices for all window periods,
    inv_all_stages:     A list of technology investment costs for all window periods
    
    Params that can be derived directly from problem setting:
    T:                  required total n of window periods
    Pad_available_agda: launch pad available in each window period
    s0:                 n of Starships available at the beginning of the project
    n0:                 maximum n of launches a launch pad can accommmodate
    c_launch0:          initial cost of launch a rocket
    c_manu0:            initial cost of build a new rocket
    p0:                 initial payload of a rocket (≈200)
    theta0:             initial resource retention rate (<1)
    manu_limit_table:   maximum n of new Starships that can be built in each window period
    demand_table:       minimum resources demands in each window period
    
    Estimate params:
    alpha:              The coefficient of positive correlation between c_launch_cut_rate_t & g_t
    beta:               The coefficient of positive correlation between c_manu_cut_rate_t & g_t

    Return a dict 'init_params' containing all initial parameters
    """
    if len(g_all_stages) == len(inv_all_stages):
        
        params = {
        "T": T,
        "Pad_available_agenda": Pad_available_agda,
        "s0": s0,
        "n0": n0,
        "g_all_stages": g_all_stages,
        "inv_all_stages": inv_all_stages,
        "c_launch0": c_launch0,
        "c_manu0": c_manu0,
        "p0": p0,
        "theta0": theta0,
        "alpha": alpha,
        "beta": beta,
        "n_thres": min(len(g_all_stages), len(inv_all_stages)),
        "manu_limit_table": manu_limit_table,
        "demand_table": demand_table,
        "max_state": n0 + sum(manu_limit_table)
        }
        
    else:
        l_min = min(len(g_all_stages), len(inv_all_stages))
        g_all_stages = g_all_stages[:l_min]
        inv_all_stages = inv_all_stages[:l_min]
        
        params = {
        "T": T,
        "Pad_available_agenda": Pad_available_agda,
        "s0": s0,
        "n0": n0,
        "g_all_stages": g_all_stages,
        "inv_all_stages": inv_all_stages,
        "c_launch0": c_launch0,
        "c_manu0": c_manu0,
        "p0": p0,
        "theta0": theta0,
        "alpha": alpha,
        "beta": beta,
        "n_thres": min(len(g_all_stages), len(inv_all_stages)),
        "manu_limit_table": manu_limit_table,
        "demand_table": demand_table,
        "max_state": n0 + sum(manu_limit_table)
        }

    return params


def get_params_for_stage_t(t, initial_params):
    #Obtain the parameters for window period t in a single iteration based on initial parameters in a forward manner
    
    pad_agenda = initial_params['Pad_available_agenda']
    params_t = {
        "P": pad_agenda[t-1],
        "N": pad_agenda[t-1] * initial_params['n0'],
        "g": initial_params['g_all_stages'][t-1],
        "m": initial_params['manu_limit_table'][t-1],
        "d": initial_params['demand_table'][t-1],
        "theta": initial_params['theta0'] * initial_params['g_all_stages'][t-1],
        "p": initial_params['p0'] * initial_params['g_all_stages'][t-1],
        "c_manu": initial_params['c_manu0'] * (1 - initial_params['alpha'] * (initial_params['g_all_stages'][t-1] - 1)),
        "c_launch": initial_params['c_launch0'] * (1 - initial_params['beta'] * (initial_params['g_all_stages'][t-1] - 1)),
        "c_tech": initial_params['inv_all_stages'][t-1]
    } 

    return params_t


def get_params_for_all_stages(T, initial_params):
    #Obtain the parameters for each window period in a single iteration based on initial parameters in a forward manner
    
    params_all_stages = []
    for i in range(1, T+1):
        params = get_params_for_stage_t(i, initial_params)
        params_all_stages.append(params)

    return params_all_stages