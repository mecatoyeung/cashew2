
import { useState, useEffect, useRef } from 'react'

import Head from "next/head"

import { useRouter } from 'next/router'

import { v4 as uuidv4 } from 'uuid'

import { produce } from 'immer';

import Image from "next/image";
import Link from "next/link";

import Col from 'react-bootstrap/Col'
import Tabs from 'react-bootstrap/Tabs'
import Tab from 'react-bootstrap/Tab'
import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'
import Card from 'react-bootstrap/Card'
import Button from 'react-bootstrap/Button'
import Modal from 'react-bootstrap/Modal'
import { Nav } from "react-bootstrap";

import Select from 'react-select'

import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch"

const ExcelJS = require('exceljs')

const FileSaver = require('file-saver')

import AIChatLayout from '../../../../../layouts/aichat'

import service from '../../../../../service'

import styles from '../../../../../styles/AIChat.module.css'


const AIChat = () => {

  const router = useRouter()

  let { pathname, parserId, documentId, pageNum } = router.query;

  const [parser, setParser] = useState(null)

  const [document, setDocument] = useState(null)

  const [textlines, setTextlines] = useState([])

  const [chatHistories, setChatHistories] = useState([])

  const [chatText, setChatText] = useState("")

  const [chatIsLoading, setChatIsLoading] = useState(false)

  const [parserDocuments, setParserDocuments] = useState([])

  const [changeDocumentModal, setChangeDocumentModal] = useState({
    show: false
  })

  const [completedMark, setCompletedMark] = useState(false)

  const [imageUri, setImageUri] = useState(null)
  const [imageRef, setImageRef] = useState()

  const [showDocumentPagePreview, setShowDocumentPagePreview] = useState(true)

  const getParser = () => {
    service.get("parsers/" + parserId + "/", response => {
      setParser(response.data)
    })
  }

  useEffect(() => {
    if (!router.isReady) return
    getParser()
  }, [router.isReady])

  const updateParser = () => {
    service.put("parsers/" + parserId + "/",
      parser,
      response => {
      }
    )
  }

  const getDocument = () => {
    if (!parserId) return
    if (!documentId) return
    service.get("documents/" + documentId + "/?parserId=" + parserId, response => {
      setDocument(response.data)
    })
  }

  const getDocumentPageImage = () => {
    if (!documentId) return
    if (!pageNum) return
    service.getFile("documents/" + documentId + "/pages/" + pageNum + "/",
      (response) => {
        let data = `data:${
          response.headers["content-type"]
        };base64,${new Buffer(response.data, "binary").toString("base64")}`
        setImageUri(data)
      })
  }

  const getTextlines = () => {
    if (!parserId) return
    if (!documentId) return
    if (!pageNum) return
    service.get("parsers/" + parserId + "/document/" + documentId + "/pages/" + pageNum + "/extract_all_text/", response => {
      setTextlines(response.data)
    })
  }

  const refreshChatHistories = () => {
    console.log("hello")
    setChatHistories(produce(draft => {
      draft.length = 0
    }))
    if (parser && parser.chatbot && parser.chatbot.openAiDefaultQuestion && parser.chatbot.openAiDefaultQuestion.trim().length > 0) {
      chatTextSendHandler(parser.chatbot.openAiDefaultQuestion)
    }
  }

  const prevPage = () => {
    if (pageNum <= 1) return
    let newPageNum = parseInt(pageNum) - 1
    router.push({
      pathname,
      query: {
        ...router.query,
        pageNum: newPageNum
      },
    })
  }

  const nextPage = () => {
    if (pageNum >= document.documentPages.length) return
    let newPageNum = parseInt(pageNum) + 1
    router.push({
      pathname,
      query: {
        ...router.query,
        pageNum: newPageNum
      },
    })
    //refreshChatHistories()
  }

  const toggleDocumentPagePreviewHandler = () => {
    setShowDocumentPagePreview(!showDocumentPagePreview)
  }

  const chatTextChangeHandler = (e) => {
    setChatText(e.target.value)
  }

  const chatTextKeyDownHandler = (e) => {
    if ((e.keyCode == 10 || e.keyCode == 13) && e.ctrlKey) {
      chatTextSendHandler(e.target.value)
      setChatText("")
    }
  }

  const chatTextSendHandler = (chatText) => {
    setChatIsLoading(true)
    setChatText("")
    addChatHistory(
      {
        uuid: uuidv4(),
        from: "staff",
        chat: chatText
      }
    )
    service.post("parsers/" + parserId + "/documents/" + documentId + "/pages/" + pageNum + "/ask_openai/", {
      "question": chatText
    }, response => {
      setChatIsLoading(false)
      addChatHistory({
        uuid: uuidv4(),
        from: "machine",
        chat: response.data
      })
    }, error => {
      console.error(error)
      setChatIsLoading(false)
      addChatHistory({
        uuid: uuidv4(),
        from: "machine",
        chat: { "Error": error.response.data }
      })
    })
  }

  const addChatHistory = (chatHistory) => {
    setChatHistories(produce(draft => {
      draft.push(chatHistory)
    }))
  }

  const downloadExcelBtnClickHandler = async () => {
    if (chatHistories.filter(ch => ch.from == "machine").length == 0) return

    const workbook = new ExcelJS.Workbook()
    const metadataWorksheet = workbook.addWorksheet('Metadata');

    let latestMachineResponse = chatHistories.filter(ch => ch.from == "machine").slice(-1)[0].chat
    let rowIndex = 0
    Object.entries(latestMachineResponse)
      .map(([key, value]) => {
        if (!Array.isArray(value)) {
          let rowValues = []
          rowValues[1] = key
          rowValues[2] = value
          metadataWorksheet.addRow(rowValues)
        } else {
          let itemTableName = key
          let itemTableRows = value
          if (itemTableRows.length > 0) {
            let itemTableSheet = workbook.addWorksheet(itemTableName)
            let rowValues = []
            let itemTableColIndex = 1
            Object.entries(itemTableRows[0])
            .map(([tableKey, tableValue]) => {
              rowValues[itemTableColIndex] = tableKey
              itemTableColIndex++
            })
            itemTableSheet.addRow(rowValues)
            
            
            for (let j=0; j<itemTableRows.length; j++) {
              let itemTableRow = itemTableRows[j]
              rowValues = []

              itemTableColIndex = 1
              Object.entries(itemTableRow)
              .map(([tableKey, tableValue]) => {
                rowValues[itemTableColIndex] = tableValue
                itemTableColIndex++
              })
              itemTableSheet.addRow(rowValues)
            }
          }
        }
    })
    const buffer = await workbook.xlsx.writeBuffer()
    FileSaver.saveAs(new Blob([buffer]), "Cashew AI Chatbot Result.xlsx")
  }

  const markAsCompletedBtnClickHandler = (e) => {
    console.log(e)
    service.post("documents/" + documentId + "/pages/" + pageNum + "/mark_as_chatbot_completed/", 
    {
      status: true
    }, 
    response => {
      getDocument()
    }, errorResponse => {
      console.error(errorResponse)
    })
  }

  const markAsIncompletedBtnClickHandler = (e) => {
    service.post("documents/" + documentId + "/pages/" + pageNum + "/mark_as_chatbot_completed/", 
    {
      status: false
    }, 
    response => {
      getDocument()
    }, errorResponse => {
      console.error(errorResponse)
    })
  }

  const timeout = async (delay) => {
    return new Promise( res => setTimeout(res, delay) );
  }

  const getParserDocuments = () => {
    if (!parserId) return
    service.get("documents/?parserId=" + parserId, response => {
      console.log(response.data)
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
      }
      setParserDocuments(parserDocuments)
    })
  }

  const changeDocumentModalOpenHandler = () => {
    setChangeDocumentModal(produce(draft => {
      draft.show = true
    }))
  }

  const changeDocumentModalCloseHandler = () => {
    setChangeDocumentModal(produce(draft => {
      draft.show = false
    }))
  }

  const selectedDocumentChangeHandler = (e) => {
    router.push({
      pathname,
      query: {
        ...router.query,
        documentId: e.target.value,
        pageNum: 1
      },
    })
  }

  useEffect(() => {
    if (!router.isReady) return
  }, [router.isReady])

  useEffect(() => {
    if (!router.isReady) return
    if (!parserId) return
    getParserDocuments()
  }, [router.isReady, parserId])

  useEffect(() => {
    if (!router.isReady) return
    getDocument()
  }, [router.isReady, parserId, documentId])

  useEffect(() => {
    if (!router.isReady) return
    getDocumentPageImage()
    getTextlines()
  }, [router.isReady, parserId, documentId, pageNum])

  useEffect(() => {
    if (!router.isReady) return
    refreshChatHistories()
  }, [router.isReady, documentId])

  return (
    <>
      <Head>
        <title>Cashew Docparser</title>
        <meta name="description" content="Written by Cato Yeung" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"
        ></meta>
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className={styles.wrapper}>
        <header className={styles.header}>
          <div>
            <div className="row" style={{ padding: 0, margin: 0 }}>
              <div
                className="col-6 col-md-6"
                style={{ paddingLeft: 20, paddingRight: 0 }}
              >
                <div className={styles.logoDiv}>
                  <Image
                    src="/static/img/logo.png"
                    width="40"
                    height="36"
                    alt="Cashew Docparser"
                  />
                </div>
                <h2>Cashew</h2>
                &nbsp;&nbsp;&nbsp;
                <Nav.Link
                  href="/workspace/parsers"
                  style={{ display: "inline-block", verticalAlign: "top" }}
                >
                  <i
                    className={
                      styles.parsersIcon + " bi bi-grid"
                    }
                  ></i>
                </Nav.Link>
                <Nav.Link
                  href={"/workspace/parsers/" + parserId + "/rules"}
                  style={{ display: "inline-block", verticalAlign: "text-bottom", marginLeft: 10 }}
                >
                  <Button>Back to Configurations</Button>
                </Nav.Link>
              </div>
              <div
                className="col-6 col-md-6"
                style={{ paddingLeft: 0, paddingRight: 20 }}
              >
                <nav className={styles.nav}>
                  <ul>
                    <li>
                      <Button className="btn" onClick={changeDocumentModalOpenHandler}>
                        Change Document
                      </Button>
                      <Modal show={changeDocumentModal.show} onHide={changeDocumentModalCloseHandler}>
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
                        </Modal.Body>
                        <Modal.Footer>
                          <Button variant="primary" onClick={changeDocumentModalCloseHandler}>
                            Confirm
                          </Button>
                          <Button variant="secondary" onClick={changeDocumentModalCloseHandler}>
                            Close
                          </Button>
                        </Modal.Footer>
                      </Modal>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </header>
        <>
          <hr className={styles.headerHr} />
          <main className={styles.main + " d-flex flex-column"}>
            <div
              className={
                styles.sideNavContainerDiv + " d-flex flex-grow-1"
              }
            >
              <div
                className="row d-flex flex-grow-1"
                style={{ padding: 0, margin: 0, flexDirection: "row" }}
              >
                <div
                  className="col-12 col-md-2 d-flex"
                  style={{ position: "relative", paddingLeft: 0, paddingRight: 0, width: showDocumentPagePreview ? 480 : 0, overflow: "auto", borderRight: "3px solid #000", borderRight: "3px solid #000", maxHeight: "calc(100vh - 121px)" }}
                >
                  {document && document.documentPages.filter(dp => dp.pageNum == pageNum && dp.ocred).length > 0 && (
                    <TransformWrapper 
                      className="my-react-transform-component"
                      wheel={{disabled: true}}
                      initialScale={0.3}
                      minScale={0.2} maxScale={1} maxPositionY={0}
                      centerZoomedOut={false} customTransform={(x, y, scale) => {
                        const a = scale;
                        const b = 0;
                        const c = 0;
                        const d = scale;
                        const tx = x;
                        const ty = y;
                        return `matrix3d(${a}, ${b}, 0, 0, ${c}, ${d}, 0, 0, 0, 0, 1, 0, ${tx}, 40, 0, 1)`;
                      }}> 
                      {({ zoomIn, zoomOut, resetTransform, ...rest }) => (
                        <>
                          <div className={styles.tools} style={{ display: showDocumentPagePreview ? "block": "none" }}>
                            <Button className={styles.toolsBtn} onClick={() => zoomIn()}>Zoom in</Button>
                            <Button className={styles.toolsBtn} onClick={() => zoomOut()}>Zoom out</Button>
                            <Button className={styles.toolsBtn} onClick={() => resetTransform()}>Reset</Button>
                            <Button className={styles.toolsBtn} onClick={() => prevPage()}><i className="bi bi-arrow-left"></i></Button>
                            <Button className={styles.toolsBtn}>Page {pageNum} of {document && document.documentPages.length}</Button>
                            <Button className={styles.toolsBtn} onClick={() => nextPage()}><i className="bi bi-arrow-right"></i></Button>
                          </div>
                          <TransformComponent>
                            <img className={styles.documentPageImg} src={imageUri} ref={imageRef}/>
                          </TransformComponent>
                        </>
                      )}
                    </TransformWrapper>
                  )}
                  {document && document.documentPages.filter(dp => dp.pageNum == pageNum && dp.ocred).length <= 0 && (
                    <TransformWrapper 
                      className="my-react-transform-component"
                      wheel={{disabled: true}}
                      minScale={0.2} maxScale={1} maxPositionY={0}
                      centerZoomedOut={false}> 
                      {({ zoomIn, zoomOut, resetTransform, ...rest }) => (
                        <>
                          <div className={styles.tools} style={{ display: showDocumentPagePreview ? "block": "none" }}>
                            <Button className={styles.toolsBtn} onClick={() => zoomIn()}>Zoom in</Button>
                            <Button className={styles.toolsBtn} onClick={() => zoomOut()}>Zoom out</Button>
                            <Button className={styles.toolsBtn} onClick={() => resetTransform()}>Reset</Button>
                            <Button className={styles.toolsBtn} onClick={() => prevPage()}><i className="bi bi-arrow-left"></i></Button>
                            <Button className={styles.toolsBtn}>Page {pageNum} of {document && document.documentPages.length}</Button>
                            <Button className={styles.toolsBtn} onClick={() => nextPage()}><i className="bi bi-arrow-right"></i></Button>
                          </div>
                          <TransformComponent>

                          </TransformComponent>
                          <div style={{ width: 100, height: 100, margin: "auto" }}>This page is undergoing OCR. Please wait...</div>
                        </>
                      )}
                    </TransformWrapper>
                  )}
                </div>
                <div
                  className="col-12 col-md-10 flex-grow-1"
                  style={{
                    paddingLeft: 0,
                    paddingRight: 0,
                    paddingBottom: 0,
                    maxHeight: "calc(100vh - 121px)",
                    display: "flex",
                    flexDirection: "column",
                    width: "calc(100vw - 500px)",
                  }}
                >
                  <div className={styles.pageText}>
                    <div className={styles.streamTableDiv}>
                          <table className={styles.streamTable}>
                            <tbody>
                              {textlines.map((row, rowIndex) => {
                                return (
                                  <tr key={rowIndex}>
                                    <td>{row}</td>
                                  </tr>
                                )
                              })}
                            </tbody>
                          </table>
                        </div>
                  </div>
                  <div className={styles.chatMessages}>
                    <div className={[styles.talkBubble, styles.triRight, styles.round, styles.btmLeft].join(" ")}>
                      <div className={styles.talktext}>
                        <p>Ask me anything about this page.</p>
                      </div>
                    </div>
                    {chatHistories && chatHistories.map((chatHistory, chatHistoryIndex) => 
                      <div key={chatHistory.uuid}>
                        {console.log(chatHistories)}
                        {chatHistory.from == "staff" && (
                          <div className={[styles.talkBubble, styles.triRight, styles.border, styles.btmRightIn, "right"].join(" ")}>
                            <div className={styles.talktext}>
                              <p>{chatHistory.chat}</p>
                            </div>
                          </div>
                        )}
                        {chatHistory.from == "machine" && (
                          <div className={[styles.talkBubble, styles.triRight, styles.round, styles.btmLeft].join(" ")}>
                            <div className={styles.talktext}>
                              {Object.entries(chatHistory.chat)
                                .map(([chatKey, chatValue]) => {
                                  console.log(chatKey, chatValue)
                                  if (!Array.isArray(chatValue)) {
                                    return (
                                      <div className={styles.talkKeyToValue} key={chatKey}>
                                        {chatKey}: {chatValue}
                                      </div>
                                    )
                                  } else {
                                    let itemTableName = chatKey
                                    let itemTableRows = chatValue
                                    if (itemTableRows.length > 0) {
                                      return (
                                        <div className="talk-table-div" key={itemTableName}>
                                          <p>{itemTableName}: </p>
                                          <table className="talk-table">
                                            <thead>
                                              <tr>
                                                {Object.entries(itemTableRows[0]).map(
                                                  ([itemTableRowThKey, itemTableRowThValue]) => {
                                                    return (<th key={itemTableRowThKey}>{itemTableRowThKey}</th>)
                                                  }
                                                )}
                                              </tr>
                                            </thead>
                                            <tbody>
                                              {itemTableRows.map((itemTableRow, itemTableRowIndex) => (
                                                <tr key={JSON.stringify(itemTableRow)}>
                                                  {Object.entries(itemTableRow).map(
                                                    ([itemTableRowTdKey, itemTableRowTdValue]) => {
                                                      return (<td key={itemTableRowTdKey}>{itemTableRowTdValue}</td>)
                                                    }
                                                  )}
                                                </tr>
                                              ))}
                                            </tbody>
                                          </table>
                                        </div>
                                      )
                                    }
                                  }
                                })
                              }
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                    <div className={styles.actions}>
                      <Button style={{marginLeft: 10, marginBottom: 10, marginTop: 10, whiteSpace: "nowrap"}} onClick={downloadExcelBtnClickHandler}>Download as Excel</Button>
                      {document && document.documentPages.find(dp => dp.pageNum == pageNum).chatbotCompleted && (
                        <Button style={{marginLeft: 10, marginBottom: 10, marginTop: 10, whiteSpace: "nowrap"}} onClick={markAsIncompletedBtnClickHandler}>Mark as incompleted</Button>
                      )}
                      {document && !document.documentPages.find(dp => dp.pageNum == pageNum).chatbotCompleted && (
                        <Button style={{marginLeft: 10, marginBottom: 10, marginTop: 10, whiteSpace: "nowrap"}} onClick={markAsCompletedBtnClickHandler}>Mark as completed</Button>
                      )}
                    </div>
                  </div>
                  <div className={styles.chatTextfield}>
                    <Form.Control
                      type="text"
                      id="chatTextfield"
                      style={{ "borderRadius": 0, "resize": "none" }}
                      placeholder={chatIsLoading ? "Sending to Open AI. Please wait..." : "Ask me anything..."}
                      as="textarea"
                      row="2"
                      value={chatText}
                      disabled={chatIsLoading}
                      onChange={chatTextChangeHandler}
                      onKeyDown={chatTextKeyDownHandler}
                    />
                    <Button style={{ borderRadius: 0}} onClick={() => chatTextSendHandler(chatText)}>Send</Button>
                  </div>
                </div>
              </div>
                <Button style={{position: "absolute", bottom: 71, left: 5, display: showDocumentPagePreview ? "none" : "block"}} onClick={() => toggleDocumentPagePreviewHandler()}>Show</Button>
                <Button style={{position: "absolute", bottom: 71, left: 5, display: showDocumentPagePreview ? "block" : "none"}} onClick={() => toggleDocumentPagePreviewHandler()}>Hide</Button>
            </div>
          </main>
        </>
        <footer className={styles.footer}>
          <div style={{ width: "100%", padding: "0 10px" }}>
            <div className="row" style={{ padding: "0 10px" }}>
              <div className="col-sm" style={{ padding: "10px" }}>
                <div className={styles.copyright}>
                  2023 @ Sonik Global Limited. All rights reserved.
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  )
}

export default AIChat