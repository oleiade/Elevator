package elevator

import (
	"bytes"
	"fmt"
	leveldb "github.com/jmhodges/levigo"
)

var database_commands = map[string]func(*Db, *Request) error{
	DB_GET:    Get,
	DB_PUT:    Put,
	DB_DELETE: Delete,
	DB_RANGE: Range,
}

var store_commands = map[string]func(*DbStore, *Request) error{
	DB_CONNECT: DbConnect,
	DB_LIST:    DbList,
}

func Exec(db *Db, request *Request) {
	if f, ok := database_commands[request.Command]; ok {
		f(db, request)
	}
}

func Forward(header *ResponseHeader, content *ResponseContent, request *Request) error {
	socket := request.Source.Socket
	address := request.Source.Id
	parts := make([][]byte, 3)

	var header_buf bytes.Buffer
	var content_buf bytes.Buffer
	header.PackInto(&header_buf)
	content.PackInto(&content_buf)

	parts[0] = address
	parts[1] = header_buf.Bytes()
	parts[2] = content_buf.Bytes()

	err := socket.SendMultipart(parts, 0)
	if err != nil {
		return err
	}

	return nil
}

func Get(db *Db, request *Request) error {
	ro := leveldb.NewReadOptions()
	key := request.Args[0]
	data, err := db.Connector.Get(ro, []byte(key))

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

func Range(db *Db, request *Request) error {
	read_options := leveldb.NewReadOptions()
	snapshot := db.Connector.NewSnapshot()
	read_options.SetSnapshot(snapshot)

	var data [][]string

	start := []byte(request.Args[0])
	end := []byte(request.Args[1])

	it := db.Connector.NewIterator(read_options)
	defer it.Close()
	it.Seek(start)

	for it = it; it.Valid(); it.Next() {
		if bytes.Compare(it.Key(), end) >= 1 {
			break
		}
		data = append(data, []string{string(it.Key()), string(it.Value())})
	}

	header := NewSuccessResponseHeader()
	content := ResponseContent{
		Datas: data,
	}

	Forward(header, &content, request)

	db.Connector.ReleaseSnapshot(snapshot)

	return nil
}

func DbConnect(db_store *DbStore, request *Request) error {
	db_name := request.Args[0]
	db_uid, exists := db_store.NameToUid[db_name]

	var header *ResponseHeader
	if exists {
		header = NewSuccessResponseHeader()
	} else {
		header = NewFailureResponseHeader(DATABASE_ERROR, "Database does not exist")
	}

	data_container := make([][]byte, 1)
	data_container[0] = []byte(db_uid)
	content := ResponseContent{
		Datas: data_container,
	}

	Forward(header, &content, request)

	return nil
}

func DbList(db_store *DbStore, request *Request) error {
	db_names := db_store.List()
	header := NewSuccessResponseHeader()
	data_container := make([][]byte, len(db_names))

	for index, db_name := range db_names {
		data_container[index] = []byte(db_name)
	}

	fmt.Println(db_names)

	content := ResponseContent{
		Datas: data_container,
	}

	Forward(header, &content, request)

	return nil
}
