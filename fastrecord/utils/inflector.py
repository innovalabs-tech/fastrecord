import re
from typing import Dict, List


class Inflector:
    """
    Rails-like string inflections for Python
    """

    def __init__(self):
        self.plurals: List[tuple] = []
        self.singulars: List[tuple] = []
        self.uncountables: set = set()
        self.acronyms: Dict[str, str] = {}

        self.load_defaults()

    def load_defaults(self):
        # Add default inflection rules
        self.plural(r'$', 's')
        self.plural(r's$', 's')
        self.plural(r'(ax|test)is$', r'\1es')
        self.plural(r'(octop|vir)us$', r'\1i')
        self.plural(r'(alias|status)$', r'\1es')
        self.plural(r'(bu)s$', r'\1ses')
        self.plural(r'(buffal|tomat)o$', r'\1oes')
        self.plural(r'([ti])um$', r'\1a')
        self.plural(r'sis$', 'ses')
        self.plural(r'(?:([^f])fe|([lr])f)$', r'\1\2ves')
        self.plural(r'(hive)$', r'\1s')
        self.plural(r'([^aeiouy]|qu)y$', r'\1ies')
        self.plural(r'(x|ch|ss|sh)$', r'\1es')
        self.plural(r'(matr|vert|ind)(?:ix|ex)$', r'\1ices')
        self.plural(r'^(m|l)ouse$', r'\1ice')
        self.plural(r'^(ox)$', r'\1en')
        self.plural(r'(quiz)$', r'\1zes')

        self.singular(r's$', '')
        self.singular(r'(n)ews$', r'\1ews')
        self.singular(r'([ti])a$', r'\1um')
        self.singular(r'((a)naly|(b)a|(d)iagno|(p)arenthe|(p)rogno|(s)ynop|(t)he)ses$', r'\1\2sis')
        self.singular(r'(^analy)ses$', r'\1sis')
        self.singular(r'([^f])ves$', r'\1fe')
        self.singular(r'(hive)s$', r'\1')
        self.singular(r'(tive)s$', r'\1')
        self.singular(r'([lr])ves$', r'\1f')
        self.singular(r'([^aeiouy]|qu)ies$', r'\1y')
        self.singular(r'(s)eries$', r'\1eries')
        self.singular(r'(m)ovies$', r'\1ovie')
        self.singular(r'(x|ch|ss|sh)es$', r'\1')
        self.singular(r'^(m|l)ice$', r'\1ouse')
        self.singular(r'(bus)es$', r'\1')
        self.singular(r'(o)es$', r'\1')
        self.singular(r'(shoe)s$', r'\1')
        self.singular(r'(cris|ax|test)es$', r'\1is')
        self.singular(r'([octop|vir])i$', r'\1us')
        self.singular(r'(alias|status)es$', r'\1')
        self.singular(r'^(ox)en', r'\1')
        self.singular(r'(vert|ind)ices$', r'\1ex')
        self.singular(r'(matr)ices$', r'\1ix')
        self.singular(r'(quiz)zes$', r'\1')
        self.singular(r'(database)s$', r'\1')

        # Add uncountable words
        self.uncountable([
            'equipment', 'information', 'rice', 'money', 'species',
            'series', 'fish', 'sheep', 'jeans', 'police'
        ])

    def plural(self, rule: str, replacement: str):
        """Add a new plural rule"""
        self.plurals.insert(0, (re.compile(rule, re.IGNORECASE), replacement))

    def singular(self, rule: str, replacement: str):
        """Add a new singular rule"""
        self.singulars.insert(0, (re.compile(rule, re.IGNORECASE), replacement))

    def uncountable(self, words: List[str]):
        """Add uncountable words"""
        self.uncountables.update(words)

    def pluralize(self, word: str) -> str:
        """Convert word to plural form"""
        if word.lower() in self.uncountables:
            return word

        for rule, replacement in self.plurals:
            if rule.search(word):
                return rule.sub(replacement, word)
        return word

    def singularize(self, word: str) -> str:
        """Convert word to singular form"""
        if word.lower() in self.uncountables:
            return word

        for rule, replacement in self.singulars:
            if rule.search(word):
                return rule.sub(replacement, word)
        return word

    def camelize(self, term: str) -> str:
        """Convert string to CamelCase"""
        return ''.join(x.capitalize() or '_' for x in term.split('_'))

    def underscore(self, term: str) -> str:
        """Convert CamelCase to snake_case"""
        return re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2',
                      re.sub(r'([a-z\d])([A-Z])', r'\1_\2', term)).lower()