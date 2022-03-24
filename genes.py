import logging
logger = logging.getLogger("genes")

class Gene:
    def __init__(self, type, name, valid_alleles):
        self.type = type
        self.name = name
        self.allele = None
        self.valid_alleles = valid_alleles
    def assign(self, allele):
        if allele in self.valid_alleles:
            self.allele = allele
        else:
            logger.debug(f"Tried to assign invalid allele to {self.name} gene.")

Coloration_One = Gene("coloration", "Coloration_One", ["r", "b", "g"])
Coloration_Two = Gene("coloration", "Coloration_Two", ["r", "b", "g"])
Coloration_Three = Gene("coloration", "Coloration_Three", ["r", "b", "g"])



all_genes = [Coloration_One, Coloration_Two, Coloration_Three]
