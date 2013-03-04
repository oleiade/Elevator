package elevator

import (
	"fmt"
)

var command_handlers = map[string]interface{}{
	DB_GET: Get,
}

func Exec(db *Db, request *Request) {
	if f, ok := command_handlers[request.Command]; ok {
		f.(func(*Db, *Request))(db, request)
	}
}

func Get(db *Db, request *Request) error {
	fmt.Println("GET RECEIVED")
}

func Put(db *Db, request *Request) {
	fmt.Println("PUT RECEIVED")
}