class Trait:
    def attach(self, attachee):
        pass
    def detatch(self, attachee):
        pass

coloration_alleles = get_alleles("Coloration")
coloration_tags = get_tags("Coloration")
 = Trait(coloration_alleles, coloration_tags)

class Coloration(Trait):
    def __init__(self):
        self.alleles = ["red", "green", "blue", "white", "black"]
    def attach(self, organism):
        attachee["has_coloration"] = True
    def update(self, organism):
        redness = 0
        for allele in self.alleles:
            if allele is "red":
                redness += 255/2
        attachee["redness"] = redness


class Beak(Trait):
    attach(self, attachee):
        attachee["has_beak"] = True
        attachee.get_beak_size = self.get_beak_size
    update(self, attachee):
        beak_allele =
        attachee["beak_size"] = 2


class Organism():
    def __init__(self, traits):
        self.traits = traits
        for trait in traits:
            trait.attach(self)

    def update(self):
        for trait in self.traits:
            trait.update(self)


def main():
    print("this runs ok")





if __name__ == "__main__":
    main()
