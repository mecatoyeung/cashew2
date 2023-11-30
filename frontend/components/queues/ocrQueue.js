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
    /*getQueues()
    const interval = setInterval(() => {
      getQueues()
    }, 5000);*/
  }, [router.isReady, props.queues])

  return (
    <>
      <div className={sharedStyles.actionsDiv}>
        <DropdownButton
          title="Perform Action"
          className={styles.performActionDropdown}>
          <Dropdown.Item href="#">Move to Parse Queue (In Progress)</Dropdown.Item>
          <Dropdown.Item href="#">Move to Integration Queue (In Progress)</Dropdown.Item>
          <Dropdown.Divider />
          <Dropdown.Item href="#">Delete Queues and Documents (In Progress)</Dropdown.Item>
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
              {console.log(queues)}
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
                    <td className={styles.tdGrow}>{queue.document.description}</td>
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