# cslint for sublime text 3

A plugin to lint and format js and css/scss for sublime text3 base on [cslint][1]

## Installation
**With Package Control**:
    
Run “Package Control: Install Package” command, find and install `cslint` plugin.
    
**Manually**:

Clone or [download][1] git repo into your packages folder (in ST3, find Browse Packages… menu item to open this folder)

```bash
$ git clone git@github.com:cslint/sublime-cslint.git
```

## Usage
First of all, make sure [cslint][1] has been installed, and cslint path is in `cslint.sublime-settings` which looks like below:
(`Preferences->Package Settings->cslint->Settings-User`)

```json
  {
    "node_bin": "/usr/local/bin/node",
    "cslint_bin": "/usr/local/bin/cslint"
  }
```
  
     1. lint automatically
     2. press `ctrl+cmd+f` to format
 
![screenshot](https://github.com/cslint/sublime-cslint/blob/master/img/screen.gif)

`Tips:` for now,  this plugin only works on *st3* and *OS X*

### License
[MIT][3]
[1]: https://github.com/cslint/cslint
[2]: https://codeload.github.com/cslint/sublime-cslint/zip/master
[3]: http://opensource.org/licenses/MIT