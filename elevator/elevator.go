package main

import (
	l4g "github.com/alecthomas/log4go"
	elevator "github.com/oleiade/Elevator"
	"log"
)

func main() {
	var err error

	// Parse command line arguments
	cmdline := &elevator.Cmdline{}
	cmdline.ParseArgs()

	// Load configuration
	config := new(elevator.Config)
	err = config.FromFile(*cmdline.ConfigFile)
	if err != nil {
		log.Fatal(err)
	}
	config.Core.UpdateFromCmdline(cmdline)

	// Set up loggers
	l4g.AddFilter("stdout", l4g.INFO, l4g.NewConsoleLogWriter())
	err = elevator.SetupFileLogger("file", config.Core.LogLevel, config.Core.LogFile)
	if err != nil {
		log.Fatal(err)
	}

	if config.Core.Daemon {
		if err := elevator.Daemon(config); err != nil {
			log.Fatal(err)
		}
	} else {
		elevator.ListenAndServe(config)
	}
}
