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
      label: "does not contains",
      value: "DOES_NOT_CONTAINS"
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

const noFirstPageRulesMatchedOperations = [
  {
    label: "Remove the page",
    value: "REMOVE_THE_PAGE"
  },
  {
    label: "Proceed to parsing queue of the current layout",
    value: "CONTINUE_PARSING"
  },
  {
    label: "Route to parser",
    value: "ROUTE_TO_PARSER"
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
      console.log(response.data)
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

  const addConsecutivePageSplittingClickHandler = (firstPageSplittingRuleIndex) => {
    setSplittingModal(
      produce((draft) => {
        draft.show = true
        draft.type = "CONSECUTIVE_PAGE"
        draft.firstPageSplittingRuleIndex = firstPageSplittingRuleIndex
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

  const selectNoFirstPageRulesMatchedRouteToParserChangeHandler = (e) => {
    setSplitting(produce((draft) => {
      draft.noFirstPageRulesMatchedRouteToParser = e.value
    }))
  }

  const firstRuleMoveUpBtnClickHandler = (firstPageIndex) => {
    if (firstPageIndex <= 0) return
    setSplitting(produce(draft => {
      let firstPageSplittingRules = draft.splittingRules
      let tmpFirstPageRule = firstPageSplittingRules[firstPageIndex]
      firstPageSplittingRules[firstPageIndex] = firstPageSplittingRules[firstPageIndex - 1]
      firstPageSplittingRules[firstPageIndex - 1] = tmpFirstPageRule
    }))
  }

  const firstRuleMoveDownBtnClickHandler = (firstPageIndex) => {
    setSplitting(produce(draft => {
      let firstPageSplittingRules = draft.splittingRules
      if (firstPageIndex >= (firstPageSplittingRules.length - 1)) return
      let tmpFirstPageRule = firstPageSplittingRules[firstPageIndex + 1]
      firstPageSplittingRules[firstPageIndex + 1] = firstPageSplittingRules[firstPageIndex]
      firstPageSplittingRules[firstPageIndex] = tmpFirstPageRule
    }))
  }

  const consecutiveRuleMoveUpBtnClickHandler = (firstPageIndex, consecutivePageIndex) => {
    if (consecutivePageIndex <= 0) return
    setSplitting(produce(draft => {
      let consecutivePageSplittingRules = draft.splittingRules[firstPageIndex].consecutivePageSplittingRules
      let tmpConsecutiveRule = consecutivePageSplittingRules[consecutivePageIndex]
      consecutivePageSplittingRules[consecutivePageIndex] = consecutivePageSplittingRules[consecutivePageIndex - 1]
      consecutivePageSplittingRules[consecutivePageIndex - 1] = tmpConsecutiveRule
    }))
  }

  const consecutiveRuleMoveDownBtnClickHandler = (firstPageIndex, consecutivePageIndex) => {
    setSplitting(produce(draft => {
      let consecutivePageSplittingRules = draft.splittingRules[firstPageIndex].consecutivePageSplittingRules
      if (consecutivePageIndex >= (consecutivePageSplittingRules.length - 1)) return
      let tmpConsecutiveRule = consecutivePageSplittingRules[consecutivePageIndex + 1]
      consecutivePageSplittingRules[consecutivePageIndex + 1] = consecutivePageSplittingRules[consecutivePageIndex]
      consecutivePageSplittingRules[consecutivePageIndex] = tmpConsecutiveRule
    }))
  }

  const firstPageSplittingRuleAddBtnClickHandler = (index) => {
    setSplitting(produce((draft) => {
      draft.splittingRules.push({
        splittingRuleType: "FIRST_PAGE",
        parentSplittingRule: splittingModal.parentSplittingRule,
        splitting: splitting.id,
        routeToParser: splittingModal.routeToParser,
        splittingConditions: splittingModal.conditions
      })
    }))
    setSplittingModal(
      produce((draft) => {
        draft.show = false
       } ))
  }

  const consecutivePageSplittingRuleAddBtnClickHandler = (index) => {
    setSplitting(produce((draft) => {
      if (draft.splittingRules[splittingModal.firstPageSplittingRuleIndex].consecutivePageSplittingRules == undefined) {
        draft.splittingRules[splittingModal.firstPageSplittingRuleIndex].consecutivePageSplittingRules = []
      }
      draft.splittingRules[splittingModal.firstPageSplittingRuleIndex].consecutivePageSplittingRules.push({
        splittingRuleType: "CONSECUTIVE_PAGE",
        parentSplittingRule: splittingModal.parentSplittingRule,
        splitting: splitting.id,
        routeToParser: splittingModal.routeToParser,
        splittingConditions: splittingModal.conditions
      })
    }))
    setSplittingModal(
      produce((draft) => {
        draft.show = false
       } ))
  }

  const firstSplittingRuleDeleteHandler = (firstPageIndex) => {
    setSplitting(produce(draft => {
      draft.splittingRules.splice(firstPageIndex, 1)
    }))
  }

  const consecutiveSplittingRuleDeleteHandler = (firstPageIndex, consecutivePageIndex) => {
    setSplitting(produce(draft => {
      let consecutivePageSplittingRules = draft.splittingRules[firstPageIndex].consecutivePageSplittingRules
      consecutivePageSplittingRules = consecutivePageSplittingRules.splice(consecutivePageIndex, 1)
    }))
  }

  const noFirstPageRulesMatchedOperationTypeChangeHandler = (e) => {
    setSplitting(produce(draft => {
      draft.noFirstPageRulesMatchedOperationType = e.value
    }))
  }

  const toggleActivatedChkHandler = (e) => {
    setSplitting(produce(draft => {
      draft.activated = e.target.checked
    }))
  }

  const closeSplittingModalHandler = () => {
    setSplittingModal(
      produce((draft) => {
        draft.show = false
      })
    )
  }

  const saveBtnClickHandler = () => {
    service.put("splittings/" + splitting.id + '/', splitting, (response) => {
      getSplitting()
    })
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
            {splitting && splitting.splittingRules.map((firstPageSplittingRule, firstPageSplittingRuleIndex) => (
            <Card style={{ width: '100%', marginBottom: 10 }} key={firstPageSplittingRuleIndex}>
              <Card.Body>
                <Card.Title>
                  First Page Splitting&nbsp;
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
                                {rules && (
                                  <span className={styles.firstPageSplittingRuleName}>
                                    {rules.find(r => r.id == firstPageSplittingCondition.rule).name}
                                  </span>
                                )}
                                <span className={styles.firstPageSplittingOperator}>
                                  {conditionOperators.find(o => o.value == firstPageSplittingCondition.operator).label}
                                </span>
                                {(firstPageSplittingCondition.operator == "CONTAINS" || firstPageSplittingCondition.operator == "DOES_NOT_CONTAINS" || firstPageSplittingCondition.operator == "EQUALS") && (
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
                                {(firstPageSplittingCondition.operator == "CONTAINS" || firstPageSplittingCondition.operator == "DOES_NOT_CONTAINS"  || firstPageSplittingCondition.operator == "EQUALS") && (
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
                        {console.log(splitting)}
                        <span className={styles.firstPageSplittingParser}>{allParsers.find(p => p.id == firstPageSplittingRule.routeToParser).name}</span>
                        <span className={styles.firstPageSplittingAsFirstPage}> as <span style={{textDecoration: "underline"}}>first page</span></span>
                      </div>
                    )}
                    <Card.Title style={{marginTop: "20px"}}>
                      Consecutive Page Splitting
                    </Card.Title>
                    {firstPageSplittingRule.consecutivePageSplittingRules && 
                      firstPageSplittingRule.consecutivePageSplittingRules.map((consecutivePageSplittingRule, consecutivePageSplittingRuleIndex) => {
                      return (
                        <div key={consecutivePageSplittingRuleIndex}>
                          {consecutivePageSplittingRuleIndex > 0 && (
                            <p style={{textAlign: "center", margin: 10}}>or</p>
                          )}
                          <Card style={{ width: '100%', marginBottom: 10 }}>
                            <Card.Body>
                              <fieldset>
                                <div className={styles.consecutivePageSplitting}>
                                  <div className={styles.consecutivePageSplittingConditions}>
                                    {consecutivePageSplittingRule && consecutivePageSplittingRule.splittingConditions.map((consecutivePageSplittingCondition, consecutiveSplittingConditionIndex) => {
                                      if (consecutiveSplittingConditionIndex == 0) {
                                        return (
                                          <div key={consecutiveSplittingConditionIndex}>
                                            <div className={styles.consecutivePageSplittingCondition}>
                                              <span className={styles.consecutivePageSplittingIf}>If</span>
                                              <span className={styles.consecutivePageSplittingRuleName}>
                                                {rules.find(r => r.id == consecutivePageSplittingCondition.rule).name}
                                              </span>
                                              <span className={styles.consecutivePageSplittingOperator}>
                                                {conditionOperators.find(o => o.value == consecutivePageSplittingCondition.operator).label}
                                              </span>
                                              {(consecutivePageSplittingCondition.operator == "CONTAINS" || consecutivePageSplittingCondition.operator == "DOES_NOT_CONTAINS" || consecutivePageSplittingCondition.operator == "EQUALS") && (
                                                <span className={styles.consecutivePageSplittingValue}>{consecutivePageSplittingCondition.value}</span>
                                              )}
                                            </div>
                                            <br/>
                                          </div>
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
                                              {(consecutivePageSplittingCondition.operator == "CONTAINS" || consecutivePageSplittingCondition.operator == "DOES_NOT_CONTAINS" || consecutivePageSplittingCondition.operator == "EQUALS") && (
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
                                    <span className={styles.consecutivePageSplittingParser}>{allParsers.find(p => p.id == firstPageSplittingRule.routeToParser).name}</span>
                                    <span className={styles.consecutivePageSplittingAsFirstPage}> as <span style={{textDecoration: "underline"}}>consecutive page</span></span>
                                  </div>
                                  <div className={styles.consecutivePageSplittingActions}>
                                    <Button style={{marginRight: 10}} onClick={() => consecutiveRuleMoveUpBtnClickHandler(firstPageSplittingRuleIndex, consecutivePageSplittingRuleIndex)}>&uarr;</Button>
                                    <Button style={{marginRight: 10}} onClick={() => consecutiveRuleMoveDownBtnClickHandler(firstPageSplittingRuleIndex, consecutivePageSplittingRuleIndex)}>&darr;</Button>
                                    <Button variant='danger' onClick={() => consecutiveSplittingRuleDeleteHandler(firstPageSplittingRuleIndex, consecutivePageSplittingRuleIndex)}>Delete</Button>
                                  </div>
                                </div>
                              </fieldset>
                            </Card.Body>
                          </Card>
                        </div>
                      )
                    })}
                    <div className={styles.consecutivePageSplittingActions}>
                      <Button onClick={() => addConsecutivePageSplittingClickHandler(firstPageSplittingRuleIndex)}>Add Consecutive Page Splitting</Button>
                    </div>
                    
                    <Card style={{ width: '100%', marginBottom: 10, marginTop: 10 }}>
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
                  </div>
                </fieldset>
                <Button style={{marginRight: 10, marginBottom: 10}} onClick={() => firstRuleMoveUpBtnClickHandler(firstPageSplittingRuleIndex)}>&uarr;</Button>
                <Button style={{marginRight: 10, marginBottom: 10}} onClick={() => firstRuleMoveDownBtnClickHandler(firstPageSplittingRuleIndex)}>&darr;</Button>
                <Button style={{marginRight: 10, marginBottom: 10}} variant='danger' onClick={() => firstSplittingRuleDeleteHandler(firstPageSplittingRuleIndex)}>Delete</Button>
              </Card.Body>
            </Card>
            ))}
            <Button onClick={addFirstPageSplittingClickHandler} style={{marginBottom: 10}}>Add First Page Splitting</Button>
            {splitting && splitting.splittingRules.length > 0 && (
              <Card style={{ width: '100%', marginBottom: 10 }}>
                <Card.Body>
                  <fieldset>
                    <div className={styles.firstPageSplitting}>
                      <div className={styles.firstPageSplittingConditions}>
                        <span className={styles.firstPageSplittingIf}>Else</span>
                      </div>
                      <div className={styles.firstPageSplittingRouter}>
                        <Select options={noFirstPageRulesMatchedOperations} value={
                            noFirstPageRulesMatchedOperations.find(m => m.value == splitting.noFirstPageRulesMatchedOperationType)
                          } onChange={noFirstPageRulesMatchedOperationTypeChangeHandler}/>
                      </div>
                      {console.log(splitting)}
                      {allParsers && splitting && splitting.noFirstPageRulesMatchedOperationType == "ROUTE_TO_PARSER" && (
                        <Form.Group>
                          <Form.Label>Route to parser: </Form.Label>
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
                          }).find(p => p.value == splitting.noFirstPageRulesMatchedRouteToParser)}
                          onChange={selectNoFirstPageRulesMatchedRouteToParserChangeHandler}
                                className={styles.parserSelect}></Select>
                        </Form.Group>
                        )}
                    </div>
                  </fieldset>
                </Card.Body>
              </Card>
            )}
            
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
                        {(condition.operator == "EQUALS" ||
                          condition.operator == "REGEX" ||
                          condition.operator == "CONTAINS" ||
                          condition.operator == "DOES_NOT_CONTAINS") && (
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
                  {splittingModal.type == "FIRST_PAGE" && (
                  <Button style={{ marginRight: 10 }} onClick={firstPageSplittingRuleAddBtnClickHandler}>Add</Button>
                  )}
                  {splittingModal.type == "CONSECUTIVE_PAGE" && (
                  <Button style={{ marginRight: 10 }} onClick={consecutivePageSplittingRuleAddBtnClickHandler}>Add</Button>
                  )}
                  <Button variant="danger" onClick={closeSplittingModalHandler}>Cancel</Button>
                </Form.Group>
              </Modal.Body>
            </Modal>
          </Card.Body>
        </Card>
        {splitting && (
          <Form.Group style={{marginBottom: 10}}>
            <Form.Check
              type={"checkbox"}
              id={`default-activated`}
              label={`Activated`}
              onChange={toggleActivatedChkHandler}
              checked={splitting.activated}
            />
          </Form.Group>
        )}
        
        <Button 
          onClick={() => saveBtnClickHandler()}>
          Save
        </Button>
      </div>
    </WorkspaceLayout>
  )
}

export default Splitting