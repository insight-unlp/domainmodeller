try:
    from urllib2 import urlparse
except ImportError:
    from urllib.parse import urlparse

from os import path
from os.path import dirname
import os, requests
from tempfile import NamedTemporaryFile

def filename_from_url(url):
    return urlparse.urlsplit(url).path.rstrip('/').split('/')[-1]

def retrieve_file(url):
    # Create temporary file with same extension (to allow mimetype detection)

    if url.startswith('file://'):
        return open(url[6:])
    
    request = requests.get(url, stream=True)
    if request.status_code != 200:
        raise requests.HTTPError(request.text)
    
    f = NamedTemporaryFile(suffix=filename_from_url(url).split('.')[-1])
    for block in request.iter_content(1024):
        if not block: break
        f.write(block)

    # Write and rewind to enable reading
    f.flush()
    f.seek(0)
    return f

package_code_path = dirname(dirname(__file__))
def get_package_path(*relative):
    '''Returns path to relative to the package root. 
    WARNING: Assumes trusted user'''
    return os.path.join(dirname(package_code_path), *relative)

def key_with_max_value(dictionary):
    return max(dictionary, key=lambda k: dictionary[k])

def chunker(seq, size=20000):
    chunk = []
    for el in seq:
        chunk.append(el)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk

def enum_chunker(seq, size=20000):
    '''Same as chunker but returns a tuple (i, chunk) where i is the size of
    the list so far, similar to enumerate().'''
    i=0
    for chunk in chunker(seq, size):
        i += len(chunk)
        yield (i, chunk)

def extract_fn_arguments(func, excluded=['self']):
    import inspect
    params = inspect.getargspec(func)

    num_kw = len(params.defaults) if params.defaults else 0
    args = params.args[:len(params.args)-num_kw]
    args = [a for a in args if a not in excluded]

    kwargs = {}
    if num_kw:
        kwvalues = params.defaults
        kwparams = params.args[-num_kw:]
        for param, value in zip(kwparams, kwvalues):
            kwargs[param] = value
    return (args, kwargs)

def remove_list_duplicates(l):
    added = set()
    result = []
    for el in l:
        if el not in added:
            added.add(el)
            result.append(el)

    return result
            
def temporary_file_path(filename, delete_existing=False):
    import tempfile
    if delete_existing and path.exists(filename):
        os.remove(path)
    filename = path.join(tempfile.gettempdir(), filename)
    return filename

def run_jar(jar_path, args, pipe_output=True):
    from subprocess import Popen, PIPE
    
    pipe = PIPE if pipe_output else None
    process = Popen(["java", "-jar", jar_path] + map(str, args), stdout=pipe)
    result = process.communicate()[0] if pipe_output else ''
    
    exit_code = process.wait()
    if exit_code>0:
        raise EnvironmentError('Java exited with code %d: %s'
                               % (exit_code, result))
    return result


