import os
import xml.etree.ElementTree as ET

# Directory containing your solution
solution_dir = './'

# File to write the package references to
output_file = 'Directory.Packages.props'

# Find all .csproj files in the solution directory
csproj_files = [os.path.join(root, file)
                for root, dirs, files in os.walk(solution_dir)
                for file in files if file.endswith('.csproj')]

print(f'Found {len(csproj_files)} .csproj files in {solution_dir}')

# Update package element in each .csproj file to remove the version
def remove_package_version(csproj_file):
    tree = ET.parse(csproj_file)
    root = tree.getroot()
    package_refs = {}
    # look for <PackageReference> elements
    for package_ref in root.iter('PackageReference'):
        # get the package name and version
        include = package_ref.attrib['Include']
        version = package_ref.attrib['Version']
        package_ref.attrib.pop('Version')
        tree.write(csproj_file)
        print(f'Removed version from {include} in {csproj_file}')

# print all .csproj files
for csproj_file in csproj_files:
    print(csproj_file)
    remove_package_version(csproj_file)