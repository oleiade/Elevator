package elevator

import (
	"sync"
)

// Service implements the structure of a long-running process.
// Helps to track running goroutines, and eventually shut them down
// gracefully.
type Service struct {
	name      string
	ch        chan bool
	waitGroup *sync.WaitGroup
}

// NewService builds a new Service instance. It instantiates
// a channel to the running service, and bootstraps a sync.waitGroup
// with an element marked as running.
func NewService(name string) *Service {
	s := &Service{
		name:      name,
		ch:        make(chan bool),
		waitGroup: &sync.WaitGroup{},
	}
	s.waitGroup.Add(1)
	return s
}

// Stop the service by closing the service's channel.
// Blocks until the service is really stopped.
func (s *Service) Stop() {
	close(s.ch)
	s.waitGroup.Wait()
}
