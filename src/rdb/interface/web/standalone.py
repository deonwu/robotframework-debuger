"""
this module is support to run RDB web interface in standalone mode. the RDB is running
with robot, it's not available after the robot is stopped. The user may be confused 
"what's happened RDB? Does crushed?" 

The RDB will switch over to stand alone mode to notify user the robot is stopped friendly.
"""

from wsgiref.simple_server import make_server, demo_app
from wsgiref.simple_server import WSGIRequestHandler
import re, sys, os, logging, urllib2, traceback, socket
import autoreload
from wsgi_proxy import WSGIProxyApplication

class HttpServletApp(object):
    def __init__(self, environ, start_response):
        """ URL? """
        self.environ = environ
        self.output = []
        self.logger = logging.getLogger("http")
        
        actions = ManageActions()
        url = environ['PATH_INFO']
        command = url.split("/")[2]
        if command and hasattr(actions, command):
            action = getattr(actions, command)
        else:
            action = actions.status
        
        result = ()
        self.params = self.__parse_param(environ['QUERY_STRING'])
        if action.func_defaults:
            reqiured_args_count = action.func_code.co_argcount - len(action.func_defaults)
        else:
            reqiured_args_count = action.func_code.co_argcount
        var_names = action.func_code.co_varnames
        reqiured_args, options_args = var_names[:reqiured_args_count], var_names[reqiured_args_count:]
        try:
            args, kw_args = self.__parse_args(self.params, reqiured_args, options_args)
            result = action(*args, **kw_args)
        except Exception, e:
            self.logger.exception(e)
            result = "Exception:%s\n%s" % (e, traceback.format_exc())
        
        self.render_output(start_response, result)
            
    def render_output(self, start_response, result):
        import types
        if self.params.get("DEBUG", '') == 'Y':
            env_list = ( "%s=%s\n" % (k, v) for k, v in self.environ.iteritems() )
            self.output.append("<!--%s-->" % "".join(env_list))
        if isinstance(result, basestring):
            self.output.append(result)
            start_response("200 OK", [('Content-Type','text/plain'), ])
        elif isinstance(result, types.TupleType):
            template_name, param = result[:2]
            import templates as t
            from robot.serializing import Template, Namespace
            from robot.running import NAMESPACES
            template = getattr(t, template_name)
            self.output.append(Template(template=template).generate(param))
            start_response("200 OK", [('Content-Type','text/html'), ])
        else:
            self.output.append(str(result))
            start_response("200 OK", [('Content-Type','text/plain'), ])
    
    def __parse_param(self, param):
        p = {}
        for e in param.split("&"):
            if "=" not in e: continue
            k, v = e.split("=", 1)
            p[k] = urllib2.unquote(v)
        return p
    
    def __parse_args(self, args, reqiured_args, options_args):
        param = []
        for name in reqiured_args:
            if 'self' == name:continue         
            if not args.has_key(name):
                raise RuntimeError, "Not found required parameter '%s'" % name
            param.append(args[name])
        kw_param = {}    
        for name in options_args:
            if args.has_key(name):
                kw_param[str(name)] = args[name]
        return (param, kw_param)        
    
    def __iter__(self):
        return iter(self.output)
    
class ManageActions(object):
    def start_rdb(self, host, port):
        rdb = SERVER_CONTEXT.rdb
        rdb.server_name = host
        rdb.server_port = port
        rdb.status = 'running'
        return 'OK'

    def done_rdb(self):
        rdb = SERVER_CONTEXT.rdb
        rdb.status = 'closed'
        return 'OK'
    
    def stop_proxy(self):
        sys.exit(0)

    def proxy_status(self):
        return self.status()

    def proxy_help(self):
        pass
    
    def status(self):
        return ["root_path:%s" % SERVER_CONTEXT.root_path,
                "rdb_port:%s" % SERVER_CONTEXT.rdb.server_port,
                "rdb_host:%s" % SERVER_CONTEXT.rdb.server_name,
                "rdb_status:%s" % SERVER_CONTEXT.rdb.status,
                ]

class StaticWebApp(object):
    def __init__(self, environ, start_response):
        """ URL? """
        self.http_url = environ['PATH_INFO']
        start_response("404 Not Found", [('Content-Type','text/plain')])
        self.env = environ
    
    def __iter__(self):
        return iter([])
    
class ApplicationContext(object):
    """A global standalone object, it's keep a web server running context."""
    
    def __init__(self, root_path='', app_setting=None):
        self.root_path = root_path
        self.app_setting = app_setting
        self.active_rdb = RDBInfo()
        self.proxy_exception = None
    
    @property
    def rdb(self): return self.active_rdb
        
    
class RDBInfo(object):
    """A RDB interface infomation."""
    STATUS = ['running', 'closed', ]
    def __init__(self, host='127.0.0.1', port=0):
        self.server_name = host
        self.server_port = port
        self.status = 'closed'
        self.info = []
        self.start_time = []

def wsgi_global_app(environ, start_response):
    #proxy = context.rdb_proxy()
    path_info = environ['PATH_INFO']
    script = path_info.split("/")[1]
    logger = logging.getLogger("rdb.proxy")
    
    if re.search(r"\.(?:html|css|js|jpg|gif|png|ico)$", path_info, re.I):
        return StaticWebApp(environ, start_response)
    elif script in ['manage', ]:
        return HttpServletApp(environ, start_response)
    elif script in ['alive', ]:
        start_response("200 OK", [('Content-Type','text/plain')])
        return ['OK', ]
    elif SERVER_CONTEXT.rdb.status == 'running':
        socket.setdefaulttimeout(5)
        rdb = SERVER_CONTEXT.rdb
        environ['HTTP_HOST'] = "%s:%s" % (rdb.server_name, rdb.server_port)
        environ['SERVER_NAME'] = rdb.server_name
        environ['SERVER_PORT'] = rdb.server_port
        proxy = WSGIProxyApplication()
        try:
            logger.info("HTTP_HOST:%s" % environ['HTTP_HOST'])
            logger.info("url:%s" % path_info)
            return proxy(environ, start_response)
        except BaseException, e:
            start_response("302 Found", [('Location','/manage/status')])
            SERVER_CONTEXT.rdb.status = 'error'
            logger.exception(e)
            return []
    else:
        #status_code = 302
        start_response("302 Found", [('Location','/manage/status')])
        return []

class RDBProxyWSGIHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        logging.getLogger("rdb.proxy").debug(format % args)

def main(config_file='', ):
    import logging
    def init_sys_logging(cfg):
        level = getattr(logging, cfg.LOGGING_LEVEL)
        logging.basicConfig(level=level,
                            format='%(asctime)s %(name)-8s %(levelname)-6s %(message)s',
                            datefmt='%m-%d %H:%M:%S',
                            filename=cfg.PROXY_LOGGING_FILE,
                            filemode='a')
    
    def start_wsgi_server():
        from rdb.RobotDebuger import DebugSetting
        app_settings = DebugSetting()
        work_root = os.getcwd()

        config_path = os.path.abspath(config_file)
        if os.path.isfile(config_path):
            app_settings.load_from_file(config_path)
        
        init_sys_logging(app_settings)
        logger = logging.getLogger("rdb.proxy")
        logger.info("Loading RDB proxy at %s" % work_root)
        
        try:
            SERVER_CONTEXT = ApplicationContext(work_root, app_settings)
            globals()['SERVER_CONTEXT'] = SERVER_CONTEXT
            
            from wsgiref.simple_server import WSGIServer
            server_address = (app_settings.WEB_BIND, int(app_settings.WEB_PORT))
            server = WSGIServer(server_address, RDBProxyWSGIHandler)
            server.set_app(wsgi_global_app)
            SERVER_CONTEXT.server = server
            
            logger.info("Serving HTTP on %s:%s..." %(app_settings.WEB_BIND,
                                                          app_settings.WEB_PORT))
            
            server.serve_forever()
        except BaseException, e:
            logger.exception(e)
        
    start_wsgi_server()
    #autoreload.main(start_wsgi_server)

if __name__ == "__main__":
    xx = os.path.dirname(__file__)
    sys.path.insert(0, os.path.normpath(os.path.join(xx, "..", "..", "..")))
    main(*sys.argv[1:])
    

