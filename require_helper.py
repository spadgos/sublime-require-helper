import sublime
import sublime_plugin
import os
import re


class RequireHelperCommand(sublime_plugin.TextCommand):

    fileList = None
    regex = None

    def run(self, edit):
        #  v = self.view
        if RequireHelperCommand.fileList is None:
            self.loadFileList()

        self.edit = edit
        self.quick_panel(RequireHelperCommand.fileList, self.insert)

    def insert(self, index):
        if index >= 0:
            self.view.insert(self.edit, self.view.sel()[0].begin(), RequireHelperCommand.fileList[index])

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
