package elevator

import (
	"bytes"
	"fmt"
	"github.com/ugorji/go-msgpack"
)

type Message interface {
	Pack()
	Unpack()
}

type Request struct {
	Db      string        `msgpack:"uid"`
	Command string        `msgpack:"cmd"`
	Args    interface{}   `msgpack:"args"`
	Source  *ClientSocket `msgpack:"-"`
}

type ResponseHeader struct {
	Status      int    `msgpack:"status"`
	Err_code    int    `msgpack:"err_code"`
	Err_msg     string `msgpack:"err_msg"`
	Compression int    `msgpack:"compression"`
}

type Batch []BatchOperation

type BatchOperation struct {
	op_code 	int
	op_data		[]string
}

type ResponseContent struct {
	Datas interface{} `msgpack:"datas"`
}

func NewRequest(command string, args []string) *Request {
	return &Request{
		Command: command,
		Args:    args,
	}
}

func NewSuccessResponseHeader() *ResponseHeader {
	return &ResponseHeader{
		Status: SUCCESS_STATUS,
	}
}

func NewFailureResponseHeader(err_code int, err_msg string) *ResponseHeader {
	return &ResponseHeader{
		Status:   FAILURE_STATUS,
		Err_code: err_code,
		Err_msg:  err_msg,
	}
}

func (r *Request) String() string {
	return fmt.Sprintf("<Request uid:%s command:%s args:%s>",
					   r.Db, r.Command, r.Args)
}

func (r *Request) PackInto(buffer *bytes.Buffer) error {
	enc := msgpack.NewEncoder(buffer)
	err := enc.Encode(r)
	if err != nil {
		return err
	}

	return nil
}

func (r *Request) UnpackFrom(data *bytes.Buffer) error {
	dec := msgpack.NewDecoder(data, nil)
	err := dec.Decode(r)
	if err != nil {
		return err
	}

	return nil
}

func (header *ResponseHeader) String() string {
	return fmt.Sprintf("<ResponseHeader status:%d err_code:%d err_msg:%s compression:%d>",
					   header.Status, header.Err_code, header.Err_msg, header.Compression)
}

func (header *ResponseHeader) PackInto(buffer *bytes.Buffer) error {
	enc := msgpack.NewEncoder(buffer)
	err := enc.Encode(header)
	if err != nil {
		return err
	}

	return nil
}

func (content *ResponseContent) PackInto(buffer *bytes.Buffer) error {
	enc := msgpack.NewEncoder(buffer)
	err := enc.Encode(content)
	if err != nil {
		return err
	}

	return nil
}
