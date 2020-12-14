from utils import mutators_arithmetic
from utils import mutators_bitvectors
from utils import mutators_boolean
from utils import mutators_core
from utils import mutators_smtlib
from utils import mutators_strings


def add_mutator_group(argparser, name):
    """Add a new argument group for a mutator group"""
    return argparser.add_argument_group('{} mutator arguments'.format(name))
    #return argparser.add_argument_group('{} mutator arguments'.format(name), help_name = name, help_group = 'mutator help', help_text = 'show help for {} mutators')

def collect_mutator_options(argparser):
    """Adds all options related to mutators to the given argument parser."""
    mutators_core.collect_mutator_options(add_mutator_group(argparser, 'core'))
    mutators_boolean.collect_mutator_options(add_mutator_group(argparser, 'boolean'))
    mutators_arithmetic.collect_mutator_options(add_mutator_group(argparser, 'arithmetic'))
    mutators_bitvectors.collect_mutator_options(add_mutator_group(argparser, 'bitvector'))
    mutators_smtlib.collect_mutator_options(add_mutator_group(argparser, 'smtlib'))
    mutators_strings.collect_mutator_options(add_mutator_group(argparser, 'string'))

def collect_mutators(args):
    """Initializes the list of all active mutators."""
    res = []
    res += mutators_core.collect_mutators(args)
    #res += mutators_boolean.collect_mutators(args)
    #res += mutators_arithmetic.collect_mutators(args)
    #res += mutators_bitvectors.collect_mutators(args)
    #res += mutators_smtlib.collect_mutators(args)
    #res += mutators_strings.collect_mutators(args)
    return res
