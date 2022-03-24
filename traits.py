from genes import *

class Trait(dict):
    allele_ids = []
    def attach(self, attachee):
        self.update(attachee)
    def detach(self, attachee):
        # TODO: unattach by resetting any organism properties we set
        pass

class _ColorationTrait(Trait):
    gene_type = "coloration"
    def attach(self, organism):
        organism.has_color = True
        super().attach(organism)
    def update(self, organism):
        color_genes = list(filter(lambda gene: gene.type == self.gene_type, organism.genes))
        organism.r = 0
        organism.g = 0
        organism.b = 0
        for gene in color_genes:
            if gene.allele == "r":
                organism.r += 255/len(color_genes)
            elif gene.allele == "g":
                organism.g += 255/len(color_genes)
            elif gene.allele == "b":
                organism.b += 255/len(color_genes)
            else:
                 logging.debug(f"UNEXPECTED ALLELE IN COLOR CALC: {gene.allele}")

        organism.greenness = max(0, organism.g - ((organism.r + organism.b)/2))
        organism.redness = max(0, organism.r - ((organism.b + organism.g)/2))
        organism.blueness = max(0, organism.b - ((organism.r + organism.g)/2))

class _Efficiency(Trait):
    def update(self, organism):
      if organism.has_color:
        organism.efficiency = organism.blueness/255
      else:
        organism.efficiency = 0.1

Coloration = _ColorationTrait()
Efficiency = _Efficiency()
