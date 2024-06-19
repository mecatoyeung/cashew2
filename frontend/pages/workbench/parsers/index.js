import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { produce } from 'immer'

import { Form } from 'react-bootstrap'
import { Modal } from 'react-bootstrap'
import { Button } from 'react-bootstrap'

import Select from 'react-select'

import Toast from 'react-bootstrap/Toast'
import ToastContainer from 'react-bootstrap/ToastContainer'

import { useDropzone } from 'react-dropzone'

import ProgressBar from 'react-bootstrap/ProgressBar'

import ParserLayout from '../../../layouts/parser'

import service from '../../../service'

import aichatStyles from '../../../styles/AIChat.module.css'

export default function Parsers() {
  const router = useRouter()

  const [parsers, setParsers] = useState([])

  const [queueStatus, setQueueStatus] = useState(null)

  const [showDefaultParserWarning, setShowDefaultParserWarning] =
    useState(false)

  const [trashConfirmForm, setTrashConfirmForm] = useState({
    show: false,
    isValid: true,
    name: '',
    errorMessage: '',
  })

  const [showUploadConfigModal, setShowUploadConfigModal] = useState({
    show: false,
    uploadDefaultParser:
      typeof window == 'undefined'
        ? 0
        : parseInt(localStorage.getItem('uploadDefaultParser')),
  })

  const closeUploadConfigModalHandler = () => {
    setShowUploadConfigModal({
      ...showUploadConfigModal,
      show: !showUploadConfigModal.show,
    })
  }

  const uploadDefaultParserChangeHandler = (e) => {
    setShowUploadConfigModal({
      ...showUploadConfigModal,
      uploadDefaultParser: e.value,
    })
  }

  const getParsers = () => {
    service.get('parsers/', (response) => {
      setParsers(response.data)
    })
  }

  const trashLayoutNameChangeHandler = (e) => {
    setTrashConfirmForm(
      produce((draft) => {
        draft.name = e.target.value
      })
    )
  }

  const confirmTrashHandler = (parserId) => {
    if (
      trashConfirmForm.name !=
      parsers.find((p) => p.id == trashConfirmForm.parserId).name
    ) {
      setTrashConfirmForm(
        produce((draft) => {
          draft.isValid = false
          draft.errorMessage = 'Parser name does not match.'
        })
      )
      return
    } else {
      setTrashConfirmForm(
        produce((draft) => {
          draft.isValid = true
          draft.errorMessage = ''
        })
      )
    }
    service.delete('parsers/' + trashConfirmForm.parserId + '/', (response) => {
      if (response.status == 204) {
        setTrashConfirmForm(
          produce((draft) => {
            draft.show = false
          })
        )
        getParsers()
      } else {
        setTrashConfirmForm(
          produce((draft) => {
            draft.isValid = false
            draft.errorMessage =
              'Delete parser failed. Please consult system administrator.'
          })
        )
        return
      }
    })
  }

  const closeTrashHandler = () => {
    setTrashConfirmForm(
      produce((draft) => {
        draft.show = false
      })
    )
  }

  const defaultUploadConfigClickHandler = () => {
    setShowUploadConfigModal({
      ...showUploadConfigModal,
      show: true,
    })
  }

  const uploadDocumentsAfterDroppingFiles = async (droppedFiles) => {
    for (let i = 0; i < droppedFiles.length; i++) {
      let droppedFile = droppedFiles[i]
      let formData = new FormData()
      let uploadDefaultParser = 0
      if (typeof window !== 'undefined') {
        uploadDefaultParser = localStorage.getItem('uploadDefaultParser')
        formData.set('parser', uploadDefaultParser)
      }
      formData.set('documentType', 'AICHAT')
      formData.append('file', droppedFile, droppedFile.name)

      const response = service
        .post(
          'documents/?parserId=' + uploadDefaultParser,
          formData,
          () => {},
          () => {},
          {
            'Content-Type': 'multipart/form-data',
          },
          {
            onUploadProgress: (progressEvent) => {
              const progress =
                (progressEvent.loaded / progressEvent.total) * 100
              let updatedFiles = [...droppedFiles]
              updatedFiles[i].progress = progress
              setDroppedFiles(updatedFiles)
              if (updatedFiles[i].progress == 100) {
                updatedFiles[i].uploaded = true
                setDroppedFiles(updatedFiles)
              }
              console.log(updatedFiles)
            },
          }
        )
        .catch((error) => {})
    }
  }

  const [droppedFiles, setDroppedFiles] = useState([])
  const onDrop = useCallback((acceptedFiles) => {
    if (typeof window !== 'undefined') {
      let uploadDefaultParser = localStorage.getItem('uploadDefaultParser')
      if (uploadDefaultParser == null) {
        setShowDefaultParserWarning(true)
        return
      }
    }

    let result = []
    for (let i = 0; i < acceptedFiles.length; i++) {
      if (acceptedFiles[i].progress == undefined) {
        acceptedFiles[i].progress = 0
      }
      result.push(acceptedFiles[i])
    }
    setDroppedFiles(result)
    uploadDocumentsAfterDroppingFiles(result)
  }, [])
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop })
  let rootProps = getRootProps()

  const confirmUploadConfigBtnClickHandler = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(
        'uploadDefaultParser',
        showUploadConfigModal.uploadDefaultParser
      )
      setShowDefaultParserWarning(false)
    }
    closeUploadConfigModalHandler()
  }

  const getQueueStatus = () => {
    service.get('queues/status', (response) => {
      let queueStatus = []
      for (let i = 0; i < parsers.length; i++) {
        queueStatus.push({
          parserId: parsers[i].id,
          queueClass: 'IMPORT',
          count: 0,
        })

        queueStatus.push({
          parserId: parsers[i].id,
          queueClass: 'PRE_PROCESSING',
          count: 0,
        })

        queueStatus.push({
          parserId: parsers[i].id,
          queueClass: 'OCR',
          count: 0,
        })

        queueStatus.push({
          parserId: parsers[i].id,
          queueClass: 'SPLITTING',
          count: 0,
        })

        queueStatus.push({
          parserId: parsers[i].id,
          queueClass: 'PROCESSED',
          count: 0,
        })
      }
      for (let i = 0; i < response.data.length; i++) {
        let singleQueueStatus = queueStatus.find(
          (o) =>
            response.data[i].parser_Id == o.parserId &&
            response.data[i].queueClass == o.queueClass
        )
        if (singleQueueStatus !== undefined) {
          singleQueueStatus.count = response.data[i].count
        }
      }
      console.log(queueStatus)
      setQueueStatus(queueStatus)
    })
  }

  useEffect(() => {
    getQueueStatus()
    const interval = setInterval(() => {
      getQueueStatus()
    }, 1000)
    return () => {
      clearTimeout(interval)
    }
  }, [parsers])

  useEffect(() => {
    getParsers()
  }, [])

  return (
    <ParserLayout>
      {parsers && (
        <>
          <h1 className={aichatStyles.parsersH1}>Parsers</h1>
          {showDefaultParserWarning && (
            <div style={{ position: 'relative' }}>
              <ToastContainer
                className="p-3"
                position={'top-center'}
                style={{ zIndex: 1 }}
              >
                <Toast>
                  <Toast.Body>Please config default parser first...</Toast.Body>
                </Toast>
              </ToastContainer>
            </div>
          )}
          <div className={aichatStyles.uploadBoxWrapper} {...rootProps}>
            <div className={aichatStyles.uploadBox}>
              <div className={aichatStyles.dragZone}>
                <input {...getInputProps()} />
                {isDragActive ? (
                  <p>Drag and drop the PDF/JPG/PNG/TIFF(s) here ...</p>
                ) : (
                  <p>
                    Drag and drop the PDF/JPG/PNG/TIFF(s) here or click to
                    upload...
                  </p>
                )}
              </div>
              <div className={aichatStyles.progressBarDiv}>
                <ProgressBar
                  now={
                    droppedFiles.length == 0
                      ? 0
                      : (droppedFiles.filter((f) => f.uploaded).length /
                          droppedFiles.length) *
                        100
                  }
                  label={
                    `Uploading ` +
                    droppedFiles.filter((f) => f.uploaded).length +
                    ` of ` +
                    droppedFiles.length
                  }
                />
              </div>
              <div className={aichatStyles.parserSettingActions}>
                <i
                  className="bi bi-gear"
                  onClick={() => defaultUploadConfigClickHandler()}
                  style={{ cursor: 'pointer' }}
                ></i>
                <Modal
                  show={showUploadConfigModal.show}
                  onHide={closeUploadConfigModalHandler}
                >
                  <Modal.Header closeButton>
                    <Modal.Title>Upload Configurations</Modal.Title>
                  </Modal.Header>
                  <Modal.Body>
                    <Form.Group
                      className="mb-3"
                      controlId="uploadDefaultParser"
                    >
                      <Form.Label>Default Parser</Form.Label>
                      <Select
                        instanceId="uploadDefaultParserSelectId"
                        options={parsers.map((p) => {
                          return {
                            label: p.name,
                            value: p.id,
                          }
                        })}
                        onChange={uploadDefaultParserChangeHandler}
                        value={{
                          value: parsers.find(
                            (d) =>
                              d.id == showUploadConfigModal.uploadDefaultParser
                          )?.id,
                          label: parsers.find(
                            (d) =>
                              d.id == showUploadConfigModal.uploadDefaultParser
                          )?.name,
                        }}
                      />
                    </Form.Group>
                  </Modal.Body>
                  <Modal.Footer>
                    <Button
                      variant="primary"
                      onClick={confirmUploadConfigBtnClickHandler}
                    >
                      Save
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={closeUploadConfigModalHandler}
                    >
                      Close
                    </Button>
                  </Modal.Footer>
                </Modal>
              </div>
            </div>
          </div>
          <ul className={aichatStyles.parsersUl}>
            {console.log(parsers)}
            {console.log(queueStatus)}
            {parsers &&
              parsers.length > 0 &&
              queueStatus &&
              queueStatus.length > 0 &&
              parsers.map((parser) => (
                <>
                  {parser && queueStatus && (
                    <ParserView parser={parser} queueStatus={queueStatus} />
                  )}
                </>
              ))}
            <Modal
              show={trashConfirmForm.show}
              onHide={closeTrashHandler}
              centered
            >
              <Modal.Header closeButton>
                <Modal.Title>Delete Layout</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                <Form>
                  <Form.Group
                    className="mb-3"
                    controlId="layoutNameControlInput"
                  >
                    <Form.Label>Name</Form.Label>
                    <Form.Control
                      type="text"
                      placeholder="e.g. Water Supply"
                      value={trashConfirmForm.name}
                      onChange={trashLayoutNameChangeHandler}
                    />
                  </Form.Group>
                </Form>
                {!trashConfirmForm.isValid && (
                  <div className="formErrorMessage">
                    {trashConfirmForm.errorMessage}
                  </div>
                )}
              </Modal.Body>
              <Modal.Footer>
                <Button variant="secondary" onClick={closeTrashHandler}>
                  Close
                </Button>
                <Button variant="danger" onClick={() => confirmTrashHandler()}>
                  Delete
                </Button>
              </Modal.Footer>
            </Modal>
          </ul>
        </>
      )}
    </ParserLayout>
  )
}

const ParserView = (props) => {
  const router = useRouter()

  let queueStatusRecs = props.queueStatus.filter(
    (qs) => qs.parserId == props.parser.id
  )
  let importQueueStatusRec = queueStatusRecs.find(
    (qs) => qs.queueClass == 'IMPORT'
  )
  let preProcessingQueueStatusRec = queueStatusRecs.find(
    (qs) => qs.queueClass == 'PRE_PROCESSING'
  )
  let ocrQueueStatusRec = queueStatusRecs.find((qs) => qs.queueClass == 'OCR')
  let splittingQueueStatusRec = queueStatusRecs.find(
    (qs) => qs.queueClass == 'SPLITTING'
  )
  let processedQueueStatusRec = queueStatusRecs.find(
    (qs) => qs.queueClass == 'PROCESSED'
  )

  return (
    <li key={props.parser.id}>
      <div className={aichatStyles.parserWrapper}>
        <div className={aichatStyles.parserName}>
          <span>{props.parser.name}</span>
        </div>
        <div className={aichatStyles.progressBarDiv}>
          <ProgressBar
            now={
              importQueueStatusRec.count +
                preProcessingQueueStatusRec.count +
                ocrQueueStatusRec.count +
                splittingQueueStatusRec.count +
                processedQueueStatusRec.count ==
              0
                ? 100
                : (processedQueueStatusRec.count /
                    (importQueueStatusRec.count +
                      preProcessingQueueStatusRec.count +
                      ocrQueueStatusRec.count +
                      splittingQueueStatusRec.count +
                      processedQueueStatusRec.count)) *
                  100
            }
            label={
              `Processed ` +
              processedQueueStatusRec.count +
              ` of ` +
              (importQueueStatusRec.count +
                preProcessingQueueStatusRec.count +
                ocrQueueStatusRec.count +
                splittingQueueStatusRec.count +
                processedQueueStatusRec.count)
            }
          />
        </div>
      </div>
      <div className={aichatStyles.parserActions}>
        <Button
          onClick={() =>
            router.push('/workbench/parsers/' + props.parser.id + '/aichat/')
          }
        >
          AI Chat
        </Button>
      </div>
    </li>
  )
}
