package elevator

import (
	l4g "github.com/alecthomas/log4go"
	"os"
)

// Log levels binding
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

// SetupLogger function ensures logging file exists, and
// is writable, and sets up a log4go filter accordingly
func SetupFileLogger(loggerName string, logLevel string, logFile string) error {
	// Check file exists or return the error
	_, err := os.Stat(logFile)
	if err != nil {
		return err
	}

	// check file permissions are correct
	_, err = os.OpenFile(logFile, os.O_WRONLY, 0400)
	if err != nil {
		return err
	}

	l4g.AddFilter(loggerName,
		LogLevels[logLevel],
		l4g.NewFileLogWriter(logFile, false))

	return nil
}
