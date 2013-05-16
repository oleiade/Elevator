package elevator

import (
	"log"
	"bytes"
	"errors"
	leveldb 	"github.com/jmhodges/levigo"
	l4g 		"github.com/alecthomas/log4go"
)

var database_commands = map[string]func(*Db, *Request) error{
	DB_GET:    	Get,
	DB_MGET:	MGet,
	DB_PUT:    	Put,
	DB_DELETE: 	Delete,
	DB_RANGE: 	Range,
	DB_SLICE:	Slice,
}

var store_commands = map[string]func(*DbStore, *Request) error{
	DB_CREATE:	DbCreate,
	DB_DROP:	DbDrop,
	DB_CONNECT: DbConnect,
	DB_MOUNT:	DbMount,
	DB_UMOUNT:	DbUnmount,
	DB_LIST:    DbList,
}

func Exec(db *Db, request *Request) {
	if f, ok := database_commands[request.Command]; ok {
		f(db, request)
	}
}

func Forward(header *ResponseHeader, content *ResponseContent, request *Request) error {	
	l4g.Debug(func()string { return header.String() })
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
	key, ok := request.Args[0].(string)
	if !ok {
		return errors.New("Unable to extract args from request")
	}

	var data []string

	ro := leveldb.NewReadOptions()
	value, err := db.Connector.Get(ro, []byte(key))

	var header *ResponseHeader
	if err != nil {
		header = NewFailureResponseHeader(KEY_ERROR, string(err.Error()))
	} else {
		header = NewSuccessResponseHeader()
	}

	data = append(data, string(value))
	content := ResponseContent{
		Datas: data,
	}

	Forward(header, &content, request)

	return nil
}

func Put(db *Db, request *Request) error {
	key, ok := request.Args[0].(string)
	value, ok := request.Args[1].(string)
	if !ok {
		return errors.New("Unable to extract args from request")
	}

	wo := leveldb.NewWriteOptions()
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
	key, ok := request.Args[0].(string)
	if !ok {
		return errors.New("Unable to cast args to []string")
	}

	wo := leveldb.NewWriteOptions()
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

func MGet(db *Db, request *Request) error {
	read_options := leveldb.NewReadOptions()
	snapshot := db.Connector.NewSnapshot()
	read_options.SetSnapshot(snapshot)

	var data []string = make([]string, len(request.Args))

	if len(request.Args) > 0 {
		start, ok := request.Args[0].([]byte)
		end, ok := request.Args[len(request.Args) - 1].([]byte)
		if !ok {
			return errors.New("Unable to extract args from request")
		}

		keys_index := make(map[string]int)

		for index, element := range request.Args {
			keys_index[element.(string)] = index
		}

		it := db.Connector.NewIterator(read_options)
		defer it.Close()
		it.Seek(start)

		for it = it; it.Valid(); it.Next() {
			if bytes.Compare(it.Key(), end) > 1 {
				break
			}

			if index, present := keys_index[string(it.Key())] ; present {
				data[index] = string(it.Value())
			}
		}

	}

	header := NewSuccessResponseHeader()
	content := ResponseContent{
		Datas: data,
	}

	Forward(header, &content, request)

	db.Connector.ReleaseSnapshot(snapshot)

	return nil
}

func Range(db *Db, request *Request) error {
	start, ok := request.Args[0].([]byte)
	end, ok := request.Args[1].([]byte)
	if !ok {
		return errors.New("Unable to extract args from request")
	}

	read_options := leveldb.NewReadOptions()
	snapshot := db.Connector.NewSnapshot()
	read_options.SetSnapshot(snapshot)

	var data [][]string

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

func Slice(db *Db, request *Request) error {
	start, ok := request.Args[0].([]byte)
	limit, ok := request.Args[1].(int)
	if !ok {
		return errors.New("Unable to extract args from request")
	}

	read_options := leveldb.NewReadOptions()
	snapshot := db.Connector.NewSnapshot()
	read_options.SetSnapshot(snapshot)

	var header *ResponseHeader
	var data [][]string

	it := db.Connector.NewIterator(read_options)
	defer it.Close()
	it.Seek(start)

	i := 0
	for it = it; it.Valid(); it.Next() {
		if i >= limit {
			break
		}

		data = append(data, []string{string(it.Key()), string(it.Value())})		
		i++
	}

	header = NewSuccessResponseHeader()
	content := ResponseContent{
		Datas: data,
	}

	Forward(header, &content, request)

	db.Connector.ReleaseSnapshot(snapshot)


	return nil
}


func DbCreate(db_store *DbStore, request *Request) error {
	db_name, ok	:= request.Args[0].(string)
	if !ok {
		return errors.New("Unable to extract args from request")
	}

	var header	*ResponseHeader

	err := db_store.Add(db_name)
	if err != nil {
		header = NewFailureResponseHeader(DATABASE_ERROR, string(err.Error()))
	} else {
		header = NewSuccessResponseHeader()
	}

	content := ResponseContent{}
	Forward(header, &content, request)

	return nil
}

func DbDrop(db_store *DbStore, request *Request) error {
	db_name, ok	:= request.Args[0].(string)
	if !ok {
		return errors.New("Unable to extract args from request")
	}

	var header 	*ResponseHeader

	err := db_store.Drop(db_name)
	if err != nil {
		header = NewFailureResponseHeader(DATABASE_ERROR, string(err.Error()))
	} else {
		header = NewSuccessResponseHeader()
	}

	content := ResponseContent{}
	Forward(header, &content, request)

	return nil
}

func DbConnect(db_store *DbStore, request *Request) error {
	db_name, ok := request.Args[0].(string)
	if !ok {
		l4g.Debug("ERROR")
		return errors.New("Unable to cast args to []string")
	}

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

	content := ResponseContent{
		Datas: data_container,
	}

	Forward(header, &content, request)

	return nil
}


func DbMount(db_store *DbStore, request *Request) error {
	db_name, ok	:= request.Args[0].(string)
	if !ok {
		return errors.New("Unable to extract args from request")
	}

	var header *ResponseHeader
	db_uid, exists := db_store.NameToUid[db_name]

	if exists {
		err := db_store.Mount(db_store.Container[db_uid].Name)
		if err != nil {
			return err
		}

		header = NewSuccessResponseHeader()
	} else {
		header = NewFailureResponseHeader(DATABASE_ERROR, "Database does not exist")
	}

	content := ResponseContent{}

	Forward(header, &content, request)

	return nil

}

func DbUnmount(db_store *DbStore, request *Request) error {
	db_name, ok := request.Args[0].(string)
	if !ok {
		return errors.New("Unable to extract args from request")
	}

	var header *ResponseHeader
	db_uid, exists := db_store.NameToUid[db_name]

	if exists {
		err := db_store.Unmount(db_uid)
		if err != nil {
			return err
		}

		header = NewSuccessResponseHeader()
	} else {
		header = NewFailureResponseHeader(DATABASE_ERROR, "Database does not exist")
	}

	content := ResponseContent{}

	Forward(header, &content, request)

	return nil
}