/**
 * Example configuration
 */

// - line comment
/* 
   - block comment
*/
// Import - exactly one model
import: {   
    from: "E:\Spike\spike-1.6.0rc2-win64\Percolation\Percolation_Model_100_100.andl";
}



configuration: {

  model: {
    constants: {
     all: {
	p: [[0.3, 0.32222222, 0.34444444, 0.36666667, 0.38888889,0.41111111, 0.43333333, 0.45555556, 0.47777778, 0.5      ]];
         }
       }
    places: {   
	site_0_0: 10; 
    }    
  }

  simulation:
  {
    // Name of a simulation
    name: "Percolation";
    /*
     * Set up a simulation
     */
    type:continuous: {
      solver:
      BDF: {
        semantic: "adapt";// "bio", "adapt"
        iniStep: 0.1;
        // "CVDense", "CVSpgmr", "CVDiag", "CVSpbcg", "CVSptfqmr"
        linSolver: "CVDense";
        relTol: 1e-5;
        absTol: 1.0e-10;
        autoStepSize: false;
        reductResultingODE: true;
        checkNegativeVal: false;
        outputNoiseVal: false;
      }
    }

    interval: 0:200:100;

    export: {
      // Array of places to save (if empty export all)
      places: [];//[];// all places
      //places:c: [];//[];// all coloured places
      //places:u: [];// uncoloured places
      transitions: [];// all transitions
      //transitions:c: [];// all coloured transitions
      //transitions:u: [];// all uncoloured transitions
      observers: [];
      csv: {
        sep: ";";// Separator  

        file: "E:\Spike\spike-1.6.0rc2-win64\Percolation\Results\"
          //<< name << "_"
          << import.name << "_"
          << configuration.simulation.type << "_"
          << configuration.model.constants.all.p
          << "_"
          << "Percolation.csv";// File name
      }
    }
  }
}   
