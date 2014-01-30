import inspect
from termcolor import colored as c
import re
from domainmodeller.util.misc import extract_fn_arguments

def pretty_doc(name_fn_map=None, groups=None, docstrings=True, exclude_vars=set()):
    s = []
    for name, func in name_fn_map.items():
        if name in groups:
            s.append('\n%s\n%s' % (groups[name], '-'*len(groups[name])))
        args, kwargs = extract_fn_arguments(func)
        kw = []
        for arg in args:
            if arg not in exclude_vars:
                kw.append(c(arg, 'yellow'))
        for arg, val in kwargs.items():
            if arg not in exclude_vars:
                kw.append('%s=%s' % (c(arg, 'yellow'), c(val, 'magenta') ))
        
        fn_name = '%s' % c(name, 'green')
        fn_args = ''
        for k in kw:
            arg = '  ' + k
            if len(fn_args.split('\n')[-1]) > 105:
                fn_args += '\n' + (' '*len(name))
            fn_args += arg
        
        s.append(fn_name + fn_args)
        
        if docstrings:
            docfn = getattr(func, '__docstring__', func.__doc__)
            docstring = docfn or ''
    
            if docstring:
                lines = docstring.split('\n')
                if len(lines) > 1:
                    spaces = len(lines[1]) - len(lines[1].lstrip())
                    r = re.compile(r"^\s{%d}" % spaces, re.MULTILINE)
                    docstring = r.sub("  ", docstring)
                docstring = "  " + docstring.strip()
                s.append(docstring)
    return '\n'.join(s)

def pretty_doc_from_class(cls):
    members = inspect.getmembers(cls, predicate=inspect.ismethod)
    name_fn_map = {k:v for k,v in members if not k.startswith('_')}
    return pretty_doc(name_fn_map)