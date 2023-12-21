import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import numpy as np
import random
import re
import os


def visualize_energy_network(map_radius, spot_coordinates, city_populations, spot_power_p_list, power_flow_matrix, add_bg=0, n_bg_img=10):
    '''
    Visualize the total population of the city (blue circle)
    Visualize the total city energy output per unit time & total energy output of power plants per unit time (orange circle)
    Visualize the total energy flow between any two points per unit time (yellow lines)
    All the above indicators are standardized and normalized to reflect relative sizes

    This function is a General-Purpose | Result Visualization function.
    '''
    
    # Set up the plot
    plt.figure(figsize=(8, 8))
    ax = plt.gca()

    # Extract city and supply spot coordinates
    n = len(city_populations)  # Number of cities
    city_coords = spot_coordinates[:n]
    supply_coords = spot_coordinates[n:]

    # Normalize data for plotting
    max_population = max(city_populations)
    max_power = max(spot_power_p_list)
    max_flow = power_flow_matrix.max()

    # Plot city spots with population-based circle size
    for i, (x, y) in enumerate(city_coords):
        population = city_populations[i]
        radius = (population / max_population) * 810 * map_radius / 7500 # Scale the radius
        circle1 = plt.Circle((x, y), radius, color='mediumblue', alpha=0.51)
        ax.add_artist(circle1)

    # Plot all spots with power production-based circle size
    for i, (x, y) in enumerate(spot_coordinates):
        if i == 0:
            plt.scatter(x, y, s=96, marker='*', color='purple')
        elif i < n:
            plt.scatter(x, y, s=50, marker='*', color='purple')
        else:    
            plt.scatter(x, y, s=30, marker='x', color='black')
        power = spot_power_p_list[i]
        radius = (power / max_power) * 650 * map_radius / 7500  # Scale the radius
        circle = plt.Circle((x, y), radius, color='darkorange', alpha=0.50)
        ax.add_artist(circle)

    # Draw lines between points based on power flow
    for i in range(len(spot_coordinates)):
        for j in range(i+1, len(spot_coordinates)):
            flow = power_flow_matrix[i, j]
            if flow > 0:
                lw = (flow / max_flow) * 3.25  # Scale line width
                plt.plot([spot_coordinates[i][0], spot_coordinates[j][0]],
                         [spot_coordinates[i][1], spot_coordinates[j][1]],
                         color='gold', linewidth=lw, alpha=0.7)


    # Set image display boundaries
    max_coord = map_radius * 1.1
    plt.xlim(-max_coord, max_coord)
    plt.ylim(-max_coord, max_coord)

    # Place the origin at the centre of the image
    plt.axhline(0, color='black', linewidth=0)  
    plt.axvline(0, color='black', linewidth=0)  

    # Hide external borders
    for spine in plt.gca().spines.values():
        spine.set_visible(False)

    # Set lables and title
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('Energy Network Visualization')
    plt.grid(True, linewidth=1.35, alpha=0.3)

    # Add background
    if add_bg:
        folder_path = "D:\MyProjects\GotoMars\PHASE3\Power_Distribution_Network\pictures"
        image_files = os.listdir(folder_path)

        if not image_files:
            print("No images found in the folder.")
            img_path = input("Please enter the path for the background image: ")
        else:
            random_image_file = random.choice(image_files)
            img_path = os.path.join(folder_path, random_image_file)

        try:
            bg_image = mpimg.imread(img_path)
            plt.imshow(bg_image, extent=[-max_coord, max_coord, -max_coord, max_coord])
            
        except FileNotFoundError:
            print("Background image not found.")
            img_path = input("Please enter the path for the background image: ")
            bg_image = mpimg.imread(img_path)
            plt.imshow(bg_image, extent=[-max_coord, max_coord, -max_coord, max_coord])
            
    plt.show()