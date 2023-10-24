import { useState, useEffect } from 'react'

import { useRouter } from 'next/router'

import { produce } from 'immer'

import Col from 'react-bootstrap/Col'
import Tabs from 'react-bootstrap/Tabs'
import Tab from 'react-bootstrap/Tab'
import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'
import Card from 'react-bootstrap/Card'
import Button from 'react-bootstrap/Button'
import Modal from 'react-bootstrap/Modal'

import Select from 'react-select'

import WorkspaceLayout from '../../../../../layouts/workspace'

import service from '../../../../../service'

import styles from '../../../../../styles/Splitting.module.css'

const splittingOptions = [
  {
    label: "No Splitting",
    value: "NO_SPLIT"
  },
  {
    label: "Split by Page Number",
    value: "SPLIT_BY_PAGE_NUM"
  },
  {
    label: "Split by Conditions",
    value: "SPLIT_BY_CONDITIONS"
  }
]

const streamOptions = [
    {
        label: "equals",
        value: "equals"
    },
    {
        label: "contains",
        value: "contains"
    },
    {
        label: "is empty",
        value: "isEmpty"
    },
    {
        label: "is not empty",
        value: "isNotEmpty"
    },
    {
        label: "regex match",
        value: "regexMatch"
    },
    {
        label: "changed",
        value: "changed"
    },
    {
        label: "not changed",
        value: "notChanged"
    }
]

const Splitting = () => {

  const router = useRouter()

  const [parser, setParser] = useState(null)

  const [firstPageSplittingModal , setFirstPageSplittingModal] = useState({
    show: false,
    conditions: [],
    layout: null
  })

  const [splitting, setSplitting] = useState([
  ])

  const getParser = () => {
    service.get("parsers/" + parserId, response => {
      setParser(response.data)
    })
  }

  useEffect(() => {
    if (!router.isReady) return
    getParser()
  }, [router.isReady])

  const updateParser = () => {
    service.put("parsers/" + parserId,
      parser,
      response => {
      }
    )
  }

  const addFirstPageSplittingClickHandler = () => {
    setFirstPageSplittingModal(
      produce((draft) => {
        draft.show = true
      })
    )
  }

  const selectOperatorChangeHandler = () => {

  }

  const txtConditionChangeHandler = () => {

  }

  const removeConditionBtnClickHandler = () => {

  }

  const closeFirstPageSplittingModalHandler = () => {
    setFirstPageSplittingModal(
      produce((draft) => {
        draft.show = false
      })
    )
  }

  useEffect(() => {
    if (!router.isReady) return
  }, [router.isReady])

  const { parserId } = router.query

  return (
    <WorkspaceLayout>
      <div className={styles.splittingWrapper}>
        <h1>Splitting</h1>
        <Card style={{ width: '100%', marginBottom: 10 }}>
          <Card.Body>
            <Card style={{ width: '100%', marginBottom: 10 }}>
              <Card.Body>
                <Card.Title>
                  First Page Splitting
                </Card.Title>
                <fieldset>
                  <div className={styles.firstPageSplitting}>
                    <div className={styles.firstPageSplittingConditions}>
                      <div className={styles.firstPageSplittingCondition}>
                        <span className={styles.firstPageSplittingIf}>If</span>
                        <span className={styles.firstPageSplittingRuleName}>Invoice No Detector</span>
                        <span className={styles.firstPageSplittingOperator}>is not empty</span>
                      </div>
                      <span className={styles.firstPageSplittingAnd}>and</span><br/>
                      <div className={styles.firstPageSplittingCondition}>
                        <span className={styles.firstPageSplittingRuleName}>Invoice No Detector</span>
                        <span className={styles.firstPageSplittingOperator}>regex</span>
                        <span className={styles.firstPageSplittingValue}>INV[0-9]{5}</span>
                      </div>
                      <span className={styles.firstPageSplittingThen}>Then</span>
                    </div>
                    <div className={styles.firstPageSplittingRouter}>
                      <span className={styles.firstPageSplittingRouteTo}>route to: </span>
                      <span className={styles.firstPageSplittingParser}>Invoice</span>
                      <span className={styles.firstPageSplittingAsFirstPage}> as <span style={{textDecoration: "underline"}}>first page</span></span>
                    </div>
                    <Card.Title style={{marginTop: "20px"}}>
                      Consecutive Page Splitting
                    </Card.Title>
                    <Card style={{ width: '100%', marginBottom: 10 }}>
                      <Card.Body>
                        <fieldset>
                          <div className={styles.consecutivePageSplitting}>
                            <div className={styles.consecutivePageSplittingConditions}>
                              <div className={styles.consecutivePageSplittingCondition}>
                                <span className={styles.consecutivePageSplittingIf}>If</span>
                                <span className={styles.consecutivePageSplittingRuleName}>Invoice No Detector</span>
                                <span className={styles.consecutivePageSplittingOperator}>does not change</span>
                              </div>
                              <span className={styles.consecutivePageSplittingThen}>Then</span>
                            </div>
                            <div className={styles.consecutivePageSplittingRouter}>
                              <span className={styles.consecutivePageSplittingRouteTo}>route to: </span>
                              <span className={styles.consecutivePageSplittingParser}>Invoice</span>
                              <span className={styles.consecutivePageSplittingAsFirstPage}> as <span style={{textDecoration: "underline"}}>consecutive page</span></span>
                            </div>
                            <div className={styles.consecutivePageSplittingActions}>
                              <Button style={{marginRight: 10}}>&uarr;</Button>
                              <Button>&darr;</Button>
                            </div>
                          </div>
                        </fieldset>
                      </Card.Body>
                    </Card>
                    <Card style={{ width: '100%', marginBottom: 10 }}>
                      <Card.Body>
                        <fieldset>
                          <div className={styles.consecutivePageSplitting}>
                            <div className={styles.consecutivePageSplittingConditions}>
                              <div className={styles.consecutivePageSplittingCondition}>
                                <span className={styles.consecutivePageSplittingIf}>Else If</span>
                                <span className={styles.consecutivePageSplittingRuleName}>Invoice No Detector</span>
                                <span className={styles.consecutivePageSplittingOperator}>is not empty</span>
                              </div>
                              <span className={styles.consecutivePageSplittingThen}>Then</span>
                            </div>
                            <div className={styles.consecutivePageSplittingRouter}>
                              <span className={styles.consecutivePageSplittingRouteTo}>route to: </span>
                              <span className={styles.consecutivePageSplittingParser}>Invoice</span>
                              <span className={styles.consecutivePageSplittingAsFirstPage}> as <span style={{textDecoration: "underline"}}>consecutive page</span></span>
                            </div>
                            <div className={styles.consecutivePageSplittingActions}>
                              <Button style={{marginRight: 10}}>&uarr;</Button>
                              <Button>&darr;</Button>
                            </div>
                          </div>
                        </fieldset>
                      </Card.Body>
                    </Card>
                    <Card style={{ width: '100%', marginBottom: 10 }}>
                      <Card.Body>
                        <fieldset>
                          <div className={styles.consecutivePageSplitting}>
                            <div className={styles.consecutivePageSplittingConditions}>
                              <div className={styles.consecutivePageSplittingCondition}>
                                <span className={styles.consecutivePageSplittingIf}>Else</span>
                              </div>
                            </div>
                            <div className={styles.consecutivePageSplittingRouter}>
                              <span className={styles.consecutivePageSplittingRouteTo}>return to first page checking.</span>
                            </div>
                          </div>
                        </fieldset>
                      </Card.Body>
                    </Card>
                    <div className={styles.firstPageSplittingActions}>
                      <Button style={{marginRight: 10}}>&uarr;</Button>
                      <Button style={{marginRight: 10}}>&darr;</Button>
                      <Button>Add Consecutive Page Splitting</Button>
                    </div>
                  </div>
                </fieldset>
              </Card.Body>
            </Card>
            <Card style={{ width: '100%', marginBottom: 10 }}>
              <Card.Body>
                <Card.Title>
                  First Page Splitting
                </Card.Title>
                <fieldset>
                  <div className={styles.firstPageSplitting}>
                    <div className={styles.firstPageSplittingConditions}>
                      <div className={styles.firstPageSplittingCondition}>
                        <span className={styles.firstPageSplittingIf}>If</span>
                        <span className={styles.firstPageSplittingRuleName}>DN No Detector</span>
                        <span className={styles.firstPageSplittingOperator}>is not empty</span>
                      </div>
                      <span className={styles.firstPageSplittingAnd}>and</span><br/>
                      <div className={styles.firstPageSplittingCondition}>
                        <span className={styles.firstPageSplittingRuleName}>DN No Detector</span>
                        <span className={styles.firstPageSplittingOperator}>regex</span>
                        <span className={styles.firstPageSplittingValue}>DN[0-9]{5}</span>
                      </div>
                      <span className={styles.firstPageSplittingThen}>Then</span>
                    </div>
                    <div className={styles.firstPageSplittingRouter}>
                      <span className={styles.firstPageSplittingRouteTo}>route to: </span>
                      <span className={styles.firstPageSplittingParser}>Delivery Note</span>
                      <span className={styles.firstPageSplittingAsFirstPage}> as <span style={{textDecoration: "underline"}}>first page</span></span>
                    </div>
                    <Card.Title style={{marginTop: "20px"}}>
                      Consecutive Page Splitting
                    </Card.Title>
                    <Card style={{ width: '100%', marginBottom: 10 }}>
                      <Card.Body>
                        <fieldset>
                          <div className={styles.consecutivePageSplitting}>
                            <div className={styles.consecutivePageSplittingConditions}>
                              <div className={styles.consecutivePageSplittingCondition}>
                                <span className={styles.consecutivePageSplittingIf}>If</span>
                                <span className={styles.consecutivePageSplittingRuleName}>DN No Detector</span>
                                <span className={styles.consecutivePageSplittingOperator}>does not change</span>
                              </div>
                              <span className={styles.consecutivePageSplittingThen}>Then</span>
                            </div>
                            <div className={styles.consecutivePageSplittingRouter}>
                              <span className={styles.consecutivePageSplittingRouteTo}>route to: </span>
                              <span className={styles.consecutivePageSplittingParser}>Delivery Note</span>
                              <span className={styles.consecutivePageSplittingAsFirstPage}> as <span style={{textDecoration: "underline"}}>consecutive page</span></span>
                            </div>
                            <div className={styles.consecutivePageSplittingActions}>
                              <Button style={{marginRight: 10}}>&uarr;</Button>
                              <Button>&darr;</Button>
                            </div>
                          </div>
                        </fieldset>
                      </Card.Body>
                    </Card>
                    <Card style={{ width: '100%', marginBottom: 10 }}>
                      <Card.Body>
                        <fieldset>
                          <div className={styles.consecutivePageSplitting}>
                            <div className={styles.consecutivePageSplittingConditions}>
                              <div className={styles.consecutivePageSplittingCondition}>
                                <span className={styles.consecutivePageSplittingIf}>Else If</span>
                                <span className={styles.consecutivePageSplittingRuleName}>DN No Detector</span>
                                <span className={styles.consecutivePageSplittingOperator}>is not empty</span>
                              </div>
                              <span className={styles.consecutivePageSplittingThen}>Then</span>
                            </div>
                            <div className={styles.consecutivePageSplittingRouter}>
                              <span className={styles.consecutivePageSplittingRouteTo}>route to: </span>
                              <span className={styles.consecutivePageSplittingParser}>Delivery Note</span>
                              <span className={styles.consecutivePageSplittingAsFirstPage}> as <span style={{textDecoration: "underline"}}>consecutive page</span></span>
                            </div>
                            <div className={styles.consecutivePageSplittingActions}>
                              <Button style={{marginRight: 10}}>&uarr;</Button>
                              <Button>&darr;</Button>
                            </div>
                          </div>
                        </fieldset>
                      </Card.Body>
                    </Card>
                    <Card style={{ width: '100%', marginBottom: 10 }}>
                      <Card.Body>
                        <fieldset>
                          <div className={styles.consecutivePageSplitting}>
                            <div className={styles.consecutivePageSplittingConditions}>
                              <div className={styles.consecutivePageSplittingCondition}>
                                <span className={styles.consecutivePageSplittingIf}>Else</span>
                              </div>
                            </div>
                            <div className={styles.consecutivePageSplittingRouter}>
                              <span className={styles.consecutivePageSplittingRouteTo}>return to first page checking.</span>
                            </div>
                          </div>
                        </fieldset>
                      </Card.Body>
                    </Card>
                    <div className={styles.firstPageSplittingActions}>
                      <Button style={{marginRight: 10}}>&uarr;</Button>
                      <Button style={{marginRight: 10}}>&darr;</Button>
                      <Button>Add Consecutive Page Splitting</Button>
                    </div>
                  </div>
                </fieldset>
              </Card.Body>
            </Card>
            <Card style={{ width: '100%', marginBottom: 10 }}>
              <Card.Body>
                <fieldset>
                  <div className={styles.firstPageSplitting}>
                    <div className={styles.firstPageSplittingConditions}>
                      <span className={styles.firstPageSplittingIf}>Else</span>
                    </div>
                    <div className={styles.firstPageSplittingRouter}>
                      <span className={styles.firstPageSplittingRouteTo}>route to: </span>
                      <span className={styles.firstPageSplittingParser}>General Document</span>
                    </div>
                  </div>
                </fieldset>
              </Card.Body>
            </Card>
            <Button onClick={addFirstPageSplittingClickHandler}>Add First Page Splitting</Button>
            <Modal className={styles.firstPageSplittingModal}
              show={firstPageSplittingModal.show}
              onHide={closeFirstPageSplittingModalHandler}
            >
              <Modal.Header closeButton>
                <Modal.Title>Add first page splitting</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                <Table striped bordered hover>
                  <thead>
                  <tr>
                      <th>#</th>
                      <th>Column</th>
                      <th>Operator</th>
                      <th>Value</th>
                      <th></th>
                  </tr>
                  </thead>
                  <tbody>
                  {firstPageSplittingModal.conditions.map((condition, conditionIndex) => (
                      <tr key={conditionIndex}>
                      <td>{conditionIndex + 1}</td>
                      <td>
                          <Form.Control value={condition.column} onChange={(e) => txtConditionColumnChangeHandler(conditionIndex, e.target.value)}/>
                      </td>
                      <td>
                          <Select
                              classNamePrefix="react-select"
                              options={streamConditionOperators}
                              value={streamConditionOperators.find(o => o.value == condition.operator)}
                              onChange={(e) => selectOperatorChangeHandler(conditionIndex, e)}
                              menuPlacement="auto"
                              menuPosition="fixed" />
                      </td>
                      <td>
                          <Form.Control value={condition.value} onChange={(e) => txtConditionChangeHandler(conditionIndex, e.target.value)}/>
                      </td>
                      <td>
                          <Button variant="danger" 
                              onClick={() => removeConditionBtnClickHandler(conditionIndex)}
                              style={{ height: 46 }}>
                              Remove
                          </Button>
                      </td>
                      </tr>
                  ))}
                  </tbody>
                </Table>
                <Form.Group>
                  <Button>Add Condition</Button>
                </Form.Group>
                <Form.Group>
                  <Form.Label>Parser</Form.Label>
                  <Select className={styles.parserSelect}></Select>
                </Form.Group>
                <Form.Group>
                  <Button style={{ marginRight: 10 }}>Save</Button>
                  <Button variant="danger">Cancel</Button>
                </Form.Group>
              </Modal.Body>
            </Modal>
          </Card.Body>
        </Card>
      </div>
    </WorkspaceLayout>
  )
}

export default Splitting