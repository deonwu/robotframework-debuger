
import threading
from breakpoints import * 
from runtime import *
import logging

class Debuger(object):
    """
        
    """
    def __init__(self, ):
        self.lock = threading.Condition() 
        self.call_stack = []
        self.break_points = []
        self.active_break_point = None
        self.listener = Listeners()
        self.logger = logging.getLogger("core.dbg")
            
    def go_steps(self, count):
        self.logger.debug("go_steps:%s" % count)
        if self.paused():
            bp = SemaphoreBreakPoint('', count)
            self.add_breakpoint(bp)
            self.go_on()
        else:
            raise RuntimeError, "the program have not paused!"
    
    def go_into(self):
        self.go_steps(1)
        
    def go_over(self):
        self.logger.debug("go_over...")
        if self.paused():
            bp = RuntimeBreakPoint('', self.call_stack[-1], BaseRuntime.DONE)
            self.add_breakpoint(bp)
            self.go_on()
        else:
            raise RuntimeError, "the program have not paused!"
        
    def go_run(self):
        """run current keyword. paused when the keyword is called.
            if the current keyword is called, go_run is ignored.
        """
        if self.paused():
            if self.call_stack[-1].state == BaseRuntime.START:
                bp = RuntimeBreakPoint('', self.call_stack[-1], BaseRuntime.END)
                self.add_breakpoint(bp)
                self.go_on()
            else:
                pass
        else:
            raise RuntimeError, "the program have not paused!"
    
    def go_return(self):
        """ """
        self.logger.debug("go_return...")
        if self.paused():
            if len(self.call_stack) > 1:
                bp = RuntimeBreakPoint('', self.call_stack[-2], BaseRuntime.DONE)
                self.add_breakpoint(bp)
            self.go_on()
        else:
            raise RuntimeError, "the program have not paused!"
    
    def go_pause(self):
        """schedule to pause the program."""
        self.logger.debug("go_pause...")
        if self.active_break_point is None:
            self.add_breakpoint(SemaphoreBreakPoint('', 1))
        else:
            self.logger.warning("the program is already paused!")
            raise RuntimeError, "the program is already paused!"
                
    def add_breakpoint(self, bp):
        self.break_points.insert(0, bp)
    
    def remove_breakpoint(self, bp):
        self.break_points.remove(bp)
    
    def start_function(self, func):
        try:
            self.call_stack.append(func)
            
            func.state = BaseRuntime.START
            self.listener.start_keyword(func)
            
            self.check_break_points()
            func.state = BaseRuntime.RUNNING
        except BaseException, e:
            self.logger.exception(e)
            raise
            
    def end_function(self, func):
        try:
            if self.call_stack[-1] != func:
                err_msg = "Not matched the call stack. %s != %s" % (self.call_stack[-1], func)
                self.logger.error(err_msg)
                raise RuntimeError, err_msg
            
            func.state = BaseRuntime.END
            
            self.listener.end_keyword(func)
            self.check_break_points()
            self.call_stack.pop()
            func.state = BaseRuntime.DONE
        except BaseException, e:
            self.logger.exception(e)
            raise        
    
    def check_break_points(self):
        matched_bps = []
        
        for bp in list(self.break_points):
            if bp.expired:
                self.remove_breakpoint(bp)
                continue
            if bp.active and bp.matched_context(self.call_stack):
                matched_bps.append(bp)
        
        #all break points should be checked, because the 'expired' need evaluated.
        #but the program paused once.
        if len(matched_bps) > 0: self.pause(matched_bps[0])
    
    def pause(self, breakpoint):
        self.active_break_point = breakpoint
                
        self.listener.pause(breakpoint)
        
        bp = self.active_break_point
        self.logger.debug("paused at '%s'" % bp)  
        self.lock.acquire()
        self.lock.wait()
        self.lock.release()
        self.logger.debug("break paused %s..." % bp)
        
    def paused(self):
        """check if the program is blocked."""
        return self.active_break_point is not None
        
    def go_on(self):
        self.logger.debug("go on from active bp:%s" % self.active_break_point)
        if self.active_break_point is not None:
            self.active_break_point = None
            self.lock.acquire()
            self.lock.notify()
            self.lock.release()
        
        self.listener.go_on()
        
    def add_listener(self, l):
        self.listener.add_listener(l)

    def remove_listener(self, l):
        self.listener.remove_listener(l)
    
class Listener:
    def __init__(self):
        pass
    
    def pause(self, breakpoint):
        pass
    def go_on(self):
        pass
    
    def start_keyword(self, keyword):
        pass
    def end_keyword(self, keyword):
        pass

class Listeners(Listener):
    def __init__(self):
        self.listeners = []
        
    def pause(self, breakpoint):
        for l in self.listeners:
            l.pause(breakpoint)
        
    def go_on(self):
        for l in self.listeners:
            l.go_on()
    
    def start_keyword(self, keyword):
        for l in self.listeners:
            l.start_keyword(keyword)
            
    def end_keyword(self, keyword):
        for l in self.listeners:
            l.end_keyword(keyword)
            
    def add_listener(self, l):
        self.listeners.append(l)

    def remove_listener(self, l):
        self.listeners.remove(l)

        