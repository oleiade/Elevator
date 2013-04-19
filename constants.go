package elevator

const DB_STATUS_MOUNTED = 1
const DB_STATUS_UNMOUNTED = 0

// Responses status
const (
	SUCCESS_STATUS = 1
	FAILURE_STATUS = -1
	WARNING_STATUS = -2
)

// Error codes
const (
	TYPE_ERROR     = 0
	KEY_ERROR      = 1
	VALUE_ERROR    = 2
	INDEX_ERROR    = 3
	RUNTIME_ERROR  = 4
	OS_ERROR       = 5
	DATABASE_ERROR = 6
	SIGNAL_ERROR   = 7
	REQUEST_ERROR  = 8
)

// Command codes
const (
	DB_GET     = "GET"
	DB_PUT     = "PUT"
	DB_DELETE  = "DELETE"
	DB_RANGE   = "RANGE"
	DB_SLICE   = "SLICE"
	DB_BATCH   = "BATCH"
	DB_MGET    = "MGET"
	DB_PING    = "PING"
	DB_CONNECT = "DBCONNECT"
	DB_MOUNT   = "DBMOUNT"
	DB_UMOUNT  = "DBUMOUNT"
	DB_CREATE  = "DBCREATE"
	DB_DROP    = "DBDROP"
	DB_LIST    = "DBLIST"
	DB_REPAIR  = "DBREPAIR"
)

// batches signals
const (
	SIGNAL_BATCH_PUT    = 1
	SIGNAL_BATCH_DELETE = 0
)
