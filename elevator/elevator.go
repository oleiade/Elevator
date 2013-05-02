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

	l4g.AddFilter("stdout",
				  elevator.LogLevels[config.LogLevel],
				  l4g.NewConsoleLogWriter())

	if config.Daemon {
		if err := elevator.Daemon(config); err != nil {
			log.Fatal(err)
		}
	} else { 
		elevator.ListenAndServe(config)
	}
}
