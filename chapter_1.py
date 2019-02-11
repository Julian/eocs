from simplehdl import Bus, HardwareModule, Pin
from simplehdl.hdl import load_builtin
from simplehdl.util import chip

__all__ = ["nand", "not_", "and_", "or_", "xor", "mux", "demux",
           "not_16", "and_16", "or_16", "mux_16", "or_8_way", "mux_4_way_16",
           "mux_8_way_16", "demux_4_way", "demux_8_way"]

a, b, s, i, o = (Pin(i) for i in ["a", "b", "sel", "in", "out"])

nand = load_builtin("Nand")

not_ = chip("Not",
            {i}, {o},

            nand.inline(a=i, b=i, out=o))

and_ = chip("And",
            {a, b}, {o},

            nand.inline(a=a, b=b, out=Pin("to_not")),
            not_.inline(**{"in" : Pin("to_not"), "out" : o}))

or_ = chip("Or",
           {a, b}, {o},

           not_.inline(**{"in" : a, "out" : Pin("to_nand_a")}),
           not_.inline(**{"in" : b, "out" : Pin("to_nand_b")}),
           nand.inline(a=Pin("to_nand_a"), b=Pin("to_nand_b"), out=o))

xor = chip("Xor",
           {a, b}, {o},

           nand.inline(a=a, b=b, out=Pin("to_and_b")),
           or_.inline(a=a, b=b, out=Pin("to_and_a")),
           and_.inline(a=Pin("to_and_a"), b=Pin("to_and_b"), out=o))

mux = chip("Mux",
           {a, b, s}, {o},

           and_.inline(a=s, b=b, out=Pin("to_or_a")),
           not_.inline(**{"in" : s, "out" : Pin("to_and_a")}),
           and_.inline(a=Pin("to_and_a"), b=a, out=Pin("to_or_b")),
           or_.inline(a=Pin("to_or_a"), b=Pin("to_or_b"), out=o))

demux = chip("Demux",
             {i, s}, {a, b},

             not_.inline(**{"in" : s, "out" : Pin("to_and_a")}),
             and_.inline(a=Pin("to_and_a"), b=i, out=a),
             and_.inline(a=s, b=i, out=b))


(a, b, c, d, e, f, g, h), s = (Bus(i, 16) for i in "abcdefgh"), Bus("sel", 2)
i, o = Bus("in", 16), Bus("out", 16)


not_16 = chip("Not16",
              {i}, {o},
              *[not_.inline(**{"in" : i[j], "out" : o[j]}) for j in range(16)])

and_16 = chip("And16",
              {a, b}, {o},
              *[and_.inline(a=a[j], b=b[j], out=o[j]) for j in range(16)])

or_16 = chip("Or16",
              {a, b}, {o},
              *[or_.inline(a=a[j], b=b[j], out=o[j]) for j in range(16)])

mux_16 = chip("Mux16",
              {a, b, Pin("sel")}, {o},
              *[mux.inline(a=a[j], b=b[j], sel=Pin("sel"), out=o[j])
                for j in range(16)])

i = Bus("in", 8)
or_8_way = chip("Or8Way",
                {i}, {Pin("out")},

                or_.inline(a=i[0], b=i[1], out=Pin("to_or_1")),
                or_.inline(a=i[7], b=Pin("to_or_6"), out=Pin("out")),
                *[or_.inline(a=i[j], b=Pin("to_or_{}".format(j - 1)),
                             out=Pin("to_or_{}".format(j))) for j in range(2, 7)])

s = Bus("sel", 2)
mux_4_way_16 = chip("Mux4Way16",
                    {a, b, c, d, s}, {o},

                    mux_16.inline(a=a, b=b, sel=s[0], out=Pin("to_mux_a")),
                    mux_16.inline(a=c, b=d, sel=s[0], out=Pin("to_mux_b")),
                    mux_16.inline(a=Pin("to_mux_a"), b=Pin("to_mux_b"), sel=s[1], out=o))

s = Bus("sel", 3)
mux_8_way_16 = chip("Mux8Way16",
                    {a, b, c, d, e, f, g, h, s}, {o},

                    mux_4_way_16.inline(a=a, b=b, c=c, d=d, sel=s[:2],
                                        out=Pin("to_mux_a")),
                    mux_4_way_16.inline(a=e, b=f, c=g, d=h, sel=s[:2],
                                        out=Pin("to_mux_b")),
                    mux_16.inline(a=Pin("to_mux_a"), b=Pin("to_mux_b"), sel=s[2], out=o))

s = Bus("sel", 2)
demux_4_way = chip("DMux4Way",
                   {Pin("in"), s}, {a, b, c, d},

                   demux.inline(a=Pin("to_d1"), b=Pin("to_d2"), sel=s[1],
                                **{"in" : Pin("in")}),
                   demux.inline(a=a, b=b, sel=s[0], **{"in" : Pin("to_d1")}),
                   demux.inline(a=c, b=d, sel=s[0], **{"in" : Pin("to_d2")}))

s = Bus("sel", 3)
demux_8_way = chip("DMux8Way",
                   {Pin("in"), s}, {a, b, c, d, e, f, g, h},

                   demux.inline(a=Pin("to_d1"), b=Pin("to_d2"), sel=s[2],
                                **{"in" : Pin("in")}),
                   demux_4_way.inline(a=a, b=b, c=c, d=d, sel=s[:2],
                                      **{"in" : Pin("to_d1")}),
                   demux_4_way.inline(a=e, b=f, c=g, d=h, sel=s[:2],
                                      **{"in" : Pin("to_d2")}))

del a, b, c, d, e, f, g, h, i, o, s
