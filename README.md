This is a simulation to show interactions between altruists and selfish individuals.

Pressing the "Start simulation" button will take all the currently inputted parameters, and if there are no value errors, will run the simulation on a pygame window.

Here are the parameters and what they individual do:

- Initial population size: The number of individuals in the 1st generation
- Max population size: The max number of individuals in any one generation. If the number of indviduals exceed this after the reproduction phase, they will be randomly culled until it matches the max size.
- Initial % of altruists: The number of altruists in the initial population, given as a percentage of the whole population
- Mutation chance (%): The chance that an offspring has the inverse of the parent's behavior. Can be betwen 0 and 100% inclusive.
- Max number of generations: The number of generations will run the simulation for, assuming the population doesn't go extinct before it reaches this value
- Family behavior distribution: Mixed means that a family could have both selfish and altruistic individuals. Homogenous means that the simulation will prioritize putting individuals with the same behavior in one family.
- Initial fitness per individual: The fitness that an individual has when they are created
- Initial family size: The number of individuals from the initial population put into one family
- Likelihood of meeting kin (%): How likely it is for an individual to meet a relative during an interaction phase. If there aren't any relatives left, the simulation will pair an individual with a non-kin individual, since there aren't any choices left.
- Rules for interactions: The first option uses Hamilton's rule for decision making, and an altruist will only perform an altrusitic act if it deems it to be worh it. For the second option, altruists are always altruistic, but gives extra benefit to relatives. This extra benefit is also a parameter, and is only available if this second interaction rule is chosen.
- Base reward for interction: The fitness that both individuals in an interaction get, guaranteed
- Selfish cost when 2 selfish individuals meet: As its name suggests, a fitness penalty for both individuals in an interaction if they are both selfish
- Benefit given to an indivdual by altruist: The fitness an altruists gives
- Cost of performing altruism for altruist: Decrease in fitness (cost) for altruism

 Additionally, a checkbox to skip animations is also present. This shortens all animations to be as short as possible.

 None of these parameters may be empty. Some parameters like population size and number of generations must be integers.
