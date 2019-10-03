import util

class Robot:
    def __init__(self, name):
        self.name = name
        self.parts = []

    def add_parts(self, *parts):
        self.parts.extend(parts)

    def is_valid(self):
        if  (len(self._parts_of_type('chassis')) == 1 and
            len(self._parts_of_type('controller')) == 1 and
            len(self._parts_of_type('power')) > 0):
           return True
        return False

    def is_alive(self):
        return self._parts_of_type('chassis')[0].health > 0

    def has_power(self):
        return any(map(lambda p: not p.is_destroyed(), self._parts_of_type('power')))

    def has_brain(self):
        return not self._parts_of_type('controller')[0].is_destroyed() and self.has_power()

    def health(self):
        return sum(map(lambda p: p.health, self.parts))

    def size(self):
        return sum(map(lambda p: p.size, self.parts))

    def weighted_parts(self):
        return [x.size/self.size() for x in self.parts]

    def pick_alive_part(self, typ):
        return util.choice([p for p in self._parts_of_type(typ) if not p.is_destroyed()])

    def alive_parts(self):
        return [p for p in self.parts if not p.is_destroyed()]

    def _parts_of_type(self, typ):
        return [p for p in self.parts if p.typ == typ]
        #return filter(lambda p: p.typ == typ, self.parts)

    def __str__(self):
        return f"Robot {self.name} with {self.health()} hp and size {self.size()}"