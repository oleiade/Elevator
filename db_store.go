package elevator

import (
	"encoding/json"
	"errors"
	"fmt"
	l4g "github.com/alecthomas/log4go"
	"io/ioutil"
	"os"
	"path/filepath"
)

type DbStore struct {
	Config    *Config
	Container map[string]*Db
	NameToUid map[string]string
}

// DbStore constructor
func NewDbStore(config *Config) *DbStore {
	return &DbStore{
		Config:    config,
		Container: make(map[string]*Db),
		NameToUid: make(map[string]string),
	}
}

func (store *DbStore) updateNameToUidIndex() {
	for _, db := range store.Container {
		if _, present := store.NameToUid[db.Name]; present == false {
			store.NameToUid[db.Name] = db.Uid
		}
	}
}

// updateDatabasesOptions makes sur that every Db instance
// in DbStore has it's storage options set. Nota, this
// operation is necessary as storage options are defined
// in an ini file and canno't be automatically loaded by the
// json store loader.
func (store *DbStore) updateDatabasesOptions() {
	for _, db := range store.Container {
		db.Options = store.Config.Storage
	}
}

// ReadFromFile syncs the content of the store
// description file to the DbStore
func (store *DbStore) ReadFromFile() (err error) {
	data, err := ioutil.ReadFile(store.Config.Core.StorePath)
	if err != nil {
		return err
	}

	err = json.Unmarshal(data, &store.Container)
	if err != nil {
		return err
	}

	store.updateNameToUidIndex()
	store.updateDatabasesOptions()

	return nil
}

// WriteToFile syncs the content of the DbStore
// to the store description file
func (store *DbStore) WriteToFile() (err error) {
	var data []byte

	// Check the directory hosting the store exists
	storeBasePath := filepath.Dir(store.Config.Core.StorePath)
	_, err = os.Stat(storeBasePath)
	if os.IsNotExist(err) {
		return err
	}

	data, err = json.Marshal(store.Container)
	if err != nil {
		return err
	}

	err = ioutil.WriteFile(store.Config.Core.StorePath, data, 0777)
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
func (store *DbStore) Mount(dbUid string) (err error) {
	if db, present := store.Container[dbUid]; present {
		err = db.Mount()
		if err != nil {
			return err
		}
	} else {
		error := errors.New(fmt.Sprintf("Database with uid %s does not exist", dbUid))
		l4g.Error(error)
		return error
	}

	return nil
}

// Unmount sets the database status to DB_STATUS_UNMOUNTED
// and deletes the according leveldb connector
func (store *DbStore) Unmount(dbUid string) (err error) {
	if db, present := store.Container[dbUid]; present {
		err = db.Unmount()
		if err != nil {
			return err
		}
	} else {
		error := errors.New(fmt.Sprintf("Database with uid %s does not exist", dbUid))
		l4g.Error(error)
		return error
	}

	return nil
}

// Add a db to the DbStore and syncs it
// to the store file
func (store *DbStore) Add(dbName string) (err error) {
	if _, present := store.NameToUid[dbName]; present {
		return errors.New("Database already exists")
	} else {
		var dbPath string

		if IsFilePath(dbName) {
			if !filepath.IsAbs(dbName) {
				error := errors.New("Creating database from relative path not allowed")
				l4g.Error(error)
				return error
			}

			dbPath = dbName
			// Check base db path exists
			dir := filepath.Dir(dbName)
			exists, err := DirExists(dir)
			if err != nil {
				l4g.Error(err)
				return err
			} else if !exists {
				error := errors.New(fmt.Sprintf("%s does not exist", dir))
				l4g.Error(error)
				return error
			}
		} else {
			dbPath = filepath.Join(store.Config.Core.StoragePath, dbName)
		}

		db := NewDb(dbName, dbPath, store.Config.Storage)
		store.Container[db.Uid] = db
		store.updateNameToUidIndex()
		err = store.WriteToFile()
		if err != nil {
			l4g.Error(err)
			return err
		}
		db.Mount()
	}

	l4g.Debug(func() string {
		return fmt.Sprintf("Database %s added to store", dbName)
	})

	return nil
}

// Drop removes a database from DbStore, and syncs it
// to store file
func (store *DbStore) Drop(dbName string) (err error) {
	if dbUid, present := store.NameToUid[dbName]; present {
		db := store.Container[dbUid]
		dbPath := db.Path

		store.Unmount(dbUid)
		delete(store.Container, dbUid)
		delete(store.NameToUid, dbName)
		store.WriteToFile()

		err = os.RemoveAll(dbPath)
		if err != nil {
			l4g.Error(err)
			return err
		}
	} else {
		error := errors.New(fmt.Sprintf("Database %s does not exist", dbName))
		l4g.Error(error)
		return error
	}

	l4g.Debug(func() string {
		return fmt.Sprintf("Database %s dropped from store", dbName)
	})

	return nil
}

// Status returns a database status defined by constants
// DB_STATUS_MOUNTED and DB_STATUS_UNMOUNTED
func (store *DbStore) Status(dbName string) (int, error) {
	if dbUid, present := store.NameToUid[dbName]; present {
		db := store.Container[dbUid]
		return db.Status, nil
	}

	return -1, errors.New("Database does not exist")
}

// Exists checks if a database present in DbStore
// exists on disk.
func (store *DbStore) Exists(dbName string) (bool, error) {
	if dbUid, present := store.NameToUid[dbName]; present {
		db := store.Container[dbUid]

		exists, err := DirExists(db.Path)
		if err != nil {
			return false, err
		}

		if exists == true {
			return exists, nil
		} else {
			// store.drop(dbName)
			fmt.Println("Dropping")
		}
	}

	return false, nil
}

// List enumerates  all the databases
// in DbStore
func (store *DbStore) List() []string {
	dbNames := make([]string, len(store.Container))

	i := 0
	for _, db := range store.Container {
		dbNames[i] = db.Name
		i++
	}

	return dbNames
}
