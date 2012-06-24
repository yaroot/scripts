_pybasever="2.7"

PYENV_PATH="$HOME/.pyenv"
CACHE_DIR="$PYENV_PATH/cache"
TMP_DIR="$PYENV_PATH/tmp"
INSTALL_PATH="$PYENV_PATH/versions/$VER"

mkdir -p $PYENV_PATH

put() {
  echo ">>>>> $1"
}

download_source() {
  local url="$1"
  local fname=`basename $url`

  mkdir -p $CACHE_DIR
  cd $CACHE_DIR

  if [ -f "$fname" ]; then
    put "Already have file ${fname}"
    return
  fi

  put "Downloading $fname"
  wget $url
}

unpack_source() {
  local fname=`basename $1`

  rm -rf $TMP_DIR
  mkdir -p $TMP_DIR
  cd $TMP_DIR
  cp "$CACHE_DIR/$fname" "$TMP_DIR"

  cd "$TMP_DIR"
  tar jxf "$fname"
}

build_source() {
  local pkgname="$1"
  local pkgid="$2"

  local builddir="$TMP_DIR/$pkgname"
  local prefix="$PYENV_PATH/versions/$pkgid"
  mkdir -p "$prefix"

  cd "$builddir"

  # Temporary workaround for FS#22322
  # See http://bugs.python.org/issue10835 for upstream report
  sed -i "/progname =/s/python/python${_pybasever}/" Python/pythonrun.c

  # Enable built-in SQLite module to load extensions (fix FS#22122)
  sed -i "/SQLITE_OMIT_LOAD_EXTENSION/d" setup.py

  # FS#23997
  # sed -i -e "s|^#.* /usr/local/bin/python|#!/usr/bin/python2|" Lib/cgi.py

  # Ensure that we are using the system copy of various libraries (expat, zlib and libffi),
  # rather than copies shipped in the tarball
  rm -r Modules/expat
  rm -r Modules/zlib
  rm -r Modules/_ctypes/{darwin,libffi}*

  export OPT="${CFLAGS}"
  put "Configuring"
  ./configure --prefix="$INSTALL_PATH" --enable-shared --with-threads --enable-ipv6 \
    --enable-unicode=ucs4 --with-system-expat --with-system-ffi \
    --with-dbmliborder=gdbm:ndbm

  local jobs=`cat /proc/cpuinfo | grep processor | wc -l`
  local makeopts="-j$jobs"

  put "Making ($jobs jobs)"
  make "$makeopts"

  put "Installing"
  make install

  put "Cleaning up"
  rm ${TMP_DIR}
}

install_package() {
  local package_url="$1"
  local package_name="$2"
  local package_id="$3"

  download_source $package_url
  unpack_source $package_url
  build_source $package_name $package_id
}



install_package "http://mirrors.sohu.com/python/2.7.1/Python-2.7.1.tar.bz2" "Python-2.7.1" "2.7.1"



