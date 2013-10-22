package elevator

import (
	"bytes"
	"fmt"
	zmq "github.com/bonnefoa/go-zeromq"
	"github.com/ugorji/go/codec"
)

type Message struct {
	DatabaseUid  string
	Command      string
	Args         []string
	SourceId     []byte
	SourceSocket zmq.Socket `msgpack:"-"`
}

// String represents the Message as a normalized string
func (r *Message) String() string {
	return fmt.Sprintf("<Message uid:%s command:%s args:%s>",
		r.DatabaseUid, r.Command, r.Args)
}

// NewMessage returns a pointer to a brand new allocated Message
func NewMessage(command string, args []string) *Message {
	return &Message{
		Command: command,
		Args:    args,
	}
}

// UnpackFrom method fulfills a Message from a received
// serialized request message
func (r *Message) UnpackFrom(data *bytes.Buffer) error {
	var rawMessage []string
	var mh codec.MsgpackHandle

	// deserialize msgpacked message into string slice
	dec := codec.NewDecoder(data, &mh)
	err := dec.Decode(&rawMessage)
	if err != nil {
		return err
	}

	// Fulfill Message with deserialized data
	r.DatabaseUid = rawMessage[0]
	r.Command = rawMessage[1]
	r.Args = rawMessage[2:]

	return nil
}
