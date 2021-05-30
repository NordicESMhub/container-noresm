FROM centos:7 AS build

# Intel Parallel Studio XE
RUN yum install -y \
        gcc \
        gcc-c++ \
        gcc-gfortran \
        make \
        which && \
    rm -rf /var/cache/yum/*
COPY parallel_studio_xe_2020_update4_cluster_edition.tgz /var/tmp/parallel_studio_xe_2020_update4_cluster_edition.tgz
COPY license.lic /var/tmp/license.lic
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/parallel_studio_xe_2020_update4_cluster_edition.tgz -C /var/tmp -z && \
    sed -i -e 's/^#\?\(COMPONENTS\)=.*/\1=intel-conda-index-tool__x86_64;intel-comp__x86_64;intel-comp-32bit__x86_64;intel-comp-doc__noarch;intel-comp-l-all-common__noarch;intel-comp-l-all-vars__noarch;intel-comp-nomcu-vars__noarch;intel-comp-ps-32bit__x86_64;intel-comp-ps__x86_64;intel-comp-ps-ss-bec__x86_64;intel-comp-ps-ss-bec-32bit__x86_64;intel-openmp__x86_64;intel-openmp-32bit__x86_64;intel-openmp-common__noarch;intel-openmp-common-icc__noarch;intel-openmp-common-ifort__noarch;intel-openmp-ifort__x86_64;intel-openmp-ifort-32bit__x86_64;intel-tbb-libs-32bit__x86_64;intel-tbb-libs__x86_64;intel-tbb-libs-common__noarch;intel-idesupport-icc-common-ps__noarch;intel-conda-intel-openmp-linux-64-shadow-package__x86_64;intel-conda-intel-openmp-linux-32-shadow-package__x86_64;intel-conda-icc_rt-linux-64-shadow-package__x86_64;intel-icc__x86_64;intel-c-comp-common__noarch;intel-icc-common__noarch;intel-icc-common-ps__noarch;intel-icc-doc__noarch;intel-icc-ps__x86_64;intel-icc-ps-ss-bec__x86_64;intel-icx__x86_64;intel-icx-common__noarch;intel-ifort__x86_64;intel-ifort-common__noarch;intel-ifort-doc__noarch;intel-mkl-common__noarch;intel-mkl-core__x86_64;intel-mkl-core-rt__x86_64;intel-mkl-doc__noarch;intel-mkl-doc-ps__noarch;intel-mkl-gnu__x86_64;intel-mkl-gnu-rt__x86_64;intel-mkl-cluster__x86_64;intel-mkl-cluster-rt__x86_64;intel-mkl-common-ps__noarch;intel-mkl-core-ps__x86_64;intel-mkl-pgi__x86_64;intel-mkl-pgi-rt__x86_64;intel-conda-mkl-linux-64-shadow-package__x86_64;intel-conda-mkl-static-linux-64-shadow-package__x86_64;intel-conda-mkl-devel-linux-64-shadow-package__x86_64;intel-conda-mkl-include-linux-64-shadow-package__x86_64;intel-mkl-common-c__noarch;intel-mkl-core-c__x86_64;intel-mkl-common-c-ps__noarch;intel-mkl-cluster-c__noarch;intel-mkl-tbb__x86_64;intel-mkl-tbb-rt__x86_64;intel-mkl-pgi-c__x86_64;intel-mkl-gnu-c__x86_64;intel-mkl-common-f__noarch;intel-mkl-core-f__x86_64;intel-mkl-cluster-f__noarch;intel-mkl-gnu-f-rt__x86_64;intel-mkl-gnu-f__x86_64;intel-mkl-f95-common__noarch;intel-mkl-f__x86_64;intel-tbb-devel__x86_64;intel-tbb-common__noarch;intel-tbb-doc__noarch;intel-conda-tbb-linux-64-shadow-package__x86_64;intel-conda-tbb-devel-linux-64-shadow-package__x86_64;intel-imb__x86_64;intel-mpi-rt__x86_64;intel-mpi-sdk__x86_64;intel-mpi-doc__x86_64;intel-mpi-samples__x86_64;intel-conda-impi_rt-linux-64-shadow-package__x86_64;intel-conda-impi-devel-linux-64-shadow-package__x86_64;intel-icsxe__noarch;intel-psxe-common__noarch;intel-psxe-doc__noarch;intel-icsxe-doc__noarch;intel-psxe-licensing__noarch;intel-psxe-licensing-doc__noarch;intel-icsxe-pset/g' \
        -e 's|^#\?\(PSET_INSTALL_DIR\)=.*|\1=/usr/local/intel|g' \
        -e 's/^#\?\(ACCEPT_EULA\)=.*/\1=accept/g' \
        -e 's/^#\?\(ACTIVATION_TYPE\)=.*/\1=license_file/g' \
        -e 's|^#\?\(ACTIVATION_LICENSE_FILE\)=.*|\1=/var/tmp/license.lic|g' /var/tmp/parallel_studio_xe_2020_update4_cluster_edition/silent.cfg && \
    cd /var/tmp/parallel_studio_xe_2020_update4_cluster_edition && ./install.sh --silent=silent.cfg && \
    rm -rf /var/tmp/parallel_studio_xe_2020_update4_cluster_edition.tgz /var/tmp/parallel_studio_xe_2020_update4_cluster_edition
RUN echo "source /usr/local/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64" >> /etc/bashrc

RUN rm -rf /usr/local/intel/compilers_and_libraries_2020.4.304/linux/mpi

RUN yum install -y \
        librdmacm-devel && \
    rm -rf /var/cache/yum/*

# UCX version 1.10.0
RUN yum install -y \
        binutils-devel \
        file \
        make \
        numactl-devel \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openucx/ucx/releases/download/v1.10.0/ucx-1.10.0.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/ucx-1.10.0.tar.gz -C /var/tmp -z && \
    /bin/bash -c "source /usr/local/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64 && \
    cd /var/tmp/ucx-1.10.0 &&  CC=icc CXX=icpc F77=ifort F90=ifort FC=ifort ./configure --prefix=/usr/local/ucx --enable-optimizations --with-rdmacm --without-cuda && \
    make -j$(nproc) && \
    make -j$(nproc) install" && \
    rm -rf /var/tmp/ucx-1.10.0 /var/tmp/ucx-1.10.0.tar.gz
ENV CPATH=/usr/local/ucx/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/ucx/lib:$LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH

# SLURM PMI2 version 20.11.7
RUN yum install -y \
        bzip2 \
        file \
        make \
        perl \
        tar \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://download.schedmd.com/slurm/slurm-20.11.7.tar.bz2 && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/slurm-20.11.7.tar.bz2 -C /var/tmp -j && \
    /bin/bash -c "source /usr/local/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64 && \
    cd /var/tmp/slurm-20.11.7 &&  CC=icc CXX=icpc F77=ifort F90=ifort FC=ifort ./configure --prefix=/usr/local/slurm-pmi2 && \
    cd /var/tmp/slurm-20.11.7 && \
    make -C contribs/pmi2 install" && \
    rm -rf /var/tmp/slurm-20.11.7 /var/tmp/slurm-20.11.7.tar.bz2

# OpenMPI version 4.1.0
RUN yum install -y \
        bzip2 \
        file \
        hwloc \
        make \
        numactl-devel \
        openssh-clients \
        perl \
        tar \
        wget && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://www.open-mpi.org/software/ompi/v4.1/downloads/openmpi-4.1.0.tar.bz2 && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/openmpi-4.1.0.tar.bz2 -C /var/tmp -j && \
    /bin/bash -c "source /usr/local/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64 && \
    cd /var/tmp/openmpi-4.1.0 &&  CC=icc CXX=icpc F77=ifort F90=ifort FC=ifort ./configure --prefix=/usr/local/openmpi --with-hwloc=internal --with-libevent=internal --with-pmi=/usr/local/slurm-pmi2 --with-ucx=/usr/local/ucx --with-verbs --without-cuda FFLAGS=-fallow-argument-mismatch && \
    make -j$(nproc) && \
    make -j$(nproc) install" && \
    rm -rf /var/tmp/openmpi-4.1.0 /var/tmp/openmpi-4.1.0.tar.bz2
ENV LD_LIBRARY_PATH=/usr/local/openmpi/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/openmpi/bin:$PATH

# HDF5 version 1.12.0
RUN yum install -y \
        bzip2 \
        file \
        make \
        wget \
        zlib-devel && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp http://www.hdfgroup.org/ftp/HDF5/releases/hdf5-1.12/hdf5-1.12.0/src/hdf5-1.12.0.tar.bz2 && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/hdf5-1.12.0.tar.bz2 -C /var/tmp -j && \
    /bin/bash -c "source /usr/local/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64 && \
    cd /var/tmp/hdf5-1.12.0 &&  CC=mpicc CXX=mpicxx F77=mpif77 F90=mpif90 FC=mpifort ./configure --prefix=/usr/local/hdf5 --disable-cxx --enable-fortran --enable-parallel --with-zlib && \
    make -j$(nproc) && \
    make -j$(nproc) install" && \
    rm -rf /var/tmp/hdf5-1.12.0 /var/tmp/hdf5-1.12.0.tar.bz2
ENV CPATH=/usr/local/hdf5/include:$CPATH \
    HDF5_DIR=/usr/local/hdf5 \
    LD_LIBRARY_PATH=/usr/local/hdf5/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/hdf5/lib:$LIBRARY_PATH \
    PATH=/usr/local/hdf5/bin:$PATH

# NetCDF version 4.7.4, NetCDF Fortran version 4.5.3
RUN yum install -y \
        ca-certificates \
        file \
        libcurl-devel \
        m4 \
        make \
        wget \
        zlib-devel && \
    rm -rf /var/cache/yum/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/Unidata/netcdf-c/archive/v4.7.4.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v4.7.4.tar.gz -C /var/tmp -z && \
    /bin/bash -c "source /usr/local/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64 && \
    cd /var/tmp/netcdf-c-4.7.4 &&  CC=mpicc CXX=mpicxx F77=mpif77 F90=mpif90 FC=mpifort ./configure --prefix=/usr/local/netcdf --enable-netcdf4 && \
    make -j$(nproc) && \
    make -j$(nproc) install" && \
    rm -rf /var/tmp/netcdf-c-4.7.4 /var/tmp/v4.7.4.tar.gz
ENV CPATH=/usr/local/netcdf/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/netcdf/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/netcdf/lib:$LIBRARY_PATH \
    PATH=/usr/local/netcdf/bin:$PATH
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/Unidata/netcdf-fortran/archive/v4.5.3.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v4.5.3.tar.gz -C /var/tmp -z && \
    /bin/bash -c "source /usr/local/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64 && \
    cd /var/tmp/netcdf-fortran-4.5.3 &&  CC=mpicc CXX=mpicxx F77=mpif77 F90=mpif90 FC=mpifort ./configure --prefix=/usr/local/netcdf && \
    make -j$(nproc) && \
    make -j$(nproc) install" && \
    rm -rf /var/tmp/netcdf-fortran-4.5.3 /var/tmp/v4.5.3.tar.gz

RUN mkdir -p /opt/esm/.cime /opt/esm/work /opt/esm/inputdata /opt/esm/archive/cases /opt/esm/my_sandbox

RUN yum install -y \
        cmake \
        csh \
        git \
        locales \
        perl-XML-LibXML \
        python \
        subversion \
        vim && \
    rm -rf /var/cache/yum/*

RUN git clone -b release-noresm2.0.4 https://github.com/NorESMhub/NorESM.git /opt/esm/my_sandbox && \
    cd /opt/esm/my_sandbox && \
    rm -rf manage_externals && \
    git clone -b manic-v1.1.8 https://github.com/ESMCI/manage_externals.git && \
    sed -i.bak "s/'checkout'/'checkout', '--trust-server-cert', '--non-interactive'/" ./manage_externals/manic/repository_svn.py && \
    ./manage_externals/checkout_externals -v

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    USER=centos

COPY cime/* /opt/esm/.cime/

COPY config_pes.xml /opt/esm/

COPY prepare /opt/esm/

COPY execute /opt/esm/execute

RUN mv /opt/esm/.cime/Depends.intel-container /opt/esm/my_sandbox/cime/config/cesm/machines



