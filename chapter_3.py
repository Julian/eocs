from simplehdl import Bus, Fork
from simplehdl.hdl import load_builtin
from simplehdl.util import chip

mux = load_builtin("Mux")
dff = load_builtin("DFF")

bit = chip("Bit",
           {"in", "load"}, {"out"},

           dff.inline(out="to_mux", **{"in" : "to_dff"}),
           mux.inline(a="to_mux", b="in", sel="load",
                      out=Fork("out", "to_dff")))

"""
i, o = Bus("in", 16), Bus("out", 16)
register = chip("Register",

                {i, "load"}, {"out"},

                *[bit.inline(load="load", out=o[j], **{"in" : i[j]})
                        for j in range(16)])
"""
