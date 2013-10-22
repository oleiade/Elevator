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
	config := elevator.NewConfig()
	err = config.OverrideWithIni(*cmdline.ConfigFile)
	if err != nil {
		log.Fatal(err)
	}
	config.UpdateFromCmdline(cmdline)

	// Set up loggers
	l4g.AddFilter("stdout", elevator.LogLevels[config.Loglevel], l4g.NewConsoleLogWriter())
	err = elevator.SetupFileLogger("file", config.Loglevel, config.Logfile)
	if err != nil {
		log.Fatal(err)
	}

    router, err := elevator.NewRouter(config)
    if err != nil {
        log.Fatal(err)
    }

    if config.Daemon {
        if err := elevator.Daemon(router); err != nil {
            log.Fatal(err)
        }
    } else {
        router.Run()
    }
}
