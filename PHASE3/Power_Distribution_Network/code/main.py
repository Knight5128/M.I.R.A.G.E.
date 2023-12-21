

if __name__ == '__main__':

    from RsomeMain import min_cost_power_flow_optimization_rsome_main
    from Visualization import visualize_energy_network

    # Get optimal power transportation plan
    (x_ins_sol, x_out_sol, y_sol, p_sol, minimum_total_cost_per_unit_time, plot_data) = min_cost_power_flow_optimization_rsome_main(5, 6, 5, realcase=0, test=0, doublecheck=0, epsilon=1)

    # Data needed for plotting
    spots = plot_data[1]
    pops = plot_data[0]
    spot_power_p_list = plot_data[2].tolist() + p_sol.tolist()

    # A primary approach to calculate power flow in each tunnel, can be improved. 
    power_flow_matrix = (x_ins_sol + x_out_sol + x_ins_sol.T + x_out_sol.T) / 2

    # Visualize the power network
    visualize_energy_network(plot_data[3], spots, pops, spot_power_p_list, power_flow_matrix, 1)