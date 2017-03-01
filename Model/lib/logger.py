from collections import OrderedDict
import inspect
import logging
import logging.config


def logger(name='logfile.log',filelevel=logging.INFO, streamlevel=logging.WARNING):
    # create logger with 'spam_application'
    logger = logging.getLogger('__main__')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(name)
    fh.setLevel(filelevel)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(streamlevel)
    # create formatter and add it to the handlers
    if filelevel>=logging.INFO:
        formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)-60s - %(funcName)s')
    elif filelevel<logging.INFO:
        formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)-60s - %(name)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger




def get_all_caller():
    cont = True
    i=2
    name = []
    while cont:
        name.append(caller_name(i))
        if name[-1] == '':
            cont = False
        
        #print(i)
        i += 1
    name = ".".join(name[::-1])
    return '.'.join(list(OrderedDict.fromkeys(name.split('.')))[1:])
            
        
    
def caller_name(skip=2):
    """Get a name of a caller in the format module.class.method
    
       `skip` specifies how many levels of stack to skip while getting caller
       name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.
       
       An empty string is returned if skipped levels exceed stack height
    """
    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start+1:
      return ''
    parentframe = stack[start][0]    
    name = []
    module = inspect.getmodule(parentframe)
    # `modname` can be None when frame is executed directly in console
    # TODO(techtonik): consider using __main__
    if module:
        name.append(module.__name__)
    # detect classname
    if 'self' in parentframe.f_locals:
        # I don't know any way to detect call from the object method
        # XXX: there seems to be no way to detect static method call - it will
        #      be just a function call
        name.append(parentframe.f_locals['self'].__class__.__name__)
    codename = parentframe.f_code.co_name
    if codename != '<module>':  # top level usually
        name.append( codename ) # function or a method
    del parentframe
    return ".".join(name)


if __name__ == '__main__':
    filename = 'test'
    import os
    cwd = os.getcwd()
    savedir = cwd + '\\' + 'test' + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    print(savedir)
    logger = logger('%s\\%s.log' %(savedir,filename))
    logger.critical('test')