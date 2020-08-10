from __future__ import annotations
import pygame
from pygame import gfxdraw
from pygame import freetype
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


class Atom:
    """A class used to store and process information about an instance of an atom.

    :ivar x: x position coordinate
    :type x: float
    :ivar y: y position coordinate
    :type y: float
    :ivar vx: velocity vector's x coordinate
    :type vx: float
    :ivar vy: velocity vector's y coordinate
    :type vy: float
    :ivar color: color used to mark the atom during the simulation
    :type color: :class:`pygame.Color`
    :ivar radius:
    :type radius: int
    """
    def __init__(self, x: int, y: int, vx: int, vy: int, color: pygame.Color, radius: int):
        """Initialize an Atom type object.

        :param x: x position coordinate
        :param y: y position coordinate
        :param vx: velocity vector's x coordinate
        :param vy: velocity vector's y coordinate
        :param color: color used to mark the atom during the simulation
        :param radius:
        """
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.radius = radius

    def update(self, time_step: float):
        """Updates the objects position by its velocity multiplied by *time_step*.

        :param time_step:
        """
        self.x, self.y = self.x + self.vx * time_step, self.y + self.vy * time_step

    def wall_bounce(self, width: int, height: int, collision_tolerance: int):
        """Checks if a collision between the atom and a wall occured and modifies the atom's velocity.
        :param width: width of the container
        :param height: height of the container
        :param collision_tolerance:
        """
        if self.x + self.vx - self.radius < collision_tolerance or \
                self.x + self.vx + self.radius > width - collision_tolerance:
            self.vx *= -1
        if self.y + self.vy - self.radius < collision_tolerance or \
                self.y + self.vy + self.radius > height - collision_tolerance:
            self.vy *= -1

    def atom_bounce(self, other: Atom, collision_tolerance: int):
        """Checks if a collision between two atoms occured and modifies their velocities.

        :param other: an another atom
        :param collision_tolerance:
        """
        distance = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        future_distance = ((self.x + self.vx - other.x - other.vx) ** 2 +
                           (self.y + self.vy - other.y - other.vy) ** 2) ** 0.5
        condition_1 = self.radius + other.radius <= distance <= self.radius + other.radius + collision_tolerance
        a = other.x - self.x
        b = other.y - self.y
        condition_2 = True
        if abs(self.vx) >= abs(self.vy) and self.vx * a <= 0:
            condition_2 = False
        if abs(self.vx) < abs(self.vy) and self.vy * b <= 0:
            condition_2 = False
        a, b = -a, -b
        condition_3 = True
        if abs(other.vx) >= abs(other.vy) and other.vx * a <= 0:
            condition_3 = False
        if abs(other.vx) < abs(other.vy) and other.vy * b <= 0:
            condition_3 = False
        condition_4 = future_distance < self.radius + other.radius
        if condition_1 and (condition_2 or condition_3) or condition_4:
            a, b = -a, -b
            if a == b == 0:
                xn1, yn1 = 0, 0
            else:
                xn1 = (a * (a * self.vx + b * self.vy)) / (a ** 2 + b ** 2)
                yn1 = (b * (a * self.vx + b * self.vy)) / (a ** 2 + b ** 2)
            a, b = -a, -b
            if a == b == 0:
                xn2, yn2 = 0, 0
            else:
                xn2 = (a * (a * other.vx + b * other.vy)) / (a ** 2 + b ** 2)
                yn2 = (b * (a * other.vx + b * other.vy)) / (a ** 2 + b ** 2)
            self.vx, self.vy, other.vx, other.vy = \
                self.vx - xn1 + xn2, self.vy - yn1 + yn2, other.vx - xn2 + xn1, other.vy - yn2 + yn1

    def wall_check(self, width: int, height: int, x: float, y: float):
        if x < self.radius:
            x = self.radius
            y = x * self.vy / self.vx + (self.x * self.vy - self.vx * self.y) / self.vx
        if x > width - self.radius:
            x = width - self.radius
            y = x * self.vy / self.vx + (self.x * self.vy - self.vx * self.y) / self.vx
        if y < self.radius:
            y = self.radius
            x = (y - (self.x * self.vy - self.vx * self.y) / self.vx) * self.vx / self.vy
        if y > height - self.radius:
            y = height - self.radius
            x = (y - (self.x * self.vy - self.vx * self.y) / self.vx) * self.vx / self.vy
        return x, y

    def atom_check(self, other: Atom, x: float, y: float):
        a = other.x - x
        b = other.y - y
        distance = (a ** 2 + b ** 2) ** 0.5
        if distance < self.radius + other.radius:
            a = other.x - self.x
            b = other.y - self.y
            distance = (a ** 2 + b ** 2) ** 0.5
            n = distance / (distance - self.radius - other.radius)
            a /= n
            b /= n
            x = a + self.x
            y = b + self.y
        return x, y


class Text:
    def __init__(self, text, width, precision, color, font, padding):
        self.text = text
        self.width = width
        self.precision = precision
        self.color = color
        self.field = self.gen_rect(font)
        self.p_field = self.gen_padded_rect(padding)

    def gen_rect(self, font):
        charr = f"{self.text}: {float(10 ** (self.width - 1))}:{self.width + self.precision + 1}.{self.precision}f"
        _, rect = font.render(charr, self.color)
        return rect

    def gen_padded_rect(self, padding):
        p_field = pygame.Rect(self.field)
        p_field.width += 2 * padding
        p_field.height += 2 * padding
        return p_field

    def update_field(self):
        self.field.center = self.p_field.center

    def gen_text(self, font, value):
        if value >= 10 ** self.width:
            charr = f"{self.text}: {float(10 ** self.width - 1):{self.width + self.precision + 1}.{self.precision}f}"
            text, _ = font.render(charr, self.color)
        else:
            charr = f"{self.text}: {float(value):{self.width + self.precision + 1}.{self.precision}f}"
            text, _ = font.render(charr, self.color)
        return text


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


def create_texts(font, padding):
    texts = {}
    texts["turn"] = Text("Turn", 3, 0, pygame.Color(0, 0, 0), font, padding)
    return texts


def coords(container, x, y):
    y = container.height - y
    return int(x), int(y)


def main():
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
    time_step = max(settings['K'], min(settings['w'], settings['h'])) * settings['v']

    # Pygame settings
    pygame.init()
    icon = pygame.image.load("assets/icon.png")
    pygame.display.set_caption(f"{project['project_name']} {project['version']}")
    pygame.display.set_icon(icon)
    font = pygame.freetype.SysFont("Courier New", 30, bold=True)
    padding = 10
    border_width = 1

    # Create rects
    texts = create_texts(font, padding)
    container = pygame.Rect((0, 0), (width, height))
    p_container = pygame.Rect((0, 0), (width + 2 * padding, height + 2 * padding))
    current = 0
    for text in texts.values():
        text.p_field.top = p_container.bottom
        text.p_field.left = current
        current = text.p_field.right
    screen_rect = pygame.Rect((0, 0), (0, 0))
    screen_rect.union_ip(p_container)
    for text in texts.values():
        screen_rect.union_ip(text.p_field)
        text.update_field()
    info_object = pygame.display.Info()
    if info_object.current_w < screen_rect.width or info_object.current_h < screen_rect.height:
        return
    p_container.centerx = screen_rect.centerx
    container.center = p_container.center
    border_rect = container.inflate(2 * border_width, 2 * border_width)

    # Initialize simulation
    screen = pygame.display.set_mode(screen_rect.bottomright)
    container_surface = pygame.Surface(container.size)
    atoms = random_list(number_of_atoms, width, height, settings['v'], settings['r'], settings['c'])
    while True:
        screen.fill(pygame.Color(246, 248, 250))
        container_surface.fill(pygame.Color(250, 251, 252))
        pygame.draw.rect(screen, pygame.Color(225, 228, 232), border_rect, border_width)
        for i in range(number_of_atoms):
            for j in range(i + 1, number_of_atoms):
                atoms[i].atom_bounce(atoms[j], settings['c'])
            atoms[i].wall_bounce(width, height, settings['c'])
            x, y = coords(container, atoms[i].x, atoms[i].y)
            pygame.gfxdraw.filled_circle(container_surface, x, y, atoms[i].radius, atoms[i].color)
            pygame.gfxdraw.aacircle(container_surface, x, y, atoms[i].radius, atoms[i].color)
            atoms[i].update(1)
        screen.blit(container_surface, container)
        for text in texts.values():
            screen.blit(text.gen_text(font, 1), text.field)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
        time.sleep(0.01)


if __name__ == "__main__":
    main()
