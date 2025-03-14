import os
import numpy as np
from scipy.special import erf

def generate_Ly_list(num_layers):
    ny = num_layers

    d_min = 0.002
    d_max = 0.01

    x1 = 90.00
    x2 = 2.0
    p = 1.50
    nnn = 633
    #23-310, 51-599

    delta = np.zeros([nnn, 1])
    for i in range(nnn):
        delta[i] = d_min + 0.5 * (erf((-x2 + (x1 + x2) / (nnn-1.0) * i) * p) - erf(-x2 * p)) * (d_max - d_min)
    normal_dis = np.zeros([ny-1, 1])
    for j in range(ny-1):
        normal_dis[j] = delta[j] * delta[ny-j-2]
    normal_dis = normal_dis / np.sum(normal_dis)

    n = np.cumsum(normal_dis)
    n = n / np.max(n) * 2.00
    n = np.insert(n, 0, 0.0)

    return n

def generate_blockMeshDict(Lx, Lz, Nx, Ny, Nz, Ly_list, output_file):
    num_layers = len(Ly_list)
    
    vertices = []
    blocks = []
    inlet_faces = []
    outlet_faces = []
    left_faces = []
    right_faces = []
    
    # Generate vertices
    for i, Ly in enumerate(Ly_list):
        vertices.append(f"    (0 {Ly} 0)")
        vertices.append(f"    ($Lx {Ly} 0)")
        vertices.append(f"    ($Lx {Ly} $Lz)")
        vertices.append(f"    (0 {Ly} $Lz)")
    
    # Generate blocks and faces
    for i in range(num_layers - 1):
        base_index = i * 4
        blocks.append(f"    hex ({base_index} {base_index+1} {base_index+5} {base_index+4} {base_index+3} {base_index+2} {base_index+6} {base_index+7}) ($Nx 1 $Nz) simpleGrading (1 1 1)")
        inlet_faces.append(f"            ({base_index} {base_index+3} {base_index+7} {base_index+4})")
        outlet_faces.append(f"            ({base_index+1} {base_index+5} {base_index+6} {base_index+2})")
        left_faces.append(f"            ({base_index} {base_index+4} {base_index+5} {base_index+1})")
        right_faces.append(f"            ({base_index+3} {base_index+2} {base_index+6} {base_index+7})")
    
    # Write to blockMeshDict file
    with open(output_file, 'w') as f:
        f.write("/*--------------------------------*- C++ -*----------------------------------*\\\n")
        f.write("| =========                 |                                                 |\n")
        f.write("| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |\n")
        f.write("|  \\    /   O peration     | Version:  2.2.0                                 |\n")
        f.write("|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |\n")
        f.write("|    \\/     M anipulation  |                                                 |\n")
        f.write("\\*---------------------------------------------------------------------------*/\n")
        f.write("FoamFile\n")
        f.write("{\n")
        f.write("    version     2.0;\n")
        f.write("    format      ascii;\n")
        f.write("    class       dictionary;\n")
        f.write("    object      blockMeshDict;\n")
        f.write("}\n")
        f.write("// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n")
        f.write("scale 1;\n")
        f.write(f"Lx {Lx};\n")
        f.write(f"Lz {Lz};\n\n")
        f.write(f"Nx {Nx};\n")
        f.write(f"Ny {Ny};\n")
        f.write(f"Nz {Nz};\n\n")
        f.write("vertices\n")
        f.write("(\n")
        for vertex in vertices:
            f.write(f"{vertex}\n")
        f.write(");\n\n")
        f.write("blocks\n")
        f.write("(\n")
        for block in blocks:
            f.write(f"{block}\n")
        f.write(");\n\n")
        f.write("edges\n")
        f.write("(\n")
        f.write(");\n\n")
        f.write("boundary\n")
        f.write("(\n")
        f.write("    inlet\n")
        f.write("    {\n")
        f.write("        type            cyclic;\n")
        f.write("        neighbourPatch  outlet;\n")
        f.write("        faces\n")
        f.write("        (\n")
        for face in inlet_faces:
            f.write(f"{face}\n")
        f.write("        );\n")
        f.write("    }\n\n")
        f.write("    outlet\n")
        f.write("    {\n")
        f.write("        type            cyclic;\n")
        f.write("        neighbourPatch  inlet;\n")
        f.write("        faces\n")
        f.write("        (\n")
        for face in outlet_faces:
            f.write(f"{face}\n")
        f.write("        );\n")
        f.write("    }\n\n")
        f.write("    bottomWall\n")
        f.write("    {\n")
        f.write("        type            wall;\n")
        f.write("        faces\n")
        f.write("        (\n")
        f.write("            (0 1 2 3)\n")
        f.write("        );\n")
        f.write("    }\n\n")
        f.write("    topWall\n")
        f.write("    {\n")
        f.write("        type            wall;\n")
        f.write("        faces\n")
        f.write("        (\n")
        f.write(f"            ({(num_layers-1)*4+1} {(num_layers-1)*4} {(num_layers-1)*4+3} {(num_layers-1)*4+2})\n")
        f.write("        );\n")
        f.write("    }\n\n")
        f.write("    left\n")
        f.write("    {\n")
        f.write("        type            cyclic;\n")
        f.write("        neighbourPatch  right;\n")
        f.write("        faces\n")
        f.write("        (\n")
        for face in left_faces:
            f.write(f"{face}\n")
        f.write("        );\n")
        f.write("    }\n\n")
        f.write("    right\n")
        f.write("    {\n")
        f.write("        type            cyclic;\n")
        f.write("        neighbourPatch  left;\n")
        f.write("        faces\n")
        f.write("        (\n")
        for face in right_faces:
            f.write(f"{face}\n")
        f.write("        );\n")
        f.write("    }\n")
        f.write(");\n\n")
        f.write("mergePatchPairs\n")
        f.write("(\n")
        f.write(");\n\n")
        f.write("// ************************************************************************* //\n")

# 示例使用
Lx = np.pi*4
Lz = 0.1
Nx= 87
Ny= 66
Nz= 1
Ly_list = generate_Ly_list(Ny)
print("Ly_list = ", Ly_list)
#write Ly_list to file
with open("./system/Ly_list", 'w') as f:
    for Ly in Ly_list:
        f.write(f"{Ly}\n")
#[0, 0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,1.0]
output_file = "./system/blockMeshDict"
generate_blockMeshDict(Lx, Lz, Nx,Ny, Nz, Ly_list, output_file)