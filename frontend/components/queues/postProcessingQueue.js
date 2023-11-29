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

const PostProcessingQueue = (props) => {

  const router = useRouter()

  const [parser, setParser] = useState(null)
  const [queues, setQueues] = useState([])
  const [selectedIds, setSelectedIds] = useState([])

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
    service.put("documents/change-queue-class/", {
      documents: documentIds,
      queue_class: "SPLIT"
    })
  }

  const moveToParseQueueClickHandler = () => {
    let documentIds = queues
      .filter(d => d.selected == true)
      .map(d => d.document.id)
    service.put("documents/change-queue-class/", {
      documents: documentIds,
      queue_class: "PARSING"
    })
  }

  const chkQueueChangeHandler = (index, e) => {
    let updateQueues = [...queues]
    updateQueues[index].selected = e.target.checked
    setQueues(updateQueues)
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
    service.get("queues/?parserId=" + props.parserId + "&queueClass=POST_PROCESSING", response => {
      let queues = response.data
      setSelectedIds([])
      setQueues(response.data)
    })
  }

  useEffect(() => {
    getParser()
    setQueues(props.queues)
    /*getQueues()
    const interval = setInterval(() => {
      getQueues()
    }, 5000);
    return () => clearInterval(interval);*/
  }, [router.isReady, props.queues])

  return (
    <>
      <div className={sharedStyles.actionsDiv}>
        <DropdownButton
          title="Perform Action"
          className={styles.performActionDropdown}>
          <Dropdown.Item href="#" onClick={moveToSplitQueueClickHandler}>Move to Split Queue (In Progress)</Dropdown.Item>
          <Dropdown.Item href="#" onClick={moveToParseQueueClickHandler}>Move to Parse Queue (In Progress)</Dropdown.Item>
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
                    style={{padding: 0}}
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
                        style={{padding: 0}}
                      />
                    </td>
                    <td className={styles.tdGrow}>{queue.document.filenameWithoutExtension + "." + queue.document.extension}</td>
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

export default PostProcessingQueue