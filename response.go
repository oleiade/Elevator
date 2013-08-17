package elevator

import (
	"bytes"
	"fmt"
	"github.com/ugorji/go-msgpack"
)

type Response struct {
	Status  int
	ErrCode int
	ErrMsg  string
	Data    []string
}

// String represents the Response as a normalized string
func (r *Response) String() string {
	return fmt.Sprintf("<Response status:%d errCode:%d errMsg:%s data:%s",
		r.Status, r.ErrCode, r.ErrMsg, r.Data)
}

// NewResponse returns a pointer to a brand new allocated Response
func NewResponse(status int, errCode int, errMsg string, data []string) *Response {
	return &Response{
		Status:  status,
		ErrCode: errCode,
		ErrMsg:  errMsg,
		Data:    data,
	}
}

// NewSuccessResponse returns a pointer to a brand
// new allocated succesfull Response
func NewSuccessResponse(data []string) *Response {
	return &Response{
		Status: SUCCESS_STATUS,
		Data:   data,
	}
}

// NewFailureResponse returns a pointer to a brand
// new allocated failure Response
func NewFailureResponse(errCode int, errMsg string) *Response {
	return &Response{
		Status:  FAILURE_STATUS,
		ErrCode: errCode,
		ErrMsg:  errMsg,
	}
}

// ToArray transforms a Response to an array-like []interface{}
func (r *Response) ToArray() []interface{} {
	var response []interface{}

	response = append(response, r.Status, r.ErrCode, r.ErrMsg)

	for _, d := range r.Data {
		response = append(response, string(d))
	}

	return response
}

// PackInto method fulfills serializes the Response
// into a msgpacked response message
func (r *Response) PackInto(buffer *bytes.Buffer) error {
	enc := msgpack.NewEncoder(buffer)
	err := enc.Encode(r.ToArray())
	if err != nil {
		return err
	}

	return nil
}
