import sublime
import sublime_plugin
import os
import platform
import re
import string


def readLine(view, point, lineOffset):
    (row, col) = view.rowcol(point)
    row += lineOffset

    if row < 0:
        return None
    point = view.text_point(row, 0)

    if point > view.size():
        return None

    return view.substr(view.line(point))


class RequireHelperCommand(sublime_plugin.TextCommand):

    regex = None

    def run(self, edit, full=False):
        self.fullInsert = full
        self.load_file_list()
        sublime.active_window().show_quick_panel(self.fileList, self.insert)

    def insert(self, index):
        if index >= 0:
            insertPos = self.view.sel()[0].begin()
            include = self.fileList[index]

            if platform.system() == "Windows":
                include = include.replace("\\", "/")

            if self.fullInsert:
                include = self.make_full_insert(include, insertPos)

            self.view.run_command('require_helper_insert', {
                'args': {
                    'insertPos': insertPos,
                    'include': include
                }
            })

    def make_full_insert(self, include, insertPos):
        req_re = re.compile("^\\s*(var )?(\\w+\\s*)= require\\(")
        varName = string.capwords(('/' + include).rsplit('/', 1)[1], '-').replace('-', '')

        #  align with adjacent requires
        lineCounter = 1
        numSpaces = 1
        while True:
            line = readLine(self.view, insertPos, lineCounter)

            if line:
                matches = req_re.match(line)
                if matches:
                    length = len(matches.groups(1)[1]) - len(varName)
                    if length > 0:
                        numSpaces = length
                        break
                    else:
                        lineCounter += 1 if lineCounter > 0 else -1
                        continue

            if lineCounter > 0:
                lineCounter *= -1
            else:
                break

        return "%s%s= require('%s')%s" % (
            varName,
            " " * numSpaces,
            include,
            "," if lineCounter > 0 else ";"
        )

    def quick_panel(self, *args, **kwargs):
        self.get_window().show_quick_panel(*args, **kwargs)

    def get_window(self):
        return self.view.window() or sublime.active_window()

    def load_file_list(self):
        RequireHelperCommand.regex = self.view.settings().get('require_helper_remove_regex')
        base = self.view.settings().get('require_helper_base') or ""
        folders = sublime.active_window().folders()
        files = []
        for folder in folders:
            get_files("", os.path.join(folder, base), files)

        self.fileList = files


# when a run() command terminates, the edit context is destroyed.
# in order to complete the async insert after the user selects
# from the file list, this helper command is invoked
class RequireHelperInsertCommand(sublime_plugin.TextCommand):

    def run(self, edit, args):
        insertPos = args['insertPos']
        include = args['include']
        self.view.insert(edit, insertPos, include)


def get_files(relativePath, base, files):
    path = os.path.join(base, relativePath)
    try:
        dir_files = os.listdir(path)
        for d in dir_files:
            # d = b(d).decode('utf-8')
            this_path = os.path.join(path, d)
            rel_path = os.path.join(relativePath, d)
            if (os.path.isdir(this_path)):
                get_files(rel_path, base, files)
            else:
                if RequireHelperCommand.regex:
                    rel_path = re.sub(RequireHelperCommand.regex, '', rel_path)
                files.append(rel_path)
    except OSError:
        print("RequireHelper: could not find " + path)
        return []


class RequireHelperGotoDef(sublime_plugin.TextCommand):

    def run(self, edit):
        v = self.view
        window = sublime.active_window()
        wordRegion = v.word(v.sel()[0].begin())
        posBefore = wordRegion.begin() - 1

       # func = None
        req = v.substr(wordRegion)

        if posBefore >= 0:
            if v.substr(posBefore) == '.':
                # func = req
                req = v.substr(v.word(posBefore))

        if not req:
            return

        requires = self.find_requires()
        require = requires[req]
        if not require:
            return

        base = self.view.settings().get('require_helper_base') or ""
        folders = window.folders()

        for folder in folders:
            path = os.path.join(folder, base, require)

            if not os.path.isfile(path):
                path += '.js'

            if os.path.isfile(path):
                window.open_file(path)
                break
        # todo: navigate to the function

    def find_requires(self):
        v = self.view
        nameToken = '[a-z_$][a-z_$0-9]*'
        path = '(?:/?[a-z0-9_$\\-\\s]+)+'  # TODO: there's a lot more valid path names
        strs = []
        v.find_all('(%s)\\s*=\\s*require\\(["\'](%s)["\']\\)' % (nameToken, path),
            sublime.IGNORECASE,
            '$1|||$2',
            strs
        )

        # there is totally a more python-y way to do this...
        pairs = {}
        for line in strs:
            split = line.split('|||')
            pairs[split[0]] = split[1]
        return pairs
