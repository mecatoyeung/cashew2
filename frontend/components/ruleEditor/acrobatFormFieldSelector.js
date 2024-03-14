import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'

import cn from 'classnames'

import Dropdown from 'react-bootstrap/Dropdown'
import Button from 'react-bootstrap/Button'
import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'
import Modal from 'react-bootstrap/Modal'

import * as _ from 'lodash'

import EditorLayout from '../../layouts/editor'

import service from "../../service"

import 'react-image-crop/dist/ReactCrop.css'
import styles from '../../styles/Editor.module.css'

const AcrobatFormFieldSelector = () => {

  const router = useRouter()

  const { pathname, parserId, layoutId, ruleId, documentId = 0, pageNum = 1 } = router.query

  const [parserDocuments, setParserDocuments] = useState([])
  const [acrobatFormFields, setAcrobatFormFields] = useState([])
  const [rule, setRule] = useState(null)

  const [showChangeDocumentModal, setShowChangeDocumentModal] = useState(false)

  useEffect(() => {
    getAcrobatFormFields()
  }, [router.isReady, ruleId, documentId])

  useEffect(() => {
    if (ruleId == undefined) return
    getRule()
  }, [router.isReady, ruleId])

  useEffect(() => {
    if (rule == null) return
  }, [router.isReady, rule])

  useEffect(() => {
    if (!parserId) return
    getParserDocuments()
  }, [router.isReady, parserId])

  const getAcrobatFormFields = () => {
    if (!ruleId) return
    if (!documentId) return
    service.get("rules/" + ruleId + "/documents/" + documentId + "/acrobat_form_fields", response => {
      setAcrobatFormFields(response.data)
    })
  }

  const getRule = () => {
    service.get("rules/" + ruleId + "?parserId" + parserId, response => {
      if (documentId != null) {
        response.data.anchorDocument = {
          id: parseInt(documentId)
        }
      }
      console.log(response.data)
      setRule(response.data)
    })
  }

  const getParserDocuments = () => {
    console.log(parserId)
    service.get("documents/?parserId=" + parserId, response => {
      let parserDocuments = response.data
      for (let j=0; j<parserDocuments.length; j++) {
        let pd = parserDocuments[j]
        let ocredPagesCount = 0
        for (let i=0 ;i<pd.documentPages.length; i++) {
          if (pd.documentPages[i].ocred) {
            ocredPagesCount += 1
          }
        }
        pd.ocredPagesCount = ocredPagesCount
        pd.name = pd.filenameWithoutExtension + "." + pd.extension + " (Page " + ocredPagesCount + " of " + pd.totalPageNum + ")"
        pd.documentPages = pd.documentPages.sort((a, b) => a.pageNum - b.pageNum)
        console.log(pd)
      }
      setParserDocuments(parserDocuments)
      if (parserDocuments.length > 0 && documentId == 0) {
        selectedDocumentChangeHandler({
          target: {
            value: parserDocuments[0].id
          }
        })
      }
    })
  }

  const closeChangeDocumentModalHandler = () => {
    setShowChangeDocumentModal(false)
  }
  const openChangeDocumentModalHandler = () => setShowChangeDocumentModal(true)

  const updateRule = (updatedRule) => {
    service.put("rules/" + ruleId + "/?parserId=" + parserId,
      updatedRule,
      response => {
      }
    )
  }

  const selectedDocumentChangeHandler = (e) => {
    router.push({
      pathname,
      query: {
        ...router.query,
        documentId: e.target.value
      },
    })
  }

  const pageNumChangeHandler = (e) => {
    router.push({
      pathname,
      query: {
        ...router.query,
        pageNum: e.target.value
      },
    })
  }

  const fieldChangeHandler = (e) => {
    let updatedRule = {
      ...rule,
      acrobatFormField: e.target.value
    }
    setRule(updatedRule)
    updateRule(updatedRule)
  }

  const saveBtnClickHandler = () => {
    console.log(rule)
    return
    service.put("rules/" + ruleId + "/?parserId=" + parserId, rule, response => {
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

  const proceedToStreamEditorBtnClickHandler = () => {
    console.log("cleared!")
    router.push("/workspace/parsers/" + parserId + "/rules/" + ruleId + "?type=streamEditor&documentId=" + documentId + "&pageNum=" + pageNum)
  }

  return (
    <EditorLayout>
      <div className={styles.workbenchHeader}>
        <div className={styles.guidelines}>
          Define Field Position
        </div>
        <div className={styles.changeSampleDocumentWrapper}>
          <Button variant="primary" className={styles.changeSampleDocumentBtn} onClick={openChangeDocumentModalHandler}>Change Sample Document</Button>
          <Modal show={showChangeDocumentModal} onHide={closeChangeDocumentModalHandler}>
            <Modal.Header closeButton>
              <Modal.Title>Change Document</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <Form.Group className="mb-3" controlId="formRuleType">
                <Form.Select aria-label="Document" onChange={selectedDocumentChangeHandler} value={documentId}>
                  <option value=""></option>
                  {parserDocuments && parserDocuments.map(parserDocument => (
                    <option key={parserDocument.id} value={parserDocument.id}>{parserDocument.name}</option>
                  ))}
                </Form.Select>
              </Form.Group>
              <Form.Group className="mb-3" controlId="formPageNum">
                <Form.Select aria-label="Page No." onChange={pageNumChangeHandler} value={pageNum}>
                  <option value=""></option>
                  {parserDocuments.length > 0 && documentId != 0 && (
                    parserDocuments.find(d => d.id == documentId).documentPages.filter(dp => dp.ocred).map(
                      documentPage => {
                        return (
                          <option key={documentPage.pageNum} value={documentPage.pageNum}>{documentPage.pageNum}</option>
                        )
                      }
                    )
                  )}
                </Form.Select>
              </Form.Group>
            </Modal.Body>
            <Modal.Footer>
              <Button variant="primary" onClick={closeChangeDocumentModalHandler}>
                Confirm
              </Button>
              <Button variant="secondary" onClick={closeChangeDocumentModalHandler}>
                Close
              </Button>
            </Modal.Footer>
          </Modal>
        </div>
      </div>
      <div className={styles.ruleConfigurations}>
        {rule && (
          <div className={styles.regionSelectorWrapper}>
            <Form.Label>Field: </Form.Label>
            <Form.Group className="mb-3" controlId="formPageNum">
              <Form.Select aria-label="Field" onChange={fieldChangeHandler} value={rule.acrobatFormField}>
                <option value=""></option>
                {acrobatFormFields.map(field => (
                  <option key={field} value={field}>{field}</option>
                ))}
              </Form.Select>
            </Form.Group>
            <Button variant="primary" onClick={saveBtnClickHandler}>
              Save
            </Button>
            <Button variant="secondary" onClick={backBtnClickHandler} style={{marginLeft: "10px"}}>
              Back
            </Button>
          </div>
        )}
      </div>
      <div className={styles.workbenchFooter}>
        <div className={styles.backBtnWrapper}>
          <Button variant="success" className={styles.confirmBtn} onClick={() => router.push("/workspace/parsers/" + parserId + "/rules/" + ruleId + "?type=ruleProperties&documentId=" + documentId + "&pageNum=" + pageNum)}>Back to Rule Properties</Button>
        </div>
        <div className={styles.copyrightWrapper}>
          Copyright @ 2022
        </div>
        <div className={styles.confirmBtnWrapper}>
          <Button variant="success" className={styles.confirmBtn} onClick={proceedToStreamEditorBtnClickHandler}>Proceed to Stream Editor</Button>
        </div>
      </div>
    </EditorLayout>
  )
}

export default AcrobatFormFieldSelector