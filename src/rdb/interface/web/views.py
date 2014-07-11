
class BaseView(object):
    def __init__(self, obj):
        self.obj = obj
        self.css_class = ""
        
    def __getattr__(self, name):
        return getattr(self.obj, name)
    
class BreakPointView(BaseView):
    pass

class CallStackView(BaseView):
    pass