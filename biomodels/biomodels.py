class BioModel:
    def __init__(self, id):
        import urllib
        import libsbml
        link = "http://www.ebi.ac.uk/biomodels-main/download?mid=" + id
        f = urllib.urlopen(link)
        sbmlString = f.read()
        self.document = libsbml.readSBMLFromString(sbmlString)
        if self.document.getNumErrors() > 0:
            raise Exception('Did not find valid BioModel with ID of ' + id)
        self.model = self.document.getModel()
        
    def getComponents(self):
        import libsbml
        def getAllReactionParameters(r):
            '''
            Find all reactions
            '''
            # list to hold found parameters
            params = []
            # initialize frontier to search
            frontier = []
            for i in range(r.kinetic_law.math.getNumChildren()):
                frontier.append(r.kinetic_law.math.getChild(i))
            while len(frontier) > 0:
                node = frontier.pop()

                for i in range(node.getNumChildren()):
                    frontier.append(node.getChild(i))

                if node.isName() and self.model.getParameter(node.getName()):
                    params.append(self.model.getParameter(node.getName()))

            return params
        
        reactions = [r for r in self.model.reactions]

        submodels = []
        for r in reactions:
            newDoc = libsbml.SBMLDocument(2, 4)
            newMod = newDoc.createModel()
            newMod.setId(self.model.getId() + '_' + r.getId())
            for reactant in r.reactants:
                s = self.model.getSpecies(reactant.getSpecies())
                newMod.addSpecies(s.clone())
                c = self.model.getCompartment(s.getCompartment())
                newMod.addCompartment(c.clone())
            for product in r.products:
                s = self.model.getSpecies(product.getSpecies())
                newMod.addSpecies(s.clone())
                c = self.model.getCompartment(s.getCompartment())
                newMod.addCompartment(c.clone())
            for parameter in getAllReactionParameters(r):
                newMod.addParameter(parameter.clone())


            newMod.addReaction(r.clone())

            submodels.append(newDoc)

        return submodels
    
    def getSbml(self):
        '''
        Returns SBML representation of model
        '''
        import libsbml
        return libsbml.writeSBMLToString(self.document)
    
    def getAntimony(self):
        '''
        Returns antimony representation of model
        '''
        import tellurium as te
        return te.sbmlToAntimony(self.getSbml())
    
    def getComponentSBML(self):
        '''
        Returns list of SBML models generated from each model reaction
        '''
        import libsbml
        return [libsbml.writeSBMLToString(doc) for doc in submodels]
    
    def getComponentAntimony(self):
        '''
        Returns list of antimony models generated from each model reaction
        
        '''
        import tellurium as te
        return [te.sbmlToAntimony(sbml) for sbml in newSBML]
    
    def getMatchingSpecies(self, speciesToMatch):
        '''
        Returns a list of species with matching annotations URIs
        '''
        urisToMatch = self.getResourceUris(speciesToMatch)
        matches = []
        for s in self.model.species:
            uris = self.getResourceUris(s)

            if any(i in uris for i in urisToMatch):
                matches.append(s)
        return matches

    def getMatchingReactions(self, idToMatch, reactions=None):
        '''
        Returns a list of reactions that contains a reactant with the id to match
        '''
        if reactions is None:
            reactions = self.model.reactions
        matches = []
        for r in reactions:
            for reactant in r.reactants:
                if reactant.getSpecies() == idToMatch:
                    matches.append(r.clone())
            for reactant in r.products:
                if reactant.getSpecies() == idToMatch:
                    matches.append(r)
            for modifier in r.modifiers:
                if modifier.getSpecies() == idToMatch:
                    matches.append(r)
        return matches
                        
    def getResourceUris(self, item):
                        #qualifierType=libsbml.BIOLOGICAL_QUALIFIER,
                        #biologicalQualifierType=libsbml.BQB_IS):
        '''
        Returns a list of all resource URIs for the given element
        '''
        import libsbml
        uris = []
        for i in range(item.getNumCVTerms()):
            term = item.getCVTerm(i)
            #if (term.getQualifierType() == qualifierType 
            #    and term.getBiologicalQualifierType() == biologicalQualifierType):
            for j in range(term.getNumResources()):
                uris.append(term.getResourceURI(j))
        return uris