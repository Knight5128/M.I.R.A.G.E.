

if __name__ == '__main__':

    from MainModelFunction import main_with_timer
    from ParamsInitialization import generate_investment_growth

    # Simulated Problem

    # Initialize the corresponding table between investment thresholds and absolute growth rates of g
    K = 5 #n_thres
    min_investment = 400000 #minimum investment needed for tech to advance  
    min_growth = 0.005  #minimum absolute growth rate of g if scientific progress is made 
    g_growth_table, g_investment_table = generate_investment_growth(10, min_investment, min_growth)
    T = 5
    Pad_available_agenda = [1,1,2,2,2]
    manu_limit_table = [4,6,8,7,7]
    demand_table = [6500, 8000, 9000, 14000, 16000]
    alpha = 0.24 
    beta = 0.185
    s_0 = 3
    n_0 = 6
    c_launch_0 = 50000
    c_manu_0 = 75000
    p_0 = 2500
    theta_0 = 0.8

    # Investment-Technological Progress Comparison Table for All the Following Test Problem Scenarios
    print('Quantity of technological investment:\n', g_investment_table)
    print()
    print('Corresponding incremental(between each launch window) technical level generated by investment:\n', g_growth_table)
    
    #Simulation Problem Solving Block
    minimum_budget_needed, optimal_actions_sequence_with_state, optimal_actions_sequence = main_with_timer(T,
                                                                                                       g_investment_table[:K],g_growth_table[:K],
                                                                                                       s_0,n_0,alpha,beta,
                                                                                                       c_launch_0,c_manu_0,p_0,theta_0,
                                                                                                       Pad_available_agenda,
                                                                                                       manu_limit_table,
                                                                                                       demand_table)  
    print("minimum_budget_needed:", minimum_budget_needed)
    print("optimal_actions_sequence_with_state:", optimal_actions_sequence_with_state)
    print("optimal_actions_sequence:", optimal_actions_sequence)