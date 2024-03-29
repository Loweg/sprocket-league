import curses
import random

import display
import grid


class Battle:
    def __init__(self, *robots):
        self.combatants = set(robots)
        if len(self.combatants) != len(set(map(lambda x: x.name, self.combatants))):
            raise ValueError("Expected unique field 'name' on parameters")

    def status(self):
        s = f"There are {len(self.combatants)} combatants:\n"
        for r in self.combatants:
            s += r.status()
            s += "\n"
        return s

    def in_progress(self):
        return sum(map(int, map(lambda x: x.is_alive(), self.combatants))) > 1

    def alive_combatants(self):
        return [x for x in self.combatants if x.is_alive()]

    def calculate_hit(self, weapon, target):
        damage = weapon.damage + random.randint(
            -(weapon.damage // 8), weapon.damage // 8
        )

        hit_chance = 100
        if target.size < 40:
            hit_chance = (target.size * 100) // 40
        hit = random.randint(0, 100)

        if hit_chance > hit:
            return damage
        return 0

    def run(self, stdscr):
        # Init grid
        size = (10, 10)
        g = grid.Grid(size)
        map(lambda x: g.add_rand(x.name), self.combatants)

        # Init displays
        display.init()
        log = curses.newwin(
            curses.LINES, curses.COLS // 4, 0, (curses.COLS - 1) - curses.COLS // 4
        )
        log.keypad(True)
        log.scrollok(True)
        statuses = curses.newwin(curses.LINES, curses.COLS // 3, 0, 0)
        arena = curses.newwin(
            g.size[1] * 2,
            g.size[0] * 4,
            curses.LINES - (g.size[1] + 5),
            (curses.COLS // 2) - (g.size[0] * 2),
        )

        # Game loop
        while self.in_progress():
            # Process displays
            log.addstr("\n")
            log.refresh()

            statuses.clear()
            statuses.addstr(0, 0, self.status())
            statuses.refresh()

            arena.clear()
            arena.addstr(g.draw())
            arena.refresh()

            # Event pump
            inp = log.getkey()
            if inp == "KEY_UP":
                log.scroll()
                continue
            elif inp == "KEY_DOWN":
                log.scroll(-1)
                continue
            elif inp == "q":
                return

            # Processs turns
            for c in self.combatants:
                if not c.is_alive():
                    continue

                if not c.controller():
                    log.addstr(f"{c.name} can't take a turn!\n", curses.color_pair(1))
                    continue

                # Process movement
                if not c.movers():
                    log.addstr(f"{c.name} is unable to move!\n", curses.color_pair(1))
                else:
                    g.move(c.name, random.randint(-1, 1), random.randint(-1, 1))

                # Choose weapon
                weapon = c.pick_alive_part("weapon")
                if weapon is None:
                    log.addstr(f"{c.name} has no weapons!\n", curses.color_pair(1))
                    continue

                # Choose a target robot and part
                candidates = self.alive_combatants()
                candidates.remove(c)
                target = random.choice(list(candidates))

                if g.get_distance(c.name, target.name) > weapon.range:
                    log.addstr(
                        f"{target.name} is out of range of {c.name}'s {weapon.name}\n",
                        curses.color_pair(1),
                    )
                    continue

                target_part = target.pick_alive_part("any")

                hit = self.calculate_hit(weapon, target_part)

                # Report and process hit
                assert hit >= 0
                if hit == 0:
                    log.addstr(
                        f"{c.name} tries to attack {target.name}'s {target_part.name}"
                        f" with the {weapon.name} but misses!\n"
                    )
                else:
                    target_part.take_damage(hit)
                    log.addstr(
                        f"{c.name} {weapon.verb()} {target.name}'s {target_part.name}"
                        f" with the {weapon.name}\n"
                    )
                    if target_part.is_destroyed():
                        log.addstr(
                            f"{target.name}'s {target_part.name} was destroyed!\n",
                            curses.color_pair(1),
                        )
                    living, reason = target.alive_reason()
                    if not living:
                        log.addstr(
                            f"{target.name} died because {reason}!\n",
                            curses.color_pair(1),
                        )

        statuses.addstr(
            f"\n\n{[r for r in self.combatants if r.is_alive()][0].name} wins!\n\n",
            curses.color_pair(2),
        )
        statuses.addstr("Press q to exit")
        statuses.refresh()
        while True:
            inp = log.getkey()
            if inp == "q":
                break
