import math
import itertools

def generate_inv_sequences(T, n_investment_choices):
    
    # Generate all possible investment sequences
    
    return [list(combination) + [0] for combination in itertools.product(range(1, n_investment_choices + 1), repeat=T-1)]


def get_feasible_actions_for_stage_t(t, state_t, params_all_stages):
    """
    Determine the feasible decision space for stage t.

    Return a list containing two-dimensional tuples, 
    where each tuple represents all possible (x_t, y_t) decision combinations that can be taken at stage_t
    """
    feasible_actions_t = []
    params_t = params_all_stages[t-1]
    flag = 0

    max_manu_t = params_t['m']
    max_launch_t_P = params_t['N']
    g_t = params_t['g']
    theta_t = params_t['theta']
    p_t = params_t['p']
    d_t = params_t['d']
    min_launch_t = math.ceil(d_t / (p_t * g_t * theta_t))

    # Iterate over possible actions
    for y_t in range(max_manu_t + 1):  # Manufactured starships from 0 to m_t
        max_launch_t = min(max_launch_t_P, state_t + y_t)
        if min_launch_t > max_launch_t:
            continue
        for x_t in range(min_launch_t, max_launch_t+1):  # Launch numbers from min_launches to max_launches
                feasible_actions_t.append((x_t, y_t))

    if len(feasible_actions_t) == 0:
        flag = 1

    return feasible_actions_t, flag
