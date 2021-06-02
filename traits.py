class Trait(dict):
    allele_ids = []
    def attach(self, attachee):
        self.update(attachee)
    def detach(self, attachee):
        # TODO: unattach by resetting any organism properties we set
        pass

class _ColorationTrait(Trait):
    allele_ids = ["red", "blue", "green"]
    def attach(self, organism):
        organism.has_color = True
        super().attach(organism)
    def update(self, organism):
        color_alleles = list(filter(lambda allele: allele.type in self.allele_ids, organism.alleles))
        r = 0
        g = 0
        b = 0
        for allele in color_alleles:
            if allele.type == "red":
                r += 255/2
            elif allele.type == "green":
                g += 255/2
            elif allele.type == "blue":
                b += 255/2
        organism.greenness = max(0, g - ((r + b)/2))
        organism.redness = max(0, r - ((b + g)/2))
        organism.blueness = max(0, b - ((r + g)/2))


class _Efficiency(Trait):
    def update(self, organism):
      if organism.has_color:
        organism.efficiency = organism.blueness/255
      else:
        organism.efficiency = 0.1

Coloration = _ColorationTrait()
Efficiency = _Efficiency()