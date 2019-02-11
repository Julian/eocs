from simplehdl import Bus, Fork
from simplehdl.hdl import load_builtin
from simplehdl.util import chip

__all__ = ["half_adder", "full_adder", "add_16", "inc_16", "alu"]

not_ = load_builtin("Not")
and_ = load_builtin("And")
or_ = load_builtin("Or")
xor = load_builtin("Xor")
not_16 = load_builtin("Not16")
and_16 = load_builtin("And16")
mux_16 = load_builtin("Mux16")
or_8_way = load_builtin("Or8Way")

half_adder = chip("HalfAdder",
                  {"a", "b"}, {"sum", "carry"},

                  xor.inline(a="a", b="b", out="sum"),
                  and_.inline(a="a", b="b", out="carry"))

full_adder = chip("FullAdder",
                  {"a", "b", "c"}, {"sum", "carry"},

                  half_adder.inline(a="a", b="b", sum="to_ha", carry="to_a"),
                  half_adder.inline(a="c", b="to_ha", sum="sum", carry="to_b"),
                  or_.inline(a="to_a", b="to_b", out="carry"))

a, b, o = Bus("a", 16), Bus("b", 16), Bus("out", 16)
add_16 = chip("Add16",
              {a, b}, {o},

              half_adder.inline(a=a[0], b=b[0], sum=o[0], carry="c1"),
              *[full_adder.inline(a=a[i], b=b[i], c="c{}".format(i),
                                  sum=o[i], carry="c{}".format(i + 1))
                for i in range(1, 16)])

i, o = Bus("in", 16), Bus("out", 16)
inc_16 = chip("Inc16",
              {i}, {o},

              not_.inline(out=o[0], **{"in" : i[0]}),
              half_adder.inline(a=i[0], b=i[1], sum=o[1], carry="c1"),
              *[half_adder.inline(a=i[j], b="c{}".format(j - 1),
                                  sum=o[j], carry="c{}".format(j))
                for j in range(2, 16)])

x, y, o = Bus("x", 16), Bus("y", 16), Bus("out", 16)
alu = chip("ALU",
           {x, y, "zx", "nx", "zy", "ny", "f", "no"}, {o, "zr", "ng"},

           mux_16.inline(a=x, b=0, sel="zx", out=Fork("to_nx", "to_mux_nx_a")),
           mux_16.inline(a=y, b=0, sel="zy", out=Fork("to_ny", "to_mux_ny_a")),

           not_16.inline(out="to_mux_nx_b", **{"in" : "to_nx"}),
           not_16.inline(out="to_mux_ny_b", **{"in" : "to_ny"}),

           mux_16.inline(a="to_mux_nx_a", b="to_mux_nx_b", sel="nx",
                         out=Fork("to_and_a", "to_add_a")),
           mux_16.inline(a="to_mux_ny_a", b="to_mux_ny_b", sel="ny",
                         out=Fork("to_and_b", "to_add_b")),

           and_16.inline(a="to_and_a", b="to_and_b", out="to_f_a"),
           add_16.inline(a="to_add_a", b="to_add_b", out="to_f_b"),
           mux_16.inline(a="to_f_a", b="to_f_b", sel="f",
                         out=Fork("to_no", "to_mux_no_a")),

           not_16.inline(out="to_mux_no_b", **{"in" : "to_no"}),
           mux_16.inline(a="to_mux_no_a", b="to_mux_no_b", sel="no", out=o,
                         with_slices=[("out", slice(8), "to_or_8_1"),
                                      ("out", slice(8, None), "to_or_8_2"),
                                      ("out", slice(15, None), "ng")]),

           or_8_way.inline(out="to_or_a", **{"in" : "to_or_8_1"}),
           or_8_way.inline(out="to_or_b", **{"in" : "to_or_8_2"}),
           or_.inline(a="to_or_a", b="to_or_b", out="to_zr"),
           not_.inline(out="zr", **{"in" : "to_zr"}))
