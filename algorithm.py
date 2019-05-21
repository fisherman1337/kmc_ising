########################################################################################################################
# M O D U L E   D O C U M E N T A T I O N : ############################################################################
########################################################################################################################

"""
This module implements the kMC algorithm for modeling a one-dimensional Ising chain.

Classes:
    KmcIsing: Implementation of the algorithm.
"""

########################################################################################################################
# I M P O R T :  #######################################################################################################
########################################################################################################################


import multiprocessing
import random
import math
from kmc_ising.supporting_tools import Notification
from kmc_ising.supporting_tools import Error


########################################################################################################################
# M A I N   C L A S S :  ###############################################################################################
########################################################################################################################


class KmcIsing(multiprocessing.Process):
    """"
    Implementation of the algorithm.

    This class implements the kMC algorithm for modeling a one-dimensional Ising chain
     and allows to model several rows of arguments in the separate processes.

    Attributes:
        self._kwargs: Task parameters.
        self_steps: Model parameter.
        self._state: Model parameter.
        self._partial_sums: Model parameter.
        self._r: Model parameter.
        self._p: Model parameter.
        self._delta_t: Model parameter.
        self._chosen_molecule: Model parameter.
        self._t: Model parameter.

    """
    # ==================================================================================================================

    __class_path = "kmc_Ising.algorithm.KmcIsing"

    # ==================================================================================================================

    def __init__(self, filename, **kwargs):
        super().__init__()
        # Attributes bounded with tasks execution: ---------------------------------------------------------------------
        self._kwargs = kwargs
        self._steps = 10 * kwargs.get('N')
        self._state = []
        self._partial_sums = []
        self._r = None
        self._p = None
        self._delta_t = None
        self._chosen_molecule = None
        self._t = None
        # --------------------------------------------------------------------------------------------------------------

        # Attributes bounded with supporting goals: --------------------------------------------------------------------
        self.daemon = True  # Process's attribute
        self._filename = filename
        # --------------------------------------------------------------------------------------------------------------

    # ==================================================================================================================

    def run(self):
        """
        Count model in separate process.
        """
        self._generate_state()
        self._count_partial_sums()
        self._count_r()
        for i in range(self._steps):
            self._generate_p()
            self._count_delta_t()
            self._choose_molecule()
            self._add_delta_t()
        print(self._delta_t)

        # Send notification to the notification handler: ---------------------------------------------------------------
        Notification(where=f'{self.__class_path}.run()',
                     what=f"""row number "{self._kwargs.get('#')}" in file "{self._filename}" is simulated""",
                     task_end=True,
                     for_verbose=True)()
        # --------------------------------------------------------------------------------------------------------------

    # ==================================================================================================================

    def _generate_state(self):
        """
        Generate the initial state.
        """

        # If 'random' was passed: --------------------------------------------------------------------------------------
        if self._kwargs.get('S')[0] == 'random':
            for i in range(int(self._kwargs.get('N'))):
                bit = random.getrandbits(1)
                if bit == 0:
                    self._state.append(-1)
                else:
                    self._state.append(1)
        # --------------------------------------------------------------------------------------------------------------

        # If 'uniform' was passed: -------------------------------------------------------------------------------------
        elif self._kwargs.get('S')[0] == 'uniform':
            for i in range(int(self._kwargs.get('N'))):
                if self._kwargs.get('B') > 0:
                    self._state.append(1)
                elif self._kwargs.get('B') < 0:
                    self._state.append(-1)
        # --------------------------------------------------------------------------------------------------------------

        # If spin sequence was passed: ---------------------------------------------------------------------------------
        else:
            self._state = [int(x) for x in self._kwargs.get('S')]
            if len(self._state) != int(self._kwargs.get('N')):
                # If wrong N in file: ----------------------------------------------------------------------------------
                Error(where=f'{self.__class_path}._generate_model()',
                      why=f"""number of sequence elements is not equal to N in row number "{self._kwargs.get('#')}" 
                          in file "{self._filename}" """,
                      task_end=True)()
                exit(1)
                # ------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

    # ==================================================================================================================

    def _count_partial_sums(self):
        """
        Count sequence of the partial sums.
        """
        for i in range(len(self._state)):
            # Partial sum for the first molecule: ----------------------------------------------------------------------
            if i == 0:
                u_ikt = (-self._kwargs.get('J')/2*(self._state[0]*self._state[-1] +
                         self._state[0]*self._state[1])-self._state[0]*self._kwargs.get('B'))
                self._partial_sums.append(math.exp(u_ikt))
            # ----------------------------------------------------------------------------------------------------------

            # Partial sum for the last molecule: -----------------------------------------------------------------------
            elif i == len(self._state)-1:
                u_ikt = (-self._kwargs.get('J') / 2 * (self._state[-1] * self._state[-2] +
                         self._state[-1] * self._state[0]) - self._state[-1] * self._kwargs.get('B'))
                self._partial_sums.append(math.exp(u_ikt) + self._partial_sums[i-1])
            # ----------------------------------------------------------------------------------------------------------

            # Partial sum for other molecules: -------------------------------------------------------------------------
            else:
                u_ikt = (-self._kwargs.get('J') / 2 * (self._state[i] * self._state[i - 1] +
                         self._state[i] * self._state[i + 1]) - self._state[i] * self._kwargs.get('B'))
                self._partial_sums.append(math.exp(u_ikt) + self._partial_sums[i-1])
            # ----------------------------------------------------------------------------------------------------------

    # ==================================================================================================================

    def _count_r(self):
        """
        Model parameter counting.
        """
        self._r = self._partial_sums[-1]

    # ==================================================================================================================

    def _generate_p(self):
        """
        Model parameter counting.
        """
        self._p = random.uniform(0, 1)

    # ==================================================================================================================

    def _count_delta_t(self):
        """
        Model parameter counting.
        """
        self._delta_t = 1/self._r * math.floor(math.log(1/self._p))

    # ==================================================================================================================

    def _choose_molecule(self):
        """
        Choose a random molecule.
        """
        for i in range(len(self._partial_sums)):
            if i == 0 and self._p * self._r < self._partial_sums[i]:
                self._chosen_molecule = 0
            elif self._partial_sums[i - 1] <= self._p * self._r < self._partial_sums[i]:
                self._chosen_molecule = i

    # ==================================================================================================================

    def _add_delta_t(self):
        """
        Model parameter counting.
        """
        if self._t is None:
            self._t = 0
        self._t += self._delta_t

    # ==================================================================================================================

########################################################################################################################
# E N D   O F   F I L E .  #############################################################################################
########################################################################################################################
