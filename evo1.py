import logging
import random
logging.basicConfig(filename='debug.txt',level=logging.ERROR, filemode='w')

def shift_list(list):
    item = None
    if len(list) > 0:
        item = list[0]
        del list[0]
    return item

#Next steps:
#make time system, rearrange data output (have output.html request and output data itself)

class World:
    def __init__(self):
        self.current_time = 0
        self.resources = 1000
        self.base_resources = 1000
    def get_resources(self):
        return self.resources
    def reset(self):
        logging.debug(f'Resetting. Resources: {self.resources}')
        self.resources = self.base_resources

class Population:
    def __init__(self):
        self.items = {}
        self.current_id = 0
    def find_by_id(self, id):
        return self.items[id]
    def filter_mature(self, minAge):
        all_organisms = self.get_all()
        by_age = []
        for org in all_organisms:
            if org.age >= minAge:
                by_age.append(org)
        return by_age
    def addOrganism(self, organism):
        self.items[organism.id] = organism
    def nextId(self):
        self.current_id = self.current_id + 1
        return self.current_id
    def get_all(self):
        return list(self.items.values())

class Allele:
    def __init__(self):
        pass

class ColorAllele(Allele):
    def __init__(self, type):
        self.type = type

class Organism:
    def __init__(self, color_alleles, id):
        # 0 = female, 1 = male
        self.gender = random.randint(0,1)
        self.color_alleles = color_alleles
        self.properties = {
            "r": 0,
            "g": 0,
            "b": 0,
        }
        for allele in color_alleles:
            if allele.type == "red":
                self.properties["r"] += 255/2
            elif allele.type == "green":
                self.properties["g"] += 255/2
            elif allele.type == "blue":
                self.properties["b"] += 255/2

        self.age = 0
        self.breed_score = 100
        self.fitness = 100
        self.has_fed = True
        self.id = id
        logging.debug(f'Creating Organism: {self.id}')

    def could_breed(self):
        return (self.age >= 2)

class SystemManager:

    def time_advance(self, world):
        world.current_time += 1
        logging.debug(f'Time advanced to {world.current_time}')

    def resource_distribute(self, pop, world):
        fitness_list = sorted(pop.get_all(), key=lambda item: item.fitness, reverse = True)
        for org in fitness_list:
            if world.resources > 0:
                org.has_fed = True
                world.resources -= 1
            else:
                logging.debug(f'Organism {org.id} unfed.')
                org.has_fed = False

    def cull(self, pop, maxAge):
        for org in pop.get_all():
            if org.age >= maxAge or org.has_fed == False:
                logging.debug(f'Culling Organism: {org.id}. Fed: {org.has_fed}')
                del pop.items[org.id]

    def logPopulation(self, pop, report, world):
        for organism in pop.items.values():
            report.append(f'{world.current_time},{organism.id},{organism.age},{organism.properties["r"]},{organism.properties["g"]},{organism.properties["b"]}')

    def calcBreedScore(self, pop):
        for organism in pop.items.values():
            organism.breed_score = 100
            r = organism.properties["r"]/255
            g = organism.properties["g"]/255
            b = organism.properties["b"]/255
            redness = max(0, r - ((b + g)/2))
            greenness = max(0, g - ((r + b)/2))
            blueness = max(0, b - ((r + g)/2))
            organism.breed_score += redness * -1 * 50
            organism.breed_score += blueness * 1 * 50
            organism.breed_score += greenness * 0 * 50
            #logging.debug(f'Organism {organism.id} breed_score: : {organism.breed_score}\n redness: {redness}, greenness: {greenness}, blueness: {blueness}')

    def calcFitness(self, pop):
        for organism in pop.items.values():
            organism.fitness = 100
            r = organism.properties["r"]/255
            g = organism.properties["g"]/255
            b = organism.properties["b"]/255
            redness = max(0, r - ((b + g)/2))
            greenness = max(0, g - ((r + b)/2))
            blueness = max(0, b - ((r + g)/2))
            organism.fitness += redness * 1 * 50
            organism.fitness += blueness * -1 * 50
            organism.fitness += greenness * 0 * 50
            logging.debug(f'Organism {organism.id} fitness: : {organism.fitness}\n redness: {redness}, greenness: {greenness}, blueness: {blueness}')


    def selectPairs(self, pop):
        males = []
        females = []
        for organism in pop.items.values():
            if organism.could_breed():
                if organism.gender == 0:
                    females.append(organism)
                elif organism.gender == 1:
                    males.append(organism)
                else:
                    logging.debug(f'UNEXPECTED GENDER VALUE: {organism.gender}')
        pairs = []
        if len(males) >= 1:
            def organism_to_string(org):
                return str(org.id)
            males = sorted(males, key=lambda item: item.breed_score, reverse = True)
            females = sorted(females, key=lambda item: item.breed_score, reverse = True)
            for male in males:
                female0 = shift_list(females)
                if (female0 is not None):
                    pairs.append([male, female0])
                else:
                    break
                female1 = shift_list(females)
                if (female1 is not None):
                    pairs.append([male, female1])
                else:
                    break
                female2 = shift_list(females)
                if (female2 is not None):
                    pairs.append([male, female2])
                else:
                    break

        return pairs

    def breedPair(self, pair, pop):
        a = pair[0]
        b = pair[1]
        children_count = 2
        outcomes = [
            [a.color_alleles[0], b.color_alleles[0]],
            [a.color_alleles[0], b.color_alleles[1]],
            [a.color_alleles[1], b.color_alleles[0]],
            [a.color_alleles[1], b.color_alleles[1]]
        ]
        for i in range(0, children_count):
            child_alelles = outcomes[random.randint(0,3)]
            # create new child with generated alleles
            child = Organism(child_alelles, pop.nextId())
            # add the new child to the population
            pop.addOrganism(child)

    def incrementAge(self, pop):
        for organism in pop.items.values():
            organism.age += 1

    def Update(self, pop, maxAge, world):
        # A new breeding season
        logging.debug(f"Population at start of timestep {world.current_time}: {len(pop.get_all())}")
        self.calcFitness(pop)
        self.resource_distribute(pop, world)
        self.incrementAge(pop)
        self.calcBreedScore(pop)
        pairs = self.selectPairs(pop)
        for pair in pairs:
            self.breedPair(pair, pop)
        self.cull(pop, maxAge)
        logging.debug(f"Population at end of timestep {world.current_time}: {len(pop.get_all())}")
        world.reset()
        self.time_advance(world)


def main():
    report = []
    population_report = []
    pop = Population()
    maxAge = 3
    r = ColorAllele("red")
    b = ColorAllele("blue")
    g = ColorAllele("green")

    pop.addOrganism(Organism([r, r], pop.nextId()))
    pop.addOrganism(Organism([g, b], pop.nextId()))
    pop.addOrganism(Organism([g, r], pop.nextId()))
    pop.addOrganism(Organism([g, r], pop.nextId()))
    pop.addOrganism(Organism([r, b], pop.nextId()))
    pop.addOrganism(Organism([g, b], pop.nextId()))
    pop.addOrganism(Organism([r, b], pop.nextId()))
    pop.addOrganism(Organism([b, r], pop.nextId()))
    pop.addOrganism(Organism([g, r], pop.nextId()))
    pop.addOrganism(Organism([b, b], pop.nextId()))
    pop.addOrganism(Organism([g, b], pop.nextId()))
    pop.addOrganism(Organism([r, b], pop.nextId()))
    # Define the initial Adam & Eve generation
    manager = SystemManager()
    world = World()
    # Output the CSV column headers
    report.append(f'Time,ID,Age,Red,Green,Blue')
    while world.current_time < 50:
        manager.Update(pop, maxAge, world)
        manager.logPopulation(pop, report, world)
        population_report.append(len(pop.get_all()))

    output = open("output.csv", "wt")
    for item in report:
        output.write(f"{item}\n")
    output.close()

    output = open("population.csv", "wt")
    for item in population_report:
        output.write(f"{item}\n")
    # write out the report list to a file


if __name__ == "__main__":
    main()
