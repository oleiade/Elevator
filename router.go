package elevator

import (
	"bytes"
	"errors"
	"fmt"
	l4g "github.com/alecthomas/log4go"
	zmq "github.com/bonnefoa/go-zeromq"
)

type Router struct {
	Service

	state    chan bool
	Config   *Config
	Registry *DatabaseRegistry
	Socket   *zmq.Socket
	Poller   zmq.PollItems
}

func NewRouter(config *Config) (*Router, error) {
	// Build server zmq socket
	socket, err := CreateSocket(zmq.Router)
	if err != nil {
		return nil, err
	}

	// build zmq poller
	poller := zmq.PollItems{
		&zmq.PollItem{Socket: socket, Events: zmq.Pollin},
	}

	// Load database store
	dbRegistry := NewDatabaseRegistry(config)
	err = dbRegistry.Load()
	if err != nil {
		err = dbRegistry.Add("default")
		if err != nil {
			return nil, err
		}
	}

	router := Router{
		Config:   config,
		Socket:   socket,
		Poller:   poller,
		Registry: dbRegistry,
	}

	return &router, nil
}

func (r *Router) Run() {
	l4g.Info(fmt.Sprintf("Elevator started on %s", r.Config.Endpoint))

	r.Socket.Bind(r.Config.Endpoint)
	defer r.Socket.Close()

	// Start the router poller, and handle
	// incoming messages
	poller_state := make(chan bool)
	incoming_messages := make(chan *Message)
	go r.Poll(poller_state, incoming_messages)

	for {
		select {
		case <-r.state:
			close(poller_state)
			r.Stop()
			return
		case message := <-incoming_messages:
			r.dispatchMessage(message)
		}
	}
}

func (r *Router) Poll(state chan bool, messages chan *Message) {
	for {
		_, _ = r.Poller.Poll(-1)

		switch {
		case r.Poller[0].REvents&zmq.Pollin > 0:
			multipart, _ := r.Poller[0].Socket.RecvMultipart(0)

			message := r.parseMessage(multipart.Data[1])
			message.SourceId = multipart.Data[0]
			message.SourceSocket = *r.Socket

			messages <- message
		case <-state:
			return
		}
	}
}

func (r *Router) parseMessage(rawMsg []byte) *Message {
	var message *Message = new(Message)
	var msg *bytes.Buffer = bytes.NewBuffer(rawMsg)

	message.UnpackFrom(msg)

	return message
}

func (r *Router) dispatchMessage(message *Message) {
	if message.DatabaseUid != "" {
		if db, ok := r.Registry.Container[message.DatabaseUid]; ok {
			if db.Status == DB_STATUS_UNMOUNTED {
				db.Mount()
			}

			// Then send the command to database for execution
			// and forwarding
			db.Channel <- message
		}
	} else {
		go func() {
			response, err := store_commands[message.Command](r.Registry, message)
			if err == nil {
				forwardResponse(response, message)
			}
		}()
	}

}

// processMessage executes the received message command, and returns
// the resulting response.
func processMessage(db *Database, message *Message) (*Response, error) {
	if f, ok := database_commands[message.Command]; ok {
		response, _ := f(db, message)
		return response, nil
	}
	error := errors.New(fmt.Sprintf("Unknown command %s", message.Command))
	l4g.Error(error)

	return nil, error
}

// forwardResponse takes a message-response pair as input and
// sends the response to the message client.
func forwardResponse(response *Response, message *Message) error {
	l4g.Debug(func() string { return response.String() })

	var responseBuf bytes.Buffer
	var socket *zmq.Socket = &message.SourceSocket
	var address []byte = message.SourceId
	var msg [][]byte = make([][]byte, 2)

	response.PackInto(&responseBuf)
	msg[0] = address
	msg[1] = responseBuf.Bytes()

	err := socket.SendMultipart(msg, 0)
	if err != nil {
		return err
	}

	return nil
}
