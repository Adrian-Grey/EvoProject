class Allele:
    def __init__(self, type, name):
        self.type = type
        self.name = name

Coloration_Red = Allele("coloration", "Coloration_Red")
Coloration_Blue = Allele("coloration", "Coloration_Blue")
Coloration_Green = Allele("coloration", "Coloration_Green")

all_alleles = [Coloration_Red, Coloration_Blue, Coloration_Green]
