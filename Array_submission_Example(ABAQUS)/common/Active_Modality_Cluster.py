# FEM Code for Dome Active Modality 
# Object Recognition using hierarchical multistability
# Juan Camilo Osorio
# Programmable Structures Lab - Purdue University
# 04/10/2021
##=======================================================================================================================
from abaqus import *
from abaqusConstants import *
import __main__

import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior

import numpy as np
import csv
import sys

#=======================================================================================================================
# Import Arguments from terminal
# Square
# Argument 1: Number of CPUs [nCPUs] 
# Argument 2: Object Number [Obj_Num]
# Argument 3: Length [L]
# Argument 4: Width [W]
# Argument 5: Heigh [h]
# Argument 6: Angel [theta]
# Argument 7: Object Position in the x axis [obj_posX]
# Argument 8: Object Position in the z axis [obj_posZ]
# Argument 9: Object Type [object_type]

arg = sys.argv[1:]
object_type = arg[-1]

##=======================================================================================================================
## PROBLEM PARAMETERS (Change every iteration -> Variables to be examine)
##=======================================================================================================================
# OBJECT
if object_type == 'square':
	nCPUs = int(arg[-9])
	Obj_Num = int(arg[-8]) + 1
	L = float(arg[-7])
	W = float(arg[-6])
	h = float(arg[-5])
	theta = float(arg[-4])
	obj_posX = float(arg[-3])
	obj_posZ = float(arg[-2])

if object_type == 'cylinder':
	nCPUs = int(arg[-8])
	Obj_Num = int(arg[-7]) + 1
	L = float(arg[-6])
	d = float(arg[-5])
	theta = float(arg[-4])
	obj_posX = float(arg[-3])
	obj_posZ = float(arg[-2])
	W = d

# FILE NAME
filename = 'Active_Object_' + str(Obj_Num)
numDom = nCPUs

##=======================================================================================================================
## FIXED GEOMETRIC parameters (Would be constant at every simulation) !CHANGE AT WILL
##=======================================================================================================================
th = 0.6			# Metasheet thickness [mm]
Dh = 6.0			# Dome Height [mm]
Unit_Cell = 24.0 	        # Unit Cell Dimmension [mm]
nDomes = 8			# Number of domes on a row [mm]
P_val = 0.1			# Pressure for inversion [MPa] (Change this base on the unit cell dimmension and dome heigh)

# Starting position of the object (0.2 mm gap between the tip of the dome and the object) 
obj_gap = 0.5

if object_type=='square':
	obj_posY = Dh + th/2 + obj_gap
if object_type=='cylinder':
	obj_posY = Dh + th/2 + d/2 + obj_gap

##=======================================================================================================================
## MODEL
##=======================================================================================================================
mdb.Model(modelType=STANDARD_EXPLICIT, name=filename)
model_p = mdb.models[filename]

##=======================================================================================================================
## GEOMETRY
# All step files need to be in the same directory as the .py file
##=======================================================================================================================

# Import Dome Sheet from CAD model (.step File)
step = mdb.openStep('Dome_Sheet.STEP', scaleFromFile=OFF)
model_p.PartFromGeometryFile(name='Dome_Sheet', 
        geometryFile=step, combine=True, dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
pMeta = model_p.parts['Dome_Sheet']

# Import Dome base from CAD model (.step File)
step = mdb.openStep('Dome_Base.STEP', scaleFromFile=OFF)
model_p.PartFromGeometryFile(name='Dome_Base', 
        geometryFile=step, combine=True, dimensionality=THREE_D, 
        type=DISCRETE_RIGID_SURFACE)
pBase = model_p.parts['Dome_Base']

# Assign Reference Point
pBase.ReferencePoint(point=(3.5*Unit_Cell,-3.5*Unit_Cell,0.))

# Create Object (Directly in ABAQUS)
if object_type=='square':
	s = model_p.ConstrainedSketch(name='__profile__',sheetSize=200.0)
	s.rectangle(point1=(0, 0), point2=(W, h))
	pObj = model_p.Part(name='Object', dimensionality=THREE_D, 
	        type=DISCRETE_RIGID_SURFACE)
	pObj = model_p.parts['Object']
	pObj.BaseShellExtrude(sketch=s, depth=L)
	# Assign Reference Point
	pObj.ReferencePoint(point=(W/2,h/2,0.))

if object_type=='cylinder':
	s = model_p.ConstrainedSketch(name='__profile__',sheetSize=200.0)
	s.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(0, d/2))
	pObj = model_p.Part(name='Object', dimensionality=THREE_D, 
	        type=DISCRETE_RIGID_SURFACE)
	pObj = model_p.parts['Object']
	pObj.BaseShellExtrude(sketch=s, depth=L)
	pObj.ReferencePoint(point=(0.,0.,0.))


##=======================================================================================================================
## MATERIAL
##=======================================================================================================================
E = 26.0            #Elastic Modulus [MPa]
v = 0.3             #Poisson Ratio [-]
rho = 1.22E-06       #Material Density [kg/mm^3]

nameM = 'TPU'
model_p.Material(name= nameM)
model_p.materials[nameM].Density(table=((rho, ), ))
model_p.materials[nameM].Elastic(table=((E,v), ))

##=======================================================================================================================
## CREATE SECTION
##=======================================================================================================================
model_p.HomogeneousShellSection(name='Meta_Sheet', 
       preIntegrate=OFF, material=nameM, thicknessType=UNIFORM, thickness=th, 
       thicknessField='', nodalThicknessField='', 
       idealization=NO_IDEALIZATION, poissonDefinition=DEFAULT, 
       thicknessModulus=None, temperature=GRADIENT, useDensity=OFF, 
       integrationRule=SIMPSON, numIntPts=5)

##=======================================================================================================================
## SECTION ASSIGMENT
##=======================================================================================================================
f = pMeta.faces
faces = f.getByBoundingBox(-24.,-10,-24.,200,10,200)
region = pMeta.Set(faces=faces, name='Sheet')
pMeta.SectionAssignment(region=region, sectionName='Meta_Sheet', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)



##=======================================================================================================================
## ASSEMBLY
##=======================================================================================================================
a = model_p.rootAssembly
a.DatumCsysByDefault(CARTESIAN)

## META SHEET ========================
a.Instance(name='Sheet_Assembly', part=pMeta, dependent=OFF)

## BASE ========================
a.Instance(name='Sheet_Base', part=pBase, dependent=OFF)
a.rotate(instanceList=('Sheet_Base', ), axisPoint=(0.0, 0.0, 0.0), 
        axisDirection=(1.0, 0.0, 0.0), angle=-90.0)
a.translate(instanceList=('Sheet_Base', ), vector=(0.0, -8.0, 0.0))


## OBJECT ========================
a.Instance(name='Object_Assembly', part=pObj, dependent=OFF)

# OBJECT Movement and Rotation
# Object start position before translation
# y is the out of plane axis
#_______________________________________________________________|
#|							        |
#|							        |
#|							        |	x
#(0,0) -> Rotation center (CCW Positive Rotation)	        W	|    /
#|						                |	|   /
#|						                |	|  /
#|					                        |	| / Theta(+)
#|______________________________L_______________________________|	|/__________z 

if object_type=='square':
	a.translate(instanceList=('Object_Assembly', ), vector=(-W/2, 0, 0))


## PASSIVE SET ================================================================================================================
# This section needs to be here, to make things easier. 
## Find Passive Set First by rotating the sheet ========================
a.rotate(instanceList=('Sheet_Assembly', ), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, 1.0, 0.0), angle=-theta) # Rotate Sheet

rot_mat = np.array([[np.cos(np.deg2rad(theta)),-np.sin(np.deg2rad(theta))],[np.sin(np.deg2rad(theta)),np.cos(np.deg2rad(theta))]])

obj_rot_coord = np.dot(rot_mat, np.array([obj_posX, obj_posZ]))
a.translate(instanceList=('Object_Assembly', ), vector=(obj_rot_coord[0], 0, obj_rot_coord[1])) # Move Object

## Pressure Surface Passive set (Needs Work) ============================

obj_c1p = np.array([-W/2- Unit_Cell/2 -4,-Unit_Cell/2 - 4])
obj_c1 = np.array([obj_rot_coord[0],obj_rot_coord[1]]) + obj_c1p
obj_c3p = np.array([W/2 + Unit_Cell/2 + 4,L +Unit_Cell/2 + 4])
obj_c3 = np.array([obj_rot_coord[0],obj_rot_coord[1]])  + obj_c3p

BC_sheet_Assembly = a.instances['Sheet_Assembly']
SPressure = BC_sheet_Assembly.faces
Passive_surface = SPressure.getByBoundingBox(obj_c1[0],-1,obj_c1[1],obj_c3[0],Dh,obj_c3[1])
a.Surface(side2Faces=Passive_surface, name='Passive_surface')

## Once we have the passive set, we can return to the original Coordinate system
a.rotate(instanceList=('Sheet_Assembly', ), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, 1.0, 0.0), angle=theta) # Rotate Sheet Back
a.translate(instanceList=('Object_Assembly', ), vector=(-obj_rot_coord[0], 0, -obj_rot_coord[1])) # Move Object Back
## ==========================================================================================================================

## OBJECT
# Object is rotated from the (0,0) Point and translate after
a.rotate(instanceList=('Object_Assembly', ), axisPoint=(0.0, 0.0, 0.0), 
        axisDirection=(0.0, 1.0, 0.0), angle=theta)
a.translate(instanceList=('Object_Assembly', ), vector=(obj_posX, obj_posY, obj_posZ))


##=======================================================================================================================
## SIMULATION STEP
##=======================================================================================================================

# STEP 1 -> Dynamic Implicit (Passive Modality)
model_p.ImplicitDynamicsStep(name='Passive_Step', previous='Initial', 
        maxNumInc=5000, application=QUASI_STATIC, initialInc=0.1, 
        minInc=1e-10, nohaf=OFF, amplitude=RAMP, alpha=DEFAULT, 
        initialConditions=OFF, nlgeom=ON)

# Request OUTPUTS in these case we reduce the field variables to work with smaller files
save_n = 10 # Save every n time steps
model_p.fieldOutputRequests['F-Output-1'].setValues(variables=(
        'S', 'EE', 'U', 'RF'),frequency=save_n)

# Allways save the strain evergy over time .... Might be useful for multi-stable analysis
model_p.historyOutputRequests['H-Output-1'].setValues(
        variables=('ALLSE', ))


# STEP 2 -> Dynamic Implicit (Active Modality)
model_p.ImplicitDynamicsStep(name='Active_Step', previous='Passive_Step', 
        maxNumInc=5000, application=QUASI_STATIC, initialInc=0.1, 
        minInc=1e-10, nohaf=OFF, amplitude=RAMP, alpha=DEFAULT, 
        initialConditions=OFF, nlgeom=ON)

# STEP 2 -> General Static (Damping and Domes Stable State 2)
model_p.ImplicitDynamicsStep(name='Dome_Relax_Step', previous='Active_Step', 
        maxNumInc=5000, application=QUASI_STATIC, initialInc=0.01, 
        minInc=1E-08, nohaf=OFF, amplitude=RAMP, alpha=DEFAULT, 
        initialConditions=OFF, nlgeom=ON)


# STEP 3 -> General Static (Release outer Ring,  Fixed on the center)
model_p.ImplicitDynamicsStep(name='BC1_Relax_Step', previous='Dome_Relax_Step', 
        maxNumInc=5000, application=QUASI_STATIC, initialInc=0.01, 
        minInc=1E-08, nohaf=OFF, amplitude=RAMP, alpha=DEFAULT, 
        initialConditions=OFF, nlgeom=ON)


# STEP 4 -> General Static (Second Ring,  Fixed on the center)
model_p.ImplicitDynamicsStep(name='BC2_Relax_Step', previous='BC1_Relax_Step', 
        maxNumInc=5000, application=QUASI_STATIC, initialInc=0.01, 
        minInc=1E-08, nohaf=OFF, amplitude=RAMP, alpha=DEFAULT, 
        initialConditions=OFF, nlgeom=ON)


# STEP 5 -> General Static (Third Ring,  Fixed on the center)
model_p.ImplicitDynamicsStep(name='BC3_Relax_Step', previous='BC2_Relax_Step', 
        maxNumInc=5000, application=QUASI_STATIC, initialInc=0.01, 
        minInc=1E-08, nohaf=OFF, amplitude=RAMP, alpha=DEFAULT, 
        initialConditions=OFF, nlgeom=ON)


# STEP 6 -> General Static (Last Ring -> Just Fixed on the center)
model_p.ImplicitDynamicsStep(name='BC4_Relax_Step', previous='BC3_Relax_Step', 
        maxNumInc=5000, application=QUASI_STATIC, initialInc=0.01, 
        minInc=1E-08, nohaf=OFF, amplitude=RAMP, alpha=DEFAULT, 
        initialConditions=OFF, nlgeom=ON)

# STEP 7 -> General Static(Relax Step -> Fixed on the center)
model_p.ImplicitDynamicsStep(name='Structure_Relax', previous='BC4_Relax_Step', 
        maxNumInc=5000, application=QUASI_STATIC, initialInc=0.001, 
        minInc=1E-12, nohaf=OFF, amplitude=RAMP, alpha=DEFAULT, 
        initialConditions=OFF, nlgeom=ON)


##=======================================================================================================================
## CONTACT
##=======================================================================================================================
model_p.ContactProperty('Inter_Prop')
model_p.interactionProperties['Inter_Prop'].TangentialBehavior(
    formulation=FRICTIONLESS, directionality=ISOTROPIC, slipRateDependency=OFF, 
    pressureDependency=OFF, temperatureDependency=OFF, dependencies=0, 
    shearStressLimit=None, maximumElasticSlip=FRACTION, 
    fraction=0.005, elasticSlipStiffness=None)

model_p.interactionProperties['Inter_Prop'].NormalBehavior(
        pressureOverclosure=HARD, allowSeparation=ON, 
        constraintEnforcementMethod=DEFAULT)

model_p.ContactStd(name='General', createStepName='Initial')
model_p.interactions['General'].includedPairs.setValuesInStep(
       stepName='Initial', useAllstar=ON)

model_p.interactions['General'].contactPropertyAssignments.appendInStep(
       stepName='Initial', assignments=((GLOBAL, SELF, 'Inter_Prop'), ))


##=======================================================================================================================
## BOUNDARY CONDITIONS SETS 
##=======================================================================================================================

## META SHEET ========================
BC_sheet_Assembly = a.instances['Sheet_Assembly']

def BC_edges_Sheet(c1,c2,c3,c4,sheet_L,thres,BCname): # Fuction to set boundary conditions over the metasheet
	#c2-------Side 3------c3|
	#|		        |
	#|		        |
	#S 		        S
	#i 		        i  x
	#d 			d  |
	#e 			e  |
	#1			2  |
	#|(Origin)		|  |
	#c1---_--Side 4-------c4|  |_________z

	e = BC_sheet_Assembly.edges
	side1 = e.getByBoundingBox(
		c1[0] - thres,-1,c1[2],c2[0],1,c2[2] + thres)
	side2 = e.getByBoundingBox(
		c4[0] - thres,-1,c4[2],c3[0],1,c3[2] + thres)
	side3 = e.getByBoundingBox(
		c2[0]- thres,-1,c2[2],c3[0]+ thres,1,c3[2])

	side4 = e.getByBoundingBox(
		c1[0]- thres,-1,c1[2],c4[0]+ thres,1,c4[2])

	a.Set(edges=side1 + side2 + side3 + side4, name=BCname)


thres = 0.1
sheet_L = nDomes*Unit_Cell

# BC1
c11 = np.array([-Unit_Cell/2,0,-Unit_Cell/2])
c21 = np.array([sheet_L-Unit_Cell/2,0,-Unit_Cell/2])
c31 = np.array([sheet_L-Unit_Cell/2,0,sheet_L-Unit_Cell/2])
c41 = np.array([-Unit_Cell/2,0,sheet_L-Unit_Cell/2])

BC_edges_Sheet(c11,c21,c31,c41,sheet_L,thres,'BC1')

# BC2
c12 = np.array([c11[0] + Unit_Cell,0,c11[2] + Unit_Cell])
c22 = np.array([c21[0] - Unit_Cell,0,c21[2] + Unit_Cell])
c32 = np.array([c31[0] - Unit_Cell,0,c31[2] - Unit_Cell])
c42 = np.array([c41[0] + Unit_Cell,0,c41[2] - Unit_Cell])

BC_edges_Sheet(c12,c22,c32,c42,sheet_L,thres,'BC2')

# BC3
c13 = np.array([c12[0] + Unit_Cell,0,c12[2] + Unit_Cell])
c23 = np.array([c22[0] - Unit_Cell,0,c22[2] + Unit_Cell])
c33 = np.array([c32[0] - Unit_Cell,0,c32[2] - Unit_Cell])
c43 = np.array([c42[0] + Unit_Cell,0,c42[2] - Unit_Cell])

BC_edges_Sheet(c13,c23,c33,c43,sheet_L,thres,'BC3')

# BC4
c14 = np.array([c13[0] + Unit_Cell,0,c13[2] + Unit_Cell])
c24 = np.array([c23[0] - Unit_Cell,0,c23[2] + Unit_Cell])
c34 = np.array([c33[0] - Unit_Cell,0,c33[2] - Unit_Cell])
c44 = np.array([c43[0] + Unit_Cell,0,c43[2] - Unit_Cell])

BC_edges_Sheet(c14,c24,c34,c44,sheet_L,thres,'BC4')

# Center Region for continuous clamping
e = BC_sheet_Assembly.edges

center_sheet = np.array([(sheet_L- Unit_Cell)/2,0,(sheet_L- Unit_Cell)/2])
center_clamp = e.getByBoundingBox(center_sheet[0]-5,-1,center_sheet[2]-5,center_sheet[0]+5,1,center_sheet[2]+5)
a.Set(edges=center_clamp, name='Sheet_Center')

# Set with all outer edges of every unitcell (Only for pressure application)
Outer_Unit = e.getByBoundingBox(-Unit_Cell/2,-1,-Unit_Cell/2,-Unit_Cell/2,1,sheet_L-Unit_Cell/2)

for i in range(nDomes):
	Outer_Unit = Outer_Unit + e.getByBoundingBox((i+1)*(Unit_Cell)-Unit_Cell/2,-1,-Unit_Cell/2,(i+1)*(Unit_Cell)-Unit_Cell/2,1,sheet_L-Unit_Cell/2)

for j in range(nDomes + 1):
	Outer_Unit = Outer_Unit + e.getByBoundingBox(-Unit_Cell/2,-1,j*(Unit_Cell)-Unit_Cell/2,sheet_L-Unit_Cell/2,1,j*(Unit_Cell)-Unit_Cell/2)

a.Set(edges=Outer_Unit, name='Outer_Unit_edges')

## OBJECT AND BASE ========================
RPs_obj = a.instances['Object_Assembly'].referencePoints
a.Set(referencePoints=(RPs_obj[2], ), name='RP_Obj')

RPs_base = a.instances['Sheet_Base'].referencePoints
a.Set(referencePoints=(RPs_base[2], ), name='RP_Base')

## Pressure ============================
SPressure = BC_sheet_Assembly.faces
a.Surface(side2Faces=SPressure, name='Pressure_surface')


##=======================================================================================================================
## BOUNDARY CONDITIONS
##=======================================================================================================================

## BC BASE ===================================
region = a.sets['RP_Base']
model_p.DisplacementBC(name='Fix_Base', createStepName='Passive_Step', region=region,u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, 
        ur3=0.0, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

model_p.boundaryConditions['Fix_Base'].setValuesInStep(stepName='Structure_Relax', u2= 4.0)

## BC OBJECT ===================================
region = a.sets['RP_Obj']
model_p.DisplacementBC(name='Obj_Dis', createStepName='Passive_Step', region=region,u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, 
        ur3=0.0, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

model_p.boundaryConditions['Obj_Dis'].setValuesInStep(stepName='Dome_Relax_Step', u2= -Dh - obj_gap)


## META SHEET ===================================
region = a.sets['Sheet_Center']
model_p.DisplacementBC(name='Fix_Center_sheet', createStepName='Passive_Step', region=region,u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, 
        ur3=0.0, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

model_p.boundaryConditions['Fix_Center_sheet'].setValuesInStep(stepName='Structure_Relax', ur1=FREED, ur2=FREED, ur3=FREED)


region = a.sets['Outer_Unit_edges']
model_p.DisplacementBC(name='Outer_Unit_edges', createStepName='Initial', region=region,u1=0.0, u2=0.0, u3=0.0, ur1=UNSET, ur2=UNSET, 
        ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

model_p.boundaryConditions['Outer_Unit_edges'].setValuesInStep(stepName='Dome_Relax_Step', ur1=FREED, ur2=FREED, ur3=FREED)
model_p.boundaryConditions['Outer_Unit_edges'].deactivate('BC1_Relax_Step')


region = a.sets['BC1']
model_p.DisplacementBC(name='BC1', createStepName='Initial', region=region,u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, 
        ur3=0.0, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

model_p.boundaryConditions['BC1'].setValuesInStep(stepName='Dome_Relax_Step', ur1=FREED, ur2=FREED, ur3=FREED)
model_p.boundaryConditions['BC1'].deactivate('BC1_Relax_Step')


region = a.sets['BC2']
model_p.DisplacementBC(name='BC2', createStepName='Initial', region=region,u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, 
        ur3=0.0, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

model_p.boundaryConditions['BC2'].setValuesInStep(stepName='Dome_Relax_Step', ur1=FREED, ur2=FREED, ur3=FREED)
model_p.boundaryConditions['BC2'].deactivate('BC2_Relax_Step')

region = a.sets['BC3']
model_p.DisplacementBC(name='BC3', createStepName='Initial', region=region,u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, 
        ur3=0.0, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

model_p.boundaryConditions['BC3'].setValuesInStep(stepName='Dome_Relax_Step', ur1=FREED, ur2=FREED, ur3=FREED)
model_p.boundaryConditions['BC3'].deactivate('BC3_Relax_Step')

region = a.sets['BC4']
model_p.DisplacementBC(name='BC4', createStepName='Initial', region=region,u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, 
        ur3=0.0, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

model_p.boundaryConditions['BC4'].setValuesInStep(stepName='Dome_Relax_Step', ur1=FREED, ur2=FREED, ur3=FREED)
model_p.boundaryConditions['BC4'].deactivate('BC4_Relax_Step')


##=======================================================================================================================
## LOADS
##=======================================================================================================================
# PASSIVE PRESSURE
region = a.surfaces['Passive_surface']
model_p.Pressure(name='P_Passive', createStepName='Passive_Step', 
        region=region, distributionType=UNIFORM, field='', magnitude=-P_val, 
        amplitude=UNSET)

model_p.loads['P_Passive'].deactivate('Active_Step')

# ACTIVE PRESSURE
# BOOLEAN OPERATION TO REMOVE PASSIVE DOMES
a.SurfaceByBoolean(name='Active', operation=DIFFERENCE, surfaces=(
        a.surfaces['Pressure_surface'], a.surfaces['Passive_surface'], ))

region = a.surfaces['Active']
model_p.Pressure(name='P_Active', createStepName='Active_Step', 
        region=region, distributionType=UNIFORM, field='', magnitude=-P_val, 
        amplitude=UNSET)

model_p.loads['P_Active'].deactivate('Dome_Relax_Step')

##=======================================================================================================================
## MESH
##=======================================================================================================================
ObjMesh = 2.5 	        # Object General mesh size[mm]
BaseMesh = 3 	        # Base General mesh size[mm]
SheetMesh = 2         # Metasheet General mesh size[mm]

ObjPart=(a.instances['Object_Assembly'], )
a.seedPartInstance(regions=ObjPart, size=ObjMesh, deviationFactor=0.1, minSizeFactor=0.1)
a.generateMesh(regions=ObjPart)

BasePart=(a.instances['Sheet_Base'], )
a.seedPartInstance(regions=BasePart, size=BaseMesh, deviationFactor=0.1, minSizeFactor=0.1)
a.generateMesh(regions=BasePart)


SheetPart=(a.instances['Sheet_Assembly'], )
a.seedPartInstance(regions=SheetPart, size=SheetMesh, deviationFactor=0.1, minSizeFactor=0.1)
a.generateMesh(regions=SheetPart)

##=======================================================================================================================
## NODE SETS FOR ANALYSIS
##=======================================================================================================================
nodes_MetaSheet = a.instances['Sheet_Assembly'].nodes

Hor_Sensors = nodes_MetaSheet.getByBoundingBox(-Unit_Cell/2,-1,-Unit_Cell/2,-Unit_Cell/2,1,sheet_L-Unit_Cell/2)
Ver_Sensors = nodes_MetaSheet.getByBoundingBox(-Unit_Cell/2,-1,-Unit_Cell/2,sheet_L-Unit_Cell/2,1,-Unit_Cell/2)

for i in range(nDomes):
	Hor_Sensors = Hor_Sensors + nodes_MetaSheet.getByBoundingBox((i+1)*(Unit_Cell)-Unit_Cell/2,-1,-Unit_Cell/2,(i+1)*(Unit_Cell)-Unit_Cell/2,1,sheet_L-Unit_Cell/2)

for j in range(nDomes):
	Ver_Sensors = Ver_Sensors + nodes_MetaSheet.getByBoundingBox(-Unit_Cell/2,-1,(j+1)*(Unit_Cell)-Unit_Cell/2,sheet_L-Unit_Cell/2,1,(j+1)*(Unit_Cell)-Unit_Cell/2)

a.Set(nodes=Hor_Sensors, name='Horizontal_Sensors')
a.Set(nodes=Ver_Sensors, name='Vertical_Sensors')

##=======================================================================================================================
## ADD EDGE TO EDGE CONTACT TO THE KEYWORDS
##=======================================================================================================================
# Synch edits to modelkwb with those made in the model. We don't need
# access to *nodes and *elements as they would appear in the inp file,
# so set the storeNodesAndElements arg to False.
modelkwb = model_p.keywordBlock
modelkwb.synchVersions(storeNodesAndElements=False)

# Search the modelkwb for the desired insertion point. In this example, 
# we are looking for a line that indicates we are beginning the Contact. 
# If it is found, we break the loop, storing the line number, and then write our keywords
# using the insert method (which actually inserts just below the specified line number, fyi).

line_num = 0
for n, line in enumerate(modelkwb.sieBlocks):
    if line == "*Contact":
        line_num = n
        break

kwds = "*CONTACT FORMULATION, TYPE=EDGE TO EDGE, FORMULATION=BOTH"
modelkwb.insert(position=line_num+1, text=kwds)

##=======================================================================================================================
## JOB SUBMISSION
##=======================================================================================================================
mdb.Job(name=filename, model=filename, description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=numDom, 
    numDomains=numDom, numGPUs=0)

mdb.jobs[filename].writeInput(consistencyChecking=OFF)
##=======================================================================================================================