from .nodes import Node
from . import options
from .smtlib import *

NAME = 'core'
MUTATORS = [
    'constants', 'erase-children', 'merge-children', 'replace-by-variable',
    'sort-children', 'substitute-children', 'top-level-binary-reduction'
]


class Constants:
    """Replaces any node by a constant."""
    def filter(self, node):
        return get_type(node) is not None

    def mutations(self, node):
        """Return :code:`get_constants(get_type(node))`."""
        t = get_type(node)
        if t is None:
            return []
        res = get_constants(t)
        if node in res:
            return []
        return res

    def __str__(self):
        return 'substitute by a constant'


class EraseNode:
    """Erases the given node."""
    def mutations(self, node):
        return [None]

    def __str__(self):
        return 'erase node'


class MergeWithChildren:
    """Merges a node with one of its children. This is possible for n-ary operators like :code:`and` or :code:`+`."""
    def filter(self, node):
        return is_nary(node)

    def mutations(self, node):
        res = []
        for cid, child in enumerate(node):
            if has_name(child) and get_name(node) == get_name(child):
                res.append(Node(*node[:cid], *node[cid][1:], *node[cid + 1:]))
        return res

    def __str__(self):
        return 'merge with child'


class ReplaceByVariable:
    """Replaces a node by a variable."""
    def filter(self, node):
        return not is_constant(node)

    def mutations(self, node):
        ret_type = get_type(node)
        if ret_type is None:
            return []
        variables = get_variables_with_type(ret_type)
        if is_leaf(node):
            if options.args().replace_by_variable_mode == 'inc':
                return [Node(v) for v in variables if v > node.data]
            return [Node(v) for v in variables if v < node.data]
        return [Node(v) for v in variables if count_nodes(v) < count_nodes(node)]

    def __str__(self):
        return 'substitute by existing variable'


class SortChildren:
    """Sorts the children of a node."""
    def filter(self, node):
        return not is_leaf(node)

    def mutations(self, node):
        """Return :code:`sorted(node, key = count_nodes)`."""
        s = nodes.Node(*sorted(node, key=count_nodes))
        if s != node:
            return [s]
        return []

    def __str__(self):
        return 'sort children'


class SubstituteChildren:
    """Substitutes a node with one of its children."""
    def filter(self, node):
        return not is_leaf(node) and not is_operator(node, 'let')

    def mutations(self, node):
        return list(node[1:])

    def __str__(self):
        return 'substitute with child'


class TopLevelBinaryReduction:
    """Performs binary reduction on the top level node. Essentially mimics line based reduction."""
    def global_mutations(self, linput, ginput):
        if linput != ginput[0]:
            return []
        # generate all sublists as generated by binary-search in bfs order
        # let den be the denominator of the list length (the tree level)
        # let num be the numerator within the current tree level
        res = []
        den = 2
        while den < len(ginput):
            for num in range(0, den):
                start = int(num / den * len(ginput))
                end = int((num + 1) / den * len(ginput))
                res.append(ginput[:start] + ginput[end:])
            den *= 2
        return res

    def __str__(self):
        return 'binary reduction'


def collect_mutator_options(argparser):
    options.add_mutator_argument(argparser, NAME, True, 'core mutators')
    options.add_mutator_argument(argparser, 'constants', True,
                                 'replace by theory constants')
    options.add_mutator_argument(argparser, 'erase-node', True,
                                 'erase single node')
    options.add_mutator_argument(argparser, 'merge-children', True,
                                 'merge children into nodes')
    options.add_mutator_argument(argparser, 'replace-by-variable', True,
                                 'replace with existing variable')
    argparser.add_argument(
        '--replace-by-variable-mode',
        choices=['inc', 'dec'],
        default='inc',
        help='replace with existing variables that are larger or smaller')
    options.add_mutator_argument(argparser, 'sort-children', True,
                                 'sort children of nodes')
    options.add_mutator_argument(argparser, 'substitute-children', True,
                                 'substitute nodes with their children')
    options.add_mutator_argument(argparser, 'top-level-binary-reduction', True,
                                 'use top level binary reduction')


def get_mutators():
    """Returns a mapping from mutator class names to the name of their config options."""
    if not options.args().mutator_core:
        return {}
    return {
        'Constants': 'constants',
        'EraseNode': 'erase_node',
        'MergeChildren': 'merge_children',
        'ReplaceByVariable': 'replace_by_variable',
        'SortChildren': 'sort_children',
        'SubstituteChildren': 'substitute_children',
        'TopLevelBinaryReduction': 'top_level_binary_reduction',
    }
