import math
import click
import os.path
import shutil
import atoms_simulator
import numpy
import matplotlib.pyplot as plt


def get_project_path():
    return os.path.dirname(os.path.dirname(atoms_simulator.__file__))


def get_path(path):
    i = 1
    while True:
        if not os.path.lexists(f"{path}{i}"):
            return f"{path}{i}"
        i += 1


@click.group()
def ats():
    """Allows to perform detailed tests using atoms_simulator module."""
    pass


@ats.command()
def init():
    """Creates a settings_ats.toml file in the current directory."""
    if not os.path.isfile("settings.toml"):
        source = os.path.join(get_project_path(), "assets/settings_source.toml")
        target = os.path.join(os.getcwd(), "settings_ats.toml")
        shutil.copy(source, target)
        click.echo("Settings file generated successfully.")
    else:
        click.echo("Settings file already exists. Please delete it in order to generate a new configuration file.")


@ats.command()
@click.option("-g", "--graphics", "graphics", help="Turn on pygame simulation", is_flag=True)
@click.option("--no-save", "no_save", help="Disable saving the results of the test.", is_flag=True)
def test(graphics, no_save):
    """Performs a series of tests based on the data in the settings_ats.toml file."""
    settings_ats = atoms_simulator.Settings("settings_ats.toml")
    if not settings_ats.load():
        click.echo("No settings file detected. Generate the file first.")
        return
    if settings_ats["N_min"] is None:
        click.echo("The settings file is corrupted, please generate a new settings file.")
    if settings_ats["N_step"] is None:
        click.echo("The settings file is corrupted, please generate a new settings file.")
    if settings_ats["N_number"] is None:
        click.echo("The settings file is corrupted, please generate a new settings file.")
    if settings_ats["R"] is None:
        click.echo("The settings file is corrupted, please generate a new settings file.")
    n_stop = settings_ats["N_min"] + settings_ats["N_step"] * (settings_ats["N_number"] - 1)
    # size = max([settings_ats['h'], settings_ats['w'], math.ceil((4 * (n_stop + 1)) ** 0.5)])
    # settings_ats['h'] = size
    # settings_ats['w'] = size
    test_cases = [
        [i for _ in range(settings_ats['R'])] for i in range(settings_ats["N_min"], n_stop + 1, settings_ats["N_step"])
    ]
    bounce = numpy.empty((len(test_cases), settings_ats['R']), dtype=int)
    bounce_results = numpy.empty(len(test_cases), dtype=int)
    cop = numpy.empty((len(test_cases), settings_ats['R']), dtype=float)
    cop_results = numpy.empty(len(test_cases), dtype=float)
    settings_ats.new('N', settings_ats["N_min"])
    with click.progressbar(
            range(len(test_cases) * settings_ats['R'] - 1, -1, -1), label="Performing simulations:", show_eta=False
    ) as progress:
        for i in progress:
            settings_ats['N'] = test_cases[i // settings_ats['R']][i % settings_ats['R']]
            try:
                bounce[i // settings_ats['R']][i % settings_ats['R']], \
                cop[i // settings_ats['R']][i % settings_ats['R']] = atoms_simulator.simulate(settings_ats, graphics)
            except ValueError as error:
                click.echo(f"\n{error} Please generate a new settings file.")
                return
            if i % settings_ats['R'] == 0:
                bounce_results[i // settings_ats['R']] = bounce[i // settings_ats['R']].mean()
                cop_results[i // settings_ats['R']] = cop[i // settings_ats['R']].mean()
    if not no_save:
        if not os.path.isdir(results_path := os.path.join(os.getcwd(), "ats_results")):
            os.mkdir(results_path)
        target_path = get_path(os.path.join(results_path, "data_batch"))
        os.mkdir(target_path)
        numpy.savetxt(os.path.join(target_path, "bounces.csv"), bounce_results)
        numpy.savetxt(os.path.join(target_path, "change_of_position.csv"), cop_results)
        settings_ats.save(target=os.path.join(target_path, "used.toml"))


@ats.command()
@click.option("-b", "--data_batch", "data_batch", prompt=True, help="Name of the previously generated data batch.")
def plot(data_batch):
    """Plots the previously generated data."""
    if not os.path.isdir(results_path := os.path.join(os.getcwd(), "ats_results")):
        click.echo(
            "The ats_results catalog doesn't exist within the current working directory. Generate some data first."
        )
    if not os.path.isdir(path := os.path.join(os.getcwd(), "ats_results", data_batch)):
        click.echo(
            f"The ats_results/{data_batch} catalog doesn't exist within the current working directory."
        )
    target_path = get_path(os.path.join(results_path, "figures_batch"))
    os.mkdir(target_path)
    settings_ats = atoms_simulator.Settings(os.path.join(path, "used.toml"))
    if not (settings_ats.load() and os.path.isfile(os.path.join(path, "bounces.csv"))
            and os.path.isfile(os.path.join(path, "change_of_position.csv"))):
        click.echo("This data batch is corrupted.")
        return
    n_stop = settings_ats["N_min"] + settings_ats["N_step"] * (settings_ats["N_number"] - 1)
    x = numpy.arange(settings_ats["N_min"], n_stop + 1, settings_ats["N_step"])
    bounce = numpy.loadtxt(os.path.join(path, "bounces.csv"))
    plt.plot(x, bounce, marker='o')
    plt.title(f"Zależność liczby zderzeń od ilości atomów, M = {settings_ats['M']}")
    plt.xlabel("Liczba atomów w pojemniku")
    plt.ylabel("Liczba odbić atomu czerownego")
    plt.grid(True)
    plt.savefig(os.path.join(target_path, "bounces.png"))
    plt.clf()

    cop = numpy.loadtxt(os.path.join(path, "change_of_position.csv"))
    plt.plot(x, cop, marker='o')
    plt.title(f"Zależność średniej drogi swobodnej od ilości atomów, M = {settings_ats['M']}")
    plt.xlabel("Liczba atomów w pojemniku")
    plt.ylabel("Średnia droga swobodna atomu czerwonego")
    plt.grid(True)
    plt.savefig(os.path.join(target_path, "change_of_position.png"))
    plt.clf()

    settings_ats.save(os.path.join(target_path, "used.toml"))
    click.echo("Figures created successfullly.")
