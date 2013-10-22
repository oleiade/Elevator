package elevator

import (
	"bytes"
	zmq "github.com/bonnefoa/go-zeromq"
	"os"
	"strings"
)

// Creates and binds the zmq socket for the server
// to listen on
func CreateSocket(sockType zmq.SocketType) (*zmq.Socket, error) {
	context, err := zmq.NewContext()
	if err != nil {
		return nil, err
	}

	socket, err := context.NewSocket(zmq.Router)
	if err != nil {
		return nil, err
	}

	return socket, nil
}

func DirExists(path string) (bool, error) {
	fileInfo, err := os.Stat(path)
	if err != nil {
		return false, err
	} // if file doesn't exists, throws here

	return fileInfo.IsDir(), nil
}

func IsFilePath(str string) bool {
	startswithDot := strings.HasPrefix(str, ".")
	containsSlash := strings.Contains(str, "/")

	if startswithDot == true || containsSlash == true {
		return true
	}

	return false
}

func Truncate(str string, l int) string {
	var truncated bytes.Buffer

	if len(str) > l {
		for i := 0; i < l; i++ {
			truncated.WriteString(string(str[i]))
		}
	} else {
		return str
	}

	return truncated.String()
}

func MegabytesToBytes(mb int) int {
	return mb * 1048576
}

func Btoi(b bool) int {
	if b {
		return 1
	}
	return 0
}

func StringSliceContains(slice []string, elem string) bool {
	for _, t := range slice {
		if t == elem {
			return true
		}
	}

	return false
}
