from breadbrawl import BreadBrawl, Loaf

my_loaf = Loaf.random_loaf()

def loaf():
    return my_loaf

def agent(obs):
    return my_loaf.random_attack()