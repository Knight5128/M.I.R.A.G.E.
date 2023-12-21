<head>
    <script src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" type="text/javascript"></script>
    <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
            tex2jax: {
            skipTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
            inlineMath: [['$','$']]
            }
        });
    </script>
</head>

- ### **Variables & Parameters**
	- $T$: Required total number of launch windows
	- $P_0$: Initial number of launch pads
	- $s_0$: Initial number of starships
	- $n_0$: Maximum number of launches a single launch pad can handle within a single window
	- $g_0$: Initial comprehensive technology index
	- $c^{launch}_0$: Initial cost of launching a single starship
	- $c^{manu}_0$: Initial cost of manufacturing a single starship
	- $\alpha$: Negative correlation coefficient between the current starship launch cost and the current comprehensive technology index
	- $\beta$: Negative correlation coefficient between the current starship manufacturing cost and the current comprehensive technology index
	- $n_{thres}$: Number of potential threshold values (discontinuity points) for scientific and technological investment
	- For the $t^{th}$ launch window ($t=1,2,3,...$):
		- $g_t$: Comprehensive technology index at the beginning of the period
		- $P_t$: Number of launch pads in the current period
		- $s_t$: Number of starships at the beginning of the period
		- $N^{max}_t$: Maximum number of starship launches in the current period
		- $m_t$: Maximum number of starship manufacturing in the current period
		- $C^{tech}_t$: Scientific research and development investment in the current period
		- $x_t$: Number of starship launches in the current period
		- $y_t$: Number of starships manufactured in the current period
		- $d_t$: Total demand for CityUnit in the current period (for Mars construction needs between this and the next launch window)
		- $C^{launch}_t$: Cost of launching a single starship in the current period
		- $C^{manu}_t$: Cost of manufacturing a single starship in the current period
		- $\theta_t$: Retention rate of resources during transportation in the current period
		- $p_t$: Maximum payload of a single starship in the current period

- ### **Recursion**:
$$ \begin{align*} 
&V_t(s_t) = \min_{(x_t, y_t, C_t^{tech}) \in \mathscr U_t} \left\{ C_t^{tech} + C_t^{launch} \cdot x_t + C_t^{manu} \cdot y_t + V_{t+1} (s_{t+1}) \right\} \\ 
& \mathscr U_t = [\left\lceil \frac{d_t}{p_t \cdot g_t \cdot \theta_t} \right \rceil, \min \{ s_t+y_t , P_t \cdot n_0 \}] \bigcap \mathbb{Z} \\
& \quad \quad \ \times [0, m_t] \bigcap \mathbb{Z} \\
& \quad \quad \ \times [0, +\infty)
\end{align*} $$

- ### **Stage & State Transition**:
$$ \begin{align*}
&s_{t+1} = s_t - x_t + y_t \\
&g_{t+1} = g_t + G(C^{tech}_t)\\
&p_t = p_0 \cdot g_t\\
&\theta_t = \theta_0 \cdot g_t\\
&C^{launch}_t = C^{launch}_0 \cdot (1 - \alpha \cdot {(g_t-1)})\\
&C^{manu}_t = C^{manu}_0 \cdot (1 - \beta \cdot {(g_t-1)})
\end{align*} $$

- ### **Boundary Condition**: 
$$
V_t(s_t) = 
\begin{cases} 
&C^{launch}_t \cdot \lceil \frac{d_t}{p_t \cdot g_t \cdot \theta_t} \rceil + C^{manu}_t \cdot ( \lceil \frac{d_t}{p_t \cdot g_t \cdot \theta_t} \rceil - s_t ), &\text{if } s_t < \lceil \frac{d_t}{p_t \cdot g_t \cdot \theta_t} \rceil\\ 
&C^{launch}_t \cdot \lceil \frac{d_t}{p_t \cdot g_t \cdot \theta_t} \rceil, &\text{if } s_t \geq \lceil \frac{d_t}{p_t \cdot g_t \cdot \theta_t} \rceil\\
\end{cases} $$