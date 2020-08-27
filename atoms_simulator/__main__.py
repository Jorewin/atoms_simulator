import atoms_simulator as ats
import os.path


if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(__file__))
    settings = ats.Settings(os.path.join(here, "settings.toml"))
    if not settings.load():
        settings.tags = {
            'h': 20,
            'w': 20,
            'r': 30,
            'v': 3,
            'c': 3,
            'M': 0,
            'K': 20,
            'N': 8
        }
        settings.save()
    ats.simulate(settings, True)