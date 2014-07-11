
from runtime import BaseRuntime as RT
from runtime import KeywordRuntime
import re, fnmatch
import logging

class BreakPoint(object):
    def __init__(self, name):
        self.name = name
        self.active = True
        self.expired = False
    
    def matched_context(self, stack):
        return False
    
    def __str__(self):
        return "break:%s" % (self.name)
    
class KeywordBreakPoint(BreakPoint):
    def __init__(self, name, kw_name, state=RT.START):
        BreakPoint.__init__(self, name)
        self.kw_name = kw_name
        self.state = state
        self.pattern = '^' + kw_name.replace('*', '.*') + '$'
        
    def matched_context(self, stack):
        
        if not self.active or len(stack) <= 0:
            return False
        
        rt = stack[-1]
        if isinstance(rt, KeywordRuntime):
            if re.match(self.pattern, rt.name, re.I) and rt.state == self.state:
                return True
            
        return False
    
    def __str__(self):
        return "break:%s, pattern=%s" % (self.name, self.kw_name)
    
class CallStackBreakPoint(KeywordBreakPoint):
    def __init__(self, name, stack, state=RT.START):
        BreakPoint.__init__(self, name)
        self.break_stack = stack
        self.state = state
        self.kw_name = ";".join(stack)
        
    def matched_context(self, stack):
        if not self.active or len(stack) <= 0:
            return False
        
        #return false, if the last runtime is not matched.
        if not fnmatch.fnmatch(str(stack[-1]), self.break_stack[-1]):
            return False
        
        cs = iter(stack)
        bps = list(self.break_stack)
        bps.reverse()
        for e in stack:
            if len(bps) == 0:break
            if fnmatch.fnmatch(str(e), bps[-1]):bps.pop()
        
        return len(bps) == 0 and stack[-1].state == self.state
    
    def __str__(self):
        return "break:%s, stack=%s" % (self.name, ";".join(self.break_stack))    
    
class RuntimeBreakPoint(BreakPoint):
    def __init__(self, name, rt, state=RT.START):
        BreakPoint.__init__(self, name)
        self.rt = rt
        self.state = state
        self.rt_done = False

    def matched_context(self, stack):
        
        if not self.active or len(stack) <= 0:
            return False 
        
        if self.rt_done and self.state == RT.DONE and \
            stack[-1].state == RT.START: #go over, go return only paused at keyword starting.
            self.expired = True
            return True
        
        if stack[-1] == self.rt:
            if stack[-1].state == self.state:
                return True
            elif self.state == RT.DONE and stack[-1].state == RT.END:
                """it's active at next step"""
                self.rt_done = True
                return False
        else:
            return False
        
    def __str__(self):
        xx = str(self.rt)
        return "Runtime break:%s, rt=%s, state=%s" % (self.name, xx, self.state)
        

class SemaphoreBreakPoint(BreakPoint):
    def __init__(self, name, init_count=1):
        BreakPoint.__init__(self, name)
        self.semaphore = init_count
        
    def matched_context(self, stack):
        
        if not self.active or len(stack) <= 0:
            return False
        
        if stack[-1].state == RT.START:
            self.semaphore -= 1
            
        self.expired = self.semaphore == 0
        
        return self.expired

    def __str__(self):
        return "Semaphore break:%s, semaphore=%s" % (self.name, self.semaphore)

    