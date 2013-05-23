![alt text](https://raw.github.com/joac/fugue/master/data/logo.png "Logo")
# Fugue

Fugue is a projector calibration tool, thats make posible to know its intrinsec an extrinsec parameters.
Good calibration and calculation, is a key aspect in projection mapping, and spatial reconstruction.

## Desired Functionality

This tool provide two functionalities:
 * Calculation of intrisec parameters of proyector: 
    - Returns the camera matrix, for the given proyector and resolution
 * Calculation of extrinsec parameter of proyector:
    - Returns the rotation|translation matrix for the given proyector on the current scene

Internally, the tool saves all proyector calibrations, begin able to easy calculate te extrinsec parameters, for any scene.

All proyector parameters, are saved on a csv file, to simplify backup and sharing off proyector params.

Also, you can save scenes for further reutilization.

## Calibrations

To estimate all parameters, you need a well constructed cube with sides of 300mm    Every face needs to have a 100mm squared grid.
The precise construction of these dummy cube, is essential for precise calibrations.
