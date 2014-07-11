from __future__ import with_statement
from contextlib import closing
import os, sys

from debuger.debuger import Debuger, Listener
from debuger.breakpoints import KeywordBreakPoint, CallStackBreakPoint
from threading import Thread
import logging, types

class DebugSetting(object):
    def __init__(self, path=None):
        try:
            import pkg_resources        
            logging_config = pkg_resources.resource_filename('rdb', "settings.rdb")
        except:
            logging_config = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "settings.rdb")
            
        self.load_from_file(logging_config)
        
        self.BPS_LIST = []
        self.WATCHING_LIST = []
        self.source_file = None
    
    def load_from_file(self, path):
        self.source_file = path
        with closing(open(path, 'r')) as records:
            for l in records:
                l = l.strip()
                if l.startswith("#") or not l:continue
                if "=" in l:
                    name, value = l.split("=", 1)
                    name, value = name.strip(), value.strip()
                if name.endswith("LIST"):
                    if(hasattr(self, name)):
                        getattr(self, name).append(value)
                    else:
                        setattr(self, name, [value, ])
                else:
                    setattr(self, name, value)
        

class DebugThread(Thread):
    def __init__(self, interface, args):
        Thread.__init__(self)
        self.setDaemon(True)
        self.interface = interface
        self.args = args
    
    def run(self):
        logger = logging.getLogger("rbt.int")
        try:
            self.interface.start(self.args)
        except BaseException, e:
            logger.exception(e)
        
class TelentMonitorProxy(object):
    def __init__(self, rdb):
        self.rdb = rdb
        self.logger = logging.getLogger("tel.monitor")
        
    def write(self, c):
        for m in self.rdb.telnet_monitor_list:
            try:
                m.write(c)
            except Exception, e:
                self.logger.warning("Exception:%s in %s" % (e, m))
                
class FileMonitor(object):
    def __init__(self, path):
        self.output = open(path,'w')
    
    def write(self, c):
        for e in str(c):
            if ord(e) > 128: continue
            self.output.write(e)

    def close(self):
        self.output.flush()
        self.output.close()

class FileCaseStatus(Listener):
    def __init__(self, path):
        self.output = open(path,'w')
        
    def start_keyword(self, rt):
        if rt.rt_type == 'case':
            self.output.write("%s run '%s' ... " %(rt.attrs['starttime'],
                                                     rt.attrs['longname']))

    def end_keyword(self, rt):
        if rt.rt_type == 'case':
            self.output.write("%s\n" % (rt.attrs['status']))

    def close(self):
        self.output.flush()
        self.output.close()

class RobotDebuger(object):
    def __init__(self, settings):
        self.bp_id = 0
        self.debugCtx = Debuger()
        self.settings = DebugSetting()
        self.logger = None
        self.watched_variable = []
        self.inteface_list = []
        self.telnet_monitor_list = []
        self.debug_listener = []
        
        if settings.endswith('.rdb'):
            self.settings.load_from_file(os.path.abspath(settings))
        else:
            self.add_breakpoint(settings)
        
        if self.settings.LOGGING_FILE:
            self.__init_sys_logging()
            self.logger = logging.getLogger("rdb.c")
            self.logger.info("starting robot debuger...")
            
        for e in self.settings.BPS_LIST:
            self.add_breakpoint(e)
        
        for e in self.settings.WATCHING_LIST:
            self.watch_variable(e)
            
        self.__set_case_status()
        self._exit_code = 0
        
            
    def add_breakpoint(self, bps):
        if not bps.strip(): return
        if isinstance(bps, types.ListType):
            self.debugCtx.add_breakpoint(CallStackBreakPoint('bp%s' % self.bp_id,
                                                             bps))
        elif ";" in bps:
            self.debugCtx.add_breakpoint(CallStackBreakPoint('bp%s' % self.bp_id,
                                                             bps.split(";")))
        else:
            self.debugCtx.add_breakpoint(KeywordBreakPoint('bp%s' % self.bp_id,
                                                           bps))
        self.bp_id += 1
        #self.debugCtx.add_breakpoint(KeywordBreakPoint('', bps))
        
    def watch_variable(self, name):
        if not name.strip(): return
        if name not in self.watched_variable:
            self.watched_variable.append(name)
    
    def remove_variable(self, name):
        if name in self.watched_variable:
            self.watched_variable.remove(name)
            
    def add_telnet_monitor(self, monitor):
        self.telnet_monitor_list.append(monitor)
    
    @property
    def watching_variable(self):return list(self.watched_variable)
    
    def run_keyword(self, name, *args):
        """, """
        import robot.output as output
        from robot.running import Keyword, NAMESPACES
        kw = Keyword(name, args)
        def get_name(handler_name, variables):
            return "RDB.%s" % handler_name
        kw._get_name = get_name
        
        if self._exit_code > 0:
            sys.exit(self._exit_code)
        
        return kw.run(output.OUTPUT, NAMESPACES.current)
        
    def run(self):
        try:
            for cls_int in self.settings.INTERFACE_LIST:
                handler = cls_int.split(".")
                module_name, handler = ".".join(handler[:-1]), handler[-1]
                module = __import__(module_name, globals(), locals(), [handler, ], -1)
                cls_int = getattr(module, handler)
                self.inteface_list.append(cls_int(self))
                DebugThread(self.inteface_list[-1], self.settings).start()
        except Exception, e:
            self.logger and self.logger.exception(e)
            raise
            
    def __init_sys_logging(self):
        level = getattr(logging, self.settings.LOGGING_LEVEL)
        logging.basicConfig(level=level,
                            format='%(asctime)s %(name)-8s %(levelname)-6s %(message)s',
                            datefmt='%m-%d %H:%M:%S',
                            filename=self.settings.LOGGING_FILE,
                            filemode='w')
                
    def __set_case_status(self):
        """output case status in file"""
        if self.settings.CASE_STATUS_FILE:
            path = os.path.abspath(self.settings.CASE_STATUS_FILE)
            self.logger.info("output case status to: %s" % path)
            try:
                l = FileCaseStatus(path)
                self.debug_listener.append(l)
                self.debugCtx.add_listener(l)
            except Exception, e:
                self.logger.exception(e)
                
    def close_telnet_monitor(self):
        for e in self.telnet_monitor_list:
            if hasattr(e, 'close'):
                try:
                    e.close()
                except Exception, e:
                    self.logger.error("exception from monitor '%s'." % e)
                    self.logger.exception(e)

    def close_debug_listener(self):
        for e in self.debug_listener:
            if hasattr(e, 'close'):
                try:
                    e.close()
                except Exception, e:
                    self.logger.error("exception from listener '%s'." % e)
                    self.logger.exception(e)

    
    def close(self):
        self.logger.info("shutdown telnet monitor...")
        self.close_telnet_monitor()
        self.close_debug_listener()
        
        for e in self.inteface_list:
            self.logger.info("shutdown interface. %s" % str(e))
            e.close()
        self.logger.info("robot debuger is closed.")

    def sys_exit(self, err_code=255):
        self._exit_code = err_code
    