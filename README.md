# Anamorphosis

## Detection of edges and deformations on a surface of several sheets of speckles

<p align="center">
  <img width="700" alt="Capture d’écran 2021-11-10 à 09 02 57" src="https://user-images.githubusercontent.com/84194324/141127089-da3f65a4-66ff-4667-b41b-1c5d69b1e156.png">
</p>

### Installation
To begin, you have to download some packages listed in the requirements.txt file
To use main.py, you also have to download Module folder. If you want to open anamorphosed speckle project, you can download the Open_project.py file

### deck_ETS_rot.yaml initialisation

Main structure for `deck.yaml` file:

```
Camera:
  Focal_length: 50 #mm
  Sensor_height: 29 #mm

Input_speckle: 
  Step: 100
  Begining: 3
  Height: 27e-2
  Width: 21e-2
  Path: './Banque_Speckle/2mm/'
  Generic_name: 'Speckle_'

Surface : 
  Angle : 78 #deg
  Length_Surface : 3.0 #m 
  Width_Surface : 0.6 #m 
  Dist_cam : 4.12 #m 
  Radius : 0.4
  Surface_type : 'Plan'

Output_speckle:
  Height_printable: 27.9e-2
  Width_printable: 21.6e-2
  Print_path: './AnamorphosePlane/ImagePrintable'
```
#### Camera section
```
Camera:
  Focal_length: 50 #mm
  Sensor_height: 29 #mm
 ```
 Enter your focal length and sensor height in mm in these variable. Field of view in degrees and radians will be calculated and printed out.
 It is also used to plot the field of view cone in the 3D viewer.
#### Input_Speckle section
```
Input_speckle: 
  Step: 100
  Begining: 3
  Height: 27e-2
  Width: 21e-2
  Path: './Banque_Speckle/2mm/'
  Generic_name: 'Speckle_'
```
Due to the multitude of points in the speckle, to test the code, we only anamorphose a few points. The variable *Step* represents the anamorphic step. `step=X` will anamorphose 1/X of all the points of a sheet of speckles.

*Begining* variable represents the first index of the contour list calculated by OpenCV to be considered in the anamorphosis. Usually `begining=3` is often sufficient to avoid black filling of the result by the algorithm. The index before 3 in the contour list usually represent the contour of the sheet hence the black filling.

You need to implement the size of the speckle sheets you want to anamorphose and the size of the anamorphosed speckle sheets you want to get. Use the *Height*, *Width*. The unit is meter.

*Path* is the path of the classic speckle sheets folder.

*Generic_name* is the name of your speckle sheets. It as to be the shape of *Generic_Name_XX* with XX a number.


#### Surface section
```
Surface : 
  Angle : 78 #deg
  Length_Surface : 3.0 #m 
  Width_Surface : 0.6 #m 
  Dist_cam : 4.12 #m 
  Radius : 0.4
  Surface_type : 'Plan'
```
Then you must to implement the surface properties :
- *Angle* represents the angle between the plane of the sensor and of the wing.
- *Length_Surface* represents the length of the surface in meter.
- *Width_Surface* represents the width of the surface in meter.
- *Dist_cam* represents the distance between the camera rig and the middle of the surface in meter.
- *Radius* is the radius of the cylinder in the case of a cylinder.
- *Surface_type* is a string to tell the programm that you want to anamorphose on a `Cylindre` or on a `Plan`. Only cylinder or plane surface case are implemented.
For now the Cylinder surface type isn't implemented.
From these surface properties, the normal vector of the plan of the wing, the wingframe position (1,2,3 and 4 on the underneath figure) and the number and position of speckle sheets are calculated.

<p align="center">
  <img width="628" alt="Capture d’écran 2021-11-09 à 20 24 42" src="https://user-images.githubusercontent.com/84194324/141032568-872ec514-2716-4acb-a321-eb7dfd5d4731.png">
</p>

#### Output_Speckle section
```
Output_speckle:
  Height_printable: 27.9e-2
  Width_printable: 21.6e-2
  Print_path: './ImagePrintable'
```
*Height_printable* and *Width_printable* variables are the height and the width of the anarmophosed speckle you want to print. 
*Print_path* is the path of the anamorphosed speckle sheets folder.


## Trucs à faire

- Développer le programme pour y ajouter la surface cylindrique
- Effectuer l'anamorphose dans un espace où la caméra n'est plus le centre et orienté dans n'importe quelle direction.
