package elevator

import (
	"flag"
)


type Cmdline struct {
	ConfigFile 	*string
	DaemonMode 	*bool
	Endpoint	*string
}


func (c *Cmdline) ParseArgs() {
	c.ConfigFile = flag.String("c",
							   DEFAULT_CONFIG_FILE,
							   "specifies config file path")
	c.DaemonMode = flag.Bool("d",
							 DEFAULT_DAEMON_MODE,
							 "Launches elevator as a daemon")
	c.Endpoint = flag.String("e",
							 DEFAULT_ENDPOINT,
							 "endpoint to bind elevator to")
	flag.Parse()
}