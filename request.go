package elevator

import (
    "fmt"
    "bytes"
    "github.com/ugorji/go-msgpack"
)

type Request struct {
    DbUid   string
    Command string
    Args    []string
    Source  *ClientSocket `msgpack:"-"`
}

func NewRequest(command string, args []string) *Request {
    return &Request{
        Command: command,
        Args:    args,
    }
}

func (r *Request) String() string {
    return fmt.Sprintf("<Request uid:%s command:%s args:%s>",
        r.DbUid, r.Command, r.Args)
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