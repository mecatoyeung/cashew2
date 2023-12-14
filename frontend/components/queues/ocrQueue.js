import { useState, useCallback, useEffect, useRef } from 'react'
import { useRouter } from 'next/router'


import moment from 'moment'

import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import DropdownButton from 'react-bootstrap/DropdownButton'
import Dropdown from 'react-bootstrap/Dropdown'

import service from "../../service"

import sharedStyles from '../../styles/Queue.module.css'
import styles from '../../styles/SplitQueue.module.css'

const OCRQueue = (props) => {

  const router = useRouter()

  const [parser, setParser] = useState(null)
  const [queues, setQueues] = useState([])
  const [selectedQueueIds, setSelectedQueueIds] = useState([])

  const getParser = () => {
    if (!props.parserId) return
    service.get("parsers/" + props.parserId +"/", response => {
      setParser(response.data)
    })
  }

  const getQueues = () => {
    if (!props.parserId) return
    service.get("queues/?parserId=" + props.parserId + "&queueClass=OCR", response => {
      let queues = response.data
      for (let i = 0; i < queues.length; i++) {
        queues[i].selected = false
      }
      setQueues(response.data)
    })
  }

  const stopOCRClickHandler = async () => {
    for (let i=0; i<selectedQueueIds.length; i++) {
      let queue = queues.find(q => q.id == selectedQueueIds[i])
      queue.queueClass = "OCR"
      queue.queueStatus = "STOPPED"
      await service.put("queues/" + selectedQueueIds[i] + "/", queue)
    }
  }

  const chkQueueChangeHandler = (e, queue) => {
    if (e.target.checked) {
      if (!selectedQueueIds.includes(queue.id)) {
        setSelectedQueueIds([...selectedQueueIds, queue.id])
      }
    } else {
      let updatedSelectedQueueIds = [...selectedQueueIds]
      let index = updatedSelectedQueueIds.indexOf(queue.id);
      if (index !== -1) {
        updatedSelectedQueueIds.splice(index, 1);
      }
      setSelectedQueueIds(updatedSelectedQueueIds)
    }
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
    if (!router.isReady) return
    getParser()
    let queues = props.queues
    for (let i=0; i<queues.length; i++) {
      let queue = queues[i]
      let ocredCount = 0
      for (let j=0; j<queue.document.documentPages.length; j++) {
        let documentPage = queue.document.documentPages[j]
        if (documentPage.ocred) ocredCount++
      } 
      queue.document.description = queue.document.filenameWithoutExtension + "." + queue.document.extension + " (OCRed " + ocredCount + " of " + queue.document.documentPages.length + ")"
    }
    setQueues(queues)
  }, [router.isReady, props.queues])

  return (
    <>
      <div className={sharedStyles.actionsDiv}>
        <DropdownButton
          title="Perform Action"
          className={styles.performActionDropdown}>
          <Dropdown.Item onClick={() => stopOCRClickHandler()}>Stop OCR and Move to Processed Queue</Dropdown.Item>
          <Dropdown.Item href="#">Move to Parse Queue (In Progress)</Dropdown.Item>
          <Dropdown.Item href="#">Move to Integration Queue (In Progress)</Dropdown.Item>
          <Dropdown.Divider />
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
                    <td>{queue.queueStatus}</td>
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

export default OCRQueue