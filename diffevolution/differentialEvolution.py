class DiffEvolution():
    def __init__(self, rr, fitnessFcn, simFcn,
                 ASYNC=False,
                 CROSSOVER_RATE=0.5,
                 FITNESS_THRESHOLD=1e-6,
                 MAX_GENS=50,
                 MIXING_RATE=0.8,
                 NON_NEGATIVE=True,
                 paramRangeDict=None,
                 POPULATION=500
                 ):
        self.rr = rr
        self.paramRange = []
        self.generations = []
        self.fitnessFcn = fitnessFcn
        self.simFcn = simFcn
        self.ASYNC = ASYNC
        self.BEST_FITNESS = float('inf')
        self.MIXING_RATE = MIXING_RATE
        self.CROSSOVER_RATE = CROSSOVER_RATE
        self.NON_NEGATIVE = NON_NEGATIVE
        self.POPULATION = POPULATION
        self.MAX_GENS = MAX_GENS
        self.FITNESS_THRESHOLD = FITNESS_THRESHOLD

        defaultMin = 0
        defaultMax = 10
        if paramRangeDict is None:
            mins = [defaultMin] * len(self.rr.model.getGlobalParameterIds())
            maxes = [defaultMax] * len(self.rr.model.getGlobalParameterIds())
            for mn, mx in zip(mins, maxes):
                self.paramRange.append((mn, mx))
        else:
            paramIds = self.rr.model.getGlobalParameterIds()
            for paramId in paramIds:
                if paramId in paramRangeDict:
                    self.paramRange.append(paramRangeDict[paramId])
                else:
                    self.paramRange.append((defaultMin, defaultMax))

        firstGen = {
            'members': [],
            'fitness': []
        }
        asyncSims = []
        for i in range(POPULATION):
            newMember = self.createRandomMember()
            firstGen['members'].append(newMember)

            if self.ASYNC:
                sim = self.simFcn(self.rr, newMember.params)
                asyncSims.append(sim)
            else:
                try:
                    newFitness = self.fitnessFcn(
                        self.simFcn(self.rr, newMember.params))
                except RuntimeError:
                    newFitness = float('inf')
                firstGen['fitness'].append(newFitness)
        if self.ASYNC:
            for output in asyncSims:
                try:
                    firstGen['fitness'].append(
                        self.fitnessFcn(output.get()[-1]))
                except RuntimeError:
                    firstGen['fitness'].append(float('inf'))

        self.generations.append(firstGen)
        self.BEST_FITNESS = max(firstGen['fitness'])

    def start(self):
        import time
        start = time.time()
        while (len(self.generations) < self.MAX_GENS and
               self.BEST_FITNESS > self.FITNESS_THRESHOLD):
            gen = self.newGeneration()
            self.generations.append(gen)

        print 'Finished after %s seconds' % str(time.time()-start)
        print ('with population of %s and %s generations'
               % (self.POPULATION, len(self.generations)))
        print 'Best fitness value of %s' % self.BEST_FITNESS
        print 'Best parameters of %s' % self.getBestMember().params

    def newGeneration(self):
        import numpy as np
        gen = {}
        numParams = len(self.paramRange)

        newMembers = []
        newFitnesses = []

        asyncSims = []
        asyncTrialMembers = []
        for i, member in enumerate(self.generations[-1]['members']):
            # Pick two other members
            a = self.generations[-1]['members'][
                np.random.randint(0, self.POPULATION)]
            b = self.generations[-1]['members'][
                np.random.randint(0, self.POPULATION)]
            # Create mutant
            mutant = self.mutate(member, a, b)
            # Crossover to create trial member
            trialP = []
            pInd = np.random.randint(
                0, numParams)  # random index of parameter to cross over
            for j, (
                    mutantP, originalP
                    ) in enumerate(zip(mutant.params, member.params)):
                r = np.random.uniform(0, 1)
                if r < self.CROSSOVER_RATE or j == pInd:
                    trialP.append(mutantP)
                else:
                    trialP.append(originalP)
            trialMember = Member(trialP)

            if self.ASYNC:
                # In the async case, create list of trial members and
                # async sim jobs to feed into fitness function
                sim = self.simFcn(self.rr, trialMember.params)
                asyncTrialMembers.append(trialMember)
                asyncSims.append(sim)
            else:
                # Fitness function should know how to handle trialmember
                # and run simulation
                try:
                    trialFitness = self.fitnessFcn(
                        self.simFcn(self.rr, trialMember.params))
                except RuntimeError:
                    trialFitness = float('inf')
                memberFitness = self.generations[-1]['fitness'][i]
                # Replace member with trial member if better fitness
                if (trialFitness < memberFitness):
                    newMembers.append(trialMember)
                    newFitnesses.append(trialFitness)
                    self.updateBestFitness(trialFitness)
                else:
                    newMembers.append(member)
                    newFitnesses.append(memberFitness)
                    self.updateBestFitness(memberFitness)
        if self.ASYNC:
            # Async operation so still need to make members
            for i, (
                    sim, trialMember
                    ) in enumerate(zip(asyncSims, asyncTrialMembers)):
                try:
                    trialFitness = self.fitnessFcn(sim.get()[-1])
                except RuntimeError:
                    trialFitness = float('inf')
                member = self.generations[-1]['members'][i]
                memberFitness = self.generations[-1]['fitness'][i]
                if (trialFitness < memberFitness):
                    newMembers.append(trialMember)
                    newFitnesses.append(trialFitness)
                    self.updateBestFitness(trialFitness)
                else:
                    newMembers.append(member)
                    newFitnesses.append(memberFitness)
                    self.updateBestFitness(memberFitness)

        gen['members'] = newMembers
        gen['fitness'] = newFitnesses

        return gen

    def updateBestFitness(self, newFitness):
        if (newFitness < self.BEST_FITNESS):
            self.BEST_FITNESS = newFitness
            return True
        return False

    def mutate(self, x, a, b):
        import numpy as np
        differential = [self.MIXING_RATE*(ai-bi)
                        for ai, bi
                        in
                        zip(a.params, b.params)
                        ]
        mutantParams = [xi + diffi
                        for xi, diffi
                        in
                        zip(x.params, differential)]
        if (self.NON_NEGATIVE):
            npParams = np.asarray(mutantParams)
            negativeIndicies = npParams < 0
            npParams[negativeIndicies] = 0
            mutantParams = npParams.tolist()
        return Member(mutantParams)

    def createRandomMember(self):
        import numpy as np
        newParams = [np.random.uniform(self.paramRange[i][0],
                                       self.paramRange[i][1])
                     for i, p
                     in
                     enumerate(self.rr.model.getGlobalParameterValues())]
        newMember = Member(newParams)
        return newMember

    def plotFitnesses(self):
        import matplotlib.pyplot as plt
        fitnesses = [min(g['fitness']) for g in self.generations]
        plt.plot(fitnesses)
        return plt.show()

    def plotBest(self, observed=None):
        import matplotlib.pyplot as plt
        ind = self.generations[-1]['fitness'].index(self.BEST_FITNESS)
        params = self.generations[-1]['members'][ind].params
        if self.ASYNC:
            sim = self.simFcn(self.rr, params).get()[-1]
        else:
            sim = self.simFcn(self.rr, params)
        plts = plt.plot(sim[:, 0], sim[:, 1:], linewidth=2.5)
        if observed is not None:
            for i, column in enumerate(observed[:, 1:].T):
                plt.scatter(
                    observed[:, 0],
                    column,
                    linewidth=2.5,
                    color=plts[i].get_color())
        return plt.show()

    def getBestMember(self):
        ind = self.generations[-1]['fitness'].index(self.BEST_FITNESS)
        bestMember = self.generations[-1]['members'][ind]
        return bestMember


class Member():
    def __init__(self, params):
        self.params = params
