import logging
import random
import traits
from alleles import *

logging.basicConfig(filename='debug.txt',level=logging.DEBUG, filemode='w')

class Organism(dict):
    def __init__(self, alleles, traits, id):
        self.id = id
        self.alleles = alleles
        self.traits = traits
        for trait in traits:
            trait.attach(self)
        logging.debug(f'Creating Organism: {self.id}')

    def __getattr__(self, name):
        # return something when requesting an attribute that doesnt exist on this instance
        return None

def main():
    # make an organism without the Coloration trait
    # it has the alleles, but not the trait to use them
    uncoloredOrganism = Organism([Coloration_Blue, Coloration_Blue, Coloration_Green], [], "o0")
    logging.debug(f'Organism {uncoloredOrganism.id} hasattr {hasattr(uncoloredOrganism, "has_color")}, has_color: {uncoloredOrganism.has_color}')

    # make an organism with the Coloration trait
    bluishOrganism = Organism([Coloration_Blue, Coloration_Blue, Coloration_Green], [traits.Coloration], "o1")
    logging.debug(f'Organism {bluishOrganism.id} has_color: {bluishOrganism.has_color}, redness: {bluishOrganism.redness}, greenness: {bluishOrganism.greenness}, blueness: {bluishOrganism.blueness}')

    # add an efficiency trait
    bluishOrganism.traits.append(traits.Efficiency)
    traits.Efficiency.attach(bluishOrganism)
    logging.debug(f'Organism {bluishOrganism.id} efficiency: {bluishOrganism.efficiency}')

    # this one has the efficiency trait, but not the coloration trait
    hungryOrganism = Organism([Coloration_Blue, Coloration_Blue, Coloration_Green], [traits.Efficiency], "o2")
    logging.debug(f'Organism {hungryOrganism.id} efficiency: {hungryOrganism.efficiency}')


if __name__ == "__main__":
    main()
