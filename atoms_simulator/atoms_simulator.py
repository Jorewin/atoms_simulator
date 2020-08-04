from __future__ import annotations
import pygame
from pygame import gfxdraw
import sys
import random
import toml
import time
import re
import os.path


class Settings:
    """A class used to load, save and access settings from a TOML file.

    :ivar tags: The dictionary containing actual settings.
    :type tags: dict
    :ivar source: The string containing name of a TOML file that is used for loading and saving settings.
    :type source: str
    """
    def __init__(self, source: str = "settings.toml"):
        """Initialize Settings type object.

        :param source: The string containing name of a TOML file that is used for loading and saving settings.
        """
        self.tags = {}
        self.source = source

    def __getitem__(self, item):
        if self.tags.get(item):
            return self.tags[item]
        else:
            return None

    def new(self, name: str, value):
        """Create a new setting

        :param name: the name of the new setting
        :param value: the value of the new setting
        """
        self.tags[name] = value

    def save(self, target: str = None) -> bool:
        """Save the settings.

        :param target: a name of a file with .toml extension
        :return:
        """
        if target is None:
            target = self.source
        if not isinstance(target, str):
            return False
        if not re.search(r".+\.toml$", target):
            return False
        with open(target, "w") as goal:
            toml.dump(self.tags, goal)
        return True

    def load(self) -> bool:
        """Load the settings from self.source file.

        :return:
        """
        if not isinstance(self.source, str):
            return False
        if not re.search(r".+\.toml$", self.source):
            return False
        if not os.path.isfile(self.source):
            return False
        with open(self.source, "r") as origin:
            self.tags = toml.load(origin)
        return True


# OBJECTS
class Atom:
    """A class used to store and process information about an instance of an atom.

    :ivar x: x position coordinate
    :type x: int
    :ivar y: y position coordinate
    :type y: int
    :ivar vx: velocity vector's x coordinate
    :type vx: float
    :ivar vy: velocity vector's y coordinate
    :type vy: float
    :ivar color: color used to mark the atom during the simulation
    :type color: pygame.Color
    :ivar radius:
    :type radius: int
    """
    def __init__(self, x: int, y: int, vx: float, vy: float, color: pygame.Color, radius: int):
        """Initialize an Atom type object.

        :param x: x position coordinate
        :param y: y position coordinate
        :param vx: velocity vector's x coordinate
        :param vy: velocity vector's y coordinate
        :param color: color used to mark the atom during the simulation
        :param radius:
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius

    def update(self, time: float):
        """Updates the objects position by its velocity multiplied by *time*.

        :param time: time
        """
        self.x += int(self.vx * time)
        self.y += int(self.vy * time)


    def wall_check(self, width: int, height: int, collision_tolerance: int):
        """Checks if a collision between the atom and a wall occured and modifies the atom's velocity.
        :param width: width of the container
        :param height: height of the container
        :param collision_tolerance:
        """
        if (self.x - self.radius <= collision_tolerance and self.vx < 0) or \
        (self.x + self.radius >= width - collision_tolerance and self.vx > 0):
            self.vx *= -1
        if (self.y - self.radius <= collision_tolerance and self.vy < 0) or \
        (self.y + self.radius >= height - collision_tolerance and self.vy > 0):
            self.vy *= -1

    def atom_check(self, other: Atom, collision_tolerance: int):
        """Checks if a collision between two atoms occured and modifies their velocities.

        :param other: an another atom
        :param collision_tolerance:
        """
        distance = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        future_distance = ((self.x + self.vx - other.x - other.vx) ** 2 +
                           (self.y + self.vy - other.y - other.vy) ** 2) ** 0.5
        if 2 * self.radius <= distance <= 2 * self.radius + collision_tolerance or \
                future_distance < 2 * self.radius:
            a = other.x - self.x
            b = other.y - self.y
            if (a * self.vx + b * self.vy) == 0:
                xn1, yn1 = 0, 0
            else:
                cosine = (a * self.vx + b * self.vy) / ((a ** 2 + b ** 2) * (self.vx ** 2 + self.vy ** 2)) ** 0.5
                xn1 = (cosine ** 2 * a * (self.vx ** 2 + self.vy ** 2)) / (a * self.vx + b * self.vy)
                yn1 = (cosine ** 2 * b * (self.vx ** 2 + self.vy ** 2)) / (a * self.vx + b * self.vy)
            a, b = -a, -b
            if (a * other.vx + b * other.vy) == 0:
                xn2, yn2 = 0, 0
            else:
                cosine = (a * other.vx + b * other.vy) / ((a ** 2 + b ** 2) * (other.vx ** 2 + other.vy ** 2)) ** 0.5
                xn2 = (cosine ** 2 * a * (other.vx ** 2 + other.vy ** 2)) / (a * other.vx + b * other.vy)
                yn2 = (cosine ** 2 * b * (other.vx ** 2 + other.vy ** 2)) / (a * other.vx + b * other.vy)
            self.vx, self.vy, other.vx, other.vy = \
                self.vx - xn1 + xn2, self.vy - yn1 + yn2, other.vx - xn2 + xn1, other.vy - yn2 + yn1

    def atom_check_linear(self, other: Atom, collision_tolerance: int):
        """Checks if a collision between two atoms occured and modifies their velocities.

                :param other: an another atom
                :param collision_tolerance:
                """
        distance = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        future_distance = ((self.x + self.vx - other.x - other.vx) ** 2 +
                           (self.y + self.vy - other.y - other.vy) ** 2) ** 0.5
        if 2 * self.radius <= distance <= 2 * self.radius + collision_tolerance or \
                future_distance < 2 * self.radius:
            if abs(self.x - other.x) > abs(self.y - other.y):
                other.vx, self.vx = self.vx, other.vx
            else:
                other.vy, self.vy = self.vy, other.vy


def random_list(n: int, width: int, height: int, v: int, atom_radius: int, collision_tolerance: int) -> list:
    """Create a list containing *n* randomly generated :class:`Atom` objects.

    :param n: number of atoms
    :param width: width of the available space
    :param height: height of the available space
    :param v: velocity will be randomly chosen from <-v, v>
    :param atom_radius:
    :param collision_tolerance:
    :return: list containing *n* randomly generated :class:`Atom` objects
    """
    atoms = []
    for i in range(n):
        while True:
            x = random.randint(atom_radius, width - atom_radius)
            y = random.randint(atom_radius, height - atom_radius)
            for i in range(len(atoms)):
                if ((x - atoms[i].x)**2 + (y - atoms[i].y)**2)**0.5 < 2 * atom_radius + collision_tolerance:
                    break
            else:
                break
        vx = 0
        vy = 0
        while vx == 0:
            vx = random.randint(-v, v)
        while vy == 0:
            vy = random.randint(-v, v)
        atoms.append(Atom(x, y, vx, vy, pygame.Color("blue"), atom_radius))
    return atoms


if __name__ == "__main__":
    # Project settings
    settings = Settings()
    settings.load()
    project = Settings(source="atoms_simulator.toml")
    project.load()
    dev = Settings(source="dev_options.toml")
    dev.load()

    # Variables
    width = settings['w'] * settings['r']
    height = settings['h'] * settings['r']
    number_of_atoms = settings["n_min"]
    time_step = max(settings['K'], min(settings['w'], settings['h']))

    # Initialize simulation
    pygame.init()
    icon = pygame.image.load("assets/icon.png")
    pygame.display.set_caption(f"{project['project_name']} {project['version']}")
    pygame.display.set_icon(icon)
    screen = pygame.display.set_mode((width, height + 71))
    atoms = random_list(number_of_atoms, width, height, settings['v'], settings['r'], settings['c'])
    while True:
        screen.fill(pygame.Color(246, 248, 250))
        pygame.draw.rect(screen, pygame.Color(225, 228, 232), [0, height, width, 1])
        pygame.draw.rect(screen, pygame.Color(250, 251, 252), pygame.Rect((0, 0), (width, height)))
        for i in range(number_of_atoms):
            pygame.gfxdraw.filled_circle(screen, atoms[i].x, atoms[i].y, settings['r'], atoms[i].color)
            pygame.gfxdraw.aacircle(screen, atoms[i].x, atoms[i].y, settings['r'], atoms[i].color)
            atoms[i].wall_check(width, height, settings['c'])
            for j in range(i + 1, number_of_atoms):
                if dev["bounce_mode"] == 1:
                    atoms[i].atom_check(atoms[j], settings['c'])
                else:
                    atoms[i].atom_check_linear(atoms[j], settings['c'])
            atoms[i].update(1)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
        time.sleep(dev["time_step"])
