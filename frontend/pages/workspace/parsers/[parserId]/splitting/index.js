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

const conditionOperators = [
  {
    label: "equals",
    value: "EQUALS"
  },
  {
      label: "regex",
      value: "REGEX"
  },
  {
      label: "contains",
      value: "CONTAINS"
  },
  {
    label: "is empty",
    value: "IS_EMPTY"
  },
  {
    label: "is not empty",
    value: "IS_NOT_EMPTY"
  },
  {
    label: "changed",
    value: "CHANGED"
  },
  {
    label: "not changed",
    value: "NOT_CHANGED"
  },
]

const Splitting = () => {

  const router = useRouter()

  const { parserId } = router.query

  const [parser, setParser] = useState(null)
  const [rules, setRules] = useState([])

  const [splittingModal , setSplittingModal] = useState({
    show: false,
    type: "FIRST_PAGE",
    conditions: [],
    parentSplittingRule: 0,
    routeToParser: 0
  })

  const [splitting, setSplitting] = useState(null)

  const [allParsers, setAllParsers] = useState([])

  const getParser = () => {
    if (!parserId) return
    service.get("parsers/" + parserId, response => {
      setParser(response.data)
    })
  }

  const getSplitting = () => {
    if (!parserId) return
    service.get("parsers/" + parserId + "/splitting", response => {
      setSplitting(response.data)
    })
  }

  const getRules = () => {
    if (!parserId) return
    service.get("rules/?parserId=" + parserId, response => {
      setRules(response.data)
    })
  }

  const updateParser = () => {
    service.put("parsers/" + parserId,
      parser,
      response => {
      }
    )
  }

  const addFirstPageSplittingClickHandler = () => {
    setSplittingModal(
      produce((draft) => {
        draft.show = true
        draft.type = "FIRST_PAGE"
        draft.parentSplittingRule = null
      })
    )
  }

  const addConsecutivePageSplittingClickHandler = (firstPageSpittingRuleId) => {
    setSplittingModal(
      produce((draft) => {
        draft.show = true
        draft.type = "CONSECUTIVE_PAGE"
        draft.parentSplittingRule = firstPageSpittingRuleId
        draft.routeToParser = null
      })
    )
  }

  const addConditionBtnClickHandler = () => {
    setSplittingModal(produce((draft) => {
      draft.conditions.push({
        column: 1,
        operator: "CONTAINS",
        value: ""
      })
    }))
  }
  
  const selectConditionRuleChangeHandler = (index, e) => {
    setSplittingModal(produce((draft) => {
      draft.conditions[index]["rule"] = e.value
    }))
  }

  const selectConditionOperatorChangeHandler = (index, e) => {
    setSplittingModal(produce((draft) => {
      draft.conditions[index]["operator"] = e.value
    }))
  }
  
  const txtConditionValueChangeHandler = (index, value) => {
    setSplittingModal(produce((draft) => {
      draft.conditions[index]["value"] = value
    }))
  }

  const removeConditionBtnClickHandler = (index) => {
    setSplittingModal(produce((draft) => {
      draft.conditions.splice(index, 1)
    }))

  }

  const selectRouteToParserChangeHandler = (e) => {
    setSplittingModal(produce((draft) => {
      draft.routeToParser = e.value
    }))
  }

  const splittingRuleAddBtnClickHandler = (index) => {
    service.post("splitting_rules/", {
      splittingRuleType: splittingModal.type,
      parentSplittingRule: splittingModal.parentSplittingRule,
      splitting: splitting.id,
      routeToParser: splittingModal.routeToParser,
      splittingConditions: splittingModal.conditions
    })
  }

  const splittingRuleDeleteHandler = (id) => {
    service.delete("splitting_rules/" + id + "/", () => {
      getSplitting()
    })
  }

  const closeSplittingModalHandler = () => {
    setSplittingModal(
      produce((draft) => {
        draft.show = false
      })
    )
  }
  
  const getAllParsers = () => {
    if (!parserId) return
    service.get("parsers/", response => {
      const allParsers = response.data.filter(p => p.id != parserId)
      setAllParsers(allParsers)
    })
  }

  useEffect(() => {
    if (!router.isReady) return
    getParser()
    getAllParsers()
    getSplitting()
    getRules()
  }, [router.isReady])

  return (
    <WorkspaceLayout>
      <div className={styles.splittingWrapper}>
        <h1>Splitting</h1>
        <Card style={{ width: '100%', marginBottom: 10 }}>
          <Card.Body>
            {console.log(splitting)}
            {splitting && splitting.splittingRules.map(firstPageSplittingRule => (
            <Card style={{ width: '100%', marginBottom: 10 }}>
              {console.log(firstPageSplittingRule)}
              <Card.Body>
                <Card.Title>
                  First Page Splitting&nbsp;
                  <Button variant='danger' onClick={() => splittingRuleDeleteHandler(firstPageSplittingRule.id)}>Delete</Button>
                </Card.Title>
                <fieldset>
                  <div className={styles.firstPageSplitting}>
                    <div className={styles.firstPageSplittingConditions}>
                      {firstPageSplittingRule.splittingConditions.map((firstPageSplittingCondition, firstPageSplittingConditionIndex) => {
                        if (firstPageSplittingConditionIndex == 0) {
                          return (
                            <>
                              <div className={styles.firstPageSplittingCondition}>
                                <span className={styles.firstPageSplittingIf}>If</span>
                                <span className={styles.firstPageSplittingRuleName}>
                                  {rules.find(r => r.id == firstPageSplittingCondition.rule).name}
                                </span>
                                <span className={styles.firstPageSplittingOperator}>
                                  {conditionOperators.find(o => o.value == firstPageSplittingCondition.operator).label}
                                </span>
                                {(firstPageSplittingCondition.operator == "CONTAINS" || firstPageSplittingCondition.operator == "EQUALS") && (
                                  <span className={styles.firstPageSplittingValue}>{firstPageSplittingCondition.value}</span>
                                )}
                              </div>
                              <br/>
                            </>
                          )
                        } else {
                          return (
                            <>
                              <div className={styles.firstPageSplittingCondition}>
                                <span className={styles.firstPageSplittingAnd}>and</span>
                                <span className={styles.firstPageSplittingRuleName}>
                                  {rules.find(r => r.id == firstPageSplittingCondition.rule).name}
                                </span>
                                <span className={styles.firstPageSplittingOperator}>
                                  {conditionOperators.find(o => o.value == firstPageSplittingCondition.operator).label}
                                </span>
                                {(firstPageSplittingCondition.operator == "CONTAINS" || firstPageSplittingCondition.operator == "EQUALS") && (
                                  <span className={styles.firstPageSplittingValue}>{firstPageSplittingCondition.value}</span>
                                )}
                              </div>
                            </>
                          )
                        }
                      })}
                      <span className={styles.firstPageSplittingThen}>Then</span>
                    </div>
                    {allParsers && allParsers.length > 0 && (
                      <div className={styles.firstPageSplittingRouter}>
                        <span className={styles.firstPageSplittingRouteTo}>route to: </span>
                        {console.log(allParsers)}
                        {console.log(firstPageSplittingRule)}
                        <span className={styles.firstPageSplittingParser}>{allParsers.find(p => p.id == firstPageSplittingRule.routeToParser).name}</span>
                        <span className={styles.firstPageSplittingAsFirstPage}> as <span style={{textDecoration: "underline"}}>first page</span></span>
                      </div>
                    )}
                    <Card.Title style={{marginTop: "20px"}}>
                      Consecutive Page Splitting
                    </Card.Title>
                    {firstPageSplittingRule.consecutivePageSplittingRules && 
                      consecutivePageSplittingRules.map((consecutivePageSplittingRule, consecutivePageSplittingRuleIndex) => {
                      return (
                        <Card style={{ width: '100%', marginBottom: 10 }}>
                          <Card.Body>
                            <fieldset>
                              <div className={styles.consecutivePageSplitting}>
                                <div className={styles.consecutivePageSplittingConditions}>
                                  {consecutivePageSplittingRule && consecutivePageSplittingRule.splittingConditions.map((consecutiveSplittingCondition, consecutiveSplittingConditionIndex) => {
                                    if (consecutiveSplittingConditionIndex == 0) {
                                      return (
                                        <>
                                          <div className={styles.consecutivePageSplittingCondition}>
                                            <span className={styles.consecutivePageSplittingIf}>If</span>
                                            <span className={styles.consecutivePageSplittingRuleName}>
                                              {rules.find(r => r.id == consecutiveSplittingCondition.rule).name}
                                            </span>
                                            <span className={styles.consecutivePageSplittingOperator}>
                                              {conditionOperators.find(o => o.value == consecutiveSplittingCondition.operator).label}
                                            </span>
                                            {(consecutiveSplittingCondition.operator == "CONTAINS" || consecutiveSplittingCondition.operator == "EQUALS") && (
                                              <span className={styles.consecutivePageSplittingValue}>{consecutiveSplittingCondition.value}</span>
                                            )}
                                          </div>
                                          <br/>
                                        </>
                                      )
                                    } else {
                                      return (
                                        <>
                                          <div className={styles.consecutivePageSplittingCondition}>
                                            <span className={styles.consecutivePageSplittingAnd}>and</span>
                                            <span className={styles.consecutivePageSplittingRuleName}>
                                              {rules.find(r => r.id == consecutivePageSplittingCondition.rule).name}
                                            </span>
                                            <span className={styles.consecutivePageSplittingOperator}>
                                              {conditionOperators.find(o => o.value == consecutivePageSplittingCondition.operator).label}
                                            </span>
                                            {(consecutivePageSplittingCondition.operator == "CONTAINS" || consecutivePageSplittingCondition.operator == "EQUALS") && (
                                              <span className={styles.consecutivePageSplittingValue}>{consecutivePageSplittingCondition.value}</span>
                                            )}
                                          </div>
                                        </>
                                      )
                                    }
                                  })}
                                  
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
                      )
                    })}
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
                      <Button onClick={() => addConsecutivePageSplittingClickHandler(firstPageSplittingRule.id)}>Add Consecutive Page Splitting</Button>
                    </div>
                  </div>
                </fieldset>
              </Card.Body>
            </Card>
            ))}
            {/*<Card style={{ width: '100%', marginBottom: 10 }}>
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
                      <Button onClick={addConsecutivePageSplittingClickHandler}>Add Consecutive Page Splitting</Button>
                    </div>
                  </div>
                </fieldset>
              </Card.Body>
            </Card>*/}
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
            <Modal className={styles.splittingModal}
              show={splittingModal.show}
              onHide={closeSplittingModalHandler}
            >
              <Modal.Header closeButton>
                <Modal.Title>{splittingModal.type == "FIRST_PAGE" ? "Add first page splitting" : "Add consecutive page splitting"}</Modal.Title>
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
                  {splittingModal.conditions.map((condition, conditionIndex) => (
                      <tr key={conditionIndex}>
                      <td>{conditionIndex + 1}</td>
                      <td>
                        {console.log(condition)}
                          <Select
                              classNamePrefix="react-select"
                              options={rules.map(r => {
                                return {
                                  label: r.name,
                                  value: r.id
                                }
                              })}
                              value={rules.map(r => {
                                return {
                                  label: r.name,
                                  value: r.id
                                }
                              }).find(o => o.value == condition.ruldId)}
                              onChange={(e) => selectConditionRuleChangeHandler(conditionIndex, e)}
                              menuPlacement="auto"
                              menuPosition="fixed" />
                      </td>
                      <td>
                          <Select
                              classNamePrefix="react-select"
                              options={conditionOperators}
                              value={conditionOperators.find(o => o.value == condition.operator)}
                              onChange={(e) => selectConditionOperatorChangeHandler(conditionIndex, e)}
                              menuPlacement="auto"
                              menuPosition="fixed" />
                      </td>
                      <td>
                        {console.log(condition.operator)}
                        {(condition.operator == "EQUALS" ||
                          condition.operator == "REGEX" ||
                          condition.operator == "CONTAINS") && (
                            <Form.Control value={condition.value} onChange={(e) => txtConditionValueChangeHandler(conditionIndex, e.target.value)}/>
                          )}
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
                <Form.Group style={{marginBottom: 10}}>
                  <Button onClick={addConditionBtnClickHandler}>Add Condition</Button>
                </Form.Group>
                {splittingModal.type == "FIRST_PAGE" && (
                <Form.Group>
                  <Form.Label>Parser</Form.Label>
                  <Select options={allParsers.map(p => {
                    return {
                      label: p.name,
                      value: p.id
                    }
                  })}
                  value={allParsers.map(p => {
                    return {
                      label: p.name,
                      value: p.id
                    }
                  }).find(p => p.value == splittingModal.routeToParser)}
                  onChange={selectRouteToParserChangeHandler}
                        className={styles.parserSelect}></Select>
                </Form.Group>
                )}
                <Form.Group>
                  <Button style={{ marginRight: 10 }} onClick={splittingRuleAddBtnClickHandler}>Add</Button>
                  <Button variant="danger" onClick={closeSplittingModalHandler}>Cancel</Button>
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