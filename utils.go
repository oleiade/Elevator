package elevator

import (
	"os"
)

func DirExists(path string) (bool, error) {
	file_info, err := os.Stat(path)
	if err != nil {
		return false, err
	} // if file doesn't exists, throws here

	return file_info.IsDir(), nil
}
