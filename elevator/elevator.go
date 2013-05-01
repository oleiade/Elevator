package main

import (
	"log"
	elevator 	"github.com/oleiade/Elevator"
	l4g 		"github.com/alecthomas/log4go"
)

func main() {
	cmdline := &elevator.Cmdline{}
	cmdline.ParseArgs()

	config := elevator.NewConfig()
	err := config.FromFile(*cmdline.ConfigFile)
	if err != nil {
		log.Fatal(err)
	}

	config.UpdateFromCmdline(cmdline)

	l4g.Info("Elevator running on %s", config.Endpoint)
	elevator.Runserver(config)
}
