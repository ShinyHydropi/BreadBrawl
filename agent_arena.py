import re
import sys
import importlib
import copy

from breadbrawl import BreadBrawl, Loaf

if len(sys.argv) > 3 or len(sys.argv) < 2:
    raise ValueError("Too many arguments")

p1_module = importlib.import_module(re.split(r'[.\\]', sys.argv[1])[2])
model1 = p1_module.agent
loaf1 = copy.copy(p1_module.loaf())
if len(sys.argv) > 2:
    p2_module = importlib.import_module(re.split(r'[.\\]', sys.argv[2])[2])
    model2 = p2_module.agent
    loaf2 = copy.copy(p2_module.loaf())
else:
    loaf2 = Loaf.random_loaf()
    model2 = loaf2.random_attack