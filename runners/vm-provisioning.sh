#!/usr/bin/env bash

# This script is meant to run on Ubuntu 20.04 on Azure (distribution provided by Azure)
# If you run it somewhere else, it likely will require major changes
# See comments to understand what is going on

# This should be left verbose, unless you use a distribution that doesn't use apt
# In general - you need docker and git, tmux is optional (useful for unsupervised running)
sudo apt-get update && sudo apt-get install -y git docker.io tmux

# This is just for clarity - this particular image is used for all data collection
# If you remove this line, it'll just be downloaded when triggering first metric collection
sudo docker pull tomaszlewowski/metric-gathering:1.10

#### ==== ++++ COPY & PASTE SECTION START ++++ ==== ####
## This part is a verbatim copy out of Azure File Share "Connect" section for Linux
## If you use Azure and want to use file shares, you should configure your own one
## and basically copy it here. If you don't use Azure, you can remove the whole section
## and replace it with something that sets the necessary binaries in /mnt/tools
## you can go for another directory, but if you do so, you'll need to adjust `docker run` commands later on

sudo mkdir /mnt/tools
if [ ! -d "/etc/smbcredentials" ]; then
    sudo mkdir /etc/smbcredentials
fi

# I use `metricstools` file share, you'll probably have a different one
# this affects username and, of course, password
# This is a default user created by Azure, you'll have a different one
if [ ! -f "/etc/smbcredentials/metricstools.cred" ]; then
    sudo bash -c 'echo "username=metricstools" >> /etc/smbcredentials/metricstools.cred'

    # I leave the password here, because it's not the real one. You can replace just the password, but you'll
    # probably be better off replacing the whole COPY & PASTE SECTION
    sudo bash -c 'echo "password=W0J8wqed44f6l7F+JxphyRLlRrqyDGeI2EQWDGGEWX22e+CHCMFq/PsA0LLjMFEWFSDDCVOD8+AStVPLQpQ==" >> /etc/smbcredentials/metricstools.cred'
fi
# Linux tools are pretty strict about permissions on credentials
sudo chmod 600 /etc/smbcredentials/metricstools.cred

# Set automatic mounting of the file share - remember to replace the file share name
sudo bash -c 'echo "//metricstools.file.core.windows.net/tools /mnt/tools cifs nofail,credentials=/etc/smbcredentials/metricstools.cred,dir_mode=0777,file_mode=0777,serverino,nosharesock,actimeo=30" >> /etc/fstab'

# Mount the share for current session
sudo mount -t cifs //metricstools.file.core.windows.net/tools /mnt/tools -o credentials=/etc/smbcredentials/metricstools.cred,dir_mode=0777,file_mode=0777,serverino,nosharesock,actimeo=30

# Again, you'll be better off replacing the whole section, Azure provides a neat script tailored just for your share
#### ==== ++++ COPY & PASTE SECTION END ++++ ==== ####

# Create I/O directories - for repository checkouts (projects), for outputs (reports) and for intermediate data (workspace)
mkdir -p ~/projects
mkdir -p ~/reports
mkdir -p ~/workspace

# Clone current version of the collection scripts and list of used commits
# You need that for reproduction and for PMD, but not for any new research that uses only JavaMetrics / JavaMetrics2
# To run reproduction, you can use tag v1.0-data-collection or anything nearby - list of commits didn't change much between those
cd ~ && git clone https://github.com/tlewowski/defect-prediction.git

# Set up SSH keys for GitHub - you'll need them to run JavaMetrics2 (aka JavaMetricsPP)
mkdir -p ~/.ssh
# And again, SSH is strict about permissions
chmod 700 ~/.ssh

# This is obviously a fake key I've generated to get an example
# You need to replace it with your own, one that is added to GitHub account
# Remember not to push the actual key to the repository, even if the repository is private!
# If you're concerned with security of adding key here, you're right, it's not the best practice
# but it works well for a quick-and-dirty deployments like this one
# Just don't push it anywhere.
echo <<HERE
-----BEGIN OPENSSH PRIVATE KEY-----
MIIEowIBAAKCAQEAqIJ8dwjg8jQmbfxpLQhfiOB5Onzs+wsMY0f/D/XStV1KjI+B
mAIt78OTBgKU5VfWVe3cpggiFWmAahNeiawSpZ9Ojw2vfBsT8wTe1W6uInmB5Tc8
uFcy3yV8C8ixTMFFaYZRed7T22Jx9DmaDHcBWteqpGk3LLsZZOAi5jzJSH5ZSM+F
hByHWp8AnhzGbWkZHxA0VeSGHku7B4UYUfk44WPl0dSv4Q5vYVLT9n2P+0ZI1fEb
k2lG00C7QKXwMymA8lOnVdTlypYPo/d4EgAoKU54Te5SQHeSYjWA8aGC2kC6/aur
fwjD3krLKsmjkUSK4sFtyo2O8mGT35GT5oG4uwIDAQABAoIBAHX+4S7tLa8MK3jK
zc811Mfg/6KgBcWIqAUBTi6b4Q8Uo3YnqwSJSidhWJtVxXOO/UwwglhUy6EYvk4J
ACMBNhF5qyXq3F3YDDEY0Py9Qvxq/zVFZ6RhkwLEmccaomRv1a4d2wGuscUme0sb
5q4hyvYUnK4B6xvMa+zCMk3sdLnocmOtaZLAIFwAZT9zQYgOrnlpjJtyamsPyYKZ
ddwD806fPqpRaN0AKk19Q2wtkMZYC8KF/RCq0erMTqElhHHTAMK9gdXEt1Keyhdh
xOKE+Hx3zOURx5cXYn/cxVm+ZXEGZMFhXId+gEd9oUVOCEXX7KE2QZfJNBgL3u1g
eKnBcMECgYEA66eI49UYCAy0X1HJQBSH3zToPJI8UIEDy9N4SLh+S1HpX7cHougd
4qd/k9i13eYm25eTMV/cHVWgUAdT/KVmZy6lCsSOK3/XjJ9plnymSahaf+wxOf/Z
RWOeUV+qqTh3eCOLghoah0vuI6X2W8pp5kriW9Gj7uHEjURom6LsrKECgYEAtw7o
9nEGrYbNG4t7hbQ0A0jWup0N3bN+QQaRuF5G/a3PoeeLv50smZHB+XrOXiIVHJOF
6LEIjFkrmTLncz4EEFgFuKL6qkv1rEfQb56ziXJls4zZwjYaaBC1M8MlKUi7ol4G
779cypORP8s07XwiqdpbFeNdPp0iZpkzJQYrK9sCgYBpv091da2IBzN1xry5rbzf
E93XOIQqWAq9D5NdhrTd1c8U7YxWtTSb/jAIx2mtPtdXGSirMmoTG9aJsxAkQpC2
Yr8bGuL1cDPo3axDJIJ2cT7TQslATqhQNAjaWUS7FSS/W6wB4PbgmdkuVA4+WJG3
DwmOzH909gj+n6EVnkH4oQKBgQC0SkkDPvpWuWcU8+EqI/r+KSTjEn9vlLKKFJA8
Rw4gFqliSgwHIiOk9DtZHKxXZbXpORovvPwwTjp0XgA6LiAOgMLRwCKkyr8heHE/
HcyxWCv2FIj7kBGd4Ka2XkIhUPMLzROD2LLpCUGK1PZB13rEUrxW6GETo+sXpVcL
5fFq9QKBgEOafqv4z3c3BxkpNH/Se2XmZNPbtHAsClaB+GzibV/XHoWxy2h2CMnp
6XW8MwD48rT8MStvmzBBk1JXWH3iEPzu00ZxQuu686ljIY5R89H1Ar260eNOYTP5
GUjP2dMygEf+5TS9g/lKAa90pxayUQPnACPKUYdrhcU/U+VfFPLM
BAUGBw==
-----END OPENSSH PRIVATE KEY-----
HERE > ~/.ssh/id_rsa

# And remember to add proper permissions to the private key
chmod 600 ~/.ssh/id_rsa
