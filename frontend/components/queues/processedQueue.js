import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'
import DropdownButton from 'react-bootstrap/DropdownButton'
import Dropdown from 'react-bootstrap/Dropdown'
import Button from 'react-bootstrap/Button'

import moment from 'moment'

import sharedStyles from '../../styles/Queue.module.css'
import styles from '../../styles/ProcessedQueue.module.css'

import service from '../../service'

const ProcessedQueue = (props) => {

  const router = useRouter()

  const [parser, setParser] = useState(null)
  const [documents, setDocuments] = useState([])
  const [queues, setQueues] = useState([])
  const [selectedQueueIds, setSelectedQueueIds] = useState([])

  const getParser = () => {
    if (!props.parserId) return
    service.get("parsers/" + props.parserId, response => {
      setParser(response.data)
    })
  }

  const getQueues = () => {
    if (!props.parserId) return
    service.get("queues/?parserId=" + props.parserId + "&queueType=PROCESSED", response => {
      let qs = response.data
      console.log(qs)
      setQueues(qs)
    })
  }

  const moveToSplitQueueClickHandler = () => {
    let documentIds = queues
      .filter(q => q.selected == true)
      .map(d => d.document.id)
    service.put("documents/change-queue-class", {
      documents: documentIds,
      queueClass: "SPLIT"
    })
  }

  const moveToParseQueueClickHandler = () => {
    let documentIds = queues
      .filter(q => q.selected == true)
      .map(d => d.document.id)
    service.put("documents/change-queue-class", {
      documents: documentIds,
      queueClass: "PARSING"
    })
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
    getQueues()
    const interval = setInterval(() => {
      getQueues()
    }, 5000);
    return () => clearInterval(interval);
  }, [router.isReady])

  return (
    <>
      <div className={sharedStyles.actionsDiv}>
        <DropdownButton title="Perform Action" className={styles.performActionDropdown}>
          <Dropdown.Item href="#">Download Excel File</Dropdown.Item>
          <Dropdown.Divider />
          <Dropdown.Item href="#" onClick={moveToSplitQueueClickHandler}>Move to Split Queue</Dropdown.Item>
          <Dropdown.Item href="#" onClick={moveToParseQueueClickHandler}>Move to Parse Queue</Dropdown.Item>
          <Dropdown.Item href="#">Move to Integration Queue</Dropdown.Item>
          <Dropdown.Divider />
          <Dropdown.Item href="#">Delete Documents</Dropdown.Item>
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
                      checked={selectedQueueIds.filter(x => x == queue.id).length > 0}
                      onChange={(e) => chkQueueChangeHandler(e, queue)}
                    />
                  </td>
                  <td className={styles.tdGrow}>{queue.document.filenameWithoutExtension + "." + queue.document.extension}</td>
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

export default ProcessedQueue