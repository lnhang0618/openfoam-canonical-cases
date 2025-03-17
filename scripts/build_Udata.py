import numpy as np
import os
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from scipy.interpolate import interp1d
import re

def get_internal_coordinates(path):
    """
    Get the cell center of the internal cells

    input:
        - path: the path of the case

    output:
        - Internal_coordinates: the coordinates of the internal cells
    """
    # vtk file path 
    # if not exist, create the vtk file
    if not os.path.exists(os.path.join(path, "VTK")):
        os.system(f"cd {path} && foamToVTK")

    vtk_file = get_dir_file_name(os.path.join(path, "VTK"))
    vtk_path = os.path.join(path, "VTK", vtk_file)

    # load the internal.vtu
    internal_path = os.path.join(vtk_path, "internal.vtu")
    Internal_coordinates = get_vtu_cell_center(internal_path)
    return Internal_coordinates

def get_dir_file_name(path):
    """
    Get the vtk file name

    input:
        - path: the path of the case

    output:
        - vtk_file: the name of the vtk file
    """
    # Initialize variable for the directory name
    dir_name = None

    # Regex pattern to match folder ending with _<number>
    pattern = re.compile(r"_\d+$")

    # Iterate over the items in the path
    for item in os.listdir(path):
        # Check if the item is a directory and matches the pattern
        if os.path.isdir(os.path.join(path, item)) and pattern.search(item):
            dir_name = item
            break

    # Handling the case where no matching directory is found
    if dir_name is None:
        raise FileNotFoundError("No directory matching the pattern found")

    return dir_name

def get_vtu_cell_center(path):
    """
    Get the cell center of the vtu file

    input:
        - path: the path of the vtu file

    output:
        - cells_coordinates: the coordinates of the cells
    """
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(path)
    reader.Update()
    vtu_data = reader.GetOutput()

    cell_centers_filter = vtk.vtkCellCenters()
    cell_centers_filter.SetInputData(vtu_data)
    cell_centers_filter.Update()

    cell_centers = cell_centers_filter.GetOutput()
    np_cell_centers = vtk_to_numpy(cell_centers.GetPoints().GetData())

    x = np_cell_centers[:, 0]
    y = np_cell_centers[:, 1]

    cell_coordinates = np.vstack((x, y)).T

    return cell_coordinates

def interpolate_u_tau(internal_coords, gt_file):
    """
    Interpolate U/u_Tau values onto mesh points based on ground truth data.

    input:
        - internal_coords: Nx2 array of mesh cell centers (x, y)
        - gt_file: path to the ground truth file with columns [U/u_Tau, y]

    output:
        - u_tau_values: array of interpolated U/u_Tau values for each mesh point
    """
    # Load and sort ground truth data by y-coordinate
    gt_data = np.loadtxt(gt_file)
    gt_data = gt_data[gt_data[:, 1].argsort()]  # Sort by y values
    gt_y = gt_data[:, 1]
    gt_u = gt_data[:, 0]

    # Create interpolation function with extrapolation
    f = interp1d(gt_y, gt_u, kind='linear', fill_value="extrapolate")

    # Extract y-coordinates from mesh
    y_mesh = internal_coords[:, 1]

    # Perform interpolation
    u_tau_values = f(y_mesh)
    
    # Set interpolated values to 1e16 where y > 1
    u_tau_values[y_mesh > 1] = 1e16
    
    # 扩展为3维 （u, 0 , 0）
    zeros = np.zeros_like(u_tau_values)
    u_tau_3d = np.stack((u_tau_values, zeros, zeros), axis=1)

    return u_tau_3d

def get_U(u_tau_3d, u_tau, bias):
    """
    Get the U values based on U/u_tau, u_tau and bias

    input:
        - u_tau_3d: the U/u_tau values
        - u_tau: the u_tau value
        - bias: the bias value

    output:
        - U: the U values
    """
    U = u_tau_3d * u_tau
    
    # bias 扩展到3维，仅在x方向上有偏置
    bias = np.array([bias, 0, 0])
    U += bias
    
    return U

def process_folders(folder_paths, u_tau, bias):
    """
    Process multiple folders to generate U_ref.txt files.

    input:
        - folder_paths: list of paths to the folders containing OpenFOAM cases
        - u_tau: the u_tau value
        - bias: the bias value
    """
    for folder_path in folder_paths:
        print(f"Processing folder: {folder_path}")
        try:
            # Ground truth file path
            gt_path = os.path.join(folder_path, "U_uTau_ref.txt")
            
            # Check if ground truth file exists
            if not os.path.exists(gt_path):
                print(f"Ground truth file not found at {gt_path}. Skipping folder.")
                continue
            
            # Get internal coordinates
            internal_coords = get_internal_coordinates(folder_path)
            
            # Interpolate U/u_Tau values
            u_tau_values = interpolate_u_tau(internal_coords, gt_path)
            
            # Compute U values
            U = get_U(u_tau_values, u_tau, bias)
            
            # Save U values to U_ref.txt
            output_path = os.path.join(folder_path, "U_ref.txt")
            
            # 如果文件已经存在，删除
            if os.path.exists(output_path):
                os.remove(output_path)
            
            np.savetxt(output_path, U, fmt='%.6f')
            print(f"Saved U_ref.txt to {output_path}")
        
        except Exception as e:
            print(f"Error processing folder {folder_path}: {e}")

if __name__ == "__main__":
    
    folder_paths = [
        "/home/lnhang/Final_cases/classifier_data/channel",
        "/home/lnhang/Final_cases/classifier_data/couette_APG",
        "/home/lnhang/Final_cases/classifier_data/couette_FPG",
        "/home/lnhang/Final_cases/classifier_data/couette_ZPG"
    ]
    
    ## 添加folder_paths 下的所有subfolder
    subfolder_paths = []
    
    for folder_path in folder_paths:
        subfolder_paths += [os.path.join(folder_path, subfolder) for subfolder in os.listdir(folder_path)]
        
    u_tau = 0.052
    bias = -1
    
    process_folders(subfolder_paths, u_tau, bias)