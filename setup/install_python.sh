#!/usr/bin/env sh

BASEPATH=`pwd`
VERSIONSPATH="$BASEPATH/versions"

put() {
  echo ">>>>> $1"
}

download_source() {
  local pkgurl="$1"
  local pkgfile="$2"

  local files="$BASEPATH/files"
  mkdir -p "$files"

  cd "$files"

  if [ -f "$pkgfile" ]; then
    put "Already have ${pkgfile}"
  else
    put "Downloading ${pkgfile}"
    wget "$pkgurl"
  fi
}

unpack_source() {
  local pkgfile="$1"
  local pkgname="$2"

  put "Unpackaging $pkgfile"
  cd $BASEPATH/files

  rm -rf ${pkgname}
  case $pkgfile in
    *.tar.bz2)  tar xjf "$pkgfile" ;;
    *.tar.gz)   tar xzf "$pkgfile" ;;
    *.tar.bz)   tar xzf "$pkgfile" ;;
  esac
}

build_package() {
  local pkgname="$1"
  local pkgver="$2"
  local install_path="$VERSIONSPATH/$pkgver"

  cd "$BASEPATH/files/$pkgname"
  mkdir -p "${install_path}"

  # Temporary workaround for FS#22322
  # See http://bugs.python.org/issue10835 for upstream report
  # _pybasever="2.7"
  # sed -i "/progname =/s/python/python${_pybasever}/" Python/pythonrun.c

  # Enable built-in SQLite module to load extensions (fix FS#22122)
  # sed -i "/SQLITE_OMIT_LOAD_EXTENSION/d" setup.py

  # FS#23997
  # sed -i -e "s|^#.* /usr/local/bin/python|#!/usr/bin/python2|" Lib/cgi.py

  # Ensure that we are using the system copy of various libraries (expat, zlib and libffi),
  # rather than copies shipped in the tarball
  # rm -r Modules/expat
  # rm -r Modules/zlib
  # rm -r Modules/_ctypes/{darwin,libffi}*

  local cflags=''

  put "Configuring"
  ./configure --prefix="$install_path" --enable-shared --with-threads --enable-ipv6 \
    --enable-unicode=ucs4 --with-system-expat --with-system-ffi \
    --with-dbmliborder=gdbm:ndbm

  local jobs=`cat /proc/cpuinfo | grep processor | wc -l`
  local makeopts="-j$jobs"

  export CFLAGS='-march=x86-64 -mtune=generic -O2 -pipe -fstack-protector --param=ssp-buffer-size=4 -D_FORTIFY_SOURCE=2'

  put "make (-j${jobs})"
  make "$makeopts"

  put "make install"
  make install
}

build_package_python(){
  local pkgname="$1"
  local PYTHON="$VERSIONSPATH/$2/bin/python"

  cd "$BASEPATH/$pkgname"
  put "Installing $pkgname"

  $PYTHON setup.py install
}

install_python() {
  local pkgurl="$1"
  local pkgfile="$2"
  local pkgname="$3"
  local pkgver="$4"

  download_source $pkgurl $pkgfile
  unpack_source $pkgfile $pkgname
  build_package $pkgname $pkgver
}

install_virtualenv() {
  local pkgurl="$1"
  local pkgfile="$2"
  local pkgname="$3"
  local pyver="$4"

}

_pyver='2.7.2'
_vever='1.7.2'
#_pipver='1.1'
#_distver='0.6.27'

install_python "http://mirrors.sohu.com/python/${_pyver}/Python-${_pyver}.tar.bz2" "Python-${_pyver}.tar.bz2" "Python-${_pyver}" "${_pyver}"
#install_package "python" "http://pypi.python.org/packages/source/d/distribute/distribute-${_distver}.tar.gz" "distribute-${_distver}.tar.gz"  "distribute-${_distver}" "${_pyver}"
#install_package "python" "http://pypi.python.org/packages/source/p/pip/pip-${_pipver}.tar.gz" "pip-${_pipver}.tar.gz" "pip-${_pipver}" "${_pyver}"

#install_virtualenv "http://pypi.python.org/packages/source/v/virtualenv/virtualenv-${_vever}.tar.gz" "virtualenv-${_vever}.tar.gz" "virtualenv-${_vever}" "${_pyver}"
download_source "http://pypi.python.org/packages/source/v/virtualenv/virtualenv-${_vever}.tar.gz" "virtualenv-${_vever}.tar.gz"

