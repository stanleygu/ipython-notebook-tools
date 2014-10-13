import bioservices
from biomodel import Biomodel
import BIOMD0000000042 as nielsen
import BIOMD0000000051 as chassagnole
import biomodeltoolbox as bmt
s = bioservices.BioModels()

# b1 = Biomodel(s.getModelSBMLById('BIOMD0000000051').encode('utf-8'))
# b2 = Biomodel(s.getModelSBMLById('BIOMD0000000042').encode('utf-8'))
# matches = bmt.getMatchingSpecies(b1.model, b2.model, logging=True)

matches = bmt.getMatchingSpecies(nielsen.sbml.getModel(), chassagnole.sbml.getModel(), logging=True)

bmt.printMatchingSpecies(matches)