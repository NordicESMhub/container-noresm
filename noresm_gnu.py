
"""
NorESM container Base image for running on HPC
Contents:
  Ubuntu                        20.04
  MPICH                         3.4.1
  HDF5                          1.12.0
  NetCDF C/Fortran              4.7.4
  OpenBLAS                      0.3.9
  NorESM                        2.0.2
"""
# base image
Stage0 += baseimage(image='ubuntu:20.04')

# GNU compilers
compiler = gnu()
Stage0 += compiler

# MPICH
mpi = mpich(version='3.4.1', configure_opts=['--with-device=ch3'], toolchain=compiler.toolchain)
Stage0 += mpi

# HDF5
Stage0 += hdf5(version='1.12.0', configure_opts=['--with-zlib', '--disable-cxx', '--enable-fortran', '--enable-parallel'], toolchain=mpi.toolchain)

# NetCDF
Stage0 += netcdf(version='4.7.4', fortran=True, cxx=False, configure_opts=['--enable-netcdf4'], toolchain=mpi.toolchain)

# OpenBLAS
Stage0 += openblas(version='0.3.9', toolchain=compiler.toolchain)

# Create folders
Stage0 += shell(commands=['mkdir -p /opt/esm/.cime /opt/esm/work /opt/esm/inputdata /opt/esm/archive/cases /opt/esm/my_sandbox'])

# Clone NorESM
Stage0 += apt_get(ospackages=['cmake', 'git', 'python', 'vim', 'libxml2-dev', 'libxml2-utils', 'libxml-libxml-perl', 'subversion', 'csh', 'locales'])
Stage0 += shell(commands=['git clone -b release-noresm2.0.2 https://github.com/NorESMhub/NorESM.git /opt/esm/my_sandbox',
                          'cd /opt/esm/my_sandbox',
                          'rm -rf manage_externals',
                          'git clone -b manic-v1.1.8 https://github.com/ESMCI/manage_externals.git',
                          'sed -i.bak "s/\'checkout\'/\'checkout\', \'--trust-server-cert\', \'--non-interactive\'/" ./manage_externals/manic/repository_svn.py',
                          './manage_externals/checkout_externals -v'])
                    
# Set the locales and user
Stage0 += shell(commands=['sed -i -e "s/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/" /etc/locale.gen', 'locale-gen'])
Stage0 += environment(variables={'USER': 'ubuntu', 'LANG': 'en_US.UTF-8', 'LANGUAGE': 'en_US:en', 'LC_ALL': 'en_US.UTF-8'})

# Copy  configuration files, and prepare/execute scripts into the container
Stage0 += copy(src='.cime/*', dest='/opt/esm/.cime/')
Stage0 += copy(src='config_pes.xml', dest='/opt/esm/')
Stage0 += copy(src='prepare', dest='/opt/esm/')
Stage0 += copy(src='execute', dest='/opt/esm/')
