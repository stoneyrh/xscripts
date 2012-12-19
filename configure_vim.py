'''
This is the script to configure vim as an IDE
This script will download necessary files automatically
This script requires Administrator privilege to run under Windows
After installation, the following commands could be a reference:
    Ctrl + F12  - Run ctags under current directory
    TlistToggle - Toggle Taglist window
    :WMToggle   - Toggle Windows Manager
'''
import os
import sys
import urllib
import zipfile
import subprocess
import shutil
import tarfile

vimrc_lines = '''map <C-F12> :!ctags -R --c++-kinds=+p --fields=+iaS --extra=+q .<CR>
let Tlist_Show_One_File=1
let Tlist_Exit_OnlyWindow=1
set cscopequickfix=s-,c-,d-,i-,t-,e-
set nocp
filetype plugin on
let g:SuperTabDefaultCompletionType="context"
let g:miniBufExplMapWindowNavVim = 1
let g:miniBufExplMapWindowNavArrows = 1
let g:miniBufExplMapCTabSwitchBufs = 1
let g:miniBufExplModSelTarget = 1
let g:miniBufExplMoreThanOne = 0
let g:NERDTree_title="[NERDTree]"
let g:winManagerWindowLayout="NERDTree|TagList"

function! NERDTree_Start()
    exec 'NERDTree'
endfunction

function! NERDTree_IsValid()
    return 1
endfunction

nmap wm :WMToggle<CR>

if has("win32")
	au GUIEnter * simalt ~x
endif

set autoindent
set tabstop=4
set shiftwidth=4
set expandtab
set nobackup
set number
set mouse=a'''

def unzip(name, to):
    try:
        zfile = zipfile.ZipFile(name)
        for name in zfile.namelist():
            dirname, filename = os.path.split(name)
            dirname = os.path.join(to, dirname)
            if not os.path.exists(dirname):
                os.mkdir(dirname)
            if filename:
                filename = os.path.join(dirname, filename)
                file = open(filename, 'wb')
                file.write(zfile.read(name))
                file.close()
        return True
    except Exception, e:
        print e
    return False

def local_file_of(name):
    if not os.path.exists('download'):
        os.mkdir('download')
    return os.path.join('download', name)

def has_downloaded(name):
    return os.path.exists(name)

def download(filename, url):
    try:
        content = urllib.urlopen(url).read()
        file = open(filename, 'wb')
        file.write(content)
        file.close()
        return True
    except Exception, e:
        print e
    return False

def user_home():
    return os.path.expanduser('~')

def output_of_cmd(cmd):
    process = subprocess.Popen(cmd, stdout = subprocess.PIPE, shell = True)
    output, error = process.communicate()
    if error:
        return error
    return output

def is_windows():
    return sys.platform.startswith('win')

def vim_home():
    if is_windows():
        return os.path.join(program_files(), 'Vim')
    return output_of_cmd('which vim')

def vim_binary_home():
    if is_windows():
        return os.path.join(vim_home(), 'vim73')
    return vim_home()

def vimfiles_home():
    if is_windows():
        return os.path.join(vim_home(), 'vimfiles')
    return vim_home()

def vim_plugin_home():
    return os.path.join(vim_binary_home(), 'plugin')

def program_files():
    return os.environ['PROGRAMFILES']

def detect_vimrc():
    if is_windows():
        return os.path.join(vim_home(), '_vimrc')
    return os.path.join(user_home(), '.vimrc')

def ctags_basedir(hint):
    dirs = os.listdir(hint)
    dirs = filter(lambda name:name.startswith('ctags'), dirs)
    if dirs:
        return os.path.join(hint, dirs[0])
    return ''

def add_to_environ(dirname):
    if dirname:
        try:
            import _winreg
            key = _winreg.CreateKey(_winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment')
            index = 0
            paths = _winreg.QueryValueEx(key, 'Path')
            success = True
            if paths:
                value_type = paths[1]
                paths = paths[0]
                # Only add to path environment when it is not there
                if dirname.lower() not in paths.lower().split(';'):
                    paths = ';'.join([paths, dirname])
                    _winreg.SetValueEx(key, 'Path', None, value_type, paths)
            else:
                success = False
            _winreg.CloseKey(key)
            return success
        except Exception, e:
            print e
    return False

def configure_ctags(filename, **kwargs):
    print 'Installing %s...' % filename
    args = {'to':kwargs['dirname'] if kwargs.has_key('dirname') else program_files()}
    if unzip(filename, **args):
        if is_windows():
            return add_to_environ(ctags_basedir(args['to']))
        return True
    return False

def configure_zip(filename, **kwargs):
    print 'Installing %s...' % filename
    args = {'to':kwargs['dirname'] if kwargs.has_key('dirname') else vimfiles_home()}
    return unzip(filename, **args)

def configure_cscope(filename, **kwargs):
    print 'Installing %s...' % filename
    cscope_basedir = os.path.join(program_files(), 'cscope')
    if unzip(filename, cscope_basedir):
        if is_windows():
            return add_to_environ(cscope_basedir)
        return True
    return False

def configure_script(filename, **kwargs):
    try:
        print 'Installing %s...' % filename
        destination = kwargs['dirname'] if kwargs.has_key('dirname') else vim_plugin_home()
        shutil.copy(filename, destination)
        return True
    except Exception, e:
        print e
    return False

def configure_vimrc():
    try:
        vimrc_file = detect_vimrc()
        file = open(vimrc_file, 'rt')
        content = file.read()
        file.close()
        if content.find(vimrc_lines) < 0:
            content = '\n'.join([content, vimrc_lines])
            file = open(vimrc_file, 'wt')
            file.write(content)
            file.close()
        return True
    except Exception, e:
        print e
    return False

items_info = [
        ('ctags.zip', 'http://prdownloads.sourceforge.net/ctags/ctags58.zip', configure_ctags),
        ('tag-list.zip', 'http://www.vim.org/scripts/download_script.php?src_id=7701', configure_zip, {'dirname':vimfiles_home()}),
        ('cscope_maps.vim', 'http://cscope.sourceforge.net/cscope_maps.vim', configure_script),
        #('cscope.tar.gz', 'http://downloads.sourceforge.net/project/cscope/cscope/15.8a/cscope-15.8a.tar.gz', configure_cscope),
        ('cscope.zip', 'http://downloads.sourceforge.net/project/mslk/Cscope/cscope-15.7/cscope-15.7.zip', configure_cscope),
        ('omni-cpp-complete.zip', 'http://www.vim.org/scripts/download_script.php?src_id=7722', configure_zip, {'dirname':vimfiles_home()}),
        ('super-tab.vmb', 'http://www.vim.org/scripts/download_script.php?src_id=18075', configure_script, {'dirname':vim_binary_home()}),
        ('win-manager.zip', 'http://www.vim.org/scripts/download_script.php?src_id=754', configure_zip, {'dirname':vimfiles_home()}),
        ('nerd-tree.zip', 'http://www.vim.org/scripts/download_script.php?src_id=17123', configure_zip, {'dirname':vimfiles_home()}),
        ('mini-buf-explorer.vim', 'http://www.vim.org/scripts/download_script.php?src_id=3640', configure_script)
        ]

def main():
    vimrc_file = detect_vimrc()
    if not os.path.exists(vimrc_file):
        print 'No Vim installation detected.'
        return
    for info in items_info:
        name, url, configure, args = info[0], info[1], info[2], info[3] if len(info) >= 4 else {}
        filename = local_file_of(name)
        if not has_downloaded(filename):
            print 'Downloading ' + name + ' to ' + filename
            if not download(filename, url):
                print 'Failed to download ' + name
                return
        if not configure(filename = filename, **args):
            print 'Failed to configure %s.' % filename
            return
    print 'Configuring startup settings...'
    if not configure_vimrc():
        print 'Failed to configure %s.' % vimrc_file

if __name__ == '__main__':
    main()
