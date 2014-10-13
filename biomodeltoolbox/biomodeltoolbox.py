import _annotations

def getMatchingSpecies(m1, m2):
    '''
    Returns a list of species with matching annotations URIs
    '''
    import libsbml
    if not isinstance(m1, libsbml.Model) or not isinstance(m2, libsbml.Model):
        raise Exception('Need to call with two libsbml.Model instances')

    matches = []
    for s1 in m1.species:
        for s2 in m2.species:
            match = _annotations.matchSpeciesChebi(s1, s2)
            if len(match['exact']) or len(match['children']) or len(match['parents']):
                matches.append(match)
    return matches

def getMatchingReactions(modelOrList, idToMatch):
    '''
    Returns a list of reactions that contains a reactant with the id to match
    '''
    import libsbml
    if isinstance(modelOrList, libsbml.Model):
        reactions = modelOrList.reactions
    else:
        reactions = modelOrList
    matches = []
    for r in reactions:
        for reactant in r.reactants:
            if reactant.getSpecies() == idToMatch:
                matches.append(r)
        for reactant in r.products:
            if reactant.getSpecies() == idToMatch:
                matches.append(r)
        for modifier in r.modifiers:
            if modifier.getSpecies() == idToMatch:
                matches.append(r)
    return matches
