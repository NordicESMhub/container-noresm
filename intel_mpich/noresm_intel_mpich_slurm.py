"""
HPC Base image
Contents:
  Centos                        7
  Intel compiler & MKL          2020 Update 4
"""

# base image
Stage0 += baseimage(image='centos:{}'.format(7), _as='build')

compiler = intel_psxe(eula=True, license=os.getenv('INTEL_LICENSE_FILE',default='license.lic'), \
                      prefix='/usr/local/intel', \
                      tarball='parallel_studio_xe_2020_update4_cluster_edition.tgz', \
                      ospackages=['gcc', 'gcc-c++', 'gcc-gfortran', 'make', 'which'], \
                      components=['intel-conda-index-tool__x86_64','intel-comp__x86_64','intel-comp-32bit__x86_64','intel-comp-doc__noarch','intel-comp-l-all-common__noarch','intel-comp-l-all-vars__noarch','intel-comp-nomcu-vars__noarch','intel-comp-ps-32bit__x86_64','intel-comp-ps__x86_64','intel-comp-ps-ss-bec__x86_64','intel-comp-ps-ss-bec-32bit__x86_64','intel-openmp__x86_64','intel-openmp-32bit__x86_64','intel-openmp-common__noarch','intel-openmp-common-icc__noarch','intel-openmp-common-ifort__noarch','intel-openmp-ifort__x86_64','intel-openmp-ifort-32bit__x86_64','intel-tbb-libs-32bit__x86_64','intel-tbb-libs__x86_64','intel-tbb-libs-common__noarch','intel-idesupport-icc-common-ps__noarch','intel-conda-intel-openmp-linux-64-shadow-package__x86_64','intel-conda-intel-openmp-linux-32-shadow-package__x86_64','intel-conda-icc_rt-linux-64-shadow-package__x86_64','intel-icc__x86_64','intel-c-comp-common__noarch','intel-icc-common__noarch','intel-icc-common-ps__noarch','intel-icc-doc__noarch','intel-icc-ps__x86_64','intel-icc-ps-ss-bec__x86_64','intel-icx__x86_64','intel-icx-common__noarch','intel-ifort__x86_64','intel-ifort-common__noarch','intel-ifort-doc__noarch','intel-mkl-common__noarch','intel-mkl-core__x86_64','intel-mkl-core-rt__x86_64','intel-mkl-doc__noarch','intel-mkl-doc-ps__noarch','intel-mkl-gnu__x86_64','intel-mkl-gnu-rt__x86_64','intel-mkl-cluster__x86_64','intel-mkl-cluster-rt__x86_64','intel-mkl-common-ps__noarch','intel-mkl-core-ps__x86_64','intel-mkl-pgi__x86_64','intel-mkl-pgi-rt__x86_64','intel-conda-mkl-linux-64-shadow-package__x86_64','intel-conda-mkl-static-linux-64-shadow-package__x86_64','intel-conda-mkl-devel-linux-64-shadow-package__x86_64','intel-conda-mkl-include-linux-64-shadow-package__x86_64','intel-mkl-common-c__noarch','intel-mkl-core-c__x86_64','intel-mkl-common-c-ps__noarch','intel-mkl-cluster-c__noarch','intel-mkl-tbb__x86_64','intel-mkl-tbb-rt__x86_64','intel-mkl-pgi-c__x86_64','intel-mkl-gnu-c__x86_64','intel-mkl-common-f__noarch','intel-mkl-core-f__x86_64','intel-mkl-cluster-f__noarch','intel-mkl-gnu-f-rt__x86_64','intel-mkl-gnu-f__x86_64','intel-mkl-f95-common__noarch','intel-mkl-f__x86_64','intel-tbb-devel__x86_64','intel-tbb-common__noarch','intel-tbb-doc__noarch','intel-conda-tbb-linux-64-shadow-package__x86_64','intel-conda-tbb-devel-linux-64-shadow-package__x86_64','intel-imb__x86_64','intel-mpi-rt__x86_64','intel-mpi-sdk__x86_64','intel-mpi-doc__x86_64','intel-mpi-samples__x86_64','intel-conda-impi_rt-linux-64-shadow-package__x86_64','intel-conda-impi-devel-linux-64-shadow-package__x86_64','intel-icsxe__noarch','intel-psxe-common__noarch','intel-psxe-doc__noarch','intel-icsxe-doc__noarch','intel-psxe-licensing__noarch','intel-psxe-licensing-doc__noarch','intel-icsxe-pset'])          
Stage0 += compiler
Stage0 += shell(commands=['rm -rf /usr/local/intel/compilers_and_libraries_2020.4.304/linux/mpi'])

# LIBRDMACM-DEVEL
Stage0 += yum(ospackages=['librdmacm-devel'])

# UCX
Stage0 += ucx(version='1.10.0', cuda=False,  configure_opts=['--enable-optimizations', '--with-rdmacm'], toolchain=compiler.toolchain)

# PMI2
Stage0 += slurm_pmi2(version='20.11.7', toolchain=compiler.toolchain)

# MPICH
mpi = mpich(version='3.4.1', configure_opts=['FFLAGS=-fallow-argument-mismatch', 'FCFLAGS=-fallow-argument-mismatch',
                                             '--enable-fast=O3', '--with-ucx=/usr/local/ucx', '--with-device=ch4:ucx', '--enable-shared'], toolchain=compiler.toolchain)
Stage0 += mpi

# HDF5
Stage0 += hdf5(version='1.12.0', configure_opts=['--with-zlib', '--disable-cxx', '--enable-fortran', '--enable-parallel'], toolchain=mpi.toolchain)

# NetCDF
Stage0 += netcdf(version='4.7.4', fortran=True, cxx=False, configure_opts=['--enable-netcdf4'], toolchain=mpi.toolchain)

# Create folders
Stage0 += shell(commands=['mkdir -p /opt/esm/.cime /opt/esm/work /opt/esm/inputdata /opt/esm/archive/cases /opt/esm/my_sandbox'])

# Clone NorESM
Stage0 += yum(ospackages=['perl-XML-LibXML', 'subversion', 'cmake', 'git', 'python', 'vim', 'csh', 'locales'])
Stage0 += shell(commands=['git clone -b release-noresm2.0.4 https://github.com/NorESMhub/NorESM.git /opt/esm/my_sandbox',
                          'cd /opt/esm/my_sandbox',
                          'rm -rf manage_externals',
                          'git clone -b manic-v1.1.8 https://github.com/ESMCI/manage_externals.git',
                          'sed -i.bak "s/\'checkout\'/\'checkout\', \'--trust-server-cert\', \'--non-interactive\'/" ./manage_externals/manic/repository_svn.py',
                          './manage_externals/checkout_externals -v'])
                    
# Set the locales and user
Stage0 += environment(variables={'USER': 'centos', 'LANG': 'en_US.UTF-8', 'LANGUAGE': 'en_US:en', 'LC_ALL': 'en_US.UTF-8'})

# Copy  configuration files, and prepare/execute scripts into the container
Stage0 += copy(src='cime/*', dest='/opt/esm/.cime/')
Stage0 += copy(src='config_pes.xml', dest='/opt/esm/')
Stage0 += copy(src='prepare', dest='/opt/esm/')
Stage0 += copy(src='execute', dest='/opt/esm/execute')
Stage0 += shell(commands=['mv /opt/esm/.cime/Depends.intel-container /opt/esm/my_sandbox/cime/config/cesm/machines'])
