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
        self.getComponents()
        
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

        self.submodels = []
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

            self.submodels.append(newDoc)
    
    def getComponentSBML(self):
        import libsbml
        return [libsbml.writeSBMLToString(doc) for doc in submodels]
    
    def getComponentAntimony(self):
        import tellurium as te
        return [te.sbmlToAntimony(sbml) for sbml in newSBML]
