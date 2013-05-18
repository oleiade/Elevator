package elevator

import (
	"bytes"
	"fmt"
	zmq "github.com/alecthomas/gozmq"
	l4g "github.com/alecthomas/log4go"
	"log"
)

type ClientSocket struct {
	Id     []byte
	Socket zmq.Socket
}

func server_socket(endpoint string) (*zmq.Socket, error) {
	context, err := zmq.NewContext()
	if err != nil {
		return nil, err
	}

	socket, err := context.NewSocket(zmq.ROUTER)
	if err != nil {
		return nil, err
	}

	socket.Bind(endpoint)

	return &socket, nil
}

func request_handler(client_socket *ClientSocket, raw_msg []byte, db_store *DbStore) {
	request := new(Request)
	msg := bytes.NewBuffer(raw_msg)
	request.UnpackFrom(msg)
	request.Source = client_socket
	l4g.Debug(func() string { return request.String() })

	if request.DbUid != "" {
		if db, ok := db_store.Container[request.DbUid]; ok {
			if db.Status == DB_STATUS_UNMOUNTED {
				db.Mount()
			}
			db.Channel <- request
		}
	} else {
		go store_commands[request.Command](db_store, request)
	}
}

func ListenAndServe(config *Config) error {
	l4g.Info(fmt.Sprintf("Elevator started on %s", config.Endpoint))

	socket, err := server_socket(config.Endpoint)
	defer (*socket).Close()
	if err != nil {
		log.Fatal(err)
	}

	db_store := NewDbStore(config.StorePath, config.StoragePath)
	err = db_store.Load()
	if err != nil {
		err = db_store.Add("default")
		if err != nil {
			log.Fatal(err)
		}
	}

	poller := zmq.PollItems{
		zmq.PollItem{Socket: *socket, zmq.Events: zmq.POLLIN},
	}

	for {
		_, _ = zmq.Poll(poller, -1)

		switch {
		case poller[0].REvents&zmq.POLLIN != 0:
			parts, _ := poller[0].Socket.RecvMultipart(0)

			client_socket := ClientSocket{
				Id:     parts[0],
				Socket: *socket,
			}
			msg := parts[1]

			go request_handler(&client_socket, msg, db_store)
		}
	}

	return nil
}
