package elevator

import (
	"bytes"
	"os"
	"strings"
)

func DirExists(path string) (bool, error) {
	file_info, err := os.Stat(path)
	if err != nil {
		return false, err
	} // if file doesn't exists, throws here

	return file_info.IsDir(), nil
}

func IsFilePath(str string) bool {
	startswith_dot := strings.HasPrefix(str, ".")
	contains_slash := strings.Contains(str, "/")

	if startswith_dot == true || contains_slash == true {
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
