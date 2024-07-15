import numpy as np
import xml.etree.ElementTree as ET

# Import classes from other files
from HyperParameters import HyperParameters
from Polygon import Polygon
from Polygon import Polygon_grid.get_grid_and_adj_matrix
from Adjacency import Adjacency
from Adjacency import Adjacency.generate_adjacency_matrix


class SIRModelSBML:
    """
    A class to generate an SBML model for the SIR (Susceptible-Infected-Recovered) model.

    Methods:
    - add_compartment: Add a compartment to the SBML model.
    - add_species: Add a species to the SBML model.
    - add_parameter: Add a parameter to the SBML model.
    - add_initial_assignment: Add an initial assignment to the SBML model.
    - add_reaction: Add a reaction to the SBML model.
    """
    
    def __init__(self):
        """
        Initialize the SBML model with necessary elements.
        """
        self.root = ET.Element("{http://www.sbml.org/sbml/level3/version1/core}sbml", level="3", version="1")
        self.model = ET.SubElement(self.root, "model", id="Model_generated_by_BIOCHAM")
        self.list_of_compartments = ET.SubElement(self.model, "listOfCompartments")
        self.list_of_species = ET.SubElement(self.model, "listOfSpecies")
        self.list_of_parameters = ET.SubElement(self.model, "listOfParameters")
        self.list_of_initial_assignments = ET.SubElement(self.model, "listOfInitialAssignments")
        self.list_of_reactions = ET.SubElement(self.model, "listOfReactions")

    def add_compartment(self, compartment_id, spatial_dimensions="3", size="1", constant="true"):
        """
        Add a compartment to the SBML model.

        Args:
        - compartment_id (str): ID of the compartment.
        - spatial_dimensions (str): Spatial dimensions of the compartment (default: "3").
        - size (str): Size of the compartment (default: "1").
        - constant (str): Whether the size is constant (default: "true").
        """
        ET.SubElement(self.list_of_compartments, "compartment", id=compartment_id,
                      spatialDimensions=spatial_dimensions, size=size, constant=constant)

    def add_species(self, species_id, name, compartment, initial_concentration="0", has_only_substance_units="false",
                    boundary_condition="false", constant="false"):
        """
        Add a species to the SBML model.

        Args:
        - species_id (str): ID of the species.
        - name (str): Name of the species.
        - compartment (str): Compartment where the species exists.
        - initial_concentration (str): Initial concentration of the species (default: "0").
        - has_only_substance_units (str): Whether the species has only substance units (default: "false").
        - boundary_condition (str): Whether the species is a boundary condition (default: "false").
        - constant (str): Whether the species concentration is constant (default: "false").
        """
        ET.SubElement(self.list_of_species, "species", id=species_id, name=name, compartment=compartment,
                      initialConcentration=initial_concentration, hasOnlySubstanceUnits=has_only_substance_units,
                      boundaryCondition=boundary_condition, constant=constant)

    def add_parameter(self, parameter_id, name, value, constant="true"):
        """
        Add a parameter to the SBML model.

        Args:
        - parameter_id (str): ID of the parameter.
        - name (str): Name of the parameter.
        - value (str): Value of the parameter.
        - constant (str): Whether the parameter value is constant (default: "true").
        """
        ET.SubElement(self.list_of_parameters, "parameter", id=parameter_id, name=name, value=value, constant=constant)

    def add_initial_assignment(self, symbol, math_content):
        """
        Add an initial assignment to the SBML model.

        Args:
        - symbol (str): Symbol for the initial assignment.
        - math_content (str): MathML content defining the assignment.
        """
        initial_assignment = ET.SubElement(self.list_of_initial_assignments, "initialAssignment", symbol=symbol)
        math = ET.SubElement(initial_assignment, "math", xmlns="http://www.w3.org/1998/Math/MathML")
        math.append(ET.fromstring(math_content))  # Parse MathML from string and append

    def add_reaction(self, reaction_id, reversible="false", reactants=None, products=None, kinetic_law_math=None):
        """
        Add a reaction to the SBML model.

        Args:
        - reaction_id (str): ID of the reaction.
        - reversible (str): Whether the reaction is reversible (default: "false").
        - reactants (dict): Dictionary of reactants {species_id: stoichiometry}.
        - products (dict): Dictionary of products {species_id: stoichiometry}.
        - kinetic_law_math (str): MathML content defining the kinetic law.
        """
        reaction = ET.SubElement(self.list_of_reactions, "reaction", id=reaction_id, reversible=reversible, fast="false")

        # Add reactants
        if reactants:
            list_of_reactants = ET.SubElement(reaction, "listOfReactants")
            for species_id, stoichiometry in reactants.items():
                ET.SubElement(list_of_reactants, "speciesReference", species=species_id, stoichiometry=str(stoichiometry), constant="true")

        # Add products
        if products:
            list_of_products = ET.SubElement(reaction, "listOfProducts")
            for species_id, stoichiometry in products.items():
                ET.SubElement(list_of_products, "speciesReference", species=species_id, stoichiometry=str(stoichiometry), constant="true")

        # Create kinetic law with MathML
        kinetic_law = ET.SubElement(reaction, "kineticLaw")
        math = ET.SubElement(kinetic_law, "math", xmlns="http://www.w3.org/1998/Math/MathML")
        math.append(ET.fromstring(kinetic_law_math))  # Parse MathML from string and append

        

    def create_model(grid_size, model_type, betas, gammas, deltas, number_of_configurations):
        """
        Create multiple SBML models based on the parameters.

        Args:
        - grid_size (int): Size of the grid (not used in current implementation).
        - model_type (str): Type of the model (e.g., "SIR").
        - adjacency_choice (str): Type of adjacency matrix generation (not used in current implementation).
        - betas (list): List of beta values for each configuration.
        - gammas (list): List of gamma values for each configuration.
        - deltas (list): List of delta values for each configuration.
        - number_of_configurations (int): Number of configurations to generate.
        """
        # If user/pre-defined input is a shapefile, we import polygon class
        if polygon_input is not None:
            try: 
                # Call from polygon
                polygon_grid = Polygon("cb_2023_us_county_500k.shp", grid_size = 10, US = True, stateabrev = ['AZ'])
                grid, adj_matrix = polygon_grid.get_grid_and_adj_matrix(hexagonal=False)
                number_of_patches = len(adj_matrix.values[0])
                adjacency_matrix = adj_matrix.values
        
            except FileNotFoundError:
                print("Shapefile not found.")
                return None
            
        # If user/pre-defined input is a matrix adjacency file, we import adjacency class
        elif adjacency_input is not None:
            try:
                # Call adjacency
                adj_matrix = Adjacency(adjacency_file, US=True, stateabrev=['TX'])
                adjacency_matrix = adj_matrix.generate_adjacency_matrix()
                number_of_patches = len(adj_matrix.values[0])
                adjacency_matrix = adj_matrix.values
            
            except FileNotFoundError:
                print("Adjacency matrix file not found.")
                return None
        else:
            print("No input found.")
            return None

        
        # Initial values conditions
        #I0_value = np.arange(0, 100, 99)
        #R0_value = np.arange(0, 100, 99)
        #S0_value = np.arange(0, 100, 99)
    
        if model_type == "SIR":
            # If model type is SIR
            for i in range(number_of_configurations):
                sir_model = SIRModelSBML() # Calls the creation of SBML file
                for patch_num in range(1, number_of_patches + 1): # goes through each of the patch/grid cells
                    compartment_id = f"compartment{patch_num}"
                    sir_model.add_compartment(compartment_id, spatial_dimensions="3", size="1", constant="true")
                    for species_type in ["S", "I", "R"]:
                        species_id = f"{species_type}{patch_num}" # Specify each place as patchnum
                        IC = str(S0_value[i]) if species_type == "S" else str(I0_value[i]) if species_type == "I" else str(R0_value[i])
                        sir_model.add_species(species_id, name=species_id, compartment=compartment_id, initial_concentration=IC)
                    
                    species_ids = [species.get('id') for species in species_list]

                    for param_name, param_value in [(f"beta_{patch_num}", beta_value[i]), (f"gamma_{patch_num}", gamma_value[i]), (f"delta_{patch_num}", delta_value[i])]:
                        sir_model.add_parameter(param_name, name=param_name, value=str(param_value), constant="true")
                    for state_var in ["S", "I", "R"]:
                        initial_assignment_symbol = f"{state_var}{patch_num}"
                        sir_model.add_initial_assignment(initial_assignment_symbol, f"<ci>{state_var}0</ci>")
                    # Add kinetic law reactions for the given parameters based on patch num
                    kinetic_law_reaction_1 = f"<apply><times/><ci>gamma_{patch_num}</ci><ci>I{patch_num}</ci></apply>"  # need to comeback and specify the beta, gamma, and delta for each patch
                    kinetic_law_reaction_2 = f"<apply><times/><ci>beta_{patch_num}</ci><ci>S{patch_num}</ci><ci>I{patch_num}</ci></apply>" # need to comeback and specify the beta, gamma, and delta for each patch

                    sir_model.add_reaction(f"R_{patch_num}_I", reactants={f"I{patch_num}": 1}, products={f"R{patch_num}": 1}, kinetic_law_math=kinetic_law_reaction_1)
                    sir_model.add_reaction(f"R_{patch_num}_R", reactants={f"S{patch_num}": 1, f"I{patch_num}": 1}, products={f"I{patch_num}": 2}, kinetic_law_math=kinetic_law_reaction_2)

                    for neighbor_patch in np.where(adjacency_matrix[patch_num - 1] == 1)[0] + 1:
                        kinetic_law_reaction_between_patches_Susceptibles = f"<apply><times/><ci>beta_{patch_num}</ci><ci>delta_{patch_num}</ci><ci>S{patch_num}</ci></apply>"
                        kinetic_law_reaction_between_patches_Infected = f"<apply><times/><ci>beta_{patch_num}</ci><ci>delta_{patch_num}</ci><ci>I{patch_num}</ci></apply>"
                        sir_model.add_reaction(f"R_{patch_num}_{neighbor_patch}_I", reactants={f"I{patch_num}": 1}, products={f"I{neighbor_patch}": 1}, kinetic_law_math=kinetic_law_reaction_between_patches_Infected)
                        sir_model.add_reaction(f"R_{patch_num}_{neighbor_patch}", reactants={f"S{patch_num}": 1}, products={f"S{neighbor_patch}": 1}, kinetic_law_math=kinetic_law_reaction_between_patches_Susceptibles)

                tree = ET.ElementTree(sir_model.root)
                tree.write(f"SIR_MOC_Multi_{i}.xml", encoding="UTF-8", xml_declaration=True, method="xml")

        elif model_type == "SEIR":
            for i in range(number_of_configurations):
                sir_model = SIRModelSBML() 
                for patch_num in range(1, number_of_patches + 1):
                    compartment_id = f"compartment{patch_num}"
                    sir_model.add_compartment(compartment_id, spatial_dimensions="3", size="1", constant="true")

                    for species_type in ["S", "E", "I", "R"]: # added the Exposed 
                        species_id = f"{species_type}{patch_num}" 
                        IC = str(S0_value[i]) if species_type == "S" else str(E0_value[i]) if species_type == "E" else str(I0_value[i]) if species_type == "I" else str(R0_value[i])

                    for param_name, param_value in [(f"beta_{patch_num}", beta_value[i]), (f"gamma_{patch_num}", gamma_value[i]), (f"delta_{patch_num}", delta_value[i])]:
                        sir_model.add_parameter(param_name, name=param_name, value=str(param_value), constant="true")

                    for state_var in ["S", "E", "I", "R"]:
                        initial_assignment_symbol = f"{state_var}{patch_num}"
                        sir_model.add_initial_assignment(initial_assignment_symbol, f"<ci>{state_var}0</ci>")

                    kinetic_law_reaction_1 = f"<apply><times/><ci>gamma_{patch_num}</ci><ci>I{patch_num}</ci></apply>"
                    kinetic_law_reaction_2 = f"<apply><times/><ci>beta_{patch_num}</ci><ci>S{patch_num}</ci><ci>I{patch_num}</ci></apply>"
                    kinetic_law_reaction_3 = f"<apply><times/><ci>nu_{patch_num}</ci><ci>E{patch_num}</ci></apply>"
    
                    sir_model.add_reaction(f"R_{patch_num}_1", reactants={f"I{patch_num}": 1}, products={f"R{patch_num}": 1}, kinetic_law_math=kinetic_law_reaction_1)
                    sir_model.add_reaction(f"R_{patch_num}_2", reactants={f"S{patch_num}": 1, f"I{patch_num}": 1}, products={f"I{patch_num}": 1, f"E{patch_num}": 1}, kinetic_law_math=kinetic_law_reaction_2)
                    sir_model.add_reaction(f"I_{patch_num}_3", reactants={f"E{patch_num}": 1}, products={f"I{patch_num}": 1}, kinetic_law_math=kinetic_law_reaction_3)
            
                    # reactions and kinetic laws BETWEEN patches
                    for neighbor_patch in np.where(adjacency_matrix[patch_num - 1] == 1)[0] + 1:
                        kinetic_law_reaction_between_patches_Susceptibles = f"<apply><times/><ci>beta_{patch_num}</ci><ci>delta_{patch_num}</ci><ci>S{patch_num}</ci></apply>"
                        kinetic_law_reaction_between_patches_Infected = f"<apply><times/><ci>beta_{patch_num}</ci><ci>delta</ci><ci>I{patch_num}</ci></apply>"
                        sir_model.add_reaction(f"R_{patch_num}_{neighbor_patch}_I", reactants={f"I{patch_num}": 1}, products={f"I{neighbor_patch}": 1}, kinetic_law_math=kinetic_law_reaction_between_patches_Infected)
                        sir_model.add_reaction(f"R_{patch_num}_{neighbor_patch}", reactants={f"S{patch_num}": 1}, products={f"S{neighbor_patch}": 1}, kinetic_law_math=kinetic_law_reaction_between_patches_Susceptibles)


                tree = ET.ElementTree(sir_model.root)
                tree.write("SEIR_MOC_Multi.xml", encoding="UTF-8", xml_declaration=True, method="xml")
        else:
            print("Invalid model type. Supported types: 'SIR', 'SEIR'")
