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

# print all .csproj files
for csproj_file in csproj_files:
    print(csproj_file)

# Extract package references from each .csproj file
def get_package_refs(csproj_file):
    tree = ET.parse(csproj_file)
    root = tree.getroot()
    package_refs = {}
    # look for <PackageReference> elements
    for package_ref in root.iter('PackageReference'):
        # get the package name and version
        include = package_ref.attrib['Include']
        version = package_ref.attrib['Version']
        package_refs[include] = version
    return package_refs

# find all package references in files ending in .csproj and add them to the package_refs dictionary
# the key is the package name and the value is the version
all_csproj_files = [os.path.join(root, file) 
                    for root, dirs, files in os.walk(solution_dir)
                    for file in files if file.endswith('.csproj')]

package_refs = {}

for csproj_file in all_csproj_files:
    package_refs.update(get_package_refs(csproj_file))

# Write the package references to the Directory.Packages.props file
with open(output_file, 'w') as f:
    f.write('<!-- For more info on central package management go to https://devblogs.microsoft.com/nuget/introducing-central-package-management/ -->\n')
    f.write('<Project>\n')
    f.write('  <PropertyGroup>\n')
    f.write('    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>\n')
    f.write('  </PropertyGroup>\n')
    f.write('  <ItemGroup>\n')

    for include, version in sorted(package_refs.items()):
        f.write(f'    <PackageVersion Include="{include}" Version="{version}" />\n')

    f.write('  </ItemGroup>\n')
    f.write('</Project>\n')

print(f'Wrote package references to {output_file}')