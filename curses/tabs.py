#!/usr/bin/env python
# coding: utf8

from os import remove
from glob import glob
import os.path
import curses

def cleanup(files):
  for f in files:
    remove(f)

def quit(files):
  cleanup(files)
  curses.endwin()
  exit()

def load(f):
  f = open(f, 'r')
  return curses.getwin(f)

def save(tab, f):
  f = open(f, 'w')
  return tab.putwin(f)

def border(tab, active=False, first=False):
  # curses.border(left, right, top, bottom, top-left, top-right, bottom-left, bottom-right)
  # 0 is default
  if active:
    if first:                                                                 # ┌───────┐
      tab.border(0, 0, 0, ' ', 0, 0, curses.ACS_VLINE, curses.ACS_LLCORNER)   # │ Tab 1 │
                                                                              # │       └

    else:                                                                     # ┌───────┐
      tab.border(0, 0, 0, ' ', 0, 0, curses.ACS_LRCORNER, curses.ACS_LLCORNER)# │ Tab X │
                                                                              # ┘       └
  else:
    if first:                                                                 # ┌───────┐
      tab.border(0, 0, 0, 0, 0, 0, curses.ACS_ULCORNER, curses.ACS_HLINE)     # │ Tab 1 │
                                                                              # ┌────────

    else:                                                                     # ┌───────┐
      tab.border(0, 0, 0, 0, 0, 0, curses.ACS_HLINE, curses.ACS_HLINE)        # │ Tab X │
                                                                              # ─────────

def help(s, key_next, key_prev, key_jump, key_help, key_quit, tab_number):
  s.addstr(0, 0, 'Next tab:       %s' % '/'.join(key_next))
  s.addstr(1, 0, 'Previous tab:   %s' % '/'.join(key_prev))
  s.addstr(2, 0, 'Jumpt to tab:   %s' % '/'.join(key_jump))
  s.addstr(3, 0, 'Help:           %s' % '/'.join(key_help))
  s.addstr(4, 0, 'Exit:           %s' % '/'.join(key_quit))
  s.addstr(6, 0, 'There are a total of %i tabs.' % tab_number)
  s.addstr(7, 0, 'Press any key to continue...')
  s.getch()

def main(stdscr):
  curses.curs_set(0)
  curses.start_color()
  curses.use_default_colors()

  # Configuration
  tab_number = 3
  key_next = ['+', '=']
  key_prev = '-'
  key_jump = ':'
  key_help = 'h'
  key_quit = 'q'


  tabs, files = ([], [])
  d = os.path.dirname(__file__)

  maxy, maxx = stdscr.getmaxyx()
  h, w = (maxy - 4, maxx - 2)
  # Set up each pane and associated file
  for i in range(0, tab_number):
    t = curses.newwin(h, w, 3, 1)
    f = os.path.join(d, '%i.ctab' % i)
    tabs  += [t]
    files += [f]

    # Initalize the tab
    t.addstr('You are in tab %i' % (i + 1))

    # Save tab to file
    save(t, files[i])

  # Set up each tab
  bar, x = ([], 0)
  for i in range(0, tab_number):
    txt = 'Tab %i' % (i + 1)
    w = len(txt) + 4
    t = curses.newwin(3, w, 0, x)
    border(t, active=False)
    t.addstr(1, 2, txt)
    t.refresh()
    bar += [t]
    x += w
    a = False
    f = False

  frame = curses.newwin(maxy - 3, maxx, 3, 0)
  frame.border(0, 0, 0, 0, curses.ACS_VLINE, curses.ACS_VLINE)
  frame.refresh()

  end = curses.newwin(1, maxx - x, 2, x)
  end.border(' ', ' ', ' ', 0, ' ', ' ', curses.ACS_HLINE, curses.ACS_URCORNER)
  end.refresh()

  n = 0 # Start at tab 0
  curses.ungetch(key_help) # Simulate press of key_help
  while True:
    # Load and display new tab
    first = False
    if n == 0:
      first = True
    border(bar[n], active=True, first=first)
    bar[n].addstr(1, 2, 'Tab %i' % (n + 1), curses.A_BOLD)
    t = load(files[n])
    bar[n].refresh()
    t.refresh()

    o = n # Save current tab ID
    while True:
      k = t.getkey()
      if k in key_next:
        n += 1
        if n > len(tabs) - 1: n = 0 # Wrap around
        break

      elif k in key_prev:
        n -= 1
        if n < 0: n = len(tabs) - 1 # Wrap around
        break

      elif k in key_jump:
        try:
          t.addstr(2, 0, ' ' * (curses.COLS - 2)) # Empty line to prevenet overlapping text
          t.addstr(2, 0, 'Jump to tab: ')
          curses.echo(1) # Show what's being typed
          k = int(t.getstr()) - 1 # This is the reason for try (might not be int)
          curses.echo(0)
          t.addstr(2, 0, ' ' * (curses.COLS - 2))
          if (k != n) and (k in range(tab_number)):
            n = k
            break
        except:
          t.addstr(2, 0, ' ' * (curses.COLS - 2))
          curses.echo(0)

      elif k in key_help:
        save(t, files[n])
        t.erase()
        help(t, key_next, key_prev, key_jump, key_help, key_quit, tab_number)
        t = load(files[n])

      elif k in key_quit:
        quit(files)

    # This isn't needed in this example, but in a real
    # use where the tab is modified in between it would
    save(t, files[o])
    if o == 0:
      first = True
    border(bar[o], first=first)
    bar[o].addstr(1, 2, 'Tab %i' % (o + 1))
    bar[o].refresh()


if __name__ == '__main__':
  try:
    curses.wrapper(main)
  except KeyboardInterrupt:
    files = os.path.join(os.path.dirname(__file__), '*.ctab')
    quit(glob(files))
  exit(0)
