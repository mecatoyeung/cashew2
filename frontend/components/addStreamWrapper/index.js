import styles from '../../styles/Editor.module.css'

import Button from 'react-bootstrap/Button'
import Form from 'react-bootstrap/Form'
import Modal from 'react-bootstrap/Modal'
import Table from 'react-bootstrap/Table'

import Select from 'react-select'
import { useState } from 'react'

import StreamModal from './streamModal'

import { ST } from 'next/dist/shared/lib/utils'

const textfieldStreamOptions = [
  {
    label: "Extract Streams",
    options: [
      {
        label: "Extract first n lines",
        value: "EXTRACT_FIRST_N_LINES"
      },
      {
        label: "Extract nth lines",
        value: "EXTRACT_NTH_LINES"
      }
    ]
  },
  {
    label: "Regex Streams",
    options: [
      {
        label: "Regex Extract",
        value: "REGEX_EXTRACT"
      },
      {
        label: "Regex Replace",
        value: "REGEX_REPLACE"
      }
    ]
  },
  {
    label: "Join, Replace, Remove Streams",
    options: [
      {
        label: "Join All Rows",
        value: "JOIN_ALL_ROWS"
      },
      {
        label: "Remove Text before Start of Text",
        value: "REMOVE_TEXT_BEFORE_START_OF_TEXT"
      },
      {
        label: "Remove Text before End of Text",
        value: "REMOVE_TEXT_BEFORE_END_OF_TEXT"
      },
      {
        label: "Remove Text after Start of Text",
        value: "REMOVE_TEXT_AFTER_START_OF_TEXT"
      },
      {
        label: "Remove Text after End of Text",
        value: "REMOVE_TEXT_AFTER_END_OF_TEXT"
      }
    ]
  },
  {
    label: "Trim Space and Remove Empty Lines",
    options: [
      {
        label: "Trim Space",
        value: "TRIM_SPACE"
      },
      {
        label: "Remove Empty Lines",
        value: "REMOVE_EMPTY_LINES"
      }
    ]
  },
  {
    label: "Convert to Table",
    options: [
      {
        label: "Convert to table by specify headers",
        value: "CONVERT_TO_TABLE_BY_SPECIFY_HEADERS"
      }
    ]
  },
  {
    label: "Open AI Extract",
    options: [
      {
        label: "Open AI Extract",
        value: "OPEN_AI"
      }
    ]
  }
]

const tableStreamOptions = [
  {
    label: "Combine lines",
    options: [
      {
        label: "Combine first n lines",
        value: "COMBINE_FIRST_N_LINES"
      }
    ]
  },
  {
    label: "Column Operations",
    options: [
      {
        label: "Get characters from next column if regex not match",
        value: "GET_CHARS_FROM_NEXT_COL_IF_REGEX_NOT_MATCH"
      },
      {
        label: "Merge rows with same columns",
        value: "MERGE_ROWS_WITH_SAME_COLUMNS"
      },
    ]
  },
  {
    label: "Trim spaces",
    options: [
      {
        label: "Trim all rows and columns",
        value: "TRIM_SPACE_FOR_ALL_ROWS_AND_COLS"
      },
    ]
  },
  {
    label: "Process Rows with Conditions",
    options: [
      {
        label: "Remove Rows with Conditions",
        value: "REMOVE_ROWS_WITH_CONDITIONS"
      },
      {
        label: "Merge Rows with Conditions",
        value: "MERGE_ROWS_WITH_CONDITIONS"
      },
      {
        label: "Remove Rows before Row with Conditions",
        value: "REMOVE_ROWS_BEFORE_ROW_WITH_CONDITIONS"
      },
      {
        label: "Remove Rows after Row with Conditions",
        value: "REMOVE_ROWS_AFTER_ROW_WITH_CONDITIONS"
      }
    ]
  },
  {
    label: "Unpivot Table",
    options: [
      {
        label: "Unpivot Table",
        value: "UNPIVOT_TABLE"
      }
    ]
  },
  {
    label: "Header",
    options: [
      {
        label: "Make first row to be header",
        value: "MAKE_FIRST_ROW_TO_BE_HEADER"
      }
    ]
  }
]

const AddStreamWrapper = (props) => {

  const [showAddStreamModal, setShowAddStreamModal] = useState(false)

  const addStreamButtonClickHandler = (e) => {
    setShowAddStreamModal(true)
  }

  const streamAddHandler = () => {
    setShowAddStreamModal(false)
    props.streamAddHandler()
  }

  return (
    <div className={styles.addFilterDropDownWrapper}>
      <Button variant="primary" onClick={addStreamButtonClickHandler}>
        Add Stream
      </Button>
      <StreamModal
        rule={props.rule}
        stream={props.stream}
        show={showAddStreamModal}
        hideHandler={() => setShowAddStreamModal(false)}
        streamAddHandler={streamAddHandler}
        onClose={() => streamAddHandler()}/>
    </div>
  )
}

export default AddStreamWrapper