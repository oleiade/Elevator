package elevator

import (
	l4g "github.com/alecthomas/log4go"
)

var LogLevels = map[string]l4g.Level{
	l4g.DEBUG.String():    l4g.DEBUG,
	l4g.FINEST.String():   l4g.FINEST,
	l4g.FINE.String():     l4g.FINE,
	l4g.DEBUG.String():    l4g.DEBUG,
	l4g.TRACE.String():    l4g.TRACE,
	l4g.INFO.String():     l4g.INFO,
	l4g.WARNING.String():  l4g.WARNING,
	l4g.ERROR.String():    l4g.ERROR,
	l4g.CRITICAL.String(): l4g.CRITICAL,
}
