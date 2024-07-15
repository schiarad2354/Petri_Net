/**
 * Example configuration
 */

// - line comment
/* 
   - block comment
*/
// Import - exactly one model
import: {   
    from: "./model/SIR_USA.xml";
}



configuration: {

  model: {
    places: {   
	S1: 100000; 
    }    
  }

  simulation:
  {
    // Name of a simulation
    name: "SIR";
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

        file: "E:\Spike\spike-1.6.0rc2-win64\SIR\data\"
          << name << "_"
          << import.name << "_"
          << configuration.simulation.type << "_"
          << configuration.simulation.type.solver
          << "_"
          << "Counties_USA.csv";// File name
      }
    }
  }
}   
