# Generate orange color ramp using the same algorithm as rampa.ts
# Seed color: #e95619 (logo orange)

import math

def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def linear_to_srgb(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1/2.4)) - 0.055

def hex_to_linear(hex_color):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join([c*2 for c in hex_color])
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return [srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)]

def linear_to_hex(lin):
    def f(v):
        return max(0, min(255, round(linear_to_srgb(max(0, min(1, v))) * 255)))
    return "#{:02x}{:02x}{:02x}".format(f(lin[0]), f(lin[1]), f(lin[2]))

def linear_to_oklab(lin):
    r, g, b = lin
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    lr = l ** (1/3)
    mr = m ** (1/3)
    sr = s ** (1/3)
    return {
        "L": 0.2104542553 * lr + 0.793617785 * mr - 0.0040720468 * sr,
        "a": 1.9779984951 * lr - 2.428592205 * mr + 0.4505937099 * sr,
        "b": 0.0259040371 * lr + 0.7827717662 * mr - 0.808675766 * sr,
    }

def oklab_to_linear(lab):
    L, a, b = lab["L"], lab["a"], lab["b"]
    lr = L + 0.3963377774 * a + 0.2158037573 * b
    mr = L - 0.1055613458 * a - 0.0638541728 * b
    sr = L - 0.0894841775 * a - 1.291485548 * b
    l = lr ** 3
    m = mr ** 3
    s = sr ** 3
    return [
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s,
    ]

def hex_to_oklch(hex_color):
    lin = hex_to_linear(hex_color)
    lab = linear_to_oklab(lin)
    h = math.atan2(lab["b"], lab["a"]) * 180 / math.pi
    if h < 0: h += 360
    return {"L": lab["L"], "C": math.hypot(lab["a"], lab["b"]), "h": h}

def oklch_to_hex(oklch):
    Lc = max(0, min(1, oklch["L"]))
    C = oklch["C"]
    h = oklch["h"]
    rad = h * math.pi / 180
    lin = oklab_to_linear({"L": Lc, "a": C * math.cos(rad), "b": C * math.sin(rad)})
    def in_gamut(v):
        return all(-1e-4 <= x <= 1 + 1e-4 for x in v)
    if not in_gamut(lin):
        low, high = 0, C
        for _ in range(40):
            mid = (low + high) / 2
            test_lin = oklab_to_linear({"L": Lc, "a": mid * math.cos(rad), "b": mid * math.sin(rad)})
            if in_gamut(test_lin):
                low = mid
            else:
                high = mid
        lin = oklab_to_linear({"L": Lc, "a": low * math.cos(rad), "b": low * math.sin(rad)})
    return linear_to_hex(lin)

# Sage constants from rampa.ts
ESCADA_L = [0.9695, 0.9317, 0.8597, 0.7634, 0.6718, 0.5899, 0.5015, 0.4303, 0.3772, 0.339, 0.2278]
CURVA_C = [0.11, 0.247, 0.486, 0.765, 1.021, 1.111, 1.0, 0.789, 0.63, 0.508, 0.334]
K = 6

seed = "#e95619"
oklch = hex_to_oklch(seed)
print("Seed: " + seed)
print("OKLCh: L={:.4f}, C={:.4f}, h={:.2f}".format(oklch["L"], oklch["C"], oklch["h"]))

Ls = oklch["L"]
Cs = oklch["C"]
h = oklch["h"]
CK = CURVA_C[K]
C0 = Cs / CK

L0 = ESCADA_L[0]
L10 = ESCADA_L[10]
LK = ESCADA_L[K]

def lightness_do_stop(indice, Lsemente):
    L = ESCADA_L[indice]
    if indice <= K:
        return L0 + (L - L0) * ((Lsemente - L0) / (LK - L0))
    else:
        return Lsemente + (L - LK) * ((L10 - Lsemente) / (L10 - LK))

stops = []
for i in range(11):
    L_stop = lightness_do_stop(i, Ls)
    C_stop = C0 * CURVA_C[i]
    hex_stop = oklch_to_hex({"L": L_stop, "C": C_stop, "h": h})
    stops.append(hex_stop)

stops[K] = seed.lower()

print("\nOrange color ramp (11 stops):")
graus = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
for grau, hex_val in zip(graus, stops):
    print("  --color-accent-{}: {};".format(grau, hex_val))

