from __future__ import print_function
import os, re, subprocess


def getGitVersion(tagPrefix, repoDir):
    """Return a version string with information about this git checkout.
    If the checkout is an unmodified, tagged commit, then return the tag version.
    If this is not a tagged commit, return the output of ``git describe --tags``.
    If this checkout has been modified, append "+" to the version.
    """
    # if not os.path.isdir(os.path.join(repoDir, '.git')):
    #     return None
        
    # v = subprocess.check_output(['git', '-C', repoDir, 'describe', '--tags', '--dirty', '--match=%s*'%tagPrefix]).strip().decode('utf-8')
    v = subprocess.check_output(['git', '-C', repoDir, 'describe', '--tags', '--dirty', '--long', '--all'])
    v = v.rstrip()
    print(v)
    v_parts = v.split('/')
    print(v_parts)
    description_type = v_parts[0]
    print('description_type: ', description_type)
    version = v_parts[1:]
    version = '/'.join(version)
    print(version)
    # # chop off prefix
    # assert v.startswith(tagPrefix)
    # v = v[len(tagPrefix):]
    # v = v.lstrip('-')

    # split up version parts
    parts = version.split('-')
    print(parts)    

    gitVersion = parts[0]

    # has working tree been modified?
    modified = False
    if parts[-1] == 'dirty':
        modified = True
        parts = parts[:-1]

    print(parts)    
        
    # have commits been added on top of last tagged version?
    # (git describe adds -NNN-gXXXXXXX if this is the case)
    git_sha = None
    if len(parts) > 2 and re.match(r'\d+', parts[-2]) and re.match(r'g[0-9a-f]{7}', parts[-1]):
        git_sha = parts[-1]
        distance = int(parts[-2])

        print('git_sha:', git_sha)
        print('distance:', distance)

    if (distance != 0) or (description_type != 'tags'):
        print(description_type)
        gitVersion = 'no_tag'  # then make it clear that this git sha isn't tagged

    if git_sha is not None:
        gitVersion += '+' + git_sha
    if modified:
        gitVersion += '.dirty'

    print( gitVersion )
    return gitVersion

