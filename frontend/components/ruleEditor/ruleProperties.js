import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'

import cn from 'classnames'

import Dropdown from 'react-bootstrap/Dropdown'
import Button from 'react-bootstrap/Button'
import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'
import Modal from 'react-bootstrap/Modal'
import ToastContainer from 'react-bootstrap/ToastContainer'
import Toast from 'react-bootstrap/Toast'

import * as _ from 'lodash'

import EditorLayout from '../../layouts/editor'

import service from "../../service"

import styles from '../../styles/Editor.module.css'

const RuleProperties = () => {

  const router = useRouter()

  const { parserId, layoutId, ruleId, documentId = 0, pageNum = 1 } = router.query

  const [rule, setRule] = useState(null)

  const [toast, setToast] = useState({
    show: false,
    type: "success",
    message: ""
  })

  useEffect(() => {
    if (!router.isReady) return
    getRule()
  }, [router.isReady, ruleId])

  const getRule = () => {
    service.get("rules/" + ruleId + "/", response => {
      setRule(response.data)
    })
  }

  const setRuleName = (e) => {
    let updatedRule = {...rule}
    updatedRule.name = e.target.value
    setRule(updatedRule)
  }

  const setRuleInputDropDown = (e) => {
    let updatedRule = {...rule}
    updatedRule.inputDropdownList = e.target.value
    setRule(updatedRule)
  }

  const saveBtnClickHandler = () => {
    service.put("rules/" + ruleId + "/", rule, response => {
      router.push("/workspace/parsers/" + parserId + "/rules/")
      setToast({
        show: true,
        type: "success",
        message: "Rule is updated successfully!"
      })
    })
  }

  const backBtnClickHandler = () => {
    router.push({
      pathname: "/workspace/parsers/" + parserId + "/rules",
      query: {
        documentId: documentId
      }
    })
  }

  const proceedToRegionSelectorBtnClickHandler = () => {
    router.push("/workspace/parsers/" + parserId + "/rules/" + ruleId + "/?type=regionSelector&documentId=" + documentId + "&pageNum=" + pageNum)
  }

  const proceedToAcrobatFormFieldSelectorBtnClickHandler = () => {
    router.push("/workspace/parsers/" + parserId + "/rules/" + ruleId + "/?type=acrobatFormFieldSelector&documentId=" + documentId + "&pageNum=" + pageNum)
  }

  return (
    <EditorLayout>
      <div className={styles.workbenchHeader}>
        <div className={styles.guidelines}>
          Rule Properties
        </div>
      </div>
      <div className={styles.rulePropertiesWrapper}>
        {rule && (
            <>
              <Form.Group className="mb-3" controlId="formNewRuleInputDropdown">
                <Form.Label>Name</Form.Label>
                <Form.Control onChange={(e) => setRuleName(e)} value={rule.name}/>
              </Form.Group>
              {rule.ruleType == 'INPUT_DROPDOWN' && (
                <Form.Group className="mb-3" controlId="formNewRuleInputDropdown">
                  <Form.Label>Input Drop Down List {"("}separated by return character{")"}</Form.Label>
                  <Form.Control as="textarea" rows={8} onChange={(e) => setRuleInputDropDown(e)} value={rule.inputDropdownList}/>
                </Form.Group>
              )}
              <Button variant="primary" onClick={saveBtnClickHandler}>
                Save
              </Button>
              <Button variant="secondary" onClick={backBtnClickHandler} style={{marginLeft: "10px"}}>
                Back
              </Button>
              <ToastContainer position="bottom-center" role={toast.type} className="p-3">
                  <Toast onClose={() => setToast({...toast, show: false})} show={toast.show} delay={3000} autohide>
                      <Toast.Body>{toast.message}</Toast.Body>
                  </Toast>
              </ToastContainer>
            </>

        )}
      </div>
      <div className={styles.workbenchFooter}>
        <div className={styles.backBtnWrapper}>
          <div className={styles.parsingRulesFooter}>
          </div>
        </div>
        <div className={styles.copyrightWrapper}>
          Copyright @ 2022
        </div>
        {rule && rule.ruleType != "INPUT_TEXTFIELD" && rule.ruleType != "INPUT_DROPDOWN" && rule.ruleType != "ACROBAT_FORM" && (
          <div className={styles.confirmBtnWrapper}>
            <Button variant="success" className={styles.confirmBtn} onClick={proceedToRegionSelectorBtnClickHandler}>Proceed to Region Selector</Button>
          </div>
        )}
        { rule && rule.ruleType == "ACROBAT_FORM" && (
          <div className={styles.confirmBtnWrapper}>
            <Button variant="success" className={styles.confirmBtn} onClick={proceedToAcrobatFormFieldSelectorBtnClickHandler}>Proceed to Field Selector</Button>
          </div>
        )}
      </div>
    </EditorLayout>
  )
}

export default RuleProperties