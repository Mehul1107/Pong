from imp import find_module, load_module
import os


module = load_module("module", *find_module("button"))
module_vars = vars(module)
print "# `%s`" % os.path.relpath(module.__file__)

not_dunderscored = lambda name: !name.startswith("__")

for var in filter(not_dunderscored, dir(module)):
    print "## ```python\n%s\n```" % var
    for var in filter(not_dunderscored, dir())

