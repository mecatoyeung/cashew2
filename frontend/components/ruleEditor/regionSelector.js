import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'

import cn from 'classnames'

import Dropdown from 'react-bootstrap/Dropdown'
import Button from 'react-bootstrap/Button'
import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'
import Modal from 'react-bootstrap/Modal'

import ReactCrop from 'react-image-crop'

import Draggable from 'react-draggable'

import * as _ from 'lodash'

import EditorLayout from '../../layouts/editor'


import service from "../../service"

import 'react-image-crop/dist/ReactCrop.css'
import styles from '../../styles/Editor.module.css'

const RegionSelector = () => {

  const router = useRouter()

  const { pathname, parserId, layoutId, ruleId, documentId = 0, pageNum = 1 } = router.query

  const [regionMode, setRegionMode] = useState("Textfield")
  const [textfieldRegion, setTextfieldRegion] = useState({
    unit: '%',
    x: 25,
    y: 25,
    width: 50,
    height: 50
  })
  const [anchorRegion, setAnchorRegion] = useState({
    unit: '%',
    x: 25,
    y: 25,
    width: 50,
    height: 50
  })

  const [textfieldAnchorToggle, setTextfieldAnchorToggle] = useState("textfield")

  const [parserDocuments, setParserDocuments] = useState([])
  const [layout, setLayout] = useState([])
  const [rule, setRule] = useState(null)

  const [showChangeDocumentModal, setShowChangeDocumentModal] = useState(false)

  const [imageUri, setImageUri] = useState(null)
  const [imageRef, setImageRef] = useState()

  useEffect(() => {
    if (layoutId == undefined) return
    getLayout()
  }, [router.isReady, layoutId])

  useEffect(() => {
    if (ruleId == undefined) return
    getRule()
  }, [router.isReady, ruleId])

  useEffect(() => {
    if (rule == null) return
    setInitialRegion()
  }, [router.isReady, rule])

  let getParserDocumentsTimer
  useEffect(() => {
    if (parserId == undefined) return
    getParserDocuments()
    /*getParserDocumentsTimer = setInterval(() => {
      getParserDocuments();
    }, 5000);
    return () => clearInterval(getParserDocumentsTimer);*/
  }, [router.isReady, parserId])

  useEffect(() => {
    getDocumentPageImage()
  }, [router.isReady, parserId, documentId, pageNum])

  useEffect(() => {
  }, [imageRef])

  const getLayout = () => {
    service.get("layouts/" + layoutId, response => {
      setLayout(response.data)
    })
  }

  const getRule = () => {
    service.get("rules/" + ruleId + "?parserId" + parserId, response => {
      if (documentId != null) {
        response.data.anchorDocument = documentId
      }
      console.log(response.data)
      setRule(response.data)
    })
  }

  const getParserDocuments = () => {
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

  const getDocumentPageImage = () => {
    if (parserId == undefined) return
    if (documentId == 0) return
    service.getFile("documents/" + documentId + "/pages/" + pageNum + "/image/",
      (response) => {
        let data = `data:${
          response.headers["content-type"]
        };base64,${new Buffer(response.data, "binary").toString("base64")}`
        setImageUri(data)
      })
  }

  const closeChangeDocumentModalHandler = () => {
    setShowChangeDocumentModal(false)
    setInitialRegion()
  }
  const openChangeDocumentModalHandler = () => setShowChangeDocumentModal(true)

  const updateRule = (updatedRule) => {
    console.log(updatedRule)
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

  const txtPagesChangeHandler = (e) => {
    let updatedRule = { ...rule }
    updatedRule.pages = e.target.value
    updateRule(updatedRule)
    setRule(updatedRule)
  }

  const txtAnchorTextChangeHandler = (e) => {
    let updatedRule = { ...rule }
    updatedRule.anchorText = e.target.value
    updateRule(updatedRule)
    setRule(updatedRule)
  }

  const selectRegionModeChangeHandler =(e) => {
    setRegionMode(e.target.value)
  }

  const setInitialRegion = () => {
    let y1 = 100 - rule.y2
    let y2 = 100 - rule.y1
    let anchorY1 = 100 - rule.anchorY2
    let anchorY2 = 100 - rule.anchorY1
    let initialRegions = [
      {
        unit: "%",
        x: parseFloat(rule.x1),
        y: y1,
        width: rule.x2 - rule.x1,
        height: y2 - y1
      },
      {
        unit: "%",
        x: parseFloat(rule.anchorX1),
        y: anchorY1,
        width: rule.anchorX2 - rule.anchorX1,
        height: anchorY2 - anchorY1
      }
    ]
    setTextfieldRegion(initialRegions[0])
    setAnchorRegion(initialRegions[1])
  }

  const selectTextFieldAnchorChangeHandler = (e) => {
    setTextfieldAnchorToggle(e.target.value)
  }

  const textfieldRegionChangeHandler = (p) => {
    setTextfieldRegion(p)
    let updatedRule = {
      ...rule,
      x1: p.x.toFixed(2),
      x2: (p.x + p.width).toFixed(2),
      y1: (100 - p.y - p.height).toFixed(2),
      y2: (100 - p.y).toFixed(2),
      anchorX1: anchorRegion.x.toFixed(2),
      anchorX2: (anchorRegion.x + anchorRegion.width).toFixed(2),
      anchorY1: (100 - anchorRegion.y - anchorRegion.height).toFixed(2),
      anchorY2: (100 - anchorRegion.y).toFixed(2),
      anchorDocument: {
        id: parseInt(documentId)
      },
      anchorPageNum: pageNum
    }
    setRule(updatedRule)
  }

  const anchorRegionChangeHandler = (p) => {
    setAnchorRegion(p)
    let updatedRule = {
      ...rule,
      x1: textfieldRegion.x.toFixed(2),
      x2: (textfieldRegion.x + textfieldRegion.width).toFixed(2),
      y1: (100 - textfieldRegion.y - textfieldRegion.height).toFixed(2),
      y2: (100 - textfieldRegion.y).toFixed(2),
      anchorX1: p.x.toFixed(2),
      anchorX2: (p.x + p.width).toFixed(2),
      anchorY1: (100 - p.y - p.height).toFixed(2),
      anchorY2: (100 - p.y).toFixed(2),
      anchorDocument: { 
        id: parseInt(documentId)
      },
      anchorPageNum: pageNum
    }
    setRule(updatedRule)
  }

  const anchorRegionDragEndHandler = (p) => {
    updateRule(rule)
    console.log(rule)
  }

  const textfieldRegionDragEndHandler = (p) => {
    updateRule(rule)
    console.log(rule)
  }

  const addSeparatorBtnClickHandler = (e) => {
    let updatedRule = { ...rule }
    let tableColumnSeparators = [...updatedRule.tableColumnSeparators]
    let x;
    if (tableColumnSeparators.length > 0) {
      x = tableColumnSeparators.slice(-1)[0].x  + 10.0
    } else {
      x = 10.0
    }
    tableColumnSeparators.push({ x, rule: updatedRule.id })
    updatedRule.tableColumnSeparators = tableColumnSeparators
    console.log(tableColumnSeparators)
    updateRule(updatedRule)
    setRule(updatedRule)
  }

  const removeSeparatorBtnClickHandler = (e) => {
    let updatedRule = { ...rule }
    let tableColumnSeparators = [...updatedRule.tableColumnSeparators]
    tableColumnSeparators.pop()
    updatedRule.tableColumnSeparators = tableColumnSeparators
    updateRule(updatedRule)
    setRule(updatedRule)
  }

  const separatorStartHandler = (e, el, xIndex) => {
    e.stopPropagation()
  }

  const separatorDragHandler = (e, el, xIndex) => {
    e.stopPropagation()
  }

  const separatorStopHandler = (e, el, xIndex) => {
    let width = imageRef.width

    let updatedRule = { ...rule }
    let tableColumnSeparators = updatedRule.tableColumnSeparators
    tableColumnSeparators[xIndex] = { 
      x: (el.x / width * 100).toFixed(2),
      rule: updatedRule.id
    }
    tableColumnSeparators.sort((a, b) => (a.x > b.x) ? 1 : -1)
    console.log(updatedRule)
    setRule(updatedRule)
    updateRule(updatedRule)
    e.stopPropagation()
  }

  const proceedToStreamEditorBtnClickHandler = () => {
    //clearInterval(getParserDocumentsTimer)
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
          <>
            <div className={styles.regionConfiurations}>
              <div className="row">
                <div className="col-3">
                  <Form.Group className="mb-3" controlId="formPages">
                    <Form.Label>Pages: </Form.Label>
                    <Form.Control value={rule.pages} onChange={txtPagesChangeHandler} />
                  </Form.Group>
                </div>
                {rule.ruleType == "TABLE" && (
                  <div className="col-6">
                    <Form.Group className="mb-3" controlId="formPages" style={{ padding: "0 10px" }}>
                      <Form.Label>Separators: </Form.Label>
                      <div className={styles.regionSelectActions} style={{display: "block", padding: "0"}}>
                        <Button variant="primary" className={styles.addSeparatorBtn} onClick={addSeparatorBtnClickHandler}>Add</Button>
                        <Button variant="primary" className={styles.removeSeparatorBtn} onClick={removeSeparatorBtnClickHandler}>Remove</Button>
                      </div>
                    </Form.Group>
                  </div>
                )}
                {rule.ruleType == "ANCHORED_TEXTFIELD" && (
                  <>
                    <div className="col-3">
                      <Form.Group className="mb-3" controlId="formAnchorText">
                        <Form.Label>Anchor Text: </Form.Label>
                        <Form.Control value={rule.anchorText} onChange={txtAnchorTextChangeHandler} />
                      </Form.Group>
                    </div>
                    <div className="col-3">
                      <Form.Group className="mb-3" controlId="formRegionMode">
                        <Form.Label>Region Mode: </Form.Label>
                        <Form.Select className={styles.textfieldAnchorSelect} aria-label="textFieldAnchor" onChange={(e) => selectTextFieldAnchorChangeHandler(e)} value={textfieldAnchorToggle}>
                          <option value="textfield">Textfield</option>
                          <option value="anchor">Anchor</option>
                        </Form.Select>
                      </Form.Group>
                    </div>
                  </>
                )}
              </div>
            </div>
            {rule && documentId != 0 && pageNum != 0 && (
              <div className={styles.regionSelectorWrapper}>
                <Form.Label>Region: </Form.Label>
                <div className={styles.imageCropperContainer}>
                  {(rule.ruleType == "TEXTFIELD" ||
                    (rule.ruleType == "ANCHORED_TEXTFIELD" && textfieldAnchorToggle == "textfield") ||
                    rule.ruleType == "BARCODE") && (
                    <ReactCrop className={styles.myReactCrop} crop={textfieldRegion} onChange={(c, p) => {
                      textfieldRegionChangeHandler(p)
                    }} onDragEnd={textfieldRegionDragEndHandler}>
                      <img src={imageUri} ref={imageRef}/>
                    </ReactCrop>
                  )}
                  {rule.ruleType == "ANCHORED_TEXTFIELD" && textfieldAnchorToggle == "anchor" && (
                    <ReactCrop className={styles.myReactCrop + " " + "anchorReactCrop"} crop={anchorRegion} onChange={(c, p) => {
                      anchorRegionChangeHandler(p)
                    }} onDragEnd={anchorRegionDragEndHandler}>

                      <img src={imageUri} ref={imageRef}/>

                    </ReactCrop>
                  )}
                  {rule.ruleType == "TABLE"  && (
                    <div style={{position: "relative"}}>
                      <ReactCrop className={styles.myReactCrop} crop={textfieldRegion} onChange={(c, p) => {
                        textfieldRegionChangeHandler(p)
                      }} onDragEnd={textfieldRegionDragEndHandler}>
                        <img src={imageUri} ref={newImageRef => setImageRef(newImageRef)}/>
                      </ReactCrop>
                      {rule && rule.tableColumnSeparators && imageRef && rule.tableColumnSeparators.map(
                        (separator, sIndex) => {
                          return (
                          <Draggable
                            axis="x"
                            defaultPosition={{x: 0, y: 0}}
                            grid={[1, 1]}
                            scale={1}
                            position={{ x: separator.x / 100 * imageRef.width, y: 0 }}
                            onStart={separatorStartHandler}
                            onDrag={separatorDragHandler}
                            onStop={(e, el) => separatorStopHandler(e, el, sIndex)}
                            key={sIndex}>
                            <div>
                              <div className="handle"></div>
                              <div className="line"></div>
                            </div>
                          </Draggable>
                          )
                        }
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>
      {rule && rule.rule_type == "TABLE" && (
        <div className={styles.regionSelectActions}>
          <Button variant="primary" className={styles.addSeparatorBtn} onClick={addSeparatorBtnClickHandler}>Add Separator</Button>
          <Button variant="primary" className={styles.removeSeparatorBtn} onClick={removeSeparatorBtnClickHandler}>Remove Separator</Button>
        </div>
      )}
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

export default RegionSelector