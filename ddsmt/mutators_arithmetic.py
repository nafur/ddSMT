from .smtlib import *

NAME = 'arithmetic'
MUTATORS = [
    'arith-constants', 'arith-negate-relations', 'split-nary-relations',
    'strengthen-relations'
]


def is_arithmetic_relation(node):
    if not has_name(node):
        return False
    return get_name(node) in ['=', '<', '>', '>=', '<=', '!=', '<>']


class ArithmeticSimplifyConstant:
    """Replace a constant by a simpler version (smaller or fewer decimal places)."""
    def filter(self, node):
        return is_arithmetic_constant(node) and float(node.data) not in [0, 1]

    def mutations(self, node):
        f = float(node.data)
        if int(f) == f:
            i = int(f)
            return [Node(str(i // 2)), Node(str(i // 10))]
        return [Node(str(int(f))), Node(node.data[:-1])]

    def global_mutations(self, linput, ginput):
        return [
            nodes.substitute(ginput, {linput: rep})
            for rep in self.mutations(linput)
        ]

    def __str__(self):
        return 'simplify arithmetic constant'


class ArithmeticNegateRelations:
    """Replace a negation around a relation by the inverse relation."""
    def filter(self, node):
        return is_operator(node, 'not') and is_arithmetic_relation(node[1])

    def mutations(self, node):
        negator = {'<': '>=', '<=': '>', '!=': '=', '<>': '=', '>=': '<', '>': '<='}
        if node[1][0] in negator:
            return [(negator[node[1][0]], ) + node[1][1:]]
        return []

    def __str__(self):
        return 'push negation into relation'


class ArithmeticSplitNaryRelations:
    """Split n-ary relations using transitivity."""
    def filter(self, node):
        return is_arithmetic_relation(node) and len(node) > 3

    def mutations(self, node):
        split = [(get_name(node), node[i], node[i + 1]) for i in range(1, len(node) - 1)]
        return [Node('and', *split)]

    def __str__(self):
        return 'split n-ary relation'


class ArithmeticStrengthenRelations:
    """Replace a relation by a stronger relation."""
    def filter(self, node):
        return is_arithmetic_relation(node)

    def mutations(self, node):
        negator = {'<': ['='], '>': ['='], '<=': ['<', '='], '>=': ['>', '=']}
        if node[0] in negator:
            return [Node(rel, *node.data[1:]) for rel in negator[node[0]]]
        return []

    def __str__(self):
        return 'strengthen relation'


def get_mutators():
    """Returns a mapping from mutator class names to the name of their config options."""
    return {
        'ArithmeticSimplifyConstant': 'arith-constants',
        'ArithmeticNegateRelations': 'arith-negate-relations',
        'ArithmeticSplitNaryRelations': 'arith-split-nary-relations',
        'ArithmeticStrengthenRelations': 'arith-strengthen-relations',
    }
