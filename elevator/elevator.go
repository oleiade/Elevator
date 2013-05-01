package main

import (
	"flag"
	elevator 	"github.com/oleiade/Elevator"
	l4g 		"github.com/alecthomas/log4go"
)

var configFile string
var daemonMode bool
var endpoint string

func init() {
	const (
		// config
		defaultConfigFile = "/etc/elevator/elevator.conf"
		configUsage       = "Path to elevator server config file, eventually"

		// daemon
		defaultDaemonMode = false
		daemonModeUsage   = "Launch elevator as a daemon"

		// endpoint
		defaultEndpoint = "tcp://127.0.0.1"
		endpointUsage   = "endpoint elevator should be binded on"
	)

	flag.StringVar(&configFile, "c", defaultConfigFile, configUsage)
	flag.BoolVar(&daemonMode, "d", defaultDaemonMode, daemonModeUsage)
	flag.StringVar(&endpoint, "e", defaultEndpoint, endpointUsage)
}

func main() {
	flag.Parse()

	config := elevator.NewConfig()
	err := config.FromFile(configFile)
	if err != nil {
		l4g.Crash(err)
	}

	// implement config override via cmdline

	l4g.Info("Elevator running on %s", config.Endpoint)
	elevator.Runserver(config)
}
