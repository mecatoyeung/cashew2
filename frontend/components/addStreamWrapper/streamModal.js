import styles from '../../styles/Editor.module.css'

import Button from 'react-bootstrap/Button'
import Form from 'react-bootstrap/Form'
import Modal from 'react-bootstrap/Modal'
import Table from 'react-bootstrap/Table'

import Select from 'react-select'
import { useState } from 'react'

import StreamConditions from "./streamConditions"

import service from '../../service'

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
        label: "Get Chars from next column when regex not match",
        value: "GET_CHARS_FROM_NEXT_COL_WHEN_REGEX_NOT_MATCH"
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
        value: "TRIM_SPACE_TABLE"
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

const AddStreamModal = (props) => {

  const [stream, setStream] = useState({
    step: props.stream.step + 1,
    rule: props.rule.id,
    type: props.stream.type,
    streamClass: "",
    extractFirstNLines: 1,
    extractNthLines: 1,
    joinString: "",
    text: "",
    regex: "",
    combineFirstNLines: 2,
    getCharsFromNextColWhenRegexNotMatch: {
      colIndex: "",
      regex: ""
    },
    removeRowsWithConditions: [],
    mergeRowsWithConditions: {
      column_conditions: []
    },
    mergeRowsWithSameColumns: "",
    removeRowsBeforeRowWithConditions: [],
    removeRowsAfterRowWithConditions: [],
    removeMatchedRowAlso: false,
    unpivotTable: {
      unpivotColumnIndex: "",
      newlineChar: "",
      propertyAssignCharacter: "",
      unpivotTableConditions: []
    },
    convertToTableBySpecifyHeaders: {
      "headers": [{ header: "" }]
    }
  })

  const selectedStreamClassChangeHandler = (e) => {
    let updatedStream = { ...stream }
    updatedStream.streamClass = e
    setStream(updatedStream)
  }

  const txtRegexChangeHandler = (e) => {
    let updatedStream = { ...stream }
    updatedStream.regex = e.target.value
    setStream(updatedStream)
  }

  const txtExtractFirstNLinesChangeHandler = (e) => {
    let updatedStream = { ...stream }
    updatedStream.extractFirstNLines = parseInt(e.target.value)
    setStream(updatedStream)
  }

  const txtExtractNthLinesChangeHandler = (e) => {
    let updatedStream = { ...stream }
    updatedStream.extractNthLines = e.target.value
    setStream(updatedStream)
  }

  const txtJoinStringChangeHandler = (e) => {
    let updatedStream = { ...stream }
    updatedStream.joinString = e.target.value
    setStream(updatedStream)
  }

  const txtTextChangeHandler = (e) => {
    let updatedStream = { ...stream }
    updatedStream.text = e.target.value
    setStream(updatedStream)
  }

  const txtCombineFirstNLinesChangeHandler = (e) => {
    let updatedStream = { ...stream }
    updatedStream.combineFirstNLines = parseInt(e.target.value)
    setStream(updatedStream)
  }

  const txtGetCharsFromNextColWhenRegexNotMatchColIndexChangeHandler = (e) => {
    let updatedStream = { ...stream }
    let getCharsFromNextColWhenRegexNotMatchJSON = JSON.parse(updatedStream.getCharsFromNextColWhenRegexNotMatch)
    getCharsFromNextColWhenRegexNotMatchJSON.col_index = e.target.value
    updatedStream.getCharsFromNextColWhenRegexNotMatch = JSON.stringify(getCharsFromNextColWhenRegexNotMatchJSON)
    setStream(updatedStream)
  }

  const txtGetCharsFromNextColWhenRegexNotMatchRegexChangeHandler = (e) => {
    let updatedStream = { ...stream }
    let getCharsFromNextColWhenRegexNotMatchJSON = JSON.parse(updatedStream.getCharsFromNextColWhenRegexNotMatch)
    getCharsFromNextColWhenRegexNotMatchJSON.regex = e.target.value
    updatedStream.getCharsFromNextColWhenRegexNotMatch = JSON.stringify(getCharsFromNextColWhenRegexNotMatchJSON)
    setStream(updatedStream)
  }

  const txtMergeRowsWithSameColumnsChangeHandler = (e) => {
    let updatedStream = { ...stream }
    updatedStream.mergeRowsWithSameColumns = e.target.value
    setStream(updatedStream)
  }

  const txtUnpivotColIndexChangeHandler = (e) => {
    let updatedStream = { ...stream }
    let unpivotTableJSON = JSON.parse(updatedStream.unpivotTable)
    unpivotTableJSON.unpivot_column_index = e.target.value
    updatedStream.unpivotTable = JSON.stringify(unpivotTableJSON)
    setStream(updatedStream)
  }

  const txtUnpivotNewLineCharChangeHandler = (e) => {
    let updatedStream = { ...stream }
    let unpivotTableJSON = JSON.parse(updatedStream.unpivotTable)
    unpivotTableJSON.newline_char = e.target.value
    updatedStream.unpivotTable = JSON.stringify(unpivotTableJSON)
    setStream(updatedStream)
  }

  const txtUnpivotPropertyAssignCharChangeHandler = (e) => {
    let updatedStream = { ...stream }
    let unpivotTableJSON = JSON.parse(updatedStream.unpivotTable)
    unpivotTableJSON.property_assign_char = e.target.value
    updatedStream.unpivotTable = JSON.stringify(unpivotTableJSON)
    setStream(updatedStream)
  }

  const updateConditionsHandler = (conditions) => {
    let updatedStream = { ...stream }
    if (stream.streamClass.value == "REMOVE_ROWS_WITH_CONDITIONS") {
      updatedStream.removeRowsWithConditions = conditions
    } else if (stream.streamClass.value == "MERGE_ROWS_WITH_CONDITIONS") {
      updatedStream.mergeRowsWithConditions = conditions
    } else if (stream.streamClass.value == "REMOVE_ROWS_BEFORE_ROW_WITH_CONDITIONS") {
      updatedStream.removeRowsBeforeRowWithConditions = conditions
    } else if (stream.streamClass.value == "REMOVE_ROWS_AFTER_ROW_WITH_CONDITIONS") {
      updatedStream.removeRowsAfterRowWithConditions = conditions
    }
    setStream(updatedStream)
  }

  const updateUnpivotTableRowConditionsHandler = (conditions) => {
    let updatedStream = { ...stream }
    updatedStream.unpivotTableConditions = conditions
    setStream(updatedStream)
  }

  const txtTableHeaderChangeHandler = (index, e) => {
    let updatedStream = { ...stream }
    updatedStream.convertToTableBySpecifyHeaders.headers[index]["header"] = e.target.value
    setStream(updatedStream)
  }

  const addTableHeaderClickHandler = () => {
    let updatedStream = { ...stream }
    updatedStream.convertToTableBySpecifyHeaders.headers.push({ "header": "" })
    setStream(updatedStream)
  }

  const removeTableHeaderClickHandler = (index) => {
    if (stream.convertToTableBySpecifyHeaders <= 1) return
    let updatedStream = { ...stream }
    updatedStream.convertToTableBySpecifyHeaders.splice(index, 1)
    setStream(updatedStream)
  }

  const confirmAddStreamButtonClickHandler = () => {
    service.post("streams/",
      {
        ...stream,
        streamClass: stream.streamClass.value
      },
      response => {
        props.streamAddHandler()
      }
    )
  }

  return (
    <Modal show={props.show}
      onHide={() => props.hideHandler(false)}
      size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Add Stream</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form.Group className="mb-3" controlId="formStep">
          <Form.Label>Step: </Form.Label>
          <Form.Control value={stream.step} readOnly />
        </Form.Group>
        <Form.Group className="mb-3" controlId="formStreamClass">
          {(stream.type == "TEXTFIELD" || stream.type == "ANCHORED_TEXTFIELD") && (
            <Select
              options={textfieldStreamOptions}
              value={stream.streamClass}
              onChange={(e) => selectedStreamClassChangeHandler(e)}
              menuPlacement="auto"
              menuPosition="fixed" />
          )}
          {stream.type == "TABLE" && (
            <Select
              options={tableStreamOptions}
              value={stream.streamClass}
              onChange={(e) => selectedStreamClassChangeHandler(e)}
              menuPlacement="auto"
              menuPosition="fixed" />
          )}
        </Form.Group>
        {stream.streamClass.value == "EXTRACT_FIRST_N_LINES" && (
          <Form.Group className="mb-3" controlId="formRegex">
            <Form.Label>n: </Form.Label>
            <Form.Control value={stream.extractFirstNLines} onChange={txtExtractFirstNLinesChangeHandler} />
          </Form.Group>
        )}
        {stream.streamClass.value == "EXTRACT_NTH_LINES" && (
          <Form.Group className="mb-3" controlId="formRegex">
            <Form.Label>n: </Form.Label>
            <Form.Control value={stream.extractNthLines} onChange={txtExtractNthLinesChangeHandler} placeholder="1,2,4-9"/>
          </Form.Group>
        )}
        {stream.streamClass.value == "COMBINE_FIRST_N_LINES" && (
          <>
            <Form.Group className="mb-3" controlId="formCombineFirstNLines">
              <Form.Label>n: </Form.Label>
              <Form.Control value={stream.combine_first_n_lines} onChange={txtCombineFirstNLinesChangeHandler} />
            </Form.Group>
          </>
        )}
        {stream.streamClass.value == "TRIM_SPACE_TABLE" && (
          <Form.Group className="mb-3" controlId="formRegex">
            <Form.Label>Trim all rows and columns</Form.Label>
          </Form.Group>
        )}
        {stream.streamClass.value == "REGEX_EXTRACT" && (
          <Form.Group className="mb-3" controlId="formRegex">
            <Form.Label>Regex: </Form.Label>
            <Form.Control value={stream.regex} onChange={txtRegexChangeHandler} placeholder="Please include brackets for regex capture group. (e.g., ([a-zA-Z0-9 _.-]*))"/>
          </Form.Group>
        )}
        {stream.streamClass.value == "REGEX_REPLACE" && (
          <>
            <Form.Group className="mb-3" controlId="formRegex">
              <Form.Label>Regex: </Form.Label>
              <Form.Control value={stream.regex} onChange={txtRegexChangeHandler} placeholder="Please include brackets for regex capture group. (e.g., ([a-zA-Z0-9 _.-]*))"/>
            </Form.Group>
            <Form.Group className="mb-3" controlId="formReplaceText">
              <Form.Label>Replace text: </Form.Label>
              <Form.Control value={stream.replaceText} onChange={txtTextChangeHandler} />
            </Form.Group>
          </>
        )}
        {stream.streamClass.value == "JOIN_ALL_ROWS" && (
          <>
            <Form.Group className="mb-3" controlId="formJoinString">
              <Form.Label>Join String: </Form.Label>
              <Form.Control value={stream.joinString} onChange={txtJoinStringChangeHandler} placeholder="e.g. ', '"/>
            </Form.Group>
          </>
        )}
        {(stream.streamClass.value == "REMOVE_TEXT_BEFORE_START_OF_TEXT" ||
          stream.streamClass.value == "REMOVE_TEXT_BEFORE_END_OF_TEXT" ||
          stream.streamClass.value == "REMOVE_TEXT_AFTER_START_OF_TEXT" ||
          stream.streamClass.value == "REMOVE_TEXT_AFTER_END_OF_TEXT") && (
            <>
              <Form.Group className="mb-3" controlId="formReplaceText">
                <Form.Label>Remove text: </Form.Label>
                <Form.Control value={stream.text} onChange={txtTextChangeHandler} />
              </Form.Group>
            </>
          )}
        {stream.streamClass.value == "GET_CHARS_FROM_NEXT_COL_WHEN_REGEX_NOT_MATCH" && (
          <>
            <Form.Group className="mb-3" controlId="formGetCharsFromNextColWhenRegexNotMatch">
              <Form.Label>Col Index: </Form.Label>
              <Form.Control value={stream.getCharsFromNextColWhenRegexNotMatch} onChange={txtGetCharsFromNextColWhenRegexNotMatchColIndexChangeHandler} />
            </Form.Group>
            <Form.Group className="mb-3" controlId="formGetCharsFromNextColWhenRegexNotMatch">
              <Form.Label>Regex: </Form.Label>
              <Form.Control value={stream.getCharsFromNextColWhenRegexNotMatch} onChange={txtGetCharsFromNextColWhenRegexNotMatchRegexChangeHandler} />
            </Form.Group>
          </>
        )}
        {stream.streamClass.value == "REMOVE_ROWS_WITH_CONDITIONS" && (
          <StreamConditions conditions={stream.removeRowsWithConditions} onUpdateConditions={(conditions) => updateConditionsHandler(conditions)} />
        )}
        {stream.streamClass.value == "MERGE_ROWS_WITH_CONDITIONS" && (
          <StreamConditions conditions={stream.mergeRowsWithConditions} onUpdateConditions={(conditions) => updateConditionsHandler(conditions)} />
        )}
        {stream.streamClass.value == "MERGE_ROWS_WITH_SAME_COLUMNS" && (
          <>
            <Form.Group className="mb-3" controlId="formReplaceText">
              <Form.Label>Same columns: </Form.Label>
              <Form.Control value={stream.mergeRowsWithSameColumns} onChange={txtMergeRowsWithSameColumnsChangeHandler} />
            </Form.Group>
          </>
        )}
        {stream.streamClass.value == "REMOVE_ROWS_BEFORE_ROW_WITH_CONDITIONS" && (
          <StreamConditions conditions={stream.removeRowsBeforeRowWithConditions} onUpdateConditions={(conditions) => updateConditionsHandler(conditions)} />
        )}
        {stream.streamClass.value == "REMOVE_ROWS_AFTER_ROW_WITH_CONDITIONS" && (
          <StreamConditions conditions={stream.removeRowsAfterRowWithConditions} onUpdateConditions={(conditions) => updateConditionsHandler(conditions)} />
        )}
        {stream.streamClass.value == "UNPIVOT_TABLE" && (
          <>
            <Form.Group className="mb-3" controlId="formUnpivotColIndex">
              <Form.Label>Column index: </Form.Label>
              <Form.Control value={JSON.parse(stream.unpivotTable).unpivotColumnIndex} onChange={txtUnpivotColIndexChangeHandler} />
            </Form.Group>
            <Form.Group className="mb-3" controlId="formUnpivotNewLineChar">
              <Form.Label>New line character: </Form.Label>
              <Form.Control value={JSON.parse(stream.unpivotTable).newlineChar} onChange={txtUnpivotNewLineCharChangeHandler} />
            </Form.Group>
            <Form.Group className="mb-3" controlId="formUnpivotPropertyAssignChar">
              <Form.Label>Property assign character: </Form.Label>
              <Form.Control value={JSON.parse(stream.unpivotTable).propertyAssignChar} onChange={txtUnpivotPropertyAssignCharChangeHandler} />
            </Form.Group>
            <StreamConditions conditions={stream.unpivotTableConditions} onUpdateConditions={(conditions) => updateUnpivotTableRowConditionsHandler(conditions)} />
          </>
        )}
        {stream.streamClass.value == "CONVERT_TO_TABLE_BY_SPECIFY_HEADERS" && (
          <>
            <Table striped bordered hover>
              <tr>
                <th>Headers</th>
                <th>Actions</th>
              </tr>
              {stream.convertToTableBySpecifyHeaders.headers.map((header, headerIndex) => (
                <tr key={headerIndex}>
                  <td>
                    <Form.Control value={header.header} onChange={(e) => txtTableHeaderChangeHandler(headerIndex, e)} />
                  </td>
                  <td>
                    <Button variant="danger" onClick={() => removeTableHeaderClickHandler(headerIndex)}>Remove</Button>
                  </td>
                </tr>
              ))}
            </Table>
            <Button onClick={() => addTableHeaderClickHandler()}>Add</Button>
          </>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="primary" onClick={confirmAddStreamButtonClickHandler}>
          Confirm
        </Button>
        <Button variant="secondary" onClick={() => props.onClose()}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  )
}

export default AddStreamModal