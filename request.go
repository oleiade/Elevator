package elevator

import (
	"bytes"
	"fmt"
	"github.com/ugorji/go/codec"
)

type Request struct {
	DatabaseUid string
	Command     string
	Args        []string
	Source      *ClientSocket `msgpack:"-"`
}

// String represents the Request as a normalized string
func (r *Request) String() string {
	return fmt.Sprintf("<Request uid:%s command:%s args:%s>",
		r.DatabaseUid, r.Command, r.Args)
}

// NewRequest returns a pointer to a brand new allocated Request
func NewRequest(command string, args []string) *Request {
	return &Request{
		Command: command,
		Args:    args,
	}
}

// UnpackFrom method fulfills a Request from a received
// serialized request message
func (r *Request) UnpackFrom(data *bytes.Buffer) error {
	var rawRequest []string
	var mh codec.MsgpackHandle

	// deserialize msgpacked message into string slice
	dec := codec.NewDecoder(data, &mh)
	err := dec.Decode(&rawRequest)
	if err != nil {
		return err
	}

	// Fulfill Request with deserialized data
	r.DatabaseUid = rawRequest[0]
	r.Command = rawRequest[1]
	r.Args = rawRequest[2:]

	return nil
}
