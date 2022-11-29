import random
import matplotlib.pyplot as plt
import time

# константы задачи
HIGHEST = 63
LOWEST = 0

# константи генетичного алгоритму
POPULATION_SIZE = 300    # кількість особин в популяції
P_CROSSOVER = 0.9       # вирогідність схрещування
P_MUTATION = 0.1        # вирогідність мутації особини
MAX_GENERATIONS = 100   # кількість поколінь

TOUR_CANDIDATES = 2     # чисельність турніру

# RANDOM_SEED = 10
# random.seed(RANDOM_SEED)

max_fitness_values_tournament = []  # для графіка максимальні значення фітнесу кожного покоління
avg_fitness_values_tournament = []  # для графіка суредні значення фітнесу кожного покоління

max_fitness_values_roulette = []  # для графіка максимальні значення фітнесу кожного покоління
avg_fitness_values_roulette = []  # для графіка суредні значення фітнесу кожного покоління


def generate_random_individual():
    result = []
    for i in range(3):
        # result.append(random.randint(0, 9))
        result.append(random.uniform(LOWEST, HIGHEST))
    return result


def generate_population(__population_size=POPULATION_SIZE):
    __population = []  # популяція
    for i in range(__population_size):
        __population.append(generate_random_individual())  # добавляємо хромосому в популяцію
    return __population


# функція підрахунку придатності індивіда.
def function_calculation(x, y, z):
    try:
        return ((x * y * z) / ((128 + x) * (x + y) * (y + z) * (z + 128))) * 100000
    except:
        return 0


# генеруємо масив з прорахованою придатністю кожного індивіда
def fitness_calculate(__population):
    result = []

    for i in range(len(__population)):
        x = __population[i][0]
        y = __population[i][1]
        z = __population[i][2]

        result.append(function_calculation(x, y, z))
    return result

# відбір нової популяцію турніром
def select_tournament(__population):
    tournament_selection = []

    for i in range(len(__population)):
        tour_candidates = random.choices(__population, k=TOUR_CANDIDATES)

        tour_candidate_max_fitness = function_calculation(tour_candidates[0][0], tour_candidates[0][1],
                                                          tour_candidates[0][2])
        tour_candidate_index_in_tour_candidates = 0

        for j in range(1, len(tour_candidates)):
            candidate_fitness = function_calculation(tour_candidates[j][0], tour_candidates[j][1],
                                                     tour_candidates[j][2])
            if candidate_fitness > tour_candidate_max_fitness:
                tour_candidate_max_fitness = candidate_fitness
                tour_candidate_index_in_tour_candidates = j

        tournament_selection.append(tour_candidates[tour_candidate_index_in_tour_candidates])

    return tournament_selection


# відбір нової популяцію рулеткою
def select_roulette(__population):
    rouletted_population = []
    __fitness_values = fitness_calculate(__population)
    sum_fitness = sum(__fitness_values)
    __proportion = []
    current_probability = 0
    for individ_fitness in __fitness_values:
        current_probability += individ_fitness / sum_fitness
        __proportion.append(current_probability)

    tmp_population = list(zip(__population, __proportion))

    for i in range(len(tmp_population)):
        pick = random.uniform(0, 1)
        for j in range(len(tmp_population)):
            if tmp_population[j][1] >= pick:
                rouletted_population.append(tmp_population[j][0])
                break

    return rouletted_population


# перекидання двох випадкових генів між парою родителів
def cross_genes(ind1, ind2):
    gen_to_crossover = random.randint(0, 2)
    tmp_gen = ind1[gen_to_crossover]
    ind1[gen_to_crossover] = ind2[gen_to_crossover]
    ind2[gen_to_crossover] = tmp_gen
    return ind1, ind2


# схрещування популяції. схрещуємо попарно 2 сусідів, якщо вирогідність схрещування
# трапилась, якщо ні - індивід переходить в нову популяцію
def crossover(__population):
    new_generation = []
    n = 0
    while n < len(__population):
        if len(__population) - n <= 1:
            new_generation.append(__population[n])
            break

        if random.random() < P_CROSSOVER:  # вирогідність спарювання P_CROSSOVER
            tmp_crossed = cross_genes(__population[n], __population[n + 1])
            for ind in tmp_crossed:
                new_generation.append(ind)
            n += 2
        else:
            new_generation.append(__population[n])
            n += 1
    return new_generation


def mutation(__population):
    mutated_population = []
    for ind in __population:
        if random.random() < P_MUTATION:  # вирогідність мутації P_CROSSOVER
            mutated_gen_index = random.randint(0, 2)
            mutated_chromosome = []
            for i in range(3):
                if i == mutated_gen_index:
                    mutated_chromosome.append(random.uniform(LOWEST, HIGHEST))
                else:
                    mutated_chromosome.append(ind[i])

            mutated_population.append(mutated_chromosome)
        else:
            mutated_population.append(ind)
    return mutated_population


# перша популяція
population = generate_population()

fitness_values_tournament = fitness_values_roulette = fitness_calculate(population)

max_fitness_values_tournament.append(max(fitness_values_tournament))
avg_fitness_values_tournament.append(sum(fitness_values_tournament) / len(fitness_values_tournament))

max_fitness_values_roulette.append(max(fitness_values_roulette))
avg_fitness_values_roulette.append(sum(fitness_values_roulette) / len(fitness_values_roulette))

best_index = fitness_values_roulette.index(max(fitness_values_roulette))

print("ПЕРШЕ ПОКОЛІННЯ")
print("Макс f:", max(fitness_values_roulette), "AVG f:,", sum(fitness_values_roulette) / len(fitness_values_roulette),
      "Найкращій індивідум: x=", population[best_index][0], "y=",
      population[best_index][1], "z=", population[best_index][2])
print("-----------------------------------------------------")


# ROULETTE
def run_roulette():
    generation_counter = 0
    population_roulette = population

    start = time.time()  # запускаємо таймер

    while generation_counter < MAX_GENERATIONS:
        generation_counter += 1

        population_roulette = select_roulette(population_roulette)  # селекція
        population_roulette = crossover(population_roulette)  # схрещування
        population_roulette = mutation(population_roulette)  # мутація

        # рахуємо придатність для кожного індивіда в популяції
        fitness_values_roulette = fitness_calculate(population_roulette)
        # для графіка зберігаємо значення придатносі найкращого індивіда
        max_fitness_values_roulette.append(max(fitness_values_roulette))
        # для графіка зберігаємо значення середньої придатності популяції
        avg_fitness_values_roulette.append(sum(fitness_values_roulette) / len(fitness_values_roulette))

    end = time.time() - start  # рахуєм час виконання алгоритму "рулеткою"

    best_index = fitness_values_roulette.index(max(fitness_values_roulette))
    print()
    print("ROULETTE -- час виконання:", end)
    print("Макс f:", max(fitness_values_roulette), "AVG f:,",
          sum(fitness_values_roulette) / len(fitness_values_roulette), "Найкращій індивідум: x=",
          population_roulette[best_index][0], "y=",
          population_roulette[best_index][1], "z=", population_roulette[best_index][2])

    print("-----------------------------------------------------")


# TOURNAMENT
def run_tournament():
    generation_counter = 0
    population_tournament = population
    start = time.time()  # запускаємо таймер

    while generation_counter < MAX_GENERATIONS:
        generation_counter += 1

        population_tournament = select_tournament(population_tournament)  # селекція
        population_tournament = crossover(population_tournament)  # схрещування
        population_tournament = mutation(population_tournament)  # мутація

        # рахуємо придатність для кожного індивіда в популяції
        fitness_values_tournament = fitness_calculate(population_tournament)
        # для графіка зберігаємо значення придатносі найкращого індивіда
        max_fitness_values_tournament.append(max(fitness_values_tournament))
        # для графіка зберігаємо значення середньої придатності популяції
        avg_fitness_values_tournament.append(sum(fitness_values_tournament) / len(fitness_values_tournament))

    end = time.time() - start  # рахуєм час виконання алгоритму "рулеткою"

    best_index = fitness_values_tournament.index(max(fitness_values_tournament))
    print()
    print("TOURNAMENT  -- час виконання:", end)
    print("Макс f:", max(fitness_values_tournament), "AVG f:,",
          sum(fitness_values_tournament) / len(fitness_values_tournament), "Найкращій індивідум: x=",
          population_tournament[best_index][0], "y=",
          population_tournament[best_index][1], "z=", population_tournament[best_index][2])


# run_tournament()
run_roulette()

# виводим графіки
fig, ax = plt.subplots()
line_r_max, = plt.plot(max_fitness_values_roulette, label='рулетка макс')
line_r_avg, = plt.plot(avg_fitness_values_roulette, label='рулетка сер')
line_t_max, = plt.plot(max_fitness_values_tournament, label='турнір макс')
line_t_avg, = plt.plot(avg_fitness_values_tournament, label='турнір сер')
plt.xlabel('Покоління')
plt.ylabel('Макс/средняя приспособленность')
# plt.title('Залежність максимальної та середньої пристосованості від покоління')
# plt.title('Рулетка - 25 особини')
# plt.title( POPULATION_SIZE +' особини')
ax.legend(handles=[line_r_max, line_r_avg])
# ax.legend(handles=[line_t_max, line_t_avg])
# ax.legend(handles=[line_r_max, line_r_avg, line_t_max, line_t_avg])

plt.show()
