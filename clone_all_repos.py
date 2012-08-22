#!/usr/bin/env python

import os
repos = [#'git@github.com:stoneyrh/xware.git',
         #'git@github.com:stoneyrh/xscripts.git',
         'git://github.com/mongodb/mongo.git',
         'git://github.com/antirez/redis.git',
         'git://github.com/web2py/web2py.git',
         'git://github.com/JuliaLang/julia.git',
    ]
for repo in repos:
    command = 'git clone %s' % repo
    os.system(command)
