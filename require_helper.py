import sublime
import sublime_plugin
import os
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
        #  v = self.view
        self.loadFileList()
        self.fullInsert = full
        self.edit = edit
        self.quick_panel(RequireHelperCommand.fileList, self.insert)

    def insert(self, index):
        if index >= 0:
            insertPos = self.view.sel()[0].begin()
            include = RequireHelperCommand.fileList[index]

            if self.fullInsert:
                include = self.makeFullInsert(include, insertPos)
            self.view.insert(self.edit, insertPos, include)

    def makeFullInsert(self, include, insertPos):
        req_re = re.compile("^\\s*(var )?(\\w+\\s*)= require\\(")
        varName = string.capwords(('/' + include).rsplit('/', 1)[1], '-').replace('-', '')

        #  align with adjacent requires
        lineCounter = -1
        numSpaces = 1
        while True:
            line = readLine(self.view, insertPos, lineCounter)
            print line
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

            if lineCounter < 0:
                lineCounter *= -1
            else:
                break

        return "%s%s= require('%s')" % (
            varName,
            " " * numSpaces,
            include
        )

    def quick_panel(self, *args, **kwargs):
        self.get_window().show_quick_panel(*args, **kwargs)

    def get_window(self):
        return self.view.window() or sublime.active_window()

    def loadFileList(self):
        RequireHelperCommand.regex = self.view.settings().get('require_helper_remove_regex')
        base = self.view.settings().get('require_helper_base') or ""
        folders = sublime.active_window().folders()
        files = []
        for folder in folders:
            getFiles("", os.path.join(folder, base), files)

        RequireHelperCommand.fileList = files


def getFiles(relativePath, base, files):
    path = os.path.join(base, relativePath)
    try:
        dir_files = os.listdir(path)
        for d in dir_files:
            d = d.decode('utf-8')
            this_path = os.path.join(path, d)
            rel_path = os.path.join(relativePath, d)
            if (os.path.isdir(this_path)):
                getFiles(rel_path, base, files)
            else:
                if RequireHelperCommand.regex:
                    rel_path = re.sub(RequireHelperCommand.regex, '', rel_path)
                files.append(rel_path)
    except OSError:
        print "RequireHelper: could not find " + path
        return []
