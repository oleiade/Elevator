package main

import (
	"flag"
	"log"
	elevator "github.com/oleiade/Elevator"
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
		log.Fatal(err)
	}

	// implement config override via cmdline

	log.Printf("Elevator running on %s", config.Endpoint)
	elevator.Runserver(config)
}
