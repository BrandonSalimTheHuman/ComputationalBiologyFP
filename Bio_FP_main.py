import tkinter as tk
from tkinter import ttk, messagebox
import math
import random
import pygame
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import matplotlib

matplotlib.use("Agg")


# class for individuals
class Individual:
    # initialize
    def __init__(self, id, behavior, family_id, generation, initial_fitness, fitness, parent=None):
        self.id = id
        # behavior: altruistic or selfish
        self.behavior = behavior
        # family_id: an id used to group families together
        self.family_id = family_id
        # mutation chance
        self.generation = generation
        # initial fitness for reproducing, then the actual fitness of the individual
        self.initial_fitness = initial_fitness
        self.fitness = fitness
        # help
        self.parent = parent
        self.position = None
        self.target_position = None

    # reproduce
    def reproduce(self, generation, total_population):
        return Individual(total_population + 1, self.behavior, self.family_id, generation, self.initial_fitness,
                          self.initial_fitness, parent=self.id)


# start simulation
def start_simulation():
    # getting everything from the UI
    try:
        population_size = int(population_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Initial population size must be an integer.")
        return
    try:
        max_population_size = int(max_population_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Max population size must be an integer.")
        return
    # make sure max isn't < initial
    if max_population_size < population_size:
        messagebox.showerror("Input Error", "Max population size can't be lower than initial population size.")
        return
    initial_distribution = altruist_slider.get()
    try:
        mutation_chance = float(mutation_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Mutation chance must be a number between 0 - 100 (inclusive).")
        return
    if mutation_chance < 0 or mutation_chance > 100:
        messagebox.showerror("Input Error", "Mutation chance must be a number between 0 - 100 (inclusive).")
        return
    try:
        max_generations = int(generations_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Max generations must be an integer.")
        return
    family_distribution = family_distribution_var.get()
    try:
        initial_fitness = float(fitness_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Initial fitness must be a number.")
        return
    try:
        family_size = int(family_size_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Family size must be an integer.")
        return
    kin_likelihood = kin_slider.get()
    rule = interaction_rule_var.get()
    try:
        base_reward = float(base_reward_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Base reward must be a number.")
        return
    try:
        selfish_cost = float(selfish_cost_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Selfish cost must be a number.")
        return
    try:
        altruism_benefit = float(altruism_benefit_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Altruism benefit must be a number.")
        return
    try:
        altruism_cost = float(altruism_cost_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Altruism cost must be a number.")
        return
    skip_animations = animation_var.get()
    # show simulation parmeters
    print(f"Population Size %: {population_size}")
    print(f"Max Population Size %: {max_population_size}")
    print(f"Initial Altruist %: {initial_distribution}")
    print(f"Mutation Chance: {mutation_chance}%")
    print(f"Max Generations: {max_generations}")
    print(f"Family distribution: {family_distribution}")
    print(f"Initial fitness: {initial_fitness}")
    print(f"Family size: {family_size}")
    print(f"Kin Encounter Likelihood: {kin_likelihood}%")
    print(f"Rule used: {rule}")
    if rule == "S":
        try:
            reward_scaling = float(scaling_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Reward scaling must be a number.")
            return
        print(f"Reward scaling: {reward_scaling}")
        rule = False
    else:
        reward_scaling = 0
        rule = True
    print(f"Base reward: {base_reward}")
    print(f"Selfish cost: {selfish_cost}")
    print(f"Altruism benefit: {altruism_benefit}")
    print(f"Altruism cost: {altruism_cost}")

    # initialize the first population and show it on the screen
    population = initialize_population(population_size, initial_distribution, initial_fitness, family_size,
                                       family_distribution)
    assign_positions(population, 800, 600)

    running = True
    generation = 1
    total_population = len(population)
    # initialize pygame
    pygame.init()
    screen_width = 1150
    screen_height = 850
    simulation_height = 600  # Height for the simulation area

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Altruism Simulation")
    while running:
        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Process Tkinter events
        root.update()

        if generation < max_generations:
            draw_population(screen, population)
            # Count altruists and selfish individuals
            render_graph_to_pygame(screen, simulation_height)
            pygame.display.flip()
            time.sleep(0)

            # the first generation doesn't need this
            if generation != 1:
                interaction_phase(population, kin_likelihood, rule, base_reward, selfish_cost, altruism_cost,
                                  altruism_benefit, reward_scaling, screen, skip_animations)
                population, total_population = reproduction_phase(mutation_chance, initial_fitness, population,
                                                                  generation, total_population, max_population_size,
                                                                  screen, skip_animations)
            if len(population) == 0:
                messagebox.showerror("Everything died", "Population is entirely extinct")
                generation = max_generations
            else:
                # Count altruists and selfish individuals
                altruists = sum(1 for individual in population if individual.behavior == "altruist")
                selfish = sum(1 for individual in population if individual.behavior == "selfish")

                print("\n==============SUMMARY OF NEW GENERATION=================")
                print("Generations:", generation)
                print("Altruists:", altruists)
                print("Selfish:", selfish)
                print("\n")

                # Update graph
                update_graph(generation, altruists, selfish, len(population))

                # Render graph to Pygame
                render_graph_to_pygame(screen, simulation_height)

                # Update Pygame display
                pygame.display.flip()

                generation += 1

                if not skip_animations:
                    time.sleep(1)

    # Cleanup Pygame
    pygame.quit()


# update graph. very insightful comment.
def update_graph(generation, altruists, selfish, total_population):
    global fig, canvas
    altruist_percentage = (altruists / total_population) * 100
    selfish_percentage = (selfish / total_population) * 100

    generations_data.append(generation)
    altruist_percentages.append(altruist_percentage)
    selfish_percentages.append(selfish_percentage)

    # Create stacked area chart
    plt.clf()  # Clear the plot
    plt.stackplot(
        generations_data,
        altruist_percentages,
        selfish_percentages,
        labels=["Altruists", "Selfish"],
        colors=["#76c7c0", "#ffab76"],  # Choose colors for areas
    )
    plt.legend(loc="upper left")
    plt.title("Population Dynamics Over Generations")
    plt.xlabel("Generations")
    plt.ylabel("Percentage (%)")
    plt.ylim(0, 100)
    plt.tight_layout()  # Automatically adjust padding to prevent clipping

    # Save as a figure for rendering in Pygame
    canvas = FigureCanvas(plt.gcf())
    canvas.draw()


# showing the graph on the pygame window
def render_graph_to_pygame(screen, y_offset):
    canvas.draw()  # Ensure the canvas is up-to-date
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_argb()
    size = canvas.get_width_height()
    argb_array = np.frombuffer(raw_data, dtype=np.uint8).reshape(size[1], size[0], 4)  # Reshape ARGB buffer
    rgb_array = argb_array[..., 1:]  # Drop the alpha channel
    rgb_data = rgb_array.tobytes()
    graph_surface = pygame.image.fromstring(rgb_data, size, "RGB")
    screen.blit(graph_surface, (175, y_offset))


# function to initialize population
def initialize_population(population_size, altruist_ratio, initial_fitness, family_size, family_behavior):
    # array to hold entire population
    population = []
    behaviors = []
    # calculate number of altruists
    num_altruists = int(population_size * altruist_ratio / 100)
    # calculate number of selfish
    num_selfish = population_size - num_altruists

    # generate appropriate number of altruistic and selfish behavior
    for i in range(num_altruists):
        behaviors.append('altruist')
    for i in range(num_selfish):
        behaviors.append('selfish')

    # if mixed, shuffle the array
    if family_behavior == 'mixed':
        random.shuffle(behaviors)
    elif family_behavior != 'homogenous':
        print("Invalid")
        return

    # starting id for the first family
    family_id = 1
    # number of people in the current family
    current_family_size = 0

    # loop through population
    for i in range(population_size):
        # Alternate between creating altruists and selfish individuals based on the ratio
        behavior = behaviors[i]

        # assign family ID and reset as needed based on family size
        if family_size:
            if current_family_size >= family_size:
                family_id += 1
                current_family_size = 0
            current_family_size += 1
        else:
            family_id = None  # No family structure if family size isn't specified

        # create individual and add to population list
        individual = Individual(i + 1, behavior, family_id, 1, initial_fitness, initial_fitness)
        population.append(individual)

    return population


# calculate how to arrange the pairs
def calculate_grid_layout(population_size, screen_width, screen_height, margin=20):
    # default guess
    base_spacing = 50
    spacing = base_spacing

    while True:
        # calculate max columns and rows
        max_columns = (screen_width - 2 * margin) // spacing
        max_columns -= max_columns % 2  # a pair needs to be adjacent, so columns must be even
        max_rows = (screen_height - 2 * margin) // spacing

        print(max_columns)
        print(max_rows)
        max_total = max_columns * max_rows

        # if the current configuration fits the entire population, return the layout
        if population_size <= max_total:
            break

        # if it doesn't fit, reduce spacing and retry
        spacing -= 1.5

    return max_columns, max_rows, margin, spacing


# assigning target positions to each individual
def assign_grid_positions(pairs, max_columns, margin, spacing):
    row, col = 0, 0

    for individual1, individual2 in pairs:
        # Assign positions for the pair
        x1 = margin + col * spacing
        y1 = margin + row * spacing
        x2 = margin + (col + 1) * spacing
        y2 = margin + row * spacing

        individual1.target_position = (x1, y1)
        individual2.target_position = (x2, y2)

        # Update column and row
        col += 2
        if col >= max_columns:
            col = 0
            row += 1


# step to move individuals to their target position
def move_to_grid(population, screen, speed=5):
    moving = True  # flag to check that something is moving

    while moving:
        moving = False  # assume no one is moving
        for individual in population:
            # get current and target positions
            current_x, current_y = individual.position
            target_x, target_y = individual.target_position

            # calculate movement step
            dx = target_x - current_x
            dy = target_y - current_y

            # update position incrementally if not already at target
            if dx != 0 or dy != 0:
                moving = True  # something is still moving
                step_x = dx / speed
                step_y = dy / speed
                individual.position = (current_x + step_x, current_y + step_y)
                # snapping, since the previous steps using division might cause individuals to just slightly be off
                if abs(dx - step_x) < 1 or abs(dy - step_y) < 1:
                    individual.position = individual.target_position

        # redraw the screen with the updated positions
        draw_population(screen, population)
        render_graph_to_pygame(screen, 600)
        pygame.display.flip()

        pygame.time.delay(50)


# connect pairs with lines
def draw_population_grid(screen, pairs):
    screen.fill((0, 0, 0))  # Clear screen
    for individual1, individual2 in pairs:
        # Draw individuals
        color1 = (0, 0, 255) if individual1.behavior == "altruist" else (255, 0, 0)
        color2 = (0, 0, 255) if individual2.behavior == "altruist" else (255, 0, 0)
        pygame.draw.circle(screen, color1, individual1.target_position, 5)
        pygame.draw.circle(screen, color2, individual2.target_position, 5)

        # Draw interaction line
        pygame.draw.line(screen, (130, 130, 130), individual1.target_position, individual2.target_position, 2)


# draw interaction outcome by using green / red outline with different intensity
def draw_interaction_outcome(screen, individual, fitness_change):
    # Normalize fitness_change to a range (0–1)
    max_change = 2  # Example max absolute fitness change for normalization
    normalized_change = min(max(abs(fitness_change) / max_change, 0), 1)

    # Determine gradient color based on fitness change
    if fitness_change > 0:
        color = (0, 255, 0)  # Green for positive
    elif fitness_change < 0:
        color = (255, 0, 0)  # Red for negative
    else:
        color = (255, 255, 0)  # Yellow for neutral

    # Create a surface for the gradient
    radius = 6
    gradient_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

    # Draw the gradient with varying transparency
    for r in range(radius, 0, -1):
        alpha = int(normalized_change * (255 * (r / radius)))
        pygame.draw.circle(gradient_surface, (*color, alpha), (radius, radius), r)

    # Blit the gradient onto the main screen at the individual's position
    x, y = individual.position
    screen.blit(gradient_surface, (x - radius, y - radius))

    pygame.display.flip()


# formula to calculate relatedness between two individuals
def calculate_relatedness(individual1, individual2):
    # completely different family
    if individual1.family_id != individual2.family_id:
        return 0

    # else, they're from the same family.
    # since individuals live for 1 generation only, then they must be siblings
    if individual1.generation == individual2.generation:
        return 1


# pairing individuals together for interaction
def interaction_phase_matchmaking(population, kin_likelihood):
    # grouping by family
    family_groups = {}
    # for each individual
    for individual in population:
        # if family isn't in family_groups yet
        if individual.family_id not in family_groups:
            # create empty set
            family_groups[individual.family_id] = set()
        # add to correct set
        family_groups[individual.family_id].add(individual)

    # all pairs
    interaction_pairs = []
    # paired individuals
    used_individuals = set()

    # generating a list of nonkin candidates for each individual
    # will take more memory, but trying this for faster lookup
    non_kin_map = {}
    for individual in population:
        non_kin_map[individual.id] = {ind for ind in population if ind.family_id != individual.family_id}

    # loop through all individuals
    for individual in population:
        # if already paired, skip it
        if individual in used_individuals:
            continue

        # random.random() returns between 0 and 1, and kin_likelihood / 100 is also between 0 and 1
        # this decides whether the pair is a kin or not
        if random.random() < kin_likelihood / 100:
            # pairing with a kin
            # all family members
            family = family_groups[individual.family_id]
            # getting candidates from set difference
            candidates = family - used_individuals
            # remove the individual itself
            candidates.discard(individual)

            # if at least one candidate exists, randomly choose one
            if candidates:
                partner = random.choice(list(candidates))

            # if there's no one else, resort to non-kin
            else:
                partner = choose_non_kin(individual, used_individuals, non_kin_map)
        else:
            partner = choose_non_kin(individual, used_individuals, non_kin_map)
            # if no non-kin, resort to kin
            if partner is None:
                # all family members
                family = family_groups[individual.family_id]
                # getting candidates from set difference
                candidates = family - used_individuals
                # remove the individual itself
                candidates.discard(individual)
                # if at least one candidate exists, randomly choose one
                if candidates:
                    partner = random.choice(list(candidates))

        # if partner was found
        if partner:
            # append the pair to the list
            interaction_pairs.append((individual, partner))
            # add both individuals to used_individuals
            used_individuals.add(individual)
            used_individuals.add(partner)
    print("Total pairs:", len(interaction_pairs))
    return interaction_pairs


# function to choose non kin
def choose_non_kin(individual, used_individuals, non_kin_map):
    # get all candidates from the precomputed map
    candidates = non_kin_map.get(individual.id, set()) - used_individuals

    # if there is at least one candidate, randomly choose one
    if candidates:
        return random.choice(list(candidates))
    # otherwise, return none
    else:
        return None


# interacting using hamilton's rule for decision making
def interaction_phase_hamilton(interaction_pairs, base_reward, selfish_penalty, altruism_loss, altruism_give_benefit,
                               screen):
    for individual1, individual2 in interaction_pairs:
        individual1_modifier = 0
        individual2_modifier = 0
        # both are selfish
        if individual1.behavior == 'selfish' and individual2.behavior == 'selfish':
            individual1_modifier += (base_reward - selfish_penalty)
            individual2_modifier += (base_reward - selfish_penalty)
        # both are altruistic
        elif individual1.behavior == 'altruist' and individual2.behavior == "altruist":
            # hamilton rule for decision making
            # print("Both altruistic", calculate_relatedness(individual1, individual2))
            if (altruism_give_benefit * calculate_relatedness(individual1, individual2)) >= altruism_loss:
                individual1_modifier += (base_reward + altruism_give_benefit - altruism_loss)
                individual2_modifier += (base_reward + altruism_give_benefit - altruism_loss)
            else:
                individual1_modifier += base_reward
                individual2_modifier += base_reward
        # one selfish one altruist
        else:
            print("One altruistic", calculate_relatedness(individual1, individual2))
            # hamilton rule for decision making
            if (altruism_give_benefit * calculate_relatedness(individual1, individual2)) >= altruism_loss:
                # if individual 1 is altruist, then 2 is selfish
                if individual1.behavior == 'altruist':
                    individual1_modifier += (base_reward - altruism_loss)
                    individual2_modifier += (base_reward + altruism_give_benefit)
                # else, it's the other way around
                else:
                    individual1_modifier += (base_reward + altruism_give_benefit)
                    individual2_modifier += (base_reward - altruism_loss)
            else:
                individual1_modifier += base_reward
                individual2_modifier += base_reward

        # apply changes
        individual1.fitness += individual1_modifier
        individual2.fitness += individual2_modifier

        draw_interaction_outcome(screen, individual1, individual1_modifier)
        draw_interaction_outcome(screen, individual2, individual2_modifier)


# altruists always altruistic, but relatives get more benefit
def interaction_phase_reward_scaling(interaction_pairs, base_reward, selfish_penalty, altruism_loss,
                                     altruism_give_benefit, relatedness_multiplier_bonus):
    for individual1, individual2 in interaction_pairs:
        individual1_modifier = 0
        individual2_modifier = 0
        # both are selfish
        if individual1.behavior == 'selfish' and individual2.behavior == 'selfish':
            individual1_modifier += (base_reward - selfish_penalty)
            individual2_modifier += (base_reward - selfish_penalty)
        # both are altruistic
        elif individual1.behavior == 'altruist' and individual2.behavior == "altruist":
            # multiply benefit by (1 + relatedness * multiplier) for the bonus benefit
            relatedness = calculate_relatedness(individual1, individual2)
            individual1_modifier += (base_reward + altruism_give_benefit *
                                     (1 + relatedness * relatedness_multiplier_bonus) - altruism_loss)
            individual2_modifier += (base_reward + altruism_give_benefit *
                                     (1 + relatedness * relatedness_multiplier_bonus) - altruism_loss)
        # one selfish one altruist
        else:
            # multiply benefit by (1 + relatedness (0, 0.25 0.5 or 1) * multiplier)
            relatedness = calculate_relatedness(individual1, individual2)
            # individual 1 is altruist, so 2 is selfish
            if individual1.behavior == 'altruist':
                individual1_modifier += (base_reward - altruism_loss)
                individual2_modifier += (base_reward + altruism_give_benefit *
                                         (1 + relatedness * relatedness_multiplier_bonus))
            # else, it's the other way around
            else:
                individual1_modifier += (base_reward + altruism_give_benefit *
                                         (1 + relatedness * relatedness_multiplier_bonus))
                individual2_modifier += (base_reward - altruism_loss)

        # apply changes
        individual1.fitness += individual1_modifier
        individual2.fitness += individual2_modifier
    pass


# for entire interaction phase
def interaction_phase(population, kin_likelihood, hamilton, base_reward, selfish_penalty, altruism_loss,
                      altruism_give_benefit, relatedness_multiplier_bonus, screen, skip_animations):
    interaction_pairs = interaction_phase_matchmaking(population, kin_likelihood)
    max_columns, num_rows, margin, spacing = calculate_grid_layout(len(population), 1150, 600, 20)
    assign_grid_positions(interaction_pairs, max_columns, margin, spacing)
    print("Positions assigned")
    if skip_animations:
        move_to_grid(population, screen, 1)
    else:
        move_to_grid(population, screen)
    draw_population_grid(screen, interaction_pairs)
    render_graph_to_pygame(screen, 600)
    pygame.display.flip()
    if not skip_animations:
        time.sleep(1)

    if hamilton:
        interaction_phase_hamilton(interaction_pairs, base_reward, selfish_penalty, altruism_loss,
                                   altruism_give_benefit, screen)
    else:
        interaction_phase_reward_scaling(interaction_pairs, base_reward, selfish_penalty, altruism_loss,
                                         altruism_give_benefit, relatedness_multiplier_bonus)

    if not skip_animations:
        time.sleep(1.5)

    # altruist stats
    altruists = [individual for individual in population if individual.behavior == "altruist"]
    average_fitness_altruists = sum(individual.fitness for individual in altruists) / len(
        altruists) if altruists else 0

    # selfish stats
    selfish = [individual for individual in population if individual.behavior == "selfish"]
    average_fitness_selfish = sum(individual.fitness for individual in selfish) / len(selfish) if selfish else 0

    print("\n===================AFTER INTERACTIONS========================")
    print("Average Fitness (Altruists):", str(math.floor(average_fitness_altruists * 100) / 100))
    print("Average Fitness (Selfish):", str(math.floor(average_fitness_selfish * 100) / 100))
    print("\n")


# entire reproduction phase
def reproduction_phase(mutation_chance, initial_fitness, population, generation, total_population, max_population_size,
                       screen, skip_animations):
    new_population = []
    print("Dying:", len(population))
    for individual in population:
        chance, guaranteed = math.modf(individual.fitness)
        guaranteed = int(guaranteed)
        for i in range(guaranteed):
            # print("Total population", total_population)
            new_individual = individual.reproduce(generation, total_population)
            if random.random() * 100 <= mutation_chance:
                new_individual.behavior = "altruist" if new_individual.behavior == "selfish" else "selfish"
                tmp = new_individual.parent
                new_individual.parent = str(tmp)
            total_population += 1
            new_population.append(new_individual)

        if random.random() <= chance:
            # print("Total population", total_population)
            new_individual = individual.reproduce(generation, total_population)
            if random.random() * 100 <= mutation_chance:
                new_individual.behavior = "altruist" if new_individual.behavior == "selfish" else "selfish"
                tmp = new_individual.parent
                new_individual.parent = str("this fcking mutated lesgooooooooo" + str(tmp))
            total_population += 1
            new_population.append(new_individual)

        # returning fitness to the base value when an individual is initialized
        individual.fitness = initial_fitness

    # applying population cap
    if len(new_population) > max_population_size:
        new_population = random.sample(new_population, max_population_size)

    # assign positions to new generation
    assign_positions(new_population, 1150, 600)
    if skip_animations:
        transition_population(screen, population, new_population, 255)
    else:
        transition_population(screen, population, new_population, 15)

    print("New generation:", len(new_population))
    return new_population, total_population


# fade out old generation, fade in new one
def transition_population(screen, old_population, new_population, step):
    # Fade-out effect for the old generation
    for alpha in range(255, 0, step):  # Gradually decrease opacity
        screen.fill((0, 0, 0))  # Clear screen
        draw_population_with_alpha(screen, old_population, alpha)
        render_graph_to_pygame(screen, 600)
        pygame.display.flip()
        pygame.time.delay(25)

    # Fade-in effect for the new generation
    for alpha in range(0, 255, step):  # Gradually increase opacity
        screen.fill((0, 0, 0))  # Clear screen
        draw_population_with_alpha(screen, new_population, alpha)
        render_graph_to_pygame(screen, 600)
        pygame.display.flip()
        pygame.time.delay(25)


# draw population while fading in / out
def draw_population_with_alpha(screen, population, alpha):
    # Create a temporary surface with per-pixel alpha
    temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    for individual in population:
        # Set the RGBA color
        color = (0, 0, 255, alpha) if individual.behavior == "altruist" else (255, 0, 0, alpha)

        # Draw the circle on the temporary surface
        pygame.draw.circle(temp_surface, color, individual.position, 5)

    # Blit the temporary surface onto the main screen
    screen.blit(temp_surface, (0, 0))


# Assign random positions to individuals
def assign_positions(population, width, height, margin=20):
    for individual in population:
        individual.position = (random.randint(margin, width - margin),
                               random.randint(margin, height - margin))
        individual.target_position = individual.position


def draw_population(screen, population):
    screen.fill((0, 0, 0))  # White background
    for individual in population:
        color = (0, 0, 255) if individual.behavior == "altruist" else (255, 0, 0)
        pygame.draw.circle(screen, color, individual.position, 5)


# Function to enable or disable slider based on selection
def update_slider_state_2():
    if interaction_rule_var.get() == "S":
        scaling_entry.config(state='normal')
        scaling_entry.delete(0, tk.END)
        scaling_entry.insert(0, "0.5")
    else:
        scaling_entry.delete(0, tk.END)
        scaling_entry.config(state='disabled')


# Main window setup
root = tk.Tk()
root.title("Altruism and Kin Selection Simulation: Inputting Parameters")
root.geometry("1400x800")
root.configure(background="#b9a7fa")

font_style = ("Arial", 13)
padding = 20
slider_length = 200
slider_width = 20
entry_width = 15

# Two-column layout
root.columnconfigure(0, weight=2)
root.columnconfigure(1, weight=3)
root.columnconfigure(2, weight=2)

# Column 1 widgets

# initial population size
population_label = ttk.Label(root, text="Initial Population size:", font=font_style, background="#b9a7fa")
population_label.grid(row=0, column=0, pady=padding, padx=padding, sticky="ew")
population_entry = ttk.Entry(root, width=entry_width, font=font_style, justify='center')
population_entry.insert(0, "50")  # Default to 50
population_entry.grid(row=1, column=0)

# max population size
max_population_label = ttk.Label(root, text="Max Population size:", font=font_style, background="#b9a7fa")
max_population_label.grid(row=2, column=0, pady=padding, padx=padding, sticky="ew")
max_population_entry = ttk.Entry(root, width=entry_width, font=font_style, justify='center')
max_population_entry.insert(0, "1000")  # Default to 1000
max_population_entry.grid(row=3, column=0)

# initial altruists as a percentage of population
altruist_label = ttk.Label(root, text="Initial % of Altruists:", font=font_style, background="#b9a7fa")
altruist_label.grid(row=4, column=0, pady=padding, padx=padding, sticky="ew")
altruist_slider = tk.Scale(root, from_=0, to=100, orient='horizontal', length=slider_length, width=slider_width,
                           font=font_style)
altruist_slider.set(50)  # Default to 50%
altruist_slider.grid(row=5, column=0)

# mutation chance
mutation_label = ttk.Label(root, text="Mutation Chance (%):", font=font_style, background="#b9a7fa")
mutation_label.grid(row=6, column=0, pady=padding, padx=padding, sticky="ew")
mutation_entry = ttk.Entry(root, width=entry_width, font=font_style, justify='center')
mutation_entry.insert(0, "1.0")  # Default to 1%
mutation_entry.grid(row=7, column=0)

# max number of generations
generations_label = ttk.Label(root, text="Max Number of Generations:", font=font_style, background="#b9a7fa")
generations_label.grid(row=8, column=0, pady=padding, padx=padding, sticky="ew")
generations_entry = ttk.Entry(root, width=entry_width, font=font_style, justify='center')
generations_entry.insert(0, "20")
generations_entry.grid(row=9, column=0)

# Column 2 widgets

# buttons for family (mixed/homogenous)
option_label = ttk.Label(root, text="Family behavior distribution:", font=font_style, background="#b9a7fa")
option_label.grid(row=0, column=1, pady=padding, padx=padding, sticky="ew")

family_distribution_var = tk.StringVar(value="homogenous")  # Default value
family_mixed = ttk.Radiobutton(root, text="Mixed", variable=family_distribution_var, value="mixed")
family_mixed.grid(row=1, column=1, sticky="ew", padx=padding, pady=padding / 2)
family_mixed.configure(style="Custom.TRadiobutton")

family_homogenous = ttk.Radiobutton(root, text="Homogenous", variable=family_distribution_var, value="homogenous")
family_homogenous.grid(row=2, column=1, sticky="ew", padx=padding, pady=padding / 2)
family_homogenous.configure(style="Custom.TRadiobutton")

# initial fitness
fitness_label = ttk.Label(root, text="Initial Fitness Per Individual:", font=font_style, background="#b9a7fa")
fitness_label.grid(row=3, column=1, pady=padding, padx=padding, sticky="ew")
fitness_entry = ttk.Entry(root, width=entry_width, font=font_style, justify='center')
fitness_entry.insert(0, "0")
fitness_entry.grid(row=4, column=1, padx=padding)

# initial family size
family_size_label = ttk.Label(root, text="Initial Family SIze:", font=font_style, background="#b9a7fa")
family_size_label.grid(row=5, column=1, pady=padding, padx=padding, sticky="ew")
family_size_entry = ttk.Entry(root, width=entry_width, font=font_style, justify='center')
family_size_entry.insert(0, "3")
family_size_entry.grid(row=6, column=1, padx=padding)

# Kin slider
kin_label = ttk.Label(root, text="Likelihood of Meeting Kin (%):", font=font_style, background="#b9a7fa")
kin_label.grid(row=7, column=1, pady=padding, padx=padding, sticky="ew")

kin_slider = tk.Scale(root, from_=0, to=100, orient='horizontal', length=slider_length, width=slider_width,
                      font=font_style)
kin_slider.set(50)  # Default to 50%
kin_slider.grid(row=8, column=1, padx=padding)

# buttons for rules
family_distribution_label = ttk.Label(root, text="Rules for interaction:", font=font_style, background="#b9a7fa")
family_distribution_label.grid(row=9, column=1, pady=padding, padx=padding, sticky="ew")

interaction_rule_var = tk.StringVar(value="H")  # Default value
hamilton_option = ttk.Radiobutton(root, text="Use Hamilton's rule as decision making for altruists",
                                  variable=interaction_rule_var, value="H", command=update_slider_state_2)
hamilton_option.grid(row=10, column=1, sticky="ew", padx=padding)
hamilton_option.configure(style="Custom.TRadiobutton")

scaling_option = ttk.Radiobutton(root, text="Altruists always perform altruism, more reward for kin based on "
                                            "relatedness", variable=interaction_rule_var, value="S",
                                 command=update_slider_state_2)
scaling_option.grid(row=11, column=1, sticky="ew", padx=padding)
scaling_option.configure(style="Custom.TRadiobutton")

# style for radio buttons
style = ttk.Style()
style.configure(
    "Custom.TRadiobutton",
    font=("Arial", 13),
    background="#b9a7fa",
    foreground="black",
)

# style for disabled state
style2 = ttk.Style()
style2.configure('Custom.TEntry', fieldbackground='#707070')
style2.map('Custom.TEntry',
           fieldbackground=[('disabled', '#707070')],  # dark background
           )

# reward scaling entry
scaling_label = ttk.Label(root, text="Reward Scaling (Multiplied by relatedness for bonus benefit for kin):",
                          font=font_style, background="#b9a7fa")
scaling_label.grid(row=0, column=2, pady=padding, padx=padding, sticky="ew")
scaling_entry = tk.Entry(root, width=entry_width, font=font_style, justify='center', state='disabled',
                         disabledbackground="#707070")
scaling_entry.grid(row=1, column=2)

# base reward
base_reward_label = ttk.Label(root, text="Base reward for interaction:", font=font_style, background="#b9a7fa")
base_reward_label.grid(row=2, column=2, pady=padding, padx=padding, sticky="ew")
base_reward_entry = ttk.Entry(root, width=entry_width, font=font_style, justify='center')
base_reward_entry.insert(0, "1")
base_reward_entry.grid(row=3, column=2, padx=padding)

# selfish cost
selfish_cost_label = ttk.Label(root, text="Selfish cost when 2 selfish individuals meet:", font=font_style,
                               background="#b9a7fa")
selfish_cost_label.grid(row=4, column=2, pady=padding, padx=padding, sticky="ew")
selfish_cost_entry = ttk.Entry(root, width=entry_width, font=font_style, justify='center')
selfish_cost_entry.insert(0, "0.3")
selfish_cost_entry.grid(row=5, column=2, padx=padding)

# altruism benefit
altruism_benefit_label = ttk.Label(root, text="Benefit given to an individual by an altruist:", font=font_style,
                                   background="#b9a7fa")
altruism_benefit_label.grid(row=6, column=2, pady=padding, padx=padding, sticky="ew")
altruism_benefit_entry = ttk.Entry(root, width=entry_width, font=font_style, justify='center')
altruism_benefit_entry.insert(0, "1.5")
altruism_benefit_entry.grid(row=7, column=2, padx=padding)

# altruism cost
altruism_cost_label = ttk.Label(root, text="Cost of performing altruism for altruist:", font=font_style,
                                background="#b9a7fa")
altruism_cost_label.grid(row=8, column=2, pady=padding, padx=padding, sticky="w")
altruism_cost_entry = ttk.Entry(root, width=entry_width, font=font_style, justify='center')
altruism_cost_entry.insert(0, "1")
altruism_cost_entry.grid(row=9, column=2, padx=padding)

# style for animation skip checkbox
style3 = ttk.Style()
style.configure(
    "TCheckbutton",
    background=root["background"],
    focuscolor=root["background"],
)
# animation skip
animation_var = tk.BooleanVar(value=False)
animation_checkbox = ttk.Checkbutton(
    root,
    text="Skip animations",
    variable=animation_var,
    style="TCheckbutton"
)
animation_checkbox.grid(row=10, column=2, padx=padding)

# Start simulation button
style.configure('StartButton.TButton', font=('Arial', 16, 'bold'))
start_button = ttk.Button(root, text="Start Simulation", command=start_simulation, style='StartButton.TButton')
start_button.grid(row=13, column=0, columnspan=3, pady=padding + 20)

# matplotlib initialization
fig, ax = plt.subplots(figsize=(8, 2.5))  # Adjust size to fit Pygame window
canvas = FigureCanvas(fig)
altruist_percentages = []
selfish_percentages = []
generations_data = []

# Run the Tkinter main loop
root.mainloop()
