import logging
import random
import asyncio
import websockets
import pandas as pd
import numpy as np
import plotly.express as px
import os.path
import json
import sys
from traits import *
from genes import *

pd.options.plotting.backend = "plotly"

def shift_list(list):
    item = None
    if len(list) > 0:
        item = list[0]
        del list[0]
    return item

class World:
    def __init__(self):
        self.resource_increment = 50
        self.resource_cap = 500
        self.reset()
    def get_resources(self):
        return self.resources
    def increment(self):
        logging.debug(f'Incrementing world. Resources: {self.resources} + {self.resource_increment} = {self.resources + self.resource_increment}.')
        self.resources += self.resource_increment
        if self.resources > self.resource_cap:
            self.resources = self.resource_cap
            logging.debug(f'Resource count set to cap: {self.resource_cap}')
    def serialize(self):
        return {
            'current_time': self.current_time,
            'resources': self.resources
        }
    def reset(self):
        self.current_time = 0
        self.resources = 500

class Population:
    def __init__(self):
        self.reset()
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
    def reset(self):
        self.items = {}
        self.current_id = 0
        self.info = {}
    def serialize(self):
        serialized_pop = []
        for org in self.get_all(): 
            serialized_pop.append(org.serialize())
        return serialized_pop
    def deserialize(self, data):
        self.reset()
        for item in data:
            genes = list(map(lambda gene: createGene(gene["name"], gene["allele"]), item["genes"]))
            traits = list(map(lambda trait: createTrait(trait["name"]), item["traits"]))
            org = Organism(genes, traits, item["id"])
            org.age = item["age"]
            org.has_fed = item["has_fed"]
            org.mature_age = item["mature_age"]
            org.max_age = item["max_age"]
            org.gender = item["gender"]
            self.addOrganism(org)



class Organism:
    def __init__(self, genes, traits, id):
        self.id = id
        self.genes = genes
        self.traits = traits
        self.age = 0
        self.has_fed = True
        self.mature_age = 2
        self.max_age = 5
        self.gender = random.randint(0,1)
        for trait in traits:
            trait.attach(self)

    def __str__(self):
        gene_strings = list(map(lambda gene: str(gene), self.genes))
        return f'<id: {self.id}, age: {self.age}, gender: {self.gender}, genes: {", ".join(gene_strings)}>'

    def __getattr__(self, name):
        # return something when requesting an attribute that doesnt exist on this instance
        return None

    def could_breed(self):
        return self.age >= self.mature_age
    
    def serialize(self):
        trait_list = []
        for trait in self.traits:
            trait_list.append(trait.serialize())
        genes_list = []
        for gene in self.genes:
            genes_list.append(gene.serialize())
        return {
            'id': self.id,
            'genes': genes_list,
            'traits': trait_list,
            'age': self.age,
            'has_fed': self.has_fed,
            'mature_age': self.mature_age,
            'max_age': self.max_age,
            'gender': self.gender
        }


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
                logging.debug(f'Culling Organism: {org}')
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

        pop.info["average_red"] = 0
        pop.info["average_green"] = 0
        pop.info["average_blue"] = 0

        if pop_count > 0:
            pop.info["average_red"] = total_red/pop_count
            pop.info["average_green"] = total_green/pop_count
            pop.info["average_blue"] = total_blue/pop_count

    def calcBreedScore(self, pop):
        for organism in pop.items.values():
            organism.breed_score = 100
            organism.breed_score += organism.redness * -0.125 * 50
            organism.breed_score += organism.blueness * 0.125 * 50
            organism.breed_score += organism.greenness * 0 * 50
            #logging.debug(f'Organism {organism.id} breed_score: : {organism.breed_score}\n redness: {redness}, greenness: {greenness}, blueness: {blueness}')

    def calcFitness(self, pop):
        for organism in pop.items.values():
            organism.fitness = 100
            organism.fitness += organism.redness * 0.125 * 50
            organism.fitness += organism.blueness * -0.125 * 50
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

    def mutate(self, organism):
        #currently breaks the sim, causes all new children born to be one color
        mutation_target = organism.genes[random.randint(0, len(organism.genes)-1)]
        old_allele = mutation_target.allele
        mutation_target.allele = mutation_target.valid_alleles[random.randint(0, len(mutation_target.valid_alleles)-1)]
        logging.debug(f"Organism {organism.id} mutated. {old_allele} -> {mutation_target.allele}.")

    def breedPair(self, pair, pop):
        logging.debug("breedPair called")
        a = pair[0]
        b = pair[1]

        #children_count = 2Population at end of timestep
        logging.debug(f'breedPair, parent a: {a}')
        logging.debug(f'breedPair, parent b: {b}')
        #children_count = 2
        genes_a = None
        genes_b = None
        both_genes = None
        child_genes = []
        child_traits = []

        # we want to ensure that both parents have compatible traits
        # For loop should take list of relevant genes for each trait, shuffle them, give output.
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
            genes_a = list(filter(lambda gene: gene.type == trait.gene_type, a.genes))
            genes_b = list(filter(lambda gene: gene.type == trait.gene_type, b.genes))
            both_genes = genes_a + genes_b

            random.shuffle(both_genes)

            for old_gene in both_genes[0:int(len(both_genes)/2)]:
                #creates a new gene instance for child of same type as original, assigns same allele
                target_gene_class = type(old_gene)
                target_gene_instance = target_gene_class()
                target_gene_instance.allele = old_gene.allele
                child_genes.append(target_gene_instance)

            child_traits.append(trait)

        child = Organism(child_genes, child_traits, pop.nextId())
        logging.debug(f'breedPair, child: {child}')

        if random.randint(0,99) == 99:
            self.mutate(child)
            for trait in child.traits:
                trait.update(child)
            logging.debug(f'breedPair, after-mutate child: {child}')

        else:
            pass

        pop.addOrganism(child)

        logging.debug(f"Org {child.id} created. Redness: {child.redness}, R: {child.r}. Greeness: {child.greenness}, G: {child.g}. Blueness: {child.blueness}, B: {child.b}.\
        ")

    def incrementAge(self, pop):
        for organism in pop.items.values():
            organism.age += 1

    def Update(self, pop, world):
        # print("manager.Update called")
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

def resetSim():
    startup()

def startup():

    FirstOrg = Organism([ColorationOne(), ColorationOne(), ColorationTwo(), ColorationTwo()], [Coloration], pop.nextId())
    SecondOrg = Organism([ColorationOne(), ColorationOne(), ColorationTwo(), ColorationTwo()], [Coloration], pop.nextId())
    FirstOrg.gender = 1
    SecondOrg.gender = 0
    ThirdOrg = Organism([ColorationOne(), ColorationOne(), ColorationTwo(), ColorationTwo()], [Coloration], pop.nextId())
    FourthOrg = Organism([ColorationOne(), ColorationOne(), ColorationTwo(), ColorationTwo()], [Coloration], pop.nextId())
    FifthOrg = Organism([ColorationOne(), ColorationOne(), ColorationTwo(), ColorationTwo()], [Coloration], pop.nextId())
    SixthOrg = Organism([ColorationOne(), ColorationOne(), ColorationTwo(), ColorationTwo()], [Coloration], pop.nextId())
    SeventhOrg = Organism([ColorationOne(), ColorationOne(), ColorationTwo(), ColorationTwo()], [Coloration], pop.nextId())

    initial_generation = [FirstOrg, SecondOrg, ThirdOrg, FourthOrg, FifthOrg, SixthOrg, SeventhOrg]

    for organism in initial_generation:
        for gene in organism.genes:
            if gene.allele == None:
                gene.assign(gene.valid_alleles[random.randint(0,len(gene.valid_alleles)-1)])
            else:
                pass

    for organism in initial_generation:
        for trait in organism.traits:
            trait.update(organism)

    pop.reset()
    world.reset()
    report.clear()
    population_report.clear()
    population_report.append("time,population,average_red,average_green,average_blue")
    report.append(f'Time,ID,Age,Red,Green,Blue')

    for org in initial_generation:
        pop.addOrganism(org)

def snapshot(filename):

    save_file_path = os.path.join("save_files", str(filename))

    serialized_pop = pop.serialize()
    serialized_world = world.serialize()
    current_id = pop.current_id

    snapshot_file = open(save_file_path, "w+")
    json_string = json.dumps({ 
        "current_id": current_id,
        "world": serialized_world,
        "population": serialized_pop,
    },  indent=4)
    logging.debug(f"snapshot: {json_string}")
    snapshot_file.write(json_string)
    snapshot_file.close()

    #return json.dumps({
    #    "population": serialized_pop,
    #    "world": serialized_world
    #})

def load_snapshot(filename):
    save_file_path = os.path.join("save_files", filename)
    if os.path.exists(save_file_path):
        data = json.load(open(save_file_path, "r"))
        world.current_time = data["world"]["current_time"]
        world.resources = data["world"]["resources"]
        pop.deserialize(data["population"])
        pop.current_id = data["current_id"]
        #current id must be set after pop deserialize
        return f"Started with savefile {filename}"
    else:
        return f"Failed to start, save file does not exist"
        

def showColors():
    color_frame = pd.read_csv('population.csv', usecols = ['time', 'average_red', 'average_green', 'average_blue'])

    color_frame.plot(x='time', y=['average_blue','average_red','average_green']).show()

def showPop():
    pop_frame = pd.read_csv('population.csv', usecols = ['time', 'population'])

    pop_frame.plot(x='time', y=['population']).show()

def showZoomed():
    zoomed_frame = pd.read_csv('population.csv', usecols = ['population', ''])

def startSim(save):
    if save == "none":
        startup()
        return "Started with fresh start"
    else:
        return load_snapshot(save)
    
async def main():
    # Start the websocket server and run forever waiting for requests
    async with websockets.serve(handleRequest, "localhost", 8765):
        await asyncio.Future()  # run forever

async def handleRequest(websocket, path):
    async for message in websocket:
        parts = message.split(",")
        command_name = parts[0]
        logging.debug(f"Got websocket request")
        if command_name == "start":
            print("Start request recieved")
            if len(parts) > 1:
                status = startSim(parts[1])
            else:
                status = startSim("none")
            await websocket.send(f"{status}")
        elif command_name == "getPop":
            print("Population count request recieved")
            await websocket.send(f"Population count: {len(pop.get_all())}")
            print("Population count sent")
        elif command_name == "runSim":
            print(f"Incrementing simulation by t={parts[1]}")
            runSim(int(parts[1]))
            await websocket.send(f"Simulation incremented by t={parts[1]}")
        elif command_name == "reset":
            print("Reset command recieved")
            resetSim()
            print("Simulation reset")
            await websocket.send("Simulation reset")
        elif command_name == "showColors":
            showColors()
            await websocket.send("Ok")
        elif command_name == "showPop":
            showPop()
            await websocket.send("Ok")
        elif command_name == "showAll":
            showPop()
            showColors()
            await websocket.send("Ok")
        elif command_name == "snapshot":
            snapshot(parts[1])
            await websocket.send(f"Saved gamestate to file {parts[1]}")
        elif command_name == "quit":
            sys.exit()
        else:
            await websocket.send("Unknown Command")
            print(f"Unknown command: {command_name}")


if __name__ == "__main__":
    logging.basicConfig(filename='debug1.txt',level=logging.DEBUG, filemode='w')
    asyncio.run(main())
