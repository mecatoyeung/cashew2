import { useState, useCallback, useEffect, useRef } from "react";
import { useRouter } from "next/router";

import Table from "react-bootstrap/Table";
import Form from "react-bootstrap/Form";
import DropdownButton from "react-bootstrap/DropdownButton";
import Dropdown from "react-bootstrap/Dropdown";
import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";
import ProgressBar from "react-bootstrap/ProgressBar";
import Toast from "react-bootstrap/Toast";
import Select from "react-select";

import { AgGridReact } from "ag-grid-react";

import { useDropzone } from "react-dropzone";

import axios from "axios";

import every from "lodash/every";

import moment from "moment";

import camelize from "../../helpers/camelize";

import service from "../../service";

import sharedStyles from "../../styles/Queue.module.css";
import styles from "../../styles/ImportQueue.module.css";
import { LayoutCssClasses } from "ag-grid-community";

const documentTypes = [
  {
    label: "Template",
    value: "TEMPLATE"
  },
  {
    label: "Import",
    value: "IMPORT"
  }
]

const ImportQueue = (props) => {
  const router = useRouter();

  const [showUploadDocumentsModal, setShowUploadDocumentsModal] =
    useState(false);
  const closeUploadDocumentsModalHandler = () =>
    setShowUploadDocumentsModal(false);
  const openUploadDocumentsModalHandler = () =>
    setShowUploadDocumentsModal(true);

  const uploadDocumentsBtnClickHandler = () => {
    setDroppedFiles([]);
    openUploadDocumentsModalHandler();
  };

  const moveToSplitQueueClickHandler = () => {
    let documentIds = queues
      .filter((d) => d.selected == true)
      .map((d) => d.document.id);
    service.put("documents/change-queue-class/", {
      documents: documentIds,
      queueClass: "SPLIT",
      queueStatus: "READY"
    });
  };

  const moveToParseQueueClickHandler = () => {
    let documentIds = queues
      .filter((d) => d.selected == true)
      .map((d) => d.document.id);
    service.put("documents/change-queue-class/", {
      documents: documentIds,
      queue_class: "PARSING",
      queue_status: "READY"
    })
  }

  const chkQueueChangeHandler = (index, e) => {
    let updateQueues = [...props.queues];
    updateQueues[index].selected = e.target.checked;
    setQueues(updateQueues);
  }

  const convertBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const fileReader = new FileReader();
      fileReader.readAsDataURL(file)
      fileReader.onload = () => {
        resolve(fileReader.result);
      }
      fileReader.onerror = (error) => {
        reject(error);
      }
    })
  }

  const confirmUploadDocumentsBtnClickHandler = async () => {
    let errorMessages = []
    for (let i = 0; i < droppedFiles.length; i++) {
      let droppedFile = droppedFiles[i];
      console.log(droppedFile)
      let fileExtension = droppedFile.path.split('.').pop();
      if (fileExtension !== "pdf" && fileExtension !== "PDF" &&
          fileExtension !== "jpg" && fileExtension !== "JPG" &&
          fileExtension !== "png" && fileExtension !== "PNG" &&
          fileExtension !== "tiff" && fileExtension !== "TIFF") {
        errorMessages.push("File type of filename(" + droppedFile.name + ") is not supported.\n")
        continue
      }
      let formData = new FormData();
      formData.set("parser", props.parserId)
      formData.set("documentType", documentType)
      formData.append("file", droppedFile, droppedFile.name)

      const response = service
        .post(
          "documents/?parserId=" + props.parserId,
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
              console.log("progress", progress);
              let updatedFiles = [...droppedFiles];
              updatedFiles[i].progress = progress;
              setDroppedFiles(updatedFiles);
              if (every(updatedFiles, { progress: 100 })) {
                getParser();
                closeUploadDocumentsModalHandler();
              }
            },
          }
        )
        .catch((error) => {});
    }
    setUploadErrorMessages(errorMessages)
  };

  const [uploadErrorMessages, setUploadErrorMessages] = useState("")
  const [droppedFiles, setDroppedFiles] = useState([]);
  const onDrop = useCallback((acceptedFiles) => {
    let result = [];
    for (let i = 0; i < acceptedFiles.length; i++) {
      if (acceptedFiles[i].progress == undefined) {
        acceptedFiles[i].progress = 0;
      }
      result.push(acceptedFiles[i]);
    }
    setDroppedFiles(result);
  }, []);
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop })

  const [parser, setParser] = useState(null)
  const [defaultLayout, setDefaultLayout] = useState(null)
  const [documents, setDocuments] = useState([])
  const [queues, setQueues] = useState([])
  const [selectedIds, setSelectedIds] = useState([])
  const [inputData, setInputData] = useState({})
  const [documentType, setDocumentType] = useState("IMPORT")

  const getParser = () => {
    if (!props.parserId) return;
    service.get("parsers/" + props.parserId + "/", (response) => {
      setParser(response.data)
    })
  }

  const txtInputChangeHandler = (rule, value) => {
    let updatedInputData = { ...inputData }
    updatedInputData[rule.name] = value
    setInputData(updatedInputData)
  }

  const documentTypeChangeHandler = (e) => {
    setDocumentType(e.value)
  }

  const getQueues = () => {
    if (!props.parserId) return;
    service.get(
      "queues/?parserId=" + props.parserId + "&queueClass=IMPORT",
      (response) => {
        let queues = response.data;
        setSelectedIds([]);
        setQueues(response.data);
      }
    );
  };

  useEffect(() => {
    getParser();
    setQueues(props.queues)
    /*getQueues();
    const interval = setInterval(() => {
      getQueues();
    }, 5000);
    return () => clearInterval(interval);*/
  }, [router.isReady, props.queues]);

  return (
    <>
      <div className={sharedStyles.actionsDiv}>
        <DropdownButton
          title="Perform Action"
          className={styles.performActionDropdown}
        >
          <Dropdown.Item href="#" onClick={uploadDocumentsBtnClickHandler}>
            Upload PDF File(s)
          </Dropdown.Item>
          <Dropdown.Divider />
          <Dropdown.Item href="#" onClick={moveToSplitQueueClickHandler}>
            Move to Split Queue (In Progress)
          </Dropdown.Item>
          <Dropdown.Item href="#" onClick={moveToParseQueueClickHandler}>
            Move to Parse Queue (In Progress)
          </Dropdown.Item>
          <Dropdown.Item href="#">Move to Integration Queue (In Progress)</Dropdown.Item>
          <Dropdown.Divider />
          <Dropdown.Item href="#">Delete Queues and Documents (In Progress)</Dropdown.Item>
        </DropdownButton>
        <Form.Control
          className={styles.searchTxt}
          placeholder="Search by filename..."
        />
        <Button variant="secondary">Search</Button>
        <Modal
          show={showUploadDocumentsModal}
          onHide={closeUploadDocumentsModalHandler}
        >
          <Modal.Header closeButton>
            <Modal.Title>Upload Documents</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Select instanceId="documentTypeSelectId" 
            options={documentTypes} 
            onChange={documentTypeChangeHandler}
            value={documentTypes.find(d => d.value == documentType)}/>
            <ul className={styles.documentUploadUl}>
              {droppedFiles.map((droppedFile, droppedFileIndex) => {
                return (
                  <li
                    className={styles.documentUploadLi}
                    key={droppedFileIndex}
                  >
                    <div>
                      <ProgressBar
                        now={droppedFile.length == 0 ? 0 : droppedFile.progress}
                        label={`${droppedFile.name} ${droppedFile.progress}%`}
                      />
                    </div>
                  </li>
                );
              })}
            </ul>
            <p>{droppedFiles.length} file(s) are found</p>
            {uploadErrorMessages && uploadErrorMessages.length > 0 && uploadErrorMessages.map((uploadErrorMessage, uploadErrorMessageIndex) => {
              return (
                <p key={uploadErrorMessageIndex} style={{ color: "red" }}>{uploadErrorMessage}</p>
              )
            })}
            <div className={styles.dragZone} {...getRootProps()}>
              <input {...getInputProps()} />
              {isDragActive ? (
                <p>Drag and drop the PDF/JPG/PNG/TIFF(s) here ...</p>
              ) : (
                <p>Drag and drop the PDF/JPG/PNG/TIFF(s) here or click to upload...</p>
              )}
            </div>
            {parser && (
              <Form>
                {parser.rules.map((rule) => {
                  if (rule.ruleType == "INPUT_TEXTFIELD") {
                    return (
                      <Form.Group
                        className="mb-3"
                        controlId={camelize(rule.name)}
                        key={rule.id}
                      >
                        <Form.Label>{rule.name}</Form.Label>
                        <Form.Control
                          type="text"
                          placeholder=""
                          onChange={(e) =>
                            txtInputChangeHandler(rule, e.target.value)
                          }
                        />
                      </Form.Group>
                    );
                  } else if (rule.ruleType == "INPUT_DROPDOWN") {
                    return (
                      <Form.Group
                        className="mb-3"
                        controlId={camelize(rule.name)}
                        key={rule.id}
                      >
                        <Form.Label>{rule.name}</Form.Label>
                        <Select
                          options={rule.inputDropdownList
                            .split("\n")
                            .map((o) => {
                              return { value: o, label: o };
                            })}
                          onChange={(e) =>
                            txtInputChangeHandler(rule, e.value)
                          }
                        />
                      </Form.Group>
                    );
                  }
                })}
              </Form>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button
              variant="primary"
              onClick={confirmUploadDocumentsBtnClickHandler}
            >
              Upload Documents
            </Button>
            <Button
              variant="secondary"
              onClick={closeUploadDocumentsModalHandler}
            >
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
                  <Form.Check type="checkbox" label="" style={{padding: 0}}/>
                </th>
                <th>Document Name</th>
                <th>Document Type</th>
                <th>Queue Status</th>
                <th>Last Modified At</th>
              </tr>
            </thead>
            <tbody>
              {queues &&
                queues.map((queue, queueIndex) => {
                  return (
                    <tr key={queueIndex}>
                      <td>
                        <Form.Check
                          type="checkbox"
                          label=""
                          checked={queue.selected}
                          onChange={(e) => chkQueueChangeHandler(queueIndex, e)}
                          style={{padding: 0}}
                        />
                      </td>
                      <td className={styles.tdGrow}>
                        {queue.document.filenameWithoutExtension +
                          "." +
                          queue.document.extension}
                      </td>
                      <td>{queue.document.documentType}</td>
                      <td>{queue.queueStatus.replace("_", " ")}</td>
                      <td className={styles.tdNoWrap}>
                        {moment(queue.document.lastModifiedAt).format(
                          "YYYY-MM-DD hh:mm:ss a"
                        )}
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </Table>
        </div>
      )}
    </>
  );
};

export default ImportQueue;
