import numpy as np
import pandas as pd
from itertools import product

from InfLayers import InfLayers

class HyperParameters:
    def __init__(self, beta_values, gamma_values, delta_values, time_steps, num_patches, start_noise_at=None, noise_mean=0, noise_std=0.1):
        """
        Purpose:
        Initializes the CombinedParameters object with given values.
        
        Inputs:
        - beta_values: DataFrame containing beta tensors
        - gamma_values: DataFrame containing gamma tensors
        - delta_values: DataFrame containing delta tensors
        - time_steps: Integer representing the number of time steps
        - num_patches: Integer representing the number of patches and their associated ids for callback
        - start_noise_at: Optional integer indicating starting time step for noise addition
        - noise_mean: Mean of noise (default: 0)
        - noise_std: Standard deviation of noise (default: 0.1)
        
        Outputs:
        None
        """
        self.beta_values = beta_values
        self.gamma_values = gamma_values
        self.delta_values = delta_values
        self.time_steps = time_steps
        self.num_patches = num_patches
        self.start_noise_at = start_noise_at
        self.noise_mean = noise_mean
        self.noise_std = noise_std

    def parameter_product_space(self, values):
        """
        Purpose:
        Generate all combinations of parameter values across patches.
        
        Inputs:
        - values: List of parameter values
        
        Outputs:
        Numpy array representing the parameter space across patches.
        """
        combinations = list(product(values, repeat=self.num_patches))
        tensor_shape = (len(combinations), self.num_patches)
        tensor = np.empty(tensor_shape)

        for i, combination in enumerate(combinations):
            tensor[i, :] = combination

        return tensor

    def generate_tensor(self, parameter_values):
        """
        Purpose:
        Generate tensors for given parameter values over time steps, optionally adding noise.
        
        Inputs:
        - parameter_values: List of parameter values
        
        Outputs:
        List of numpy arrays representing tensors for each time step.
        """
        tensors = []
        for t in self.time_steps:
            combinations = list(product(parameter_values, repeat=self.num_patches))
            tensor_shape = (len(combinations), self.num_patches)
            tensor = np.empty(tensor_shape)

            for i, combination in enumerate(combinations):
                if self.start_noise_at is not None and t >= self.start_noise_at:
                    noisy_combination = abs(np.array(combination) + np.random.normal(self.noise_mean, self.noise_std, self.num_patches))
                    tensor[i, :] = noisy_combination
                else:
                    tensor[i, :] = combination

            tensors.append(tensor)
        return tensors

    def save_tensor_as_csv(self, df, filename):
        """
        Purpose:
        Save tensor dataframes to CSV file.
        
        Inputs:
        - df: DataFrame to save
        - filename: Name of the CSV file to save as
        
        Outputs:
        None
        """
        df.to_csv(filename, index=False)

    def save_tensor(self, tensor):
        """
        Purpose:
        Transform tensor into DataFrame with time steps and instance IDs.
        
        Inputs:
        - tensor: Numpy array of tensor data
        
        Outputs:
        DataFrame with columns for patch IDs, time steps, and instance IDs.
        """
        tensor_reshaped = tensor.reshape(-1, self.num_patches)
        df = pd.DataFrame(tensor_reshaped, columns=[f'Patch_{j+1}' for j in range(self.num_patches)])
        rows_per_step = tensor_reshaped.shape[0] // len(self.time_steps)
        df['Time_Step'] = np.repeat(self.time_steps, len(tensor_reshaped) // len(self.time_steps))
        df['id'] = np.tile(np.arange(0, rows_per_step), len(self.time_steps))

        return df

    def generate_and_save_tensors(self, global_param_change=False, save_csv=True):
        """
        Purpose:
        Generate tensors for beta, gamma, and delta values over time steps and optionally save them as CSV files.
        
        Inputs:
        - global_param_change: Boolean flag indicating whether to use global parameter change
        - save_csv: Boolean flag indicating whether to save output as CSV files
        
        Outputs:
        DataFrames containing beta, gamma, and delta tensors.
        """
        beta_tensors = []
        gamma_tensors = []
        delta_tensors = []

        for t in self.time_steps:
            if self.start_noise_at is not None and t >= self.start_noise_at:
                noisy_beta_values = [abs(beta + np.random.normal(self.noise_mean, self.noise_std) * (t - self.start_noise_at + 1)) for beta in self.beta_values]
                noisy_gamma_values = [abs(gamma + np.random.normal(self.noise_mean, self.noise_std) * (t - self.start_noise_at + 1)) for gamma in self.gamma_values]
                noisy_delta_values = [abs(delta + np.random.normal(self.noise_mean, self.noise_std) * (t - self.start_noise_at + 1)) for delta in self.delta_values]
            else:
                noisy_beta_values = self.beta_values
                noisy_gamma_values = self.gamma_values
                noisy_delta_values = self.delta_values

            if global_param_change:
                beta_tensor = self.generate_tensor(noisy_beta_values)
                gamma_tensor = self.generate_tensor(noisy_gamma_values)
                delta_tensor = self.generate_tensor(noisy_delta_values)
            else:
                beta_tensor = self.parameter_product_space(noisy_beta_values)
                gamma_tensor = self.parameter_product_space(noisy_gamma_values)
                delta_tensor = self.parameter_product_space(noisy_delta_values)

            beta_tensors.append(beta_tensor)
            gamma_tensors.append(gamma_tensor)
            delta_tensors.append(delta_tensor)
            
        beta_tensors_df = self.save_tensor(np.concatenate(beta_tensors))
        gamma_tensors_df = self.save_tensor(np.concatenate(gamma_tensors))
        delta_tensors_df = self.save_tensor(np.concatenate(delta_tensors))

        if save_csv:
            self.save_tensor_as_csv(beta_tensors_df, 'beta_tensors.csv')
            self.save_tensor_as_csv(gamma_tensors_df, 'gamma_tensors.csv')
            self.save_tensor_as_csv(delta_tensors_df, 'delta_tensors.csv')

        return beta_tensors_df, gamma_tensors_df, delta_tensors_df
    
    def generate_dataframe(self):
        beta_gamma_delta_list = []

        for time_step in range(1, self.time_steps+1):  
            concatenated_df = pd.merge(self.beta_tensors[self.beta_tensors['Time_Step'] == time_step].assign(key=0),
                                        self.gamma_tensors[self.gamma_tensors['Time_Step'] == time_step].assign(key=0),
                                        on='key').merge(self.delta_tensors[self.delta_tensors['Time_Step'] == time_step].assign(key=0),
                                                      on='key').drop('key', axis=1)

            concatenated_df['Configuration_id'] = range(len(concatenated_df))

            beta_gamma_delta_list.append(concatenated_df)

        beta_gamma_delta = pd.concat(beta_gamma_delta_list, ignore_index=True)

        patches = [col for col in self.beta_tensors.columns if col.startswith('Patch_')]

        for patch in patches:
            beta_gamma_delta[f'Beta_{patch}'] = beta_gamma_delta[f'{patch}_x']
            beta_gamma_delta[f'Gamma_{patch}'] = beta_gamma_delta[f'{patch}_y']
            beta_gamma_delta[f'Delta_{patch}'] = beta_gamma_delta[patch]

        beta_gamma_delta = beta_gamma_delta.drop([f'{patch}_x' for patch in patches] + [f'{patch}_y' for patch in patches] + patches, axis=1)

        return beta_gamma_delta

    
    
    
    
    
    
# INPUTS/INITIALIZATIONS
# Given beta, gamma, and delta values, time steps, and other hyperparameters
# beta_values = [0.1, 0.2]
# gamma_values = [0.5, 0.2, 0.4]
# delta_values = [0.6,0.7]

#beta_values = np.linspace(0, 1, 10)
#gamma_values = [0.2]
#delta_values = [0.1, 0.2]

#time = 3 # this is the outside loop of the petri net, so this is the various time scales e.g. day, month, week etc. Note: should correspond with the parameters
#time_steps = [i for i in range(1, time + 1)] # time steps 

#start_noise_at = None  # Add noise to the parameter values starting at a time step e.g. 2

#num_patches = 4 # Number of patches of interest

## Call functions for outputs
#hyper_params = HyperParameters(beta_values, gamma_values, delta_values, time_steps, num_patches, start_noise_at=start_noise_at)
#beta_tensors, gamma_tensors, delta_tensors = hyper_params.generate_and_save_tensors(global_param_change=False, save_csv=False)

#bgd = BetaGammaDelta_Dataframe(beta_tensors, gamma_tensors, delta_tensors, time)
#beta_gamma_delta_df = bgd.generate_dataframe()
#beta_gamma_delta_df