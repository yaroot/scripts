URL="http://mirrors.sohu.com/python/2.7.1/Python-2.7.1.tar.bz2"
VER="2.7.1"
_pybasever="2.7"
FILENAME="`basename $URL`"

PYENV_PATH="$HOME/.pyenv"
CACHE_DIR="$PYENV_PATH/cache"
TMP_DIR="$PYENV_PATH/tmp"
INSTALL_PATH="$PYENV_PATH/versions/$VER"


put() {
  echo ">>>>> $1"
}

build_check_dirs() {
  mkdir -p $CACHE_DIR
  rm -rf $TMP_DIR
  mkdir -p $TMP_DIR
  mkdir -p $INSTALL_PATH
}

build_cleanup() {
  rm -rf $TMP_DIR
}

build_download_source() {
  if [ ! -f "$CACHE_DIR/$FILENAME" ]; then
    put "Downloading source"
    cd "$CACHE_DIR"
    wget $URL
  else
    put "Source file already exists"
  fi
}

build_compile_pre() {
  cp "$CACHE_DIR/$FILENAME" "$TMP_DIR"
  put "Copy file to tmp directory"
  cd "$TMP_DIR"
  put "Unpacking tarball"
  tar jxf "$FILENAME"
}

build_compile_config() {
  cd "$TMP_DIR/Python-$VER"

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

  popd > /dev/null
}

build_compile_make() {
  "$TMP_DIR/Python-$VER"

  local jobs=`cat /proc/cpuinfo | grep processor | wc -l`
  local makeopts="-j$jobs"

  put "Making ($jobs jobs)"
  make "$makeopts"

  popd > /dev/null
}

build_compile_install() {
  cd "$TMP_DIR/Python-$VER"

  put "Installing"
  make install

  popd > /dev/null
}

build_process() {
  build_check_dirs
  build_download_source

  build_compile_pre
  build_compile_config
  build_compile_make
  build_compile_install

  build_cleanup
}

main() {
  local py_dir="${PYENV_PATH}/$VER"
  if [ -d "$py_dir" ]; then
    put "You have python $VER installed in $py_dir"
    exit
  fi

  build_process
}

main

