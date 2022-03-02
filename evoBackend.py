import logging
import random
import asyncio
import websockets
import traits
from alleles import *

# using pandas and plotly to visualize population data

# add reset method to UI to reset pop simulation, avoiding need to close and re-run evoBackend

logging.basicConfig(filename='debug1.txt',level=logging.DEBUG, filemode='w')

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
        self.resource_increment = 50
        self.resource_cap = 500
    def get_resources(self):
        return self.resources
    def increment(self):
        logging.debug(f'Incrementing world. Resources: {self.resources} + {self.resource_increment} = {self.resources + self.resource_increment}.')
        self.resources += self.resource_increment
        if self.resources > self.resource_cap:
            self.resources = self.resource_cap
            logging.debug(f'Resource count set to cap: {self.resource_cap}')

class Population:
    def __init__(self):
        self.items = {}
        self.current_id = 0
        self.info = {}
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
        total_red = 0
        total_green = 0
        total_blue = 0
        for organism in pop.items.values():
            report.append(f'{world.current_time},{organism.id},{organism.age},{organism.r},{organism.g},{organism.b}')
            total_red += organism.r
            total_green += organism.g
            total_blue += organism.b
        pop_count = len(pop.get_all())
        pop.info["average_red"] = total_red/pop_count
        pop.info["average_green"] = total_green/pop_count
        pop.info["average_blue"] = total_blue/pop_count

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
        logging.debug("selectPairs called")
        males = []
        females = []
        for organism in pop.items.values():
            logging.debug(f"selectPairs: organism could breed? {organism.could_breed()}")
            if organism.could_breed():
                if organism.gender == 0:
                    females.append(organism)
                elif organism.gender == 1:
                    males.append(organism)
                else:
                    logging.debug(f'UNEXPECTED GENDER VALUE: {organism.gender}')
        logging.debug(f"{len(males)} males, {len(females)} females")
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
        logging.debug("breedPair called")
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

            #logging.debug(f"both_alleles length: {len(both_alleles)}")

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
        print("manager.Update called")
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
        world.increment()
        self.time_advance(world)


report = []
population_report = ["time,population,average_red,average_green,average_blue"]
pop = Population()
manager = SystemManager()
world = World()

def runSim(count):
    while count > 0:
        logging.debug(f"runSim, calling manager.Update")
        manager.Update(pop, world)
        manager.logPopulation(pop, report, world)
        pop_count = len(pop.get_all())
        population_report.append(f"{world.current_time},{pop_count}, {pop.info['average_red']},{pop.info['average_green']},{pop.info['average_blue']}")
        output = open("output.csv", "wt")
        for item in report:
            output.write(f"{item}\n")
        output.close()

        output = open("population.csv", "wt")
        for item in population_report:
            output.write(f"{item}\n")
        output.close()
        count -= 1
    return population_report

async def main():

    # Define the initial Adam & Eve generation
    Adam = Organism([Coloration_Green, Coloration_Blue], [traits.Coloration], pop.nextId())
    Eve = Organism([Coloration_Red, Coloration_Blue], [traits.Coloration], pop.nextId())

    Adam.gender = 1
    Eve.gender = 0

    pop.addOrganism(Adam)
    pop.addOrganism(Eve)

    # Output the CSV column headers
    report.append(f'Time,ID,Age,Red,Green,Blue')

    # Start the websocket server and run forever waiting for requests
    async with websockets.serve(handleRequest, "localhost", 8765):
        await asyncio.Future()  # run forever

async def handleRequest(websocket, path):
    # right now, message is a string.
    # but we could have a command, with a structure like:
    # { name: "runSim", count: n-times }
    # commandname,param
    async for message in websocket:
        parts = message.split(",")
        command_name = parts[0]
        logging.debug(f"Got websocket request")
        if command_name == "getPop":
            print("Population count request recieved")
            await websocket.send(f"{len(pop.get_all())}")
            print("Population count sent")
        elif command_name == "runSim":
            print(f"Incrementing simulation by t={parts[1]}")
            runSim(int(parts[1]))
            await websocket.send("ok")
        else:
            await websocket.send("Unknown Command")
            print(f"{message}")


if __name__ == "__main__":
    asyncio.run(main())
