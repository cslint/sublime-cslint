import subprocess
import json
import os
import re
import json
import xml.etree.ElementTree as ET

import sublime
import sublime_plugin

PLUGIN_NAME = 'sublime-cslint'
PREFS_SETTINGS = 'Preferences.sublime-settings'
PLUGIN_SETTINGS = 'cslint.sublime-settings'
MARK_SCOPE_FORMAT = 'cslint.mark.{}'
ICON_PATH = 'Packages/sublime-cslint/img/{}.png'

JSDOCLINK = 'http://eslint.cn/docs/rules/'
CSSDOCLink = 'http://stylelint.io/user-guide/rules/'

WARNING = 'warning'
ERROR = 'error'
WORD_RE = re.compile(r'^([-\w]+)')
problems = []
marks = {WARNING: [], ERROR: []}

COLOR_SCHEME_STYLES = {
    'warning': '''
        <dict>
            <key>name</key>
            <string>CSLint Warning</string>
            <key>scope</key>
            <string>cslint.mark.warning</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>#efbe0a</string>
            </dict>
        </dict>
    ''',
    'error': '''
        <dict>
            <key>name</key>
            <string>CSLint Error</string>
            <key>scope</key>
            <string>cslint.mark.error</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>#d70a0a</string>
            </dict>
        </dict>
    '''
}
HOVER_STYLE = '''
    <style>
        body#show-definitions {
            margin: 4.8px;
            padding: 0 0.2em;
            font-family: sans-serif;
            line-height: 1.6rem;
            border: none;
        }
        .error {
            color: red;
        }
        .warning {
            color: yellow;
        }
        p, a {
            display: inline;
        }
        p {
            color: #fff;
        }
        .cslint-rule {
            margin-left: 6px;
        }
        .cslint-close-btn {
            padding: 0 0.4rem;
            margin-left: 100px;
            color: #fff;
            background-color: #272821;
            text-decoration: none;
        }
    </style>
    '''
HOVER_TMPL = '''
        <body id="show-definitions">
            {css}
            <p class="cslint-rule-txt"><span class="{type}">{type}:</span>&nbsp;&nbsp;{msg}</p>
            <a class="cslint-rule" href="{url}">{ruleId}</a>
            <a class="cslint-close-btn" href="close">x</a>
        </body>
    '''

def plugin_loaded():
    global settings, NODE_BIN, CSLINT_BIN, PKGS_PATH, PLUGIN_CUSTUM_PATH
    
    settings = sublime.load_settings(PLUGIN_SETTINGS)

    NODE_BIN = settings.get('node_bin')
    CSLINT_BIN = settings.get('cslint_bin')
    PKGS_PATH = sublime.packages_path()
    PLUGIN_CUSTUM_PATH = os.path.join(PKGS_PATH, 'User', PLUGIN_NAME)
    
    generate_color_scheme();
   

def hightlight(view, messages):
    marks = {WARNING: [], ERROR: []}

    viewRegion = sublime.Region(0, view.size())
    viewText = view.substr(viewRegion)
    lines = view.lines(viewRegion)

    problemLen = len(messages)
    if (problemLen):
        print('\n%s: ' % view.file_name())

    for msg in messages:
        error_type = ERROR if msg['severity'] == 2 else WARNING

        print('  %s : %s, %s - %s (%s)' % (msg['line'], msg['column'], error_type, msg['message'], msg['ruleId']))
        
        row = msg['line'] - 1
        col = msg['column'] - 1
        lineRegion = lines[row]
        line_start = lineRegion.a
        line_end = lineRegion.b

        length = -1

        if (col < 0):
            col = 0
            length = line_end - line_start - 1
        elif length < 0:
            code = viewText[line_start: line_end][col:]
            match = WORD_RE.search(code)
            if match:
                length = len(match.group())
            else:
                length = 1

        pos = col + line_start

        region = sublime.Region(pos, pos + length)
        problem = {'start': pos, 'end': pos + length, 'message': {
            'type': error_type,
            'from': msg['from'],
            'ruleId': msg['ruleId'],
            'message': msg['message']
        }}

        problems.append(problem)
        marks[error_type].append(region)
        
    if (problemLen):
        print('%s probloms\n' % len(messages))

    for t in (ERROR, WARNING):
        view.erase_regions(t)
        view.add_regions(t, marks[t], 
            MARK_SCOPE_FORMAT.format(t), 
            ICON_PATH.format(t), 
            sublime.DRAW_NO_FILL)    

def fileCheck(filename):
    if (not filename):
        return False, ''
    else:
        ext = os.path.splitext(filename)[1]
        return ext in ('.js', '.css', '.scss'), ext

def processor(view, fixable = False):
    filename = view.file_name();

    isValid, ext = fileCheck(filename)

    if (not isValid): 
        return

    if (not NODE_BIN or not CSLINT_BIN):
        sublime.error_message('Please checkout your cslint settings: node path or cslint path')
        return

    args = [NODE_BIN, CSLINT_BIN, filename, '--format=json']

    if (fixable == True):
        args.append('--fix')

    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        outs, errs = proc.communicate()
        results = json.loads(outs.decode('utf-8'))
    except Exception as e:
        return

    if len(results):
        messages = results[0]['messages']
        problems = []
        hightlight(view, messages)

class LintCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        processor(self.view)

class FixCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        processor(self.view, True)

class CSLintEvent(sublime_plugin.EventListener):
    
    def open_url(self, view, problem):
        def on_navigate(link): 
            if link == "close":
                view.hide_popup()
            else:
                sublime.active_window().run_command('open_url', {"url": link})

        filename = view.file_name()
        isValid, ext = fileCheck(filename)
        if not isValid:
            return
        
        ruleId = problem['ruleId']

        if problem['from'] == 'eslint':
            ruleLink = JSDOCLINK + ruleId
        elif problem['from'] == 'stylelint':
            ruleLink = CSSDOCLink + ruleId
        else:
            ruleLink = 'plugin'


        view.show_popup(HOVER_TMPL.format(
                css = HOVER_STYLE, 
                type = problem['type'], 
                msg = problem['message'], 
                url = ruleLink, 
                ruleId = ruleId),
            flags = sublime.HIDE_ON_MOUSE_MOVE_AWAY,
            on_navigate = on_navigate)

    def on_activated_async(self, view):
        view.run_command('lint')

    def on_post_save(self, view):
        view.run_command('lint')

    def on_hover(self, view, point, hover_zone):
        if (len(problems)):
            for problem in problems:
                if (point >= problem['start'] and point <= problem['end']):
                    self.open_url(view, problem['message'])
                    break;
            
def generate_color_scheme():
    '''
    This code is taken from sublimelinter util.py#generate_color_scheme_async
    and modified to meet our needs.
    '''
    prefs = sublime.load_settings(PREFS_SETTINGS)

    color_scheme = prefs.get('color_scheme')

    if color_scheme is None:
        return

    isExisted = color_scheme.find('Packages/User/') > -1
    
    scheme_text = sublime.load_resource(color_scheme)

    scheme_preface = scheme_text.split('<plist')[0]

    scopes = {
        'cslint.mark.warning': False,
        'cslint.mark.error': False
    }

    for scope in scopes:
        if re.search(scope, scheme_text):
            scopes[scope] = True

    if False not in scopes.values():
        return
    
    plist = ET.fromstring(scheme_text)
    styles = plist.find('./dict/array')

    for style in COLOR_SCHEME_STYLES:
        styles.append(ET.fromstring(COLOR_SCHEME_STYLES[style]))

    if isExisted:
        scheme_path = os.path.normpath(os.path.join(PKGS_PATH, '..', color_scheme))
    else:
        if not os.path.exists(PLUGIN_CUSTUM_PATH):
            os.makedirs(PLUGIN_CUSTUM_PATH)

        original_name = os.path.splitext(os.path.basename(color_scheme))[0]
        scheme_path = os.path.join(PLUGIN_CUSTUM_PATH, original_name + '.tmTheme')

    with open(scheme_path, 'w', encoding='utf8') as f:
        f.write(scheme_preface)
        f.write(ET.tostring(plist, encoding='unicode'))

    if not isExisted:
        path = os.path.join('Packages','User', 'sublime-cslint', os.path.basename(scheme_path))
        prefs.set('color_scheme', path)
        sublime.save_settings('Preferences.sublime-settings')
