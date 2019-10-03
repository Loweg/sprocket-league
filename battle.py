from sys import stdin
import random
import curses
import time
import display

class Battle:
    def __init__(self, *robots):
        self.combatants = set(robots)

    def status(self):
        s = f"There are {len(self.combatants)} combatants:\n"
        for r in self.combatants:
            s += r.status()
            s += '\n'
        return s

    def in_progress(self):
        return sum(map(int, map(lambda x: x.is_alive(), self.combatants))) > 1

    def run(self, stdscr):
        display.init()
        log = curses.newwin(curses.LINES, curses.COLS//5, 0, (curses.COLS-1)-curses.COLS//5)
        statuses = curses.newwin(curses.LINES//2, curses.COLS//2, 0, 0)

        statuses.clear()
        statuses.addstr(0, 0, self.status())
        statuses.refresh()
        inp = log.getkey()
        if inp == 'q':
            return

        while self.in_progress():
            log.addstr('\n')

            for c in self.combatants:
                if not c.is_alive():
                    continue

                if not c.has_brain():
                    log.addstr(f"Robot {c.name} is unable to move!\n", curses.color_pair(1))
                    continue

                weapon = c.pick_alive_part('weapon')
                if weapon is None:
                    log.addstr(f"Robot {c.name} has no weapons!\n", curses.color_pair(1))
                    continue

                candidates = self.combatants.copy()
                candidates.remove(c)
                target = random.choice(list(candidates))

                target_part = target.pick_alive_part('any')

                damage = random.randint(0, 5)
                hit_chance = 100
                if target_part.size < 5:
                    hit_chance = 80
                hit = random.randint(0, 100)

                if hit > hit_chance:
                    log.addstr(f"Robot {c.name} tries to attack {target.name}'s {target_part.name} with {weapon.name} but misses!\n")
                else:
                    target_part.take_damage(damage)
                    log.addstr(f"Robot {c.name} battered {target.name}'s {target_part.name} with {weapon.name}\n")
                    if target_part.is_destroyed():
                        log.addstr(f"{target.name}'s {target_part.name} was destroyed!\n", curses.color_pair(1))
                    living, reason = target.alive_reason()
                    if not living:
                        log.addstr(f"{target.name} died because {reason}!\n", curses.color_pair(1))
                log.refresh()
            statuses.clear()
            statuses.addstr(0, 0, self.status())
            statuses.refresh()
            inp = log.getkey()
            if inp == 'q':
                break
        statuses.addstr(f"\n\n{[r for r in self.combatants if r.is_alive()][0].name} wins!\n\n", curses.color_pair(2))
        statuses.addstr("Press q to exit")
        statuses.refresh()
        while True:
            inp = log.getkey()
            if inp == 'q':
                break