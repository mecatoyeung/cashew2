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
import styles from '../../styles/ParsingQueue.module.css'
import { LayoutCssClasses } from 'ag-grid-community'

const ParsingQueue = (props) => {

  const router = useRouter()

  const [parser, setParser] = useState(null)
  const [queues, setQueues] = useState([])
  const [selectedQueueIds, setSelectedQueueIds] = useState([])

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

  const getParser = () => {
    if (!props.parserId) return
    service.get("parsers/" + props.parserId +"/", response => {
      setParser(response.data)
    })
  }

  const stopParsingClickHandler = async () => {
    for (let i=0; i<selectedQueueIds.length; i++) {
      let queue = queues.find(q => q.id == selectedQueueIds[i])
      queue.queueClass = "PARSING"
      queue.queueStatus = "STOPPED"
      await service.put("queues/" + selectedQueueIds[i] + "/", queue)
    }
  }

  useEffect(() => {
    getParser()
    setQueues(props.queues)
  }, [router.isReady, props.queues])

  return (
    <>
      <div className={sharedStyles.actionsDiv}>
        <DropdownButton
          title="Perform Action"
          className={styles.performActionDropdown}>
          <Dropdown.Item onClick={() => stopParsingClickHandler()}>Stop Parsing and Move to Processed Queue</Dropdown.Item>
          {/*<Dropdown.Item href="#" onClick={moveToSplitQueueClickHandler}>Move to Split Queue (In Progress)</Dropdown.Item>
          <Dropdown.Item href="#" onClick={moveToParseQueueClickHandler}>Move to Parse Queue (In Progress)</Dropdown.Item>
          <Dropdown.Item href="#">Move to Integration Queue (In Progress)</Dropdown.Item>
          <Dropdown.Divider />
  <Dropdown.Item href="#">Delete Queues and Documents (In Progress)</Dropdown.Item>*/}
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
                        checked={queue.selected}
                        onChange={(e) => chkQueueChangeHandler(e, queue)}
                        style={{padding: 0}}
                      />
                    </td>
                    <td className={styles.tdGrow}>{queue.document.filenameWithoutExtension + "." + queue.document.extension}</td>
                    <td>{queue.document.documentType}</td>
                    <td>{queue.queueStatus.replace("_", " ")}</td>
                    <td className={styles.tdNoWrap}>{moment(queue.document.lastModifiedAt).format('YYYY-MM-DD hh:mm:ss a')}</td>
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

export default ParsingQueue