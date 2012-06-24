#!/usr/bin/env lua

local parse_repo = function(str)
    -- adding new server URL to database 'extra': http://mirrors.163.com/archlinux/extra/os/x86_64
    local name, url = str:match"adding new server URL to database '(.+)': (.+)"
    return name, url
end

local main = function()
    local repos = {}
    local debug_print = io.popen"pacman -T --debug 2>&1"

    for line in debug_print:lines() do
        local name, url = parse_repo(line)
        if(name and url and not repos[name]) then
            repos[name] = url
        end
    end

    debug_print:close()


    for k, v in next, repos do
        print(string.format("%s#%s", k, v))
    end
end

main()
