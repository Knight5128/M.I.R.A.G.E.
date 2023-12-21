

- ### **Variables** 
  - $XoY$: Two-dimensional coordinate system on the Martian surface (with city $A$ as the origin)
  - $(x_{city_{i}},y_{city_{i}})$: Coordinates of the node city
  - $(x_{spot_{i}},y_{spot_{i}})$: Coordinates of potential power plant locations
  - $n$: Total number of node cities
  - $m$: Total number of potential energy supply station locations
  - $k$: Total number of power plant levels
  - $\omega_{dev-cost}$: Coefficient optimizing unit time unit energy production cost due to node city development level
  - $N_{city_{i}}$: Total population of the node city
  - $\lambda_{city_{i}}^{dev}$: Development level of the node city
  - $\lambda_{city_{i}}^{dep}$: Dependence of the node city on external energy inputs
  - $d_{city_{i}}$: Steady-state unit time energy consumption of the node city
  - $p_{city_{i}}$: Steady-state unit time energy output of the node city
  - $x^{out}_{ij}$: Amount of energy transported from node $i$ to node $j$
  - $x^{ins}_{ij}$: Actual amount of energy transported from node $i$ to node $j$
  - $l_{ij}$: Total length of the energy transportation pipeline between nodes $i$ and $j$
  - $C^{maint}_{ij}$: Maintenance cost per unit length per unit time of the energy transportation pipeline between nodes $i$ and $j$
  - $C^{trans}_{ij}$: Cost of transporting unit energy per unit length per unit time of the energy transportation pipeline between nodes $i$ and $j$
  - $C_{p}^{city}$: Initial cost of producing unit energy per unit time in node city
  - $C_{p}^{plant}$: Initial cost of producing unit energy per unit time in power plant
  - $\mu^{scale}_i$: Production cost optimization index related to the scale of the power plant 
  - $\eta_{i}$: Suitable power plant level for construction at power plant location $i$
  - $\lambda_{ij}$: Energy loss rate of the energy transportation pipeline between nodes $i$ and $j$
  - $\xi_{i} $: Required net minimum energy surplus for node $i$
  - $p_{i}$: Net energy output per unit time of the $i$th power plant
  - $p_{i}^{max}$: Maximum net energy output per unit time of the $i$th power plant
  - $y_{ij}$: Whether a pipeline needs to be directly laid between nodes $i$ and $j$
- A total of $3(n+m)^2+m$ decision variables.


- ### **Optimization Model**
$$ \begin{align*}
\min \quad \sum_{i=1}^{n_{0}} p_i \cdot (1 - \omega_{dev-cost} \cdot \lambda_{i}^{dev}) \cdot C_{p}^{city}&  + \sum_{i=n_{0}+1}^{n_{0}+m_{0}} p_i \cdot 
(1 - \mu^{scale}_i) \cdot C_{p}^{plant} + \sum_{\substack{1 \leq i \lt j \leq n_{0}+m_{0}}} y_{ij} \cdot l_{ij} \cdot C_{ij}^{maint} + \sum_{\substack{\\ 1 \leq i \lt j \leq n_{0}+m_{0}}} l_{ij} \cdot C_{ij}^{flow} \cdot \frac{x_{ij}^{out} + x_{ji}^{out} + x_{ij}^{ins} + x_{ji}^{ins}}{2} \\
\text{s.t.} \quad 
\begin{cases}
&\lambda_{ij} = \lambda_{ji} & \text{for } i,j \text{ in } {1, 2, \ldots, n_{0}+m_{0}} \\
&l_{ij} = l_{ji} & \text{for } i,j \text{ in } \{1, 2, \ldots, n_{0}+m_{0}\} \\
&x_{ij}^{ins} = x_{ij}^{out} \cdot (1-\lambda_{ij}) & \text{for } i,j \text{ in } \{1, 2, \ldots, n_{0}+m_{0}\} \\
&\sum_{i \neq j} x_{ij}^{ins} + p_j \geq \xi_j + d_j + \sum_{i \neq j} x_{ji}^{out} & \text{for } j \text{ in } \{1, \ldots, n_{0}\} \\
&\sum_{i \neq j} x_{ij}^{ins} + p_j \geq \xi_j + \sum_{i \neq j} x_{ji}^{out} & \text{for } j \text{ in } \{n_{0}+1, \ldots, n_{0}+m_{0}\} \\
&x_{ij}^{out} \leq M \cdot y_{ij} & \text{for } i,j \text{ in } \{1, 2, \ldots, n_{0}+m_{0}\} \\
&x_{ij}^{ins} \leq M \cdot y_{ij} & \text{for } i,j \text{ in } \{1, 2, \ldots, n_{0}+m_{0}\} \\
&y_{ij} = y_{ji} & \text{for } i,j \text{ in } \{1, 2, \ldots, n_{0}+m_{0}\} \\
&y_{ij} \in \{ 0, 1 \} & \text{for } i,j \text{ in } \{1, 2, \ldots, n_{0}+m_{0}\}\\
&0 \leq p_i \leq p_i^{max} & \text{for } i \text{ in } \{n_{0}+1, \ldots, n_{0}+m_{0}\} \\
&x_{ij}^{ins}, x_{ij}^{out} \geq 0 & \text{for } i,j \text{ in } \{1, 2, \ldots, n_{0}+m_{0}\}
\end{cases}
\end{align*} $$


