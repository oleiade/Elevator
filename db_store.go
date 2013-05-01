package elevator

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	l4g 		"github.com/alecthomas/log4go"
)

type DbStore struct {
	FilePath    string
	StoragePath string
	Container   map[string]*Db
	NameToUid   map[string]string
}

// DbStore constructor
func NewDbStore(filepath string, storage_path string) *DbStore {
	return &DbStore{
		FilePath:    filepath,
		StoragePath: storage_path,
		Container:   make(map[string]*Db),
		NameToUid:   make(map[string]string),
	}
}

func (store *DbStore) updateNameToUidIndex() {
	for _, db := range store.Container {
		if _, present := store.NameToUid[db.Name]; present == false {
			store.NameToUid[db.Name] = db.Uid
		}
	}
}

// ReadFromFile syncs the content of the store
// description file to the DbStore
func (store *DbStore) ReadFromFile() (err error) {
	data, err := ioutil.ReadFile(store.FilePath)
	if err != nil {
		return err
	}

	err = json.Unmarshal(data, &store.Container)
	if err != nil {
		return err
	}

	store.updateNameToUidIndex()

	return nil
}

// WriteToFile syncs the content of the DbStore
// to the store description file
func (store *DbStore) WriteToFile() (err error) {
	var data []byte

	// Check the directory hosting the store exists
	store_base_path := filepath.Dir(store.FilePath)
	_, err = os.Stat(store_base_path)
	if os.IsNotExist(err) {
		return err
	}

	data, err = json.Marshal(store.Container)
	if err != nil {
		return err
	}

	err = ioutil.WriteFile(store.FilePath, data, 0777)
	if err != nil {
		return err
	}

	return nil
}

// Load updates the DbStore with databases
// described by store file
func (store *DbStore) Load() (err error) {
	err = store.ReadFromFile()
	if err != nil {
		return err
	}

	return nil
}

// Mount sets the database status to DB_STATUS_MOUNTED
// and instantiates the according leveldb connector
func (store *DbStore) Mount(db_uid string) (err error) {

	if db, present := store.Container[db_uid]; present {
		err = db.Mount()
		if err != nil {
			return err
		}
	} else {
		return errors.New("Database does not exist")
	}
	
	return nil
}

// Unmount sets the database status to DB_STATUS_UNMOUNTED
// and deletes the according leveldb connector
func (store *DbStore) Unmount(db_uid string) (err error) {
	if db, present := store.Container[db_uid]; present {
		err = db.Unmount()
		if err != nil {
			return err
		}
	} else {
		return errors.New("Database does not exist")
	}

	return nil
}

// Add a db to the DbStore and syncs it
// to the store file
func (store *DbStore) Add(db_name string) (err error) {
	if _, present := store.NameToUid[db_name]; present {
		return errors.New("Database already exists")
	} else {
		var db_path string

		if IsFilePath(db_name) {
			if !filepath.IsAbs(db_name) {
				return errors.New("Cannot create database from relative path")
			}

			db_path = db_name
			// Check base db path exists
			dir := filepath.Dir(db_name)
			exists, err := DirExists(dir)
			if err != nil {
				l4g.Error(err)
				return err
			} else if !exists {
				return errors.New(fmt.Sprintf("%s does not exist", dir))
			}
		} else {
			db_path = filepath.Join(store.StoragePath, db_name)
		}

		db := NewDb(db_name, db_path)
		store.Container[db.Uid] = db
		store.updateNameToUidIndex()
		err = store.WriteToFile()
		if err != nil { return err }
		db.Mount()
	}

	l4g.Debug(func()string {
		return fmt.Sprintf("Database %s added to store", db_name)
	})

	return nil
}

// Drop removes a database from DbStore, and syncs it
// to store file
func (store *DbStore) Drop(db_name string) (err error) {
	if db_uid, present := store.NameToUid[db_name]; present {
		db := store.Container[db_uid]
		db_path := db.Path

		store.Unmount(db_uid)
		delete(store.Container, db_uid)
		delete(store.NameToUid, db_name)
		store.WriteToFile()

		err = os.RemoveAll(db_path)
		if err != nil {
			return err
		}
	} else {
		return errors.New("Database does not exist")
	}

	l4g.Debug(func()string {
		return fmt.Sprintf("Database %s dropped from store", db_name)
	})

	return nil
}

// Status returns a database status defined by constants
// DB_STATUS_MOUNTED and DB_STATUS_UNMOUNTED
func (store *DbStore) Status(db_name string) (int, error) {
	if db_uid, present := store.NameToUid[db_name]; present {
		db := store.Container[db_uid]
		return db.Status, nil
	}

	return -1, errors.New("Database does not exist")
}

// Exists checks if a database present in DbStore 
// exists on disk.
func (store *DbStore) Exists(db_name string) (bool, error) {
	if db_uid, present := store.NameToUid[db_name]; present {
		db := store.Container[db_uid]

		exists, err := DirExists(db.Path)
		if err != nil {
			return false, err
		}

		if exists == true {
			return exists, nil
		} else {
			// store.drop(db_name)
			fmt.Println("Dropping")
		}
	}

	return false, nil
}

// List enumerates  all the databases
// in DbStore
func (store *DbStore) List() []string {
	db_names := make([]string, len(store.Container))

	i := 0
	for _, db := range store.Container {
		db_names[i] = db.Name
		i++
	}

	return db_names
}
