from pyomo.environ import ConcreteModel, Var, Objective, Constraint, SolverFactory, RangeSet, NonNegativeReals, Binary, Param, minimize, value, sum_product, Set
import pyomo as pyo
import numpy as np

def min_cost_power_flow_optimization_pyomo_main(n_0, m_0, k_0, c_0, c_1, omg, populs, dev_arr, dep_arr, lambda_mat, length_mat, 
                                        cmaint_mat, cflow_mat,
                                        p_arr, d_arr, s_arr, 
                                        plant_lev, plant_ccr_table, plant_pc_table,
                                        rand_seed):

    N = n_0 + m_0
    M = 100000000
    
    # Model
    model = ConcreteModel()

    # Announce Domains
    model.I = Set(initialize = [i for i in range(N)])
    model.J = Set(initialize = [j for j in range(N)])
    model.M = Set(initialize = [m for m in range(m_0)])

    # Decision variables
    model.x_ins = Var(model.I, model.J, domain=NonNegativeReals, initialize=0.0)
    model.x_out = Var(model.I, model.J, domain=NonNegativeReals, initialize=0.0)
    model.y = Var(model.I, model.J, domain=Binary, initialize=0.0)
    model.p = Var(model.M, domain=NonNegativeReals, initialize=0.0)

    # Objective function
    model.objective = Objective(expr=sum([ep * (1 - omg * dv) * c_0 for ep, dv in zip(p_arr.tolist(), dev_arr)]) +
                            sum(model.p[i-n_0] * (1 - plant_ccr_table[plant_lev[i-n_0]]) * c_1 for i in range(n_0, N)) +
                            sum(model.y[i, j] * length_mat[i, j] * cmaint_mat[i, j] for i in range(N) for j in range(i+1, N)) +
                            sum(0.5 * length_mat[i, j] * cflow_mat[i, j] * (model.x_out[i, j] + 
                                                                            model.x_ins[j, i] + 
                                                                            model.x_out[j, i] + 
                                                                            model.x_ins[i, j]) for i in range(N) for j in range(i+1, N)), sense=minimize)

    # Constraints
    def power_balance_rule(model, j):
        if j < n_0:
            return sum(model.x_ins[i, j] for i in model.I) + p_arr[j] >= s_arr[j] + d_arr[j] + sum(model.x_out[j, i] for i in model.I)
        elif j >= n_0 and j < N:
            return sum(model.x_ins[i, j] for i in model.I) + model.p[j-n_0] >= s_arr[j] + sum(model.x_out[j, i] for i in model.I)

    model.c_power_balance = Constraint(model.J, rule=power_balance_rule)

    
    def power_ceil_rule(model, j):
        return model.p[j] <= plant_pc_table[plant_lev[j]]

    model.c_power_ceil = Constraint(model.M, rule=power_ceil_rule)

    
    def c1_rule(model, i, j):
        if i != j:
            return model.x_ins[i, j] == model.x_out[i, j] * (1 - lambda_mat[i, j])
        else:
            return model.x_ins[i, j] == 0

    def c2_rule(model, i, j):
        if i != j:
            return model.x_ins[i, j] <= M * model.y[i, j]
        else:
            return model.x_out[i, j] == 0

    def c3_rule(model, i, j):
        if i != j:
            return model.x_out[i, j] <= M * model.y[i, j]
        else:
            return model.x_out[i, j] == 0

    def c4_rule(model, i, j):
            return model.y[i, j] == model.y[j, i]

    model.c1 = Constraint(model.I, model.J, rule=c1_rule)
    model.c2 = Constraint(model.I, model.J, rule=c2_rule)
    model.c3 = Constraint(model.I, model.J, rule=c3_rule)
    model.c4 = Constraint(model.I, model.J, rule=c4_rule)


    # Solving 
    solver = SolverFactory('gurobi')
    solver.solve(model)

    # Extract the solution
    x_ins_sol = np.array([value(model.x_ins[i,j]) for i in model.I for j in model.J]).reshape((len(model.I), len(model.J)))
    x_out_sol = np.array([value(model.x_out[i,j]) for i in model.I for j in model.J]).reshape((len(model.I), len(model.J)))
    y_sol = np.array([value(model.y[i,j]) for i in model.I for j in model.J]).reshape((len(model.I), len(model.J)))
    p_sol = np.array([value(model.p[i]) for i in model.M])
    minimum_total_cost_per_unit_time = value(model.objective)

    return x_ins_sol, x_out_sol, y_sol, p_sol, minimum_total_cost_per_unit_time