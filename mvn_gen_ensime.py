#!/usr/bin/env python2
"""
.ensime example
https://github.com/ensime/ensime-server/wiki/Example-Configuration-File

"""

import sys
import os
import subprocess


DEFAULT_JAVA_HOME = '/usr/lib/jvm/default'
if 'JAVA_HOME' in os.environ:
    DEFAULT_JAVA_HOME = os.environ['JAVA_HOME']


def dump_props(name, props):
    print ' ', name
    for a, b in props.items():
        print '   ', a, '  ->  ', b
    if not props:
        print '    <empty>'


def add_name(props, proj_props, base_dir):
    name = os.path.dirname(base_dir)
    props['name'] = name
    proj_props['name'] = name


def shell_out(*args):
    return subprocess.check_output(args, shell=True)


def find_deps(lines):
    found = False
    for line in lines.splitlines():
        if found:
            return line
        if line.startswith('[INFO] Dependencies classpath:'):
            found = True


def format_classpath(raw):
    return list(set(raw.split(':')))


def get_deps(scope=''):
    cmd = "mvn dependency:build-classpath -DincludeScope=%s" % scope
    output = shell_out(cmd)
    deps = find_deps(output)
    return format_classpath(deps)


def scala_ver(deps):
    lib_path = 'org/scala-lang/scala-library/'
    for d in deps:
        if lib_path in d:
            ss = d[d.find(lib_path)+len(lib_path):]
            return ss[:ss.find('/')]


def deps_to_source_jar(p):
    if p.endswith('.jar'):
        return p[:-4] + '-sources.jar'
    return p


def add_path(props, proj_props, base_dir):
    deps = get_deps(scope='')
    # proj_props['compile-deps'] = 
    # proj_props[''] = get_deps(scope='')
    # proj_props['compile-deps'] = get_deps(scope='')
    # proj_props['compile-deps'] = get_deps(scope='')
    proj_props['compile-deps'] = deps
    proj_props['runtime-deps'] = deps
    proj_props['reference-source-roots'] = map(deps_to_source_jar, deps)

    props['scala-version'] = scala_ver(deps)
    proj_props['source-roots'] = [
        os.path.join(base_dir, 'src/main/scala'),
        os.path.join(base_dir, 'src/test/scala')
    ]
    proj_props['target'] = os.path.join(base_dir, 'target/classes')
    proj_props['test-target'] = os.path.join(base_dir, 'target/classes')
    proj_props['depends-on-modules'] = None
    # target
    # test-target
    # compile-deps
    # runtime-deps
    # reference-source-roots


def lb(f): f.write('\n')
def ob(f): f.write('(')
def cb(f): f.write(')')
def quote(f, s): f.write('"%s" ' % s)


def dump_elisp(f, data):
    _t = type(data)
    if _t == dict:
        ob(f)
        lb(f)
        for k, v in data.items():
            # :key `value`
            f.write(':%s ' % k)
            dump_elisp(f, v)
            lb(f)
        cb(f)
        lb(f)
    elif _t in (str, unicode):
        quote(f, data)
    elif data is None or data == False:
        f.write('nil')
    elif data == True:
        f.write('t')
    elif _t in (list, set):
        ob(f)
        for v in data:
            dump_elisp(f, v)
        cb(f)
        lb(f)
    else:
        raise ValueError("serialization for type(%s) is not implemented" % _t)


def dump_ensime_config(props, proj_props):
    dump_props('main', props)
    dump_props('project', proj_props)
    props['subprojects'] = [proj_props]
    with open('.ensime', 'w') as f:
        dump_elisp(f, props)


def main():
    base_dir = os.path.abspath('.')
    props = {
        'java-home': DEFAULT_JAVA_HOME,
        'reference-source-roots': [os.path.join(DEFAULT_JAVA_HOME, 'src.zip')],
        'root-dir': base_dir,
        'cache-dir': os.path.join(base_dir, '.ensime_cache'),
    }
    proj_props = {}

    add_name(props, proj_props, base_dir)
    add_path(props, proj_props, base_dir)
    dump_ensime_config(props, proj_props)


def check_pom():
    return os.path.isfile('pom.xml')


if __name__ == '__main__':
    if not check_pom():
        print 'Please run %s in maven project root' % sys.argv[0]
        sys.exit(1)
    main()

