"""
Pewedit, the text editor for the Pewpew.
See: https://github.com/pewpew-game/

"""

import pew

STARTPOS = 2
MAXLEN = 6
WELCOME_TEXT = "EUROPYTHON 2019"

MORSE = {
    "A": 7,
    "B": 41,
    "C": 50,
    "D": 14,
    "E": 1,
    "F": 49,
    "G": 17,
    "H": 40,
    "I": 4,
    "J": 79,
    "K": 23,
    "L": 43,
    "M": 8,
    "N": 5,
    "O": 26,
    "P": 52,
    "Q": 71,
    "R": 16,
    "S": 13,
    "T": 2,
    "U": 22,
    "V": 67,
    "W": 25,
    "X": 68,
    "Y": 77,
    "Z": 44,
    "1": 241,
    "2": 238,
    "3": 229,
    "4": 202,
    "5": 121,
    "6": 122,
    "7": 125,
    "8": 134,
    "9": 161,
    "0": 242,
    " ": 0,
}

MORSE_REV = {}
for k, v in MORSE.items():
    MORSE_REV[v] = k


def to_byte(s):
    total = 0
    for i, c in enumerate(s):
        if c > 2:
            c = 2
        total += c * 3 ** i
    return total


def to_beep(b):
    total = []
    for _ in range(6):
        total.append(b % 3)
        b = b // 3
    return total


def cls():
    global current_line
    global cp
    global offset
    global lp
    current_line = ""
    cp = 0
    offset = 0
    lp = STARTPOS


curcol = 3


def refresh_screen(scr, cline, cp, offset, blink=False):

    global curcol
    curcol = 1 if curcol == 3 else 3

    if not scr:
        scr = pew.Pix()

    if blink:
        scr.pixel(0, cp, curcol)
    else:
        dt = (cline + "        ")[offset : offset + 8]
        for i in range(8):
            scr.pixel(0, i, curcol if cp == i else 1)
            try:
                b = MORSE.get(dt[i], 0)
            except IndexError:
                b = MORSE.get(" ")
            for j, v in enumerate(to_beep(b)):
                if v > 0:
                    v += 1
                scr.pixel(STARTPOS + j, i, v)

    if offset > 0:
        scr.pixel(7, 0, curcol)
    else:
        scr.pixel(7, 0, 0)
    if len(cline) - 8 > offset:
        scr.pixel(7, 7, curcol)
    else:
        scr.pixel(7, 7, 0)


def read_char(scr, cp, offset, store=False):
    global current_line
    c = scr.buffer[8 * cp + STARTPOS : 8 * cp + 8]
    hc = MORSE_REV.get(to_byte(c), " ")
    if store:
        current_line = set_char(current_line, hc, cp, offset)
        hint(hc)


def set_char(cl, ch, cp, offset):
    try:
        if cl[cp + offset] == ch:
            return cl
        _cl = list(cl or "")
        _cl[cp + offset] = ch
        return "".join(_cl)
    except IndexError:
        # todo: proper
        while len(cl) < cp + offset:
            cl = cl + " "
        return cl + ch


def update_pos(cp, offset, delta=1):
    cp = cp + delta
    while cp < 0:
        offset -= 1
        cp += 1
    while cp > 7:
        offset += 1
        cp -= 1
    if offset < 0 and cp == 0:
        offset = 0
    return cp, offset


def hint(lt):
    if lt:
        b = MORSE.get(lt, 0)
        if b:
            scr = pew.Pix()
            scr.blit(pew.Pix.from_text(lt, color=3), 2, 0)
            for j, v in enumerate(to_beep(b)):
                if v > 1:
                    v = 3
                scr.pixel(STARTPOS + j, 7, v)
            pew.show(scr)
            pew.tick(1)


def show_text(t):
    if not t.strip():
        return
    scr = pew.Pix()
    rpt = False
    text = pew.Pix.from_text(t, color=3)
    while True:
        for dx in range(-8, text.width):
            scr.blit(text, -dx, 1)
            pew.show(scr)
            keys = pew.keys()
            if keys:
                if keys & pew.K_X:
                    return
                if keys & pew.K_O:
                    pew.tick(1 / 24)
                    rpt = True
            else:
                pew.tick(1 / 6)
        if not rpt:
            return


pew.init()
screen = pew.Pix()
cls()
current_line = WELCOME_TEXT
refresh_screen(screen, current_line, cp, offset)
pew.show(screen)
game_speed = 2

while True:
    if cp < 0:
        cp = 0
    if cp > 7:
        cp = 7
    pew.tick(1 / game_speed)

    keys = pew.keys()
    if keys:
        if keys & pew.K_X:
            if lp > STARTPOS:
                lp -= 1
                screen.pixel(lp, cp, 0)
                if lp == STARTPOS:
                    lp = STARTPOS
            else:
                if keys & pew.K_O:
                    cls()
                    lp = STARTPOS
                    refresh_screen(screen, current_line, cp, offset)
        elif (keys & pew.K_LEFT) or (keys & pew.K_RIGHT):
            if lp == STARTPOS:
                for i in range(1, MAXLEN):
                    screen.pixel(lp + i, cp, 0)
            screen.pixel(lp, cp, 1 if keys & pew.K_LEFT else 3)
            lp += 1
        elif (keys & pew.K_DOWN) or (keys & pew.K_UP):
            read_char(screen, cp, offset, lp > STARTPOS)
            cp, offset = update_pos(cp, offset, 1 if (keys & pew.K_DOWN) else -1)
            lp = STARTPOS
            refresh_screen(screen, current_line, cp, offset)
        elif keys & pew.K_O:
            read_char(screen, cp, offset, lp > STARTPOS)
            lp = STARTPOS
            show_text(current_line)
    else:
        refresh_screen(screen, current_line, cp, offset, True)

    pew.show(screen)
