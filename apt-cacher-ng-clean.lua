#!/usr/bin/env lua

--  This script clean up archlinux pkgs cached by apt-cacher-ng
--  default path is ``/var/cache/apt-cacher-ng/alxrep''

require'lfs'

function repodir_get_old_package_list(list)
    local pkgs = {}
    for fname in next, list do
        if(not fname:match'head$' and not fname:match'db$') then
            local pkgname = fname:match'([%-a-zA-Z0-9]+)%-[0-9%.]+'
            if(pkgname) then
                pkgs[pkgname] = pkgs[pkgname] or {}
                table.insert(pkgs[pkgname], fname)
            else
                print(fname)
            end
        end
    end

    local f2remove = {}
    for pkg, flist in next, pkgs do
        if(#flist > 1) then
            table.sort(flist)
            for i = 1, #flist - 1 do
                local pname = flist[i]
                table.insert(f2remove, pname)
            end
        end
    end
    return f2remove
end

function repodir_getfilelist(dir)
    local filelist = {}
    for file in lfs.dir(dir) do
        if(file ~= '.' and file ~= '..') then
            filelist[file] = true
        end
    end
    return filelist
end

function repodir_clean(dir)
    local filelist = repodir_getfilelist(dir)
    local old_list = repodir_get_old_package_list(filelist)
    for k, v in next, old_list do
        print('Remove   ' .. v)
        os.remove(dir..'/'..v)
        os.remove(dir..'/'..v..'.head')
    end
end

local function main(path)
    local repos = {}
    for dname in lfs.dir(path) do
        if(dname~='.' and dname~='..') then
            table.insert(repos, dname)
        end
    end

    local repodirs = {}
    for _, reponame in next, repos do
        local pth = path..'/'..reponame..'/'..'os'
        for darch in lfs.dir(pth) do
            if(darch~='.' and darch~='..') then
                repodir_clean(pth..'/'..darch)
            end
        end
    end
end

local basepath = '/var/cache/apt-cacher-ng/alxrep'
main(basepath)

