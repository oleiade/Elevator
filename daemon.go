package elevator

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"os/signal"
	"strconv"
	"syscall"
)

func createPidFile(pidfile string) error {
	if pidString, err := ioutil.ReadFile(pidfile); err == nil {
		pid, err := strconv.Atoi(string(pidString))
		if err == nil {
			if _, err := os.Stat(fmt.Sprintf("/proc/%d/", pid)); err == nil {
				return fmt.Errorf("pid file found, ensure elevator is not running or delete %s", pidfile)
			}
		}
	}

	file, err := os.Create(pidfile)
	if err != nil {
		log.Println(err)
		return err
	}

	defer file.Close()

	_, err = fmt.Fprintf(file, "%d", os.Getpid())
	return err
}

func removePidFile(pidfile string) {
	if err := os.Remove(pidfile); err != nil {
		log.Printf("Error removing %s: %s", pidfile, err)
	}
}

func Daemon(config *Config) error {
	if err := createPidFile(config.Core.Pidfile); err != nil {
		log.Fatal(err)
	}
	defer removePidFile(config.Core.Pidfile)

	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, os.Kill, os.Signal(syscall.SIGTERM))

	go func() {
		sig := <-c
		log.Printf("Received signal '%v', exiting\n", sig)
		removePidFile(config.Core.Pidfile)
		os.Exit(0)
	}()

	return ListenAndServe(config)
}
