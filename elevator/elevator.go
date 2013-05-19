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

	// Set up loggers
	l4g.AddFilter("stdout",
				  l4g.INFO,
				  l4g.NewConsoleLogWriter())
	err = elevator.SetupFileLogger("file",
								   config.LogLevel,
								   config.LogFile)
	if err != nil {
		log.Fatal(err)
	}

	if config.Daemon {
		if err := elevator.Daemon(config); err != nil {
			log.Fatal(err)
		}
	} else {
		elevator.ListenAndServe(config)
	}
}
