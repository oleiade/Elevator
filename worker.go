package elevator

import (
	"sync"
)

// Worker implements the structure of a long-running process.
// Helps to track running goroutines, and eventually shut them down
// gracefully.
type Worker struct {
	name        string
	waitGroup   *sync.WaitGroup
	ExitChannel chan bool
}

// NewWorker builds a new Worker instance. It instantiates
// a channel to the running service, and bootstraps a sync.waitGroup
// with an element marked as running.
func NewWorker(name string, wg *sync.WaitGroup) *Worker {
	return &Worker{
		name:           name,
		ExitChannel:    make(chan bool),
		waitGroup:      wg,
	}
}

func (w *Worker) Start() {
    w.waitGroup.Add(1)
}

// Stop the service by closing the service's channel.
// Blocks until the service is really stopped.
func (w *Worker) Stop() {
    if _, ok := <- w.ExitChannel; ok {
        close(w.ExitChannel)
    }
	w.waitGroup.Wait()
}
