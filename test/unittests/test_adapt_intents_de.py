# write your first unittest!
import unittest
from os.path import join, dirname
import os
from ovos_utils.bracket_expansion import expand_options

from adapt.engine import IntentDeterminationEngine
from adapt.intent import IntentBuilder


def collect_intents(skill_file):
    intents = []
    in_intent = False
    intent_lines = ""
    intent_name = None

    with open(skill_file) as f:
        for l in f.read().split("\n"):
            if "IntentBuilder(" in l or "AdaptIntent(" in l:
                in_intent = True
                if "IntentBuilder(" in l:
                    intent_name = l.split("IntentBuilder(")[-1].split(")")[0]
                else:
                    intent_name = l.split("AdaptIntent(")[-1].split(")")[0]
                intent_lines = "".join(l.split(")")[1:]).strip()
                if len(intent_name):
                    intent_name = intent_name[1:-1]
                else:
                    intent_name = f"AnonIntent{len(intents)}"

            elif in_intent and " def " in l:
                intent = IntentBuilder(intent_name)

                requires = [r.split(")")[0][1:-1]
                            for r in intent_lines.split("require(")[1:]]
                for r in requires:
                    intent.require(r)

                optionals = [r.split(")")[0][1:-1]
                            for r in intent_lines.split("optionally(")[1:]]
                for opt in optionals:
                    intent.optionally(opt)

                one_of = [r.split(")")[0].split(", ")
                          for r in intent_lines.split("one_of(")[1:]]
                for one in one_of:
                    one = [r[1:-1] for r in one]
                    intent.one_of(*one)

                intents.append(intent.build())

                intent_name = None
                in_intent = False
                intent_lines = ""
            elif in_intent:
                intent_lines += l.strip()
    return intents


def read_samples(path):
    samples = []
    with open(path) as fi:
        for _ in fi.read().split("\n"):
            if _ and not _.strip().startswith("#"):
                samples += expand_options(_)
    return samples


def collect_test_utterances(intent, kws):
    test_utts = []
    for k, k2 in intent.at_least_one:
        test_utts += kws[k]
        test_utts += kws[k2]
    for k, _ in intent.requires:
        if test_utts:
            for utt in set(test_utts):
                test_utts += [f"{utt} {_}" for _ in kws[k]]
        else:
            test_utts += kws[k]
    for utt in set(test_utts):
        for k2, _ in intent.optional:
            for k3 in kws[k2]:
                test_utts.append(f"{utt} {k3}")
    return test_utts


class TestAdapt(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        lang = "de-de"
        engine = IntentDeterminationEngine()
        res_folder = join(dirname(dirname(dirname(__file__))), "locale", lang)
        skill = join(dirname(dirname(dirname(__file__))), "__init__.py")
        kws = {}
        for root, folders, files in os.walk(res_folder):
            for f in files:
                if f.endswith(".voc"):
                    samples = read_samples(join(root, f))
                    kw = f.replace(".voc", "")
                    kws[kw] = samples
                    for s in samples:
                        engine.register_entity(s, kw)

        intents = collect_intents(skill)
        test_utterances = {}
        for intent in intents:

            engine.register_intent_parser(intent)
            test_utterances[intent.name] = collect_test_utterances(intent, kws)

        self.res_folder = res_folder
        self.test_utterances = test_utterances
        self.intents = intents
        self.engine = engine

    def test_adapt(self):
        for intent_name, utterances in self.test_utterances.items():
            for utt in utterances:
                intent = list(self.engine.determine_intent(utt))
                if intent:
                    self.assertEqual(intent[0]['intent_type'], intent_name)
                else:
                    raise ValueError(f"No intent returned for {utt}, expected: {intent_name}")
