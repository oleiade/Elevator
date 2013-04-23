package elevator

import (
	"bytes"
	zmq "github.com/alecthomas/gozmq"
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

	log.Println(request)
	if request.Db != "" {
		if db, ok := db_store.Container[request.Db]; ok {
			if db.Status == DB_STATUS_UNMOUNTED {
				db.Mount()
			}
			db.Channel <- request
		}
	} else {
		go store_commands[request.Command](db_store, request)
	}
}

func Runserver(config *Config) {
	socket, err := server_socket(config.Endpoint)
	defer (*socket).Close()
	if err != nil {
		log.Fatal(err)
	}

	db_store := NewDbStore(config.StorePath, config.StoragePath)
	db_store.ReadFromFile()
	db_store.Add(config.DefaultDb)
	log.Println(db_store)

	poller := zmq.PollItems{
		zmq.PollItem{Socket: *socket, zmq.Events: zmq.POLLIN},
	}

	for i := 0; ; i++ {
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
}
