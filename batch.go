package elevator

type BatchOperations []BatchOperation

type BatchOperation struct {
	OpCode string
	OpArgs []string
}

// NewBatchOperation builds a BatchOperation from batch operation
// code and batch operation args
func NewBatchOperation(opCode string, opArgs []string) *BatchOperation {
	return &BatchOperation{
		OpCode: opCode,
		OpArgs: opArgs,
	}
}

// BatchOperationFromSlice builds a BatchOperation from
// a string slice containing the batch operation code and
// arguments
func BatchOperationFromSlice(slice []string) *BatchOperation {
	return NewBatchOperation(slice[0], slice[1:])
}

// BatchOperationsFromMessageArgs builds a BatchOperations from
// a string slice resprensenting a sequence of batch operations
func BatchOperationsFromMessageArgs(args []string) *BatchOperations {
	var ops BatchOperations
	var curIndex int = 0
	var lastIndex int = 0

	for index, elem := range args {
		curIndex = index
		if index > 0 {
			if elem == SIGNAL_BATCH_PUT || elem == SIGNAL_BATCH_DELETE {
				ops = append(ops, *BatchOperationFromSlice(args[lastIndex:index]))
				lastIndex = index
			}
		}
	}

	// Add the rest
	if curIndex > 0 {
		ops = append(ops, *BatchOperationFromSlice(args[lastIndex : curIndex+1]))
	}

	return &ops
}
