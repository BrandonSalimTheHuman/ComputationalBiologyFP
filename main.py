import tkinter as tk
from tkinter import ttk, messagebox
import math
import random


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

    # reproduce
    def reproduce(self, generation, total_population):
        return Individual(total_population + 1, self.behavior, self.family_id, generation, self.initial_fitness,
                          self.initial_fitness, parent=self.id)


# start simulation (placeholder for now)
def start_simulation():
    # getting everything from the UI
    population_size = int(population_entry.get())
    max_population_size = int(max_population_entry.get())
    # make sure max isn't < initial
    if max_population_size < population_size:
        messagebox.showerror("Input Error", "Max population size can't be lower than initial population size.")
        return
    initial_distribution = altruist_slider.get()
    mutation_chance = float(mutation_entry.get())
    max_generations = int(generations_entry.get())
    family_distribution = family_distribution_var.get()
    initial_fitness = float(fitness_entry.get())
    family_size = int(family_size_entry.get())
    kin_likelihood = kin_slider.get()
    rule = interaction_rule_var.get()
    base_reward = float(base_reward_entry.get())
    selfish_cost = float(selfish_cost_entry.get())
    altruism_benefit = float(altruism_benefit_entry.get())
    altruism_cost = float(altruism_cost_entry.get())

    # test
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
        reward_scaling = float(scaling_entry.get())
        print(f"Reward scaling: {reward_scaling}")
        rule = False
    else:
        reward_scaling = 0
        rule = True
    print(f"Base reward: {base_reward}")
    print(f"Selfish cost: {selfish_cost}")
    print(f"Altruism benefit: {altruism_benefit}")
    print(f"Altruism cost: {altruism_cost}")

    population = initialize_population(population_size, initial_distribution, initial_fitness, family_size,
                                       family_distribution)

    generation = 1
    total_population = len(population)
    for i in range(max_generations):
        interaction_phase(population, kin_likelihood, rule, base_reward, selfish_cost, altruism_cost, altruism_benefit,
                          reward_scaling)
        generation += 1
        population, total_population = reproduction_phase(mutation_chance, initial_fitness, population, generation,
                                                          total_population, max_population_size)

        print("\n==============SUMMARY OF NEW GENERATION=================")
        print("Generations:", generation)
        print("Altruists:", sum(1 for individual in population if individual.behavior == "altruist"))
        print("Selfish:", sum(1 for individual in population if individual.behavior == "selfish"))
        print("\n")


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

    # print(behaviors)

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

    # loop through popualtion
    for i in range(population_size):
        # Alternate between creating altruists and selfish individuals based on the ratio
        behavior = behaviors[i]

        # Assign family ID and reset as needed based on family size
        if family_size:
            if current_family_size >= family_size:
                family_id += 1
                current_family_size = 0
            current_family_size += 1
        else:
            family_id = None  # No family structure if family size isn't specified

        # Create individual and add to population list
        individual = Individual(i + 1, behavior, family_id, 1, initial_fitness, initial_fitness)
        population.append(individual)

    return population


# formula to calculate relatedness between two individuals
def calculate_relatedness(individual1, individual2):
    # completely different family
    if individual1.family_id != individual2.family_id:
        return 0

    # else, they're from the same family. If they're also the same generation, then they're siblings
    if individual1.generation == individual2.generation:
        return 0.5
    # if the difference is 1, then it's between a parent and offspring
    elif abs(individual1.generation - individual2.generation) == 1:
        return 1.0
    # cousins or anything more distant is considered as 0.25
    else:
        return 0.25


# this is the part where I will want to die
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
            # print([ind.id for ind in used_individuals])
            # print("")
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


def interaction_phase_hamilton(interaction_pairs, base_reward, selfish_penalty, altruism_loss, altruism_give_benefit):
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
            # print("One altruistic", calculate_relatedness(individual1, individual2))
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
            # multiply benefit by (1 + relatedness (0, 0.25 0.5 or 1) * multiplier)
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
                      altruism_give_benefit, relatedness_multiplier_bonus):
    interaction_pairs = interaction_phase_matchmaking(population, kin_likelihood)
    # print("===================BEFORE INTERACTIONS========================")
    # for individual in population:
    #     print("Id", individual.id)
    #     print("Behavior:", individual.behavior)
    #     print("Family id:", individual.family_id)
    #     print("Fitness:", individual.fitness)
    # base reward, cooperation benefit, selfish penalty, altruism loss, selfish benefit
    if hamilton:
        interaction_phase_hamilton(interaction_pairs, base_reward, selfish_penalty, altruism_loss,
                                   altruism_give_benefit)
    else:
        interaction_phase_reward_scaling(interaction_pairs, base_reward, selfish_penalty, altruism_loss,
                                         altruism_give_benefit, relatedness_multiplier_bonus)

    # print("\n\n===================AFTER INTERACTIONS========================")
    # for individual in population:
    #     print("Id", individual.id)
    #     print("Behavior:", individual.behavior)
    #     print("Family id:", individual.family_id)
    #     print("Fitness:", individual.fitness)

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


def reproduction_phase(mutation_chance, initial_fitness, population, generation, total_population, max_population_size):
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
                new_individual.parent = str("this fcking mutated lesgooooooooo " + str(tmp))
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

    print("New generation:", len(new_population))
    return new_population, total_population


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

# Start simulation button
style.configure('StartButton.TButton', font=('Arial', 16, 'bold'))
start_button = ttk.Button(root, text="Start Simulation", command=start_simulation, style='StartButton.TButton')
start_button.grid(row=13, column=0, columnspan=3, pady=padding + 20)

# Run the Tkinter main loop
root.mainloop()
