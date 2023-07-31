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
  const imageRef = useRef(null)

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

  useEffect(() => {
    if (parserId == undefined) return
    getParserDocuments()
  }, [router.isReady, parserId])

  useEffect(() => {
    if (parserId == undefined) return
    if (documentId == 0) return
    getDocumentPageImage()
  }, [router.isReady, ,documentId, pageNum])

  const getLayout = () => {
    service.get("layouts/" + layoutId, response => {
      setLayout(response.data)
    })
  }

  const getRule = () => {
    service.get("rules/" + ruleId + "/", response => {
      setRule(response.data)
    })
  }

  const getParserDocuments = () => {
    service.get("documents/?parserId=" + parserId, response => {
      setParserDocuments(response.data)
    })
  }

  const getDocumentPageImage = () => {
    service.getFile("documents/" + documentId + "/image/?parserId=" + parserId + "&pageNum=" + pageNum,
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
    service.put("rules/" + ruleId + "/",
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
    let anchorX1 = rule.anchorX1 ?? 0
    let anchorX2 = rule.anchorX2 ?? 100
    let ruleAnchorY1 = rule.anchorY2 ?? 100
    let ruleAnchorY2 = rule.anchorY1 ?? 0
    let anchorY1 = 100 - ruleAnchorY2
    let anchorY2 = 100 - ruleAnchorY1
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
        x: parseFloat(anchorX1),
        y: anchorY1,
        width: rule.anchorX2 - anchorX1,
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
    }
    if (rule.ruleType == "ANCHORED_TEXTFIELD") {
      rule.anchorDocumentId = documentId
      rule.anchorPageNo = pageNum
      rule.anchorText = anchorText
    }
    setRule(updatedRule)
    updateRule(updatedRule)
  }

  const addSeparatorBtnClickHandler = (e) => {
    let updatedRule = { ...rule }
    let updatedTableColumnXs
    if (updatedRule.tableColumnXs == "") {
      updatedTableColumnXs = []
    } else {
      updatedTableColumnXs = updatedRule.tableColumnXs.split(",").map(value => parseFloat(value))
    }
    if (updatedTableColumnXs.length > 0) {
      updatedTableColumnXs.push(Number(updatedTableColumnXs.slice(-1)) + 10.0)
    } else {
      updatedTableColumnXs.push(0)
    }
    updatedTableColumnXs.sort()
    updatedRule.tableColumnXs = updatedTableColumnXs.join(",")
    updateRule(updatedRule)
    setRule(updatedRule)
  }

  const removeSeparatorBtnClickHandler = (e) => {
    let updatedRule = { ...rule }
    let updatedTableColumnXs
    if (updatedRule.tableColumnXs == "") {
      updatedTableColumnXs = []
    } else {
      updatedTableColumnXs = updatedRule.tableColumnXs.split(",").map(value => parseFloat(value))
    }
    updatedTableColumnXs.pop()
    updatedTableColumnXs.sort()
    updatedRule.tableColumnXs = updatedTableColumnXs.join(",")
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
    let selectedDocument = parserDocuments.find(d => d.id == documentId)
    let width = imageRef.current.offsetWidth

    let updatedRule = { ...rule }
    let updatedTableColumnXs = updatedRule.tableColumnXs.split(",").map(value => Number(value))
    updatedTableColumnXs[xIndex] = Number(el.x) / width * 100
    updatedTableColumnXs.sort((a, b) => {
      return a - b;
    })
    updatedRule.tableColumnXs = updatedTableColumnXs.map(x => x.toFixed(2)).join(",")
    setRule(updatedRule)
    updateRule(updatedRule)
    e.stopPropagation()
  }

  const proceedToStreamEditorBtnClickHandler = () => {
    router.push("/workspace/parsers/" + parserId + "/layouts/" + layoutId + "/rules/" + ruleId + "?editorType=streamEditor&documentId=" + documentId)
  }

  return (
    <EditorLayout>
      <div className={styles.workbenchWrapper}>
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
                      <option key={parserDocument.id} value={parserDocument.id}>{parserDocument.filenameWithoutExtension + "." + parserDocument.extension}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
                <Form.Group className="mb-3" controlId="formPageNum">
                  <Form.Select aria-label="Page No." onChange={pageNumChangeHandler} value={pageNum}>
                    <option value=""></option>
                    {parserDocuments.length > 0 && documentId != 0 && (
                      parserDocuments.find(d => d.id == documentId).documentPages.map(
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
        {rule && (
          <div className={styles.ruleConfigurations}>
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
                    <Form.Group className="mb-3" controlId="formPages">
                      <Form.Label>Separators: </Form.Label>
                      <div className={styles.regionSelectActions} style={{display: "block", padding: "3px"}}>
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
                        <Form.Select aria-label="textFieldAnchor" onChange={(e) => selectTextFieldAnchorChangeHandler(e)} value={textfieldAnchorToggle}>
                          <option value="textField">Textfield</option>
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
                  (rule.ruleType == "ANCHORED_TEXTFIELD" && textfieldAnchorToggle == "textfield")) && (
                  <ReactCrop className={styles.myReactCrop} crop={textfieldRegion} onChange={(c, p) => {
                    textfieldRegionChangeHandler(p)
                  }}>
                    <img src={imageUri} />
                  </ReactCrop>
                )}
                {rule.ruleType == "ANCHORED_TEXTFIELD" && textfieldAnchorToggle == "anchor" && (
                  <ReactCrop className={styles.myReactCrop} crop={anchorRegion} onChange={(c, p) => {
                    setAnchorRegion(p)
                  }}>

                    <img src={process.env.NEXT_PUBLIC_API_BASE_URL + "documents/" + documentId + "/page/" + pageNum + "/image"} />

                  </ReactCrop>
                )}
                {rule.ruleType == "TABLE" && (
                  <div style={{position: "relative"}}>
                    <ReactCrop className={styles.myReactCrop}
                               crop={textfieldRegion}
                               onChange={(c, p) => {
                                 setTextfieldRegion(p)
                               }}>

                      <img src={process.env.NEXT_PUBLIC_API_BASE_URL + "documents/" + documentId + "/page/" + pageNum + "/image"}
                          ref={imageRef}
                          style={{position: "relative", zIndex: 999}}/>
                    </ReactCrop>
                    {rule && imageRef.current && imageRef.current.offsetWidth != 0 && rule.tableColumnXs && rule.tableColumnXs.split(",").map(
                      (columnX, xIndex) => {
                        return (
                        <Draggable
                          axis="x"
                          defaultPosition={{x: 0, y: 0}}
                          grid={[1, 1]}
                          scale={1}
                          position={{ x: columnX * imageRef.current.offsetWidth / 100, y: 0 }}
                          onStart={separatorStartHandler}
                          onDrag={separatorDragHandler}
                          onStop={(e, el) => separatorStopHandler(e, el, xIndex)}
                          key={columnX}>
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
          </div>
        )}
        {rule && rule.rule_type == "TABLE" && (
          <div className={styles.regionSelectActions}>
            <Button variant="primary" className={styles.addSeparatorBtn} onClick={addSeparatorBtnClickHandler}>Add Separator</Button>
            <Button variant="primary" className={styles.removeSeparatorBtn} onClick={removeSeparatorBtnClickHandler}>Remove Separator</Button>
          </div>
        )}
        <div className={styles.workbenchFooter}>
          <div className={styles.backBtnWrapper}>
            <Button variant="success" className={styles.confirmBtn} onClick={() => router.push("/workspace/parsers/" + parserId + "/layouts/" + layoutId + "/rules/" + ruleId + "?editorType=ruleProperties&documentId=" + documentId)}>Back to Rule Properties</Button>
          </div>
          <div className={styles.copyrightWrapper}>
            Copyright @ 2022
          </div>
          <div className={styles.confirmBtnWrapper}>
            <Button variant="success" className={styles.confirmBtn} onClick={proceedToStreamEditorBtnClickHandler}>Proceed to Stream Editor</Button>
          </div>
        </div>
      </div>
    </EditorLayout>
  )
}

export default RegionSelector