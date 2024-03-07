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

import { useDropzone } from "react-dropzone"

import ProgressBar from 'react-bootstrap/ProgressBar'

import ParserLayout from '../../../layouts/parser'

import service from '../../../service'

import aichatStyles from "../../../styles/AIChat.module.css"

export default function Parsers() {

  const router = useRouter()

  const [parsers, setParsers] = useState([])

  const [trashConfirmForm, setTrashConfirmForm] = useState({
    show: false,
    isValid: true,
    name: "",
    errorMessage: ""
  })

  const [showUploadConfigModal , setShowUploadConfigModal] = useState({
    show: false,
    uploadDefaultParser: typeof window == 'undefined' ? 0 : parseInt(localStorage.getItem("uploadDefaultParser"))
  })

  const closeUploadConfigModalHandler = () => {
    setShowUploadConfigModal({
      ...showUploadConfigModal,
      show: !showUploadConfigModal.show
    })
  }

  const uploadDefaultParserChangeHandler = (e) => {
    console.log(e)
    setShowUploadConfigModal({
      ...showUploadConfigModal,
      uploadDefaultParser: e.value
    })
  }

  const getParsers = () => {
    service.get("parsers/", (response)=> {
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
    if (trashConfirmForm.name != parsers.find(p => p.id == trashConfirmForm.parserId).name) {
      setTrashConfirmForm(
        produce((draft) => {
          draft.isValid = false
          draft.errorMessage = "Parser name does not match."
        })
      )
      return
    } else {
      setTrashConfirmForm(
        produce((draft) => {
          draft.isValid = true
          draft.errorMessage = ""
        })
      )
    }
    service.delete("parsers/" + trashConfirmForm.parserId + "/", (response) => {
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
            draft.errorMessage = "Delete parser failed. Please consult system administrator."
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
      show: true
    })
  }

  const uploadDocumentsAfterDroppingFiles = async (droppedFiles) => {
    
    for (let i = 0; i < droppedFiles.length; i++) {
      let droppedFile = droppedFiles[i];
      let formData = new FormData();
      let uploadDefaultParser = 0
      if (typeof window !== 'undefined') {
        uploadDefaultParser = localStorage.getItem("uploadDefaultParser")
        formData.set("parser", uploadDefaultParser)
      }
      formData.set("documentType", "AICHAT")
      formData.append("file", droppedFile, droppedFile.name)

      const response = service
        .post(
          "documents/?parserId=" + uploadDefaultParser,
          formData,
          () => {},
          () => {},
          {
            "Content-Type": "multipart/form-data",
          },
          {
            onUploadProgress: (progressEvent) => {
              const progress =
                (progressEvent.loaded / progressEvent.total) * 100;
              let updatedFiles = [...droppedFiles];
              updatedFiles[i].progress = progress;
              setDroppedFiles(updatedFiles);
              if (updatedFiles[i].progress ==  100) {
                updatedFiles[i].uploaded = true
                setDroppedFiles(updatedFiles)
              }
            },
          }
        )
        .catch((error) => {});
    }
  };

  const [droppedFiles, setDroppedFiles] = useState([]);
  const onDrop = useCallback((acceptedFiles) => {

    if (typeof window !== 'undefined') {
      let uploadDefaultParser = localStorage.getItem("uploadDefaultParser")
      if (uploadDefaultParser == null) {
        return
      }
    }

    let result = [];
    for (let i = 0; i < acceptedFiles.length; i++) {
      if (acceptedFiles[i].progress == undefined) {
        acceptedFiles[i].progress = 0;
      }
      result.push(acceptedFiles[i]);
    }
    setDroppedFiles(result)
    uploadDocumentsAfterDroppingFiles(result);
  }, []);
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop })
  let rootProps = getRootProps()
  if (typeof window !== 'undefined') {
    let uploadDefaultParser = localStorage.getItem("uploadDefaultParser")
    if (uploadDefaultParser == null) {
      delete rootProps.onClick
      delete rootProps.onDragEnter
    }
  }

  const confirmUploadConfigBtnClickHandler = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem("uploadDefaultParser", showUploadConfigModal.uploadDefaultParser)
    }
    closeUploadConfigModalHandler()
  }

  useEffect(() => {
    getParsers()
  }, [])

  return (
    <ParserLayout>
      <h1 className={aichatStyles.parsersH1}>Parsers</h1>
      <div className={aichatStyles.uploadBoxWrapper}>
        <div className={aichatStyles.uploadBox}>
          <div className={aichatStyles.dragZone} {...rootProps}>
            <input {...getInputProps()} />
            {isDragActive ? (
              <p>Drag and drop the PDFs here ...</p>
            ) : (
              <p>Drag and drop the PDFs here or click to upload...</p>
            )}
            {!rootProps.onClick && (
              <ToastContainer
                className="p-3"
                position={'bottom-center'}
                style={{ zIndex: 1 }}
              >
                <Toast>
                  <Toast.Body>Please config default parser first...</Toast.Body>
                </Toast>
              </ToastContainer>
            )}
          </div>
          <div className={aichatStyles.progressBarDiv}>
            <ProgressBar
              now={droppedFiles.length == 0 ? 0 : droppedFiles.filter(f => f.uploaded).length / droppedFiles.length}
              label={`Uploading ` + droppedFiles.filter(f => f.uploaded).length + ` of ` + droppedFiles.length}
            />
          </div>
          <div className={aichatStyles.parserSettingActions}>
            <i className="bi bi-gear" 
              onClick={() => defaultUploadConfigClickHandler()}
              style={{ cursor: "pointer"}}></i>
            <Modal
              show={showUploadConfigModal.show}
              onHide={closeUploadConfigModalHandler}
            >
              <Modal.Header closeButton>
                <Modal.Title>Upload Configurations</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                <Form.Group className="mb-3" controlId="uploadDefaultParser">
                  <Form.Label>Default Parser</Form.Label>
                  <Select instanceId="uploadDefaultParserSelectId" 
                  options={parsers.map(p => {
                    return {
                      label: p.name,
                      value: p.id
                    }
                  })} 
                  onChange={uploadDefaultParserChangeHandler}
                  value={{ 
                    value: parsers.find(d => d.id == showUploadConfigModal.uploadDefaultParser)?.id,
                    label: parsers.find(d => d.id == showUploadConfigModal.uploadDefaultParser)?.name
                  }}/>
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
        {parsers && parsers.length > 0 && parsers.map(parser => (
          <li key={parser.id}>
            <div className={aichatStyles.parserName}>
              <span>{parser.name}</span>
            </div>
            <div className={aichatStyles.parserActions}>
              <Button onClick={() => router.push("/workbench/parsers/" + parser.id + "/aichat/")}>AI Chat</Button>
              <Button>Verifier</Button>
            </div>
          </li>
        ))}
        <Modal show={trashConfirmForm.show} onHide={closeTrashHandler} centered>
          <Modal.Header closeButton>
            <Modal.Title>Delete Layout</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form>
              <Form.Group className="mb-3" controlId="layoutNameControlInput">
                <Form.Label>Name</Form.Label>
                <Form.Control type="text"
                  placeholder="e.g. Water Supply"
                  value={trashConfirmForm.name}
                  onChange={trashLayoutNameChangeHandler}/>
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
    </ParserLayout>
  )
}
