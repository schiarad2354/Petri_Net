import os
import subprocess
from contextlib import suppress
from multiprocessing import Pool

from SIRModelSBML import SIRModelSBML

class RunThroughSpike:
    def __init__(self, spike_file_path, continuous=True, stochastic=False):
        """
        Initializes the RunThroughSpike class with the given parameters.

        Args:
            spike_file_path (str): The path to the spike file.
            continuous (bool): Flag to determine if the continuous simulator should be used.
            stochastic (bool): Flag to determine if the stochastic simulator should be used.
        """
        self.spike_file_path = spike_file_path
        self.continuous = continuous
        self.stochastic = stochastic
        self.model = SIRModelSBML()
        
        # Check if both continuous and stochastic are True or both are False
        if (self.continuous and self.stochastic) or (not self.continuous and not self.stochastic):
            raise ValueError("RunThroughSpike: can only choose continuous or stochastic Petri Net simulator, not both or neither.")
        
        # Run the appropriate Spike simulation
        self.run_spike_simulation()
    
    def run_spike_simulation(self):
        """
        Executes the Spike Petri Net simulator based on the given mode.
        """
        if self.continuous:
            try:
                # Execute the Spike command for continuous simulation
                command = "spike exe -f=continuous.spc"
                subprocess.run(command, shell=True)
            except Exception as e:
                print("RunThroughSpike: cannot find SBML/ANDL files. Error:", e)
                return None
        
        elif self.stochastic:
            try:
                # Execute the Spike command for stochastic simulation
                command = "spike exe -f=stochastic.spc"
                subprocess.run(command, shell=True)
            except Exception as e:
                print("RunThroughSpike: cannot find SBML/ANDL files. Error:", e)
                return None

# Example usage:
# spike_runner = RunThroughSpike("path/to/spike_file", continuous=True, stochastic=False)
