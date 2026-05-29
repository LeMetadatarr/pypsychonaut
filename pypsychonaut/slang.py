"""Street/slang name → canonical substance lexicon for PsychonautWiki.

``DRUG_SLANG`` maps a colloquial name (lower-case key) to the canonical
substance name PsychonautWiki indexes it under. It powers
:func:`pypsychonaut.extract_substance_name`, which normalises free text into a
queryable substance before hitting the GraphQL API.

This is a hand-curated mapping; the values are the spellings PsychonautWiki
prefers (e.g. ``"acid"`` → ``"lsd"``). Keys are matched case-insensitively
against whitespace-split tokens.
"""
from __future__ import annotations

from typing import Dict

DRUG_SLANG: Dict[str, str] = {
    'marijuana': "thc", 'hashish': "thc", 'hash': "thc", 'weed': "thc",
    'marijjuana': "thc", 'cannabis': "thc", 'benzo fury': '6-apb', 'l': 'lsd',
    'x': 'mdma', 'speed': 'amphetamine', 'pepper oil': 'capsaicin', 'cpp': 'piperazines',
    'blow': 'cocaine', 'foxy': '5-meo-dipt', 'symmetry': 'salvinorin b ethoxymethyl ether',
    'nexus': '2c-b', 'tea': 'caffeine', 'robo': 'dxm', ' tussin': 'dxm',
    'methylethyltryptamine': 'met', 'it-290': 'amt', 'jwh-018': 'cannabinoids',
    'coffee': 'caffeine', 'mpa': 'methiopropamine', 'ergine': 'lsa',
    'harmine': 'harmala', 'mxe': 'methoxetamine',
    '4-ho-met; metocin; methylcybin': '4-hydroxy-met', 'mdea': 'mde',
    'elavil': 'amitriptyline', 'bk-mdma': 'methylone', 'eve': 'mde',
    'a2': 'piperazines', 'dimitri': 'dmt', 'plant food': 'mdpv', 'dr. bob': 'dob', 'doctor bob': 'dob',
    'mini thins': 'ephedrine', 'meth': 'methamphetamines', 'acid': 'lsd',
    'etc.': 'nbome', ' wine': 'alcohol', 'toad venom': 'bufotenin', ' methyl-j': 'mbdb',
    'krokodil': 'desomorphine', ' 5-hydroxy-dmt': 'bufotenin', ' 3-cpp': 'mcpp',
    'special k': 'ketamine', 'ice': 'methamphetamines',
    'nrg-1': 'mdpv', ' gravel': 'alpha-pvp', 'whippits': 'nitrous', 'g': 'ghb',
    'k': 'ketamine', ' harmaline': 'harmala', 'bob': 'dob', '4-ace': '4-acetoxy-dipt',
    'quaaludes': 'methaqualone', ' opium': 'opiates', 'u4ea': '4-methylaminorex',
    'meopp': 'piperazines', 'methcathinone': 'cathinone', 'horse': 'heroin',
    'haoma': 'harmala', 'unknown': '"spice" product', '4-b': '1,4-butanediol',
    'naptha': 'petroleum ether', 'beer': 'alcohol', 'bees': '2c-b',
    '2c-bromo-fly': '2c-b-fly', 'flatliner': '4-mta', 'orexins': 'hypocretin',
    "meduna's mixture": 'carbogen', 'bdo': '1,4-butanediol',
    'fatal meperedine-analog contaminant': 'mptp', 'piperazine': 'bzp', '4-ma': 'pma',
    'paramethoxyamphetamine': 'pma', 'eden': 'mbdb', 'theobromine': 'chocolate',
    'la-111': 'lsa', 'lysergamide': 'lsa', 'yaba': 'methamphetamines',
    'ethyl cat': 'ethylcathinone', 'stp': 'dom', '2c-c-nbome': 'nbome',
    'morphine': 'opiates', 'flakka': 'alpha-pvp', 'yage': 'ayahuasca',
    'ecstasy': 'mdma', 'ludes': 'methaqualone', 'golden eagle': '4-mta',
    '4-mma': 'pmma', 'o-dms': '5-meo-amt', 'liquor': 'alcohol',
    'mephedrone': '4-methylmethcathinone', '1': '1,4-butanediol', 'phencyclidine': 'pcp',
    'crystal': 'methamphetamines', 'pink adrenaline': 'adrenochrome',
    '4-mec': '4-methylethcathinone', 'green fairy': 'absinthe', 'laa': 'lsa',
    'cp 47': 'cannabinoids', 'paramethoxymethylamphetamine': 'pmma',
    '5-meo': '5-meo-dmt', 'alpha': '5-meo-amt', 'mescaline-nbome': 'nbome',
    '25c-nbome': '2c-c-nbome', 'flephedrone': '4-fluoromethcathinone',
    'bzp': 'piperazines', 'codeine': 'opiates', 'foxy methoxy': '5-meo-dipt',
    '25i-nbome': '2c-i-nbome', '3c-bromo-dragonfly': 'bromo-dragonfly', 'mdai': 'mdai',
    'tfmpp': 'piperazines',
}

__all__ = ["DRUG_SLANG"]
