import re

# TODO předělat - ideální do db?
ZKRATKY = {
    "gn": {
        "reg": re.compile("((^| )[gG][nN]( |!|$))"),
        "delay": 600,  # je to ve vteřinách
        "tmp": 0,
    },
    "gm": {"reg": re.compile("(D|d)obr(e|é|y|ý) r(a|á)n"), "delay": 600, "tmp": 0},
    "fuchs": {"reg": re.compile("(F|f)uchs"), "delay": 86400, "tmp": 0},  # den
    "purkyne": {"reg": re.compile("(P|p)urky"), "delay": 3600, "tmp": 0},  # hodina
    "eo": {"reg": re.compile("(^| )(E|e)+(O|o)+( |!|$)"), "delay": 3600, "tmp": 0},
    "hovno": {"reg": re.compile("(^| )(H|h)ovno( |!|$)"), "delay": 3600, "tmp": 0},
    "ruby": {"reg": re.compile("(^| )(R|r)+u+b+y+( |!|$)"), "delay": 3600, "tmp": 0},
    "party": {
        "reg": re.compile("((^| )(p|P)(a|á)rty|(K|k)alb(u|a))"),
        "delay": 86400,
        "tmp": 0,
    },
    # "Brno": {"reg" : re.compile("(^| )(b|B)rn(o|u|a)( |!|$)"),
    #        "delay" : 10,
    #        "tmp" : 0},
    "tramvaj": {
        "reg": re.compile("(t|T)ramvaj"),
        "delay": 86400 * 7,  # týden
        "tmp": 0,
    },
    # "kebab": {"reg" : re.compile("(k|K)eba(b|p)"),
    #        "delay" : 10,
    #        "tmp" : 0},
    "sushi": {"reg": re.compile("(s|S)ushi"), "delay": 86400, "tmp": 0},
    # "pozdě": {"reg" : re.compile("(^| )(P|p)ozdě( |!|$)"),
    #        "delay" : 10,
    #        "tmp" : 0},
    "vodka": {"reg": re.compile("vodk(a|u)"), "delay": 86400, "tmp": 0},
    # "adidas": {"reg" : re.compile("(a|A)didas"),
    #        "delay" : 10,
    #        "tmp" : 0},
    "kachna": {"reg": re.compile("(k|K)achn(y|a)"), "delay": 86400, "tmp": 0},
    # "idm": {"reg" : re.compile("(^| )[Ii][dD][Mm]( |!|$)"),
    #        "delay" : 10,
    #        "tmp" : 0},
    "flex": {"reg": re.compile("(^| )(f|F)lex( |!|$)"), "delay": 86400, "tmp": 0},
    # "projekt": {"reg" : re.compile("(p|P)projekt"),
    #        "delay" : 10,
    #        "tmp" : 0},
    # "gopnik": {"reg" : re.compile("((g|G)opnik)"),
    #        "delay" : 10,
    #        "tmp" : 0},
    # "asiat": {"reg" : re.compile("(A|a)siat"),
    #        "delay" : 10,
    #        "tmp" : 0},
    "černoch": {
        "reg": re.compile("((N|n)egr|(n|N)i(g|gg)er)"),
        "delay": 86400,
        "tmp": 0,
    },
    "ahoj": {
        "reg": re.compile(
            "((A|a)hoj|(N|n)azdar|(^| )(c|C|Č|č)au( |!|$)|(^| )(c|C|Č|č)us( |!|$))"
        ),
        "delay": 3600,
        "tmp": 0,
    },
    # "sex": {"reg" : re.compile("(^| )[sS][eE][xX]( |!|$)"),
    #        "delay" : 10,
    #        "tmp" : 0},
    "off": {"reg": re.compile("(^| )off( |!|$)"), "delay": 0, "tmp": 0},
    "stop": {"reg": re.compile("krutý světe"), "delay": 0, "tmp": 0},
    "badbot": {"reg": re.compile("Co zas děláš"), "delay": 300, "tmp": 0},
    "hihahuhahi": {"reg": re.compile("hihahuhahi"), "delay": 0, "tmp": 0},
    "stopemote": {"reg": re.compile("TimeToStop"), "delay": 1800, "tmp": 0},
    # "rusko": {"reg" : re.compile("(R|r)usk(o|a|á|é|e|y|ý)"),
    #        "delay" : 10,
    #        "tmp" : 0},
    "okBot": {"reg": re.compile("zkurvenej bot"), "delay": 0, "tmp": 0},
    "anti": {"reg": re.compile("zkurvenej bot"), "delay": 1, "tmp": 0},
}
