package elevator

import (
	"bytes"
	"github.com/ugorji/go-msgpack"
)

type Message interface {
	Pack()
	Unpack()
}

type Request struct {
	Db 		string 			`msgpack:"uid"`
	Command string 			`msgpack:"cmd"`
	Args 	[]string 		`msgpack:"args"`
	Source	*ClientSocket 	`msgpack:"-"`
}

type ResponseHeader struct {
	Status 		int 	`msgpack:"status"`
	Err_code 	int 	`msgpack:"err_code"`
	Err_msg 	string	`msgpack:"err_msg"`
	Compression int 	`msgpack:"compression"`
}

type ResponseContent struct {
	Datas [][]byte `msgpack:"datas"`
}

func NewRequest(command string, args []string) *Request {
	return &Request{
		Command: command,
		Args: args,
	}
}

func (r *Request) PackInto(buffer *bytes.Buffer) error {
	enc := msgpack.NewEncoder(buffer)
	err := enc.Encode(r)
	if err != nil { return err }

	return nil
}

func (r *Request) UnpackFrom(data *bytes.Buffer) error {
	dec := msgpack.NewDecoder(data, nil)
	err := dec.Decode(r)
	if err != nil { return err }

	return nil
}

func (header *ResponseHeader) PackInto(buffer *bytes.Buffer) error {
	enc := msgpack.NewEncoder(buffer)
	err := enc.Encode(header)
	if err != nil { return err }

	return nil
}

func (content *ResponseContent) PackInto(buffer *bytes.Buffer) error {
	enc := msgpack.NewEncoder(buffer)
	err := enc.Encode(content)
	if err != nil { return err }

	return nil
}

