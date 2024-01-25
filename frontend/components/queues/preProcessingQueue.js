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

import service from "../../service"

import sharedStyles from '../../styles/Queue.module.css'
import styles from '../../styles/ParsingQueue.module.css'
import { LayoutCssClasses } from 'ag-grid-community'

const PreProcessingQueue = (props) => {

  const router = useRouter()

  const [parser, setParser] = useState(null)
  const [queues, setQueues] = useState([])
  const [selectedQueueIds, setSelectedQueueIds] = useState([])

  const [showUploadDocumentsModal, setShowUploadDocumentsModal] = useState(false)
  const closeUploadDocumentsModalHandler = () => setShowUploadDocumentsModal(false);
  const openUploadDocumentsModalHandler = () => setShowUploadDocumentsModal(true);

  const uploadDocumentsBtnClickHandler = () => {
    setDroppedFiles([])
    openUploadDocumentsModalHandler()
  }

  const getParser = () => {
    if (!props.parserId) return
    service.get("parsers/" + props.parserId + "/", response => {
      setParser(response.data)
    })
  }

  const txtInputChangeHandler = (rule, value) => {
    let updatedInputData = {...inputData}
    updatedInputData[rule.name] = value
    console.log(updatedInputData)
    setInputData(updatedInputData)
  }

  const getQueues = () => {
    if (!props.parserId) return
    service.get("(queues/?parserId=" + props.parserId + "&queueClass=PRE_PROCESSING", response => {
      console.log(response.data)
      setSelectedIds([])
      setQueues(response.data)
    })
  }

  const stopPrePocessessingClickHandler = async () => {
    for (let i=0; i<selectedQueueIds.length; i++) {
      let queue = queues.find(q => q.id == selectedQueueIds[i])
      queue.queueClass = "PRE_PROCESSING"
      queue.queueStatus = "STOPPED"
      await service.put("queues/" + selectedQueueIds[i] + "/", queue)
    }
  }

  const chkQueueChangeHandler = (e, queue) => {
    let updatedSelectedQueueIds = []
    if (e.target.checked) {
      if (!selectedQueueIds.includes(queue.id)) {
        updatedSelectedQueueIds = [...selectedQueueIds, queue.id]
      }
    } else {
      let updatedSelectedQueueIds = [...selectedQueueIds]
      let index = updatedSelectedQueueIds.indexOf(queue.id);
      if (index !== -1) {
        updatedSelectedQueueIds.splice(index, 1);
      }
    }
    let filteredSelectedQueueIds = []
    for (let i=0; i<updatedSelectedQueueIds.length; i++) {
      if (queues.filter(q => q.id == updatedSelectedQueueIds[i]).length > 0) {
        filteredSelectedQueueIds.push(updatedSelectedQueueIds[i])
      }
    }
    setSelectedQueueIds(filteredSelectedQueueIds)
  }

  const chkAllChangeHandler = (e) => {
    if (e.target.checked) {
      let updatedSelectedQueueIds = []
      for (let i=0; i<queues.length; i++) {
        updatedSelectedQueueIds.push(queues[i].id)
      }
      setSelectedQueueIds(updatedSelectedQueueIds)
    } else {
      setSelectedQueueIds([])
    }
  }

  useEffect(() => {
    getParser()
    let queues = props.queues
    queues = queues.filter(q => q.queueStatus != "STOPPED")
    for (let i=0; i<queues.length; i++) {
      let queue = queues[i]
      let preprocessedCount = 0
      for (let j=0; j<queue.document.documentPages.length; j++) {
        let documentPage = queue.document.documentPages[j]
        if (documentPage.preprocessed) preprocessedCount++
      } 
      queue.document.description = queue.document.filenameWithoutExtension + "." + queue.document.extension + " (Pre-processed " + preprocessedCount + " of " + queue.document.documentPages.length + ")"
    }
    setQueues(queues)
  }, [router.isReady, props.queues])

  return (
    <>
      <div className={sharedStyles.actionsDiv}>
        <DropdownButton
          title="Perform Action"
          className={styles.performActionDropdown}>
          <Dropdown.Item onClick={() => stopPrePocessessingClickHandler()}>Stop Pre-Processing and Move to Processed Queue</Dropdown.Item>
          <Dropdown.Item href="#">Move to Integration Queue (In Progress)</Dropdown.Item>
          <Dropdown.Divider />
          <Dropdown.Item href="#">Delete Queues Documents (In Progress)</Dropdown.Item>
        </DropdownButton>
        <Form.Control className={styles.searchTxt} placeholder="Search by filename..." />
        <Button variant="secondary">Search</Button>
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
                    onChange={chkAllChangeHandler}
                    style={{padding: 0}}
                  />
                </th>
                <th>Document Name</th>
                <th>Document Type</th>
                <th>Queue Status</th>
                <th>Last Modified At</th>
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
                        checked={selectedQueueIds.filter(x => x == queue.id).length > 0}
                        onChange={(e) => chkQueueChangeHandler(e, queue)}
                        style={{padding: 0}}
                      />
                    </td>
                    <td className={styles.tdGrow}>{queue.document.description}</td>
                    <td>{queue.document.documentType}</td>
                    <td>{queue.queueStatus.replace("_", " ")}</td>
                    <td className={styles.tdNoWrap}>{moment(queue.document.lastModified_at).format('YYYY-MM-DD hh:mm:ss a')}</td>
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

export default PreProcessingQueue