"""Process the command line variables for the ``explorant`` program."""
# -------------------------------------------------------------------------------
# Version info
# -------------------------------------------------------------------------------
__version__ = "2023-04-12"
# 2023-04-12    Added version argument
# 2020-05-01    Added: vhu, no command line variable defined
# 2020-04-23    Create() and Get() removed because it is weard
# 2020-04-20    Added: -S -V
# 2020-03-04    Command-line variables with values printed when debugging
# 2020-02-18    -s added
# 2020-01-29    first version
# -------------------------------------------------------------------------------
import argparse

from fortius_ant import debug, logfile


# -------------------------------------------------------------------------------
# E x p l o r   A N T   -   C o m m a n d L i n e V a r i a b l e s
# -------------------------------------------------------------------------------
class CommandLineVariables:  # noqa PLR902 PLR903
    """A wrapper for the command line variables set when running the program."""

    args = None

    autostart = False
    debug = 0
    dongle = -1
    hrm = -1  # Heart rate monitor
    fe = -1  # Fitness equipment
    scs = -1  # Speed and cadence sensor
    vtx = -1  # i-Vortex
    vhu = -1  # i-Vortex Headunit
    SimulateTrainer = False

    # ---------------------------------------------------------------------------
    # Define and process command line
    # ---------------------------------------------------------------------------
    def __init__(self):
        """Initialize parser."""
        # -----------------------------------------------------------------------
        # Define and process command line
        # -----------------------------------------------------------------------
        parser = argparse.ArgumentParser(
            description="Program to explore ANT devices in the system"
        )
        parser.add_argument(
            "-a",
            "--autostart",
            help="Automatically start",
            required=False,
            action="store_true",
        )
        parser.add_argument(
            "-d", "--debug", help="Show debugging data", required=False, default=False
        )
        parser.add_argument(
            "-s",
            "--simulate",
            help="Simulate master HRM and FE-C",
            required=False,
            action="store_true",
        )
        parser.add_argument(
            "-D", "--dongle", help="Use this ANT dongle", required=False, default=False
        )
        parser.add_argument(
            "-H",
            "--hrm",
            help="Pair with this Heart Rate Monitor",
            required=False,
            default=False,
        )
        parser.add_argument(
            "-F",
            "--fe",
            help="Pair with this Fitness Equipment",
            required=False,
            default=False,
        )
        parser.add_argument(
            "-S",
            "--scs",
            help="Pair with this Speed Cadence Sensor",
            required=False,
            default=False,
        )
        parser.add_argument(
            "-V",
            "--vtx",
            help="Pair with this Tacx i-Vortex trainer",
            required=False,
            default=False,
        )
        parser.add_argument(
            "-v",
            "--version",
            help="Get version",
            required=False,
            default=False,
            action="store_true",
        )
        args = parser.parse_args()
        self.args = args

        # -----------------------------------------------------------------------
        # Booleans; either True or False
        # -----------------------------------------------------------------------
        self.autostart = args.autostart
        self.SimulateTrainer = args.simulate
        self.version = args.version

        # -----------------------------------------------------------------------
        # Get debug-flags, used in debug module
        # -----------------------------------------------------------------------
        if args.debug:
            try:
                self.debug = int(args.debug)
            except ValueError:
                logfile.Console(
                    f"Command line error; -d incorrect debugging flags={args.debug}"
                )

        # -----------------------------------------------------------------------
        # Get ANTdongle
        # -----------------------------------------------------------------------
        if args.dongle:
            try:
                self.dongle = int(args.dongle)
            except ValueError:
                logfile.Console(
                    f"Command line error; -D incorrect dongle={args.dongle}"
                )
        # -----------------------------------------------------------------------
        # Get HRM
        # -----------------------------------------------------------------------
        if args.hrm:
            try:
                self.hrm = int(args.hrm)
            except ValueError:
                logfile.Console(f"Command line error; -H incorrect HRM={args.hrm}")
        # -----------------------------------------------------------------------
        # Get FE
        # -----------------------------------------------------------------------
        if args.fe:
            try:
                self.fe = int(args.fe)
            except ValueError:
                logfile.Console(
                    f"Command line error; -F incorrect Fitness Equipment={args.fe}"
                )

        # -----------------------------------------------------------------------
        # Get SCS
        # -----------------------------------------------------------------------
        if args.scs:
            try:
                self.scs = int(args.scs)
            except ValueError:
                logfile.Console(
                    f"Command line error; -S incorrect Speed Cadence Sensor={args.scs}"
                )

        # -----------------------------------------------------------------------
        # Get VTX
        # -----------------------------------------------------------------------
        if args.vtx:
            try:
                self.vtx = int(args.vtx)
            except ValueError:
                logfile.Console(
                    f"Command line error; -V incorrect Tacx i-Vortex={args.vtx}"
                )

    def print(self):
        """Print command line variables to console."""
        try:
            v = debug.on(
                debug.Any
            )  # Verbose: print all command-line variables with values
            if self.autostart:
                logfile.Console("-a")
            if self.SimulateTrainer:
                logfile.Console("-s")
            if v or self.args.debug:
                logfile.Console(f"-d {self.debug} ({bin(self.debug)})")
            if v or self.args.dongle:
                logfile.Console(f"-D {self.dongle} ({hex(self.dongle)})")
            if v or self.args.hrm:
                logfile.Console(f"-H {self.hrm} ({hex(self.hrm)})")
            if v or self.args.fe:
                logfile.Console(f"-F {self.fe} ({hex(self.fe)})")
            if v or self.args.scs:
                logfile.Console(f"-S {self.scs} ({hex(self.scs)})")
            if v or self.args.vtx:
                logfile.Console(f"-V {self.vtx} ({hex(self.vtx)})")
        except ValueError:
            pass  # May occur when incorrect command line parameters, error given before


# -------------------------------------------------------------------------------
# Main program to test the previous functions
# -------------------------------------------------------------------------------
if __name__ == "__main__":
    clv = CommandLineVariables()
    clv.print()
