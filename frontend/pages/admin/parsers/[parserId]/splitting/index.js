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

import AdminLayout from '../../../../../layouts/admin'

import service from '../../../../../service'

import styles from '../../../../../styles/Splitting.module.css'

const splittingOptions = [
  {
    label: 'No Splitting',
    value: 'NO_SPLIT',
  },
  {
    label: 'Split by Page Number',
    value: 'SPLIT_BY_PAGE_NUM',
  },
  {
    label: 'Split by Conditions',
    value: 'SPLIT_BY_CONDITIONS',
  },
]

const conditionOperators = [
  {
    label: 'equals',
    value: 'EQUALS',
  },
  {
    label: 'regex',
    value: 'REGEX',
  },
  {
    label: 'not regex',
    value: 'NOT_REGEX',
  },
  {
    label: 'contains',
    value: 'CONTAINS',
  },
  {
    label: 'does not contains',
    value: 'DOES_NOT_CONTAINS',
  },
  {
    label: 'is empty',
    value: 'IS_EMPTY',
  },
  {
    label: 'is not empty',
    value: 'IS_NOT_EMPTY',
  },
  {
    label: 'changed',
    value: 'CHANGED',
  },
  {
    label: 'not changed',
    value: 'NOT_CHANGED',
  },
]

const noFirstPageRulesMatchedOperations = [
  {
    label: 'Remove the page',
    value: 'REMOVE_THE_PAGE',
  },
  {
    label: 'Route to parser',
    value: 'ROUTE_TO_PARSER',
  },
]

const Splitting = () => {
  const router = useRouter()

  const { parserId } = router.query

  const [parser, setParser] = useState(null)
  const [rules, setRules] = useState([])

  const [splittingModal, setSplittingModal] = useState({
    show: false,
    type: 'FIRST_PAGE',
    addOrEdit: 'ADD',
    firstPageSplittingRuleIndex: 0,
    consecutivePageSplittingRuleIndex: 0,
    consecutivePageSplittingRuleType: 'BY_CONDITIONS',
    lastPageSplittingRuleIndex: 0,
    conditions: [],
    parentSplittingRule: 0,
    routeToParser: null,
  })

  const [splitting, setSplitting] = useState(null)

  const [allParsers, setAllParsers] = useState([])

  const getParser = () => {
    if (!parserId) return
    service.get('parsers/' + parserId, (response) => {
      setParser(response.data)
    })
  }

  const getSplitting = () => {
    if (!parserId) return
    service.get('parsers/' + parserId + '/splitting', (response) => {
      setSplitting(response.data)
    })
  }

  const getRules = () => {
    if (!parserId) return
    service.get('rules/?parserId=' + parserId, (response) => {
      setRules(response.data)
    })
  }

  const addFirstPageSplittingClickHandler = () => {
    setSplittingModal(
      produce((draft) => {
        draft.show = true
        draft.type = 'FIRST_PAGE'
        draft.addOrEdit = 'ADD'
        draft.parentSplittingRule = null
        draft.routeToParser = parserId
      })
    )
  }

  const editFirstPageSplittingClickHandler = (index) => {
    setSplittingModal(
      produce((draft) => {
        draft.show = true
        draft.type = 'FIRST_PAGE'
        draft.addOrEdit = 'EDIT'
        draft.firstPageSplittingRuleIndex = index
        draft.conditions = splitting.splittingRules[0].splittingConditions
        draft.parentSplittingRule = null
      })
    )
  }

  const addConsecutivePageSplittingClickHandler = (
    firstPageSplittingRuleIndex
  ) => {
    setSplittingModal(
      produce((draft) => {
        draft.show = true
        draft.type = 'CONSECUTIVE_PAGE'
        draft.addOrEdit = 'ADD'
        draft.firstPageSplittingRuleIndex = firstPageSplittingRuleIndex
        draft.consecutivePageSplittingRuleType = 'BY_CONDITIONS'
        draft.lastPageSplittingRuleType = ''
        draft.routeToParser = parserId
      })
    )
  }

  const consecutivePageSplittingRuleTypeChangeHandler = (e) => {
    console.log(e)
    setSplittingModal(
      produce((draft) => {
        draft.consecutivePageSplittingRuleType = e.target.value
      })
    )
  }

  const editConsecutivePageSplittingClickHandler = (
    firstPageIndex,
    consecutivePageIndex
  ) => {
    setSplittingModal(
      produce((draft) => {
        draft.show = true
        draft.type = 'CONSECUTIVE_PAGE'
        draft.addOrEdit = 'EDIT'
        draft.firstPageSplittingRuleIndex = firstPageIndex
        draft.consecutivePageSplittingRuleIndex = consecutivePageIndex
        draft.conditions =
          splitting.splittingRules[
            firstPageIndex
          ].consecutivePageSplittingRules[
            consecutivePageIndex
          ].consecutivePageSplittingConditions
        draft.consecutivePageSplittingRuleType =
          splitting.splittingRules[
            firstPageIndex
          ].consecutivePageSplittingRules[
            consecutivePageIndex
          ].consecutivePageSplittingRuleType
        draft.lastPageSplittingRuleType = ''
        draft.parentSplittingRule = null
      })
    )
  }

  const addLastPageSplittingClickHandler = (firstPageSplittingRuleIndex) => {
    setSplittingModal(
      produce((draft) => {
        draft.show = true
        draft.type = 'LAST_PAGE'
        draft.addOrEdit = 'ADD'
        draft.firstPageSplittingRuleIndex = firstPageSplittingRuleIndex
        draft.consecutivePageSplittingRuleType = ''
        draft.lastPageSplittingRuleType = 'BY_CONDITIONS'
        draft.routeToParser = parserId
      })
    )
  }

  const lastPageSplittingRuleTypeChangeHandler = (e) => {
    console.log(e)
    setSplittingModal(
      produce((draft) => {
        draft.lastPageSplittingRuleType = e.target.value
      })
    )
  }

  const editLastPageSplittingClickHandler = (firstPageIndex, lastPageIndex) => {
    setSplittingModal(
      produce((draft) => {
        draft.show = true
        draft.type = 'LAST_PAGE'
        draft.addOrEdit = 'EDIT'
        draft.firstPageSplittingRuleIndex = firstPageIndex
        draft.lastPageSplittingRuleIndex = lastPageIndex
        draft.conditions =
          splitting.splittingRules[firstPageIndex].lastPageSplittingRules[
            lastPageIndex
          ].lastPageSplittingConditions
        draft.consecutivePageSplittingRuleType = ''
        draft.lastPageSplittingRuleType =
          splitting.splittingRules[firstPageIndex].lastPageSplittingRules[
            lastPageIndex
          ].lastPageSplittingRuleType
        draft.parentSplittingRule = null
      })
    )
  }

  const addConditionBtnClickHandler = () => {
    setSplittingModal(
      produce((draft) => {
        draft.conditions.push({
          column: 1,
          operator: 'CONTAINS',
          value: '',
        })
      })
    )
  }

  const selectConditionRuleChangeHandler = (index, e) => {
    setSplittingModal(
      produce((draft) => {
        draft.conditions[index]['rule'] = e.value
      })
    )
  }

  const selectConditionOperatorChangeHandler = (index, e) => {
    setSplittingModal(
      produce((draft) => {
        draft.conditions[index]['operator'] = e.value
      })
    )
  }

  const txtConditionValueChangeHandler = (index, value) => {
    setSplittingModal(
      produce((draft) => {
        draft.conditions[index]['value'] = value
      })
    )
  }

  const removeConditionBtnClickHandler = (index) => {
    setSplittingModal(
      produce((draft) => {
        draft.conditions.splice(index, 1)
      })
    )
  }

  const selectRouteToParserChangeHandler = (e) => {
    setSplittingModal(
      produce((draft) => {
        draft.routeToParser = e.value
      })
    )
  }

  const selectNoFirstPageRulesMatchedRouteToParserChangeHandler = (e) => {
    setSplitting(
      produce((draft) => {
        draft.noFirstPageRulesMatchedRouteToParser = e.value
      })
    )
  }

  const firstRuleMoveUpBtnClickHandler = (firstPageIndex) => {
    if (firstPageIndex <= 0) return
    setSplitting(
      produce((draft) => {
        let firstPageSplittingRules = draft.splittingRules
        let tmpFirstPageRule = firstPageSplittingRules[firstPageIndex]
        firstPageSplittingRules[firstPageIndex] =
          firstPageSplittingRules[firstPageIndex - 1]
        firstPageSplittingRules[firstPageIndex - 1] = tmpFirstPageRule
      })
    )
  }

  const firstRuleMoveDownBtnClickHandler = (firstPageIndex) => {
    setSplitting(
      produce((draft) => {
        let firstPageSplittingRules = draft.splittingRules
        if (firstPageIndex >= firstPageSplittingRules.length - 1) return
        let tmpFirstPageRule = firstPageSplittingRules[firstPageIndex + 1]
        firstPageSplittingRules[firstPageIndex + 1] =
          firstPageSplittingRules[firstPageIndex]
        firstPageSplittingRules[firstPageIndex] = tmpFirstPageRule
      })
    )
  }

  const consecutiveRuleMoveUpBtnClickHandler = (
    firstPageIndex,
    consecutivePageIndex
  ) => {
    if (consecutivePageIndex <= 0) return
    setSplitting(
      produce((draft) => {
        let consecutivePageSplittingRules =
          draft.splittingRules[firstPageIndex].consecutivePageSplittingRules
        let tmpConsecutiveRule =
          consecutivePageSplittingRules[consecutivePageIndex]
        consecutivePageSplittingRules[consecutivePageIndex] =
          consecutivePageSplittingRules[consecutivePageIndex - 1]
        consecutivePageSplittingRules[consecutivePageIndex - 1] =
          tmpConsecutiveRule
      })
    )
  }

  const lastRuleMoveUpBtnClickHandler = (firstPageIndex, lastPageIndex) => {
    if (lastPageIndex <= 0) return
    setSplitting(
      produce((draft) => {
        let lastPageSplittingRules =
          draft.splittingRules[firstPageIndex].lastPageSplittingRules
        let tmpLastRule = lastPageSplittingRules[lastPageIndex]
        lastPageSplittingRules[lastPageIndex] =
          lastPageSplittingRules[lastPageIndex - 1]
        lastPageSplittingRules[lastPageIndex - 1] = tmpLastRule
      })
    )
  }

  const consecutiveRuleMoveDownBtnClickHandler = (
    firstPageIndex,
    consecutivePageIndex
  ) => {
    setSplitting(
      produce((draft) => {
        let consecutivePageSplittingRules =
          draft.splittingRules[firstPageIndex].consecutivePageSplittingRules
        if (consecutivePageIndex >= consecutivePageSplittingRules.length - 1)
          return
        let tmpConsecutiveRule =
          consecutivePageSplittingRules[consecutivePageIndex + 1]
        consecutivePageSplittingRules[consecutivePageIndex + 1] =
          consecutivePageSplittingRules[consecutivePageIndex]
        consecutivePageSplittingRules[consecutivePageIndex] = tmpConsecutiveRule
      })
    )
  }

  const lastRuleMoveDownBtnClickHandler = (firstPageIndex, lastPageIndex) => {
    setSplitting(
      produce((draft) => {
        let lastPageSplittingRules =
          draft.splittingRules[firstPageIndex].lastPageSplittingRules
        if (lastPageIndex >= lastPageSplittingRules.length - 1) return
        let tmpLastRule = lastPageSplittingRules[lastPageIndex + 1]
        lastPageSplittingRules[lastPageIndex + 1] =
          lastPageSplittingRules[lastPageIndex]
        lastPageSplittingRules[lastPageIndex] = tmpLastRule
      })
    )
  }

  const firstPageSplittingRuleAddBtnClickHandler = (index) => {
    if (splittingModal.addOrEdit == 'ADD') {
      setSplitting(
        produce((draft) => {
          draft.splittingRules.push({
            splittingRuleType: 'FIRST_PAGE',
            parentSplittingRule: splittingModal.parentSplittingRule,
            splitting: splitting.id,
            routeToParser: splittingModal.routeToParser,
            splittingConditions: splittingModal.conditions,
          })
        })
      )
    } else if (splittingModal.addOrEdit == 'EDIT') {
      let splitttingRuleIndex = splittingModal.firstPageSplittingRuleIndex
      setSplitting(
        produce((draft) => {
          let updatedSplittingRule = draft.splittingRules[splitttingRuleIndex]
          updatedSplittingRule.splittingRuleType = 'FIRST_PAGE'
          updatedSplittingRule.parentSplittingRule =
            splittingModal.parentSplittingRule
          updatedSplittingRule.splitting = splitting.id
          updatedSplittingRule.routeToParser = splittingModal.routeToParser
          updatedSplittingRule.splittingConditions = splittingModal.conditions
        })
      )
    }
    setSplittingModal(
      produce((draft) => {
        draft.show = false
      })
    )
  }

  const consecutivePageSplittingRuleAddBtnClickHandler = (index) => {
    let consecutivePageSplittingRuleIndex =
      splittingModal.consecutivePageSplittingRuleIndex
    setSplitting(
      produce((draft) => {
        if (splittingModal.addOrEdit == 'ADD') {
          if (
            draft.splittingRules[splittingModal.firstPageSplittingRuleIndex]
              .consecutivePageSplittingRules == undefined
          ) {
            draft.splittingRules[
              splittingModal.firstPageSplittingRuleIndex
            ].consecutivePageSplittingRules = []
          }
          draft.splittingRules[
            splittingModal.firstPageSplittingRuleIndex
          ].consecutivePageSplittingRules.push({
            splittingRuleType: 'CONSECUTIVE_PAGE',
            parentSplittingRule: splittingModal.parentSplittingRule,
            consecutivePageSplittingRuleType:
              splittingModal.consecutivePageSplittingRuleType,
            splitting: splitting.id,
            routeToParser: splittingModal.routeToParser,
            consecutivePageSplittingConditions: splittingModal.conditions,
          })
        } else if (splittingModal.addOrEdit == 'EDIT') {
          draft.splittingRules[
            splittingModal.firstPageSplittingRuleIndex
          ].consecutivePageSplittingRules[consecutivePageSplittingRuleIndex] = {
            splittingRuleType: 'CONSECUTIVE_PAGE',
            parentSplittingRule: splittingModal.parentSplittingRule,
            consecutivePageSplittingRuleType:
              splittingModal.consecutivePageSplittingRuleType,
            splitting: splitting.id,
            routeToParser: splittingModal.routeToParser,
            consecutivePageSplittingConditions: splittingModal.conditions,
          }
        }
        console.log(draft)
      })
    )
    setSplittingModal(
      produce((draft) => {
        draft.show = false
      })
    )
  }

  const lastPageSplittingRuleAddBtnClickHandler = (index) => {
    let lastPageSplittingRuleIndex = splittingModal.lastPageSplittingRuleIndex
    setSplitting(
      produce((draft) => {
        if (splittingModal.addOrEdit == 'ADD') {
          if (
            draft.splittingRules[splittingModal.firstPageSplittingRuleIndex]
              .lastPageSplittingRules == undefined
          ) {
            draft.splittingRules[
              splittingModal.firstPageSplittingRuleIndex
            ].lastPageSplittingRules = []
          }
          console.log(splittingModal)
          draft.splittingRules[
            splittingModal.firstPageSplittingRuleIndex
          ].lastPageSplittingRules.push({
            splittingRuleType: 'LAST_PAGE',
            parentSplittingRule: splittingModal.parentSplittingRule,
            lastPageSplittingRuleType: splittingModal.lastPageSplittingRuleType,
            splitting: splitting.id,
            routeToParser: splittingModal.routeToParser,
            lastPageSplittingConditions: splittingModal.conditions,
          })
        } else if (splittingModal.addOrEdit == 'EDIT') {
          draft.splittingRules[
            splittingModal.firstPageSplittingRuleIndex
          ].lastPageSplittingRules[lastPageSplittingRuleIndex] = {
            splittingRuleType: 'LAST_PAGE',
            parentSplittingRule: splittingModal.parentSplittingRule,
            lastPageSplittingRuleType: splittingModal.lastPageSplittingRuleType,
            splitting: splitting.id,
            routeToParser: splittingModal.routeToParser,
            lastPageSplittingConditions: splittingModal.conditions,
          }
        }
      })
    )
    setSplittingModal(
      produce((draft) => {
        draft.show = false
      })
    )
  }

  const firstSplittingRuleDeleteHandler = (firstPageIndex) => {
    setSplitting(
      produce((draft) => {
        draft.splittingRules.splice(firstPageIndex, 1)
      })
    )
  }

  const consecutiveSplittingRuleDeleteHandler = (
    firstPageIndex,
    consecutivePageIndex
  ) => {
    setSplitting(
      produce((draft) => {
        let consecutivePageSplittingRules =
          draft.splittingRules[firstPageIndex].consecutivePageSplittingRules
        consecutivePageSplittingRules = consecutivePageSplittingRules.splice(
          consecutivePageIndex,
          1
        )
      })
    )
  }

  const lastSplittingRuleDeleteHandler = (firstPageIndex, lastPageIndex) => {
    setSplitting(
      produce((draft) => {
        let lastPageSplittingRules =
          draft.splittingRules[firstPageIndex].lastPageSplittingRules
        lastPageSplittingRules = lastPageSplittingRules.splice(lastPageIndex, 1)
      })
    )
  }

  const noFirstPageRulesMatchedOperationTypeChangeHandler = (e) => {
    setSplitting(
      produce((draft) => {
        draft.noFirstPageRulesMatchedOperationType = e.value
      })
    )
  }

  const toggleActivatedChkHandler = (e) => {
    setSplitting(
      produce((draft) => {
        draft.activated = e.target.checked
      })
    )
  }

  const closeSplittingModalHandler = () => {
    setSplittingModal(
      produce((draft) => {
        draft.show = false
      })
    )
  }

  const saveBtnClickHandler = () => {
    service.put('splittings/' + splitting.id + '/', splitting, (response) => {
      getSplitting()
    })
  }

  const getAllParsers = () => {
    if (!parserId) return
    service.get('parsers/', (response) => {
      const allParsers = response.data.filter((p) => p.id != parserId)
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
    <AdminLayout>
      <div className={styles.splittingWrapper}>
        <h1>Splitting</h1>
        <Card style={{ width: '100%', marginBottom: 10 }}>
          <Card.Body style={{ border: '3px solid #000', paddingLeft: 30 }}>
            {splitting &&
              splitting.splittingRules.map(
                (firstPageSplittingRule, firstPageSplittingRuleIndex) => (
                  <>
                    {firstPageSplittingRuleIndex > 0 && (
                      <p
                        style={{
                          textAlign: 'center',
                          margin: 10,
                        }}
                      >
                        or
                      </p>
                    )}
                    <Card
                      style={{ width: '100%', marginBottom: 10 }}
                      key={firstPageSplittingRuleIndex}
                    >
                      <Card.Body
                        style={{ border: '3px solid #0d6efd', paddingLeft: 30 }}
                      >
                        <Card.Title>First Page Splitting&nbsp;</Card.Title>
                        <fieldset>
                          <div className={styles.firstPageSplitting}>
                            <div
                              className={styles.firstPageSplittingConditions}
                            >
                              {firstPageSplittingRule &&
                                firstPageSplittingRule.splittingConditions.map(
                                  (
                                    firstPageSplittingCondition,
                                    firstPageSplittingConditionIndex
                                  ) => {
                                    if (firstPageSplittingConditionIndex == 0) {
                                      return (
                                        <>
                                          <div
                                            className={
                                              styles.firstPageSplittingCondition
                                            }
                                          >
                                            <span
                                              className={
                                                styles.firstPageSplittingIf
                                              }
                                            >
                                              If
                                            </span>
                                            {rules && (
                                              <span
                                                className={
                                                  styles.firstPageSplittingRuleName
                                                }
                                              >
                                                {rules &&
                                                  rules.find(
                                                    (r) =>
                                                      r.id ==
                                                      firstPageSplittingCondition.rule
                                                  ).name}
                                              </span>
                                            )}
                                            <span
                                              className={
                                                styles.firstPageSplittingOperator
                                              }
                                            >
                                              {
                                                conditionOperators.find(
                                                  (o) =>
                                                    o.value ==
                                                    firstPageSplittingCondition.operator
                                                ).label
                                              }
                                            </span>
                                            {(firstPageSplittingCondition.operator ==
                                              'CONTAINS' ||
                                              firstPageSplittingCondition.operator ==
                                                'DOES_NOT_CONTAINS' ||
                                              firstPageSplittingCondition.operator ==
                                                'EQUALS' ||
                                              firstPageSplittingCondition.operator ==
                                                'REGEX' ||
                                              firstPageSplittingCondition.operator ==
                                                'NOT_REGEX') && (
                                              <span
                                                className={
                                                  styles.firstPageSplittingValue
                                                }
                                              >
                                                {
                                                  firstPageSplittingCondition.value
                                                }
                                              </span>
                                            )}
                                          </div>
                                          <br />
                                        </>
                                      )
                                    } else {
                                      return (
                                        <>
                                          <div
                                            className={
                                              styles.firstPageSplittingCondition
                                            }
                                          >
                                            <span
                                              className={
                                                styles.firstPageSplittingAnd
                                              }
                                            >
                                              and
                                            </span>
                                            <span
                                              className={
                                                styles.firstPageSplittingRuleName
                                              }
                                            >
                                              {
                                                rules.find(
                                                  (r) =>
                                                    r.id ==
                                                    firstPageSplittingCondition.rule
                                                ).name
                                              }
                                            </span>
                                            <span
                                              className={
                                                styles.firstPageSplittingOperator
                                              }
                                            >
                                              {
                                                conditionOperators.find(
                                                  (o) =>
                                                    o.value ==
                                                    firstPageSplittingCondition.operator
                                                ).label
                                              }
                                            </span>
                                            {(firstPageSplittingCondition.operator ==
                                              'CONTAINS' ||
                                              firstPageSplittingCondition.operator ==
                                                'DOES_NOT_CONTAINS' ||
                                              firstPageSplittingCondition.operator ==
                                                'EQUALS' ||
                                              firstPageSplittingCondition.operator ==
                                                'REGEX' ||
                                              firstPageSplittingCondition.operator ==
                                                'NOT_REGEX') && (
                                              <span
                                                className={
                                                  styles.firstPageSplittingValue
                                                }
                                              >
                                                {
                                                  firstPageSplittingCondition.value
                                                }
                                              </span>
                                            )}
                                          </div>
                                        </>
                                      )
                                    }
                                  }
                                )}
                              <span className={styles.firstPageSplittingThen}>
                                Then
                              </span>
                            </div>
                            {parser && allParsers && allParsers.length > 0 && (
                              <div className={styles.firstPageSplittingRouter}>
                                <span
                                  className={styles.firstPageSplittingRouteTo}
                                >
                                  route to:{' '}
                                </span>
                                <span
                                  className={styles.firstPageSplittingParser}
                                >
                                  {parser.type == 'LAYOUT' && (
                                    <p>{parser.name}</p>
                                  )}
                                  {parser.type == 'ROUTING' && (
                                    <>
                                      {
                                        allParsers.find(
                                          (p) =>
                                            p.id ==
                                            firstPageSplittingRule.routeToParser
                                        ).name
                                      }
                                    </>
                                  )}
                                </span>
                                <span
                                  className={
                                    styles.firstPageSplittingAsFirstPage
                                  }
                                >
                                  {' '}
                                  as{' '}
                                  <span style={{ textDecoration: 'underline' }}>
                                    first page
                                  </span>
                                </span>
                              </div>
                            )}
                            <Card.Title style={{ marginTop: '20px' }}>
                              Consecutive Page Splitting
                            </Card.Title>
                            {firstPageSplittingRule.consecutivePageSplittingRules &&
                              firstPageSplittingRule.consecutivePageSplittingRules.map(
                                (
                                  consecutivePageSplittingRule,
                                  consecutivePageSplittingRuleIndex
                                ) => {
                                  return (
                                    <div
                                      key={consecutivePageSplittingRuleIndex}
                                    >
                                      {consecutivePageSplittingRuleIndex >
                                        0 && (
                                        <p
                                          style={{
                                            textAlign: 'center',
                                            margin: 10,
                                          }}
                                        >
                                          or
                                        </p>
                                      )}
                                      <Card
                                        style={{
                                          width: '100%',
                                          marginBottom: 10,
                                        }}
                                      >
                                        <Card.Body
                                          style={{
                                            border: '3px solid #dc3545',
                                            paddingLeft: 30,
                                          }}
                                        >
                                          <fieldset>
                                            <div
                                              className={
                                                styles.consecutivePageSplitting
                                              }
                                            >
                                              {consecutivePageSplittingRule &&
                                                consecutivePageSplittingRule.consecutivePageSplittingRuleType ==
                                                  'BY_CONDITIONS' && (
                                                  <div
                                                    className={
                                                      styles.consecutivePageSplittingConditions
                                                    }
                                                  >
                                                    {consecutivePageSplittingRule.consecutivePageSplittingConditions.map(
                                                      (
                                                        consecutivePageSplittingCondition,
                                                        consecutiveSplittingConditionIndex
                                                      ) => {
                                                        if (
                                                          consecutiveSplittingConditionIndex ==
                                                          0
                                                        ) {
                                                          return (
                                                            <div
                                                              key={
                                                                consecutiveSplittingConditionIndex
                                                              }
                                                            >
                                                              <div
                                                                className={
                                                                  styles.consecutivePageSplittingCondition
                                                                }
                                                              >
                                                                <span
                                                                  className={
                                                                    styles.consecutivePageSplittingIf
                                                                  }
                                                                >
                                                                  If
                                                                </span>
                                                                <span
                                                                  className={
                                                                    styles.consecutivePageSplittingRuleName
                                                                  }
                                                                >
                                                                  {
                                                                    rules.find(
                                                                      (r) =>
                                                                        r.id ==
                                                                        consecutivePageSplittingCondition.rule
                                                                    ).name
                                                                  }
                                                                </span>
                                                                <span
                                                                  className={
                                                                    styles.consecutivePageSplittingOperator
                                                                  }
                                                                >
                                                                  {
                                                                    conditionOperators.find(
                                                                      (o) =>
                                                                        o.value ==
                                                                        consecutivePageSplittingCondition.operator
                                                                    ).label
                                                                  }
                                                                </span>
                                                                {(consecutivePageSplittingCondition.operator ==
                                                                  'CONTAINS' ||
                                                                  consecutivePageSplittingCondition.operator ==
                                                                    'DOES_NOT_CONTAINS' ||
                                                                  consecutivePageSplittingCondition.operator ==
                                                                    'EQUALS' ||
                                                                  consecutivePageSplittingCondition.operator ==
                                                                    'REGEX' ||
                                                                  consecutivePageSplittingCondition.operator ==
                                                                    'NOT_REGEX') && (
                                                                  <span
                                                                    className={
                                                                      styles.consecutivePageSplittingValue
                                                                    }
                                                                  >
                                                                    {
                                                                      consecutivePageSplittingCondition.value
                                                                    }
                                                                  </span>
                                                                )}
                                                              </div>
                                                              <br />
                                                            </div>
                                                          )
                                                        } else {
                                                          return (
                                                            <>
                                                              <div
                                                                className={
                                                                  styles.consecutivePageSplittingCondition
                                                                }
                                                              >
                                                                <span
                                                                  className={
                                                                    styles.consecutivePageSplittingAnd
                                                                  }
                                                                >
                                                                  and
                                                                </span>
                                                                <span
                                                                  className={
                                                                    styles.consecutivePageSplittingRuleName
                                                                  }
                                                                >
                                                                  {
                                                                    rules.find(
                                                                      (r) =>
                                                                        r.id ==
                                                                        consecutivePageSplittingCondition.rule
                                                                    ).name
                                                                  }
                                                                </span>
                                                                <span
                                                                  className={
                                                                    styles.consecutivePageSplittingOperator
                                                                  }
                                                                >
                                                                  {
                                                                    conditionOperators.find(
                                                                      (o) =>
                                                                        o.value ==
                                                                        consecutivePageSplittingCondition.operator
                                                                    ).label
                                                                  }
                                                                </span>
                                                                {(consecutivePageSplittingCondition.operator ==
                                                                  'CONTAINS' ||
                                                                  consecutivePageSplittingCondition.operator ==
                                                                    'DOES_NOT_CONTAINS' ||
                                                                  consecutivePageSplittingCondition.operator ==
                                                                    'EQUALS' ||
                                                                  consecutivePageSplittingCondition.operator ==
                                                                    'REGEX' ||
                                                                  consecutivePageSplittingCondition.operator ==
                                                                    'NOT_REGEX') && (
                                                                  <span
                                                                    className={
                                                                      styles.consecutivePageSplittingValue
                                                                    }
                                                                  >
                                                                    {
                                                                      consecutivePageSplittingCondition.value
                                                                    }
                                                                  </span>
                                                                )}
                                                              </div>
                                                            </>
                                                          )
                                                        }
                                                      }
                                                    )}
                                                    <span
                                                      className={
                                                        styles.consecutivePageSplittingThen
                                                      }
                                                    >
                                                      Then
                                                    </span>
                                                  </div>
                                                )}
                                              {consecutivePageSplittingRule &&
                                                consecutivePageSplittingRule.consecutivePageSplittingRuleType ==
                                                  'WHEN_OTHER_FIRST_PAGE_SPLITTING_RULES_DO_NOT_MATCH' && (
                                                  <>
                                                    When other first page
                                                    splitting rules do not match
                                                  </>
                                                )}
                                              <div
                                                className={
                                                  styles.consecutivePageSplittingRouter
                                                }
                                              >
                                                <span
                                                  className={
                                                    styles.consecutivePageSplittingRouteTo
                                                  }
                                                >
                                                  route to:{' '}
                                                </span>
                                                {parser &&
                                                  parser.type == 'LAYOUT' && (
                                                    <span
                                                      className={
                                                        styles.consecutivePageSplittingParser
                                                      }
                                                    >
                                                      {parser.name}
                                                    </span>
                                                  )}
                                                {parser &&
                                                  parser.type == 'ROUTING' && (
                                                    <span
                                                      className={
                                                        styles.consecutivePageSplittingParser
                                                      }
                                                    >
                                                      {
                                                        allParsers.find(
                                                          (p) =>
                                                            p.id ==
                                                            firstPageSplittingRule.routeToParser
                                                        ).name
                                                      }
                                                    </span>
                                                  )}
                                                <span
                                                  className={
                                                    styles.consecutivePageSplittingAsFirstPage
                                                  }
                                                >
                                                  {' '}
                                                  as{' '}
                                                  <span
                                                    style={{
                                                      textDecoration:
                                                        'underline',
                                                    }}
                                                  >
                                                    consecutive page
                                                  </span>
                                                </span>
                                              </div>
                                              <div
                                                className={
                                                  styles.consecutivePageSplittingActions
                                                }
                                              >
                                                <Button
                                                  style={{ marginRight: 10 }}
                                                  onClick={() =>
                                                    consecutiveRuleMoveUpBtnClickHandler(
                                                      firstPageSplittingRuleIndex,
                                                      consecutivePageSplittingRuleIndex
                                                    )
                                                  }
                                                >
                                                  &uarr;
                                                </Button>
                                                <Button
                                                  style={{ marginRight: 10 }}
                                                  onClick={() =>
                                                    consecutiveRuleMoveDownBtnClickHandler(
                                                      firstPageSplittingRuleIndex,
                                                      consecutivePageSplittingRuleIndex
                                                    )
                                                  }
                                                >
                                                  &darr;
                                                </Button>
                                                <Button
                                                  style={{ marginRight: 10 }}
                                                  onClick={(e) =>
                                                    editConsecutivePageSplittingClickHandler(
                                                      firstPageSplittingRuleIndex,
                                                      consecutivePageSplittingRuleIndex
                                                    )
                                                  }
                                                >
                                                  Edit
                                                </Button>
                                                <Button
                                                  variant="danger"
                                                  onClick={() =>
                                                    consecutiveSplittingRuleDeleteHandler(
                                                      firstPageSplittingRuleIndex,
                                                      consecutivePageSplittingRuleIndex
                                                    )
                                                  }
                                                >
                                                  Delete
                                                </Button>
                                              </div>
                                            </div>
                                          </fieldset>
                                        </Card.Body>
                                      </Card>
                                    </div>
                                  )
                                }
                              )}
                            <div
                              className={styles.consecutivePageSplittingActions}
                            >
                              <Button
                                onClick={() =>
                                  addConsecutivePageSplittingClickHandler(
                                    firstPageSplittingRuleIndex
                                  )
                                }
                              >
                                Add Consecutive Page Splitting
                              </Button>
                            </div>
                            <Card.Title style={{ marginTop: '20px' }}>
                              Last Page Splitting
                            </Card.Title>
                            {firstPageSplittingRule.lastPageSplittingRules &&
                              firstPageSplittingRule.lastPageSplittingRules.map(
                                (
                                  lastPageSplittingRule,
                                  lastPageSplittingRuleIndex
                                ) => {
                                  return (
                                    <div key={lastPageSplittingRuleIndex}>
                                      {lastPageSplittingRuleIndex > 0 && (
                                        <p
                                          style={{
                                            textAlign: 'center',
                                            margin: 10,
                                          }}
                                        >
                                          or
                                        </p>
                                      )}
                                      <Card
                                        style={{
                                          width: '100%',
                                          marginBottom: 10,
                                        }}
                                      >
                                        <Card.Body
                                          style={{
                                            border: '3px solid #dc3545',
                                            paddingLeft: 30,
                                          }}
                                        >
                                          <fieldset>
                                            <div
                                              className={
                                                styles.lastPageSplitting
                                              }
                                            >
                                              {lastPageSplittingRule &&
                                                lastPageSplittingRule.lastPageSplittingRuleType ==
                                                  'BY_CONDITIONS' && (
                                                  <div
                                                    className={
                                                      styles.lastPageSplittingConditions
                                                    }
                                                  >
                                                    {lastPageSplittingRule &&
                                                      lastPageSplittingRule.lastPageSplittingConditions.map(
                                                        (
                                                          lastPageSplittingCondition,
                                                          lastSplittingConditionIndex
                                                        ) => {
                                                          if (
                                                            lastSplittingConditionIndex ==
                                                            0
                                                          ) {
                                                            return (
                                                              <div
                                                                key={
                                                                  lastSplittingConditionIndex
                                                                }
                                                              >
                                                                <div
                                                                  className={
                                                                    styles.lastPageSplittingCondition
                                                                  }
                                                                >
                                                                  <span
                                                                    className={
                                                                      styles.lastPageSplittingIf
                                                                    }
                                                                  >
                                                                    If
                                                                  </span>
                                                                  <span
                                                                    className={
                                                                      styles.lastPageSplittingRuleName
                                                                    }
                                                                  >
                                                                    {
                                                                      rules.find(
                                                                        (r) =>
                                                                          r.id ==
                                                                          lastPageSplittingCondition.rule
                                                                      ).name
                                                                    }
                                                                  </span>
                                                                  <span
                                                                    className={
                                                                      styles.lastPageSplittingOperator
                                                                    }
                                                                  >
                                                                    {
                                                                      conditionOperators.find(
                                                                        (o) =>
                                                                          o.value ==
                                                                          lastPageSplittingCondition.operator
                                                                      ).label
                                                                    }
                                                                  </span>
                                                                  {(lastPageSplittingCondition.operator ==
                                                                    'CONTAINS' ||
                                                                    lastPageSplittingCondition.operator ==
                                                                      'DOES_NOT_CONTAINS' ||
                                                                    lastPageSplittingCondition.operator ==
                                                                      'EQUALS' ||
                                                                    lastPageSplittingCondition.operator ==
                                                                      'REGEX' ||
                                                                    lastPageSplittingCondition.operator ==
                                                                      'NOT_REGEX') && (
                                                                    <span
                                                                      className={
                                                                        styles.lastPageSplittingValue
                                                                      }
                                                                    >
                                                                      {
                                                                        lastPageSplittingCondition.value
                                                                      }
                                                                    </span>
                                                                  )}
                                                                </div>
                                                                <br />
                                                              </div>
                                                            )
                                                          } else {
                                                            return (
                                                              <>
                                                                <div
                                                                  className={
                                                                    styles.lastPageSplittingCondition
                                                                  }
                                                                >
                                                                  <span
                                                                    className={
                                                                      styles.lastPageSplittingAnd
                                                                    }
                                                                  >
                                                                    and
                                                                  </span>
                                                                  <span
                                                                    className={
                                                                      styles.lastPageSplittingRuleName
                                                                    }
                                                                  >
                                                                    {
                                                                      rules.find(
                                                                        (r) =>
                                                                          r.id ==
                                                                          lastPageSplittingCondition.rule
                                                                      ).name
                                                                    }
                                                                  </span>
                                                                  <span
                                                                    className={
                                                                      styles.lastPageSplittingOperator
                                                                    }
                                                                  >
                                                                    {
                                                                      conditionOperators.find(
                                                                        (o) =>
                                                                          o.value ==
                                                                          lastPageSplittingCondition.operator
                                                                      ).label
                                                                    }
                                                                  </span>
                                                                  {(lastPageSplittingCondition.operator ==
                                                                    'CONTAINS' ||
                                                                    lastPageSplittingCondition.operator ==
                                                                      'DOES_NOT_CONTAINS' ||
                                                                    lastPageSplittingCondition.operator ==
                                                                      'EQUALS' ||
                                                                    lastPageSplittingCondition.operator ==
                                                                      'REGEX' ||
                                                                    lastPageSplittingCondition.operator ==
                                                                      'NOT_REGEX') && (
                                                                    <span
                                                                      className={
                                                                        styles.lastPageSplittingValue
                                                                      }
                                                                    >
                                                                      {
                                                                        lastPageSplittingCondition.value
                                                                      }
                                                                    </span>
                                                                  )}
                                                                </div>
                                                              </>
                                                            )
                                                          }
                                                        }
                                                      )}

                                                    <span
                                                      className={
                                                        styles.lastPageSplittingThen
                                                      }
                                                    >
                                                      Then
                                                    </span>
                                                  </div>
                                                )}
                                              {lastPageSplittingRule &&
                                                lastPageSplittingRule.lastPageSplittingRuleType ==
                                                  'WHEN_OTHER_FIRST_PAGE_SPLITTING_RULES_MATCH' && (
                                                  <>
                                                    When other first page
                                                    splitting rules match
                                                  </>
                                                )}
                                              <div
                                                className={
                                                  styles.lastPageSplittingRouter
                                                }
                                              >
                                                <span
                                                  className={
                                                    styles.lastPageSplittingRouteTo
                                                  }
                                                >
                                                  exit routing to:{' '}
                                                </span>
                                                <span
                                                  className={
                                                    styles.lastPageSplittingParser
                                                  }
                                                >
                                                  {parser &&
                                                    parser.type ==
                                                      'ROUTING' && (
                                                      <span
                                                        className={
                                                          styles.consecutivePageSplittingParser
                                                        }
                                                      >
                                                        {
                                                          allParsers.find(
                                                            (p) =>
                                                              p.id ==
                                                              firstPageSplittingRule.routeToParser
                                                          ).name
                                                        }
                                                      </span>
                                                    )}
                                                </span>
                                              </div>
                                              <div
                                                className={
                                                  styles.lastPageSplittingActions
                                                }
                                              >
                                                <Button
                                                  style={{ marginRight: 10 }}
                                                  onClick={() =>
                                                    lastRuleMoveUpBtnClickHandler(
                                                      firstPageSplittingRuleIndex,
                                                      lastPageSplittingRuleIndex
                                                    )
                                                  }
                                                >
                                                  &uarr;
                                                </Button>
                                                <Button
                                                  style={{ marginRight: 10 }}
                                                  onClick={() =>
                                                    lastRuleMoveDownBtnClickHandler(
                                                      firstPageSplittingRuleIndex,
                                                      lastPageSplittingRuleIndex
                                                    )
                                                  }
                                                >
                                                  &darr;
                                                </Button>
                                                <Button
                                                  style={{ marginRight: 10 }}
                                                  onClick={(e) =>
                                                    editLastPageSplittingClickHandler(
                                                      firstPageSplittingRuleIndex,
                                                      lastPageSplittingRuleIndex
                                                    )
                                                  }
                                                >
                                                  Edit
                                                </Button>
                                                <Button
                                                  variant="danger"
                                                  onClick={() =>
                                                    lastSplittingRuleDeleteHandler(
                                                      firstPageSplittingRuleIndex,
                                                      lastPageSplittingRuleIndex
                                                    )
                                                  }
                                                >
                                                  Delete
                                                </Button>
                                              </div>
                                            </div>
                                          </fieldset>
                                        </Card.Body>
                                      </Card>
                                    </div>
                                  )
                                }
                              )}
                            <div className={styles.lastPageSplittingActions}>
                              <Button
                                onClick={() =>
                                  addLastPageSplittingClickHandler(
                                    firstPageSplittingRuleIndex
                                  )
                                }
                              >
                                Add Last Page Splitting
                              </Button>
                            </div>
                            <Card
                              style={{
                                width: '100%',
                                marginBottom: 10,
                                marginTop: 10,
                              }}
                            >
                              <Card.Body
                                style={{
                                  border: '3px solid #dc3545',
                                  paddingLeft: 30,
                                }}
                              >
                                <fieldset>
                                  <div
                                    className={styles.consecutivePageSplitting}
                                  >
                                    <div
                                      className={
                                        styles.consecutivePageSplittingConditions
                                      }
                                    >
                                      <div
                                        className={
                                          styles.consecutivePageSplittingCondition
                                        }
                                      >
                                        <span
                                          className={
                                            styles.consecutivePageSplittingIf
                                          }
                                        >
                                          Else
                                        </span>
                                      </div>
                                    </div>
                                    <div
                                      className={
                                        styles.consecutivePageSplittingRouter
                                      }
                                    >
                                      <span
                                        className={
                                          styles.consecutivePageSplittingRouteTo
                                        }
                                      >
                                        return to first page checking.
                                      </span>
                                    </div>
                                  </div>
                                </fieldset>
                              </Card.Body>
                            </Card>
                          </div>
                        </fieldset>
                        <Button
                          style={{ marginRight: 10, marginBottom: 10 }}
                          onClick={() =>
                            firstRuleMoveUpBtnClickHandler(
                              firstPageSplittingRuleIndex
                            )
                          }
                        >
                          &uarr;
                        </Button>
                        <Button
                          style={{ marginRight: 10, marginBottom: 10 }}
                          onClick={() =>
                            firstRuleMoveDownBtnClickHandler(
                              firstPageSplittingRuleIndex
                            )
                          }
                        >
                          &darr;
                        </Button>
                        <Button
                          style={{ marginRight: 10, marginBottom: 10 }}
                          onClick={(e) =>
                            editFirstPageSplittingClickHandler(
                              firstPageSplittingRuleIndex
                            )
                          }
                        >
                          Edit
                        </Button>
                        <Button
                          style={{ marginRight: 10, marginBottom: 10 }}
                          variant="danger"
                          onClick={() =>
                            firstSplittingRuleDeleteHandler(
                              firstPageSplittingRuleIndex
                            )
                          }
                        >
                          Delete
                        </Button>
                      </Card.Body>
                    </Card>
                  </>
                )
              )}
            <Button
              onClick={addFirstPageSplittingClickHandler}
              style={{ marginBottom: 10 }}
            >
              Add First Page Splitting
            </Button>
            {splitting && splitting.splittingRules.length > 0 && (
              <Card style={{ width: '100%', marginBottom: 10 }}>
                <Card.Body
                  style={{ border: '3px solid #0d6efd', paddingLeft: 30 }}
                >
                  <fieldset>
                    <div className={styles.firstPageSplitting}>
                      <div className={styles.firstPageSplittingConditions}>
                        <span className={styles.firstPageSplittingIf}>
                          Else
                        </span>
                      </div>
                      <div className={styles.firstPageSplittingRouter}>
                        <Select
                          styles={{
                            control: (baseStyles, state) => ({
                              ...baseStyles,
                              border: '3px solid #0d6efd',
                            }),
                          }}
                          options={noFirstPageRulesMatchedOperations}
                          value={noFirstPageRulesMatchedOperations.find(
                            (m) =>
                              m.value ==
                              splitting.noFirstPageRulesMatchedOperationType
                          )}
                          onChange={
                            noFirstPageRulesMatchedOperationTypeChangeHandler
                          }
                        />
                      </div>
                      {allParsers &&
                        splitting &&
                        splitting.noFirstPageRulesMatchedOperationType ==
                          'ROUTE_TO_PARSER' && (
                          <Form.Group>
                            <Form.Label>Route to parser: </Form.Label>
                            <Select
                              styles={{
                                control: (baseStyles, state) => ({
                                  ...baseStyles,
                                  border: '3px solid #0d6efd',
                                }),
                              }}
                              options={allParsers.map((p) => {
                                return {
                                  label: p.name,
                                  value: p.id,
                                }
                              })}
                              value={allParsers
                                .map((p) => {
                                  return {
                                    label: p.name,
                                    value: p.id,
                                  }
                                })
                                .find(
                                  (p) =>
                                    p.value ==
                                    splitting.noFirstPageRulesMatchedRouteToParser
                                )}
                              onChange={
                                selectNoFirstPageRulesMatchedRouteToParserChangeHandler
                              }
                              className={styles.parserSelect}
                            ></Select>
                          </Form.Group>
                        )}
                    </div>
                  </fieldset>
                </Card.Body>
              </Card>
            )}

            <Modal
              className={styles.splittingModal}
              show={splittingModal.show}
              onHide={closeSplittingModalHandler}
            >
              <Modal.Header closeButton>
                <Modal.Title>
                  {splittingModal.type == 'FIRST_PAGE' &&
                    'Add first page splitting'}
                  {splittingModal.type == 'CONSECUTIVE_PAGE' &&
                    'Add consecutive page splitting'}
                  {splittingModal.type == 'LAST_PAGE' &&
                    'Add last page splitting'}
                </Modal.Title>
              </Modal.Header>
              <Modal.Body>
                {splittingModal.type == 'CONSECUTIVE_PAGE' && (
                  <>
                    <Form.Group
                      className="mb-3"
                      controlId="formConsecutivePageRuleType"
                    >
                      <Form.Select
                        aria-label="Document"
                        onChange={consecutivePageSplittingRuleTypeChangeHandler}
                        value={splittingModal.consecutivePageSplittingRuleType}
                      >
                        <option value="BY_CONDITIONS">By Conditions</option>
                        <option value="WHEN_OTHER_FIRST_PAGE_SPLITTING_RULES_DO_NOT_MATCH">
                          When other first page splitting rules do not match
                        </option>
                      </Form.Select>
                    </Form.Group>
                  </>
                )}
                {splittingModal.type == 'LAST_PAGE' && (
                  <>
                    <Form.Group
                      className="mb-3"
                      controlId="formConsecutivePageRuleType"
                    >
                      <Form.Select
                        aria-label="Document"
                        onChange={lastPageSplittingRuleTypeChangeHandler}
                        value={splittingModal.lastPageSplittingRuleType}
                      >
                        <option value="BY_CONDITIONS">By Conditions</option>
                        <option value="WHEN_OTHER_FIRST_PAGE_SPLITTING_RULES_MATCH">
                          When other first page splitting rules match
                        </option>
                      </Form.Select>
                    </Form.Group>
                  </>
                )}
                {(splittingModal.consecutivePageSplittingRuleType ==
                  'BY_CONDITIONS' ||
                  splittingModal.lastPageSplittingRuleType ==
                    'BY_CONDITIONS') && (
                  <>
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
                        {splittingModal.conditions.map(
                          (condition, conditionIndex) => (
                            <tr key={conditionIndex}>
                              <td>{conditionIndex + 1}</td>
                              <td>
                                <Select
                                  classNamePrefix="react-select"
                                  options={rules.map((r) => {
                                    return {
                                      label: r.name,
                                      value: r.id,
                                    }
                                  })}
                                  value={rules
                                    .map((r) => {
                                      return {
                                        label: r.name,
                                        value: r.id,
                                      }
                                    })
                                    .find((o) => o.value == condition.rule)}
                                  onChange={(e) =>
                                    selectConditionRuleChangeHandler(
                                      conditionIndex,
                                      e
                                    )
                                  }
                                  menuPlacement="auto"
                                  menuPosition="fixed"
                                />
                              </td>
                              <td>
                                <Select
                                  classNamePrefix="react-select"
                                  options={conditionOperators}
                                  value={conditionOperators.find(
                                    (o) => o.value == condition.operator
                                  )}
                                  onChange={(e) =>
                                    selectConditionOperatorChangeHandler(
                                      conditionIndex,
                                      e
                                    )
                                  }
                                  menuPlacement="auto"
                                  menuPosition="fixed"
                                />
                              </td>
                              <td>
                                {(condition.operator == 'EQUALS' ||
                                  condition.operator == 'REGEX' ||
                                  condition.operator == 'NOT_REGEX' ||
                                  condition.operator == 'CONTAINS' ||
                                  condition.operator ==
                                    'DOES_NOT_CONTAINS') && (
                                  <Form.Control
                                    value={condition.value}
                                    onChange={(e) =>
                                      txtConditionValueChangeHandler(
                                        conditionIndex,
                                        e.target.value
                                      )
                                    }
                                  />
                                )}
                              </td>
                              <td>
                                <Button
                                  variant="danger"
                                  onClick={() =>
                                    removeConditionBtnClickHandler(
                                      conditionIndex
                                    )
                                  }
                                  style={{ height: 46 }}
                                >
                                  Remove
                                </Button>
                              </td>
                            </tr>
                          )
                        )}
                      </tbody>
                    </Table>
                    <Form.Group style={{ marginBottom: 10 }}>
                      <Button onClick={addConditionBtnClickHandler}>
                        Add Condition
                      </Button>
                    </Form.Group>
                  </>
                )}
                {splittingModal.type == 'FIRST_PAGE' && parser && (
                  <Form.Group>
                    <Form.Label>Parser</Form.Label>
                    {parser.type == 'LAYOUT' && <p>{parser.name}</p>}
                    {parser.type == 'ROUTING' && (
                      <Select
                        options={allParsers.map((p) => {
                          return {
                            label: p.name,
                            value: p.id,
                          }
                        })}
                        value={allParsers
                          .map((p) => {
                            return {
                              label: p.name,
                              value: p.id,
                            }
                          })
                          .find((p) => p.value == splittingModal.routeToParser)}
                        onChange={selectRouteToParserChangeHandler}
                        className={styles.parserSelect}
                      ></Select>
                    )}
                  </Form.Group>
                )}
                <Form.Group>
                  {splittingModal.type == 'FIRST_PAGE' && (
                    <Button
                      style={{ marginRight: 10 }}
                      onClick={firstPageSplittingRuleAddBtnClickHandler}
                    >
                      {splittingModal.addOrEdit == 'ADD' && 'Add'}
                      {splittingModal.addOrEdit == 'EDIT' && 'Update'}
                    </Button>
                  )}
                  {splittingModal.type == 'CONSECUTIVE_PAGE' && (
                    <Button
                      style={{ marginRight: 10 }}
                      onClick={consecutivePageSplittingRuleAddBtnClickHandler}
                    >
                      {splittingModal.addOrEdit == 'ADD' && 'Add'}
                      {splittingModal.addOrEdit == 'EDIT' && 'Update'}
                    </Button>
                  )}
                  {splittingModal.type == 'LAST_PAGE' && (
                    <Button
                      style={{ marginRight: 10 }}
                      onClick={lastPageSplittingRuleAddBtnClickHandler}
                    >
                      {splittingModal.addOrEdit == 'ADD' && 'Add'}
                      {splittingModal.addOrEdit == 'EDIT' && 'Update'}
                    </Button>
                  )}
                  <Button variant="danger" onClick={closeSplittingModalHandler}>
                    Cancel
                  </Button>
                </Form.Group>
              </Modal.Body>
            </Modal>
          </Card.Body>
        </Card>
        {splitting && (
          <Form.Group style={{ marginBottom: 10 }}>
            <Form.Check
              type={'checkbox'}
              id={`default-activated`}
              label={`Activated`}
              onChange={toggleActivatedChkHandler}
              checked={splitting.activated}
            />
          </Form.Group>
        )}

        <Button onClick={() => saveBtnClickHandler()}>Save</Button>
      </div>
    </AdminLayout>
  )
}

export default Splitting
