from alleles import *

class Trait(dict):
    allele_ids = []
    def attach(self, attachee):
        self.update(attachee)
    def detach(self, attachee):
        # TODO: unattach by resetting any organism properties we set
        pass

class _ColorationTrait(Trait):
    allele_type = "coloration"
    def attach(self, organism):
        organism.has_color = True
        super().attach(organism)
    def update(self, organism):
        color_alleles = list(filter(lambda allele: allele.type == self.allele_type, organism.alleles))
        organism.r = 0
        organism.g = 0
        organism.b = 0
        for allele in color_alleles:
            if allele == Coloration_Red:
                organism.r += 255/2
            elif allele == Coloration_Green:
                organism.g += 255/2
            elif allele == Coloration_Blue:
                organism.b += 255/2
            else:
                 logging.debug("UNEXPECTED ALLELE IN COLOR CALC")

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
