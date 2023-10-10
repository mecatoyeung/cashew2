import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'

import Button from 'react-bootstrap/Button'
import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'
import Modal from 'react-bootstrap/Modal'

import StreamTable from '../streamTable'
import StreamSeparator from '../streamSeparator'
import AddStreamWrapper from '../addStreamWrapper'

import EditorLayout from '../../layouts/editor'

import service from "../../service"

import styles from '../../styles/Editor.module.css'

import streamConditionOperators from '../../helpers/streamConditionOperators'

const StreamEditor = () => {
  const router = useRouter()
  const { pathname, parserId, layoutId, ruleId, documentId = 0 } = router.query

  const [rule, setRule] = useState(null)
  const [parserDocuments, setParserDocuments] = useState([])

  const [processedStreams, setProcessedStreams] = useState(null)

  const [showChangeDocumentModal, setShowChangeDocumentModal] = useState(false)
  const closeChangeDocumentModalHandler = () => {
    setShowChangeDocumentModal(false)
  }
  const openChangeDocumentModalHandler = () => setShowChangeDocumentModal(true)

  const selectedDocumentChangeHandler = (e) => {
    router.push({
      pathname,
      query: {
        ...router.query,
        documentId: e.target.value
      },
    })
  }

  const getRule = () => {
    service.get("rules/" + ruleId + "/", response => {
      setRule(response.data)
    })
  }

  const getParserDocuments = () => {
    service.get("documents/?parserId=" + parserId , response => {
      setParserDocuments(response.data)
    })
  }

  const getProcessedStreams = () => {
    if (documentId == 0) return
    service.get("rules/" + ruleId + "/document/" + documentId + "/processed_streams/", response => {
      setProcessedStreams(response.data)
    })
  }

  const streamAddHandler = () => {
    getProcessedStreams()
  }

  const deleteStreamBtnClickHandler = (id) => {
    service.delete("streams/" + id + "/").then(() => {
      getRule()
      getParserDocuments()
      getProcessedStreams()
    })
  }

  const saveParsingRuleClickHandler = () => {
    router.push({
      pathname: "/workspace/parsers/" + parserId + "/rules",
      query: {
        documentId: documentId
      }
    })
  }

  useEffect(() => {
    if (!router.isReady) return
    getRule()
    getParserDocuments()
    getProcessedStreams()
  }, [router.isReady, ruleId, documentId])

  return (
    <EditorLayout>
      <div className={styles.workbenchWrapper}>
        <div className={styles.workbenchHeader}>
          <div className={styles.guidelines}>
            Add Filters
          </div>
          <div className={styles.changeSampleDocumentWrapper}>
            <Button variant="primary" className={styles.changeSampleDocumentBtn} onClick={openChangeDocumentModalHandler}>Change Sample Document</Button>
            <Modal show={showChangeDocumentModal} onHide={closeChangeDocumentModalHandler}>
              <Modal.Header closeButton>
                <Modal.Title>Change Document</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                <Form.Group className="mb-3" controlId="formRuleType">
                  <Form.Select aria-label="Document" onChange={selectedDocumentChangeHandler} value={documentId}>
                    <option value=""></option>
                    {parserDocuments && parserDocuments.map(parserDocument => (
                      <option key={parserDocument.id} value={parserDocument.id}>{parserDocument.filenameWithoutExtension + "." + parserDocument.extension}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Modal.Body>
              <Modal.Footer>
                <Button variant="primary" onClick={closeChangeDocumentModalHandler}>
                  Confirm
                </Button>
                <Button variant="secondary" onClick={closeChangeDocumentModalHandler}>
                  Close
                </Button>
              </Modal.Footer>
            </Modal>
          </div>
        </div>
        <div className={styles.streamEditorWrapper}>
          {processedStreams && processedStreams.map(processedStream => (
            <div key={processedStream.step}>
              {processedStream.step == 0 && (
                <div>
                  <div className={styles.streamDescription}>Original Extracted Data</div>
                  <StreamTable stream={processedStream} />
                </div>
              )}
              {processedStream.step != 0 && (
              <div>
                {(processedStream.type == "TEXTFIELD" || processedStream.type == "ANCHORED_TEXTFIELD") &&
                  (
                    <>
                      {processedStream.class == "EXTRACT_FIRST_N_LINES" && (
                        <div className={styles.streamDescription}>Extract first n lines: {processedStream.extractFirstNLines}</div>
                      )}
                      {processedStream.class == "EXTRACT_NTH_LINES" && (
                        <div className={styles.streamDescription}>Extract nth lines: {processedStream.extractNthLines}</div>
                      )}
                      {processedStream.class == "REGEX_EXTRACT" && (
                        <div className={styles.streamDescription}>Regex extract: {processedStream.regex}</div>
                      )}
                      {processedStream.class == "REGEX_REPLACE" && (
                        <div className={styles.streamDescription}>Regex replace from {processedStream.regex} to {processedStream.text}:</div>
                      )}
                      {processedStream.class == "TRIM_SPACE" && (
                        <div className={styles.streamDescription}>Trim space:</div>
                      )}
                      {processedStream.class == "REMOVE_EMPTY_LINES" && (
                        <div className={styles.streamDescription}>Remove empty lines:</div>
                      )}
                      {processedStream.class == "JOIN_ALL_ROWS" && (
                        <div className={styles.streamDescription}>Join all rows:</div>
                      )}
                      {processedStream.class == "REMOVE_TEXT_BEFORE_START_OF_TEXT" && (
                        <div className={styles.streamDescription}>Remove text before start of text {processedStream.text}:</div>
                      )}
                      {processedStream.class == "REMOVE_TEXT_BEFORE_END_OF_TEXT" && (
                        <div className={styles.streamDescription}>Remove text before end of text {processedStream.text}:</div>
                      )}
                      {processedStream.class == "REMOVE_TEXT_AFTER_START_OF_TEXT" && (
                        <div className={styles.streamDescription}>Remove Text after Start of Text {processedStream.text}:</div>
                      )}
                      {processedStream.class == "REMOVE_TEXT_AFTER_END_OF_TEXT" && (
                        <div className={styles.streamDescription}>Remove Text after End of Text {processedStream.text}:</div>
                      )}
                      <div className={styles.streamDeleteBtn}>
                        <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(processedStream.id)}>Delete</Button>
                      </div>
                      {processedStream.data && (
                        <table className={styles.streamTable}>
                          <tbody>
                            {processedStream.data.map((row, rowIndex) => {
                              return (
                                <tr key={rowIndex}>
                                  <td>{row.replace(/ /g, "\u00a0")}</td>
                                </tr>
                              )
                            })}
                          </tbody>
                        </table>
                      )}
                    </>
                  )
                }
                {processedStream.status == "error" && (
                  <div class="alert alert-danger" role="alert">
                    {processedStream.errorMessage}
                  </div>
                )}
                {processedStream.type == "TABLE" && (
                  <>
                    {processedStream.class == "COMBINE_FIRST_N_LINES" && (
                      <>
                        <div className={styles.streamDescription}>Combine first n lines: {processedStream.combineFirstNLines}</div>
                        <div className={styles.streamDeleteBtn}>
                          <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(processedStream.id)}>Delete</Button>
                        </div>
                      </>
                    )}
                    {processedStream.class == "GET_CHARS_FROM_NEXT_COL_IF_REGEX_NOT_MATCH" && (
                      <>
                        <div className={styles.streamDescription}>Get chars from next col if regex not match:</div>
                        <div className={styles.streamDescription}>Col Index: {processedStream.colIndex}</div>
                        <div className={styles.streamDescription}>Regex: {processedStream.regex}</div>
                        <div className={styles.streamDeleteBtn}>
                          <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(processedStream.id)}>Delete</Button>
                        </div>
                      </>
                    )}
                    {processedStream.class == "REMOVE_ROWS_WITH_CONDITIONS" && (
                      <>
                        <div className={styles.streamDescription}>Remove rows with conditions:</div>
                        <div className={styles.streamDeleteBtn}>
                          <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(processedStream.id)}>Delete</Button>
                        </div>
                        {console.log(processedStream)}
                        {processedStream.streamConditions.length > 0 && (
                          <Table>
                            <thead>
                              <tr>
                                <th>#</th>
                                <th>Column</th>
                                <th>Operator</th>
                                <th>Value</th>
                                <th></th>
                              </tr>
                            </thead>
                            <tbody>
                              {processedStream.streamConditions.map((condition, conditionIndex) => (
                                <tr key={conditionIndex}>
                                  <td>{conditionIndex + 1}</td>
                                  <td>
                                    {condition.column}
                                  </td>
                                  <td>
                                    {streamConditionOperators.find(o => o.value == condition.operator).label}
                                  </td>
                                  <td>
                                    {condition.value}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </Table>
                        )}
                      </>
                    )}
                    {processedStream.class == "MERGE_ROWS_WITH_CONDITIONS" && (
                      <>
                        <div className={styles.streamDescription}>Merge rows with conditions:</div>
                        <div className={styles.streamDeleteBtn}>
                          <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(processedStream.id)}>Delete</Button>
                        </div>
                        {processedStream.streamConditions.length > 0 && (
                          <Table>
                            <thead>
                              <tr>
                                <th>#</th>
                                <th>Column</th>
                                <th>Operator</th>
                                <th>Value</th>
                                <th></th>
                              </tr>
                            </thead>
                            <tbody>
                              {processedStream.streamConditions.map((condition, conditionIndex) => (
                                <tr key={conditionIndex}>
                                  <td>{conditionIndex + 1}</td>
                                  <td>
                                    {condition.column}
                                  </td>
                                  <td>
                                    {streamConditionOperators.find(o => o.value == condition.operator).label}
                                  </td>
                                  <td>
                                    {condition.value}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </Table>
                        )}
                      </>
                    )}
                    {processedStream.class == "MERGE_ROWS_WITH_SAME_COLUMNS" && (
                      <>
                        <div className={styles.streamDescription}>Merge rows with same columns: {processedStream.mergeRowsWithSameColumns}</div>
                        <div className={styles.streamDeleteBtn}>
                          <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(processedStream.id)}>Delete</Button>
                        </div>
                      </>
                    )}
                    {processedStream.class == "REMOVE_ROWS_BEFORE_ROW_WITH_CONDITIONS" && (
                      <>
                        <div className={styles.streamDescription}>Remove Rows before rows with conditions:</div>
                        <div className={styles.streamDeleteBtn}>
                          <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(processedStream.id)}>Delete</Button>
                        </div>
                        {processedStream.streamConditions.length > 0 && (
                          <Table>
                            <thead>
                              <tr>
                                <th>#</th>
                                <th>Column</th>
                                <th>Operator</th>
                                <th>Value</th>
                                <th></th>
                              </tr>
                            </thead>
                            <tbody>
                              {processedStream.streamConditions.map((condition, conditionIndex) => (
                                <tr key={conditionIndex}>
                                  <td>{conditionIndex + 1}</td>
                                  <td>
                                    {condition.column}
                                  </td>
                                  <td>
                                    {streamConditionOperators.find(o => o.value == condition.operator).label}
                                  </td>
                                  <td>
                                    {condition.value}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </Table>
                        )}
                        <Form.Group className="mb-3" controlId="formRemoveMatchedRowAlso">
                          <Form.Check
                            type="checkbox"
                            label="Remove matched row also"
                            checked={processedStream.removeMatchedRowAlso}
                          />
                        </Form.Group>
                      </>
                    )}
                    {processedStream.class == "REMOVE_ROWS_AFTER_ROW_WITH_CONDITIONS" && (
                      <>
                        <div className={styles.streamDescription}>Remove Rows after rows with conditions:</div>
                        <div className={styles.streamDeleteBtn}>
                          <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(processedStream.id)}>Delete</Button>
                        </div>
                        {processedStream.streamConditions.length > 0 && (
                          <Table>
                            <thead>
                              <tr>
                                <th>#</th>
                                <th>Column</th>
                                <th>Operator</th>
                                <th>Value</th>
                                <th></th>
                              </tr>
                            </thead>
                            <tbody>
                              {processedStream.streamConditions.map((condition, conditionIndex) => (
                                <tr key={conditionIndex}>
                                  <td>{conditionIndex + 1}</td>
                                  <td>
                                    {condition.column}
                                  </td>
                                  <td>
                                    {streamConditionOperators.find(o => o.value == condition.operator).label}
                                  </td>
                                  <td>
                                    {condition.value}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </Table>
                        )}
                        <Form.Group className="mb-3" controlId="formRemoveMatchedRowAlso">
                          <Form.Check
                            type="checkbox"
                            label="Remove matched row also"
                            checked={processedStream.removeMatchedRowAlso}
                          />
                        </Form.Group>
                      </>
                    )}
                    {processedStream.class == "UNPIVOT_TABLE" && (
                      <>
                        <div className={styles.streamDescription}>Unpivot table:</div>
                        <div className={styles.streamDescription}>Column Index: {JSON.parse(processedStream.unpivotTable).unpivot_column_index}</div>
                        <div className={styles.streamDescription}>New Line Character: {JSON.parse(processedStream.unpivotTable).newline_char}</div>
                        <div className={styles.streamDescription}>Property Assign Character: {JSON.parse(processedStream.unpivotTable).property_assign_char}</div>
                        <div className={styles.streamDeleteBtn}>
                          <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(processedStream.id)}>Delete</Button>
                        </div>
                        {processedStream.unpivotTableConditions.length > 0 && (
                          <Table>
                            <thead>
                              <tr>
                                <th>#</th>
                                <th>Column</th>
                                <th>Operator</th>
                                <th>Value</th>
                                <th></th>
                              </tr>
                            </thead>
                            <tbody>
                              {processedStream.unpivoTableConditions.map((condition, conditionIndex) => (
                                <tr key={conditionIndex}>
                                  <td>{conditionIndex + 1}</td>
                                  <td>
                                    {condition.column}
                                  </td>
                                  <td>
                                    {condition.operator}
                                  </td>
                                  <td>
                                    {condition.value}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </Table>
                        )}
                      </>
                    )}
                    {processedStream.class == "TRIM_SPACE_FOR_ALL_ROWS_AND_COLS" && (
                      <>
                        <div className={styles.streamDescription}>Trim Space for All Rows and Columns:</div>
                        <div className={styles.streamDeleteBtn}>
                          <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(processedStream.id)}>Delete</Button>
                        </div>
                      </>
                    )}
                    {processedStream.class == "MAKE_FIRST_ROW_TO_BE_HEADER" && (
                      <>
                        <div className={styles.streamDescription}>Make first row to be header:</div>
                        <div className={styles.streamDeleteBtn}>
                          <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(processedStream.id)}>Delete</Button>
                        </div>
                      </>
                    )}
                    {processedStream.class == "CONVERT_TO_TABLE_BY_SPECIFY_HEADERS" && (
                      <>
                        <div className={styles.streamDescription}>Convert to table by specify header:</div>
                        <div className={styles.streamDeleteBtn}>
                          <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(processedStream.id)}>Delete</Button>
                        </div>
                      </>
                    )}
                    {processedStream.data && (
                      <div className={styles.streamTableDiv}>
                        <table className={styles.streamTable}>
                          <thead>
                            <tr>
                              {processedStream.data.header.map((header, headerIndex) => {
                                return (
                                  <th key={headerIndex}>{header}</th>
                                )
                              })}
                            </tr>
                          </thead>
                          <tbody>
                            {processedStream.data.body.map((row, rowIndex) => {
                              return (
                                <tr key={rowIndex}>
                                  {row.map((col, colIndex) => {
                                    return (
                                      <td key={colIndex}>{col.replace(/ /g, "\u00a0")}</td>
                                    )
                                  })}
                                </tr>
                              )
                            })}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </>
                )}
              </div>)}
              <div className={styles.streamSeparatorWrapper}>
                <div className={styles.separatorBefore}>
                  <AddStreamWrapper rule={rule} stream={processedStream} streamAddHandler={streamAddHandler}/>
                </div>
                <StreamSeparator />
              </div>
            </div>
          ))}
        </div>
        <div className={styles.workbenchFooter}>
          <div className={styles.backBtnWrapper}>
            <Link href={"/workspace/parsers/" + parserId + "/rules/" + ruleId + "?type=regionSelector&documentId=" + documentId}>
              &lt; Back to Region Selection
            </Link>
          </div>
          <div className={styles.copyrightWrapper}>
            Copyright @ 2022
          </div>
          <div className={styles.confirmBtnWrapper}>
            <Button variant="success" className={styles.confirmBtn} onClick={saveParsingRuleClickHandler}>Save Parsing Rule</Button>
          </div>
        </div>
      </div>
    </EditorLayout>
  )
}

export default StreamEditor