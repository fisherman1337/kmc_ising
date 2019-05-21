########################################################################################################################
# M O D U L E   D O C U M E N T A T I O N : ############################################################################
########################################################################################################################


"""
Control module of "kmc_ising".

This module provides execution of modelling for each row in the separate
 processes and synchronized output in the terminal.

Classes:
    Core: The main control class.
"""


########################################################################################################################
# I M P O R T :  #######################################################################################################
########################################################################################################################


import singleton_decorator
import multiprocessing
import threading
import kmc_ising
import os
from kmc_ising.supporting_tools import Notification
from kmc_ising.supporting_tools import Error
from kmc_ising.supporting_tools import extract_parameter_sequence


########################################################################################################################
# M A I N   C L A S S :  ###############################################################################################
####################################################
# ###################################################################


@singleton_decorator.singleton
class Core:
    """
    The main control class.

    This class provides execution of the tasks in the separate processes and
     synchronized output in the terminal.

    Attributes:
        self._kwargs: Arguments from the terminal.
        self._manager: The Manager for synchronization.
        self._queue: The queue for notifications and errors.
        self._notification_event: Event of new notification.
        self._notification_thread: The thread for notification handling.
        self._process_counter: Process counter for checking if it is > CPU_COUNT .
        self._process_counter_event: Event that is set when process_counter < CPU_COUNT
    """

    # ==================================================================================================================

    __CPU_COUNT = multiprocessing.cpu_count()
    __class_path = 'kmc_ising.core.Core'

    # ==================================================================================================================

    def __init__(self, **kwargs):
        # Attributes bounded with tasks execution: ---------------------------------------------------------------------
        self._kwargs = kwargs
        # --------------------------------------------------------------------------------------------------------------

        # Attributes bounded with notification handler: ----------------------------------------------------------------
        self._manager = multiprocessing.Manager()
        self._notification_queue = self._manager.list()
        self._notification_event = self._manager.Event()
        self._process_counter_event = self._manager.Event()
        self._notification_thread = threading.Thread(target=self._notification_handler)
        self._process_counter = multiprocessing.Value('i', 0)  # Synchronized value
        # --------------------------------------------------------------------------------------------------------------

    # ==================================================================================================================

    @property
    def verbose_mode(self):
        """
        Getter for "-v" flag.
        """
        return self._kwargs.get('v')

    # ==================================================================================================================

    @property
    def filename(self):
        """
        Getter for terminal argument.
        """
        return self._kwargs.get('filename')

    # ==================================================================================================================

    @property
    def _next_notification(self):
        """
        Get notification or error instance from the notification queue.
        """

        # Check if notification queue is empty: ------------------------------------------------------------------------
        try:
            notification = self._notification_queue.pop(0)
        # --------------------------------------------------------------------------------------------------------------

        # If it is - unset notification event and return None: ---------------------------------------------------------
        except IndexError:
            self._notification_event.clear()
            return None
        # --------------------------------------------------------------------------------------------------------------
        else:
            return notification

    # ==================================================================================================================

    def start(self):
        """
        Start tasks executing in the separate processes.
        """
        # Start notification handler in the separate thread: -----------------------------------------------------------
        self._process_counter.value += 1  # Notification handler consider as one of the tasks
        self._notification_thread.start()
        # --------------------------------------------------------------------------------------------------------------
        try:
            open(self.filename)
        except FileNotFoundError:
            # If can't open .csv file: ---------------------------------------------------------------------------------
            Error(where=f'{self.__class_path}.start()',
                  why=f"""can't open .csv file: "{self.filename}" """,
                  fatal=True)()
            # ----------------------------------------------------------------------------------------------------------
        else:
            if os.stat(self.filename).st_size == 0:
                # If .csv file is empty: -------------------------------------------------------------------------------
                Error(where=f'{self.__class_path}.start()',
                      why=f""".csv file : "{self.filename}" is empty """,
                      fatal=True)()
                # ------------------------------------------------------------------------------------------------------
            # If temperature plotting mode is off: ---------------------------------------------------------------------
            self._process_counter_event.set()
            for param_dict in extract_parameter_sequence(self.filename):
                if self._process_counter.value <= self.__CPU_COUNT:
                    self._process_counter.value += 1
                    if param_dict.__class__ is not dict:
                        # If row in .csv file has wrong format: --------------------------------------------------------
                        Error(where=f'{self.__class_path}.start()',
                              why=f"""row number "{param_dict}" in file "{self.filename}" has wrong format """,
                              task_end=True)()
                        # ----------------------------------------------------------------------------------------------
                    else:
                        process = kmc_ising.algorithm.KmcIsing(self.filename, **param_dict)
                        process.start()
                else:
                    # Waiting when process_counter <= CPU_COUNT: -------------------------------------------------------
                    self._process_counter_event.clear()
                    self._process_counter_event.wait()
                    # --------------------------------------------------------------------------------------------------

            # Send notification to the notification handler: -----------------------------------------------------------
            Notification(where=f'{self.__class_path}.start()',
                         what='all processes are started',
                         task_end=True,
                         for_verbose=True)()
            # ----------------------------------------------------------------------------------------------------------

    # ==================================================================================================================

    def _notification_handler(self):
        """
        This loop handles notifications and errors from queue.
        """
        while self._process_counter.value != 0:  # Endless loop, while not all tasks are finished
            # Waiting for new notification: ----------------------------------------------------------------------------
            self._notification_event.wait()
            # ----------------------------------------------------------------------------------------------------------

            # Print new notification: ----------------------------------------------------------------------------------
            notification = self._next_notification
            if notification is None:
                continue
            else:
                # Check if the notification is for verbose mode only: --------------------------------------------------
                if self.verbose_mode:
                    notification.output()
                elif not notification.for_verbose:
                    notification.output()
                # ------------------------------------------------------------------------------------------------------

                # Subtract 1 from the task counter if the task finished: -----------------------------------------------
                if notification.task_end:
                    self._process_counter.value += -1
                    # Check process counter: ---------------------------------------------------------------------------
                    if self._process_counter.value <= 4:
                        self._process_counter_event.set()
                    # --------------------------------------------------------------------------------------------------
                # ------------------------------------------------------------------------------------------------------
            # ----------------------------------------------------------------------------------------------------------

    # ==================================================================================================================

    def print_notification(self, notification):
        """
        Send notification or error instance to the notification queue.
        """
        self._notification_queue.append(notification)
        self._notification_event.set()

    # ==================================================================================================================


########################################################################################################################
# E N D   O F   F I L E .  #############################################################################################
########################################################################################################################
