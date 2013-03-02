package main

import (
	"fmt"
	zmq "github.com/alecthomas/gozmq"
)

func runserver() {
	context, _ := zmq.NewContext()
	
	socket, _ := context.NewSocket(zmq.ROUTER)
	defer socket.Close()
	socket.Bind("tcp://127.0.0.1:4141")

	poller := zmq.PollItems {
	zmq.PollItem{ Socket: socket, zmq.Events: zmq.POLLIN },
	}

	for i := 0; ; i++ {
		 _, _ = zmq.Poll(poller, -1)

		switch {
		case poller[0].REvents&zmq.POLLIN != 0:
			// Process task
			parts, _ := poller[0].Socket.RecvMultipart(0) // eat the incoming message
			fmt.Println(parts)
		}
	}
}

func main() {
	db := Db{"testdb", "/dev/null", 0, nil}
	// runserver()
}