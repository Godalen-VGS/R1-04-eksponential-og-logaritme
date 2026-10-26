"""Automatisk retting av R1-04-eksponential-og-logaritme.

Hver sjekk i SJEKKER er én deltest, og poengene fordeles likt på dem.
De samme sjekkene ligger i "Test løsningen din"-cellen nederst i notebooken.
"""
import pytest

from notebook_loader import last_notebook

def naer(a, b, rel=1e-3):
    """Sant hvis tallet a er innenfor rel (relativt) av b."""
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if b == 0:
        return abs(a) < 1e-9
    return abs(a - b) <= rel * abs(b)


def S(tekst):
    """Gjør tekst om til et sympy-uttrykk, f.eks. S("x**2 - 1")."""
    import sympy
    return sympy.sympify(tekst, locals={n: sympy.Symbol(n) for n in ("N", "O", "Q", "S")})


def lik(a, b):
    """Sant hvis a og b er matematisk like.

    Lister og mengder sammenlignes uten hensyn til rekkefølge, tupler (koordinater) i rekkefølge.
    """
    import sympy
    if a is None:
        return False
    if isinstance(b, tuple):
        if not isinstance(a, (tuple, list, sympy.Tuple)) or len(a) != len(b):
            return False
        return all(lik(x, y) for x, y in zip(a, b))
    if isinstance(b, (list, set)):
        if isinstance(a, sympy.FiniteSet):
            a = list(a)
        if not isinstance(a, (list, tuple, set)) or len(a) != len(b):
            return False
        rest = list(a)
        for y in b:
            for i, x in enumerate(rest):
                if lik(x, y):
                    del rest[i]
                    break
            else:
                return False
        return True
    if isinstance(b, dict):
        if not isinstance(a, dict) or len(a) != len(b):
            return False
        a = {str(k): v for k, v in a.items()}
        return all(str(k) in a and lik(a[str(k)], v) for k, v in b.items())
    try:
        a, b = sympy.sympify(a), sympy.sympify(b)
    except (sympy.SympifyError, TypeError):
        return False
    vanlige = lambda u: u.subs({s: sympy.Symbol(s.name) for s in u.free_symbols})
    a, b = vanlige(a), vanlige(b)
    if isinstance(a, sympy.Set) or isinstance(b, sympy.Set):
        return a == b
    if getattr(b, "is_Relational", False):
        return a == b
    try:
        return sympy.simplify(a - b) == 0
    except TypeError:
        return a == b

oppgave = last_notebook("oppgave")

SJEKKER = [
    ('1a', 'los_1a skal være [4]', 'lik(los_1a, [4])'),
    ('1b', 'los_1b skal være [ln(7)/2]', "lik(los_1b, [S('log(7)/2')])"),
    ('1c', 'los_1c skal være [3] (x = -2 er ikke gyldig)', 'lik(los_1c, [3])'),
    ('2', 'doblingstid(7) skal gi ca. 10.24 år', 'naer(doblingstid(7), 10.2448, rel=1e-4) and naer(doblingstid(100), 1)'),
    ('3_rate', 'vekstrate(15) skal gi ln(1.15) ≈ 0.1398', 'naer(vekstrate(15), 0.139762, rel=1e-4) and naer(vekstrate(-50), -0.693147, rel=1e-4)'),
    ('3_kont', 'kontinuerlig(2000, 0.1, 5) skal gi 2000·e^0.5 ≈ 3297', 'naer(kontinuerlig(2000, 0.1, 5), 3297.44, rel=1e-4)'),
    ('4', 'alder(0.25) skal gi 11460 år og alder(0.5) 5730 år', 'naer(alder(0.25), 11460) and naer(alder(0.5), 5730)'),
    ('5_rente', 'rente(1000, 0.05, 12, 10) skal gi ca. 1647.01', 'naer(rente(1000, 0.05, 12, 10), 1647.0095, rel=1e-6)'),
    ('5_e', 'grense_e skal være tallet e', "lik(grense_e, S('E'))"),
    ('6', 'vekstrate_fra_data([0, 1, 2], [5, 5e^0.3, 5e^0.6]) skal gi k = 0.3', 'naer(vekstrate_fra_data([0, 1, 2], [5, 5*2.718281828459045**0.3, 5*2.718281828459045**0.6]), 0.3)'),
]


@pytest.mark.parametrize(
    "beskrivelse,uttrykk", [s[1:] for s in SJEKKER], ids=[s[0] for s in SJEKKER]
)
def test_sjekk(beskrivelse, uttrykk):
    navnerom = {**vars(oppgave), "naer": naer, "lik": lik, "S": S}
    assert eval(uttrykk, navnerom), beskrivelse
