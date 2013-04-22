package main

import (
	"flag"
	"fmt"
	"log"
	elevator "github.com/oleiade/Elevator"
)

var configFile string
var daemonMode bool
var transport string
var bind string
var port int
var logLevel string

func init() {
	const (
		// config
		defaultConfigFile = "/etc/elevator/elevator.conf"
		configUsage       = "Path to elevator server config file, eventually"

		// daemon
		defaultDaemonMode = false
		daemonModeUsage   = "Launch elevator as a daemon"

		// transport
		defaultTransport = "tcp"
		transportUsage   = "Transport layer : tcp | ipc"

		// bind
		defaultBind = "127.0.0.1"
		bindUsage   = `If tcp transport is selected: ip the server
		                      socket should be listening on.`

		// port
		defaultPort = 4141
		portUsage   = "Port the server should listen on"

		// log level
		defaultLogLevel = "DEBUG"
		logLevelUsage   = `Log level, see python logging documentation
                      		  for more information :
                      		  http://docs.python.org/library/logging.html#logger-objects`
	)

	flag.StringVar(&configFile, "c", defaultConfigFile, configUsage+" (shorthand)")
	flag.BoolVar(&daemonMode, "d", defaultDaemonMode, daemonModeUsage)
	flag.StringVar(&transport, "t", defaultTransport, transportUsage)
	flag.StringVar(&bind, "b", defaultBind, bindUsage)
	flag.IntVar(&port, "p", defaultPort, portUsage)
	flag.StringVar(&logLevel, "l", defaultLogLevel, logLevelUsage)
}

func main() {
	flag.Parse()
	c := elevator.NewConfig()
	err := c.FromFile(configFile)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("Elevator running on %s://%s:%s", transport, bind, port)
	elevator.Runserver(c)
}
