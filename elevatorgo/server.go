package elevator

import (
	"fmt"
	"log"
	"bytes"
	zmq "github.com/alecthomas/gozmq"
)

func server_socket(endpoint string) (zmq.Socket, error) {
	context, err := zmq.NewContext()
	if err != nil { return nil, err }

	socket, err := context.NewSocket(zmq.ROUTER)
	if err != nil { return nil, err }

	socket.Bind(endpoint)

	return socket, nil
}

func request_handler(requests chan [][]byte, db_store *DbStore) {
	for request := range requests {
		req := new(Request)
		msg := bytes.NewBuffer(request[1])
		req.UnpackFrom(msg)
		req.Source = request[0]

		if db, ok := db_store.Container[req.Db]; ok {
			if db.Status == DB_STATUS_UNMOUNTED {
				db.Mount()
			}
			go db.Forward(req)
		}
	}
}

func Runserver() {
	socket, err := server_socket("tcp://127.0.0.1:4141")
	defer socket.Close()
	if err != nil { log.Fatal(err) }

	db_store := NewDbStore("/tmp/test.json", "/tmp")
	err = db_store.Load()
	if err != nil { log.Fatal(err) }

	poller := zmq.PollItems {
		zmq.PollItem{ Socket: socket, zmq.Events: zmq.POLLIN },
	}

	requests := make(chan [][]byte)
	go request_handler(requests, db_store)

	for i := 0; ; i++ {
		 _, _ = zmq.Poll(poller, -1)

		switch {
		case poller[0].REvents & zmq.POLLIN != 0:
			parts, _ := poller[0].Socket.RecvMultipart(0)
			requests <- parts
		}
	}
}
