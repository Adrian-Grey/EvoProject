import logging
logger = logging.getLogger("genes")

def createGene(name, allele):
        for gene_class in all_genes:
            if name == gene_class.__name__:
                gene = gene_class()
                gene.allele = allele
                return gene
        # no match for the gene name               
        return None

class Gene:
    def assign(self, allele):
        if allele in self.valid_alleles:
            self.allele = allele
        else:
            logger.debug(f"Tried to assign invalid allele to {self.name} gene.")
    def __str__(self):
        return f'{self.name}, {self.allele}'
    def serialize(self):
        return {
            'name': self.name,
            'allele': self.allele 
        }

class ColorationOne(Gene):
    def __init__(self):
        self.type = "coloration"
        self.name = "ColorationOne"
        self.allele = None
        self.valid_alleles = ["r", "g", "b"]
    def assign(self, allele):
        super().assign(allele)

class ColorationTwo(Gene):
    def __init__(self):
        self.type = "coloration"
        self.name = "ColorationTwo"
        self.allele = None
        self.valid_alleles = ["r", "g", "b"]
    def assign(self, allele):
        super().assign(allele)

class ColorationThree(Gene):
    def __init__(self):
        self.type = "coloration"
        self.name = "ColorationThree"
        self.allele = None
        self.valid_alleles = ["r", "g", "b"]
    def assign(self, allele):
        super().assign(allele)
        
#currently broken
#changes to one organism's gene seem to be mirrored over entire population


all_genes = [ColorationOne, ColorationTwo, ColorationThree]
