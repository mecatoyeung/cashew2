import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import dynamic from 'next/dynamic'

import { produce } from 'immer'

import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'
import DropdownButton from 'react-bootstrap/DropdownButton'
import Dropdown from 'react-bootstrap/Dropdown'
import Button from 'react-bootstrap/Button'
import { Modal } from 'react-bootstrap'

import moment from 'moment'

import sharedStyles from '../../styles/Queue.module.css'
import styles from '../../styles/ProcessedQueue.module.css'

import service from '../../service'

const CodeEditor = dynamic(
  () => import('@uiw/react-textarea-code-editor').then((mod) => mod.default),
  { ssr: false }
)

import '@uiw/react-textarea-code-editor/dist.css'

const ProcessedQueue = (props) => {
  const router = useRouter()

  const [parser, setParser] = useState(null)
  const [documents, setDocuments] = useState([])
  const [queues, setQueues] = useState([])
  const [selectedQueueIds, setSelectedQueueIds] = useState([])
  const [parsedResultForm, setParsedResultForm] = useState({
    show: false,
    parsedResult: '',
  })

  const getParser = () => {
    if (!props.parserId) return
    service.get('parsers/' + props.parserId + '/', (response) => {
      setParser(response.data)
    })
  }

  const getQueues = () => {
    if (!props.parserId) return
    service.get(
      'queues/?parserId=' + props.parserId + '&queueClass=PROCESSED',
      (response) => {
        let qs = response.data
        setQueues(qs)
      }
    )
  }

  const deleteQueueClickHandler = async () => {
    for (let i = 0; i < selectedQueueIds.length; i++) {
      await service.delete('queues/' + selectedQueueIds[i] + '/')
    }
    getQueues()
    setSelectedQueueIds([])
  }

  const moveToImportQueueClickHandler = async () => {
    for (let i = 0; i < selectedQueueIds.length; i++) {
      let queue = queues.find((q) => q.id == selectedQueueIds[i])
      queue.queueClass = 'IMPORT'
      queue.queueStatus = 'READY'
      await service.put('queues/' + selectedQueueIds[i] + '/', queue)
    }
    getQueues()
    setSelectedQueueIds([])
  }

  const chkQueueChangeHandler = (e, queue) => {
    if (e.target.checked) {
      if (!selectedQueueIds.includes(queue.id)) {
        setSelectedQueueIds([...selectedQueueIds, queue.id])
      }
    } else {
      let updatedSelectedQueueIds = [...selectedQueueIds]
      let index = updatedSelectedQueueIds.indexOf(queue.id)
      if (index !== -1) {
        updatedSelectedQueueIds.splice(index, 1)
      }
      setSelectedQueueIds(updatedSelectedQueueIds)
    }
  }

  const chkAllChangeHandler = (e) => {
    if (e.target.checked) {
      let updatedSelectedQueueIds = []
      for (let i = 0; i < queues.length; i++) {
        updatedSelectedQueueIds.push(queues[i].id)
      }
      setSelectedQueueIds(updatedSelectedQueueIds)
    } else {
      setSelectedQueueIds([])
    }
  }

  const parsedResultCloseHandler = (e) => {
    setParsedResultForm(
      produce((draft) => {
        draft.show = false
      })
    )
  }

  const showParsedResultBtnClickHandler = (queue) => {
    setParsedResultForm(
      produce((draft) => {
        draft.show = true
        draft.parsedResult = JSON.stringify(
          JSON.parse(queue.parsedResult),
          null,
          '\t'
        )
      })
    )
  }

  useEffect(() => {
    if (!router.isReady) return
    getParser()
    setQueues(props.queues)
  }, [router.isReady, props.queues])

  return (
    <>
      <div className={sharedStyles.actionsDiv}>
        <DropdownButton
          title="Perform Action"
          className={styles.performActionDropdown}
        >
          <Dropdown.Item href="#" onClick={moveToImportQueueClickHandler}>
            Move to Import Queue
          </Dropdown.Item>
          <Dropdown.Divider />
          <Dropdown.Item href="#" onClick={deleteQueueClickHandler}>
            Delete Queues and Documents
          </Dropdown.Item>
        </DropdownButton>
        <Form.Control
          className={styles.searchTxt}
          placeholder="Search by filename..."
        />
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
                    style={{ padding: 0 }}
                  />
                </th>
                <th>Document Name</th>
                <th>Document Type</th>
                <th>Queue Status</th>
                <th>Show Parsed Result</th>
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
                          checked={
                            selectedQueueIds.filter((x) => x == queue.id)
                              .length > 0
                          }
                          onChange={(e) => chkQueueChangeHandler(e, queue)}
                          style={{ padding: 0 }}
                        />
                      </td>
                      <td className={styles.tdGrow}>
                        {queue.document.filenameWithoutExtension +
                          '.' +
                          queue.document.extension +
                          ' (' +
                          queue.document.totalPageNum +
                          ' Pages)'}
                      </td>
                      <td>{queue.document.documentType}</td>
                      <td>{queue.queueStatus.replace('_', ' ')}</td>
                      <td>
                        <Button
                          onClick={() => showParsedResultBtnClickHandler(queue)}
                        >
                          Show
                        </Button>
                      </td>
                      <Modal
                        show={parsedResultForm.show}
                        onHide={(e) => parsedResultCloseHandler(e)}
                        size="lg"
                      >
                        <Modal.Header closeButton>
                          <Modal.Title>
                            Parsed Result (
                            {queue.document.filenameWithoutExtension +
                              '.' +
                              queue.document.extension}
                            )
                          </Modal.Title>
                        </Modal.Header>
                        <Modal.Body>
                          {console.log(parsedResultForm)}
                          {parsedResultForm.parsedResult != '' &&
                            parsedResultForm.parsedResult != '{}' && (
                              <CodeEditor
                                value={JSON.parse(
                                  parsedResultForm.parsedResult
                                ).map((pr) => {
                                  console.log(pr)
                                  let vars = {}
                                  if (pr['streamed']['type'] == 'TEXTFIELD') {
                                    vars[pr['rule']['name']] =
                                      pr['streamed']['value']
                                  } else if (
                                    pr['streamed']['type'] == 'TABLE'
                                  ) {
                                    let rows = []
                                    for (
                                      let i = 0;
                                      i <
                                      pr['streamed']['value']['body'].length;
                                      i++
                                    ) {
                                      let row = {}
                                      for (
                                        let j = 0;
                                        j <
                                        pr['streamed']['value']['header']
                                          .length;
                                        j++
                                      ) {
                                        row[
                                          pr['streamed']['value']['header'][j]
                                        ] =
                                          pr['streamed']['value']['body'][i][j]
                                      }
                                      rows.push(row)
                                    }
                                    vars[pr['rule']['name']] = rows
                                  } else if (pr['streamed']['type'] == 'JSON') {
                                    vars[pr['rule']['name']] = JSON.parse(
                                      pr['streamed']['value']
                                    )
                                  }
                                  return JSON.stringify(vars, null, '\t')
                                })}
                                language="json"
                                padding={15}
                                style={{
                                  border: '1px solid #333',
                                }}
                              />
                            )}
                        </Modal.Body>
                        <Modal.Footer>
                          <Button
                            variant="secondary"
                            onClick={(e) => parsedResultCloseHandler(e)}
                          >
                            Close
                          </Button>
                        </Modal.Footer>
                      </Modal>

                      <td className={styles.tdNoWrap}>
                        {moment(queue.document.lastModifiedAt).format(
                          'YYYY-MM-DD hh:mm:ss a'
                        )}
                      </td>
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
