#!/usr/bin/env python

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

def help(s, key_next, key_prev, key_jump, key_help, key_quit, tab_number):
  s.addstr(0, 0, 'Next tab:       %s' % key_next)
  s.addstr(1, 0, 'Previous tab:   %s' % key_prev)
  s.addstr(2, 0, 'Jumpt to tab:   %s' % key_jump)
  s.addstr(3, 0, 'Help:           %s' % key_help)
  s.addstr(4, 0, 'Exit:           %s' % key_quit)
  s.addstr(6, 0, 'There are a total of %i tabs.' % tab_number)
  s.addstr(7, 0, 'Press any key to continue...')
  s.getch()

def main(stdscr):
  curses.curs_set(0)
  curses.start_color()
  curses.use_default_colors()

  # Configuration
  tab_number = 5
  key_next = '+'
  key_prev = '-'
  key_jump = ':'
  key_help = 'h'
  key_quit = 'q'


  tabs, files = ([], [])
  d = os.path.dirname(__file__)

  # Set up each tab and associated file
  for i in range(0, tab_number):
    t = curses.newwin(0, 0)
    f = os.path.join(d, '%i.ctab' % i)
    tabs  += [t]
    files += [f]

    # Initalize the tab
    t.box()
    t.addstr(1, 1, 'You are in tab %i' % (i + 1))

    # Save tab to file
    save(t, files[i])


  help(stdscr, key_next, key_prev, key_jump, key_help, key_quit, tab_number)

  n = 0 # Start at tab 0
  while True:
    # Load and display new tab
    t = load(files[n])
    t.refresh()

    o = n # Save current tab ID
    while True:
      k = t.getkey()
      if k ==  key_next:
        n += 1
        if n > len(tabs) - 1: n = 0 # Wrap around
        break

      elif k == key_prev:
        n -= 1
        if n < 0: n = len(tabs) - 1 # Wrap around
        break

      elif k == key_jump:
        try:
          t.addstr(4, 1, ' ' * (curses.COLS - 2)) # Empty line to prevenet overlapping text
          t.addstr(4, 1, 'Jump to tab: ')
          k = int(t.getkey()) - 1 # This is the reason for try (might not be int)
          t.addstr(4, 1, ' ' * (curses.COLS - 2))
          if (k != n) and (k in range(tab_number)):
            n = k
            break
        except:
          t.addstr(4, 1, ' ' * (curses.COLS - 2))

      elif k == key_help:
        save(t, f)
        t.erase()
        help(t, key_next, key_prev, key_jump, key_help, key_quit, tab_number)
        t = load(f)

      elif k == key_quit:
        quit(files)

    # This isn't needed in this example, but in a real
    # use where the tab is modified in between it would
    save(t, files[o])


if __name__ == '__main__':
  try:
    curses.wrapper(main)
  except KeyboardInterrupt:
    files = os.path.join(os.path.dirname(__file__), '*.ctab')
    quit(glob(files))
  exit(0)
