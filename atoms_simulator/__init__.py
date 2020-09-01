from __future__ import annotations
import os
import os.path
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame import gfxdraw
from pygame import freetype
import sys
import random
import toml
import re
import os.path


class Settings:
    """A class used to load, save and access settings from a TOML file.

    :ivar tags: The dictionary containing actual settings.
    :type tags: dict
    :ivar source: The string containing name of a TOML file that is used for loading and saving settings.
    :type source: str
    """
    def __init__(self, source: str):
        """Initialize Settings type object.

        :param source: The string containing name of a TOML file that is used for loading and saving settings.
        """
        self.tags = {}
        self.source = source

    def __getitem__(self, item):
        if self.tags.get(item) is not None:
            return self.tags[item]
        else:
            return None

    def __setitem__(self, key, value):
        if self.tags.get(key) is not None:
            self.tags[key] = value

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

    :ivar x: the x position coordinate
    :type x: float
    :ivar y: the y position coordinate
    :type y: float
    :ivar vx: the velocity vector's x coordinate
    :type vx: float
    :ivar vy: the velocity vector's y coordinate
    :type vy: float
    :ivar color: the color used to mark the atom during the simulation
    :type color: :class:`pygame.Color`
    :ivar radius: the radius of the atom
    :type radius: int
    """
    def __init__(self, x: int, y: int, vx: int, vy: int, color: pygame.Color, radius: int):
        """Initialize an Atom type object.

        :param x: the x position coordinate
        :param y: the y position coordinate
        :param vx: the velocity vector's x coordinate
        :param vy: the velocity vector's y coordinate
        :param color: the color used to mark the atom during the simulation
        :param radius: the radius of the atom
        """
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.radius = radius

    def update(self, time_step: float):
        """Updates the object's position by its velocity multiplied by *time_step*.

        :param time_step:
        """
        self.x, self.y = self.x + self.vx * time_step, self.y + self.vy * time_step

    def wall_bounce(self, width: int, height: int, collision_tolerance: int) -> bool:
        """Checks if a collision between the atom and the wall occured and modifies the atom's velocity.

        :param width: width of the container
        :param height: height of the container
        :param collision_tolerance:
        :return:
        """
        result = False
        # if self.x + self.vx - self.radius < collision_tolerance or \
        #         self.x + self.vx + self.radius > width - collision_tolerance:
        #     self.vx *= -1
        #     result = True
        # if self.y + self.vy - self.radius < collision_tolerance or \
        #         self.y + self.vy + self.radius > height - collision_tolerance:
        #     self.vy *= -1
        #     result = True
        if (self.x - self.radius <= collision_tolerance and self.vx < 0) or \
                (self.x + self.radius >= width - collision_tolerance and self.vx > 0):
            self.vx *= -1
            result = True
        if (self.y - self.radius <= collision_tolerance and self.vy < 0) or \
                (self.y + self.radius >= height - collision_tolerance and self.vy > 0):
            self.vy *= -1
            result = True
        return result

    def atom_bounce(self, other: Atom, collision_tolerance: int) -> bool:
        """Checks if a collision between two atoms occured and modifies their velocities.

        :param other: an another atom
        :param collision_tolerance:
        :return:
        """
        distance = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        future_distance = ((self.x + self.vx - other.x - other.vx) ** 2 +
                           (self.y + self.vy - other.y - other.vy) ** 2) ** 0.5
        condition_1 = self.radius + other.radius <= distance <= self.radius + other.radius + collision_tolerance
        a = other.x - self.x
        b = other.y - self.y
        condition_2 = round(self.vx * a + self.vy * b, 1) > 0
        # condition_2 = (abs(self.vx) >= abs(self.vy) and self.vx * a > 0) or \
        #               (abs(self.vx) < abs(self.vy) and self.vy * b > 0)
        a, b = -a, -b
        condition_3 = round(other.vx * a + other.vy * b, 1) > 0
        # condition_3 = (abs(other.vx) >= abs(other.vy) and other.vx * a > 0) or \
        #               (abs(other.vx) < abs(other.vy) and other.vy * b > 0)
        # condition_4 = future_distance < self.radius + other.radius
        if condition_1 and (condition_2 or condition_3):
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
            return True
        return False


class TestAtom(Atom):
    """A class used to store and process information about an instance of an atom.

        :ivar x: the x position coordinate
        :type x: float
        :ivar y: the y position coordinate
        :type y: float
        :ivar vx: the velocity vector's x coordinate
        :type vx: float
        :ivar vy: the velocity vector's y coordinate
        :type vy: float
        :ivar color: the color used to mark the atom during the simulation
        :type color: :class:`pygame.Color`
        :ivar radius: the radius of the atom
        :type radius: int
        :ivar bounced: Indicates if the atom has bounced recently.
        :type bounced: bool
        :ivar distance: The distance that the atom has managed to travel since the last bounce.
        :type distance: float
        :ivar distance_storage: A list containing all previous distances.
        :type distance_storage: list
        """
    def __init__(self, x: int, y: int, vx: int, vy: int, color: pygame.Color, radius: int):
        """Initialize an Atom type object.

        :param x: the x position coordinate
        :param y: the y position coordinate
        :param vx: the velocity vector's x coordinate
        :param vy: the velocity vector's y coordinate
        :param color: the color used to mark the atom during the simulation
        :param radius: the radius of the atom
        """
        super().__init__(x, y, vx, vy, color, radius)
        self.bounced = False
        self.distance = 0.0
        self.distance_storage = []

    def store_distance(self):
        """Saves the current distance and resets its counter.

        :return:
        """
        if self.bounced:
            self.distance_storage.append(self.distance)
            self.distance = 0.0
        self.bounced = False

    def update(self, time_step: float):
        """Updates the object's position by its velocity multiplied by *time_step*.

        :param time_step:
        """
        self.x, self.y = self.x + self.vx * time_step, self.y + self.vy * time_step
        self.distance += time_step * (self.vx ** 2 + self.vy ** 2) ** 0.5

    def average_distance(self) -> float:
        """Calculates the average distance that the atom travels.

        :return:
        """
        if len(self.distance_storage) == 0:
            return 0.0
        return sum(self.distance_storage) / len(self.distance_storage)

    def atom_bounce(self, other: Atom, collision_tolerance: int) -> bool:
        """Checks if a collision between two atoms occured and modifies their velocities.

        :param other: an another atom
        :param collision_tolerance:
        :return:
        """
        result = super().atom_bounce(other, collision_tolerance)
        self.bounced = self.bounced or result
        return result


class TextBlock:
    """A class used to create text blocks for :py:mod:`pygame` simulation.

    :ivar text: The actual text that will be displayed.
    :type text: str
    :ivar width: A value that will be displayed must be within range (-10 ^ (*width* - 1), 10 ^ *width*). 0 - disable
    :type width: int
    :ivar precision: the precision of the fraction part of the number
    :type precision: int
    :ivar color: The color that will be applied to the text.
    :type color: :py:class:`pygame.Color`
    :ivar font: The font that will be used to generate the text.
    :type font: :py:class:`pygame.freetype.Font`
    :ivar field:
    :type field: :py:class:`pygame.Rect`
    :ivar p_field: Field with added padding around it.
    :type p_field: :py:class:`pygame.Rect`
    """
    def __init__(self, text: str, width: int, precision: int, color: pygame.Color, font: pygame.freetype.Font,
                 padding: int):
        """Initialize a TextBlock type object

        :param text: The actual text that will be displayed.
        :param width: A value that will be displayed must be within range (-10 ^ (*width* - 1), 10 ^ *width*).
        :param precision: the precision of the fraction part of the number
        :param color: The color that will be applied to the text.
        :param font: The font that will be used to generate the text.
        :param padding: The size of the padding that will be created.
        """
        self.text = text
        self.width = width
        self.precision = precision
        self.color = color
        self.font = font
        self.field = self.gen_rect()
        self.render_point = (0, self.font.get_sized_ascender())
        self.p_field = self.gen_padded_rect(padding)
        self.font.origin = True

    def gen_rect(self) -> pygame.Rect:
        """Generates a field.

        :return:
        """
        if self.width == 0:
            _, rect = self.font.render(f"|{self.text}|", self.color)
        else:
            placeholder = float(10 ** (self.width - 1))
            charr = f"|{self.text}: {placeholder:<{self.width + self.precision + 1}.{self.precision}f}|"
            _, rect = self.font.render(charr, self.color)
        rect.width += rect.x
        rect.height = self.font.get_sized_height()
        return rect

    def gen_padded_rect(self, padding) -> pygame.Rect:
        """Generates a padded field.

        :param padding: The size of the padding that will be created.
        :return:
        """
        p_field = pygame.Rect(self.field)
        p_field.width += 2 * padding
        p_field.height += 2 * padding
        return p_field

    def update_field(self):
        """Centers the field based on the position of padded field."""
        self.field.center = self.p_field.center
        self.render_point = (self.render_point[0] + self.field.x, self.render_point[1] + self.field.y)

    def gen_text(self, surface: pygame.Surface, value: float = 0):
        """Generates a *text* surface.

        :param value: An updated value for an optional number field.
        """
        if self.width == 0:
            self.font.render_to(surface, self.render_point, f"|{self.text}|", self.color)
        elif value >= 10 ** self.width:
            placeholder = float(10 ** self.width - 10 ** -self.precision)
            charr = f"|{self.text}: {placeholder:<{self.width + self.precision + 1}.{self.precision}f}|"
            self.font.render_to(surface, self.render_point, charr, self.color)
        elif value <= -10 ** (self.width - 1):
            placeholder = float(-10 ** (self.width - 1) + 10 ** -self.precision)
            charr = f"|{self.text}: {placeholder:<{self.width + self.precision + 1}.{self.precision}f}|"
            self.font.render_to(surface, self.render_point, charr, self.color)
        else:
            charr = f"|{self.text}: {float(value):<{self.width + self.precision + 1}.{self.precision}f}|"
            self.font.render_to(surface, self.render_point, charr, self.color)


def random_list(n: int, width: int, height: int, v: int,
                atom_radius: int, collision_tolerance: int, atoms: list = None) -> list:
    """Create a list containing *n* randomly generated :py:class:`Atom` objects.

    :param n: number of atoms
    :param width: width of the available space
    :param height: height of the available space
    :param v: velocity will be randomly chosen from <-v, v>
    :param atom_radius:
    :param collision_tolerance:
    :param atoms: New atoms will be added to this list.
    :return: list containing *n* randomly generated :py:class:`Atom` objects
    :raise ValueError: if the container is too small for the chosen number of atoms
    """
    if atoms is None:
        atoms = []
    positions = []
    for i in range(height // (2 * atom_radius + collision_tolerance)):
        for j in range(width // (2 * atom_radius + collision_tolerance)):
            positions.append(
                (i * (2 * atom_radius + collision_tolerance) + atom_radius,
                 j * (2 * atom_radius + collision_tolerance) + atom_radius)
            )

    for atom in atoms:
        for i in range(len(positions)):
            if positions[i] == (atom.x, atom.y):
                del positions[i]
                break

    for _ in range(n):
        if len(positions) == 0:
            raise ValueError("The container is too small for the chosen number of atoms.")
        index = random.randint(0, len(positions) - 1)
        x, y = positions[index]
        del positions[index]
        vx = 0
        vy = 0
        while vx == 0:
            vx = random.randint(-v, v)
        while vy == 0:
            vy = random.randint(-v, v)
        atoms.append(Atom(x, y, vx, vy, pygame.Color(0, 0, 255), atom_radius))
    return atoms


def create_text_blocks(font: pygame.freetype.Font, padding: int) -> dict:
    """Initializes all the text blocks for later use.

    :param font: The font that will be used to generate the texts.
    :param padding: The size of the padding that will be created.
    :return: A dictionary containing :py:class:`TextBlock` objects.
    """
    text_blocks = {
        "title": TextBlock("Dane atomu czerwonego", 0, 0, pygame.Color(0, 0, 0), font, padding),
        "bounces": TextBlock("Ilość odbić", 3, 0, pygame.Color(0, 0, 0), font, padding),
        "average": TextBlock("Średnia droga swobodna", 3, 2, pygame.Color(0, 0, 0), font, padding)
    }
    return text_blocks


def convert_coords(container: pygame.Rect, x: float, y: float) -> (int, int):
    """Converts the given coordinates for a simulation display purposes.

    :param container: the simulation surface
    :param x: the x position coordinate
    :param y: the x position coordinate
    :return: converted coordinates
    """
    y = container.height - y
    return int(x), int(y)


def settings_check(settings: Settings):
    """Checks if all of the necessary keys are present in a settings dictionary.

    :param settings:
    :raise ValueError: if one of the settings is not present
    """
    if settings['h'] is None:
        raise ValueError("The settings file doesn't specify the height of the container.")
    if settings['w'] is None:
        raise ValueError("The settings file doesn't specify the width of the container.")
    if settings['r'] is None:
        raise ValueError("The settings file doesn't specify the atom radius.")
    if settings['v'] is None:
        raise ValueError("The settings file doesn't specify the velocity limit.")
    if settings['c'] is None:
        raise ValueError("The settings file doesn't specify the collision tolerance.")
    if settings['M'] is None:
        raise ValueError("The settings file doesn't specify the M constant.")
    if settings['K'] is None:
        raise ValueError("The settings file doesn't specify the K constant.")
    if settings['N'] is None:
        raise ValueError("The settings file doesn't specify the number of atoms")


def simulate(settings: Settings, graphics: bool):
    """Performs a simulation of atoms in an enclosed container.

    :param settings: Settings file containing all of the necessary options.
    :param graphics: Indicates if the pygame module should be used for graphical representation of the simulation.
    :raise ValueError: if velocity value if equal to 0
    """
    here = os.path.dirname(__file__)

    settings_check(settings)

    # Variables
    with open(os.path.join(here, "VERSION"), 'r') as version_source:
        version = version_source.read()
    width = settings['w'] * settings['r']
    height = settings['h'] * settings['r']
    number_of_atoms = settings["N"]
    time_step = 1 / (max(settings['K'], min(settings['w'], settings['h'])) * settings['v'])
    if settings['v'] == 0:
        raise ValueError("The velocity limit value must be different than 0.")

    # Prepare graphic enviroment if necessary
    if graphics:
        # Pygame variables #1
        pygame.init()
        icon = pygame.image.load(os.path.join(here, "assets/icon.png"))
        pygame.display.set_caption(f"atoms_simulator {version}")
        pygame.display.set_icon(icon)
        font = pygame.freetype.Font(os.path.join(here, "assets/JetBrainsMono-Bold.ttf"), size=25)
        padding = 10
        border_width = 1

        # Arrange the fields
        text_blocks = create_text_blocks(font, padding)
        container = pygame.Rect((0, 0), (width, height))
        p_container = pygame.Rect((0, 0), (width + 2 * padding, height + 2 * padding))
        current = 0
        for text_block in text_blocks.values():
            text_block.p_field.top = p_container.bottom
            text_block.p_field.left = current
            current = text_block.p_field.right
        screen_rect = pygame.Rect((0, 0), (0, 0))
        screen_rect.union_ip(p_container)
        for text_block in text_blocks.values():
            screen_rect.union_ip(text_block.p_field)
            text_block.update_field()
        info_object = pygame.display.Info()
        p_container.centerx = screen_rect.centerx
        container.center = p_container.center
        border_rect = container.inflate(2 * border_width, 2 * border_width)
        if info_object.current_w < screen_rect.width or info_object.current_h < screen_rect.height:
            screen_rect = container

        # Pygame variables #2
        screen = pygame.display.set_mode(screen_rect.bottomright)
        container_surface = pygame.Surface(container.size)

    # Create atoms
    test_atom = TestAtom(settings['r'], settings['r'], random.randint(1, settings['v']),
                         random.randint(1, settings['v']), pygame.Color(255, 0, 0), settings['r'])
    atoms = [test_atom]
    atoms = random_list(number_of_atoms, width, height, settings['v'], settings['r'], settings['c'], atoms=atoms)

    # Start simulation
    turn = 0
    while turn <= settings['M']:
        for i in range(len(atoms)):
            for j in range(i, len(atoms)):
                if i == j:
                    continue
                atoms[i].atom_bounce(atoms[j], settings['c'])
            atoms[i].wall_bounce(width, height, settings['c'])
        test_atom.store_distance()
        if graphics:
            screen.fill(pygame.Color(246, 248, 250))
            container_surface.fill(pygame.Color(250, 251, 252))
            pygame.draw.rect(screen, pygame.Color(225, 228, 232), border_rect, border_width)
            for i in range(number_of_atoms):
                x, y = convert_coords(container, atoms[i].x, atoms[i].y)
                pygame.gfxdraw.filled_circle(container_surface, x, y, atoms[i].radius, atoms[i].color)
                pygame.gfxdraw.aacircle(container_surface, x, y, atoms[i].radius, atoms[i].color)
            screen.blit(container_surface, container)
            text_blocks["title"].gen_text(screen)
            text_blocks["bounces"].gen_text(screen, len(test_atom.distance_storage))
            text_blocks["average"].gen_text(screen, test_atom.average_distance())
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
        for i in range(number_of_atoms):
            atoms[i].update(time_step)
        if settings['M'] > 0:
            turn += 1
    return len(test_atom.distance_storage), test_atom.average_distance()
