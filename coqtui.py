import sys
from coqtui_vim import CoqTUIView
from coqtui_coqtop import CoqTUIModel

launched = False
def launch(*args):
    global launched
    if launched:
        pass
    launched = True
    view = CoqTUIView()
    model = CoqTUIModel(None, args)
