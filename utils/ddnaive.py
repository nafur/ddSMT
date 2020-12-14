import collections
from multiprocessing import Pool
import sys
import time

from utils import checker
from utils import iter as iters
from utils import options
from utils import parser
from utils import subst
from utils import smtlib
from utils import tmpfiles
from utils import mutators

Mutation = collections.namedtuple('Mutation', ['nodeid', 'name', 'exprs'])

def ddnaive_passes():
    return mutators.collect_mutators(options.args())


class MutationGenerator:
    def __init__(self, skip, mutators):
        self.__node_count = 0
        self.__node_skip = skip
        self.__mutators = mutators

    def __mutate_node(self, linput, ginput):
        """Apply all active mutators to the given node.
        Returns a list of all possible mutations as tuples :code:`(name, local, global)`
        where :code:`local` is a modification of the current node and :code:`global` is
        a modification of the whole input and one of those is always :code:`None`."""
        for m in self.__mutators:
            try:
                if hasattr(m, 'filter') and not m.filter(linput):
                    continue
                if hasattr(m, 'mutations'):
                    yield from list(map(lambda x: Mutation(self.__node_count, str(m), subst.subs_local(ginput, linput, x)), m.mutations(linput)))
                if hasattr(m, 'global_mutations'):
                    yield from list(map(lambda x: Mutation(self.__node_count, "(global) " + str(m), subst.subs_global(ginput, linput, x)), m.global_mutations(linput, ginput)))
            except Exception as e:
                print("Exception: {}".format(e))
                pass


    def generate_mutations(self, original):
        """A generator that produces all possible mutations from the given original."""
        for node in iters.dfs(original):
            for subst in self.__mutate_node(node, original):
                yield original, subst

def _check(task):
    success, runtime = checker.check_exprs(task[1].exprs)
    if success:
        nreduced = iters.count_exprs(task[0]) - iters.count_exprs(task[1].exprs)
        return nreduced, task[1].exprs, runtime
    return 0, [], 0

def reduce(exprs):

    passes = ddnaive_passes()
    smtlib.collect_information(exprs)

    mg = MutationGenerator(0, passes)

    nreduced = 0
    ntests = 0 
    with Pool(options.args().nprocs) as pool:

        reduction = True
        while reduction:
            reduction = False
            for result in pool.imap(_check, mg.generate_mutations(exprs)):
                ntests += 1
                nred, exp, runtime = result
                if nred > 0:
                    nreduced += nred
                    exprs = exp
                    parser.print_exprs(options.args().outfile, exprs)
                    reduction = True
                    break

    return exprs, nreduced, ntests
