#!/usr/bin/env lua

while true do
    line = io.stdin:read('*L')
    if not line then return end
    user, repo = line:match('github.com/([^/]+)/([^/]+)[^"]*"')
    if user and repo then
        print(('git clone git://github.com/%s/%s.git openresty_module-%s'):format(user, repo, repo))
    end
end

