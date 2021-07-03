import logging
import random
import traits
from alleles import *

#Fix traits/alleles implementation in evo1

logging.basicConfig(filename='debug.txt',level=logging.DEBUG, filemode='w')

def shift_list(list):
    item = None
    if len(list) > 0:
        item = list[0]
        del list[0]
    return item

class World:
    def __init__(self):
        self.current_time = 0
        self.resources = 500
        self.base_resources = 500
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

class Organism:
    def __init__(self, alleles, traits, id):
        self.id = id
        self.alleles = alleles
        self.traits = traits
        self.age = 0
        self.has_fed = True
        self.mature_age = 2
        self.max_age = 5
        self.gender = random.randint(0,1)
        for trait in traits:
            trait.attach(self)

    def __getattr__(self, name):
        # return something when requesting an attribute that doesnt exist on this instance
        return None

    def could_breed(self):
        return self.age >= self.mature_age


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

    def cull(self, pop):
        for org in pop.get_all():
            if org.age >= org.max_age or org.has_fed == False:
                logging.debug(f'Culling Organism: {org.id}. Fed: {org.has_fed}. Age: {org.age}')
                del pop.items[org.id]

    def logPopulation(self, pop, report, world):
        for organism in pop.items.values():
            report.append(f'{world.current_time},{organism.id},{organism.age},{organism.r},{organism.g},{organism.b}')

    def calcBreedScore(self, pop):
        for organism in pop.items.values():
            organism.breed_score = 100
            organism.breed_score += organism.redness * -1 * 50
            organism.breed_score += organism.blueness * 1 * 50
            organism.breed_score += organism.greenness * 0 * 50
            #logging.debug(f'Organism {organism.id} breed_score: : {organism.breed_score}\n redness: {redness}, greenness: {greenness}, blueness: {blueness}')

    def calcFitness(self, pop):
        for organism in pop.items.values():
            organism.fitness = 100
            organism.fitness += organism.redness * 1 * 50
            organism.fitness += organism.blueness * -1 * 50
            organism.fitness += organism.greenness * 0 * 50
            #logging.debug(f'Organism {organism.id} fitness: : {organism.fitness}\n redness: {organism.redness}, greenness: {organism.greenness}, blueness: {organism.blueness}')


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
        trait_alleles_a = None
        trait_alleles_b = None
        both_alleles = None
        child_alelles = []
        child_traits = []

        # we want to ensure that both parents have compatible traits and alleles for those traits
        # For loop should take list of relevant alleles for each trait, shuffle them, give output.
        # If either parent has a trait the other lacks, abort the whole function and move to next pair.
        for trait in a.traits:
            if not trait in b.traits:
                logging.debug(f"Pairing rejected: Org {b.id} doesnt have trait {trait}")
                return

        for trait in b.traits:
            if not trait in a.traits:
                logging.debug(f"Pairing rejected: Org {a.id} doesnt have trait {trait}")
                return

        for trait in a.traits:
            trait_alleles_a = list(filter(lambda allele: allele.type == trait.allele_type, a.alleles))
            trait_alleles_b = list(filter(lambda allele: allele.type == trait.allele_type, b.alleles))
            both_alleles = trait_alleles_a + trait_alleles_b

            random.shuffle(both_alleles)

            logging.debug(f"both_alleles length: {len(both_alleles)}")

            for allele in both_alleles[0:2]:
                child_alelles.append(allele)

            child_traits.append(trait)

        child = Organism(child_alelles, child_traits, pop.nextId())

        pop.addOrganism(child)

        logging.debug(f"Org {child.id} created. Redness: {child.redness}, R: {child.r}. Greeness: {child.greenness}, G: {child.g}. Blueness: {child.blueness}, B: {child.b}.")

    def incrementAge(self, pop):
        for organism in pop.items.values():
            organism.age += 1

    def Update(self, pop, world):
        # A new breeding season
        logging.debug(f"Population at start of timestep {world.current_time}: {len(pop.get_all())}")
        self.calcFitness(pop)
        self.resource_distribute(pop, world)
        self.incrementAge(pop)
        self.calcBreedScore(pop)
        pairs = self.selectPairs(pop)
        for pair in pairs:
            self.breedPair(pair, pop)
        self.cull(pop)
        logging.debug(f"Population at end of timestep {world.current_time}: {len(pop.get_all())}")
        world.reset()
        self.time_advance(world)


def main():
    report = []
    population_report = []
    pop = Population()

    Adam = Organism([Coloration_Blue, Coloration_Blue], [traits.Coloration], pop.nextId())
    Eve = Organism([Coloration_Red, Coloration_Blue], [traits.Coloration], pop.nextId())

    Adam.gender = 1
    Eve.gender = 0

    pop.addOrganism(Adam)
    pop.addOrganism(Eve)



    # Define the initial Adam & Eve generation
    manager = SystemManager()
    world = World()
    # Output the CSV column headers
    report.append(f'Time,ID,Age,Red,Green,Blue')
    while world.current_time < 50:
        manager.Update(pop, world)
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
