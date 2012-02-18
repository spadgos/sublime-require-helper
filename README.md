## RequireHelper

RequireHelper is a small Sublime Text 2 plugin which allows you to insert file paths relative to your project root, or a custom subfolder.

I wrote it to save me some time when writing Javascript using the CommonJS style:

```javascript
var Baz = require('foo/bar/baz');
```

### Usage

Activate RequireHelper by pressing its shortcut key (default is <kbd>Ctrl+Alt+O</kbd>). Select the file you want by typing its name and press <kbd>enter</kbd>. The path, relative to your base is inserted into the document.

### Configuration

There are two configuration options. These can be set in your `Preferences.sublime-settings` file, or in your project file, under the key of `settings`. *(Examples below)*

- `require_helper_base` - This is the directory inside your project which should be searched for files.

- `require_helper_remove_regex` - If you want to remove characters from the filename before inserting, you can specify a regex here.

#### Example

In my project, all my javascript files are in a subfolder called `/app`. This is the contents of my project file (you can get to this file by selecting `Project -> Edit Project`

```javascript
{
  "folders":
  [
    {
      "path": "/home/nick/dev/myproject"
    }
  ],
  "settings": {
    "require_helper_base": "app",
    "require_helper_remove_regex": "\\.js$"
  }
}
```

For example, when I select a file which is on disk at `/home/nick/dev/myproject/app/foo/bar.js`, then `'foo/bar` is inserted into the document.