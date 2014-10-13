import bioservices
from biomodel import Biomodel
from biomodeltoolbox import getMatchingSpecies

s = bioservices.BioModels()

b1 = Biomodel(s.getModelSBMLById('BIOMD0000000051').encode('utf-8'))
b2 = Biomodel(s.getModelSBMLById('BIOMD0000000042').encode('utf-8'))

matches = getMatchingSpecies(b1.model, b2.model)

print matches