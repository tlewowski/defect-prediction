#!/bin/env python

import os
import re
import shutil
import pathlib

file1 = open('unique_repos.txt', 'r')
Lines = file1.readlines()
  
# Strips the newline character
for line in Lines:
    try:
   
      elems = line.strip().split("\t")
      repo = elems[0]
      print(repo)
      dir = re.findall("^.*/([a-zA-Z-_0-9.]*).git$", repo)[0]
      print(dir)
      org_dir = re.findall("^.*:(.*)/.*\.git$", repo)[0]
      print(org_dir)
      sha = elems[1]
      print("Cloning {} version {} to {}".format(repo, sha, dir))
      
      target = org_dir + "/" + dir

      if(not os.path.exists(org_dir)):
        os.mkdir(org_dir)
      
      if(not os.path.exists(target)):
        os.system("git clone " + repo + " " + target)

      os.system("cd " + target + " && " + "git checkout " + sha + " && git clean -f -d -x")
        
      
    except Exception as e:
      print(e)
    
#    os.system("cd " + dir + " && git checkout " + sha)
    
