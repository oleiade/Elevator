package elevator

import (
	"errors"
	"os"
	"fmt"
	"path/filepath"
	"io/ioutil"
	"encoding/json"
	"code.google.com/p/go-uuid/uuid"
)

type DbStore struct {
	FilePath			string
	StoragePath			string
	Container			map[string]Db
}


// DbStore constructor
func NewDbStore(filepath string, storage_path string) (*DbStore) {
	return &DbStore{
		FilePath: filepath,
		StoragePath: storage_path,
		Container: make(map[string]Db),
	}
}


// ReadFromFile syncs the content of the store
// description file to the DbStore
func (store *DbStore) ReadFromFile() (err error) {
	data, err := ioutil.ReadFile(store.FilePath)
	if err != nil { return err }

	err = json.Unmarshal(data, &store.Container)
	if err != nil { return err }

	return nil
}


// WriteToFile syncs the content of the DbStore
// to the store description file
func (store *DbStore) WriteToFile() (err error) {
	var data []byte
	
	data, err = json.Marshal(store.Container)
	if err != nil { return err }

	err = ioutil.WriteFile(store.FilePath, data, 0777)
	if err != nil { return err }

	return nil
}


// Load updates the DbStore with databases
// described by store file
func (store *DbStore) Load() (err error) {
	err = store.ReadFromFile()
	if err != nil { return err }

	return nil
}


// Mount sets the database status to DB_STATUS_MOUNTED
// and instantiates the according leveldb connector
func (store *DbStore) Mount(db_name string) error {
	if db, ok := store.Container[db_name]; ok {
		err := db.Mount()
		if err != nil { return err }
	} else {
		return errors.New("Database does not exist")
	}

	return nil
}


// Unmount sets the database status to DB_STATUS_UNMOUNTED
// and deletes the according leveldb connector
func (store *DbStore) Unmount(db_name string) error {
	if db, ok := store.Container[db_name]; ok {
		err := db.Unmount()
		if err != nil { return err }
	} else {
		return errors.New("Database does not exist")
	}

	return nil
}


// Add a db to the DbStore and syncs it
// to the store file"""
func (store *DbStore) Add(db_name string) error {
	if _, ok := store.Container[db_name]; ok {
		return errors.New("Database already exists")
	} else {
		db := Db{
			Name: db_name,
			Path: filepath.Join(store.StoragePath, db_name),
			Uid: uuid.New(),
			Status: DB_STATUS_UNMOUNTED,
		}
		store.Container[db_name] = db
		store.WriteToFile()
	}

	return nil
}


// Drop removes a database from DbStore, and syncs it
// to store file
func (store *DbStore) Drop(db_name string) error {
	if db, ok := store.Container[db_name]; ok {
		db_path := db.Path
		delete(store.Container, db_name)
		store.WriteToFile()

		err := os.RemoveAll(db_path)
		if err != nil { return err }
	} else {
		return errors.New("Database does not exist")	
	}

	return nil
}


// Status returns a database status defined by constants
// DB_STATUS_MOUNTED and DB_STATUS_UNMOUNTED
func (store *DbStore) Status(db_name string) (int, error) {
	if db, ok := store.Container[db_name]; ok {
		return db.Status, nil
	}

	return -1, errors.New("Database does not exist")
}


// Exists checks if a database present in DbStore 
// exists on disk.
func (store *DbStore) Exists(db_name string) (bool, error) {
	if db, ok := store.Container[db_name]; ok {
		exists, err := DirExists(db.Path)
		if err != nil { return false, err}

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
func (store *DbStore) List() ([]string) {
	db_names := make([]string, len(store.Container))

	i := 0
	for k, _ := range store.Container {
		db_names[i] = k
		i++
	}

	return db_names
}