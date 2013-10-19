package elevator

import (
	"bytes"
	"errors"
	"fmt"
    zmq "github.com/bonnefoa/go-zeromq"
	l4g "github.com/alecthomas/log4go"
	"log"
)

type ClientSocket struct {
	Id     []byte
	Socket zmq.Socket
}

// Creates and binds the zmq socket for the server
// to listen on
func CreateSocket(sockType zmq.SocketType) (*zmq.Socket, error) {
	context, err := zmq.NewContext()
	if err != nil {
		return nil, err
	}

	socket, err := context.NewSocket(zmq.Router)
	if err != nil {
		return nil, err
	}

	return socket, nil
}

// handleRequest deserializes the input msgpack request,
// processes it and ensures it is forwarded to the client.
func handleRequest(clientSocket *ClientSocket, rawMsg []byte, dbStore *DatabaseRegistry) {
	var request *Request = new(Request)
	var msg *bytes.Buffer = bytes.NewBuffer(rawMsg)

	// Deserialize request message and fulfill request
	// obj with it's content
	request.UnpackFrom(msg)
	request.Source = clientSocket
	l4g.Debug(func() string { return request.String() })

	if request.DatabaseUid != "" {
		if db, ok := dbStore.Container[request.DatabaseUid]; ok {
			if db.Status == DB_STATUS_UNMOUNTED {
				db.Mount()
			}

			// Then send the command to database for execution
			// and forwarding
			db.Channel <- request
		}
	} else {
		go func() {
			response, err := store_commands[request.Command](dbStore, request)
			if err == nil {
				forwardResponse(response, request)
			}
		}()
	}
}

// processRequest executes the received request command, and returns
// the resulting response.
func processRequest(db *Database, request *Request) (*Response, error) {
	if f, ok := database_commands[request.Command]; ok {
		response, _ := f(db, request)
		return response, nil
	}
	error := errors.New(fmt.Sprintf("Unknown command %s", request.Command))
	l4g.Error(error)

	return nil, error
}

// forwardResponse takes a request-response pair as input and
// sends the response to the request client.
func forwardResponse(response *Response, request *Request) error {
	l4g.Debug(func() string { return response.String() })

	var responseBuf bytes.Buffer
	var socket *zmq.Socket = &request.Source.Socket
	var address []byte = request.Source.Id
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

func ListenAndServe(config *Config) error {
	l4g.Info(fmt.Sprintf("Elevator started on %s", config.Endpoint))

	// Build server zmq socket
	socket, err := CreateSocket(zmq.Router)
	if err != nil {
		log.Fatal(err)
	}
	socket.Bind(config.Endpoint)
	defer (*socket).Close()

	// Load database store
	dbStore := NewDatabaseRegistry(config)
	err = dbStore.Load()
	if err != nil {
		err = dbStore.Add("default")
		if err != nil {
			log.Fatal(err)
		}
	}

	// build zmq poller
	poller := zmq.PollItems{
		&zmq.PollItem{Socket: socket, Events: zmq.Pollin},
	}

	// Poll for events on the zmq socket
	// and handle the incoming requests in a goroutine
	for {
		_, _ = poller.Poll(-1)

		switch {
		case poller[0].REvents&zmq.Pollin > 0:
			multipart, _ := poller[0].Socket.RecvMultipart(0)

			clientSocket := ClientSocket{
				Id:     multipart.Data[0],
				Socket: *socket,
			}
			msg := multipart.Data[1]

			go handleRequest(&clientSocket, msg, dbStore)
		}
	}
}
