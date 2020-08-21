import click
import os.path
import shutil
import atoms_simulator


def get_project_path():
    return os.path.dirname(os.path.dirname(atoms_simulator.__file__))


def get_path(name):
    i = 1
    while True:
        if result := os.path.isdir(os.path.join(os.getcwd(), f"{name}{i}")):
            return result
        i += 1



@click.group()
@click.pass_context
def ats(ctx):
    """Allows to perform detailed tests using atoms_simulator module."""
    if ctx.invoked_subcommand != "init" and not os.path.isfile(os.path.join(os.getcwd(), "settings_ats.toml")):
        click.echo("No settings file detected. Generate the file first.")


@ats.command()
def init():
    """Creates a settings_ats.toml file in the current directory."""
    if not os.path.isfile("settings.toml"):
        source = os.path.join(get_project_path(), "assets/settings_source.toml")
        target = os.path.join(os.getcwd(), "settings_ats.toml")
        shutil.copy(source, target)


@ats.command()
@click.option("-g", "--graphics", "graphics", help="Turn on pygame simulation", is_flag=True)
def test(graphics):
    """Performs a series of tests based on the data in the settings_ats.toml file."""
    settings_ats = atoms_simulator.Settings("settings_ats.toml")
    settings_ats.load()
    n_stop = settings_ats['N'] + settings_ats["N_step"] * (settings_ats["N_number"] - 1)
    size = max(settings_ats['h'], settings_ats['w'], (4 * n_stop) ** 0.5)
    settings_ats['h'] = size
    settings_ats['w'] = size


@ats.command()
def dummy():
    pass