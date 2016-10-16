# cslint for sublime text 3

A plugin to lint and format js and css/scss for sublime text3 base on [cslint][1]

first of all, make sure [cslint][1] has been installed, and cslint path is in `cslint.sublime-settings` which looks like below:
(`Preferences->Package Settings->cslint->Settings-User`)

```json
  {
    "node_bin": "/usr/local/bin/node",
    "cslint_bin": "/usr/local/bin/cslint"
  }
```
  
     1. lint automatically
     2. press `ctrl+cmd+f` to format
 
![screenshot](https://github.com/cslint/sublime-cslint/blob/master/img/screenshot.png)

`Tips:` for now,  this plugin only works on *st3* and *OS X*

### License
[MIT][2]
[1]: https://github.com/cslint/cslint
[2]: http://opensource.org/licenses/MIT
