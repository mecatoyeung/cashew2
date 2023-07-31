import { useState, useCallback, useEffect, useRef } from 'react'
import { useRouter } from 'next/router'

import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'
import DropdownButton from 'react-bootstrap/DropdownButton'
import Dropdown from 'react-bootstrap/Dropdown'
import Button from 'react-bootstrap/Button'
import Modal from 'react-bootstrap/Modal'
import ProgressBar from 'react-bootstrap/ProgressBar'
import Toast from 'react-bootstrap/Toast'
import Select from 'react-select'

import { AgGridReact } from 'ag-grid-react'

import { useDropzone } from 'react-dropzone'

import axios from 'axios'

import every from 'lodash/every'

import moment from 'moment'

import camelize from "../../helpers/camelize"

import service from "../../service"

import sharedStyles from '../../styles/Queue.module.css'
import styles from '../../styles/ImportQueue.module.css'
import { LayoutCssClasses } from 'ag-grid-community'

const ImportQueue = (props) => {

  const router = useRouter()

  const [showUploadDocumentsModal, setShowUploadDocumentsModal] = useState(false)
  const closeUploadDocumentsModalHandler = () => setShowUploadDocumentsModal(false);
  const openUploadDocumentsModalHandler = () => setShowUploadDocumentsModal(true);

  const uploadDocumentsBtnClickHandler = () => {
    setDroppedFiles([])
    openUploadDocumentsModalHandler()
  }

  const moveToSplitQueueClickHandler = () => {
    let documentIds = queues
      .filter(d => d.selected == true)
      .map(d => d.document.id)
    service.put("documents/change-queue-class", {
      documents: documentIds,
      queue_class: "SPLIT"
    })
  }

  const moveToParseQueueClickHandler = () => {
    let documentIds = queues
      .filter(d => d.selected == true)
      .map(d => d.document.id)
    service.put("documents/change-queue-class", {
      documents: documentIds,
      queue_class: "PARSING"
    })
  }

  const chkQueueChangeHandler = (index, e) => {
    let updateQueues = [...queues]
    updateQueues[index].selected = e.target.checked
    setQueues(updateQueues)
  }

  const confirmUploadDocumentsBtnClickHandler = async () => {

    for (let i = 0; i < droppedFiles.length; i++) {
      let droppedFile = droppedFiles[i]
      let formData = new FormData();
      formData.set("parserId", props.parserId)
      formData.set("name", droppedFile.name)
      formData.set("inputData", JSON.stringify(inputData))
      formData.append("sourceFile", droppedFile)

      const response = service.post("documents/?parserId=" + props.parserId, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          const progress = (progressEvent.loaded / progressEvent.total) * 100
          let updatedFiles = [...droppedFiles]
          updatedFiles[i].progress = progress
          setDroppedFiles(updatedFiles)
          if (every(updatedFiles, { 'progress': 100 })) {
            getParser()
            closeUploadDocumentsModalHandler()
          }
        }
      }).catch((error) => {
      });
    }
  }

  const [droppedFiles, setDroppedFiles] = useState([])
  const onDrop = useCallback(acceptedFiles => {
    let result = []
    for (let i = 0; i < acceptedFiles.length; i++) {
      if (acceptedFiles[i].progress == undefined) {
        acceptedFiles[i].progress = 0
      }
      result.push(acceptedFiles[i])
    }
    setDroppedFiles(result)
  }, [])
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop })

  const [parser, setParser] = useState(null)
  const [defaultLayout, setDefaultLayout] = useState(null)
  const [documents, setDocuments] = useState([])
  const [queues, setQueues] = useState([])
  const [selectedIds, setSelectedIds] = useState([])
  const [inputData, setInputData] = useState({})

  const getParser = () => {
    if (!props.parserId) return
    service.get("parsers/" + props.parserId, response => {
      setParser(response.data)
    })
  }

  const txtInputChangeHandler = (rule, value) => {
    let updatedInputData = {...inputData}
    updatedInputData[rule.name] = value
    setInputData(updatedInputData)
  }

  const getQueues = () => {
    if (!props.parserId) return
    service.get("queues/?parserId=" + props.parserId + "&queueType=IMPORT", response => {
      let queues = response.data
      setSelectedIds([])
      setQueues(response.data)
    })
  }

  useEffect(() => {
    getParser()
    getQueues()
    const interval = setInterval(() => {
      getQueues()
    }, 5000);
    return () => clearInterval(interval);
  }, [router.isReady])

  return (
    <>
      <div className={sharedStyles.actionsDiv}>
        <DropdownButton
          title="Perform Action"
          className={styles.performActionDropdown}>
          <Dropdown.Item href="#" onClick={uploadDocumentsBtnClickHandler}>Upload PDF File(s)</Dropdown.Item>
          <Dropdown.Divider />
          <Dropdown.Item href="#" onClick={moveToSplitQueueClickHandler}>Move to Split Queue</Dropdown.Item>
          <Dropdown.Item href="#" onClick={moveToParseQueueClickHandler}>Move to Parse Queue</Dropdown.Item>
          <Dropdown.Item href="#">Move to Integration Queue</Dropdown.Item>
          <Dropdown.Divider />
          <Dropdown.Item href="#">Delete Documents</Dropdown.Item>
        </DropdownButton>
        <Form.Control className={styles.searchTxt} placeholder="Search by filename..." />
        <Button variant="secondary">Search</Button>
        <Modal show={showUploadDocumentsModal} onHide={closeUploadDocumentsModalHandler}>
          <Modal.Header closeButton>
            <Modal.Title>Upload Documents</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <ul className={styles.documentUploadUl}>
              {droppedFiles.map((droppedFile, droppedFileIndex) => {
                return (
                  <li className={styles.documentUploadLi} key={droppedFileIndex}>
                    <div>
                      <ProgressBar now={droppedFile.progress} label={`${droppedFile.name} ${droppedFile.progress}%`} />
                    </div>
                  </li>
                )
              })}
            </ul>
            <p>
              {droppedFiles.length} file(s) are found
            </p>
            <div className={styles.dragZone} {...getRootProps()}>
              <input {...getInputProps()} />
              {
                isDragActive ?
                  <p>Drag and drop the PDFs here ...</p> :
                  <p>Drag and drop the PDFs here or click to upload...</p>
              }
            </div>
            {parser && (
              <Form>
                {console.log(parser) || parser.rules.map((rule) => {
                  if (rule.ruleType == "INPUT_TEXTFIELD") {
                    return (
                      <Form.Group className="mb-3" controlId={camelize(rule.name)} key={rule.id}>
                        <Form.Label>{rule.name}</Form.Label>
                        <Form.Control type="text" placeholder="" onChange={e => txtInputChangeHandler(rule, e.target.value)}/>
                      </Form.Group>
                    )
                  } else if (rule.ruleType == "INPUT_DROPDOWN") {
                    return (
                      <Form.Group className="mb-3" controlId={camelize(rule.name)} key={rule.id}>
                        <Form.Label>{rule.name}</Form.Label>
                        <Select
                          options={rule.inputDropdownList.split("\n").map(
                            (o) => {
                              return { value: o, label: o }
                            }
                          )}
                          onChange={(e) => txtInputChangeHandler(rule, e.value)}
                        />
                      </Form.Group>
                    )
                  }
                })}
              </Form>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="primary" onClick={confirmUploadDocumentsBtnClickHandler}>
              Upload Documents
            </Button>
            <Button variant="secondary" onClick={closeUploadDocumentsModalHandler}>
              Close
            </Button>
          </Modal.Footer>
        </Modal>
      </div>
      {queues && queues.length == 0 && (
        <div className={sharedStyles.noDocumentsInQueue}>
          There is no queues in this queue currently.
        </div>
      )}
      {queues && queues.length > 0 && (
        <div className={sharedStyles.queueTableDiv}>
          <Table className={sharedStyles.queueTable} striped bordered hover>
            <thead>
              <tr>
                <th>
                  <Form.Check
                    type="checkbox"
                    label=""
                  />
                </th>
                <th colSpan={2}>

                </th>
              </tr>
            </thead>
            <tbody>
              {queues && queues.map((queue, queueIndex) => {
                return (
                  <tr key={queueIndex}>
                    <td>
                      <Form.Check
                        type="checkbox"
                        label=""
                        checked={queue.selected}
                        onChange={(e) => chkQueueChangeHandler(queueIndex, e)}
                      />
                    </td>
                    <td className={styles.tdGrow}>{queue.document.filename_without_extension + "." + queue.document.extension}</td>
                    <td className={styles.tdNoWrap}>{moment(queue.document.last_modified_at).format('YYYY-MM-DD hh:mm:ss a')}</td>
                  </tr>
                )
              })}
            </tbody>
          </Table>
        </div>
      )}
    </>
  )
}

export default ImportQueue