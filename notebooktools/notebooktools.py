
# coding: utf-8

# In[2]:

import io
import os
import sys
import types
import matplotlib.pyplot as p
from IPython.nbformat import current
from IPython.core.interactiveshell import InteractiveShell


def find_notebook(fullname, path=None):
    """find a notebook, given its fully qualified name and an optional path

    This turns "foo.bar" into "foo/bar.ipynb"
    and tries turning "Foo_Bar" into "Foo Bar" if Foo_Bar
    does not exist.
    """
    name = fullname.rsplit('.', 1)[-1]
    if not path:
        path = ['']
    for d in path:
        nb_path = os.path.join(d, name + ".ipynb")
        if os.path.isfile(nb_path):
            return nb_path
        # let import Notebook_Name find "Notebook Name.ipynb"
        nb_path = nb_path.replace("_", " ")
        if os.path.isfile(nb_path):
            return nb_path


class NotebookLoader(object):
    """Module Loader for IPython Notebooks"""
    def __init__(self, path=None):
        self.shell = InteractiveShell.instance()
        self.path = path

    def load_module(self, fullname):
        """import a notebook as a module"""
        path = find_notebook(fullname, self.path)

        print ("importing IPython notebook from %s" % path)

        # load the notebook object
        with io.open(path, 'r', encoding='utf-8') as f:
            nb = current.read(f, 'json')

        # create the module and add it to sys.modules
        # if name in sys.modules:
        #    return sys.modules[name]
        mod = types.ModuleType(fullname)
        mod.__file__ = path
        mod.__loader__ = self
        sys.modules[fullname] = mod

        # extra work to ensure that magics that would affect the user_ns
        # actually affect the notebook module's ns
        save_user_ns = self.shell.user_ns
        self.shell.user_ns = mod.__dict__

        try:
            for cell in nb.worksheets[0].cells:
                if cell.cell_type == 'code' and cell.language == 'python':
                    # transform the input to executable Python
                    code = self.shell.input_transformer_manager.transform_cell(
                        cell.input
                    )
                    # run the code in themodule
                    exec(code, mod.__dict__)
        finally:
            self.shell.user_ns = save_user_ns
        return mod


class NotebookFinder(object):
    """Module finder that locates IPython Notebooks"""
    def __init__(self):
        self.loaders = {}

    def find_module(self, fullname, path=None):
        nb_path = find_notebook(fullname, path)
        if not nb_path:
            return

        key = path
        if path:
            # lists aren't hashable
            key = os.path.sep.join(path)

        if key not in self.loaders:
            self.loaders[key] = NotebookLoader(path)
        return self.loaders[key]


def loadNotebooksAsModules():
    sys.meta_path.append(NotebookFinder())


def sideBySideOutput():
	print '''
For side-by-side output, add this to a new cell:

%%html
<style>
div.cell {box-orient:horizontal;flex-direction:row;}
div.cell *{width:100%;}div.prompt{width:80px;}</style>
'''


def plot2DParameterScan(
    r, param1, param1Range, param2, param2Range, start=0, end=100, steps=100
):
    f, axarr = p.subplots(
        len(param1Range),
        len(param2Range),
        sharex='col',
        sharey='row')

    for i, k1 in enumerate(param1Range):
        for j, k2 in enumerate(param2Range):
            r.reset()
            r[param1], r[param2] = k1, k2
            result = r.simulate(start, end, steps)
            columns = result.shape[1]
            legendItems = r.selections[1:]
            if columns-1 != len(legendItems):
                raise Exception('Legend list must match result array')
            for c in range(columns-1):
                axarr[i, j].plot(
                    result[:, 0],
                    result[:, c+1],
                    linewidth=2,
                    label=legendItems[c])

            if (i == len(param1Range) - 1):
                axarr[i, j].set_xlabel('%s = %.2f' % (param2, k2))
            if (j is 0):
                axarr[i, j].set_ylabel('%s = %.2f' % (param1, k1))


def makeParameterSliders(r,
                         paramIds=None,
                         minFactor=0,
                         maxFactor=2,
                         sliderStepFactor=10):
    """
    Create interactive sliders to change model parameters.

    r - roadrunner instance with model loaded
    paramIds (optional) - list of parameter ids to create sliders,
                          by default creates slider for every parameter
    minFactor (optional) - scale factor multiplied with parameter value,
                           to determine minimum value of slider
    maxFactor (optional) - scale factor multiplied with parameter value,
                           to determine maximum value of slider
    sliderStepFactor (optional) - scale factor divided with parameter value,
                                  to determine step size of slider

    Example Usage:

    import tellurium as te
    import notebooktools as nb
    model = '''
      model pathway()
        S1 -> S2; k1*S1 - k2*S2 # Reversible term added here

        # Initialize values
        S1 = 5; S2 = 0;
        k1 = 0.1;  k2 = 0.05;

      end
    '''
    r = te.loadAntimonyModel(model)
    nb.makeParameterSliders(r, paramIds=['k1'])
    """
    from IPython.html.widgets import interact
    from IPython.html import widgets
    import tellurium as te
    import sys

    if paramIds is None:
        paramIds = r.model.getGlobalParameterIds()
    paramMap = {}

    def runSim(start=0, stop=100, steps=100, **paramMap):
        r.reset()
        for k, v in paramMap.items():
            try:
                key = k.encode('ascii', 'ignore')
                r[key] = v
            except:
                # error in setting model variable
                e = sys.exc_info()
                print e

        try:
            s = r.simulate(start, stop, steps)
            te.plotArray(s)
        except:
            # error in simulation
            e = sys.exc_info()
            print e

    for i, id in enumerate(paramIds):
        val = r[id]
        try:
            r[id] = val
            paramMap[id] = widgets.FloatSliderWidget(
                min=minFactor*val,
                max=maxFactor*val,
                step=val/sliderStepFactor,
                value=val)
        except:
            e = sys.exc_info()
            print e

    interact(runSim,
             start=widgets.FloatTextWidget(min=0, value=0),
             stop=widgets.FloatTextWidget(min=0, value=100),
             steps=widgets.IntTextWidget(min=0, value=100),
             **paramMap
             )
