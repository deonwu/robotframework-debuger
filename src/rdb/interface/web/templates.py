
_BUTTON_STYLE = """
.buttons a, .buttons button{
    display:block;
    float:left;
    margin:0 7px 0 0;
    background-color:#f5f5f5;
    border:1px solid #dedede;
    border-top:1px solid #eee;
    border-left:1px solid #eee;

    font-family:"Lucida Grande", Tahoma, Arial, Verdana, sans-serif;
    font-size:12px;
    line-height:130%%;
    text-decoration:none;
    font-weight:bold;
    color:#565656;
    cursor:pointer;
    padding:5px 10px 6px 7px; /* Links */
}
.buttons button{
    width:auto;
    overflow:visible;
    padding:4px 10px 3px 7px; /* IE6 */
}
.buttons button[type]{
    padding:5px 10px 5px 7px; /* Firefox */
    line-height:17px; /* Safari */
}
*:first-child+html button[type]{
    padding:4px 10px 3px 7px; /* IE7 */
}
.buttons button img, .buttons a img{
    margin:0 3px -3px 0 !important;
    padding:0;
    border:none;
    width:16px;
    height:16px;
}

/* STANDARD */

button:hover, .buttons a:hover{
    background-color:#dff4ff;
    border:1px solid #c2e1ef;
    color:#336699;
}
.buttons a:active{
    background-color:#6299c5;
    border:1px solid #6299c5;
    color:#fff;
}

/* POSITIVE */

button.positive, .buttons a.positive{
    color:#529214;
}
.buttons a.positive:hover, button.positive:hover{
    background-color:#E6EFC2;
    border:1px solid #C6D880;
    color:#529214;
}
.buttons a.positive:active{
    background-color:#529214;
    border:1px solid #529214;
    color:#fff;
}

/* NEGATIVE */

.buttons a.negative, button.negative{
    color:#d12f19;
}
.buttons a.negative:hover, button.negative:hover{
    background:#fbe3e4;
    border:1px solid #fbc2c4;
    color:#d12f19;
}
.buttons a.negative:active{
    background-color:#d12f19;
    border:1px solid #d12f19;
    color:#fff;
}

/* REGULAR */

button.regular, .buttons a.regular{
    color:#336699;
}
.buttons a.regular:hover, button.regular:hover{
    background-color:#dff4ff;
    border:1px solid #c2e1ef;
    color:#336699;
}
.buttons a.regular:active{
    background-color:#6299c5;
    border:1px solid #6299c5;
    color:#fff;
}
"""

_STYLE = """
<style media="all" type="text/css">
  /* Generic styles */ 
  body {
    font-family: sans-serif;
    font-size: 0.8em;
    color: black;
    padding: 6px; 
    background: white;
  }
  h2 {
    margin-top: 1.2em;
  }
  .panel{ width:98%%;}
  .panel td{vertical-align: top; padding:5px;}
table.app {
  background: white;
  border: 1px solid #444444;
  border-collapse: collapse;
  empty-cells: show;
  font-size: 0.9em;
  margin: 1em 0em;
  width: 100%%;
}
table.app th, table.app td {
  border: 1px solid #444444;
  padding: 0.2em 0.3em;
}
table.app th {
  background: #eeeeee;
  font-weight: normal;
  color: black;
}
table.app td {
  vertical-align: top;
}

tr.active {background: #E6EFC2;}

.paused {background-color:red;}
.running {background-color:green;}

div.mml_output{
    border: 1px solid #444444;
    width:100%%;
    height:400px;
    overflow:scroll;
}

%(BUTTON_STYLE)s
</style>
""" % {'BUTTON_STYLE':_BUTTON_STYLE}

CALL_STACK = """
<table class='app'>
<tr>
  <th width="80px">Type</th>
  <th>Name</th>
  <th width="140px">Start time</th>
  <th width="80px">State</th>
</tr>
<!-- FOR ${rt} IN ${call_stack} -->
<tr class='${rt.css_class}'>
  <td>${rt.rt_type}</td>
  <td>${rt.name}</td>
  <td>${rt.starttime}</td>
  <td>${rt.state}</td>
</tr>
<!-- END FOR -->
</table> 
"""

BREAK_POINTS = """
<table class='app'>
<tr>
  <th width="50px">Enable</th>
  <th>Name</th>
  <th width="50px">Action</th>
</tr>
<!-- FOR ${bp} IN ${break_points} -->
<tr class='${bp.css_class}'>
  <td><a href="/update_breakpoint?sid=${session}&name=${bp.name}">${bp.active}</a></td>
  <td>${bp.kw_name}</td>
  <td></td>
</tr>
<!-- END FOR -->
<tr>
  <td><b>Add</b></td>
  <td>
      <form action="/add_breakpoint?sid=${session}" method='GET'>
          <input type='hidden' name="sid" value="${session}"/>
          <input type='text' name="bp" size="20"/>
          <input type='submit' value="Add" />
      </form>
  </td>
  <td>&nbsp;</td>
</tr>
</table> 
"""

MESSAGES = """
    <div class='${robot_status.css_class}'><b>Robot Status:</b> 
        ${robot_status.name}
    </div>
    <div><b>Command:</b> ${command}</div>
    <div><b>Result:</b> ${command_result}</div>
    <div><b>Message:</b> 
        <div id='status_msg' style='display:inline;'>${msg}</div>
    </div>    
    <!-- IF '${active_bp}' != 'None' -->
    <div style='display:none;'>
    class:${active_bp.__class__.__name__},
    expired:${active_bp.expired},
    str:${active_bp},
    </div>
    <!-- END IF -->
"""

CONSOLE = """
<form action="/run_keyword?sid=${session}" method='GET'>
    <input type='hidden' name="sid" value="${session}"/>
<table class='app'>
<tr>
  <th width="100px">Name</th>
  <th>Keyword</th>
  <th></th>
</tr>
<tr>
  <td><b>Run Keyword</b></td>
  <td>
    <input type='text' name="kw" size="45" value="${kw}"/>
  </td>
  <td><input type='submit' value="Run" /></td>
</tr>
</table>
</form> 
"""

VARIABLES = """
<table class='app'>
<tr>
  <th width="100px">Name</th>
  <th>Value</th>
  <th>Remove</th>
</tr>
<!-- FOR ${var} IN ${cur_varibles} -->
<tr>
  <td>${var.name}</td>
  <td>${var.value}</td>
  <td><a href="/remove_variable?sid=${session}&name=${var.name}">Remove</a></td>
</tr>
<!-- END FOR -->
<tr>
  <td><b>Watch variable</b></td>
  <td>
      <form action="/watch_variable?sid=${session}" method='GET'>
          <input type='hidden' name="sid" value="${session}"/>
          <input type='text' name="name" size="20"/>
          <input type='submit' value="Watch" />
      </form>
  </td>
  <td>&nbsp;</td>
</tr>
<tr>
  <td><b>Update variable</b></td>
  <td>
      <form action="/update_variable?sid=${session}" method='GET'>
          <input type='hidden' name="sid" value="${session}"/>
          <select name="name">
<!-- FOR ${var} IN ${cur_varibles} -->
            <option value="${var.name}">${var.name}</option>
<!-- END FOR -->
          </select>
          =
          <input type='text' name="value" size="20"/>
          <input type='submit' value="Update" />
      </form>
  </td>
  <td>&nbsp;</td>
</tr>
</table> 
"""

LISTENER = """
<table class='app'>
<tr>
  <th width="100px">Attribute</th>
  <th>Value</th>
</tr>
<!-- FOR ${attr} IN ${cur_attrs} -->
<tr>
  <td>${attr.name}</td>
  <td>${attr.value}</td>
</tr>
<!-- END FOR -->
</table> 
"""

DEBUGER_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta http-equiv="Expires" content="Mon, 20 Jan 2001 20:01:21 GMT" />
%(STYLE)s
<script type="text/javascript">
    //stop to refresh page if have any click in page.
    //Have not use 'meta http-equiv="refresh"', because it can't canceled by javascript.   
    var reload_event;
    var interval = ${refresh_interval} * 1000;
    function stop_refresh(){
        if(reload_event){
            window.clearInterval(reload_event);
            //refresh page if no action in 30 seconds.
            reload_event = window.setInterval(xxxx, 30 * 1000);            
            if(interval < 10 * 1000){
                var msg = document.getElementById('status_msg');
                msg.innerHTML = "<span style='color:#ff33cc;'><b>Robot is running, The page is stopped to refresh. Please click 'refresh' to check robot status.</b></span>";
            }
        }
    }
    function xxxx(){
        window.location.href = '/refresh'
    }
    function schedule_reload(){
        reload_event = window.setInterval(xxxx, interval);
    }
</script>
<title>${title}</title>
</head>
<body onclick='stop_refresh()' onload='schedule_reload()'>
    <h1>Robotframework web debuger...</h1>
    <div style="margin-left:100px;">
    <div class='buttons'>
        <a href="go_on?sid=${session}" class='positive'>Run</a>
        <a href="go_into?sid=${session}" class='positive'>Go into</a>
        <a href="go_over?sid=${session}" class='positive'>Go over</a>
        <a href="go_return?sid=${session}" class='positive'>Go Return</a>
        <a href="go_pause?sid=${session}" class='positive'>Pause</a>
        <a href="refresh?sid=${session}" class='regular'>Refresh</a>
    </div>
    </div>
    <div style="clear:both;">
        <table class='panel'>
            <tr>
                <td>
                    <b>Call Stacks</b>
                    %(CALL_STACK)s
                </td>
                <td width="40%%">
                    <b>Break Points</b>
                    %(BREAK_POINTS)s
                </td>            
            </tr>
            <tr>
                <td>
                    <b>Debug status</b>
                    %(MESSAGES)s
                    <div>
                </td>
                <td>
                    <b>Variables</b>
                    %(VARIABLES)s
                    <div>
                        <b>Console</b>
                        %(CONSOLE)s
                    </div>
                </td>            
            </tr>
            <tr>
                <td colspan='2'>
                    <b>Listener attributes</b>
                    %(LISTENER)s
                </td>
            </tr>            
        </table>
    </div>
</body>
</html>
""" % {'CALL_STACK': CALL_STACK, 'BREAK_POINTS': BREAK_POINTS, 
       'MESSAGES':MESSAGES, 'VARIABLES':VARIABLES,
       'STYLE':_STYLE, 'LISTENER':LISTENER,
       'CONSOLE': CONSOLE}
