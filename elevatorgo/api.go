package elevator

import (
	"fmt"
	"bytes"
	leveldb 	"github.com/jmhodges/levigo"

)

var command_handlers = map[string]func(*Db, *Request) error {
	DB_GET: Get,
	DB_PUT: Put,
	DB_DELETE: Delete,
}


func Exec(db *Db, request *Request) {
	if f, ok := command_handlers[request.Command]; ok {
		f(db, request)
	}
}


func Forward(header *ResponseHeader, content *ResponseContent, request *Request) error {
	socket := request.Source.Socket
	address := request.Source.Id
	parts := make([][]byte, 3)

	var header_buf 	bytes.Buffer
	var content_buf bytes.Buffer
	header.PackInto(&header_buf)
	content.PackInto(&content_buf)

	parts[0] = address
	parts[1] = header_buf.Bytes()
	parts[2] = content_buf.Bytes()

	err := socket.SendMultipart(parts, 0)
	if err != nil { return err }

	return nil
}


func Get(db *Db, request *Request) error {
	ro := leveldb.NewReadOptions()
	key := request.Args[0]
	data, err := db.Connector.Get(ro, []byte(key))

	fmt.Println(key)

	var header *ResponseHeader
	if err != nil {
		header = NewFailureResponseHeader(KEY_ERROR, string(err.Error()))
	} else {
		header = NewSuccessResponseHeader()
	}
	
	data_container := make([][]byte, 1)
	data_container[0] = data
	content := ResponseContent{
		Datas: data_container,
	}

	Forward(header, &content, request)

	return nil
}


func Put(db *Db, request *Request) error {
	wo := leveldb.NewWriteOptions()
	key := request.Args[0]
	value := request.Args[1]
	err := db.Connector.Put(wo, []byte(key), []byte(value))

	fmt.Println(key)
	
	var header *ResponseHeader
	if err != nil {
		header = NewFailureResponseHeader(VALUE_ERROR, string(err.Error()))
	} else {
		header = NewSuccessResponseHeader()
	}

	content := ResponseContent{}

	Forward(header, &content, request)

	return nil
}

func Delete(db *Db, request *Request) error {
	wo := leveldb.NewWriteOptions()
	key := request.Args[0]
	err := db.Connector.Delete(wo, []byte(key))

	fmt.Println(key)

	var header *ResponseHeader
	if err != nil {
		header = NewFailureResponseHeader(KEY_ERROR, string(err.Error()))		
	} else {
		header = NewSuccessResponseHeader()
	}

	content := ResponseContent{}

	Forward(header, &content, request)

	return nil
}
