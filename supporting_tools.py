########################################################################################################################
# M O D U L E   D O C U M E N T A T I O N : ############################################################################
########################################################################################################################


"""
This module contains templates for various notifications and
 supporting functions.

This module provides classes for convenient output of notifications,
 errors and special information, marking where the notification is coming from.
 Also, module contains implementations of auxiliary functions,
 that are often used in other modules.

Functions:
    extract_parameter_sequence: Extract arguments from the row in .csv file.

Classes:
    Notification: For printing notifications.
    Error: For printing errors.
"""

########################################################################################################################
# I M P O R T :  #######################################################################################################
########################################################################################################################


import colorama
import kmc_ising
import datetime


########################################################################################################################
# S P E C I A L   C H A R A C T E R S :  ###############################################################################
########################################################################################################################


UNDERLINE_ON = '\u001b[4m'
UNDERLINE_OFF = '\u001b[0m'
GREEN = colorama.Fore.LIGHTGREEN_EX
RED = colorama.Fore.LIGHTRED_EX
RESET = colorama.Style.RESET_ALL
YELLOW = colorama.Fore.LIGHTYELLOW_EX


########################################################################################################################
# S U P P O R T I N G   T O O L   F U N C T I O N :  ###################################################################
########################################################################################################################


def extract_parameter_sequence(filename):
    """
    Extract arguments from the row in .csv file.
    """
    param_dict = {}
    counter = 0
    # Splitting .csv file: ---------------------------------------------------------------------------------------------
    for row in open(filename, newline='\n'):
        counter += 1
        row = row[:-1].split(',')
    # ------------------------------------------------------------------------------------------------------------------
        try:
            # The row number: ------------------------------------------------------------------------------------------
            param_dict['#'] = counter
            # ----------------------------------------------------------------------------------------------------------

            # Model parameters: ----------------------------------------------------------------------------------------
            param_dict['J'] = float(row[0])
            param_dict['B'] = float(row[1])
            param_dict['N'] = int(row[2])
            param_dict['S'] = row[3:]
            # ----------------------------------------------------------------------------------------------------------
        except IndexError:  # If wrong format of the row
            yield counter
        else:
            yield param_dict


########################################################################################################################
# S U P P O R T I N G   C L A S S :  ###################################################################################
########################################################################################################################


class Notification:
    """
    Class for printing notifications.

    Args:
        self._string: Notification string.
        self._task_end: Notification about task ending.
        self._for_verbose: If notification for verbose mode only.
        self._time: Current time.
    """

    # ==================================================================================================================

    def __init__(self, where='unknown', what='unknown', task_end=False, for_verbose=False):
        if for_verbose:
            self._COLOR = YELLOW
        else:
            self._COLOR = GREEN
        self._time = None
        self._string = ('\n' + f'{UNDERLINE_ON} {UNDERLINE_OFF}' * 40 +
                        f'\n{self._COLOR}{UNDERLINE_ON}NOTIFICATION{UNDERLINE_OFF}{RESET}' +
                        ' |{TIME}| :' +
                        f'\n\n\t{UNDERLINE_ON}Where?{UNDERLINE_OFF}: %s' % where +
                        f'\n\t{UNDERLINE_ON}What?{UNDERLINE_OFF}: %s' % what +
                        f'\n\t{UNDERLINE_ON}Task end?{UNDERLINE_OFF}: %s ' % task_end +
                        '\n' + f'{UNDERLINE_ON} {UNDERLINE_OFF}' * 40 + '\n')
        self._task_end = task_end
        self._for_verbose = for_verbose

    # ==================================================================================================================

    @property
    def for_verbose(self):
        """
        Check if notification for verbose mode only.
        """
        return self._for_verbose

    # ==================================================================================================================

    @property
    def task_end(self):
        """
        Notification about task ending.
        """
        return self._task_end

    # ==================================================================================================================

    def output(self):
        """
        Print notification string.
        """
        print(self._string)

    # ==================================================================================================================

    def __call__(self):
        """
        Send to the notification handler.
        """

        # Set current time: --------------------------------------------------------------------------------------------
        self._time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        self._string = self._string.format(TIME=self._time)
        # --------------------------------------------------------------------------------------------------------------
        kmc_ising.core.Core().print_notification(self)

    # ==================================================================================================================

########################################################################################################################
# S U P P O R T I N G   C L A S S :  ###################################################################################
########################################################################################################################


class Error(Notification):
    """
    Class for printing errors.

    Args:
        self._string: Error string.
        self._for_verbose: Always False.
        self._fatal: If need to terminate notification handler.
    """

    # ==================================================================================================================

    def __init__(self, where='unknown', why='unknown', fatal=False, task_end=False):
        super().__init__(task_end=task_end)
        self._string = ('\n' + f'{UNDERLINE_ON} {UNDERLINE_OFF}' * 40 +
                        f'\n{RED}{UNDERLINE_ON}ERROR{UNDERLINE_OFF}{RESET}' +
                        ' |{TIME}| :' +
                        f'\n\n\t{UNDERLINE_ON}Where?{UNDERLINE_OFF}: %s' % where +
                        f'\n\t{UNDERLINE_ON}Why?{UNDERLINE_OFF}: %s' % why +
                        f'\n\t{UNDERLINE_ON}Fatal?{UNDERLINE_OFF}: %s ' % fatal +
                        f'\n\t{UNDERLINE_ON}Task end?{UNDERLINE_OFF}: %s ' % task_end +
                        '\n\n' + f'{UNDERLINE_ON} {UNDERLINE_OFF}' * 40 + '\n')
        self._fatal = fatal

    # ==================================================================================================================

    def output(self):
        """
        Print error string.
        """
        print(self._string)
        if self._fatal:
            exit(1)  # Exit from notification handler if error is fatal

    # ==================================================================================================================


########################################################################################################################
# E N D   O F   F I L E .  #############################################################################################
########################################################################################################################
