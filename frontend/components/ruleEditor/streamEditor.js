import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'

import cn from 'classnames'

import Dropdown from 'react-bootstrap/Dropdown'
import Button from 'react-bootstrap/Button'
import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'
import Modal from 'react-bootstrap/Modal'

import EditorLayout from '../../components/layouts/editor'

import service from "../../service"

import styles from '../../styles/Editor.module.css'

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
    service.get("rules/" + ruleId, response => {
      setRule(response.data)
    })
  }

  const getParserDocuments = () => {
    service.get("documents/parserId=" + parserId , response => {
      setParserDocuments(response.data)
    })
  }

  const getProcessedStreams = () => {
    service.get("rules/" + ruleId + "/process-document/" + documentId + "/processed-stream", response => {
      setProcessedStreams(response.data)
    })
  }

  const addStreamHandler = (stream) => {
    service.post("streams/", {
    }).then(() => {
      getRule()
      getProcessedStreams()
    })
  }

  const deleteStreamBtnClickHandler = (id) => {
    service.delete("streams/" + id).then(() => {
      getRule()
      getParserDocuments()
      getProcessedStreams()
    })
  }

  const saveParsingRuleClickHandler = () => {
    router.push({
      pathname: "/workspace/parsers/" + parserId + "/layouts/" + layoutId + "/rules",
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
            Define Field Position - Draw a rectangle around the fixed position where the text is located
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
          {processedStreams && processedStreams.processedStreams.map(stream => {
            if (stream.step == 0) {
              return (
                <div key={stream.step}>
                  <div className={styles.streamDescription}>Your Raw Data</div>
                  {(stream.type == "TEXTFIELD") && (
                    <div className={styles.streamTableDiv}>
                      <table className={styles.streamTable}>
                        <tbody>
                          {stream.data.map((row, rowIndex) => {
                            return (
                              <tr key={rowIndex}>
                                <td>{row.replace(/ /g, "\u00a0")}</td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                  {stream.type == "ANCHORED_TEXTFIELD" && (
                    <div className={styles.streamTableDiv}>
                      <table className={styles.streamTable}>
                        <tbody>
                          {stream.data.map((row, rowIndex) => {
                            return (
                              <tr key={rowIndex}>
                                <td>{row.replace(/ /g, "\u00a0")}</td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                  {stream.type == "TABLE" && (
                    <div className={styles.streamTableDiv}>
                      <table className={styles.streamTable}>
                        <tbody>
                          {stream.data.body.map((row, rowIndex) => {
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
                  <StreamSeparator step={stream.step} streamType={stream.type} streamClass={stream.stream_class} onAddStream={(stream) => addStreamHandler(stream)}></StreamSeparator>
                </div>
              )
            } else {
              return (
                <div key={stream.step}>
                  {stream.status == "error" && (
                    <div class="alert alert-dark" role="alert">
                      {stream.errorMessage}
                    </div>
                  )}
                  {(stream.type == "TEXTFIELD" || stream.type == "ANCHORED_TEXTFIELD") &&
                    (
                      <>
                        {stream.class == "REGEX_EXTRACT" && (
                          <div className={styles.streamDescription}>Regex Extract: {stream.regex}</div>
                        )}
                        {stream.class == "REGEX_REPLACE" && (
                          <div className={styles.streamDescription}>Regex Replace from {stream.regex} to {stream.replace_text}:</div>
                        )}
                        {stream.class == "EXTRACT_FIRST_N_LINE" && (
                          <div className={styles.streamDescription}>Extract N Line: {stream.extract_first_n_lines}</div>
                        )}
                        {stream.class == "EXTRACT_NTH_LINE" && (
                          <div className={styles.streamDescription}>Extract Nth Line: {stream.extract_nth_line}</div>
                        )}
                        {stream.class == "TRIM_SPACE" && (
                          <div className={styles.streamDescription}>Trim Space:</div>
                        )}
                        {stream.class == "JOIN_ALL_ROWS" && (
                          <div className={styles.streamDescription}>Join All Rows:</div>
                        )}
                        {stream.class == "REMOVE_TEXT_BEFORE_START_OF_TEXT" && (
                          <div className={styles.streamDescription}>Remove Text before Start of Text {stream.remove_text}:</div>
                        )}
                        {stream.class == "REMOVE_TEXT_BEFORE_END_OF_TEXT" && (
                          <div className={styles.streamDescription}>Remove Text before End of Text {stream.remove_text}:</div>
                        )}
                        {stream.class == "REMOVE_TEXT_AFTER_START_OF_TEXT" && (
                          <div className={styles.streamDescription}>Remove Text after Start of Text {stream.remove_text}:</div>
                        )}
                        {stream.class == "REMOVE_TEXT_AFTER_END_OF_TEXT" && (
                          <div className={styles.streamDescription}>Remove Text after End of Text {stream.remove_text}:</div>
                        )}
                        <div className={styles.streamDeleteBtn}>
                          <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(stream.id)}>Delete</Button>
                        </div>
                        <table className={styles.streamTable}>
                          <tbody>
                            {stream.data.map((row, rowIndex) => {
                              return (
                                <tr key={rowIndex}>
                                  <td>{row.replace(/ /g, "\u00a0")}</td>
                                </tr>
                              )
                            })}
                          </tbody>
                        </table>
                      </>
                    )
                  }
                  {stream.type == "TABLE" && (
                    <>
                      {stream.class == "COMBINE_FIRST_N_LINES" && (
                        <>
                          <div className={styles.streamDescription}>Combine first n lines: {stream.combineFirstNLines}</div>
                          <div className={styles.streamDeleteBtn}>
                            <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(stream.id)}>Delete</Button>
                          </div>
                        </>
                      )}
                      {stream.class == "GET_CHARS_FROM_NEXT_COL_WHEN_REGEX_NOT_MATCH" && (
                        <>
                          <div className={styles.streamDescription}>Get chars from next col when regex not match:</div>
                          <div className={styles.streamDescription}>Col Index: {JSON.parse(stream.getCharsFromNextColWhenRegexNotMatch).col_index}</div>
                          <div className={styles.streamDescription}>Regex: {JSON.parse(stream.getCharsFromNextColWhenRegexNotMatch).regex}</div>
                          <div className={styles.streamDeleteBtn}>
                            <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(stream.id)}>Delete</Button>
                          </div>
                        </>
                      )}
                      {stream.class == "REMOVE_ROWS_WITH_CONDITIONS" && (
                        <>
                          <div className={styles.streamDescription}>Remove rows with conditions:</div>
                          <div className={styles.streamDeleteBtn}>
                            <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(stream.id)}>Delete</Button>
                          </div>
                          {JSON.parse(stream.removeRowsWithConditions).length > 0 && (
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
                                {JSON.parse(stream.removeRowsWithConditions).map((condition, conditionIndex) => (
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
                      {stream.class == "MERGE_ROWS_WITH_CONDITIONS" && (
                        <>
                          <div className={styles.streamDescription}>Merge rows with conditions:</div>
                          <div className={styles.streamDeleteBtn}>
                            <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(stream.id)}>Delete</Button>
                          </div>
                          {JSON.parse(stream.mergeRowsWithConditions).length > 0 && (
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
                                {JSON.parse(stream.mergeRowsWithConditions).map((condition, conditionIndex) => (
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
                      {stream.class == "MERGE_ROWS_WITH_SAME_COLUMNS" && (
                        <>
                          <div className={styles.streamDescription}>Merge rows with same columns: {stream.mergeRowsWithSameColumns}</div>
                          <div className={styles.streamDeleteBtn}>
                            <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(stream.id)}>Delete</Button>
                          </div>
                        </>
                      )}
                      {stream.class == "REMOVE_ROWS_BEFORE_ROW_WITH_CONDITIONS" && (
                        <>
                          <div className={styles.streamDescription}>Remove Rows before rows with conditions:</div>
                          <div className={styles.streamDeleteBtn}>
                            <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(stream.id)}>Delete</Button>
                          </div>
                          {JSON.parse(stream.removeRowsBeforeRowWithConditions).length > 0 && (
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
                                {JSON.parse(stream.removeRowsBeforeRowWithConditions).map((condition, conditionIndex) => (
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
                      {stream.class == "REMOVE_ROWS_AFTER_ROW_WITH_CONDITIONS" && (
                        <>
                          <div className={styles.streamDescription}>Remove Rows after rows with conditions:</div>
                          <div className={styles.streamDeleteBtn}>
                            <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(stream.id)}>Delete</Button>
                          </div>
                          {JSON.parse(stream.removeRowsAfterRowWithConditions).length > 0 && (
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
                                {JSON.parse(stream.removeRowsAfterRowWithConditions).map((condition, conditionIndex) => (
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
                      {stream.class == "UNPIVOT_TABLE" && (
                        <>
                          <div className={styles.streamDescription}>Unpivot table:</div>
                          <div className={styles.streamDescription}>Column Index: {JSON.parse(stream.unpivotTable).unpivot_column_index}</div>
                          <div className={styles.streamDescription}>New Line Character: {JSON.parse(stream.unpivotTable).newline_char}</div>
                          <div className={styles.streamDescription}>Property Assign Character: {JSON.parse(stream.unpivotTable).property_assign_char}</div>
                          <div className={styles.streamDeleteBtn}>
                            <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(stream.id)}>Delete</Button>
                          </div>
                          {JSON.parse(stream.unpivotTableConditions).length > 0 && (
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
                                {JSON.parse(stream.unpivoTableConditions).map((condition, conditionIndex) => (
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
                      {stream.class == "TRIM_SPACE_TABLE" && (
                        <>
                          <div className={styles.streamDescription}>Trim Space for All Rows and Columns:</div>
                          <div className={styles.streamDeleteBtn}>
                            <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(stream.id)}>Delete</Button>
                          </div>
                        </>
                      )}
                      {stream.class == "MAKE_FIRST_ROW_TO_BE_HEADER" && (
                        <>
                          <div className={styles.streamDescription}>Make first row to be header:</div>
                          <div className={styles.streamDeleteBtn}>
                            <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(stream.id)}>Delete</Button>
                          </div>
                        </>
                      )}
                      {stream.class == "CONVERT_TO_TABLE_BY_SPECIFY_HEADERS" && (
                        <>
                          <div className={styles.streamDescription}>Convert to table by specify header:</div>
                          <div className={styles.streamDeleteBtn}>
                            <Button variant="danger" onClick={() => deleteStreamBtnClickHandler(stream.id)}>Delete</Button>
                          </div>
                        </>
                      )}
                      {stream.data && (
                        <div className={styles.streamTableDiv}>
                          <table className={styles.streamTable}>
                            <thead>
                              <tr>
                                {stream.data.header.map((header, headerIndex) => {
                                  return (
                                    <th key={headerIndex}>{header}</th>
                                  )
                                })}
                              </tr>
                            </thead>
                            <tbody>
                              {stream.data.body.map((row, rowIndex) => {
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
                  <StreamSeparator step={stream.step} streamType={stream.type} streamClass={stream.class} onAddStream={(stream) => addStreamHandler(stream)}></StreamSeparator>
                </div>
              )
            }
          })}
        </div>
        <div className={styles.workbenchFooter}>
          <div className={styles.backBtnWrapper}>
            <div className={styles.parsingRulesFooter}>
              <Link href={"/workspace/parsers/" + parserId + "/layouts/" + layoutId + "/rules/" + ruleId + "?editorType=regionSelector&documentId=" + documentId}>
                &lt; Back to Region Selection
              </Link>
            </div>
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