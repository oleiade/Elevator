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
	DbUid   string
	Command string
	Args    []string
	Source  *ClientSocket `msgpack:"-"`
}

type Response struct {
	Status   int
	Err_code int
	Err_msg  string
	Data     []string
}

type BatchOperations []BatchOperation

type BatchOperation struct {
	OpCode string
	OpArgs []string
}

func NewRequest(command string, args []string) *Request {
	return &Request{
		Command: command,
		Args:    args,
	}
}

func NewResponse(status int, err_code int, err_msg string, data []string) *Response {
	return &Response{
		Status:   status,
		Err_code: err_code,
		Err_msg:  err_msg,
		Data:     data,
	}
}

func NewSuccessResponse(data []string) *Response {
	return &Response{
		Status: SUCCESS_STATUS,
		Data:   data,
	}
}

func NewFailureResponse(err_code int, err_msg string) *Response {
	return &Response{
		Status:   FAILURE_STATUS,
		Err_code: err_code,
		Err_msg:  err_msg,
	}
}

func NewBatchOperation(op_code string, op_args []string) *BatchOperation {
	return &BatchOperation{
		OpCode: op_code,
		OpArgs: op_args,
	}
}

func (r *Request) String() string {
	return fmt.Sprintf("<Request uid:%s command:%s args:%s>",
		r.DbUid, r.Command, r.Args)
}

func (r *Response) String() string {
	return fmt.Sprintf("<Response status:%d err_code:%d err_msg:%s data:%s",
		r.Status, r.Err_code, r.Err_msg, r.Data)
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
	var raw_request []string

	dec := msgpack.NewDecoder(data, nil)
	err := dec.Decode(&raw_request)
	if err != nil {
		return err
	}

	r.DbUid = raw_request[0]
	r.Command = raw_request[1]
	r.Args = raw_request[2:]

	return nil
}

func (r *Response) ToArray() []interface{} {
	var response []interface{}

	response = append(response, r.Status, r.Err_code, r.Err_msg)

	for _, d := range r.Data {
		response = append(response, string(d))
	}

	return response
}

func (r *Response) PackInto(buffer *bytes.Buffer) error {
	enc := msgpack.NewEncoder(buffer)
	err := enc.Encode(r.ToArray())
	if err != nil {
		return err
	}

	return nil
}

func BatchOperationFromSlice(slice []string) *BatchOperation {
	return NewBatchOperation(slice[0], slice[1:])
}

func BatchOperationsFromRequestArgs(args []string) *BatchOperations {
	var ops BatchOperations
	var cur_index int = 0
	var last_index int = 0

	for index, elem := range args {
		cur_index = index
		if index > 0 {
			if elem == SIGNAL_BATCH_PUT || elem == SIGNAL_BATCH_DELETE {
				ops = append(ops, *BatchOperationFromSlice(args[last_index:index]))
				last_index = index
			}
		}
	}

	// Add the rest
	if cur_index > 0 {
		ops = append(ops, *BatchOperationFromSlice(args[last_index : cur_index+1]))
	}

	return &ops
}
